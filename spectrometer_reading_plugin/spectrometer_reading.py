# -*- coding: utf-8 -*-
from __future__ import annotations

import adafruit_as7341
import board
import click
from pioreactor.background_jobs.base import BackgroundJobWithDodging
from pioreactor.whoami import get_latest_experiment_name
from pioreactor.whoami import get_unit_name

class SpectrometerReading(BackgroundJobWithDodging):

    job_name='spectrometer_reading'
    
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

    def __init__(  # config stuff, settable in activities
        self,
        unit,
        experiment
    ):
        super().__init__(unit=unit, experiment=experiment)

        i2c = board.I2C()
        self.sensor = adafruit_as7341.AS7341(i2c)
        
        self.sensor.led_current = 5

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
    
    def normalize(self, band_recording):
        return band_recording / self.sensor.channel_clear
    
    def action_to_do_before_od_reading(self):
        pass
    
    def action_to_do_after_od_reading(self):
        self.sensor.led = True
        self.record_all_bands()
        self.sensor.led = False
        
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


if __name__ == "__main__":
    click_spectrometer_reading()
