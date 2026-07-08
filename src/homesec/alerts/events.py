"""The event object passed from the detection pipeline to alerters."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from homesec.detection.types import RawDetection


@dataclass(frozen=True)
class DetectionEvent:
    source_name: str
    timestamp: datetime
    detections: list[RawDetection]
    snapshot_path: Path | None = None
