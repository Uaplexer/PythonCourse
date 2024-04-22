import logging


def setup_logger():
    """
    Setup logger configuration and return a logger instance.

    This function configures the logger to write log messages to 'my_log_file.log' with DEBUG level.
    The log messages format includes timestamp, log level, and message content.

    :return: Logger instance for 'my_logger'.
    """
    logging.basicConfig(
        filename='my_log_file.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('my_logger')
