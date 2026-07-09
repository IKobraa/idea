"""Sends detection alerts to a Telegram chat via the Bot HTTP API."""

from __future__ import annotations

import logging
from pathlib import Path

import requests

from homesec.alerts.events import DetectionEvent

logger = logging.getLogger("homesec.alerts.telegram")

_API_BASE = "https://api.telegram.org"


class TelegramAlerter:
    def __init__(self, bot_token: str, chat_id: str, timeout: float = 10.0) -> None:
        self._bot_token = bot_token
        self._chat_id = chat_id
        self._timeout = timeout

    def send(self, event: DetectionEvent) -> None:
        caption = (
            f"Person detected on {event.source_name} at {event.timestamp.isoformat()} "
            f"({len(event.detections)} detection(s))"
        )
        if event.snapshot_path is not None:
            self._send_photo(caption, event.snapshot_path)
        else:
            self._send_message(caption)

    def _send_message(self, text: str) -> None:
        url = f"{_API_BASE}/bot{self._bot_token}/sendMessage"
        response = requests.post(
            url, json={"chat_id": self._chat_id, "text": text}, timeout=self._timeout
        )
        response.raise_for_status()

    def _send_photo(self, caption: str, photo_path: Path) -> None:
        url = f"{_API_BASE}/bot{self._bot_token}/sendPhoto"
        with open(photo_path, "rb") as photo_file:
            response = requests.post(
                url,
                data={"chat_id": self._chat_id, "caption": caption},
                files={"photo": photo_file},
                timeout=self._timeout,
            )
        response.raise_for_status()
