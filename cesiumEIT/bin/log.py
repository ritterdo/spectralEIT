import logging
from datetime import datetime

debug_mode = True

def get_logger(name:str = __name__):

    now = datetime.now()

    logger = logging.getLogger(name) 
    logger.setLevel(logging.DEBUG)  

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    if debug_mode:
        file_debug_handler = logging.FileHandler("logs/debug_" + now.strftime("%Y-%m-%d_%H:%M") + ".log")
        file_debug_handler.setLevel(logging.DEBUG)  
        file_debug_handler.setFormatter(formatter)
        logger.addHandler(file_debug_handler)
    else:
        file_info_handler = logging.FileHandler("logs/info_" + now.strftime("%Y-%m-%d_%H:%M") + ".log")
        file_info_handler.setLevel(logging.INFO)  
        file_info_handler.setFormatter(formatter)
        logger.addHandler(file_info_handler)

    # Create a console handler to log messages to the console
    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.INFO)  # Set the desired level for the console handler
    # console_handler.setFormatter(formatter)

    # logger.addHandler(console_handler)

    return logger