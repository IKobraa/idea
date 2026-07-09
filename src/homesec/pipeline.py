"""Ties the video source, detector, storage, and alert dispatcher together."""

from __future__ import annotations

import logging
from datetime import datetime

from homesec.alerts.dispatcher import AlertDispatcher
from homesec.alerts.events import DetectionEvent
from homesec.detection.detector import PersonDetector
from homesec.detection.types import RawDetection
from homesec.preview import PreviewWindow
from homesec.storage import SnapshotStore
from homesec.video_source import VideoSource

logger = logging.getLogger("homesec.pipeline")


class DetectionPipeline:
    def __init__(
        self,
        source_name: str,
        video_source: VideoSource,
        detector: PersonDetector,
        snapshot_store: SnapshotStore,
        dispatcher: AlertDispatcher,
        frame_skip: int = 5,
        preview: PreviewWindow | None = None,
    ) -> None:
        self._source_name = source_name
        self._video_source = video_source
        self._detector = detector
        self._snapshot_store = snapshot_store
        self._dispatcher = dispatcher
        self._frame_skip = frame_skip
        self._preview = preview

    def run(self) -> None:
        logger.info("Starting detection pipeline for %s", self._source_name)
        last_detections: list[RawDetection] = []
        with self._video_source as source:
            for frame_index, frame in enumerate(source.frames()):
                if frame_index % self._frame_skip == 0:
                    last_detections = self._detector.detect(frame)
                    if last_detections:
                        timestamp = datetime.now()
                        snapshot_path = self._snapshot_store.save(frame, timestamp)
                        event = DetectionEvent(
                            source_name=self._source_name,
                            timestamp=timestamp,
                            detections=last_detections,
                            snapshot_path=snapshot_path,
                        )
                        self._dispatcher.dispatch(event)

                if self._preview is not None:
                    annotated = self._preview.draw(frame, last_detections)
                    if not self._preview.show(annotated):
                        logger.info("Preview window closed by user")
                        break

        if self._preview is not None:
            self._preview.close()
