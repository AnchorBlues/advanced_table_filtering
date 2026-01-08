"""Data parsing utilities for various file formats."""

import base64
import io
from typing import Tuple
import pandas as pd


def parse_file(upload_contents: str, upload_filename: str) -> Tuple[pd.DataFrame, str]:
    """
    Parse uploaded file content based on file extension.
    
    Args:
        upload_contents: Base64 encoded file content (with data URL prefix)
        upload_filename: Original filename with extension
        
    Returns:
        Tuple of (DataFrame, file_format)
    """
    # Extract base64 content (remove data URL prefix if present)
    if ',' in upload_contents:
        content_type, base64_content = upload_contents.split(',', 1)
    else:
        base64_content = upload_contents
    
    # Decode base64 content
    try:
        file_content = base64.b64decode(base64_content)
    except Exception as e:
        raise ValueError(f"Invalid base64 encoded file content: {str(e)}")
    
    # Determine file format from extension
    file_ext = upload_filename.lower().split('.')[-1] if '.' in upload_filename else ''
    
    # Parse based on file extension
    if file_ext in ['csv']:
        df = parse_csv(file_content, upload_filename)
        return df, 'csv'
    elif file_ext in ['xlsx', 'xls']:
        df = parse_excel(file_content, upload_filename)
        return df, 'excel'
    elif file_ext in ['json']:
        df = parse_json(file_content, upload_filename)
        return df, 'json'
    elif file_ext in ['feather', 'ftr']:
        df = pd.read_feather(io.BytesIO(file_content))
        return df, 'feather'
    elif file_ext in ['parquet', 'pq']:
        df = pd.read_parquet(io.BytesIO(file_content))
        return df, 'parquet'
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")


def parse_csv(file_content: bytes, filename: str) -> pd.DataFrame:
    """
    Parse CSV file content.
    
    Args:
        file_content: Raw file content as bytes
        filename: Original filename
        
    Returns:
        Parsed pandas DataFrame
        
    Raises:
        ValueError: If file is empty or cannot be parsed
    """
    # Check if file is empty
    if len(file_content) == 0:
        raise ValueError(f"CSV file '{filename}' is empty")
    
    try:
        # Try UTF-8 first
        df = pd.read_csv(io.BytesIO(file_content), encoding='utf-8')
    except UnicodeDecodeError:
        # Fallback to other encodings
        try:
            df = pd.read_csv(io.BytesIO(file_content), encoding='shift_jis')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(io.BytesIO(file_content), encoding='latin-1')
            except UnicodeDecodeError as e:
                raise ValueError(f"Failed to decode CSV file '{filename}': unsupported encoding") from e
    except Exception as e:
        raise ValueError(f"Failed to parse CSV file '{filename}': {str(e)}") from e
    
    # Check if DataFrame is empty (no rows)
    if len(df) == 0 and len(df.columns) == 0:
        raise ValueError(f"CSV file '{filename}' contains no data")
    
    return df


def parse_excel(file_content: bytes, filename: str) -> pd.DataFrame:
    """
    Parse Excel file content.
    
    Args:
        file_content: Raw file content as bytes
        filename: Original filename
        
    Returns:
        Parsed pandas DataFrame
        
    Raises:
        ValueError: If required library (xlrd or openpyxl) is not installed
        ValueError: If file parsing fails
    """
    file_ext = filename.lower().split('.')[-1] if '.' in filename else 'xlsx'
    try:
        if file_ext == 'xls':
            # Old Excel format
            df = pd.read_excel(io.BytesIO(file_content), engine='xlrd')
        else:
            # New Excel format (.xlsx)
            df = pd.read_excel(io.BytesIO(file_content), engine='openpyxl')
        return df
    except ImportError as e:
        if 'xlrd' in str(e) or 'openpyxl' in str(e):
            required_lib = 'xlrd' if file_ext == 'xls' else 'openpyxl'
            raise ValueError(
                f"Required library '{required_lib}' is not installed. "
                f"Please install it with: pip install {required_lib}"
            ) from e
        raise
    except Exception as e:
        raise ValueError(f"Failed to parse Excel file '{filename}': {str(e)}") from e


def parse_json(file_content: bytes, filename: str) -> pd.DataFrame:
    """
    Parse JSON file content.
    
    Args:
        file_content: Raw file content as bytes
        filename: Original filename
        
    Returns:
        Parsed pandas DataFrame
        
    Raises:
        ValueError: If file is empty, invalid JSON, or unsupported structure
    """
    # Check if file is empty
    if len(file_content) == 0:
        raise ValueError(f"JSON file '{filename}' is empty")
    
    # Try to decode as UTF-8
    try:
        json_str = file_content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            json_str = file_content.decode('latin-1')
        except UnicodeDecodeError as e:
            raise ValueError(f"Failed to decode JSON file '{filename}': unsupported encoding") from e
    
    # Try to parse as JSON
    import json
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in file '{filename}': {str(e)}") from e
    except Exception as e:
        raise ValueError(f"Failed to parse JSON file '{filename}': {str(e)}") from e
    
    # Handle different JSON structures
    try:
        if isinstance(data, list):
            # List of objects
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # Check if it's a records format
            if 'records' in data or 'data' in data:
                records = data.get('records', data.get('data', []))
                df = pd.DataFrame(records)
            else:
                # Single object or other structure
                df = pd.DataFrame([data])
        else:
            raise ValueError("Unsupported JSON structure")
    except Exception as e:
        raise ValueError(f"Failed to convert JSON data to DataFrame in file '{filename}': {str(e)}") from e
    
    # Check if DataFrame is empty (no rows)
    if len(df) == 0 and len(df.columns) == 0:
        raise ValueError(f"JSON file '{filename}' contains no data")
    
    return df

