import logging
import sys
import os


def get_logger(name):
    """
    Get a logger instance with the specified name.
    """
    logger = logging.getLogger(name)
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logger.setLevel(log_level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger


# Usage example
# logger = get_logger(__name__)
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
