"""Adapts an Ultralytics YOLO model to the detection backend interface.

Ultralytics (and its ``torch`` dependency) is imported lazily inside
:meth:`YoloBackend.__init__` so that modules which don't need object
detection (config, alerts, CLI parsing, ...) stay fast to import, and so
unit tests can exercise :class:`~homesec.detection.detector.PersonDetector`
against a fake backend without the real dependency installed.
"""

from __future__ import annotations

import numpy as np

from homesec.detection.types import RawDetection


class YoloBackend:
    """Runs inference with a YOLO model and yields :class:`RawDetection`."""

    def __init__(self, weights_path: str) -> None:
        from ultralytics import YOLO

        self._model = YOLO(weights_path)

    def infer(self, frame: np.ndarray) -> list[RawDetection]:
        results = self._model(frame, verbose=False)[0]
        detections: list[RawDetection] = []
        for box in results.boxes:
            class_id = int(box.cls[0])
            label = self._model.names[class_id]
            confidence = float(box.conf[0])
            x1, y1, x2, y2 = (float(v) for v in box.xyxy[0].tolist())
            detections.append(RawDetection(label, confidence, (x1, y1, x2, y2)))
        return detections
