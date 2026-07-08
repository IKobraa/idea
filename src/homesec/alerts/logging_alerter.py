"""Records detection events to the standard logging module."""

from __future__ import annotations

import logging

from homesec.alerts.events import DetectionEvent

logger = logging.getLogger("homesec.alerts.logging")


class LoggingAlerter:
    def send(self, event: DetectionEvent) -> None:
        logger.info(
            "Person detected on %s at %s (%d detection(s), snapshot=%s)",
            event.source_name,
            event.timestamp.isoformat(),
            len(event.detections),
            event.snapshot_path,
        )
