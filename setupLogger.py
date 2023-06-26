import logging,sys,os
from logging.handlers import TimedRotatingFileHandler

FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOGGER_DIR='log/'

import multiprocessing
class ScrapLogger():

    @classmethod
    def get_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(FORMATTER)
        return console_handler

    @classmethod
    def get_file_handler(self, LOG_FILE):
        if not os.path.isdir(LOGGER_DIR):
            os.mkdir(LOGGER_DIR)
        file_handler = TimedRotatingFileHandler(LOGGER_DIR+LOG_FILE, when='midnight')
        return file_handler

    @classmethod
    def get_logger(self, logger_name):
        logger = multiprocessing.get_logger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(self.get_console_handler())
        logger.addHandler(self.get_file_handler(logger_name+'.log'))
        logger.propagate = False
        return logger
