"""
Tests for configuration loader.
"""

import os
import pytest
import tempfile
import yaml
from src.config_loader import Config, str_to_bool


class TestStrToBool:
    """Tests for string to boolean conversion."""

    def test_true_values(self):
        """Test values that should convert to True."""
        for value in ["true", "True", "TRUE", "1", "yes", "Yes", "on", "On"]:
            assert str_to_bool(value) is True

    def test_false_values(self):
        """Test values that should convert to False."""
        for value in ["false", "False", "FALSE", "0", "no", "No", "off", "Off"]:
            assert str_to_bool(value) is False


class TestConfig:
    """Tests for Config class."""

    def test_config_defaults(self):
        """Test configuration with defaults."""
        config = Config()
        assert config.get("nonexistent", default="default") == "default"

    def test_config_from_yaml(self, tmp_path):
        """Test loading configuration from YAML."""
        config_file = tmp_path / "config.yaml"
        config_data = {
            "default_ticker": "AAPL",
            "years_of_history": 10,
            "cache_enabled": False,
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = Config(str(config_file))
        assert config.get("default_ticker") == "AAPL"
        assert config.get("years_of_history") == 10
        assert config.get("cache_enabled") is False

    def test_config_env_override(self, tmp_path, monkeypatch):
        """Test environment variable override."""
        # Set environment variable
        monkeypatch.setenv("TEST_VALUE", "from_env")

        config = Config()
        assert config.get("test_value", default="default", env_var="TEST_VALUE") == "from_env"

    def test_config_type_conversion(self, monkeypatch):
        """Test automatic type conversion."""
        monkeypatch.setenv("INT_VALUE", "42")
        monkeypatch.setenv("FLOAT_VALUE", "3.14")
        monkeypatch.setenv("BOOL_VALUE", "true")

        config = Config()
        assert config.get("int_value", default=0, env_var="INT_VALUE") == 42
        assert config.get("float_value", default=0.0, env_var="FLOAT_VALUE") == 3.14
        assert config.get("bool_value", default=False, env_var="BOOL_VALUE") is True
