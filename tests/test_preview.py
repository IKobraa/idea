import numpy as np

from homesec.detection.types import RawDetection
from homesec.preview import PreviewWindow


def test_draw_returns_frame_of_same_shape_with_no_detections():
    window = PreviewWindow()
    frame = np.zeros((20, 30, 3), dtype=np.uint8)

    annotated = window.draw(frame, [])

    assert annotated.shape == frame.shape
    assert annotated is not frame


def test_draw_paints_box_pixels_for_a_detection():
    window = PreviewWindow()
    frame = np.zeros((20, 30, 3), dtype=np.uint8)
    detections = [RawDetection("person", 0.9, (2.0, 2.0, 10.0, 10.0))]

    annotated = window.draw(frame, detections)

    assert annotated.shape == frame.shape
    assert annotated.any()
