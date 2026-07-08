"""Load and validate application configuration from YAML.

Config files may reference environment variables with ``${VAR_NAME}``
placeholders (typically for secrets such as bot tokens or SMTP
credentials). Placeholders are resolved before YAML parsing, using a
``.env`` file (if present) in addition to the process environment.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Literal

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator

_ENV_VAR_PATTERN = re.compile(r"\$\{(\w+)\}")


class VideoSourceConfig(BaseModel):
    type: Literal["webcam", "file", "rtsp"]
    webcam_index: int = 0
    file_path: str | None = None
    rtsp_url: str | None = None

    @model_validator(mode="after")
    def _check_required_field(self) -> VideoSourceConfig:
        if self.type == "file" and not self.file_path:
            raise ValueError("video_source.file_path is required when type is 'file'")
        if self.type == "rtsp" and not self.rtsp_url:
            raise ValueError("video_source.rtsp_url is required when type is 'rtsp'")
        return self


class DetectionConfig(BaseModel):
    model_weights: str = "yolov8n.pt"
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    frame_skip: int = Field(default=5, ge=1)


class TelegramConfig(BaseModel):
    enabled: bool = False
    bot_token: str | None = None
    chat_id: str | None = None

    @model_validator(mode="after")
    def _check_required_fields(self) -> TelegramConfig:
        if self.enabled and not (self.bot_token and self.chat_id):
            raise ValueError("telegram.bot_token and telegram.chat_id are required when enabled")
        return self


class EmailConfig(BaseModel):
    enabled: bool = False
    smtp_host: str | None = None
    smtp_port: int = 587
    username: str | None = None
    password: str | None = None
    from_addr: str | None = None
    to_addrs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_required_fields(self) -> EmailConfig:
        if self.enabled and not (self.smtp_host and self.from_addr and self.to_addrs):
            raise ValueError(
                "email.smtp_host, email.from_addr and email.to_addrs are required when enabled"
            )
        return self


class LoggingAlertConfig(BaseModel):
    enabled: bool = True


class AlertsConfig(BaseModel):
    cooldown_seconds: float = Field(default=30.0, ge=0.0)
    logging: LoggingAlertConfig = Field(default_factory=LoggingAlertConfig)
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)


class StorageConfig(BaseModel):
    snapshot_dir: str = "snapshots"


class AppConfig(BaseModel):
    source_name: str = "camera1"
    video_source: VideoSourceConfig
    detection: DetectionConfig = Field(default_factory=DetectionConfig)
    alerts: AlertsConfig = Field(default_factory=AlertsConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)


def _resolve_env_vars(raw_text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        var_name = match.group(1)
        value = os.environ.get(var_name)
        if value is None:
            raise ValueError(f"Config references undefined environment variable: {var_name}")
        return value

    return _ENV_VAR_PATTERN.sub(replace, raw_text)


def load_config(path: str | Path, *, env_file: str | Path | None = ".env") -> AppConfig:
    """Load an :class:`AppConfig` from a YAML file at ``path``.

    Loads ``env_file`` (if it exists) before resolving ``${VAR}``
    placeholders so secrets can be kept out of the YAML file.
    """
    if env_file is not None:
        load_dotenv(env_file, override=False)

    raw_text = Path(path).read_text()
    resolved_text = _resolve_env_vars(raw_text)
    data = yaml.safe_load(resolved_text) or {}
    return AppConfig.model_validate(data)
