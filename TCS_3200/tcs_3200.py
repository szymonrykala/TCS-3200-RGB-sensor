import RPi.GPIO as GPIO

from .components import BackLight, CalibrationConfig, Frequency, Photodiode
from .logger import LOGGER as logger


class TCS3200:
    def __init__(
        self,
        fscale0: int,
        fscale1: int,
        pdiode0: int,
        pdiode1: int,
        led: int,
        signal: int,
    ):
        self.cleanup()
        GPIO.setmode(GPIO.BCM)
        self.frequency = Frequency(signal_input=signal, out1=fscale0, out2=fscale1)

        self.diode = Photodiode(out1=pdiode0, out2=pdiode1)
        self.back_light = BackLight(led)
        self.calibration = CalibrationConfig()
        self.calibration.load_from_file()

        logger.info("Sensor setup finished")

    def __transpose_frequency(self, white_ref: int, freq_hz: float):
        x = (freq_hz * 255) / white_ref
        return int(x) if x <= 255 else 255

    def calibrate(self):
        logger.debug("Sensor calibration started")

        self.back_light.on()

        self.diode.red()
        red = self.frequency.measure()

        self.diode.green()
        green = self.frequency.measure()

        self.diode.blue()
        blue = self.frequency.measure()

        self.diode.no_filter()
        no_filter = self.frequency.measure()

        self.back_light.off()

        self.calibration.set(red, green, blue, no_filter)

        logger.info("Sensor calibration finished")
        self.calibration.save()

    def read(self):
        output = {}

        logger.info("Starting color measurments")
        self.back_light.on()

        self.diode.red()
        output.update(red=self.__transpose_frequency(self.calibration.data.red, self.frequency.measure()))
        logger.debug("red finished")

        self.diode.green()
        output.update(green=self.__transpose_frequency(self.calibration.data.green, self.frequency.measure()))
        logger.debug("green finished")

        self.diode.blue()
        output.update(blue=self.__transpose_frequency(self.calibration.data.blue, self.frequency.measure()))
        logger.debug("blue finished")

        self.diode.no_filter()
        output.update(no_filter=self.__transpose_frequency(self.calibration.data.no_filter, self.frequency.measure()))
        logger.debug("no_filter finished")

        logger.info(f"Measuring finished {output}")

        self.back_light.off()
        return output

    def cleanup(self):
        logger.info("cleaning up...")
        GPIO.cleanup()
