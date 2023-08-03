import logging
from datetime import datetime
import os


def get_logger():

    now = datetime.now()

    logger = logging.getLogger() 
    logger.setLevel(logging.INFO)  

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s")
    file_info_handler = logging.FileHandler("logs/" + now.strftime("%Y-%m-%d_%H:%M") + ".log")
    file_info_handler.setLevel(logging.INFO)  
    file_info_handler.setFormatter(formatter)
    logger.addHandler(file_info_handler)

    logger.info("Initializing logger")

    return logger
