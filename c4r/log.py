import logging
import logging.handlers


class Logger(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.config_logging_to_console()

    def get_log(self):
        return self.logger

    def config_logging_to_console(self):
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(console)


    def config_logging_to_file(self, log_file_path):
        log_file = logging.handlers.RotatingFileHandler(log_file_path, maxBytes=1024 * 1024, backupCount=10)
        log_file.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
        self.logger.addHandler(log_file)
