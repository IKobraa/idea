"""The interface every alert channel implements."""

from __future__ import annotations

from typing import Protocol

from homesec.alerts.events import DetectionEvent


class Alerter(Protocol):
    def send(self, event: DetectionEvent) -> None: ...
