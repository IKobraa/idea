"""Saves detection snapshots to disk."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import cv2
import numpy as np


class SnapshotStore:
    def __init__(self, output_dir: str | Path) -> None:
        self._output_dir = Path(output_dir)

    def save(self, frame: np.ndarray, timestamp: datetime) -> Path:
        self._output_dir.mkdir(parents=True, exist_ok=True)
        filename = timestamp.strftime("%Y%m%d_%H%M%S_%f") + ".jpg"
        path = self._output_dir / filename
        cv2.imwrite(str(path), frame)
        return path
