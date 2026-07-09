"""Sends detection alerts by email, with the snapshot attached if available."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from homesec.alerts.events import DetectionEvent

logger = logging.getLogger("homesec.alerts.email")


class EmailAlerter:
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        from_addr: str,
        to_addrs: list[str],
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._from_addr = from_addr
        self._to_addrs = to_addrs
        self._username = username
        self._password = password

    def send(self, event: DetectionEvent) -> None:
        message = EmailMessage()
        message["Subject"] = f"Person detected on {event.source_name}"
        message["From"] = self._from_addr
        message["To"] = ", ".join(self._to_addrs)
        message.set_content(
            f"Person detected on {event.source_name} at {event.timestamp.isoformat()} "
            f"({len(event.detections)} detection(s))."
        )
        if event.snapshot_path is not None:
            image_bytes = event.snapshot_path.read_bytes()
            message.add_attachment(
                image_bytes,
                maintype="image",
                subtype="jpeg",
                filename=event.snapshot_path.name,
            )

        with smtplib.SMTP(self._smtp_host, self._smtp_port) as smtp:
            smtp.starttls()
            if self._username and self._password:
                smtp.login(self._username, self._password)
            smtp.send_message(message)
