"""Pipeline orchestration for frame analyzer v2."""

from __future__ import annotations

import os
import uuid
from typing import Dict, List

import cv2

from detector import detect_frame_events
from loader import load_video_frames
from renderer import render_annotated_video, save_motion_graph, save_results_csv


def _build_frame_rows(frames, detection: Dict) -> List[Dict]:
    """Convert frame data + detection output into table rows."""
    drop_set = set(detection["drop_indices"])
    merge_set = set(detection["merge_indices"])
    drop_counts = detection.get("drop_counts", {})
    motion_curve = detection["motion_curve"]

    rows: List[Dict] = []
    for i, frame in enumerate(frames):
        motion = motion_curve[i - 1] if i > 0 and i - 1 < len(motion_curve) else 0.0
        rows.append(
            {
                "frame_index": frame.index,
                "timestamp_ms": round(frame.timestamp_ms, 3),
                "gap_ms": round(frame.gap_ms, 3),
                "motion_diff": round(float(motion), 3),
                "is_drop": frame.index in drop_set,
                "dropped_count": int(drop_counts.get(frame.index, 0)),
                "is_merge": frame.index in merge_set,
            }
        )
    return rows


def run_pipeline(video_path: str, output_root: str) -> Dict:
    """Execute loading, detection, rendering, and summary generation."""
    run_id = uuid.uuid4().hex[:10]
    run_dir = os.path.join(output_root, run_id)
    os.makedirs(run_dir, exist_ok=True)

    frames = load_video_frames(video_path)
    detection = detect_frame_events(frames)

    rows = _build_frame_rows(frames, detection)

    csv_path = os.path.join(run_dir, "results.csv")
    video_path_out = os.path.join(run_dir, "annotated_video.mp4")
    graph_path = os.path.join(run_dir, "motion_graph.png")

    cap = cv2.VideoCapture(video_path)
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 24.0)
    cap.release()

    save_results_csv(rows, csv_path)
    render_annotated_video(
        frames=frames,
        drop_indices=detection["drop_indices"],
        merge_indices=detection["merge_indices"],
        output_path=video_path_out,
        fps=fps,
    )
    save_motion_graph(detection["motion_curve"], detection["smooth_curve"], graph_path)

    return {
        "run_id": run_id,
        "summary": {
            "total_frames": len(frames),
            "drop_events": len(detection["drop_indices"]),
            "estimated_dropped_frames": int(sum(detection.get("drop_counts", {}).values())),
            "merge_events": len(detection["merge_indices"]),
        },
        "csv_path": csv_path,
        "video_path": video_path_out,
        "graph_path": graph_path,
        "rows": rows,
    }
