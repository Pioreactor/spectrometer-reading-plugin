# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name="spectrometer_reading_plugin",
    version="0.0.1",
    license="MIT",
    description="Take spectrometer readings (between OD readings) from the Adafruit AS7341 attached to your Pioreactor",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author_email="cam@pioreactor.com",
    author="Kelly Tran, Cam Davidson-Pilon",
    url="https://github.com/Pioreactor/spectrometer-reading-plugin",
    packages=find_packages(),
    install_requires=['adafruit-circuitpython-as7341'],
    entry_points={
        "pioreactor.plugins": "spectrometer_reading_plugin = spectrometer_reading_plugin"
    },
)