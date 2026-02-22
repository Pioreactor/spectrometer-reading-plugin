# -*- coding: utf-8 -*-
from __future__ import annotations

from setuptools import find_packages
from setuptools import setup


setup(
    name="spectrometer-reading-plugin",
    version="0.4.0",
    license="MIT",
    description="Take spectrometer readings (between OD readings) from the Adafruit AS7341 attached to your Pioreactor",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author_email="info@pioreactor.com",
    author="Kelly Tran, Cameron Davidson-Pilon, Pioreactor",
    url="https://github.com/Pioreactor/spectrometer-reading-plugin",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={"pioreactor.plugins": "spectrometer_reading_plugin = spectrometer_reading_plugin"},
)
