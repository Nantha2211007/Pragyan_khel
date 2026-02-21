"""Video loading helpers for frame analyzer v2."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import cv2
import numpy as np


@dataclass
class FrameInfo:
    """Container for frame metadata used by the detection pipeline."""

    index: int
    timestamp_ms: float
    gap_ms: float
    bgr: np.ndarray
    gray: np.ndarray


def load_video_frames(video_path: str) -> List[FrameInfo]:
    """Load frames, grayscale versions, and timing gaps from a video."""
    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        raise ValueError(f"Unable to open video: {video_path}")

    frames: List[FrameInfo] = []
    prev_timestamp = None

    while True:
        ok, frame = capture.read()
        if not ok:
            break

        frame_index = int(capture.get(cv2.CAP_PROP_POS_FRAMES)) - 1
        timestamp_ms = float(capture.get(cv2.CAP_PROP_POS_MSEC))

        if prev_timestamp is None:
            gap_ms = 0.0
        else:
            gap_ms = max(0.0, timestamp_ms - prev_timestamp)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frames.append(
            FrameInfo(
                index=frame_index,
                timestamp_ms=timestamp_ms,
                gap_ms=gap_ms,
                bgr=frame,
                gray=gray,
            )
        )
        prev_timestamp = timestamp_ms

    capture.release()

    if not frames:
        raise ValueError("The uploaded video contains no readable frames.")

    return frames
