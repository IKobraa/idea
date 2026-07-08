# idea — homesec

Person detection and alerting for a home security system. It watches a
video source (webcam, video file, or RTSP camera stream), detects people
with a YOLO model, saves a snapshot, and sends alerts (Telegram, email,
and/or local logging) with a per-source cooldown to avoid spam.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

cp config/config.example.yaml config/config.yaml
cp .env.example .env   # fill in Telegram/SMTP secrets if you enable those alerters

homesec --config config/config.yaml
```

## Development

```bash
pytest              # run the test suite
ruff check .         # lint
```
