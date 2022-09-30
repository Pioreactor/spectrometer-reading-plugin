# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name="spectrometer_reading_plugin",
    version="0.0.1",
    license="MIT",
    description="Take spectrometer readings (between OD readings) from the Adafruit AS7341 attached to your Pioreactor",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author_email="kelly@pioreactor.com",
    author="Kelly Tran",
    url="https://github.com/kellytr/pioreactor-relay-plugin",
    packages=find_packages(),
    include_package_data=True,
    install_requires=['adafruit_as7341']
    entry_points={
        "pioreactor.plugins": "pioreactor_relay_plugin = pioreactor_relay_plugin"
    },
)