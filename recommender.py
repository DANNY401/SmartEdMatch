import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors


class SmartEdMatch:
    def __init__(self, data_path="nigerian_institutions_full.csv"):
        self.df = pd.read_csv(data_path)
        self.scaler     = MinMaxScaler()
        self.num_scaler = MinMaxScaler()   # separate scaler for JAMB/tuition proximity
        self.feature_matrix = None
        self.encoded_df     = None
        self._preprocess()

    def _preprocess(self):
        df = self.df.copy()

        # Ensure numeric types
        for col in ["jamb_cutoff", "tuition_min", "tuition_max"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        df["tuition_avg"] = (df["tuition_min"] + df["tuition_max"]) / 2

        # ── One-hot encode categorical columns ───────────────────────────────
        cat_cols = ["type", "geopolitical_zone", "course", "faculty"]
        encoded  = pd.get_dummies(df[cat_cols], prefix=cat_cols)

        # ── FEATURE WEIGHTING ────────────────────────────────────────────────
        # Course is the most important factor — weight it 3x
        # Institution type is important — weight it 2x
        # Geopolitical zone — weight it 1.5x
        # Faculty — keep at 1x
        for col in encoded.columns:
            if col.startswith("course_"):
                encoded[col] = encoded[col] * 3.0
            elif col.startswith("type_"):
                encoded[col] = encoded[col] * 2.0
            elif col.startswith("geopolitical_zone_"):
                encoded[col] = encoded[col] * 1.5
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

        # ── Fit separate scaler for proximity scoring ──────────────────────────
        self.num_scaler.fit(df[["jamb_cutoff", "tuition_avg"]])

        # Store raw ranges for proximity calculation
        self._jamb_min  = df["jamb_cutoff"].min()
        self._jamb_max  = df["jamb_cutoff"].max()
        self._tuit_min  = df["tuition_avg"].min()
        self._tuit_max  = df["tuition_avg"].max()

    def _build_query_vector(self, course, institution_type, geopolitical_zone,
                             faculty, jamb_score, max_tuition):
        # Build one-hot vector with same weights applied
        query_cat = {col: 0.0 for col in self.encoded_columns}
        for col in self.encoded_columns:
            if col == f"type_{institution_type}":
                query_cat[col] = 2.0         # matches type_ weight
            elif col == f"geopolitical_zone_{geopolitical_zone}":
                query_cat[col] = 1.5         # matches zone weight
            elif col == f"course_{course}":
                query_cat[col] = 3.0         # matches course weight
            elif col == f"faculty_{faculty}":
                query_cat[col] = 1.0

        cat_vector = list(query_cat.values())

        # Normalise numeric inputs using the same scaler
        avg_tuition = max_tuition  # use max_tuition as the query tuition avg
        num_input   = np.array([[jamb_score, avg_tuition]])
        num_scaled  = self.scaler.transform(num_input)[0].tolist()

        return np.array(cat_vector + num_scaled).reshape(1, -1)

    def _jamb_compatibility_score(self, inst_cutoff, student_jamb):
        """
        Score how well the student's JAMB fits the institution's cut-off.
        Returns 0–1. Higher = better fit (student qualifies AND cut-off is
        close to their score — not too easy, not too hard).
        """
        if inst_cutoff > student_jamb:
            return 0.0   # Student doesn't qualify — hard filter
        gap = student_jamb - inst_cutoff
        # Reward institutions where cut-off is close to student's score
        # Gap of 0–30 = excellent fit, gap > 100 = very easy (less relevant)
        score = max(0.0, 1.0 - (gap / 120.0))
        return round(score, 4)

    def _tuition_proximity_score(self, inst_tuition_min, max_tuition):
        """
        Score how well the institution's tuition fits within the student's budget.
        Returns 0–1. Higher = more affordable relative to budget.
        """
        if inst_tuition_min > max_tuition:
            return 0.0   # Outside budget — hard filter
        # How much of the budget is used (closer to budget = better fit)
        ratio = inst_tuition_min / max_tuition if max_tuition > 0 else 0
        # Sweet spot: using 40–90% of budget = ideal range
        if ratio <= 0.9:
            return round(0.5 + (ratio * 0.5), 4)
        else:
            return round(1.0 - ((ratio - 0.9) * 2), 4)

    def _fuzzy_course_match(self, course):
        """
        Returns a list of course names that are related to the requested course.
        Enables matching even when exact course name is not in dataset.
        """
        course_lower = course.lower()
        all_courses  = self.df["course"].unique().tolist()

        # Extract the core subject keyword from the course name
        # e.g. "Engineering (Electrical)" → "engineering"
        # e.g. "Agricultural Science" → "agricultural"
        keywords = [w for w in course_lower.replace("(","").replace(")","").split()
                    if len(w) > 3 and w not in ["and","the","for","with","science"]]

        matches = [c for c in all_courses if c == course]  # exact match first
        for kw in keywords:
            for c in all_courses:
                if kw in c.lower() and c not in matches:
                    matches.append(c)

        return matches if matches else [course]

    def recommend(self, course, institution_type, geopolitical_zone,
                  faculty, jamb_score, max_tuition, top_n=10):

        # ── Fuzzy course resolution ───────────────────────────────────────────
        matched_courses = self._fuzzy_course_match(course)

        # ── Hard filter (includes fuzzy course matches) ───────────────────────
        filtered = self.df[
            (self.df["jamb_cutoff"] <= jamb_score) &
            (self.df["tuition_min"] <= max_tuition) &
            (self.df["available"]   == "Yes") &
            (self.df["accredited"]  == "Yes") &
            (self.df["course"].isin(matched_courses))
        ].copy()

        # Fallback: if fuzzy match returns nothing, remove course filter
        if filtered.empty:
            filtered = self.df[
                (self.df["jamb_cutoff"] <= jamb_score) &
                (self.df["tuition_min"] <= max_tuition) &
                (self.df["available"]   == "Yes") &
                (self.df["accredited"]  == "Yes")
            ].copy()

        if filtered.empty:
            return pd.DataFrame(), []

        filtered_indices = filtered.index.tolist()
        filtered_matrix  = self.feature_matrix[filtered_indices]

        # ── Build query vector ────────────────────────────────────────────────
        query_vec = self._build_query_vector(
            course, institution_type, geopolitical_zone,
            faculty, jamb_score, max_tuition
        )

        # ── Component 1: Cosine Similarity (50% weight) ───────────────────────
        cos_scores = cosine_similarity(query_vec, filtered_matrix)[0]

        # ── Component 2: JAMB Compatibility Score (25% weight) ───────────────
        jamb_scores = np.array([
            self._jamb_compatibility_score(row["jamb_cutoff"], jamb_score)
            for _, row in filtered.iterrows()
        ])

        # ── Component 3: Tuition Proximity Score (25% weight) ────────────────
        tuition_scores = np.array([
            self._tuition_proximity_score(row["tuition_min"], max_tuition)
            for _, row in filtered.iterrows()
        ])

        # ── Weighted Hybrid Score ─────────────────────────────────────────────
        hybrid_scores = (
            0.50 * cos_scores +
            0.25 * jamb_scores +
            0.25 * tuition_scores
        )

        filtered["cosine_score"]   = cos_scores
        filtered["jamb_score"]     = jamb_scores
        filtered["tuition_score"]  = tuition_scores
        filtered["similarity_pct"] = (hybrid_scores * 100).round(1)

        # ── KNN validation ────────────────────────────────────────────────────
        k = min(top_n, len(filtered))
        knn = NearestNeighbors(n_neighbors=k, metric="cosine")
        knn.fit(filtered_matrix)
        distances, indices = knn.kneighbors(query_vec)
        knn_indices = [filtered_indices[i] for i in indices[0]]

        # ── Rank and return ───────────────────────────────────────────────────
        result = filtered.sort_values("similarity_pct", ascending=False).head(top_n)
        result = result[[
            "university_name", "state", "geopolitical_zone", "type",
            "course", "faculty", "jamb_cutoff", "tuition_min",
            "tuition_max", "similarity_pct"
        ]].reset_index(drop=True)
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
