from homesec.detection.detector import PersonDetector
from homesec.detection.types import RawDetection


class FakeBackend:
    def __init__(self, detections):
        self._detections = detections

    def infer(self, frame):
        return self._detections


def test_detect_filters_to_person_label_above_threshold():
    backend = FakeBackend(
        [
            RawDetection("person", 0.9, (0, 0, 10, 10)),
            RawDetection("dog", 0.95, (0, 0, 10, 10)),
            RawDetection("person", 0.2, (0, 0, 10, 10)),
        ]
    )
    detector = PersonDetector(backend, confidence_threshold=0.5)

    detections = detector.detect(frame=None)

    assert detections == [RawDetection("person", 0.9, (0, 0, 10, 10))]


def test_detect_returns_empty_when_no_person():
    backend = FakeBackend([RawDetection("cat", 0.99, (0, 0, 10, 10))])
    detector = PersonDetector(backend, confidence_threshold=0.5)

    assert detector.detect(frame=None) == []
