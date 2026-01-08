"""Filter engine for applying filters to DataFrames."""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np


def validate_filter_operator(operator: str, data_type: str) -> bool:
    """
    Validate if an operator is valid for a given data type.
    
    Args:
        operator: Filter operator (e.g., 'equals', 'contains', 'greater_than')
        data_type: Column data type ('text', 'numeric', 'date')
    
    Returns:
        True if operator is valid for the data type, False otherwise
    """
    text_operators = ['equals', 'contains', 'starts_with', 'ends_with']
    numeric_operators = ['equals', 'greater_than', 'less_than', 'between']
    date_operators = ['equals', 'before', 'after', 'between']
    
    if data_type == 'text':
        return operator in text_operators
    elif data_type == 'numeric':
        return operator in numeric_operators
    elif data_type == 'date':
        return operator in date_operators
    else:
        return False


def apply_single_filter(df: pd.DataFrame, column_name: str, operator: str, value: Any, data_type: str = 'text') -> pd.DataFrame:
    """
    Apply a single filter condition to a DataFrame.
    
    Args:
        df: Input pandas DataFrame
        column_name: Column to filter on
        operator: Filter operator
        value: Filter value (can be single value, list, or tuple for 'between')
        data_type: Column data type ('text', 'numeric', 'date')
    
    Returns:
        Filtered DataFrame
    """
    if column_name not in df.columns:
        return df
    
    col = df[column_name]
    
    # Handle missing values
    mask = pd.Series([True] * len(df), index=df.index)
    
    if operator == 'equals':
        if isinstance(value, list):
            mask = col.isin(value)
        else:
            mask = col == value
    elif operator == 'contains':
        mask = col.astype(str).str.contains(str(value), case=False, na=False)
    elif operator == 'starts_with':
        mask = col.astype(str).str.startswith(str(value), na=False)
    elif operator == 'ends_with':
        mask = col.astype(str).str.endswith(str(value), na=False)
    elif operator == 'greater_than':
        mask = col > value
    elif operator == 'less_than':
        mask = col < value
    elif operator == 'between':
        if isinstance(value, tuple) and len(value) == 2:
            # Validate that min < max (per data-model.md specification)
            if value[0] > value[1]:
                raise ValueError(f"Invalid 'between' filter: min value ({value[0]}) must be less than or equal to max value ({value[1]})")
            mask = (col >= value[0]) & (col <= value[1])
        else:
            mask = pd.Series([False] * len(df), index=df.index)
    elif operator == 'before':
        mask = col < value
    elif operator == 'after':
        mask = col > value
    else:
        # Unknown operator, return original DataFrame
        return df
    
    return df[mask]


def apply_text_filter(df: pd.DataFrame, column_name: str, operator: str, value: Any) -> pd.DataFrame:
    """
    Apply a text filter to a DataFrame.
    
    Args:
        df: Input pandas DataFrame
        column_name: Column to filter on
        operator: Filter operator ('equals', 'contains', 'starts_with', 'ends_with')
        value: Filter value
    
    Returns:
        Filtered DataFrame
    """
    return apply_single_filter(df, column_name, operator, value, data_type='text')


def apply_numeric_filter(df: pd.DataFrame, column_name: str, operator: str, value: Any) -> pd.DataFrame:
    """
    Apply a numeric filter to a DataFrame.
    
    Args:
        df: Input pandas DataFrame
        column_name: Column to filter on
        operator: Filter operator ('equals', 'greater_than', 'less_than', 'between')
        value: Filter value (can be single value or tuple for 'between')
    
    Returns:
        Filtered DataFrame
    """
    return apply_single_filter(df, column_name, operator, value, data_type='numeric')


def apply_date_filter(df: pd.DataFrame, column_name: str, operator: str, value: Any) -> pd.DataFrame:
    """
    Apply a date filter to a DataFrame.
    
    Args:
        df: Input pandas DataFrame
        column_name: Column to filter on
        operator: Filter operator ('equals', 'before', 'after', 'between')
        value: Filter value (can be single value or tuple for 'between')
    
    Returns:
        Filtered DataFrame
    """
    return apply_single_filter(df, column_name, operator, value, data_type='date')


def apply_multiple_filters(df: pd.DataFrame, filter_conditions: List[Dict], logic_operator: str = 'AND') -> pd.DataFrame:
    """
    Apply multiple filter conditions to a DataFrame with AND/OR logic.
    
    Args:
        df: Input pandas DataFrame
        filter_conditions: List of filter condition dictionaries, each with:
            - column_name: Column to filter on
            - operator: Filter operator
            - value: Filter value
            - data_type: Column data type (optional, defaults to 'text')
        logic_operator: 'AND' or 'OR' to combine conditions
    
    Returns:
        Filtered DataFrame
    
    Raises:
        ValueError: If more than 10 filter conditions are provided
    """
    if not filter_conditions:
        return df
    
    # Maximum 10 conditions allowed
    if len(filter_conditions) > 10:
        raise ValueError("Maximum 10 filter conditions allowed")
    
    result_df = df.copy()
    
    # Apply each filter condition
    masks = []
    for condition in filter_conditions:
        col = condition.get('column_name')
        op = condition.get('operator')
        val = condition.get('value')
        dtype = condition.get('data_type', 'text')
        
        if col and op is not None:
            filtered = apply_single_filter(result_df, col, op, val, dtype)
            # Create mask for this condition
            mask = result_df.index.isin(filtered.index)
            masks.append(mask)
    
    if not masks:
        return result_df
    
    # Combine masks based on logic operator
    if logic_operator.upper() == 'OR':
        # OR: at least one condition must be true
        combined_mask = masks[0]
        for mask in masks[1:]:
            combined_mask = combined_mask | mask
    else:
        # AND (default): all conditions must be true
        combined_mask = masks[0]
        for mask in masks[1:]:
            combined_mask = combined_mask & mask
    
    return result_df[combined_mask]
