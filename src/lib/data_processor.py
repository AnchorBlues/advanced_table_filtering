"""Data processing utilities for table data transformation."""

from typing import Dict, List
import warnings
import pandas as pd
import numpy as np


def detect_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """
    Detect data types for each column in the DataFrame.
    
    Args:
        df: Input pandas DataFrame
    
    Returns:
        Dictionary mapping column names to detected types ('text', 'numeric', 'date')
    """
    column_types = {}
    
    for col in df.columns:
        col_data = df[col].dropna()
        
        if len(col_data) == 0:
            # Empty column defaults to text
            column_types[col] = 'text'
            continue
        
        # Check if column is datetime
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            column_types[col] = 'date'
        # Try to parse as date if it's a string column
        elif df[col].dtype == 'object':
            # Try to parse first few non-null values as dates
            sample_values = col_data.head(10).astype(str)
            try:
                # Suppress pandas date parsing warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    # Try to parse as date (pandas will infer format automatically)
                    pd.to_datetime(sample_values, errors='raise')
                column_types[col] = 'date'
            except (ValueError, TypeError):
                # Not a date, check if numeric
                if pd.api.types.is_numeric_dtype(df[col]):
                    column_types[col] = 'numeric'
                else:
                    column_types[col] = 'text'
        # Check if column is numeric
        elif pd.api.types.is_numeric_dtype(df[col]):
            column_types[col] = 'numeric'
        else:
            # Default to text
            column_types[col] = 'text'
    
    return column_types


def handle_duplicate_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle duplicate column names by disambiguating them.
    
    Args:
        df: Input pandas DataFrame (may have duplicate column names)
    
    Returns:
        DataFrame with unique column names (duplicates renamed with _1, _2, etc.)
    """
    df = df.copy()
    
    # Get duplicate column names
    seen = {}
    new_columns = []
    
    for col in df.columns:
        if col in seen:
            seen[col] += 1
            new_col = f"{col}_{seen[col]}"
            new_columns.append(new_col)
        else:
            seen[col] = 0
            new_columns.append(col)
    
    df.columns = new_columns
    
    return df


def convert_to_json_format(df: pd.DataFrame) -> List[Dict]:
    """
    Convert DataFrame to JSON-serializable format (list of dictionaries).
    
    Args:
        df: Input pandas DataFrame
    
    Returns:
        List of dictionaries (DataFrame.to_dict('records') format)
    """
    # Replace NaN with None for JSON serialization
    df_clean = df.replace({np.nan: None})
    
    # Convert to list of dictionaries
    return df_clean.to_dict('records')


def prepare_table_data(df: pd.DataFrame, file_format: str, file_name: str) -> Dict:
    """
    Prepare table data structure for storage in dcc.Store.
    
    Args:
        df: Parsed pandas DataFrame
        file_format: File format ('csv', 'excel', 'json')
        file_name: Original file name
    
    Returns:
        Dictionary with table data structure matching data-model.md
    """
    # Handle duplicate columns
    df_processed = handle_duplicate_columns(df)
    
    # Detect column types
    column_types = detect_column_types(df_processed)
    
    # Convert to JSON format
    dataframe_json = convert_to_json_format(df_processed)
    
    return {
        'dataframe_json': dataframe_json,
        'row_count': len(df_processed),
        'column_count': len(df_processed.columns),
        'column_names': list(df_processed.columns),
        'column_types': column_types,
        'file_format': file_format,
        'file_name': file_name
    }
