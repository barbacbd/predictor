import logging


class LogFormatter(logging.Formatter):
    '''Formatter class that will be used for formatting information in color.'''
    green = "\x1b[32;20m"
    blue = "\x1b[34;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    purple = "\x1b[35;20m"
    reset = "\x1b[0m"
    fmt = "[%(levelname)s]: %(message)s"

    FORMATS = {
        logging.DEBUG: blue + fmt + reset,
        logging.INFO: green + fmt + reset,
        logging.WARNING: yellow + fmt + reset,
        logging.ERROR: red + fmt + reset,
        logging.CRITICAL: purple + fmt + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(verbosity=logging.DEBUG):
    '''Wrap the logging.getLogger functionality

    :param verbosity: Level of verbosity for the logger
    :return: logging.log formatted with the NauticalLogFormatter
    '''
    log = logging.getLogger('predictor')

    if not log.handlers:
        log.setLevel(verbosity)
        
        handler = logging.StreamHandler()
        handler.setFormatter(LogFormatter())
        log.addHandler(handler)

    return log
