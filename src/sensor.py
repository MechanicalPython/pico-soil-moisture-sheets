from machine import Pin
import time
import machine
import util


# this class is a controller that coordinates measurements from multiple sensors
# in a specified interval, it checks a number of sensors and sends the measurements to a handler
class Sensors:

    # initializes an instance of Weather with the following parameters
    # - an interval which specifies the schedule for measurements
    # - a handler for handling measurements from sensors
    def __init__(self, interval, handler):
        self.last_measurement = None
        self.interval = util.string_to_millis(interval)
        self.handler = handler
        self.sensors = []

    # add a sensor
    def add(self, sensor):
        self.sensors.append(sensor)

    # checks if it's time to measure
    def check(self):
        current_time = time.ticks_ms()
        deadline = time.ticks_add(self.last_measurement, self.interval)
        if self.last_measurement is None or time.ticks_diff(deadline, current_time) <= 0:
            self.measure()
            self.last_measurement = current_time

    # measure everything and send the measurements to the handler
    def measure(self):
        data = []
        for sensor in self.sensors:
            measurement = sensor.measure()
            data = data + measurement

        if self.handler is not None:
            self.handler.handle(data)


# The class to measure soil moisture
class SoilSensor:
    def __init__(self, vcc_pin=22, adc_pin=26, water_thresh=30):
        machine.Pin(vcc_pin, Pin.OUT).on()  # Turn moisture sensor power on.
        self.adc_pin = machine.Pin(adc_pin)  # Pin 31/GPIO 26/ADC 0.
        self.sensor = machine.ADC(self.adc_pin)
        self.pump = Pin(18, Pin.OUT)  # Relay GPIO pin is pin 18.
        self.max = 54000  # 0% wet.
        self.min = 21000  # 100% wet
        self.water_thresh = water_thresh

    def get_moisture(self, number_of_readings):
        # New capacitive sensor can be constantly powered so no need to turn the sensor on and off.
        total = 0
        for x in range(0, number_of_readings):
            total += self.sensor.read_u16()
        value = total / number_of_readings
        return value

    def convert_raw_to_perc(self, raw):
        """
        Returns % wet. Max = 100% wet, min = 0% wet.
        Can (in theory) be +- 0 to 100%
        :param raw:
        :return:
        """
        # wet = 21600, dry = 59000
        percentage = (raw - self.min) / (self.max - self.min)  # Gives it as if 100% is dry.
        invert = ((percentage - 1) * -1) * 100  # to make 100% = wet.
        return round(invert, 2)

    def pump_water(self, seconds):
        self.pump.on()
        time.sleep(seconds)
        self.pump.off()

    def main(self):
        moisture = self.get_moisture(1000)
        moisture = self.convert_raw_to_perc(moisture)
        if moisture < self.water_thresh:  # High moisture level to keep the plant watered. This value may need to be altered.
            self.pump_water(4)
        return moisture
