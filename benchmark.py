"""
SmartEdMatch — Performance Benchmark
Run: python benchmark.py
Records timing for every critical operation so you can track improvements.
"""
import time
import statistics

SEPARATOR = "=" * 60

def timer(label, fn, runs=3):
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        result = fn()
        times.append(time.perf_counter() - t0)
    avg = statistics.mean(times)
    best = min(times)
    print(f"  {label:<45} avg={avg*1000:.0f}ms  best={best*1000:.0f}ms")
    return result, avg

print(SEPARATOR)
print("SmartEdMatch — Performance Benchmark")
print(SEPARATOR)

# ── 1. Engine load time ───────────────────────────────────────────────────────
print("\n[1] Engine initialisation")
from recommender import SmartEdMatch
_, engine_time = timer("Cold engine load (first run)", lambda: SmartEdMatch("nigerian_institutions_full.csv"))
engine = SmartEdMatch("nigerian_institutions_full.csv")
_, warm_time = timer("Warm engine load (cached)", lambda: SmartEdMatch("nigerian_institutions_full.csv"))

# ── 2. Recommendation speed ───────────────────────────────────────────────────
print("\n[2] Recommendation speed")
profiles = [
    ("Computer Science", "Federal University",  "South West",    "Sciences",          220, 100000),
    ("Law",              "State University",     "South West",    "Law",               200, 160000),
    ("Medicine and Surgery","Federal University","South West",    "Medical Sciences",  280, 130000),
    ("Engineering (Electrical)","Federal University","North West","Engineering",       190,  90000),
    ("Computer Science", "Any",                  "Any",           "Sciences",          200, 500000),
]
times = []
for profile in profiles:
    course, itype, zone, fac, jamb, tuition = profile
    t0 = time.perf_counter()
    results, _ = engine.recommend(course, itype, zone, fac, jamb, tuition, top_n=10)
    elapsed = time.perf_counter() - t0
    times.append(elapsed)
    status = "✅" if elapsed < 0.5 else "⚠️" if elapsed < 2.0 else "❌"
    print(f"  {status} {course:<30} {itype:<22} {elapsed*1000:.0f}ms  ({len(results)} results)")

print(f"\n  Average recommendation time : {statistics.mean(times)*1000:.0f}ms")
print(f"  Worst  recommendation time  : {max(times)*1000:.0f}ms")
print(f"  Target                      : <500ms")

# ── 3. Sentiment speed ────────────────────────────────────────────────────────
print("\n[3] Sentiment analysis speed (live sources)")
from sentiment_service import get_institution_sentiment

institutions = [
    "University of Lagos",
    "Covenant University",
    "Ahmadu Bello University",
    "University of Port Harcourt",
    "Baze University",
]
sent_times = []
for inst in institutions:
    t0 = time.perf_counter()
    result = get_institution_sentiment(inst)
    elapsed = time.perf_counter() - t0
    sent_times.append(elapsed)
    src = result["data_source"]
    live = "duckduckgo" in src or "wikipedia" in src
    badge = "🟢" if live else "📚"
    status = "✅" if elapsed < 3.0 else "⚠️" if elapsed < 8.0 else "❌"
    print(f"  {status} {badge} {inst:<40} {elapsed*1000:.0f}ms  [{src}]")

print(f"\n  First  call (uncached) avg : {statistics.mean(sent_times)*1000:.0f}ms")

# Second pass — should all be from cache
print("\n[4] Sentiment cache performance (second pass)")
cache_times = []
for inst in institutions:
    t0 = time.perf_counter()
    get_institution_sentiment(inst)
    elapsed = time.perf_counter() - t0
    cache_times.append(elapsed)
print(f"  Cached call avg            : {statistics.mean(cache_times)*1000:.0f}ms")
print(f"  Cache speedup              : {statistics.mean(sent_times)/statistics.mean(cache_times):.0f}x faster")

# ── 4. Concurrent sentiment simulation ───────────────────────────────────────
print("\n[5] Concurrent sentiment (simulating 5 simultaneous users)")
import threading
results_concurrent = []
errors_concurrent  = []

def fetch_sentiment(inst):
    try:
        t0 = time.perf_counter()
        get_institution_sentiment(inst)
        results_concurrent.append(time.perf_counter() - t0)
    except Exception as e:
        errors_concurrent.append(str(e))

threads = [threading.Thread(target=fetch_sentiment, args=(inst,)) for inst in institutions]
t0 = time.perf_counter()
for t in threads: t.start()
for t in threads: t.join()
total_concurrent = time.perf_counter() - t0

print(f"  5 concurrent calls finished in : {total_concurrent*1000:.0f}ms")
print(f"  Errors                         : {len(errors_concurrent)}")
if errors_concurrent:
    for e in errors_concurrent: print(f"    ❌ {e}")

# ── 5. Dataset stats ──────────────────────────────────────────────────────────
print("\n[6] Dataset stats")
import pandas as pd
df = pd.read_csv("nigerian_institutions_full.csv")
print(f"  Total records               : {len(df)}")
print(f"  Unique institutions         : {df['university_name'].nunique()}")
print(f"  Unique courses              : {df['course'].nunique()}")
print(f"  Unique zones                : {df['geopolitical_zone'].nunique()}")
print(f"  Available + accredited      : {len(df[(df['available']=='Yes') & (df['accredited']=='Yes')])}")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + SEPARATOR)
print("SUMMARY")
print(SEPARATOR)
rec_ok   = max(times) < 0.5
sent_ok  = statistics.mean(sent_times) < 5.0
cache_ok = statistics.mean(cache_times) < 0.05
print(f"  Recommendation speed  : {'✅ PASS' if rec_ok   else '❌ NEEDS OPTIMISATION'} (worst={max(times)*1000:.0f}ms, target <500ms)")
print(f"  Sentiment first call  : {'✅ PASS' if sent_ok  else '⚠️  SLOW'} (avg={statistics.mean(sent_times)*1000:.0f}ms, target <5000ms)")
print(f"  Sentiment cache hit   : {'✅ PASS' if cache_ok else '❌ CACHE NOT WORKING'} (avg={statistics.mean(cache_times)*1000:.0f}ms, target <50ms)")
print(SEPARATOR)
print("\nSave this output and compare after each optimisation run.")
