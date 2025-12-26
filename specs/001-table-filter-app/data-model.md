# Data Model: Advanced Table Filtering Web Application

**Date**: 2025-01-27  
**Feature**: Advanced Table Filtering Web Application  
**Branch**: 001-table-filter-app

## Entities

### TableData

Represents the uploaded tabular data with rows and columns.

**Attributes**:
- `dataframe` (pandas.DataFrame): The parsed table data
- `row_count` (int): Total number of rows in the dataset
- `column_count` (int): Total number of columns
- `column_names` (list[str]): List of column names/headers
- `column_types` (dict[str, str]): Mapping of column names to data types (e.g., 'text', 'numeric', 'date')
- `file_format` (str): Original file format ('csv', 'excel', 'json')
- `file_name` (str): Original uploaded file name
- `upload_timestamp` (datetime): When the file was uploaded

**State Transitions**:
- `empty` → `loaded`: File uploaded and parsed successfully
- `loaded` → `filtered`: Filters applied to data
- `loaded` → `empty`: File cleared/reset

**Validation Rules**:
- `row_count` must be >= 0
- `column_count` must be >= 1
- `column_names` must be unique (duplicates disambiguated)
- Maximum `row_count`: 10,000 (enforced during upload)
- Maximum file size: 50MB (enforced during upload)

**Relationships**:
- Has many `FilterCondition` instances (one per column filter)
- Belongs to one `FilterSet` (current active filters)

### FilterCondition

Represents a single filtering rule applied to a column.

**Attributes**:
- `column_name` (str): Name of the column to filter
- `operator` (str): Filter operator ('equals', 'contains', 'starts_with', 'ends_with', 'greater_than', 'less_than', 'between', 'equals_date', 'before_date', 'after_date', 'between_dates')
- `value` (str | number | date | tuple): Filter value(s). For 'between' operators, tuple of (min, max)
- `data_type` (str): Data type of the column ('text', 'numeric', 'date')
- `is_active` (bool): Whether this filter condition is currently applied

**State Transitions**:
- `inactive` → `active`: Filter condition enabled
- `active` → `inactive`: Filter condition disabled/cleared

**Validation Rules**:
- `column_name` must exist in the table's column names
- `operator` must be valid for the column's `data_type`
- `value` must match the expected type for the operator
- For 'between' operators, `value` must be a tuple of (min, max) where min < max

**Relationships**:
- Belongs to one `TableData` instance
- Part of one `FilterSet`

### FilterSet

Represents a collection of filter conditions applied together.

**Attributes**:
- `conditions` (list[FilterCondition]): List of active filter conditions
- `logic_operator` (str): How conditions are combined ('AND' or 'OR')
- `is_saved` (bool): Whether this filter set is saved for reuse
- `saved_name` (str | None): Name of saved filter set (if saved)
- `created_at` (datetime): When filter set was created
- `result_count` (int): Number of rows matching the filter set

**State Transitions**:
- `empty` → `active`: First filter condition added
- `active` → `modified`: Filter condition added/removed/modified
- `active` → `saved`: Filter set saved with a name
- `active` → `empty`: All filters cleared

**Validation Rules**:
- `logic_operator` must be 'AND' or 'OR'
- `conditions` list can be empty (no filters applied)
- Maximum number of conditions: 10 (to prevent performance issues)
- `saved_name` must be unique if provided

**Relationships**:
- Contains many `FilterCondition` instances
- Applies to one `TableData` instance

### FileUpload

Represents the process of loading data into the system.

**Attributes**:
- `file_content` (bytes): Raw file content (base64 decoded)
- `file_name` (str): Original file name
- `file_size` (int): File size in bytes
- `file_type` (str): MIME type or file extension
- `upload_status` (str): Status ('pending', 'processing', 'success', 'error')
- `error_message` (str | None): Error message if upload/parsing failed
- `parsed_data` (TableData | None): Parsed table data if successful

**State Transitions**:
- `pending` → `processing`: File upload initiated
- `processing` → `success`: File parsed successfully
- `processing` → `error`: File parsing failed
- `success` → `pending`: New file upload initiated (reset)

**Validation Rules**:
- `file_size` must be <= 50MB (52,428,800 bytes)
- `file_type` must be one of: 'text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/json'
- `file_name` must have valid extension (.csv, .xlsx, .xls, .json)

**Relationships**:
- Produces one `TableData` instance (on successful upload)

## Data Type Mappings

### Column Type Detection

**Text Type**:
- Detected when column contains non-numeric strings
- Supports operators: 'equals', 'contains', 'starts_with', 'ends_with'

**Numeric Type**:
- Detected when column contains numbers (int or float)
- Supports operators: 'equals', 'greater_than', 'less_than', 'between'

**Date Type**:
- Detected when column contains date/datetime values
- Supports operators: 'equals_date', 'before_date', 'after_date', 'between_dates'
- Common date formats: ISO 8601, MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD

## State Management

### Application State (Dash dcc.Store)

The application maintains state in Dash's dcc.Store component:

```python
{
    'table_data': {
        'dataframe_json': list[dict],  # DataFrame as JSON (to_dict('records'))
        'row_count': int,
        'column_count': int,
        'column_names': list[str],
        'column_types': dict[str, str],
        'file_format': str,
        'file_name': str
    },
    'filter_set': {
        'conditions': list[FilterCondition],
        'logic_operator': str,
        'result_count': int
    },
    'upload_status': str  # Current upload status
}
```

**Note**: DataFrame is stored as JSON using `DataFrame.to_dict('records')` format for dcc.Store compatibility. When retrieving, reconstruct using `pd.DataFrame.from_dict(data['dataframe_json'])`.

### Filter Application Logic

1. User uploads file → `FileUpload` created → `TableData` created → stored in dcc.Store
2. User applies filter → `FilterCondition` created → added to `FilterSet` → stored in dcc.Store
3. Filter callback triggered → retrieves `TableData` and `FilterSet` from dcc.Store
4. Filter logic applied → filtered DataFrame created → table display updated

## Edge Case Handling

### Missing Values
- Null/NaN values in DataFrame are preserved
- Filtering: null values excluded from matches unless explicitly filtered for
- Display: null values shown as empty cells or "N/A"

### Duplicate Column Names
- Detected during parsing
- Disambiguated by appending "_1", "_2", etc. to duplicate names
- User notified of disambiguation

### Inconsistent Column Counts (CSV)
- Rows with fewer columns: missing values filled with NaN
- Rows with more columns: extra columns ignored or handled as additional columns

### Large Datasets
- Virtual scrolling enabled for tables > 1,000 rows
- Filter operations optimized using pandas vectorized operations
- Memory monitoring to prevent browser crashes

### Encoding Issues
- Automatic encoding detection for CSV files (utf-8, shift-jis, etc.)
- Fallback to utf-8 with error handling if detection fails
- User notified of encoding issues

