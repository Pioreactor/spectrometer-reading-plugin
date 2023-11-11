# -*- coding: utf-8 -*-
from __future__ import annotations

from setuptools import find_packages
from setuptools import setup


setup(
    name="spectrometer-reading-plugin",
    version="0.2.6",
    license="MIT",
    description="Take spectrometer readings (between OD readings) from the Adafruit AS7341 attached to your Pioreactor",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author_email="cam@pioreactor.com",
    author="Kelly Tran, Pioreactor",
    url="https://github.com/Pioreactor/spectrometer-reading-plugin",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["adafruit-circuitpython-as7341"],
    entry_points={"pioreactor.plugins": "spectrometer_reading_plugin = spectrometer_reading_plugin"},
)
