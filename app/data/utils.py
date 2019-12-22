import logging
from app.config import LOG_LEVEL


def get_logger(app_name, logfile_path):
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s",
                        level=logging.DEBUG,
                        datefmt="%Y%m%d %H%M%S")
    logger = logging.getLogger(app_name)
    # Set formatter
    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%Y%m%d %H%M%S")

    # Create file logger
    file_handler = logging.FileHandler(logfile_path, mode="a+")
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)

    # Add handlers and return logger object
    logger.addHandler(file_handler)

    return logger


