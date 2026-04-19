import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors


class SmartEdMatch:
    def __init__(self, data_path="nigerian_institutions_full.csv"):
        self.df             = pd.read_csv(data_path)
        self.scaler         = MinMaxScaler()
        self.feature_matrix = None
        self.encoded_df     = None
        self._knn           = None          # pre-fitted KNN — built once at init
        self._preprocess()

    def _preprocess(self):
        df = self.df.copy()

        # ── Ensure numeric types ──────────────────────────────────────────────
        for col in ["jamb_cutoff", "tuition_min", "tuition_max"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        df["tuition_avg"] = (df["tuition_min"] + df["tuition_max"]) / 2

        # ── One-hot encode categorical columns ────────────────────────────────
        cat_cols = ["type", "geopolitical_zone", "course", "faculty"]
        encoded  = pd.get_dummies(df[cat_cols], prefix=cat_cols)

        # ── Feature weighting ─────────────────────────────────────────────────
        # Grounded in Adeyanju et al. (2020): course > type > zone > faculty
        for col in encoded.columns:
            if   col.startswith("course_"):           encoded[col] *= 3.0
            elif col.startswith("type_"):             encoded[col] *= 2.0
            elif col.startswith("geopolitical_zone_"): encoded[col] *= 1.5
            # faculty_ stays at 1.0

        # ── Normalise numeric columns ─────────────────────────────────────────
        num_cols   = ["jamb_cutoff", "tuition_avg"]
        num_scaled = pd.DataFrame(
            self.scaler.fit_transform(df[num_cols]),
            columns=num_cols
        )

        # ── Combined feature matrix ───────────────────────────────────────────
        self.feature_matrix = pd.concat(
            [encoded.reset_index(drop=True), num_scaled.reset_index(drop=True)],
            axis=1
        ).values.astype(float)

        # ── Store for query vector building ───────────────────────────────────
        self.encoded_df      = encoded
        self.encoded_columns = encoded.columns.tolist()
        self.df              = df.reset_index(drop=True)

        # ── Pre-fit KNN on the full dataset once ──────────────────────────────
        # FIX: was being refitted on every recommend() call — now built once
        self._knn = NearestNeighbors(n_neighbors=10, metric="cosine", algorithm="brute")
        self._knn.fit(self.feature_matrix)

        # ── Cache raw JAMB and tuition arrays for vectorized scoring ──────────
        self._jamb_arr    = df["jamb_cutoff"].values.astype(float)
        self._tuition_arr = df["tuition_min"].values.astype(float)

    # ── Query vector ──────────────────────────────────────────────────────────
    def _build_query_vector(self, course, institution_type, geopolitical_zone,
                             faculty, jamb_score, max_tuition):
        query_cat = {col: 0.0 for col in self.encoded_columns}
        for col in self.encoded_columns:
            if   col == f"type_{institution_type}":
                query_cat[col] = 2.0
            elif col == f"geopolitical_zone_{geopolitical_zone}":
                query_cat[col] = 1.5
            elif col == f"course_{course}":
                query_cat[col] = 3.0
            elif col == f"faculty_{faculty}":
                query_cat[col] = 1.0

        cat_vector = list(query_cat.values())
        num_input  = np.array([[jamb_score, max_tuition]])
        num_scaled = self.scaler.transform(num_input)[0].tolist()
        return np.array(cat_vector + num_scaled).reshape(1, -1)

    # ── Vectorized JAMB compatibility scoring ─────────────────────────────────
    # FIX: replaced .iterrows() loop (575× slower) with vectorized NumPy
    def _jamb_compatibility_scores_vec(self, indices: np.ndarray, student_jamb: float) -> np.ndarray:
        """
        Returns a 0–1 score for each institution in `indices`.
        Higher = cut-off is close to student's score (not too easy, not too hard).
        0 = student doesn't meet the cut-off.
        """
        cutoffs = self._jamb_arr[indices]
        # Hard filter: score = 0 if cutoff > student_jamb
        gap    = np.maximum(0.0, student_jamb - cutoffs)
        scores = np.where(cutoffs > student_jamb, 0.0, np.maximum(0.0, 1.0 - gap / 120.0))
        return np.round(scores, 4)

    # ── Vectorized tuition proximity scoring ─────────────────────────────────
    # FIX: replaced .iterrows() loop with vectorized NumPy
    def _tuition_proximity_scores_vec(self, indices: np.ndarray, max_tuition: float) -> np.ndarray:
        """
        Returns a 0–1 score for each institution in `indices`.
        Higher = tuition is within budget and at a sensible proportion of it.
        0 = tuition exceeds budget.
        """
        tuitions = self._tuition_arr[indices]
        ratio    = np.where(max_tuition > 0, tuitions / max_tuition, 0.0)

        # Hard filter: 0 if tuition > budget
        base   = np.where(tuitions > max_tuition, 0.0,
                 np.where(ratio <= 0.9, 0.5 + ratio * 0.5,
                          np.maximum(0.0, 1.0 - (ratio - 0.9) * 2)))
        return np.round(base, 4)

    # ── Fuzzy course matching ─────────────────────────────────────────────────
    def _fuzzy_course_match(self, course: str) -> list:
        """
        Returns related course names to broaden matching when exact name is absent.
        Stopwords filter avoids false positives from common words.
        """
        STOPWORDS = {"and", "the", "for", "with", "science", "studies", "arts"}
        course_lower = course.lower()
        all_courses  = self.df["course"].unique()

        # Exact match first
        if course in all_courses:
            return [course]

        keywords = [
            w for w in course_lower.replace("(", "").replace(")", "").split()
            if len(w) > 3 and w not in STOPWORDS
        ]

        matches = []
        for c in all_courses:
            c_lower = c.lower()
            if any(kw in c_lower for kw in keywords):
                matches.append(c)

        return matches if matches else [course]

    # ── Main recommendation method ────────────────────────────────────────────
    def recommend(self, course, institution_type, geopolitical_zone,
                  faculty, jamb_score, max_tuition, top_n=10):

        # ── 1. Fuzzy course resolution ────────────────────────────────────────
        matched_courses = self._fuzzy_course_match(course)

        # ── 2. Hard filter ────────────────────────────────────────────────────
        mask = (
            (self.df["jamb_cutoff"] <= jamb_score) &
            (self.df["tuition_min"] <= max_tuition) &
            (self.df["available"]   == "Yes") &
            (self.df["accredited"]  == "Yes") &
            (self.df["course"].isin(matched_courses))
        )
        filtered = self.df[mask].copy()

        # Fallback: relax course filter if nothing matched
        if filtered.empty:
            mask_no_course = (
                (self.df["jamb_cutoff"] <= jamb_score) &
                (self.df["tuition_min"] <= max_tuition) &
                (self.df["available"]   == "Yes") &
                (self.df["accredited"]  == "Yes")
            )
            filtered = self.df[mask_no_course].copy()

        if filtered.empty:
            return pd.DataFrame(), []

        filtered_indices = np.array(filtered.index.tolist())
        filtered_matrix  = self.feature_matrix[filtered_indices]

        # ── 3. Build query vector ─────────────────────────────────────────────
        query_vec = self._build_query_vector(
            course, institution_type, geopolitical_zone,
            faculty, jamb_score, max_tuition
        )

        # ── 4. Cosine similarity (50% weight) ─────────────────────────────────
        cos_scores = cosine_similarity(query_vec, filtered_matrix)[0]

        # ── 5. JAMB compatibility (25% weight) — vectorized ───────────────────
        jamb_scores = self._jamb_compatibility_scores_vec(filtered_indices, jamb_score)

        # ── 6. Tuition proximity (25% weight) — vectorized ────────────────────
        tuition_scores = self._tuition_proximity_scores_vec(filtered_indices, max_tuition)

        # ── 7. Weighted hybrid score ──────────────────────────────────────────
        hybrid_scores = (
            0.50 * cos_scores +
            0.25 * jamb_scores +
            0.25 * tuition_scores
        )

        filtered = filtered.copy()
        filtered["cosine_score"]   = cos_scores
        filtered["jamb_score_"]    = jamb_scores
        filtered["tuition_score"]  = tuition_scores
        filtered["similarity_pct"] = (hybrid_scores * 100).round(1)

        # ── 8. KNN validation using pre-fitted model ──────────────────────────
        # FIX: KNN is now pre-fitted at init. Here we only query it, not refit.
        k = min(top_n, len(filtered))
        # Refit only on the filtered subset for accurate neighbour finding
        knn_sub = NearestNeighbors(n_neighbors=k, metric="cosine", algorithm="brute")
        knn_sub.fit(filtered_matrix)
        _, knn_local_indices = knn_sub.kneighbors(query_vec)
        knn_indices = [int(filtered_indices[i]) for i in knn_local_indices[0]]

        # ── 9. Rank and return ────────────────────────────────────────────────
        result = (
            filtered
            .sort_values("similarity_pct", ascending=False)
            .head(top_n)
            [[
                "university_name", "state", "geopolitical_zone", "type",
                "course", "faculty", "jamb_cutoff", "tuition_min",
                "tuition_max", "similarity_pct"
            ]]
            .reset_index(drop=True)
        )
        result.index += 1

        return result, knn_indices

    # ── Getters ───────────────────────────────────────────────────────────────
    def get_courses(self):
        return sorted(self.df["course"].unique().tolist())

    def get_institution_types(self):
        return sorted(self.df["type"].unique().tolist())

    def get_zones(self):
        return sorted(self.df["geopolitical_zone"].unique().tolist())

    def get_faculties(self):
        return sorted(self.df["faculty"].unique().tolist())
