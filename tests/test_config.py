import pytest

from homesec.config import load_config

BASE_YAML = """
source_name: test_camera
video_source:
  type: webcam
  webcam_index: 2
detection:
  confidence_threshold: 0.7
alerts:
  telegram:
    enabled: true
    bot_token: "${TELEGRAM_BOT_TOKEN}"
    chat_id: "${TELEGRAM_CHAT_ID}"
"""


def test_load_config_resolves_env_vars(tmp_path, monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "secret-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "12345")
    config_path = tmp_path / "config.yaml"
    config_path.write_text(BASE_YAML)

    config = load_config(config_path, env_file=None)

    assert config.source_name == "test_camera"
    assert config.video_source.webcam_index == 2
    assert config.detection.confidence_threshold == 0.7
    assert config.alerts.telegram.bot_token == "secret-token"
    assert config.alerts.telegram.chat_id == "12345"


def test_load_config_raises_when_enabled_channel_missing_secret(tmp_path, monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    config_path = tmp_path / "config.yaml"
    config_path.write_text(BASE_YAML)

    with pytest.raises(ValueError, match="telegram.bot_token"):
        load_config(config_path, env_file=None)


def test_load_config_ignores_missing_env_var_for_disabled_channel(tmp_path, monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
    config_path = tmp_path / "config.yaml"
    config_path.write_text("""
video_source:
  type: webcam
alerts:
  telegram:
    enabled: false
    bot_token: "${TELEGRAM_BOT_TOKEN}"
    chat_id: "${TELEGRAM_CHAT_ID}"
""")

    config = load_config(config_path, env_file=None)

    assert config.alerts.telegram.enabled is False
    assert config.alerts.telegram.bot_token == ""


def test_file_source_requires_file_path(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("video_source:\n  type: file\n")

    with pytest.raises(ValueError, match="file_path"):
        load_config(config_path, env_file=None)
