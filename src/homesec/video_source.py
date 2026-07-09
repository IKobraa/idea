"""Video frame acquisition from a webcam, video file, or RTSP stream."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import cv2
import numpy as np

from homesec.config import VideoSourceConfig


class VideoSource:
    """Wraps a ``cv2.VideoCapture`` target with a simple frame iterator."""

    def __init__(self, capture_target: int | str) -> None:
        self._capture_target = capture_target
        self._capture: cv2.VideoCapture | None = None

    def open(self) -> None:
        self._capture = cv2.VideoCapture(self._capture_target)
        if not self._capture.isOpened():
            raise RuntimeError(f"Failed to open video source: {self._capture_target}")

    def frames(self) -> Iterator[np.ndarray]:
        """Yield frames until the source is exhausted or closed."""
        if self._capture is None:
            self.open()
        assert self._capture is not None
        while True:
            ok, frame = self._capture.read()
            if not ok:
                return
            yield frame

    def close(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def __enter__(self) -> VideoSource:
        self.open()
        return self

    def __exit__(self, *exc_info: Any) -> None:
        self.close()


def create_video_source(config: VideoSourceConfig) -> VideoSource:
    """Build a :class:`VideoSource` for the target described by ``config``."""
    target: int | str
    if config.type == "webcam":
        target = config.webcam_index
    elif config.type == "file":
        assert config.file_path is not None
        target = config.file_path
    elif config.type == "rtsp":
        assert config.rtsp_url is not None
        target = config.rtsp_url
    else:  # pragma: no cover - guarded by pydantic Literal
        raise ValueError(f"Unknown video source type: {config.type}")
    return VideoSource(target)
