# Quickstart Guide: Advanced Table Filtering Web Application

**Date**: 2025-01-27  
**Feature**: Advanced Table Filtering Web Application  
**Branch**: 001-table-filter-app

## Overview

This guide provides step-by-step instructions for getting started with the Advanced Table Filtering Web Application. The application allows users to upload table data files and perform advanced filtering operations in a browser-based interface.

## Prerequisites

- Python 3.11.8 installed
- pip package manager
- Web browser (Chrome, Firefox, Safari, or Edge - latest 2 versions)

## Installation

### 1. Clone Repository and Navigate to Project

```bash
cd /path/to/flexible_table
```

### 2. Create Virtual Environment (Recommended)

```bash
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

Create a `requirements.txt` file with version-pinned dependencies:

```bash
cat > requirements.txt << EOF
dash>=2.14.0
pandas>=2.0.0
openpyxl>=3.1.0
pytest>=7.4.0
EOF
```

Then install:

```bash
pip install -r requirements.txt
```

**Note**: `dash_table` is included in the `dash` package (imported as `dash_table`), so no separate package installation is needed.

### 4. Verify Installation

```bash
python -c "import dash; import dash_table; import pandas; print('All dependencies installed successfully')"
```

## Running the Application

### 1. Start the Application

```bash
python src/app.py
```

### 2. Access the Application

Open your web browser and navigate to:
```
http://localhost:8050
```

The application should now be running and displaying the file upload interface.

## Basic Usage

### Step 1: Upload a File

1. Click the "Upload File" area or drag and drop a file
2. Supported formats:
   - CSV files (.csv)
   - Excel files (.xlsx, .xls)
   - JSON files (.json) - array of objects format
3. Wait for the file to be processed (typically < 5 seconds for files up to 1,000 rows)
4. The table data will appear in the main display area

### Step 2: Apply Basic Filter

1. Select a column from the "Column" dropdown
2. Choose a filter operator:
   - For text columns: equals, contains, starts with, ends with
   - For numeric columns: equals, greater than, less than, between
   - For date columns: equals, before, after, between
3. Enter or select the filter value:
   - **For "equals" operator**: A multi-select dropdown will appear. Select one or more values from the list of unique values found in that column.
   - **For other operators**: Enter the value in the text input field.
   - **For "between" operator**: Enter the minimum and maximum values in the two input fields.
4. Click "Apply Filters" or "Add Filter" (to build a set of filters).
5. The table will update to show only matching rows.
6. The row count will update to show filtered vs. total rows.

### Step 3: Apply Multiple Filters

1. Apply additional filters to other columns using the same process
2. Select the logic operator (AND/OR) to combine filters:
   - **AND**: Rows must match ALL filter conditions
   - **OR**: Rows must match ANY filter condition
3. Click "Apply Filters" to see combined results
4. The table will update to show rows matching the combined filter criteria

### Step 4: Clear Filters

- **Clear Single Filter**: Select the column from dropdown and click "Clear Filter"
- **Clear All Filters**: Click "Clear All Filters" to remove all filters and show original data

### Step 5: Export Filtered Results

1. Apply desired filters to your data
2. Click "Export to CSV" button
3. The filtered results will download as a CSV file

## Advanced Features

### Column Visibility

1. Use the column visibility checklist to show/hide columns
2. Hidden columns remain in the data but are not displayed
3. Useful for focusing on specific columns while filtering

### Sorting

1. Click on any column header to sort ascending
2. Click again to sort descending
3. Sorting works on filtered data

### Large Datasets

- For datasets with 1,000+ rows, virtual scrolling is automatically enabled
- The table will load rows as you scroll
- Filtering performance is optimized for datasets up to 10,000 rows

## File Format Requirements

### CSV Files
- First row should contain column headers
- UTF-8 encoding recommended (other encodings auto-detected)
- Maximum file size: 50MB

### Excel Files
- First sheet will be used
- First row should contain column headers
- Supports .xlsx and .xls formats
- Maximum file size: 50MB

### JSON Files
- Must be an array of objects format:
  ```json
  [
    {"column1": "value1", "column2": "value2"},
    {"column1": "value3", "column2": "value4"}
  ]
  ```
- Object keys become column headers
- Maximum file size: 50MB

## Troubleshooting

### File Upload Fails

**Problem**: File upload shows error message

**Solutions**:
- Check file format is supported (CSV, Excel, JSON)
- Verify file size is under 50MB
- Ensure file is not corrupted
- For CSV files, check encoding (try saving as UTF-8)

### Filter Not Working

**Problem**: Filter applied but no results shown

**Solutions**:
- Verify filter value matches data type (text vs. number vs. date)
- Check for typos in filter value
- Try clearing filters and reapplying
- Verify column data type is correct (check column type indicator)

### Performance Issues

**Problem**: Application is slow or freezes

**Solutions**:
- Reduce dataset size (aim for < 10,000 rows)
- Apply filters to reduce visible rows
- Close other browser tabs to free memory
- Use column visibility to hide unnecessary columns

### Table Not Displaying

**Problem**: File uploaded but table is empty

**Solutions**:
- Check browser console for errors (F12)
- Verify file has data rows (not just headers)
- Try uploading a different file format
- Check that file parsing completed successfully (check status message)

## Example Workflows

### Workflow 1: Find Active Records

1. Upload CSV file with "Status" column
2. Filter "Status" column with operator "equals" and value "Active"
3. View filtered results
4. Export to CSV if needed

### Workflow 2: Find High-Value Transactions

1. Upload Excel file with "Amount" column
2. Filter "Amount" column with operator "greater than" and value "1000"
3. Apply additional filter on "Date" column (e.g., "after" specific date)
4. Use AND logic to combine filters
5. View combined results

### Workflow 3: Search Text Across Multiple Columns

1. Upload JSON file
2. Apply "contains" filter to "Name" column with value "John"
3. Apply "contains" filter to "Description" column with value "urgent"
4. Use OR logic to find rows matching either condition
5. View results

## Next Steps

After completing this quickstart:

1. Review the [Feature Specification](./spec.md) for detailed requirements
2. Check the [Implementation Plan](./plan.md) for technical details
3. Explore the [Data Model](./data-model.md) to understand data structures
4. Review [Callback Contracts](./contracts/callbacks.md) for API details

## Getting Help

- Check application logs for detailed error messages
- Review browser console (F12) for client-side errors
- Refer to Dash documentation: https://dash.plotly.com/
- Refer to dash_table documentation: https://dash.plotly.com/datatable

