import logging
import logging.config
import logging.handlers
from logging import StreamHandler, Formatter
from logging.handlers import RotatingFileHandler

logger = None


def create_logger():
    global logger  # pylint: disable=W0603
    logger = logging.getLogger(__name__)

    logger.setLevel(logging.INFO)
    set_logging_to_console()


def get_logger():
    ensure_logger()
    return logger


def ensure_logger():
    if logger is None:
        create_logger()


def set_logger_level(level):
    ensure_logger()
    logger.setLevel(level)


def set_logging_to_console():
    ensure_logger()
    console = StreamHandler()
    console.setFormatter(Formatter('%(message)s'))
    logger.addHandler(console)


def set_logging_to_file(log_file_path):
    ensure_logger()

    file = RotatingFileHandler(log_file_path, maxBytes=1024 * 1024, backupCount=10)
    file.setFormatter(Formatter('%(asctime)s: %(message)s'))
    logger.addHandler(file)
