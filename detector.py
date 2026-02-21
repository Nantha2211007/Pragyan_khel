"""Detection logic for frame drops and merges."""

from __future__ import annotations

from typing import Dict, List, Sequence

import numpy as np


TIME_DROP_RATIO = 1.9
MERGE_DIFF_THRESHOLD = 3.0
SMOOTH_WINDOW = 5


def _moving_average(values: Sequence[float], window: int) -> np.ndarray:
    """Simple centered moving average with edge padding."""
    arr = np.asarray(values, dtype=np.float32)
    if len(arr) == 0:
        return arr

    if window <= 1:
        return arr

    pad = window // 2
    padded = np.pad(arr, (pad, pad), mode="edge")
    kernel = np.ones(window, dtype=np.float32) / window
    smooth = np.convolve(padded, kernel, mode="valid")
    return smooth


def detect_frame_events(frames) -> Dict[str, List[float]]:
    """Run Kaushik-style frame drop and merge detection."""
    if len(frames) < 2:
        return {
            "drop_indices": [],
            "merge_indices": [],
            "motion_curve": [],
            "smooth_curve": [],
            "drop_counts": {},
        }

    gaps = np.array([f.gap_ms for f in frames[1:]], dtype=np.float32)
    positive_gaps = gaps[gaps > 0]
    median_gap = float(np.median(positive_gaps)) if len(positive_gaps) else 0.0

    motion_curve: List[float] = []
    merge_indices: List[int] = []

    for i in range(1, len(frames)):
        prev_gray = frames[i - 1].gray.astype(np.float32)
        curr_gray = frames[i].gray.astype(np.float32)
        diff = float(np.mean(np.abs(curr_gray - prev_gray)))
        motion_curve.append(diff)

        if diff < MERGE_DIFF_THRESHOLD:
            merge_indices.append(frames[i].index)

    smooth_curve = _moving_average(motion_curve, SMOOTH_WINDOW)

    drop_indices: List[int] = []
    drop_counts: Dict[int, int] = {}

    # Step 1: time-based detection.
    for i in range(1, len(frames)):
        if median_gap <= 0:
            continue
        ratio = frames[i].gap_ms / median_gap
        if ratio >= TIME_DROP_RATIO:
            dropped_count = max(1, int(round(ratio) - 1))
            drop_indices.append(frames[i].index)
            drop_counts[frames[i].index] = dropped_count

    # Step 2: motion fallback if no time drops were found.
    if not drop_indices and len(motion_curve) > 0:
        deviation = np.abs(np.asarray(motion_curve) - smooth_curve)
        threshold = float(np.percentile(deviation, 90))

        for i in range(1, len(frames)):
            if deviation[i - 1] > threshold:
                drop_indices.append(frames[i].index)
                drop_counts[frames[i].index] = 1

    return {
        "drop_indices": sorted(set(drop_indices)),
        "merge_indices": sorted(set(merge_indices)),
        "motion_curve": list(map(float, motion_curve)),
        "smooth_curve": list(map(float, smooth_curve)),
        "drop_counts": drop_counts,
    }
