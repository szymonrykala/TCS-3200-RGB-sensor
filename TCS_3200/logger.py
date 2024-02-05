import os
import sys
from logging import DEBUG, INFO, Formatter, StreamHandler, getLogger

LOGGER_NAME = "TCS3200"


def setupLogger():
    logger = getLogger(LOGGER_NAME)
    debug_mode = os.environ.get("DEBUG_MODE", "false")

    if debug_mode.lower() == "true":
        logger.setLevel(DEBUG)
    else:
        logger.setLevel(INFO)

    log_stream = StreamHandler(sys.stdout)
    formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    logger.handlers.clear()
    log_stream.setFormatter(formatter)
    logger.addHandler(log_stream)

    logger.debug("logger setup finished")

    return logger


LOGGER = setupLogger()
