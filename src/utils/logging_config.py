"""Logging configuration for the table filtering application."""

import logging
import sys
from typing import Optional


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
    """
    Configure structured logging for the application.
    
    Args:
        level: Logging level (default: INFO)
        log_file: Optional file path for file logging
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger('flexible_table')
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler with structured format
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def log_file_upload(logger: logging.Logger, file_name: str, file_size: int, status: str, duration: Optional[float] = None):
    """
    Log file upload event.
    
    Args:
        logger: Logger instance
        file_name: Name of uploaded file
        file_size: File size in bytes
        status: Upload status ('success' or 'error')
        duration: Optional upload duration in seconds
    """
    log_data = {
        'event': 'file_upload',
        'file_name': file_name,
        'file_size': file_size,
        'status': status,
    }
    
    if duration is not None:
        log_data['duration_seconds'] = duration
    
    logger.info(f"File upload: {log_data}")


def log_filter_operation(logger: logging.Logger, operation: str, filter_count: int, result_count: int, duration: Optional[float] = None):
    """
    Log filter operation event.
    
    Args:
        logger: Logger instance
        operation: Filter operation type ('single', 'multiple', 'clear')
        filter_count: Number of filters applied
        result_count: Number of rows after filtering
        duration: Optional operation duration in seconds
    """
    log_data = {
        'event': 'filter_operation',
        'operation': operation,
        'filter_count': filter_count,
        'result_count': result_count,
    }
    
    if duration is not None:
        log_data['duration_seconds'] = duration
    
    logger.info(f"Filter operation: {log_data}")

