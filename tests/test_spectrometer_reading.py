# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any


def _build_job(plugin_module: Any):
    job = plugin_module.SpectrometerReading.__new__(plugin_module.SpectrometerReading)

    class _Logger:
        def __init__(self) -> None:
            self.errors: list[str] = []

        def error(self, message: str) -> None:
            self.errors.append(message)

    job.logger = _Logger()
    job.state = job.READY
    job.currently_dodging_od = False
    job.job_name = "spectrometer_reading"
    job.continuous_sampling_timer = None
    return job


def test_initialize_continuous_operation_uses_od_sample_rate(plugin_module, monkeypatch) -> None:
    module = plugin_module
    created: dict[str, Any] = {}

    class FakeTimer:
        def __init__(self, interval: float, function: Any, **kwargs: Any) -> None:
            created["interval"] = interval
            created["function"] = function
            created["kwargs"] = kwargs
            self.cancel_called = False

        def start(self):
            created["started"] = True
            return self

        def cancel(self) -> None:
            self.cancel_called = True

    monkeypatch.setattr(module, "RepeatedTimer", FakeTimer)

    module.config.set("od_reading.config", "samples_per_second", "2.0")
    job = _build_job(module)

    call_count = {"count": 0}

    def _record_once() -> None:
        call_count["count"] += 1

    job._record_once = _record_once
    job.initialize_continuous_operation()

    assert created["interval"] == 0.5
    assert created["kwargs"]["run_immediately"] is True
    assert created["started"] is True

    created["function"]()
    assert call_count["count"] == 1


def test_initialize_continuous_operation_rejects_non_positive_rate(plugin_module, monkeypatch) -> None:
    module = plugin_module

    class FakeTimer:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise AssertionError("timer should not be created for invalid sample rate")

    monkeypatch.setattr(module, "RepeatedTimer", FakeTimer)

    module.config.set("od_reading.config", "samples_per_second", "0.0")
    job = _build_job(module)
    cleaned = {"called": False}

    def _clean_up() -> None:
        cleaned["called"] = True

    job.clean_up = _clean_up
    job.initialize_continuous_operation()

    assert cleaned["called"] is True
    assert any("samples_per_second" in message for message in job.logger.errors)


def test_record_continuously_skips_while_dodging(plugin_module) -> None:
    module = plugin_module
    job = _build_job(module)
    job.currently_dodging_od = True

    call_count = {"count": 0}
    job._record_once = lambda: call_count.__setitem__("count", call_count["count"] + 1)

    job._record_continuously()

    assert call_count["count"] == 0


def test_initialize_dodging_operation_cancels_continuous_timer(plugin_module) -> None:
    module = plugin_module
    job = _build_job(module)

    class _Timer:
        def __init__(self) -> None:
            self.cancelled = False

        def cancel(self) -> None:
            self.cancelled = True

    timer = _Timer()
    job.continuous_sampling_timer = timer

    job.initialize_dodging_operation()

    assert timer.cancelled is True


def test_on_disconnected_calls_super_and_cleans_local_resources(plugin_module, monkeypatch) -> None:
    module = plugin_module
    job = _build_job(module)

    class _Timer:
        def __init__(self) -> None:
            self.cancelled = False

        def cancel(self) -> None:
            self.cancelled = True

    super_called = {"called": False}

    def _base_on_disconnected(self) -> None:
        super_called["called"] = True

    monkeypatch.setattr(module.BackgroundJobWithDodgingContrib, "on_disconnected", _base_on_disconnected)

    led = {"off": False}
    timer = _Timer()

    job.continuous_sampling_timer = timer
    job.turn_off_led = lambda: led.__setitem__("off", True)

    job.on_disconnected()

    assert super_called["called"] is True
    assert timer.cancelled is True
    assert led["off"] is True
