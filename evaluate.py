"""
SmartEdMatch Evaluation Script
Runs 20 test cases and computes Precision, Recall, and Accuracy
"""
import pandas as pd
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from recommender import SmartEdMatch

engine = SmartEdMatch("nigerian_institutions_full.csv")

# ── 20 Test Cases ─────────────────────────────────────────────────────────────
# Format: (course, type, zone, faculty, jamb_score, max_tuition, expected_keywords)
test_cases = [
    ("Computer Science", "Federal University",   "South West",    "Sciences",          220, 100000,  ["University of Lagos", "Obafemi Awolowo University"]),
    ("Computer Science", "Federal University",   "South East",    "Sciences",          200, 100000,  ["University of Nigeria Nsukka", "Nnamdi Azikiwe University"]),
    ("Computer Science", "Federal University",   "North West",    "Sciences",          180, 80000,   ["Ahmadu Bello University", "Bayero University Kano"]),
    ("Computer Science", "State University",     "South West",    "Sciences",          180, 150000,  ["Lagos State University", "Ekiti State University"]),
    ("Computer Science", "Private University",   "South West",    "Sciences",          200, 1600000, ["Covenant University", "Babcock University"]),
    ("Computer Science", "Federal Polytechnic",  "South West",    "Sciences",          140, 60000,   ["Yaba College of Technology", "Federal Polytechnic Ilaro"]),
    ("Computer Science", "Federal Polytechnic",  "South East",    "Sciences",          130, 50000,   ["Federal Polytechnic Nekede", "Federal Polytechnic Oko"]),
    ("Computer Science", "Federal College of Education", "North West", "Sciences",     100, 35000,   ["Federal College of Education Zaria", "Federal College of Education Kano"]),
    ("Law",              "Federal University",   "South West",    "Law",               220, 100000,  ["University of Lagos", "Obafemi Awolowo University"]),
    ("Law",              "State University",     "South West",    "Law",               200, 160000,  ["Lagos State University"]),
    ("Medicine and Surgery", "Federal University", "South West",  "Medical Sciences",  280, 130000,  ["University of Lagos", "University of Ibadan"]),
    ("Medicine and Surgery", "Private University","South West",   "Medical Sciences",  240, 2500000, ["Covenant University", "Babcock University"]),
    ("Accounting",       "Federal University",   "South East",    "Management Sciences",180,100000,  ["Nnamdi Azikiwe University", "University of Nigeria Nsukka"]),
    ("Accounting",       "State University",     "North Central", "Management Sciences",160,70000,   ["Kogi State University"]),
    ("Engineering (Electrical)", "Federal University","North West","Engineering",      190, 90000,   ["Kano State University of Science", "University of Ilorin"]),
    ("Petroleum Engineering","Federal University","South South",  "Engineering",       220, 120000,  ["University of Port Harcourt", "Rivers State University"]),
    ("Agricultural Science","Federal University","North Central", "Agriculture",       160, 60000,   ["Federal University Lafia", "Ahmadu Bello University"]),
    ("Computer Science", "Private University",   "North Central", "Sciences",         175, 1500000, ["Nile University of Nigeria", "Baze University"]),
    ("Computer Science Education","Federal College of Education","South West","Sciences",100,35000,  ["Federal College of Education Abeokuta", "Adeyemi College of Education"]),
    ("Computer Science", "State Polytechnic",    "South West",   "Sciences",          130, 55000,   ["The Polytechnic Ibadan", "Lagos State Polytechnic"]),
]

print("=" * 70)
print("SmartEdMatch — System Evaluation Report")
print("=" * 70)

results_summary = []
total_precision = 0
total_recall = 0

for i, (course, inst_type, zone, faculty, jamb, tuition, expected) in enumerate(test_cases, 1):
    results, _ = engine.recommend(course, inst_type, zone, faculty, jamb, tuition, top_n=5)

    if results.empty:
        precision = 0.0
        recall = 0.0
        retrieved = []
    else:
        retrieved = results["university_name"].tolist()
        # True positives: recommended institutions matching expected keywords
        tp = sum(1 for name in retrieved if any(exp in name for exp in expected))
        precision = tp / len(retrieved) if retrieved else 0
        recall = tp / len(expected) if expected else 0

    total_precision += precision
    total_recall += recall

    status = "✅ PASS" if precision >= 0.4 else "⚠️ PARTIAL" if precision > 0 else "❌ FAIL"
    results_summary.append({
        "Test": i,
        "Course": course,
        "Type": inst_type,
        "Zone": zone,
        "JAMB": jamb,
        "Budget": f"₦{tuition:,}",
        "Precision": f"{precision:.2f}",
        "Recall": f"{recall:.2f}",
        "Status": status,
        "Top Match": retrieved[0] if retrieved else "None"
    })

    print(f"\nTest {i:02d}: {course} | {inst_type} | {zone}")
    print(f"  JAMB: {jamb} | Budget: ₦{tuition:,}")
    print(f"  Top Results: {retrieved[:3]}")
    print(f"  Precision: {precision:.2f} | Recall: {recall:.2f} | {status}")

# ── Summary Metrics ───────────────────────────────────────────────────────────
avg_precision = total_precision / len(test_cases)
avg_recall = total_recall / len(test_cases)
f1 = (2 * avg_precision * avg_recall) / (avg_precision + avg_recall) if (avg_precision + avg_recall) > 0 else 0
passes = sum(1 for r in results_summary if "PASS" in r["Status"])
accuracy = passes / len(test_cases)

print("\n" + "=" * 70)
print("EVALUATION SUMMARY")
print("=" * 70)
print(f"Total Test Cases     : {len(test_cases)}")
print(f"Passed               : {passes}")
print(f"Average Precision    : {avg_precision:.4f} ({avg_precision*100:.1f}%)")
print(f"Average Recall       : {avg_recall:.4f} ({avg_recall*100:.1f}%)")
print(f"F1 Score             : {f1:.4f} ({f1*100:.1f}%)")
print(f"System Accuracy      : {accuracy:.4f} ({accuracy*100:.1f}%)")
print("=" * 70)

# Save to CSV
df_summary = pd.DataFrame(results_summary)
df_summary.to_csv("evaluation_results.csv", index=False)
print("\n✅ Evaluation results saved to evaluation_results.csv")
