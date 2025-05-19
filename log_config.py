import logging
import os
import time
from logging.handlers import RotatingFileHandler

def setup_logging(log_dir="logs", log_level=logging.INFO, console_level=logging.INFO):
    os.makedirs(log_dir, exist_ok=True)
    timestamp = time.strftime("%m%d_%H%M%S")
    
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    if root_logger.handlers:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)-2s | %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s | %(message)s'
    )
    
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, f'simulation_{timestamp}.log'),
        backupCount=5
    )
    
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    return root_logger

def get_logger(name):
    return logging.getLogger(name)