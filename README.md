# Automatic plant irrigation based on Pi Pico and MicroPython


Here is a list of main features:

*  Measuring soil moisture levels with a [Capacitive moisture sensor](https://thepihut.com/products/capacitive-soil-moisture-sensor)
*  Sending data to a Google sheet
*  Supporting Google OAuth 2.0 service to get access to the sheet
*  Reporting network connection status, errors and moisture levels with [LEDs](https://thepihut.com/products/adafruit-neopixel-ring-12-x-5050-rgbw-leds-w-integrated-drivers)
*  Configuring the device via web browser

The sheet doesn't need to be publicly available on the Internet. The device doesn't require any middleman such as PushingBox or IFTTT.

This README contains a brief description how the project can be built. 

## How to make an irrigation system

The project uses [Micropython for Pico W, version rp2-pico-w-20221220-unstable-v1.19.1-782-g699477d12.uf2](https://micropython.org/download/rp2-pico-w/).
The project uses the following tools:

*  `Pycharm Community edition with the Micropython plugin` for uploading files to the Pico, however [Thonny](https://thonny.org) also works.
*  `openssl` and `rsa` package for reading cryptographic keys

### Preparing a service account in Google IAM

To access a Google sheet, the project needs a service account:

*  [Follow the instructions](https://developers.google.com/identity/protocols/OAuth2ServiceAccount) and create a service account
*  Create a key
*  Download a JSON file with the key

The key is encoded in PKCS1 format. Unfortunately, the project doesn't support PKCS1 yet. You need to convert the key to the format which the project understands:

```
$ cd scripts
$ sh extract_key.sh ../google_key.json ../key.json
```

You'll need `key.json` and an email for the service account.

### Creating a Google sheet

Create a Google sheet and extract its ID from the URL

```
https://docs.google.com/spreadsheets/d/<ID_is_here>/edit#gid=0
```

Share the sheet with your service account. The sheet doesn't need to be publicly accessible from the Internet.

### Preparing a configuration file

`main.conf` contains a configuration for the device. Provide the following parameters:

*  `ssid` and `password` are credentials for your Wi-Fi
*  `access_point_ssid` and `access_point_password` are credentials for a Wi-Fi access point
    that is started by the device in the configuration mode.
*  `google_service_account_email` is an email for the Google's service account
*  `google_sheet_id` is the Google's sheet ID
*  `measurement_interval` is a mesurement interval in `Xh Ym Zs` format, for example, `1h 2m 3s`
*  `co2_threshold` is a threshold for CO2 level. If the current CO2 level is higher than the threshold,
    the yellow LED turns on.
*   Pins on the ESP32 board that are connected to the sensors, switch and LEDs.

### Uploading MicroPython

The following scripts may be used to upload MicroPython to ESP32:

```
$ sh scripts/erase.sh
$ sh scripts/flash.sh
$ sh scripts/verify.sh
```

### Uploading code and configs

You can run `sh scripts/upload.sh` to upload the code, the configuration file and the key.
Before running the script, set the followin environment variables:

```
$ export SSID=ssid-for-your-wifi
$ export WIFI_PASSWORD=password-for-your-wifi
$ export ACCESS_POINT_SSID=esp32-weather-google-sheets
$ export ACCESS_POINT_PASSWORD=password-for-the-access-point
$ export GOOGLE_SERVICE_ACCOUNT_EMAIL=your-google-service-account-email
$ export GOOGLE_SHEET_ID=your-google-sheet-id
$ sh scripts/upload.sh
```

Then, you can connect to the board with `sh scripts/minicon.sh` command to check if everything works fine.

### Configuration mode

The switch turns on the configuration mode. In this mode the device starts up a Wi-Fi access point, and runs an HTTP server on http://192.168.4.1.
The server provides a web form for updating the configuration of the device.

## Acknowledgement
Forked from https://github.com/artem-smotrakov/esp32-weather-google-sheets.

## Further enhancements

Here is a list of possbile enhancements:

1.  Support [BMP280](https://www.bosch-sensortec.com/bst/products/all_products/bmp280) barometric pressure sensor
1.  Support [DS18B20](https://datasheets.maximintegrated.com/en/ds/DS18B20.pdf) temperature sensor
1.  Support PKCS1
