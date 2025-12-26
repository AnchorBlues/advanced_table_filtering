# Callback Contracts: Advanced Table Filtering Web Application

**Date**: 2025-01-27  
**Feature**: Advanced Table Filtering Web Application  
**Branch**: 001-table-filter-app

## Overview

This document defines the Dash callback interfaces for the table filtering application. Since Dash applications use callback-based architecture rather than RESTful APIs, these contracts define the callback signatures, inputs, outputs, and behaviors.

## Callback Conventions

- **Inputs**: Dash component properties that trigger the callback
- **Outputs**: Dash component properties that are updated by the callback
- **State**: Dash component properties used in callback but don't trigger it
- **Error Handling**: All callbacks must handle errors gracefully and return user-friendly error messages

## Callback Contracts

### 1. File Upload Callback

**Purpose**: Handle file upload, parse file content, and initialize table data.

**Callback ID**: `upload_file`

**Inputs**:
- `upload_contents` (dcc.Upload.contents): Base64 encoded file content
- `upload_filename` (dcc.Upload.filename): Original file name

**State**:
- None

**Outputs**:
- `table_data` (dcc.Store.data): Updated table data in dcc.Store
- `upload_status` (dcc.Store.data): Upload status message
- `table_display` (dash_table.DataTable.data): Table data for display
- `table_columns` (dash_table.DataTable.columns): Column definitions
- `row_count_display` (html.Div.children): Display of row count

**Behavior**:
1. Validate file type and size
2. Decode base64 content
3. Parse file based on extension (CSV/Excel/JSON)
4. Convert to pandas DataFrame
5. Detect column types
6. Store in dcc.Store
7. Update table display

**Error Cases**:
- Invalid file type → Return error message, clear table
- File too large → Return error message, clear table
- Parsing error → Return error message with details, clear table
- Encoding error → Return error message, attempt fallback encoding

**Success Response**:
```python
{
    'table_data': {
        'dataframe_json': <DataFrame.to_dict('records')>,  # JSON-serializable format
        'row_count': int,
        'column_count': int,
        'column_names': list[str],
        'column_types': dict[str, str],
        'file_format': str,
        'file_name': str
    },
    'upload_status': 'success',
    'table_display': <DataTable data>,  # Same as dataframe_json for display
    'table_columns': <DataTable columns>,
    'row_count_display': f"Total rows: {row_count}"
}
```

**Note**: DataFrame is stored as JSON using `DataFrame.to_dict('records')` format for dcc.Store compatibility. When retrieving, reconstruct DataFrame using `pd.DataFrame.from_dict(data['dataframe_json'])`.

**Error Response**:
```python
{
    'upload_status': 'error: {error_message}',
    'table_display': [],
    'table_columns': [],
    'row_count_display': 'Error: {error_message}'
}
```

---

### 2. Single Column Filter Callback

**Purpose**: Apply a single filter condition to a column and update table display.

**Callback ID**: `apply_column_filter`

**Inputs**:
- `filter_column` (dcc.Dropdown.value): Column name to filter
- `filter_operator` (dcc.Dropdown.value): Filter operator
- `filter_value` (dcc.Input.value): Filter value
- `filter_apply_btn` (html.Button.n_clicks): Apply button click

**State**:
- `table_data` (dcc.Store.data): Current table data
- `filter_set` (dcc.Store.data): Current filter set

**Outputs**:
- `filter_set` (dcc.Store.data): Updated filter set
- `table_display` (dash_table.DataTable.data): Filtered table data
- `row_count_display` (html.Div.children): Updated row count

**Behavior**:
1. Retrieve table data from dcc.Store
2. Create FilterCondition from inputs
3. Add/update condition in FilterSet
4. Apply filter to DataFrame
5. Update table display with filtered results
6. Update row count

**Error Cases**:
- Invalid column name → Return error, no filter applied
- Invalid operator for column type → Return error, no filter applied
- Invalid filter value → Return error, no filter applied
- No table data loaded → Return error message

**Success Response**:
```python
{
    'filter_set': {
        'conditions': [FilterCondition],
        'logic_operator': 'AND',
        'result_count': int
    },
    'table_display': <filtered DataTable data>,
    'row_count_display': f"Filtered rows: {result_count} / {total_rows}"
}
```

---

### 3. Multiple Filter Combination Callback

**Purpose**: Apply multiple filter conditions with AND/OR logic.

**Callback ID**: `apply_filter_combination`

**Inputs**:
- `filter_logic` (dcc.RadioItems.value): 'AND' or 'OR'
- `apply_filters_btn` (html.Button.n_clicks): Apply button click

**State**:
- `table_data` (dcc.Store.data): Current table data
- `filter_set` (dcc.Store.data): Current filter set with all conditions

**Outputs**:
- `filter_set` (dcc.Store.data): Updated filter set with logic operator
- `table_display` (dash_table.DataTable.data): Filtered table data
- `row_count_display` (html.Div.children): Updated row count

**Behavior**:
1. Retrieve table data and filter set from dcc.Store
2. Update FilterSet logic_operator
3. Apply all filter conditions with specified logic (AND/OR)
4. Update table display
5. Update row count

