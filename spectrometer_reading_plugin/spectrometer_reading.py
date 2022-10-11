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
        "band_415": {"datatype": "int", "unit": "AU", "settable": False},
        "band_445": {"datatype": "int", "unit": "AU", "settable": False},
        "band_480": {"datatype": "int", "unit": "AU", "settable": False},
        "band_515": {"datatype": "int", "unit": "AU", "settable": False},
        "band_555": {"datatype": "int", "unit": "AU", "settable": False},
        "band_590": {"datatype": "int", "unit": "AU", "settable": False},
        "band_630": {"datatype": "int", "unit": "AU", "settable": False},
        "band_680": {"datatype": "int", "unit": "AU", "settable": False},
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

    def record_band_415(self):
        self.band_415 = self.normalize(self.sensor.channel_415nm)

    def record_band_445(self):
        self.band_445 = self.normalize(self.sensor.channel_445nm)

    def record_band_480(self):
        self.band_480 = self.normalize(self.sensor.channel_480nm)

    def record_band_515(self):
        self.band_515 = self.normalize(self.sensor.channel_515nm)

    def record_band_555(self):
        self.band_555 = self.normalize(self.sensor.channel_555nm)

    def record_band_590(self):
        self.band_590 = self.normalize(self.sensor.channel_590nm)

    def record_band_630(self):
        self.band_630 = self.normalize(self.sensor.channel_630nm)

    def record_band_680(self):
        self.band_680 = self.normalize(self.sensor.channel_680nm)

    def record_all_bands(self):
        self.record_band_415()
        self.record_band_445()
        self.record_band_480()
        self.record_band_515()
        self.record_band_555()
        self.record_band_590()
        self.record_band_630()
        self.record_band_680()

    def normalize(self, band_recording: int):
        return band_recording

    def action_to_do_before_od_reading(self):
        pass

    def turn_on_led(self):
        self.sensor.led = True

    def turn_off_led(self):
        self.sensor.led = False

    def action_to_do_after_od_reading(self):
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
