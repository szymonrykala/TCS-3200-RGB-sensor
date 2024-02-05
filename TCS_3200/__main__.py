#!/usr/bin/python3

import RPi.GPIO as GPIO
from logger import LOGGER
from tcs_3200 import TCS3200

# output frequency scaling
S0 = 17
S1 = 27

# photodiode select
S2 = 23
S3 = 24

LED_POWER = 22
SIGNAL = 25

if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)

    rgb = TCS3200(fscale0=S0, fscale1=S1, pdiode0=S2, pdiode1=S3, led=LED_POWER, signal=SIGNAL)
    rgb.frequency.scale20()
    rgb.frequency.set_mean_count(3)
    rgb.frequency.set_cycles_count(30)
    try:
        value = rgb.read()
        LOGGER.info(value)
    except KeyboardInterrupt:
        LOGGER.info("shutting down...")
    finally:
        rgb.cleanup()
