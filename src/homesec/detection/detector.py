"""Filters raw model detections down to confident person sightings."""

from __future__ import annotations

from typing import Protocol

import numpy as np

from homesec.detection.types import RawDetection

PERSON_LABEL = "person"


class DetectionBackend(Protocol):
    def infer(self, frame: np.ndarray) -> list[RawDetection]: ...


class PersonDetector:
    def __init__(self, backend: DetectionBackend, confidence_threshold: float = 0.5) -> None:
        self._backend = backend
        self._confidence_threshold = confidence_threshold

    def detect(self, frame: np.ndarray) -> list[RawDetection]:
        return [
            detection
            for detection in self._backend.infer(frame)
            if detection.label == PERSON_LABEL
            and detection.confidence >= self._confidence_threshold
        ]
