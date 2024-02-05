import time
from abc import ABC
from dataclasses import dataclass
from os import path
from statistics import mean

import RPi.GPIO as GPIO

from .logger import LOGGER as logger


@dataclass
class CalibrationData:
    red: int = 10_500
    green: int = 10_500
    blue: int = 10_500
    no_filter: int = 10_500


class CalibrationConfig:
    __file_name: str = "tcs-3200-calibration"

    def __init__(self):
        self.data: CalibrationData = CalibrationData()

    def set(self, red: int, green: int, blue: int, no_filter: int):
        self.data = CalibrationData(red, green, blue, no_filter)

    def load_from_file(self):
        logger.info(f"Reading calibration data from file '{self.__file_name}'")
        if path.exists(self.__file_name):
            with open(self.__file_name, "r") as file:
                self.data = eval(file.read())
        else:
            logger.warning(f"Calibration data file '{self.__file_name}' is not exists")

    def save(self):
        with open(self.__file_name, "w+") as file:
            file.write(repr(self.data))

        logger.debug(f"Calibration data has been saved")


class PinPairSeter(ABC):
    def __init__(self, out1: int, out2: int):
        self.__p1 = out1
        self.__p2 = out2

        GPIO.setup(self.__p1, GPIO.OUT)
        GPIO.setup(self.__p2, GPIO.OUT)

    def _set_outputs(self, p1_state, p2_state):
        GPIO.output(self.__p1, p1_state)
        GPIO.output(self.__p2, p2_state)


class Photodiode(PinPairSeter):
    def red(self):
        logger.debug("setting up red photodiode")
        self._set_outputs(GPIO.LOW, GPIO.LOW)

    def green(self):
        logger.debug("setting up green photodiode")
        self._set_outputs(GPIO.HIGH, GPIO.HIGH)

    def blue(self):
        logger.debug("setting up blue photodiode")
        self._set_outputs(GPIO.LOW, GPIO.HIGH)

    def no_filter(self):
        logger.debug("setting up no filter mode")
        self._set_outputs(GPIO.HIGH, GPIO.LOW)


class BackLight:
    def __init__(self, pin: int):
        self.__pin = pin
        GPIO.setup(self.__pin, GPIO.OUT)

    def on(self):
        logger.debug("backlight LED on")
        GPIO.output(self.__pin, GPIO.HIGH)
        time.sleep(0.1)

    def off(self):
        logger.debug("backlight LED off")
        GPIO.output(self.__pin, GPIO.LOW)


class Frequency(PinPairSeter):
    def __init__(self, signal_input: int, out1: int, out2: int):
        super().__init__(out1, out2)
        self.__mean_count = 5
        self.__cycles_count = 100
        self.__signal = signal_input

        GPIO.setup(self.__signal, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def __get_frequency(self):
        now = time.time()

        for _ in range(self.__cycles_count):
            GPIO.wait_for_edge(self.__signal, GPIO.RISING)

        duration = time.time() - now
        return self.__cycles_count / duration

    def scale100(self):
        logger.info("setting measure readings scale to 100%")
        self._set_outputs(GPIO.HIGH, GPIO.HIGH)

    def scale20(self):
        logger.info("setting measure readings scale to 20%")
        self._set_outputs(GPIO.HIGH, GPIO.LOW)

    def scale2(self):
        logger.info("setting measure readings scale to 2%")
        self._set_outputs(GPIO.LOW, GPIO.HIGH)

    def set_mean_count(self, val: int):
        self.__mean_count = val

    def set_cycles_count(self, val: int):
        self.__cycles_count = val

    def measure(self):
        logger.debug(f"Measuring frequency {self.__mean_count} times started")
        mes = [self.__get_frequency() for _ in range(self.__mean_count)]
        logger.debug(f"Measuring frequency finished: {mes}")
        return mean(mes)
