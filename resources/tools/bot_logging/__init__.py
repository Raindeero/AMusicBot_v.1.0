from logging import Filter, StreamHandler, INFO, WARNING, basicConfig
from logging.handlers import RotatingFileHandler
from sys import stdout


def set_logging(debug: bool):
    class MyFilter(Filter):
        def __init__(self, level, name=''):
            self.__level = level
            super(MyFilter, self).__init__(name)

        def filter(self, log_record):
            return log_record.levelno <= self.__level

    console = StreamHandler(stdout)
    console_lvl = INFO if debug else WARNING
    console.setLevel(console_lvl)
    console.addFilter(MyFilter(INFO))

    file_log = RotatingFileHandler(
        filename='logs/soft.log', mode='a', maxBytes=512_000_000, backupCount=1,
        encoding="utf-8"
    )
    file_log.setLevel(INFO)

    error = StreamHandler()
    error.setLevel(WARNING)

    basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=INFO, handlers=[console, error, file_log]
    )
