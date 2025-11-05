#!/usr/bin/env python3
"""Discordo - Discord TUI client for terminal."""

import logging
import sys

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point for the application."""
    try:
        from discordo.cmd.cmd import run
        run()
    except Exception as err:
        logger.error("failed to run command", exc_info=err)
        sys.exit(1)


if __name__ == '__main__':
    main()
