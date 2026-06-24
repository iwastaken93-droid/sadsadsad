"""Tests for configuration management."""
import os
import tempfile
from pathlib import Path

from roastme.config import RoastConfig


def test_default_config():
    cfg = RoastConfig()
    assert cfg.api_base == "https://api.openai.com/v1"
    assert cfg.model == "gpt-4o"
    assert cfg.roast_level == "savage"
    assert cfg.persona == "disappointed_mentor"


def test_config_save_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override config dir
        import roastme.config
        original_dir = roastme.config.CONFIG_DIR
        original_file = roastme.config.CONFIG_FILE
        roastme.config.CONFIG_DIR = Path(tmpdir)
        roastme.config.CONFIG_FILE = Path(tmpdir) / "config.env"

        cfg = RoastConfig()
        cfg.api_key = "test-key"
        cfg.model = "gpt-3.5-turbo"
        cfg.save()

        # Load it back
        cfg2 = RoastConfig.load()
        assert cfg2.api_key == "test-key"
        assert cfg2.model == "gpt-3.5-turbo"

        # Restore
        roastme.config.CONFIG_DIR = original_dir
        roastme.config.CONFIG_FILE = original_file