**Error Cases**:
- No filter conditions → Return message "No filters applied"
- All filters result in zero matches → Display "No results" message
- Invalid logic operator → Default to 'AND'

**Success Response**:
```python
{
    'filter_set': {
        'conditions': [FilterCondition, ...],
        'logic_operator': 'AND' | 'OR',
        'result_count': int
    },
    'table_display': <filtered DataTable data>,
    'row_count_display': f"Filtered rows: {result_count} / {total_rows}"
}
```

---

### 4. Clear Filter Callback

**Purpose**: Clear individual filter or all filters.

**Callback ID**: `clear_filter`

**Inputs**:
- `clear_single_btn` (html.Button.n_clicks): Clear single filter button
- `clear_all_btn` (html.Button.n_clicks): Clear all filters button
- `filter_to_clear` (dcc.Dropdown.value): Column name to clear (for single clear)

**State**:
- `table_data` (dcc.Store.data): Current table data
- `filter_set` (dcc.Store.data): Current filter set

**Outputs**:
- `filter_set` (dcc.Store.data): Updated filter set (cleared)
- `table_display` (dash_table.DataTable.data): Unfiltered table data
- `row_count_display` (html.Div.children): Updated row count

**Behavior**:
1. If clear single: Remove FilterCondition for specified column
2. If clear all: Remove all FilterConditions from FilterSet
3. Retrieve original table data from dcc.Store
4. Update table display with unfiltered data
5. Update row count

**Success Response**:
```python
{
    'filter_set': {
        'conditions': [],  # or reduced list for single clear
        'logic_operator': 'AND',
        'result_count': <original_row_count>
    },
    'table_display': <unfiltered DataTable data>,
    'row_count_display': f"Total rows: {original_row_count}"
}
```

---

### 5. Export Filtered Results Callback

**Purpose**: Export currently displayed (filtered) table data to CSV.

**Callback ID**: `export_filtered_data`

**Inputs**:
- `export_btn` (html.Button.n_clicks): Export button click

**State**:
- `table_data` (dcc.Store.data): Original table data with metadata
- `filter_set` (dcc.Store.data): Current active filter set
- `table_display` (dash_table.DataTable.data): Current filtered table data (for fallback)

**Outputs**:
- `download_data` (dcc.Download.data): CSV file download

**Behavior**:
1. Retrieve original DataFrame from dcc.Store (`table_data['dataframe_json']`)
2. Reconstruct DataFrame: `pd.DataFrame.from_dict(table_data['dataframe_json'])`
3. If filters are active, apply filter logic using `filter_set` to get filtered DataFrame
4. If no filters active, use original DataFrame
5. Convert filtered DataFrame to CSV string using `DataFrame.to_csv(index=False)`
6. Trigger browser download via dcc.Download component

**Error Cases**:
- No table data loaded → Return error message "No data to export"
- DataFrame reconstruction fails → Return error message
- Export fails → Return error message

**Success Response**:
- Browser download triggered with CSV file containing filtered results
- File name format: `{original_filename}_filtered_{timestamp}.csv`

---

### 6. Column Visibility Toggle Callback

**Purpose**: Show/hide columns in table display.

**Callback ID**: `toggle_column_visibility`

**Inputs**:
- `column_checklist` (dcc.Checklist.value): List of visible column names

**State**:
- `table_data` (dcc.Store.data): Current table data
- `table_columns` (dash_table.DataTable.columns): All column definitions

**Outputs**:
- `table_columns` (dash_table.DataTable.columns): Updated column definitions (hidden columns have `hidden=True`)

**Behavior**:
1. Retrieve all column definitions
2. Update `hidden` property based on checklist
3. Update table display

**Success Response**:
```python
{
    'table_columns': [
        {'name': col, 'id': col, 'hidden': not (col in visible_columns)}
        for col in all_columns
    ]
}
```

---

## Data Flow Diagrams

### File Upload Flow
```
User uploads file
  → upload_file callback triggered
  → Validate file
  → Parse file (CSV/Excel/JSON)
  → Create TableData entity
  → Store in dcc.Store
  → Update DataTable display
```

### Filter Application Flow
```
User sets filter condition
  → apply_column_filter callback triggered
  → Create FilterCondition
  → Add to FilterSet
  → Apply filter to DataFrame
  → Update DataTable display
  → Update row count
```

### Multiple Filter Flow
```
User applies multiple filters
  → apply_filter_combination callback triggered
  → Retrieve all FilterConditions from FilterSet
  → Apply with AND/OR logic
  → Update DataTable display
  → Update row count
```

## Error Handling Standards

All callbacks must:
1. Use try-except blocks to catch exceptions
2. Return user-friendly error messages (no stack traces)
3. Log errors with structured logging
4. Maintain application state consistency on errors
5. Provide clear feedback to users about what went wrong

## Performance Requirements

- File upload callback: Complete in < 5 seconds for 1,000 rows
- Single filter callback: Complete in < 1 second
- Multiple filter callback: Complete in < 2 seconds for up to 5 filters
- Export callback: Complete in < 3 seconds for 1,000 rows

