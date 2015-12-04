import logging, logging.handlers
from logging import StreamHandler, Formatter
from logging.handlers import RotatingFileHandler

logger = None

def get_logger():
    global logger
    if logger is None:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        config_logging_to_console(logger)

    return logger


def config_logging_to_console(logger):
    console = StreamHandler()
    console.setFormatter(Formatter('%(message)s'))
    logger.addHandler(console)


def config_logging_to_file(logger, log_file_path):
    log_file = RotatingFileHandler(log_file_path, maxBytes=1024 * 1024, backupCount=10)
    log_file.setFormatter(Formatter('%(asctime)s: %(message)s'))
    logger.addHandler(log_file)
