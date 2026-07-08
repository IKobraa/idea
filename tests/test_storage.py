from datetime import datetime

import numpy as np

from homesec.storage import SnapshotStore


def test_save_writes_jpeg_with_timestamped_filename(tmp_path):
    store = SnapshotStore(tmp_path)
    frame = np.zeros((10, 10, 3), dtype=np.uint8)
    timestamp = datetime(2026, 1, 2, 3, 4, 5, 678901)

    path = store.save(frame, timestamp)

    assert path.exists()
    assert path.parent == tmp_path
    assert path.name == "20260102_030405_678901.jpg"
