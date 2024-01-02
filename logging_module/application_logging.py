import logging.handlers
import os
import sys
import time
from logging import StreamHandler

import constants

LOG_HANDLERS = constants.LOG_HANDLERS
log_level = constants.LOG_LEVEL
log_file = os.path.join(constants.LOG_FILE_NAME + "_" + time.strftime("%Y%m%d") + '.log')

logger = logging.getLogger(constants.LOGGER_NAME)
logger.setLevel(log_level)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s  - %(filename)s - %(module)s: %(funcName)s: '
                              '%(lineno)d - %(message)s')

if 'console' in LOG_HANDLERS:
    # Adding the log Console handler to the logger
    console_handler = StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

if 'file' in LOG_HANDLERS:
    # Adding the log file handler to the logger
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
