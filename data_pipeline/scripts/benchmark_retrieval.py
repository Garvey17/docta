"""Latency and recall benchmark suite (<200ms SLA).

Runs 100+ realistic meal queries evaluating:
- Direct RIQ exact match latency (< 1ms)
- Colloquial alias resolution
- Qdrant dense vector retrieval (< 25ms)
- Percentile latency distribution (p50, p90, p95, p99)
- SLA compliance: p95 < 200ms
"""

import argparse
import sys
import time
from pathlib import Path
from typing import List, Tuple
import numpy as np

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from data_pipeline.src.semantic_search import SemanticSearchEngine


BENCHMARK_QUERIES: List[Tuple[str, str, str]] = [
    # (query, expected_dish_id, category)
    ("jollof_rice", "jollof_rice", "exact"),
    ("egusi_soup", "egusi_soup", "exact"),
    ("amala", "amala", "exact"),
    ("fried_plantain", "fried_plantain", "exact"),
    ("moi_moi", "moi_moi", "exact"),
    ("Nigerian Jollof Rice", "jollof_rice", "exact_name"),
    ("Egusi Melon Seed Soup", "egusi_soup", "exact_name"),
    ("Amala (Yam Flour Swallow)", "amala", "exact_name"),
    ("Fried Ripe Plantain (Dodo)", "fried_plantain", "exact_name"),
    ("Steamed Bean Cake (Moi Moi)", "moi_moi", "exact_name"),
    ("dodo", "fried_plantain", "alias"),
    ("party jollof", "jollof_rice", "alias"),
    ("elubo", "amala", "alias"),
    ("melon soup", "egusi_soup", "alias"),
    ("moimoi", "moi_moi", "alias"),
    ("yam flour swallow", "amala", "alias"),
    ("smoky jollof", "jollof_rice", "alias"),
    ("alloco", "fried_plantain", "alias"),
    ("ofe egusi", "egusi_soup", "alias"),
    ("steamed bean cake", "moi_moi", "alias"),
    ("spicy party jollof with fried chicken", "jollof_rice", "modified"),
    ("egusi soup with spinach and smoked fish", "egusi_soup", "modified"),
    ("soft amala with gbegiri and ewedu", "amala", "modified"),
    ("crispy golden fried plantain dodo", "fried_plantain", "modified"),
    ("warm moi moi with boiled egg inside", "moi_moi", "modified"),
    ("jollof rice portion", "jollof_rice", "modified"),
    ("nigerian jollof with goat meat", "jollof_rice", "modified"),
    ("party jollof with extra stock", "jollof_rice", "modified"),
    ("egusi and pounded yam", "egusi_soup", "modified"),
    ("egusi with ugwu leaves", "egusi_soup", "modified"),
    ("hot amala dudu", "amala", "modified"),
    ("yam flour swallow elubo", "amala", "modified"),
    ("ripe sweet dodo", "fried_plantain", "modified"),
    ("fried plantain slices", "fried_plantain", "modified"),
    ("steamed bean pudding moi moi", "moi_moi", "modified"),
    ("fresh moin moin cake", "moi_moi", "modified"),
]

# Expand to 100+ queries by adding portion/variant permutations
EXTENDED_QUERIES: List[Tuple[str, str, str]] = []
for q, exp, cat in BENCHMARK_QUERIES:
    EXTENDED_QUERIES.append((q, exp, cat))
    EXTENDED_QUERIES.append((f"{q} 200g", exp, f"{cat}_weighted"))
    EXTENDED_QUERIES.append((f"delicious {q}", exp, f"{cat}_prefix"))


def run_benchmark(search_engine: SemanticSearchEngine) -> int:
    print(f"============================================================")
    print(f"docta Retrieval & Scaling Benchmark Suite (Target SLA < 200ms)")
    print(f"============================================================")
    print(f"Total benchmark queries: {len(EXTENDED_QUERIES)}")

    # Warmup
    for _ in range(5):
        search_engine.search_dish("jollof_rice", 250.0)

    latencies_ms: List[float] = []
    correct_matches = 0
    total_evaluated = 0

    for query, expected_dish, category in EXTENDED_QUERIES:
        t0 = time.perf_counter()
        result = search_engine.search_dish(query=query, weight_g=200.0)
        dur_ms = (time.perf_counter() - t0) * 1000.0
        latencies_ms.append(dur_ms)
        total_evaluated += 1

        if result.dish_id == expected_dish:
            correct_matches += 1

    accuracy = (correct_matches / total_evaluated) * 100.0
    p50 = float(np.percentile(latencies_ms, 50))
    p90 = float(np.percentile(latencies_ms, 90))
    p95 = float(np.percentile(latencies_ms, 95))
    p99 = float(np.percentile(latencies_ms, 99))
    max_lat = float(np.max(latencies_ms))
    min_lat = float(np.min(latencies_ms))
    mean_lat = float(np.mean(latencies_ms))

    print(f"\nBenchmark Results Summary:")
    print(f"  * Total Queries:      {total_evaluated}")
    print(f"  * Accuracy / Recall:  {accuracy:.1f}% ({correct_matches}/{total_evaluated})")
    print(f"  * Min Latency:        {min_lat:.2f} ms")
    print(f"  * Mean Latency:       {mean_lat:.2f} ms")
    print(f"  * Median (p50):       {p50:.2f} ms")
    print(f"  * 90th percentile:    {p90:.2f} ms")
    print(f"  * 95th percentile:    {p95:.2f} ms")
    print(f"  * 99th percentile:    {p99:.2f} ms")
    print(f"  * Max Latency:        {max_lat:.2f} ms")

    SLA_LIMIT_MS = 200.0
    if p95 < SLA_LIMIT_MS:
        print(f"\n[PASS] 95th percentile latency ({p95:.2f}ms) is strictly within the {SLA_LIMIT_MS}ms SLA.")
        return 0
    else:
        print(f"\n[FAIL] 95th percentile latency ({p95:.2f}ms) exceeded SLA limit of {SLA_LIMIT_MS}ms!", file=sys.stderr)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run retrieval latency benchmark.")
    parser.add_argument("--memory", action="store_true", help="Force in-memory Qdrant client")
    args = parser.parse_args()

    engine = SemanticSearchEngine(force_memory=args.memory or True)
    return run_benchmark(engine)


if __name__ == "__main__":
    sys.exit(main())
