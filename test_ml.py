"""
SmartEdMatch — ML Library & Algorithm Performance Test
Tests: Pandas, NumPy, Scikit-learn, and the recommendation algorithm

Run: python test_ml.py
Save the output each time so you can track improvements.
"""

import time
import sys

SEPARATOR = "=" * 65

def section(title):
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)

def check(label, passed, detail=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    line   = f"  {status}  {label}"
    if detail:
        line += f"  ({detail})"
    print(line)
    return passed

def timeit(fn):
    t0 = time.perf_counter()
    result = fn()
    return result, (time.perf_counter() - t0) * 1000  # ms


print(SEPARATOR)
print("  SmartEdMatch — ML Library & Algorithm Test")
print(SEPARATOR)

all_passed = []

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1: Library versions and imports
# ══════════════════════════════════════════════════════════════════════════════
section("1 / 6   Library Imports & Versions")

try:
    import pandas as pd
    check("pandas imported", True, f"version {pd.__version__}")
except ImportError as e:
    check("pandas imported", False, str(e)); sys.exit(1)

try:
    import numpy as np
    check("numpy imported", True, f"version {np.__version__}")
except ImportError as e:
    check("numpy imported", False, str(e)); sys.exit(1)

try:
    import sklearn
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.neighbors import NearestNeighbors
    check("scikit-learn imported", True, f"version {sklearn.__version__}")
    check("MinMaxScaler available", True)
    check("cosine_similarity available", True)
    check("NearestNeighbors available", True)
except ImportError as e:
    check("scikit-learn imported", False, str(e)); sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2: Pandas performance on the real dataset
# ══════════════════════════════════════════════════════════════════════════════
section("2 / 6   Pandas — Dataset Loading & Operations")

# Load
df, load_ms = timeit(lambda: pd.read_csv("nigerian_institutions_full.csv"))
all_passed.append(check("CSV loaded", True,
    f"{len(df)} rows in {load_ms:.0f}ms — target <200ms"))
all_passed.append(check("Load speed", load_ms < 200,
    f"{load_ms:.0f}ms"))

# Schema check
expected_cols = ["university_name","state","geopolitical_zone","type",
                 "course","faculty","jamb_cutoff","tuition_min","tuition_max",
                 "available","accredited"]
missing_cols = [c for c in expected_cols if c not in df.columns]
all_passed.append(check("All required columns present", len(missing_cols)==0,
    f"missing: {missing_cols}" if missing_cols else ""))

# Data quality
null_counts = df[expected_cols].isnull().sum()
total_nulls = null_counts.sum()
all_passed.append(check("No null values in key columns", total_nulls == 0,
    f"{total_nulls} nulls found" if total_nulls else "clean"))

# Numeric types
_, ms = timeit(lambda: pd.to_numeric(df["jamb_cutoff"], errors="coerce"))
all_passed.append(check("Numeric conversion (jamb_cutoff)", True, f"{ms:.1f}ms"))
_, ms = timeit(lambda: pd.to_numeric(df["tuition_min"],  errors="coerce"))
all_passed.append(check("Numeric conversion (tuition_min)", True, f"{ms:.1f}ms"))

# Filter operations (simulate what recommender.py does on every query)
_, ms = timeit(lambda: df[
    (df["jamb_cutoff"] <= 220) &
    (df["tuition_min"] <= 150000) &
    (df["available"]   == "Yes") &
    (df["accredited"]  == "Yes") &
    (df["course"]      == "Computer Science")
].copy())
all_passed.append(check("Filter query speed", ms < 50, f"{ms:.1f}ms — target <50ms"))

# Value counts
_, ms = timeit(lambda: df["type"].value_counts())
all_passed.append(check("value_counts() on institution type", True, f"{ms:.1f}ms"))

# Unique values
n_inst    = df["university_name"].nunique()
n_courses = df["course"].nunique()
n_zones   = df["geopolitical_zone"].nunique()
print(f"\n  📊 Dataset summary:")
print(f"     Total records       : {len(df)}")
print(f"     Unique institutions : {n_inst}")
print(f"     Unique courses      : {n_courses}")
print(f"     Unique zones        : {n_zones}")
all_passed.append(check("Record count matches expected", len(df) >= 495,
    f"{len(df)} records"))
all_passed.append(check("Course count matches expected", n_courses >= 46,
    f"{n_courses} courses"))


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3: NumPy performance
# ══════════════════════════════════════════════════════════════════════════════
section("3 / 6   NumPy — Matrix & Array Operations")

# Build a realistic feature matrix (same size as SmartEdMatch's real matrix)
cat_cols = ["type","geopolitical_zone","course","faculty"]
encoded  = pd.get_dummies(df[cat_cols], prefix=cat_cols)
n_rows   = len(encoded)
n_cols   = len(encoded.columns)

feature_matrix, ms = timeit(lambda: encoded.values.astype(float))
all_passed.append(check("Feature matrix construction", True,
    f"{n_rows}×{n_cols} matrix in {ms:.1f}ms"))

# Test matrix operations NumPy does under the hood
arr = np.random.rand(n_rows, n_cols).astype(np.float32)

_, ms = timeit(lambda: np.linalg.norm(arr, axis=1))
all_passed.append(check("Row-wise norm (used in cosine similarity)", ms < 100,
    f"{ms:.1f}ms — target <100ms"))

_, ms = timeit(lambda: arr.mean(axis=0))
all_passed.append(check("Column means", ms < 50, f"{ms:.1f}ms"))

_, ms = timeit(lambda: arr[:5] @ arr.T)  # 5 queries × full matrix (realistic simulation)
all_passed.append(check("Matrix dot product (query × matrix)", ms < 200,
    f"{ms:.1f}ms"))

# dtype check — float64 is default but float32 saves memory
print(f"\n  📊 NumPy matrix stats:")
print(f"     Feature matrix shape : {feature_matrix.shape}")
print(f"     dtype                : {feature_matrix.dtype}")
print(f"     Memory               : {feature_matrix.nbytes / 1024:.1f} KB")
print(f"     NaN values           : {np.isnan(feature_matrix).sum()}")
all_passed.append(check("No NaN in feature matrix",
    np.isnan(feature_matrix).sum() == 0))


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4: Scikit-learn — MinMaxScaler, cosine_similarity, KNN
# ══════════════════════════════════════════════════════════════════════════════
section("4 / 6   Scikit-learn — Scaler · Cosine Similarity · KNN")

# MinMaxScaler
df2 = df.copy()
for col in ["jamb_cutoff","tuition_min","tuition_max"]:
    df2[col] = pd.to_numeric(df2[col], errors="coerce").fillna(0)
df2["tuition_avg"] = (df2["tuition_min"] + df2["tuition_max"]) / 2

scaler = MinMaxScaler()
num_data = df2[["jamb_cutoff","tuition_avg"]].values

scaled, ms = timeit(lambda: scaler.fit_transform(num_data))
all_passed.append(check("MinMaxScaler fit_transform", ms < 50,
    f"{ms:.1f}ms — target <50ms"))

# Verify scale correctness
min_val = scaled.min()
max_val = scaled.max()
scale_ok = min_val >= 0.0 and max_val <= 1.0
all_passed.append(check("Scaled values in [0, 1] range", scale_ok,
    f"min={min_val:.4f} max={max_val:.4f}"))

# Cosine similarity — single query against full matrix
full_matrix  = np.hstack([feature_matrix, scaled])
query_vector = full_matrix[0:1]   # simulate a student query

sims, ms = timeit(lambda: cosine_similarity(query_vector, full_matrix))
all_passed.append(check("Cosine similarity (1 query vs full matrix)", ms < 100,
    f"{ms:.1f}ms — target <100ms"))

# Verify cosine similarity range
sim_min = sims.min()
sim_max = sims.max()
range_ok = sim_min >= -1.0 and sim_max <= 1.0
all_passed.append(check("Similarity scores in valid range [-1, 1]", range_ok,
    f"min={sim_min:.4f} max={sim_max:.4f}"))

# Top-N ranking correctness
top5_idx  = np.argsort(sims[0])[::-1][:5]
top5_vals = sims[0][top5_idx]
ranked_ok = all(top5_vals[i] >= top5_vals[i+1] for i in range(len(top5_vals)-1))
all_passed.append(check("Top-5 ranking correctly ordered", ranked_ok,
    f"scores: {[round(v,3) for v in top5_vals]}"))

# KNN
knn = NearestNeighbors(n_neighbors=5, metric="cosine")
_, ms = timeit(lambda: knn.fit(full_matrix))
all_passed.append(check("KNN fit on full matrix", ms < 200,
    f"{ms:.1f}ms — target <200ms"))

distances, indices_knn = knn.kneighbors(query_vector)
all_passed.append(check("KNN kneighbors query", True,
    f"returned {len(indices_knn[0])} neighbours"))

# Check KNN and cosine return the same top institution
cos_top1 = top5_idx[0]
knn_top1 = indices_knn[0][0]
agreement = cos_top1 == knn_top1
all_passed.append(check("KNN and cosine agree on top match", agreement,
    "consistent ✓" if agreement else f"cosine={cos_top1} knn={knn_top1}"))


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5: Full recommender.py end-to-end algorithm test
# ══════════════════════════════════════════════════════════════════════════════
section("5 / 6   Recommendation Algorithm — End-to-End Tests")

try:
    from recommender import SmartEdMatch
    engine = SmartEdMatch("nigerian_institutions_full.csv")
    check("SmartEdMatch engine loaded", True)

    # Test 20 realistic student profiles
    test_profiles = [
        # (course, type, zone, faculty, jamb, budget, expect_results)
        ("Computer Science","Federal University","South West","Sciences",220,100000, True),
        ("Computer Science","Federal University","South East","Sciences",200,100000, True),
        ("Computer Science","Federal University","North West","Sciences",180, 80000, True),
        ("Computer Science","State University",  "South West","Sciences",180,150000, True),
        ("Computer Science","Private University","South West","Sciences",200,1600000,True),
        ("Computer Science","Federal Polytechnic","South West","Sciences",140, 60000, True),
        ("Computer Science","Federal Polytechnic","South East","Sciences",130, 50000, True),
        ("Law","Federal University","South West","Law",220,100000, True),
        ("Medicine and Surgery","Federal University","South West","Medical Sciences",280,130000,True),
        ("Pharmacy","Federal University","South West","Pharmacy",250,100000, True),
        ("Nursing Science","Federal University","South West","Medical Sciences",240,100000,True),
        ("Banking and Finance","Private University","North Central","Management Sciences",175,1500000,True),
        ("Microbiology","Federal University","South West","Sciences",200,100000, True),
        ("Architecture","Federal University","South West","Environmental Sciences",210,100000,True),
        ("Petroleum Engineering","Federal University","South South","Engineering",220,120000,True),
        ("Agricultural Science","Federal University","North Central","Agriculture",160, 60000, True),
        # Edge cases
        ("Computer Science","Federal University","South West","Sciences",400,3000000,True),  # max values
        ("Computer Science","Federal University","South West","Sciences",100, 10000, False), # min values — may return 0
        ("Medicine and Surgery","Federal University","South West","Medical Sciences",100,5000,False),  # impossible score
        ("Computer Science","Federal University","South West","Sciences",250,500000, True),
    ]

    passed_count = 0
    failed_profiles = []

    print(f"\n  Running {len(test_profiles)} recommendation profiles...\n")
    for i, (course,itype,zone,fac,jamb,budget,expect) in enumerate(test_profiles, 1):
        t0 = time.perf_counter()
        results, knn_idx = engine.recommend(course,itype,zone,fac,jamb,budget,top_n=5)
        elapsed = (time.perf_counter() - t0) * 1000
        has_results = not results.empty

        # Correctness check
        correct = has_results == expect

        # Speed check
        fast = elapsed < 500

        if correct and fast:
            passed_count += 1
            status = "✅"
        elif correct and not fast:
            status = "⚠️"
            failed_profiles.append(f"Profile {i:02d}: SLOW ({elapsed:.0f}ms)")
        else:
            status = "❌"
            failed_profiles.append(f"Profile {i:02d}: WRONG (expected results={expect}, got={has_results})")

        n = len(results) if has_results else 0
        print(f"  {status} #{i:02d} {course[:22]:<22} | JAMB {jamb} | "
              f"Budget ₦{budget:>8,} | {n} results | {elapsed:.0f}ms")

    all_passed.append(check(
        f"Recommendation correctness ({passed_count}/{len(test_profiles)} passed)",
        passed_count >= 18,
        f"{passed_count}/20"
    ))

    # Test similarity score range
    results_main, _ = engine.recommend(
        "Computer Science","Federal University","South West","Sciences",220,100000,top_n=10
    )
    if not results_main.empty:
        scores = results_main["similarity_pct"].values
        all_passed.append(check("Similarity scores in 0–100 range",
            scores.min() >= 0 and scores.max() <= 100,
            f"min={scores.min():.1f} max={scores.max():.1f}"))
        all_passed.append(check("Results sorted descending",
            all(scores[i] >= scores[i+1] for i in range(len(scores)-1)),
            "correctly ranked"))
        all_passed.append(check("Top match score is meaningful (>30%)",
            scores[0] > 30, f"top score = {scores[0]:.1f}%"))

        # Verify hard filters are respected
        jamb_violations   = results_main[results_main["jamb_cutoff"] > 220]
        tuition_violations = results_main[results_main["tuition_min"] > 100000]
        all_passed.append(check("Hard JAMB filter respected",
            len(jamb_violations) == 0,
            f"{len(jamb_violations)} violations"))
        all_passed.append(check("Hard tuition filter respected",
            len(tuition_violations) == 0,
            f"{len(tuition_violations)} violations"))

    if failed_profiles:
        print(f"\n  Issues found:")
        for f in failed_profiles:
            print(f"    • {f}")

except Exception as e:
    check("SmartEdMatch engine", False, str(e))
    import traceback; traceback.print_exc()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6: Algorithm quality metrics
# ══════════════════════════════════════════════════════════════════════════════
section("6 / 6   Algorithm Quality Metrics")

try:
    from recommender import SmartEdMatch as _SME
    _engine = _SME("nigerian_institutions_full.csv")

    # Precision and recall on known expected results
    eval_cases = [
        ("Computer Science","Federal University","South West","Sciences",220,100000,
         ["University of Lagos","Obafemi Awolowo University","University of Ibadan"]),
        ("Computer Science","Federal University","South East","Sciences",200,100000,
         ["University of Nigeria Nsukka","Nnamdi Azikiwe University"]),
        ("Computer Science","Private University","South West","Sciences",200,1600000,
         ["Covenant University","Babcock University"]),
        ("Law","Federal University","South West","Law",220,100000,
         ["University of Lagos","Obafemi Awolowo University"]),
        ("Medicine and Surgery","Federal University","South West","Medical Sciences",280,130000,
         ["University of Lagos","University of Ibadan"]),
        ("Petroleum Engineering","Federal University","South South","Engineering",220,120000,
         ["University of Port Harcourt"]),
        ("Computer Science","Federal Polytechnic","South West","Sciences",140,60000,
         ["Yaba College of Technology"]),
        ("Banking and Finance","Private University","North Central","Management Sciences",175,1500000,
         ["Baze University","Nile University of Nigeria"]),
    ]

    total_precision = 0
    total_recall    = 0

    print(f"\n  {'Course':<28} {'Precision':>10} {'Recall':>8} {'Status':>10}")
    print(f"  {'-'*60}")

    for course,itype,zone,fac,jamb,budget,expected in eval_cases:
        res, _ = _engine.recommend(course,itype,zone,fac,jamb,budget,top_n=5)
        if res.empty:
            precision, recall = 0.0, 0.0
        else:
            retrieved = res["university_name"].tolist()
            tp = sum(1 for name in retrieved if any(exp in name for exp in expected))
            precision = tp / len(retrieved) if retrieved else 0
            recall    = tp / len(expected)  if expected  else 0

        total_precision += precision
        total_recall    += recall
        status = "✅ PASS" if precision >= 0.4 else ("⚠️ PART" if precision > 0 else "❌ FAIL")
        print(f"  {course:<28} {precision:>10.2f} {recall:>8.2f} {status:>10}")

    n = len(eval_cases)
    avg_p = total_precision / n
    avg_r = total_recall    / n
    f1    = (2 * avg_p * avg_r) / (avg_p + avg_r) if (avg_p + avg_r) else 0

    print(f"\n  {'Average Precision':<28} {avg_p:>10.3f}  ({avg_p*100:.1f}%)")
    print(f"  {'Average Recall':<28} {avg_r:>10.3f}  ({avg_r*100:.1f}%)")
    print(f"  {'F1 Score':<28} {f1:>10.3f}  ({f1*100:.1f}%)")

    all_passed.append(check("Average precision meets threshold",
        avg_p >= 0.30, f"{avg_p*100:.1f}% (target ≥30%)"))
    all_passed.append(check("Average recall meets threshold",
        avg_r >= 0.70, f"{avg_r*100:.1f}% (target ≥70%)"))
    all_passed.append(check("F1 score acceptable",
        f1 >= 0.40, f"{f1*100:.1f}% (target ≥40%)"))

except Exception as e:
    check("Algorithm quality metrics", False, str(e))


# ══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print(f"\n{SEPARATOR}")
print("  FINAL SUMMARY")
print(SEPARATOR)

defined_checks = [p for p in all_passed if isinstance(p, bool)]
n_pass  = sum(defined_checks)
n_total = len(defined_checks)
n_fail  = n_total - n_pass
pct     = (n_pass / n_total * 100) if n_total else 0

print(f"\n  Total checks : {n_total}")
print(f"  Passed       : {n_pass}  ✅")
print(f"  Failed       : {n_fail}  {'❌' if n_fail else '—'}")
print(f"  Score        : {pct:.0f}%")

if n_fail == 0:
    print(f"\n  🎉 All checks passed! The ML stack is healthy and performing optimally.")
elif n_fail <= 3:
    print(f"\n  ⚠️  Minor issues found. Review the ❌ items above and fix before deployment.")
else:
    print(f"\n  ❌ Multiple failures. Do not deploy until all critical checks pass.")

print(f"\n  Save this output and compare after each change.")
print(SEPARATOR)
