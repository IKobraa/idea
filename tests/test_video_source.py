import pytest

from homesec.config import VideoSourceConfig
from homesec.video_source import create_video_source


def test_webcam_source_uses_index():
    source = create_video_source(VideoSourceConfig(type="webcam", webcam_index=3))
    assert source._capture_target == 3


def test_file_source_uses_path():
    source = create_video_source(VideoSourceConfig(type="file", file_path="clip.mp4"))
    assert source._capture_target == "clip.mp4"


def test_rtsp_source_uses_url():
    source = create_video_source(
        VideoSourceConfig(type="rtsp", rtsp_url="rtsp://camera.local/stream")
    )
    assert source._capture_target == "rtsp://camera.local/stream"


def test_open_raises_when_capture_fails(monkeypatch):
    import cv2

    class FakeCapture:
        def isOpened(self):
            return False

    monkeypatch.setattr(cv2, "VideoCapture", lambda target: FakeCapture())
    source = create_video_source(VideoSourceConfig(type="webcam", webcam_index=0))

    with pytest.raises(RuntimeError):
        source.open()
