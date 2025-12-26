# Flexible Table - Advanced Table Filtering Web Application

A browser-based web application that allows users to upload table data files (CSV, Excel, JSON) and perform advanced filtering operations similar to Excel's advanced filter functionality.

## Features

- **File Upload**: Support for CSV, Excel (.xlsx, .xls), and JSON file formats
- **Interactive Table Display**: View tabular data in a browser with virtual scrolling for large datasets
- **Advanced Filtering**: 
  - Single column filtering (text, numeric, date)
  - **Multi-select Value Selection**: Select multiple values from a list for "Equals" operator (similar to Excel filter)
  - Multiple column filtering with AND/OR logic
  - Real-time filter updates
  - Clear individual or all filters
- **Data Export**: Export filtered results to CSV with a timestamped filename
- **Column Management**: Show/hide specific columns, multi-column sorting
- **Performance**: Virtual scrolling for large datasets (handles 10,000+ rows smoothly)

## Advanced Filtering Features

| Data Type | Operators | Multi-select Support |
|-----------|-----------|----------------------|
| **Text**  | Equals, Contains, Starts with, Ends with | Yes (for Equals) |
| **Numeric**| Equals, Greater than, Less than, Between | Yes (for Equals) |
| **Date**  | Equals, Before, After, Between | Yes (for Equals) |

### How to use Multi-select
When you select the **Equals** operator for any column, the Value input will automatically transform into a dropdown list containing all unique values present in that column. You can select one or more values to filter the data.

## Requirements

- Python 3.11.8
- See `requirements.txt` for dependencies

## Installation

1. Clone the repository:
```bash
cd /path/to/flexible_table
```

2. Create a virtual environment (recommended):
```bash
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Verify installation:
```bash
python -c "import dash; import dash_table; import pandas; print('All dependencies installed successfully')"
```

## Running the Application

1. Start the application:
```bash
python3.11 src/app.py
```

2. Open your web browser and navigate to:
```
http://127.0.0.1:8050
```

## Usage

See [quickstart guide](specs/001-table-filter-app/quickstart.md) for detailed usage instructions.

## Development

### Running Tests

```bash
# Running via 'python -m pytest' automatically adds the project root to PYTHONPATH
python3.11 -m pytest tests/
```

### Code Quality

- **Linting**: `flake8 src/ tests/`
- **Formatting**: `black src/ tests/`
- **Type Checking**: `mypy src/`

## Project Structure

```
src/
├── app.py                 # Main Dash application entry point
├── components/            # Dash UI components
├── lib/                   # Core business logic (library-first)
└── utils/                 # Utility functions

tests/
├── unit/                  # Unit tests
├── integration/           # Integration tests
└── fixtures/              # Test data files
```

## License

MIT License

