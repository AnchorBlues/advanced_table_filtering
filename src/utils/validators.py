"""File validation utilities for the table filtering application."""

from typing import Optional, Tuple
import base64


def validate_file_type(file_name: str, allowed_extensions: list[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate if file extension is in the allowed list.
    
    Args:
        file_name: Name of the uploaded file
        allowed_extensions: List of allowed file extensions (e.g., ['.csv', '.xlsx'])
    
    Returns:
        Tuple of (is_valid, error_message). If valid, error_message is None.
    """
    if not file_name:
        return False, "File name is required"
    
    file_extension = None
    for ext in allowed_extensions:
        if file_name.lower().endswith(ext.lower()):
            file_extension = ext
            break
    
    if file_extension is None:
        allowed_str = ", ".join(allowed_extensions)
        return False, f"Invalid file type. Allowed types: {allowed_str}"
    
    return True, None


def validate_file_size(file_content_base64: str, max_size_bytes: int) -> Tuple[bool, Optional[str]]:
    """
    Validate if file size is within the maximum limit.
    
    Args:
        file_content_base64: Base64 encoded file content
        max_size_bytes: Maximum file size in bytes
    
    Returns:
        Tuple of (is_valid, error_message). If valid, error_message is None.
    """
    if not file_content_base64:
        return False, "File content is required"
    
    try:
        # Decode base64 to get actual file size
        # Base64 encoding increases size by ~33%, so we estimate
        # Actual size = base64_length * 3 / 4
        base64_length = len(file_content_base64.split(',')[-1])  # Remove data URL prefix if present
        estimated_size = (base64_length * 3) // 4
        
        if estimated_size > max_size_bytes:
            max_size_mb = max_size_bytes / (1024 * 1024)
            return False, f"File size ({estimated_size / (1024 * 1024):.2f} MB) exceeds maximum limit ({max_size_mb:.2f} MB)"
        
        return True, None
    except Exception as e:
        return False, f"Error validating file size: {str(e)}"


def validate_file_upload(file_name: str, file_content_base64: str, max_size_bytes: int = 52_428_800) -> Tuple[bool, Optional[str]]:
    """
    Comprehensive file upload validation.
    
    Args:
        file_name: Name of the uploaded file
        file_content_base64: Base64 encoded file content
        max_size_bytes: Maximum file size in bytes (default: 50MB)
    
    Returns:
        Tuple of (is_valid, error_message). If valid, error_message is None.
    """
    allowed_extensions = ['.csv', '.xlsx', '.xls', '.json', '.feather', '.ftr', '.parquet', '.pq']
    
    # Validate file type
    is_valid_type, type_error = validate_file_type(file_name, allowed_extensions)
    if not is_valid_type:
        return False, type_error
    
    # Validate file size
    is_valid_size, size_error = validate_file_size(file_content_base64, max_size_bytes)
    if not is_valid_size:
        return False, size_error
    
    return True, None

