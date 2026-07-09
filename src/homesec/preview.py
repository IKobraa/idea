"""Optional live preview window with detection boxes drawn, for local testing.

Only used when ``--show`` is passed on the CLI. Requires a display (GTK/Cocoa/
X11) to be available — don't enable it on headless servers.
"""

from __future__ import annotations

import cv2
import numpy as np

from homesec.detection.types import RawDetection

WINDOW_NAME = "homesec preview (press q to quit)"
BOX_COLOR = (0, 0, 255)


class PreviewWindow:
    def draw(self, frame: np.ndarray, detections: list[RawDetection]) -> np.ndarray:
        annotated = frame.copy()
        for detection in detections:
            x1, y1, x2, y2 = (int(v) for v in detection.bbox)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), BOX_COLOR, 2)
            label = f"{detection.label} {detection.confidence:.2f}"
            cv2.putText(
                annotated,
                label,
                (x1, max(y1 - 8, 0)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                BOX_COLOR,
                2,
            )
        return annotated

    def show(self, frame: np.ndarray) -> bool:
        """Display ``frame``; returns False once the user asks to quit (q/Esc)."""
        cv2.imshow(WINDOW_NAME, frame)
        return cv2.waitKey(1) & 0xFF not in (ord("q"), 27)

    def close(self) -> None:
        cv2.destroyWindow(WINDOW_NAME)
