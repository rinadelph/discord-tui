#!/usr/bin/env python3
"""Quick test of the Discordo app."""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from discordo.internal.config import Config
from discordo.cmd.application import run_app

if __name__ == "__main__":
    # Load config
    config_path = Path.home() / ".config/discordo/config.toml"
    
    if not config_path.exists():
        print(f"Creating config at {config_path}")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        from pathlib import Path as P
        default_config = P(__file__).parent / "config.toml"
        if default_config.exists():
            import shutil
            shutil.copy(default_config, config_path)
    
    cfg = Config.load(str(config_path))
    run_app(cfg)
