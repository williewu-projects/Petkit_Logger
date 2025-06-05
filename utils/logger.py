import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(name=__name__):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set to INFO or WARNING in production

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating file handler
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "petkit.log"),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=20
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.propagate = False  # Avoid duplicate logs in root
    return logger