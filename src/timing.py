"""
Timing utilities for performance debugging.
"""

import functools
import time
from collections import defaultdict
from typing import Dict, List

# Global statistics storage
_timing_stats: Dict[str, List[float]] = defaultdict(list)
_timing_counts: Dict[str, int] = defaultdict(int)


def timing_decorator(func):
    """
    Decorator to measure and log function execution time.

    Usage:
        @timing_decorator
        def my_function():
            ...
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed = end_time - start_time

        # Store statistics
        func_name = func.__name__
        _timing_stats[func_name].append(elapsed)
        _timing_counts[func_name] += 1

        # Print if execution time is significant (> 0.1 seconds)
        if elapsed > 0.1:
            pass
            # print(f"[TIMING] {func_name}: {elapsed:.4f}s")

        return result

    return wrapper


def get_timing_stats() -> Dict[str, Dict[str, float]]:
    """
    Get timing statistics for all timed functions.

    Returns:
        Dictionary mapping function names to statistics (min, max, avg, total, count)
    """
    stats = {}
    for func_name, times in _timing_stats.items():
        if times:
            stats[func_name] = {
                "min": min(times),
                "max": max(times),
                "avg": sum(times) / len(times),
                "total": sum(times),
                "count": _timing_counts[func_name],
            }
    return stats


def print_timing_summary():
    """Print a summary of all timing statistics."""
    stats = get_timing_stats()
    if not stats:
        print("No timing statistics available.")
        return

    print("\n" + "=" * 80)
    print("TIMING SUMMARY")
    print("=" * 80)
    print(
        f"{'Function':<40} {'Count':<10} {'Total (s)':<12} {'Avg (s)':<12} {'Min (s)':<12} {'Max (s)':<12}"
    )
    print("-" * 80)

    # Sort by total time (descending)
    sorted_stats = sorted(stats.items(), key=lambda x: x[1]["total"], reverse=True)

    for func_name, stat in sorted_stats:
        print(
            f"{func_name:<40} {stat['count']:<10} {stat['total']:<12.4f} "
            f"{stat['avg']:<12.4f} {stat['min']:<12.4f} {stat['max']:<12.4f}"
        )

    print("=" * 80)
    print()


def reset_timing_stats():
    """Reset all timing statistics."""
    global _timing_stats, _timing_counts
    _timing_stats.clear()
    _timing_counts.clear()
