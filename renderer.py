"""Result rendering helpers for CSV, annotated video, and graph output."""

from __future__ import annotations

import csv
import os
from typing import Dict, Iterable, List

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


DROP_COLOR = (0, 0, 255)  # red in BGR
MERGE_COLOR = (0, 255, 255)  # yellow in BGR
TEXT_COLOR = (240, 240, 240)


def save_results_csv(rows: Iterable[Dict], csv_path: str) -> None:
    """Save frame-level results to CSV."""
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    rows = list(rows)
    fieldnames = [
        "frame_index",
        "timestamp_ms",
        "gap_ms",
        "motion_diff",
        "is_drop",
        "dropped_count",
        "is_merge",
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_annotated_video(
    frames,
    drop_indices: List[int],
    merge_indices: List[int],
    output_path: str,
    fps: float,
) -> None:
    """Write annotated output video with frame labels."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    height, width = frames[0].bgr.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps if fps > 0 else 24.0, (width, height))

    drop_set = set(drop_indices)
    merge_set = set(merge_indices)

    for frame in frames:
        out_frame = frame.bgr.copy()
        y = 30

        cv2.putText(
            out_frame,
            f"Frame: {frame.index}",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            TEXT_COLOR,
            2,
            cv2.LINE_AA,
        )

        if frame.index in drop_set:
            y += 36
            cv2.putText(out_frame, "DROP", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, DROP_COLOR, 3, cv2.LINE_AA)

        if frame.index in merge_set:
            y += 36
            cv2.putText(out_frame, "MERGE", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, MERGE_COLOR, 3, cv2.LINE_AA)

        writer.write(out_frame)

    writer.release()


def save_motion_graph(motion_curve: List[float], smooth_curve: List[float], graph_path: str) -> None:
    """Save motion and smooth curves as a PNG graph."""
    os.makedirs(os.path.dirname(graph_path), exist_ok=True)

    plt.figure(figsize=(11, 4.5))
    plt.plot(motion_curve, label="Motion curve", linewidth=1.2)
    plt.plot(smooth_curve, label="Moving average (window=5)", linewidth=1.2)
    plt.title("Frame-to-frame Motion")
    plt.xlabel("Frame transition index")
    plt.ylabel("Mean absolute difference")
    plt.legend()
    plt.tight_layout()
    plt.savefig(graph_path, dpi=140)
    plt.close()
