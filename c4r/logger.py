import os
import logging, logging.handlers
from logging import StreamHandler, Formatter
from logging.handlers import RotatingFileHandler
from config import LOG_FILE_NAME

logger = None

def get_logger():
    global logger # pylint: disable=W0603
    if logger is None:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        config_logging_to_console(logger)

        config_logging_to_file(logger,  os.path.join('./', LOG_FILE_NAME))

    return logger


def config_logging_to_console(log):
    console = StreamHandler()
    console.setFormatter(Formatter('%(message)s'))
    log.addHandler(console)


def config_logging_to_file(log, log_file_path):
    log_file = RotatingFileHandler(log_file_path, maxBytes=1024 * 1024, backupCount=10)
    log_file.setFormatter(Formatter('%(asctime)s: %(message)s'))
    log.addHandler(log_file)
