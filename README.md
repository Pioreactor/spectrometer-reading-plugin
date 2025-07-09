## Spectrometer reading plugin

Records spectrometer readings from the Adafruit AS7341 spectrometer sensor attached to your Pioreactor.

Available wavelengths:

- ![#7600ed](https://placehold.co/15/7600ed/FFF?text=\n) `415nm`
- ![#0028ff](https://placehold.co/15/0028ff/FFF?text=\n) `445nm`
- ![#00d5ff](https://placehold.co/15/00d5ff/FFF?text=\n) `480nm`
- ![#1fff00](https://placehold.co/15/1fff00/FFF?text=\n) `515nm`
- ![#b3ff00](https://placehold.co/15/b3ff00/FFF?text=\n) `555nm`
- ![#ffdf00](https://placehold.co/15/ffdf00/FFF?text=\n) `590nm`
- ![#ff4f00](https://placehold.co/15/ff4f00/FFF?text=\n) `630nm`
- ![#ff0000](https://placehold.co/15/ff0000/FFF?text=\n) `680nm`


This plugin also installs a SQL table, `as7341_spectrum_readings`, that will store the readings.


### Charts

After installation, you can add specific bands as charts. Add `spec_415=1`, or whatever band(s) you want, to the `[ui.overview.charts]` section, ex:

![ui of configuration](https://user-images.githubusercontent.com/884032/282266761-c1f962f7-2ddf-45e3-9bf6-ad78b4c6b75a.png)




### Hardware installation

See [notes here](https://github.com/Pioreactor/spectrometer-reading-plugin/wiki#installation).

### How it works

1. In between optical density recordings, the white-light LED on the AS7341 board turns on, and all other LEDs from the Pioreactor's LED channels turn off.
2. The light is reflected back towards the board, with some wavelengths being absorbed by the culture.
3. All sensors for each wavelength are recorded to MQTT and the SQLite3 database (see below)
4. The onboard LED is turned off.

Each wavelength is sent to MQTT under the topics:

```
pioreactor/<unit>/<experiment>/spectrometer_reading/band_<xxx>
```

And it is also placed in the SQL table `as7341_spectrum_readings`.


#### Using a different LED

You can provide a 5mm LED instead of using the onboard one. We suggest using the following config to accomplish this:

```
led_current_mA=0
turn_off_leds_during_reading=0
```

### Hardware requirements

 - Requires the [Adafruit board AS7341](https://www.adafruit.com/product/4698) and a StemmaQT 4pin cable.
