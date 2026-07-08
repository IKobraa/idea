"""Builds pipeline components from a validated :class:`AppConfig`."""

from __future__ import annotations

from homesec.alerts.base import Alerter
from homesec.alerts.dispatcher import AlertDispatcher
from homesec.alerts.email_alerter import EmailAlerter
from homesec.alerts.logging_alerter import LoggingAlerter
from homesec.alerts.telegram_alerter import TelegramAlerter
from homesec.config import AlertsConfig, AppConfig, DetectionConfig
from homesec.detection.detector import PersonDetector
from homesec.detection.yolo_backend import YoloBackend
from homesec.pipeline import DetectionPipeline
from homesec.storage import SnapshotStore
from homesec.video_source import create_video_source


def build_detector(config: DetectionConfig) -> PersonDetector:
    backend = YoloBackend(config.model_weights)
    return PersonDetector(backend, confidence_threshold=config.confidence_threshold)


def build_alerters(config: AlertsConfig) -> list[Alerter]:
    alerters: list[Alerter] = []
    if config.logging.enabled:
        alerters.append(LoggingAlerter())
    if config.telegram.enabled:
        assert config.telegram.bot_token and config.telegram.chat_id
        alerters.append(TelegramAlerter(config.telegram.bot_token, config.telegram.chat_id))
    if config.email.enabled:
        assert config.email.smtp_host and config.email.from_addr
        alerters.append(
            EmailAlerter(
                smtp_host=config.email.smtp_host,
                smtp_port=config.email.smtp_port,
                from_addr=config.email.from_addr,
                to_addrs=config.email.to_addrs,
                username=config.email.username,
                password=config.email.password,
            )
        )
    return alerters


def build_pipeline(config: AppConfig) -> DetectionPipeline:
    return DetectionPipeline(
        source_name=config.source_name,
        video_source=create_video_source(config.video_source),
        detector=build_detector(config.detection),
        snapshot_store=SnapshotStore(config.storage.snapshot_dir),
        dispatcher=AlertDispatcher(
            build_alerters(config.alerts), cooldown_seconds=config.alerts.cooldown_seconds
        ),
        frame_skip=config.detection.frame_skip,
    )
