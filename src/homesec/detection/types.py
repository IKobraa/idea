"""Shared types for the detection pipeline."""

from __future__ import annotations

from typing import NamedTuple


class RawDetection(NamedTuple):
    """A single object detected in a frame, before any filtering."""

    label: str
    confidence: float
    bbox: tuple[float, float, float, float]  # x1, y1, x2, y2
