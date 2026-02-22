# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

import pytest


def _write_test_configs(global_config_path: Path, local_config_path: Path) -> None:
    log_file_path = global_config_path.parent / "pioreactor.log"
    global_config_path.write_text(
        f"""
[cluster.topology]
leader_hostname=leader
leader_address=127.0.0.1

[mqtt]
broker_address=127.0.0.1

[logging]
log_file={log_file_path}
console_log_level=DEBUG

[od_reading.config]
samples_per_second=0.2

[spectrometer_reading.config]
enable_dodging_od=true
use_onboard_led=true
led_current_mA=5
turn_off_leds_during_reading=true
always_keep_led_on=false
""".strip()
        + "\n",
        encoding="utf-8",
    )
    local_config_path.write_text("[unit]\n", encoding="utf-8")


def _reset_plugin_import_cache() -> None:
    for module_name in list(sys.modules):
        if module_name == "spectrometer_reading_plugin" or module_name.startswith("spectrometer_reading_plugin."):
            sys.modules.pop(module_name, None)


@pytest.fixture()
def plugin_module(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    global_config_path = tmp_path / "config.ini"
    local_config_path = tmp_path / "unit_config.ini"
    _write_test_configs(global_config_path, local_config_path)

    monkeypatch.setenv("GLOBAL_CONFIG", str(global_config_path))
    monkeypatch.setenv("LOCAL_CONFIG", str(local_config_path))
    monkeypatch.setenv("TESTING", "1")
    _reset_plugin_import_cache()

    busio_mod = types.ModuleType("busio")
    busio_mod.I2C = object
    monkeypatch.setitem(sys.modules, "busio", busio_mod)

    board_mod = types.ModuleType("board")
    board_mod.I2C = object
    monkeypatch.setitem(sys.modules, "board", board_mod)

    vendor_mod = types.ModuleType("spectrometer_reading_plugin._vendor.adafruit_as7341")

    class _AS7341:
        def __init__(self, i2c) -> None:
            self.led_current: float = 0.0
            self.gain: int = 10
            self.atime: int = 100
            self.led: bool = False
            self._channels: list[int] = [0] * 8

        @property
        def all_channels(self) -> tuple[int, ...]:
            return tuple(self._channels)

    vendor_mod.AS7341 = _AS7341
    monkeypatch.setitem(sys.modules, "spectrometer_reading_plugin._vendor.adafruit_as7341", vendor_mod)

    config_module = importlib.import_module("pioreactor.config")
    for cache_name in ("get_config", "get_leader_hostname", "_get_leader_address", "_get_mqtt_address"):
        cached = getattr(config_module, cache_name, None)
        if cached is not None and hasattr(cached, "cache_clear"):
            cached.cache_clear()

    mqtt_to_db_streaming = importlib.import_module("pioreactor.background_jobs.leader.mqtt_to_db_streaming")

    class _TopicToParserToTable:
        def __init__(self, *args, **kwargs) -> None:
            if args:
                self.topic, self.parser, self.table = args
            else:
                self.topic = kwargs["topic"]
                self.parser = kwargs["parser"]
                self.table = kwargs["table"]

    monkeypatch.setattr(mqtt_to_db_streaming, "TopicToParserToTable", _TopicToParserToTable)
    monkeypatch.setattr(mqtt_to_db_streaming, "register_source_to_sink", lambda items: items)

    return importlib.import_module("spectrometer_reading_plugin")
