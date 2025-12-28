"""Data formatting utilities for the table filtering application."""

from typing import Any
import pandas as pd


def format_error_message(error: Exception, context: str = "") -> str:
    """
    Format exception into user-friendly error message.
    
    Args:
        error: Exception object
        context: Additional context about where the error occurred
    
    Returns:
        User-friendly error message string
    """
    error_type = type(error).__name__
    error_message = str(error)
    
    # Map common exceptions to user-friendly messages
    user_friendly_messages = {
        'FileNotFoundError': 'File not found',
        'PermissionError': 'Permission denied',
        'ValueError': 'Invalid value provided',
        'KeyError': 'Required field missing',
        'TypeError': 'Invalid data type',
    }
    
    base_message = user_friendly_messages.get(error_type, f'{error_type}: {error_message}')
    
    if context:
        return f'{context}: {base_message}'
    
    return base_message


def format_row_count(total_rows: int, filtered_rows: int = None) -> str:
    """
    Format row count display string.
    
    Args:
        total_rows: Total number of rows in the dataset
        filtered_rows: Number of filtered rows (if filters are applied)
    
    Returns:
        Formatted row count string
    """
    if filtered_rows is not None and filtered_rows != total_rows:
        return f"Filtered rows: {filtered_rows:,} / {total_rows:,}"
    return f"Total rows: {total_rows:,}"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
    
    Returns:
        Formatted file size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"



