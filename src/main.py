from sensor import SoilSensor
from sensor import Sensors
from config import Config
from lights import Lights
from machine import Pin
from google.auth import ServiceAccount
from google.sheet import Spreadsheet
from wifi import AccessPoint
from wifi import Connection
import gc
import time
import util
import sys
import uerrno


# the handle() method below takes temperature and humidity
# and writes them to a spreadsheet
#
# the following function, when added to the Google sheet (Tools > Script editor) allows the
# formula uploaded in the "now" variable (see "measure(self)") to calculate a local timestamp
# from the epoch value loaded in column A of the inserted row
#
# function TIMESTAMP_TO_DATE(value) {
#   return new Date(value * 1000);
# }
# see the sheets.py file to set the ValueInputOption to USER_INPUT to avoid now string value being prefixed with a '
class SensorHandler:

    # initializes a new handler
    def __init__(self, sheet):
        self.sheet = sheet

    # send data to the sheet
    def handle(self, data):
        now = "=TIMESTAMP_TO_DATE(INDIRECT(\"A\" & ROW()))"
        data.append(now)
        print('send the following to the sheet: %s' % data)
        self.sheet.append_values(data)


if __name__ == '__main__':
    # enable garbage collection
    gc.enable()
    print('garbage collection threshold: ' + str(gc.threshold()))

    # load configuration for a file
    config = Config('main.conf', 'key.json')

    # create an instance of ServiceAccount class
    # which then is going to be used to obtain an OAuth2 token
    # for writing data to a sheet
    sa = ServiceAccount()
    sa.email(config.get('google_service_account_email'))
    sa.scope('https://www.googleapis.com/auth/spreadsheets')
    sa.private_rsa_key(config.private_rsa_key())

    # create an instance of Spreadsheet which is used to write data to a sheet
    spreadsheet = Spreadsheet()
    spreadsheet.set_service_account(sa)
    spreadsheet.set_id(config.get('google_sheet_id'))
    spreadsheet.set_range('A:A')

    # create a handler which takes temperature and humidity and write them to a sheet
    sensor_handler = SensorHandler(spreadsheet)

    # initialize available sensors and add them to a controller
    sensor = Sensors(config.get('measurement_interval'),
                     sensor_handler)
    if config.get('adc_pin'):
        sensor.add(SoilSensor(config.get('dht22_pin')))
        print('registered a DHT22 sensor')

# todo - config mode? I would need a button or something.
    # first, check if the configuration mode is enabled
    # if so, set up an access point, and then start an HTTP server
    # the server provides a web form which updates the configuration of the device
    # the server runs on http://192.168.4.1:80
    # if config_mode_switch.value() == 1:
    #     from http.server import HttpServer
    #     from settings import ConnectionHandler
    #     print('enabled configuration mode')
    #
    #     access_point = AccessPoint(config.get('access_point_ssid'),
    #                                config.get('access_point_password'))
    #     access_point.start()
    #     lights.wifi_on()
    #     handler = ConnectionHandler(config, lights)
    #     HttpServer(access_point.ip(), 80, handler).start()
    #     lights.wifi_off()
    #     util.reboot()

# todo - do I want any lights? Either to show no internet connection or other states?
    # try to connect to Wi-Fi if the configuration mode is disabled
    wifi = Connection(config.get('ssid'), config.get('password'))
    wifi.connect()

    # finally, start the main loop
    # in the loop, the board is going to check temperature and humidity
    error = False
    while True:
        try:
            # reconnect if a error occurred or the connection is lost
            if error or not wifi.is_connected():
                wifi.reconnect()

            error = False
            # lights.error_off()
            sensor.check()
        except Exception as e:
            error = True
            # lights.error_on()
            print('achtung! something wrong happened! ...')
            sys.print_exception(e)
            if isinstance(e, OSError) and e.args[0] in uerrno.errorcode:
                print('error code: %s' % uerrno.errorcode[e.args[0]])
            if config.get('error_handling') == 'reboot':
                print('rebooting ...')
                util.reboot()
            elif config.get('error_handling') == 'stop':
                print('stop ...')
                raise
            else:
                print('continue ...')

            # a little delay
            time.sleep(10)
