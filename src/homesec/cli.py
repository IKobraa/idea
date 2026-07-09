"""Command-line entry point: ``homesec --config config/config.yaml``."""

from __future__ import annotations

import argparse
import logging
from collections.abc import Sequence

from homesec.config import load_config
from homesec.factory import build_pipeline


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Home security person detection")
    parser.add_argument(
        "--config",
        default="config/config.yaml",
        help="Path to a YAML config file (see config/config.example.yaml)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Open a live preview window with detection boxes drawn (local display required)",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=args.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    config = load_config(args.config)
    pipeline = build_pipeline(config, show_preview=args.show)
    try:
        pipeline.run()
    except KeyboardInterrupt:
        logging.getLogger("homesec.cli").info("Stopped by user")


if __name__ == "__main__":
    main()
