import logging
import os
from datetime import datetime


def setup_logger(output_dir: str, log_level = logging.INFO) -> logging.Logger:
    """
    Set up comprehensive logging with error logging to one file,
    general logging to another file, and console output.
    
    Args:
        output_dir: Directory where log files will be saved
        
    Returns:
        Configured logger instance
    """
    # Create timestamp for log file names
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(output_dir, "logs")
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    
    # Define log file paths
    general_log_file = os.path.join(log_path, f"general_log_{timestamp}.log")
    error_log_file = os.path.join(log_path, f"error_log_{timestamp}.log")
    
    # Create logger
    logger = logging.getLogger("sec_analyzer")
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler for all levels
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # General log file handler (INFO and above)
    general_file_handler = logging.FileHandler(general_log_file, encoding='utf-8')
    general_file_handler.setLevel(log_level)
    general_file_handler.setFormatter(detailed_formatter)
    logger.addHandler(general_file_handler)
    
    # Error log file handler (ERROR and above only)
    error_file_handler = logging.FileHandler(error_log_file, encoding='utf-8')
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_file_handler)
    
    # Log the setup completion
    logger.info(f"Logging system initialized")
    logger.info(f"General log file: {general_log_file}")
    logger.info(f"Error log file: {error_log_file}")
    
    return logger
