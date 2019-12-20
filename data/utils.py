import logging
from app.config import LOG_LEVEL, LOGFILE_PATH

def get_logger(app_name):
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s",
                        level=LOG_LEVEL,
                        datefmt="%Y%m%d %H%M%S")
    logger = logging.getLogger(app_name)
    # Set formatter
    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%Y%m%d %H%M%S")
    # Create console logger
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)

    # Create file logger
    file_handler = logging.FileHandler(LOGFILE_PATH, mode="a+")
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(formatter)

    # Add handlers and return logger object
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger