"""Command-line interface for Discordo."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

import keyring

from discordo.internal.config import Config
from discordo.internal.consts import DISCORDO_NAME
from discordo.internal.logger import setup_logger
from discordo.cmd.application import Application

logger = logging.getLogger(__name__)

# Global state
discord_state = None
app: Optional[Application] = None


def run() -> None:
    """Run the Discordo application."""
    parser = argparse.ArgumentParser(
        prog='discord',
        description='Discord TUI client for terminal'
    )
    parser.add_argument(
        '--token',
        default='',
        help='authentication token'
    )
    parser.add_argument(
        '--config-path',
        default=str(Config.default_path()),
        help='path of the configuration file'
    )
    parser.add_argument(
        '--log-path',
        default=str(Path.home() / '.cache' / 'discordo' / 'discordo.log'),
        help='path of the log file'
    )
    parser.add_argument(
        '--log-level',
        default='info',
        choices=['debug', 'info', 'warn', 'error'],
        help='log level'
    )
    
    args = parser.parse_args()
    
    # Convert log level string to logging level
    log_level_map = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARNING,
        'error': logging.ERROR,
    }
    log_level = log_level_map.get(args.log_level, logging.INFO)
    
    # Setup logger
    try:
        setup_logger(args.log_path, log_level)
    except Exception as err:
        print(f"failed to load logger: {err}", file=sys.stderr)
        sys.exit(1)
    
    # Load configuration
    try:
        cfg = Config.load(args.config_path)
    except Exception as err:
        logger.error(f"failed to load config: {err}")
        sys.exit(1)
    
    # Get token from flag or keyring
    token = args.token
    if not token:
        try:
            token = keyring.get_password(DISCORDO_NAME, 'token')
            if not token:
                logger.error("no token provided via --token flag or keyring")
                sys.exit(1)
        except Exception as err:
            logger.info(f"failed to retrieve token from keyring: {err}")
            sys.exit(1)
    
    # Create and run application
    global app
    app = Application(cfg)
    
    try:
        app.run(token)
    except Exception as err:
        logger.error(f"application error: {err}", exc_info=err)
        sys.exit(1)
