import logging
import configparser
from time import strftime


class Logger:

    def __init__(self, logger_name=None, log_type=None, file_name=None, level=logging.DEBUG, formatter=None):

        self.logger_name = logger_name
        self.log_type = log_type
        self.file_name = file_name
        self.level = level
        self.formatter = formatter

        self.logger = None
        self.file_handler = None
        self.console_handler = None

        self._init_logger()
        self._init_handler()

    def _init_logger(self):

        if self.logger_name is None:
            self.logger = logging.getLogger('sniffer')
        else:
            self.logger = logging.getLogger(self.logger_name)

        self.logger.setLevel(self.level)

        if self.file_name is None:
            self.file_name = '%s' % strftime('%Y-%m-%d_%H_%M_%S')

        if self.formatter is None:
            self.formatter = logging.Formatter('[%(levelname)-8s] %(asctime)s %(filename)s:%(lineno)d %(message)s')

    def _init_handler(self):

        # default handler is console
        if self.log_type is None or self.log_type == "console":
            self.console_handler = logging.StreamHandler()
            self.console_handler.setLevel(self.level)
            self.console_handler.setFormatter(self.formatter)

            self.logger.addHandler(self.console_handler)

        elif self.log_type == "file":
            self.file_handler = logging.FileHandler(self.file_name)
            self.file_handler.setLevel(self.level)
            self.file_handler.setFormatter(self.formatter)

            self.logger.addHandler(self.file_handler)
        # use both handler
        else:
            self.console_handler = logging.StreamHandler()
            self.console_handler.setLevel(self.level)
            self.console_handler.setFormatter(self.formatter)

            self.file_handler = logging.FileHandler(self.file_name)
            self.file_handler.setLevel(self.level)
            self.file_handler.setFormatter(self.formatter)

            self.logger.addHandler(self.console_handler)
            self.logger.addHandler(self.file_handler)

    def get_logger(self):
        return self.logger


parser = configparser.ConfigParser()
parser.read('config.ini')
file_name = parser['Logger']['file_name']
log_type = parser['Logger']['log_type']
log_level = parser['Logger']['log_level']
# CRITICAL, FATAL = CRITICAL, ERROR, WARNING, WARN = WARNING, INFO, DEBUG, NOTSET
log_dict = {'CRITICAL': logging.CRITICAL, 'FATAL': logging.FATAL, 'ERROR': logging.ERROR, 'WARNING': logging.WARNING, 'WARN': logging.WARN, 'INFO': logging.INFO, 'DEBUG': logging.DEBUG, 'NOTSET': logging.NOTSET}
try:
    log_level = log_dict[log_level]
except KeyError:
    log_level = log_dict['DEBUG']

log = Logger(file_name=file_name, log_type=log_type, level=log_level)
logger = log.get_logger()

