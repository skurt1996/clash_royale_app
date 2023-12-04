"""
logger used by db.py
"""
import logging

def configured_logger(file_name):
    """
    Configures and returns a logger object for logging database operations.

    Returns:
        logging.Logger: The configured logger object.

    The logger is configured with the following settings:
    - Log level: DEBUG
    - File handler: Logs are written to a file named 'db.log' with DEBUG level.
    - Console handler: Logs are printed to the console with DEBUG level.

    Usage:
        logger = configure_logger()
        logger.debug('This is a debug message')
        logger.info('This is an info message')
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d - %(funcName)s)")

    file_handler = logging.FileHandler(file_name)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger

TX_ROLLBACK_MSG = "Transaction rolled back"