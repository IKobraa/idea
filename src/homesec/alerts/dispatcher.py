"""Fans a detection event out to every configured alerter, with a cooldown.

The cooldown prevents alert spam (e.g. one message per video frame) by
suppressing dispatch for a source until ``cooldown_seconds`` have elapsed
since its last alert.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable

from homesec.alerts.base import Alerter
from homesec.alerts.events import DetectionEvent

logger = logging.getLogger("homesec.alerts.dispatcher")


class AlertDispatcher:
    def __init__(
        self,
        alerters: list[Alerter],
        cooldown_seconds: float = 30.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._alerters = alerters
        self._cooldown_seconds = cooldown_seconds
        self._clock = clock
        self._last_dispatch_at: dict[str, float] = {}

    def dispatch(self, event: DetectionEvent) -> bool:
        """Send ``event`` to every alerter unless still within cooldown.

        Returns whether the event was actually dispatched.
        """
        now = self._clock()
        last_at = self._last_dispatch_at.get(event.source_name)
        if last_at is not None and now - last_at < self._cooldown_seconds:
            return False

        self._last_dispatch_at[event.source_name] = now
        for alerter in self._alerters:
            try:
                alerter.send(event)
            except Exception:
                logger.exception("Alerter %s failed to send event", type(alerter).__name__)
        return True
