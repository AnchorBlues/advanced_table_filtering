"""Error handling utilities for user-friendly error messages."""

from typing import Optional
import traceback
from .formatters import format_error_message


class TableFilterError(Exception):
    """Base exception for table filtering application errors."""
    pass


class FileUploadError(TableFilterError):
    """Error during file upload or parsing."""
    pass


class FilterError(TableFilterError):
    """Error during filter application."""
    pass


class ValidationError(TableFilterError):
    """Error during data validation."""
    pass


def handle_file_upload_error(error: Exception, file_name: str = "") -> str:
    """
    Handle file upload errors and return user-friendly message.
    
    Args:
        error: Exception that occurred during file upload
        file_name: Name of the file being uploaded
    
    Returns:
        User-friendly error message
    """
    context = f"Error uploading file '{file_name}'" if file_name else "Error uploading file"
    
    # Map specific errors to user-friendly messages
    if isinstance(error, FileNotFoundError):
        return f"{context}: File not found"
    elif isinstance(error, PermissionError):
        return f"{context}: Permission denied"
    elif isinstance(error, ValueError):
        return f"{context}: Invalid file format or corrupted file"
    elif isinstance(error, UnicodeDecodeError):
        return f"{context}: File encoding issue. Please ensure the file is UTF-8 encoded or try a different encoding."
    else:
        return format_error_message(error, context)


def handle_filter_error(error: Exception, filter_description: str = "") -> str:
    """
    Handle filter application errors and return user-friendly message.
    
    Args:
        error: Exception that occurred during filtering
        filter_description: Description of the filter being applied
    
    Returns:
        User-friendly error message
    """
    context = f"Error applying filter" + (f": {filter_description}" if filter_description else "")
    
    if isinstance(error, KeyError):
        return f"{context}: Column not found in data"
    elif isinstance(error, ValueError):
        return f"{context}: Invalid filter value or operator"
    elif isinstance(error, TypeError):
        return f"{context}: Data type mismatch. Please check filter value matches column type."
    else:
        return format_error_message(error, context)


def handle_parsing_error(error: Exception, file_format: str = "") -> str:
    """
    Handle file parsing errors and return user-friendly message.
    
    Args:
        error: Exception that occurred during parsing
        file_format: Format of the file being parsed (csv, excel, json)
    
    Returns:
        User-friendly error message
    """
    context = f"Error parsing {file_format} file" if file_format else "Error parsing file"
    
    if isinstance(error, ValueError):
        return f"{context}: Invalid file format or structure. Please check the file is properly formatted."
    elif isinstance(error, KeyError):
        return f"{context}: Required columns or structure missing in file"
    else:
        return format_error_message(error, context)

