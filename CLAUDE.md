# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

`homesec` is a person-detection and alerting system for a home security setup. It reads frames
from a video source (webcam, video file, or RTSP camera), runs a YOLO person detector on them,
saves a snapshot when a person is found, and dispatches alerts (Telegram, email, local logging)
subject to a per-source cooldown.

## Commands

```bash
# Setup (editable install with dev deps: pytest, ruff)
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Tests
pytest                          # full suite
pytest tests/test_dispatcher.py # single file
pytest tests/test_detector.py::test_detect_filters_to_person_label_above_threshold  # single test

# Lint
ruff check .
ruff check . --fix

# Run the app (requires config/config.yaml, copied from config.example.yaml)
homesec --config config/config.yaml
# equivalently: python -m homesec.cli --config config/config.yaml

# with a live preview window (detection boxes drawn, requires a local display)
homesec --config config/config.yaml --show
```

There is no configured type checker or CI pipeline yet.

## Architecture

Package lives under `src/homesec` (src-layout, installed via `pyproject.toml` as the `homesec`
console script). Data flows through a fixed pipeline of small, independently testable stages
wired together by `factory.py`:

```
config.yaml --config.load_config--> AppConfig
                                        |
                                   factory.build_pipeline
                                        |
video_source.VideoSource --frames--> detection.PersonDetector --DetectionEvent--> alerts.AlertDispatcher --> [LoggingAlerter, TelegramAlerter, EmailAlerter]
        ^                                    ^                         |
        |                                    |                    storage.SnapshotStore
   cv2.VideoCapture                    detection.YoloBackend
   (webcam/file/rtsp)                  (ultralytics YOLO, lazy import)
```

Key seams to know about when modifying behavior:

- **`config.py`** — single source of truth for validated settings (pydantic models). Config
  files may reference `${ENV_VAR}` placeholders (resolved via `.env` + `os.environ` in
  `load_config`, before YAML parsing). Quote placeholders in YAML (`"${VAR}"`) when the
  underlying value could look numeric (e.g. a Telegram `chat_id`), otherwise YAML will coerce
  the type and pydantic validation will fail.
- **`detection/`** — split into a backend (`YoloBackend`, talks to `ultralytics.YOLO`) and a
  filter (`PersonDetector`, keeps only `label == "person"` above a confidence threshold). The
  backend is a `Protocol` (`DetectionBackend`), so tests substitute a fake backend and never need
  `ultralytics`/`torch` installed. `ultralytics` is imported lazily inside
  `YoloBackend.__init__`, not at module load time — keep that pattern for any other heavy ML
  dependency you add.
- **`alerts/`** — each channel (`LoggingAlerter`, `TelegramAlerter`, `EmailAlerter`) implements
  the `Alerter` protocol (`send(event: DetectionEvent) -> None`) independently; `dispatcher.py`
  fans a `DetectionEvent` out to all configured alerters and enforces a per-`source_name`
  cooldown (`AlertDispatcher` takes an injectable `clock` for deterministic tests — see
  `tests/test_dispatcher.py`). A single alerter raising is caught and logged so it doesn't block
  the others.
- **`pipeline.py`** — the run loop: pulls frames, applies `frame_skip` (detect every Nth frame
  for performance), saves a snapshot via `SnapshotStore` only when a person is detected, then
  hands the event to the dispatcher. When a `PreviewWindow` is passed in, every frame (not just
  every Nth) is annotated with the most recent detections and shown via `cv2.imshow`.
- **`preview.py`** — optional live debug window (`--show` flag), draws bounding boxes with
  `cv2.rectangle`/`putText` and polls for `q`/Esc to let the user quit. Requires a real display
  (GTK/Cocoa/X11); this is why the project depends on plain `opencv-python` rather than
  `opencv-python-headless` — don't switch back without adding a display-optional code path first.
- **`factory.py`** — the only place that turns `AppConfig` into wired-up objects
  (`build_detector`, `build_alerters`, `build_pipeline`). Add new alert channels or detection
  backends here, not in `cli.py`.
- **`cli.py`** — thin argparse wrapper: load config, build pipeline, run, handle `KeyboardInterrupt`.

## Conventions

- New alert channels: add a class implementing `Alerter.send(event)` under `alerts/`, a matching
  config block in `config.py` (`enabled` flag + required fields validated via
  `@model_validator(mode="after")`), and wire it up in `factory.build_alerters`.
- Tests fake the narrow interface at each seam (`DetectionBackend`, `Alerter`, `clock: Callable`)
  rather than mocking library internals — follow that pattern for new components.
- `model_weights` (default `yolov8n.pt`) is downloaded by `ultralytics` on first run and is not
  committed to the repo (`*.pt` is gitignored), same for `snapshots/` and `.env`.
