# -*- coding: utf-8 -*-
from __future__ import annotations

import adafruit_as7341
import board
import click
from pioreactor.background_jobs.base import BackgroundJobWithDodging
from pioreactor.background_jobs.leader.mqtt_to_db_streaming import produce_metadata
from pioreactor.background_jobs.leader.mqtt_to_db_streaming import register_source_to_sink
from pioreactor.background_jobs.leader.mqtt_to_db_streaming import TopicToParserToTable
from pioreactor.config import config
from pioreactor.exc import HardwareNotFoundError
from pioreactor.utils.timing import current_utc_timestamp
from pioreactor.whoami import get_latest_experiment_name
from pioreactor.whoami import get_unit_name


def parser(topic, payload) -> dict:
    metadata = produce_metadata(topic)

    return {
        "experiment": metadata.experiment,
        "pioreactor_unit": metadata.pioreactor_unit,
        "timestamp": current_utc_timestamp(),
        "reading": float(payload),
        "band": int(metadata.rest_of_topic[-1].removeprefix("band_")),
    }


register_source_to_sink(
    TopicToParserToTable(
        [
            "pioreactor/+/+/spectrometer_reading/band_415",
            "pioreactor/+/+/spectrometer_reading/band_445",
            "pioreactor/+/+/spectrometer_reading/band_480",
            "pioreactor/+/+/spectrometer_reading/band_515",
            "pioreactor/+/+/spectrometer_reading/band_555",
            "pioreactor/+/+/spectrometer_reading/band_590",
            "pioreactor/+/+/spectrometer_reading/band_630",
            "pioreactor/+/+/spectrometer_reading/band_680",
        ],
        parser,
        "as7341_spectrum_readings",
    )
)


class SpectrometerReading(BackgroundJobWithDodging):

    job_name = "spectrometer_reading"

    published_settings = {
        "band_415": {"datatype": "float", "unit": "AU", "settable": False},
        "band_445": {"datatype": "float", "unit": "AU", "settable": False},
        "band_480": {"datatype": "float", "unit": "AU", "settable": False},
        "band_515": {"datatype": "float", "unit": "AU", "settable": False},
        "band_555": {"datatype": "float", "unit": "AU", "settable": False},
        "band_590": {"datatype": "float", "unit": "AU", "settable": False},
        "band_630": {"datatype": "float", "unit": "AU", "settable": False},
        "band_680": {"datatype": "float", "unit": "AU", "settable": False},
    }

    def __init__(self, unit, experiment):
        super().__init__(unit=unit, experiment=experiment)

        try:
            i2c = board.I2C()
            self.sensor = adafruit_as7341.AS7341(i2c)
        except Exception:
            self.logger.error("Is the AS7341 board attached to the Pioreactor HAT?")
            raise HardwareNotFoundError("Is the AS7341 board attached to the Pioreactor HAT?")

        self.sensor.led_current = config.getfloat("spectrometer_reading", "led_current_mA")
        self.sensor.gain = 10  # use max gain - vary the LED current to avoid saturation
        self.is_setup = False
        self._background_noise = (0.0,) * 8

    def record_all_bands(self):
        raw_channels = list(self.sensor.all_channels)
        normalized_channels = self.normalize_by_gain_time(raw_channels)

        self.band_415 = self.normalize_by_offset(normalized_channels, 0)
        self.band_445 = self.normalize_by_offset(normalized_channels, 1)
        self.band_480 = self.normalize_by_offset(normalized_channels, 2)
        self.band_515 = self.normalize_by_offset(normalized_channels, 3)
        self.band_555 = self.normalize_by_offset(normalized_channels, 4)
        self.band_590 = self.normalize_by_offset(normalized_channels, 5)
        self.band_630 = self.normalize_by_offset(normalized_channels, 6)
        self.band_680 = self.normalize_by_offset(normalized_channels, 7)

        if max(raw_channels) == 2**16 - 1:
            # gain is too high
            self.logger.warning("A color sensor is saturated - reduce the value of [led_current_mA]")

        return normalized_channels

    def normalize_by_offset(self, band_recordings: list[float], index) -> float:
        return band_recordings[index] - self._background_noise[index]

    def normalize_by_gain_time(self, band_recordings: list[int]) -> list[float]:
        # we normalize by the gain and integration time
        # https://ams.com/documents/20143/36005/AS7341_AN000633_1-00.pdf/fc552673-9800-8d60-372d-fc67cf075740
        # section 2.1
        return [x / 2 ** (self.sensor.gain - 1) / self.sensor.atime for x in band_recordings]

    def action_to_do_before_od_reading(self):
        pass

    def on_disconnected(self):
        self.turn_off_led()

    def turn_on_led(self):
        self.sensor.led = True

    def turn_off_led(self):
        self.sensor.led = False

    def record_background_noise(self):
        self.turn_off_led()
        # initially we record all sensors with LED off, to account for dark current, ambient light, etc.
        self._background_noise = self.normalize_by_gain_time(list(self.sensor.all_channels))

        self.logger.debug(f"Setup done, {self._background_noise=}")

    def action_to_do_after_od_reading(self):
        if self.is_setup is False:
            self.record_background_noise()
            self.is_setup = True
        else:
            self.turn_on_led()
            self.record_all_bands()
            self.turn_off_led()


@click.command(name="spectrometer_reading")
def click_spectrometer_reading():
    """
    Start spectrometer reading from the AS7341 sensor.
    """
    job = SpectrometerReading(
        unit=get_unit_name(),
        experiment=get_latest_experiment_name(),
    )
    job.block_until_disconnected()
