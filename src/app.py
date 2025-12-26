"""Main Dash application for Advanced Table Filtering Web Application."""

import time
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
import dash
from dash import Dash, dcc, html, Input, Output, State, callback, ALL, ctx

# Add parent directory to path for imports when running as script
# This allows both direct execution (python src/app.py) and module execution (python -m src.app)
_script_dir = Path(__file__).parent
_project_root = _script_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.components.upload_component import create_upload_component
from src.components.table_component import create_table_component
from src.components.filter_ui import create_filter_ui, get_operators_for_type
from src.lib.data_parser import parse_file
from src.lib.data_processor import prepare_table_data, convert_to_json_format
from src.lib.filter_engine import apply_single_filter, apply_multiple_filters, validate_filter_operator
from src.utils.validators import validate_file_upload
from src.utils.error_handlers import handle_file_upload_error, FileUploadError
from src.utils.logging_config import setup_logging, log_file_upload, log_filter_operation
from src.utils.formatters import format_row_count

# Initialize logger
logger = setup_logging()

# Initialize Dash app
app = Dash(__name__)
app.title = "Flexible Table - Advanced Table Filtering"

# App layout
app.layout = html.Div([
    html.H1("Flexible Table - Advanced Table Filtering", style={'textAlign': 'center', 'margin': '20px'}),
    
    # File upload section
    html.Div([
        create_upload_component("upload-data"),
        html.Div(id="upload-status", style={'margin': '10px', 'padding': '10px'})
    ]),
    
    # Row count display
    html.Div(id="row-count-display", style={'margin': '10px', 'fontWeight': 'bold'}),
    
    # Filter UI section (initially hidden until data is loaded)
    html.Div(id="filter-ui-container", style={'display': 'none'}),
    
    # Table display
    html.Div(id="table-container"),
    
    # Store components for state management
    dcc.Store(id="table-data-store", data={}),  # Store table data
    dcc.Store(id="filter-set-store", data={'conditions': [], 'logic_operator': 'AND'}),  # Store filter set
    dcc.Store(id="upload-status-store", data=''),  # Store upload status
    dcc.Store(id="visible-columns-store", data=[]),  # Store visible columns selection
    dcc.Download(id="download-csv"),
])


@callback(
    [
        Output("visible-columns-store", "data", allow_duplicate=True),
        Output("table-container", "children", allow_duplicate=True),
    ],
    [Input("filter-visible-columns", "value")],
    [
        State("table-data-store", "data"),
        State("filter-set-store", "data"),
    ],
    prevent_initial_call=True,
)
def update_visible_columns(
    visible_columns: Optional[list[str]],
    table_data: Dict,
    current_filter_set: Optional[Dict],
) -> tuple:
    """Update visible columns and re-render the table (keeping current filters)."""
    _t0 = time.time()
    if not table_data or "dataframe_json" not in table_data:
        return dash.no_update, dash.no_update

    # Normalize selection
    all_columns: list[str] = list(table_data.get("column_names", []))
    if not visible_columns:
        visible_columns_effective = all_columns
    else:
        visible_set = set(visible_columns)
        visible_columns_effective = [c for c in all_columns if c in visible_set]

    # Reconstruct df
    df = pd.DataFrame.from_dict(table_data["dataframe_json"])

    # Reapply filters if present
    filtered_df = _apply_filter_set_to_df(df, current_filter_set, table_data.get("column_types", {}))

    filtered_json = convert_to_json_format(filtered_df)
    table_columns = _select_table_columns(all_columns, visible_columns_effective)
    table_component = create_table_component(
        component_id="data-table",
        data=filtered_json,
        columns=table_columns,
        enable_virtual_scrolling=len(filtered_df) > 1000,
        enable_sorting=True,
    )
    log_filter_operation(
        logger,
        operation="visible_columns",
        filter_count=len(current_filter_set.get("conditions", [])) if current_filter_set else 0,
        result_count=len(filtered_df),
        duration=time.time() - _t0,
    )
    return visible_columns_effective, _wrap_table_with_empty_state(table_component, len(filtered_df))


@callback(
    Output("download-csv", "data"),
    [Input("filter-export-btn", "n_clicks")],
    [
        State("table-data-store", "data"),
        State("filter-set-store", "data"),
        State("visible-columns-store", "data"),
    ],
    prevent_initial_call=True,
)
def export_filtered_csv(
    n_clicks: int,
    table_data: Dict,
    current_filter_set: Optional[Dict],
    visible_columns: list[str],
):
    """Export current (filtered) data to CSV."""
    _t0 = time.time()
    if not n_clicks:
        return dash.no_update
    if not table_data or "dataframe_json" not in table_data:
        return dash.no_update

    df = pd.DataFrame.from_dict(table_data["dataframe_json"])

    # Reapply filters if present
    filtered_df = _apply_filter_set_to_df(df, current_filter_set, table_data.get("column_types", {}))

    if visible_columns:
        # Keep original column order
        keep_cols = [c for c in table_data.get("column_names", []) if c in set(visible_columns)]
        if keep_cols:
            filtered_df = filtered_df.loc[:, keep_cols]

    filename = "filtered_data.csv"
    log_filter_operation(
        logger,
        operation="export_csv",
        filter_count=len(current_filter_set.get("conditions", [])) if current_filter_set else 0,
        result_count=len(filtered_df),
        duration=time.time() - _t0,
    )
    return dcc.send_data_frame(filtered_df.to_csv, filename, index=False)


@callback(
    [
        Output("table-data-store", "data"),
        Output("upload-status-store", "data"),
        Output("table-container", "children"),
        Output("row-count-display", "children"),
        Output("upload-status", "children"),
        Output("filter-ui-container", "children"),
        Output("filter-ui-container", "style"),
        Output("visible-columns-store", "data"),
    ],
    [Input("upload-data", "contents")],
    [State("upload-data", "filename")]
)
def upload_file(upload_contents: Optional[str], upload_filename: Optional[str]) -> tuple:
    """
    Handle file upload, parse file content, and initialize table data.
    
    Callback contract: upload_file (see contracts/callbacks.md)
    """
    start_time = time.time()
    
    # Default empty response
    empty_response = (
        {},  # table_data
        '',  # upload_status
        html.Div("No data loaded. Please upload a file."),  # table_container
        '',  # row_count_display
        '',  # upload_status
        None,  # filter_ui_container
        {'display': 'none'},  # filter_ui_style
        [],  # visible_columns
    )
    
    # Check if file was uploaded
    if upload_contents is None or upload_filename is None:
        return empty_response
    
    try:
        # Validate file
        is_valid, validation_error = validate_file_upload(upload_filename, upload_contents)
        if not is_valid:
            error_msg = f"Validation error: {validation_error}"
            logger.error(error_msg)
            return (
                {},  # table_data
                f'error: {validation_error}',  # upload_status
                html.Div(),  # table_container (empty)
                f'Error: {validation_error}',  # row_count_display
                html.Div(error_msg, style={'color': 'red'}),  # upload_status
                None,  # filter_ui_container
                {'display': 'none'},  # filter_ui_style
                [],  # visible_columns
            )
        
        # Parse file
        df, file_format = parse_file(upload_contents, upload_filename)
        
        # Prepare table data structure
        table_data = prepare_table_data(df, file_format, upload_filename)
        
        # Create table component
        table_columns = _select_table_columns(list(table_data['column_names']), list(table_data['column_names']))
        table_component = create_table_component(
            component_id="data-table",
            data=table_data['dataframe_json'],
            columns=table_columns,
            enable_virtual_scrolling=table_data['row_count'] > 1000,
            enable_sorting=True
        )
        
        # Log successful upload
        duration = time.time() - start_time
        # Calculate actual file size from base64 content
        # Base64 encoding increases size by ~33%, so actual size = base64_length * 3 / 4
        base64_length = len(upload_contents.split(',')[-1]) if ',' in upload_contents else len(upload_contents)
        actual_file_size = (base64_length * 3) // 4
        log_file_upload(
            logger,
            upload_filename,
            actual_file_size,
            'success',
            duration
        )
        log_filter_operation(
            logger,
            operation="upload_parse",
            filter_count=0,
            result_count=int(table_data.get("row_count", 0)),
            duration=duration,
        )
        
        # Format row count
        row_count_display = format_row_count(table_data['row_count'])
        
        # Create filter UI component
        filter_ui = create_filter_ui(
            component_id_prefix="filter",
            column_names=table_data['column_names'],
            column_types=table_data['column_types']
        )
        
        return (
            table_data,  # table_data
            'success',  # upload_status
            html.Div([table_component], style={'margin': '20px'}),  # table_container
            row_count_display,  # row_count_display
            html.Div(f"File '{upload_filename}' uploaded successfully!", style={'color': 'green'}),  # upload_status
            filter_ui,  # filter_ui_container
            {'display': 'block'},  # filter_ui_style
            list(table_data['column_names']),  # visible_columns
        )
    
    except FileUploadError as e:
        error_msg = str(e)
        logger.error(f"File upload error: {error_msg}")
        return (
            {},  # table_data
            f'error: {error_msg}',  # upload_status
            html.Div(),  # table_container (empty)
            f'Error: {error_msg}',  # row_count_display
            html.Div(error_msg, style={'color': 'red'}),  # upload_status
            None,  # filter_ui_container
            {'display': 'none'},  # filter_ui_style
            [],  # visible_columns
        )
    
    except Exception as e:
        error_msg = handle_file_upload_error(e, upload_filename)
        logger.error(f"Unexpected error during file upload: {str(e)}", exc_info=True)
        return (
            {},  # table_data
            f'error: {error_msg}',  # upload_status
            html.Div(),  # table_container (empty)
            f'Error: {error_msg}',  # row_count_display
            html.Div(error_msg, style={'color': 'red'}),  # upload_status
            None,  # filter_ui_container
            {'display': 'none'},  # filter_ui_style
            [],  # visible_columns
        )


# Filter callbacks
@callback(
    [
        Output("filter-set-store", "data", allow_duplicate=True),
        Output("filter-conditions-list", "children")
    ],
    [Input("filter-logic", "value")],
    [State("filter-set-store", "data")],
    prevent_initial_call=True
)
def update_filter_logic(logic_operator: Optional[str], current_filter_set: Optional[Dict]) -> tuple:
    """
    Update logic operator in filter set when user changes AND/OR selection.
    Also update the conditions list display.
    """
    if not current_filter_set:
        current_filter_set = {'conditions': [], 'logic_operator': 'AND'}
    
    if logic_operator:
        current_filter_set['logic_operator'] = logic_operator
    else:
        current_filter_set['logic_operator'] = current_filter_set.get('logic_operator', 'AND')
    
    # Generate conditions list display
    conditions_list = _generate_conditions_list(current_filter_set.get('conditions', []))
    
    return current_filter_set, conditions_list


def _generate_conditions_list(conditions: list) -> list:
    """
    Generate HTML list of filter conditions for display.
    
    Args:
        conditions: List of filter condition dictionaries
    
    Returns:
        List of HTML components
    """
    if not conditions:
        return [html.Div("No filters applied.", style={'color': '#666', 'fontStyle': 'italic'})]
    
    condition_items = []
    for i, cond in enumerate(conditions):
        column_name = cond.get('column_name', '')
        operator = cond.get('operator', '')
        value = cond.get('value', '')
        
        # Format operator for display
        operator_display = {
            'equals': '=',
            'contains': 'contains',
            'starts_with': 'starts with',
            'ends_with': 'ends with',
            'greater_than': '>',
            'less_than': '<',
            'between': 'between',
            'before': 'before',
            'after': 'after'
        }.get(operator, operator)
        
        # Format value for display
        if isinstance(value, (list, tuple)):
            if operator == 'between' and len(value) == 2:
                value_display = f"{value[0]} and {value[1]}"
            else:
                value_display = f"[{', '.join(map(str, value))}]"
        else:
            value_display = str(value)

        condition_items.append(
            html.Div([
                html.Span(f"{i+1}. {column_name} {operator_display} {value_display}", 
                         style={'marginRight': '10px'}),
                html.Button(
                    "×",
                    id={"type": "remove-filter", "index": i},
                    n_clicks=0,
                    style={
                        'backgroundColor': '#dc3545',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '3px',
                        'cursor': 'pointer',
                        'padding': '2px 8px',
                        'fontSize': '14px'
                    }
                )
            ], style={
                'margin': '5px 0',
                'padding': '5px',
                'backgroundColor': '#f0f0f0',
                'borderRadius': '3px',
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center'
            })
        )
    
    return condition_items


def _no_results_banner(message: str = "No results match the current filter criteria.") -> html.Div:
    """Create a clear 'no results' banner to avoid confusing empty table states."""
    return html.Div(
        message,
        style={
            "margin": "10px 0",
            "padding": "10px 12px",
            "border": "1px solid #f5c2c7",
            "backgroundColor": "#f8d7da",
            "color": "#842029",
            "borderRadius": "6px",
            "fontWeight": "bold",
        },
    )


def _wrap_table_with_empty_state(table_component: Any, filtered_rows: int) -> html.Div:
    """Wrap a table with an empty-state banner when filtered result is empty."""
    children = []
    if filtered_rows == 0:
        children.append(_no_results_banner("No results match the current filter(s)."))
    children.append(table_component)
    return html.Div(children, style={"margin": "20px"})


def _apply_filter_set_to_df(df: pd.DataFrame, current_filter_set: Optional[Dict], column_types: Dict) -> pd.DataFrame:
    """
    Helper to apply a filter set to a DataFrame.
    Unified logic used across multiple callbacks.
    """
    if not current_filter_set or not current_filter_set.get("conditions"):
        return df

    conditions = current_filter_set.get("conditions", [])
    logic = current_filter_set.get("logic_operator", "AND")

    filter_conditions = []
    for cond in conditions:
        col = cond.get("column_name")
        op = cond.get("operator")
        val = cond.get("value")
        dtype = cond.get("data_type") or column_types.get(col, "text")
        if col and op:
            if dtype == "numeric":
                try:
                    if isinstance(val, list):
                        val = [float(v) for v in val]
                    elif isinstance(val, tuple):
                        val = (float(val[0]), float(val[1]))
                    else:
                        val = float(val)
                except Exception:
                    pass
            elif dtype == "date":
                try:
                    if isinstance(val, list):
                        val = [pd.to_datetime(v) for v in val]
                    elif isinstance(val, tuple):
                        val = (pd.to_datetime(val[0]), pd.to_datetime(val[1]))
                    else:
                        val = pd.to_datetime(val)
                except Exception:
                    pass
            filter_conditions.append(
                {"column_name": col, "operator": op, "value": val, "data_type": dtype}
            )
            
    if not filter_conditions:
        return df
        
    return apply_multiple_filters(df, filter_conditions, logic_operator=str(logic))


def _select_table_columns(all_columns: list[str], visible_columns: Optional[list[str]]) -> list[dict]:
    """Build DataTable columns list respecting visible column selection."""
    if not visible_columns:
        return [{"name": col, "id": col} for col in all_columns]
    visible_set = set(visible_columns)
    selected = [col for col in all_columns if col in visible_set]
    return [{"name": col, "id": col} for col in selected]


@callback(
    [
        Output("filter-value", "style"),
        Output("filter-value", "disabled"),
        Output("filter-value-multi", "style"),
        Output("filter-value-multi", "options"),
        Output("filter-value-multi", "value"),
        Output("filter-value2-container", "style"),
        Output("filter-value2", "disabled"),
    ],
    [Input("filter-column", "value"), Input("filter-operator", "value")],
    [State("table-data-store", "data")]
)
def update_value_input_type(selected_column: Optional[str], selected_operator: Optional[str], table_data: Dict) -> tuple:
    """Toggle between text input and multi-select dropdown based on operator."""
    default_input_style = {'width': '100%', 'display': 'inline-block'}
    hidden_style = {'display': 'none'}
    
    if not selected_column or not table_data or 'dataframe_json' not in table_data:
        return default_input_style, True, hidden_style, [], None, hidden_style, True

    if not selected_operator:
        return default_input_style, True, hidden_style, [], None, hidden_style, True

    # Check for 'between' operator
    if selected_operator == 'between':
        return default_input_style, False, hidden_style, [], None, {'display': 'inline-block'}, False

    # Check for 'equals' operator
    if selected_operator == 'equals':
        try:
            df = pd.DataFrame.from_dict(table_data['dataframe_json'])
            if selected_column in df.columns:
                unique_values = sorted(df[selected_column].dropna().unique().tolist())
                options = [{'label': str(v), 'value': v} for v in unique_values]
                return hidden_style, True, default_input_style, options, [], hidden_style, True
        except Exception as e:
            logger.error(f"Error populating unique values: {e}")
    
    # Default: show text input
    return default_input_style, False, hidden_style, [], None, hidden_style, True


@callback(
    [
        Output("filter-operator", "options"),
        Output("filter-operator", "disabled"),
        Output("filter-apply-btn", "disabled")
    ],
    [Input("filter-column", "value")],
    [State("table-data-store", "data")]
)
def update_filter_controls(selected_column: Optional[str], table_data: Dict) -> tuple:
    """
    Update filter operator dropdown and enable/disable controls based on selected column.
    
    Callback contract: update_filter_controls (see contracts/callbacks.md)
    """
    if not selected_column or not table_data or 'column_types' not in table_data:
        return (
            [],  # operator_options
            True,  # operator_disabled
            True  # apply_btn_disabled
        )
    
    # Get data type for selected column
    column_types = table_data.get('column_types', {})
    data_type = column_types.get(selected_column, 'text')
    
    # Get operators for this data type
    operators = get_operators_for_type(data_type)
    
    return (
        operators,  # operator_options
        False,  # operator_disabled
        False  # apply_btn_disabled
    )


@callback(
    [
        Output("filter-set-store", "data", allow_duplicate=True),  # Changed to allow_duplicate=True
        Output("table-container", "children", allow_duplicate=True),
        Output("row-count-display", "children", allow_duplicate=True),
        Output("filter-status", "children"),
        Output("filter-conditions-list", "children", allow_duplicate=True)
    ],
    [Input("filter-apply-btn", "n_clicks")],
    [
        State("filter-column", "value"),
        State("filter-operator", "value"),
        State("filter-value", "value"),
        State("filter-value-multi", "value"),
        State("filter-value2", "value"),
        State("filter-logic", "value"),
        State("table-data-store", "data"),
        State("filter-set-store", "data"),
        State("visible-columns-store", "data"),
    ],
    prevent_initial_call=True
)
def apply_column_filter(
    n_clicks: int,
    column_name: Optional[str],
    operator: Optional[str],
    filter_value: Optional[str],
    filter_value_multi: Optional[list],
    filter_value2: Optional[str],
    logic_operator: Optional[str],
    table_data: Dict,
    current_filter_set: Optional[Dict],
    visible_columns: list[str],
) -> tuple:
    """
    Apply single column filter and update table display.
    
    Callback contract: apply_column_filter (see contracts/callbacks.md)
    """
    # Initialize filter set if None
    if not current_filter_set:
        current_filter_set = {'conditions': [], 'logic_operator': 'AND'}
    
    # Check if table data is available
    if not table_data or 'dataframe_json' not in table_data:
        return (
            current_filter_set,  # filter_set
            html.Div("No data loaded. Please upload a file first."),  # table_container
            '',  # row_count_display
            html.Div("Error: No data loaded.", style={'color': 'red'}),  # filter_status
            []  # conditions_list
        )
    
    # Decide which filter value to use
    actual_value = filter_value
    if operator == 'equals' and filter_value_multi is not None:
        actual_value = filter_value_multi
    elif operator == 'between':
        actual_value = (filter_value, filter_value2)

    # Validate inputs
    if not column_name or not operator or actual_value is None or (isinstance(actual_value, list) and not actual_value):
        return (
            current_filter_set,  # filter_set
            html.Div(),  # table_container (keep current)
            '',  # row_count_display (keep current)
            html.Div("Please select column, operator, and enter/select a value.", style={'color': 'orange'}),  # filter_status
            _generate_conditions_list(current_filter_set.get('conditions', []))  # conditions_list
        )
    
    _t0 = time.time()
    try:
        # Reconstruct DataFrame from stored JSON
        df = pd.DataFrame.from_dict(table_data['dataframe_json'])
        
        # Get column data type
        column_types = table_data.get('column_types', {})
        data_type = column_types.get(column_name, 'text')
        
        # Validate operator for data type
        if not validate_filter_operator(operator, data_type):
            return (
                current_filter_set,  # filter_set
                html.Div(),  # table_container (keep current)
                '',  # row_count_display (keep current)
                html.Div(f"Invalid operator '{operator}' for {data_type} column.", style={'color': 'red'}),  # filter_status
                _generate_conditions_list(current_filter_set.get('conditions', []))  # conditions_list
            )
        
        # Convert filter value based on data type
        filter_value_typed: Any = actual_value
        if data_type == 'numeric':
            try:
                if isinstance(actual_value, list):
                    filter_value_typed = [float(v) for v in actual_value if v is not None]
                elif isinstance(actual_value, tuple):
                    val1 = float(actual_value[0]) if actual_value[0] is not None else 0.0
                    val2 = float(actual_value[1]) if actual_value[1] is not None else 0.0
                    filter_value_typed = (val1, val2)
                elif actual_value is not None:
                    filter_value_typed = float(actual_value)
            except (ValueError, TypeError):
                return (
                    current_filter_set,  # filter_set
                    html.Div(),  # table_container (keep current)
                    '',  # row_count_display (keep current)
                    html.Div("Invalid numeric value.", style={'color': 'red'}),  # filter_status
                    _generate_conditions_list(current_filter_set.get('conditions', []))  # conditions_list
                )
        elif data_type == 'date':
            try:
                if isinstance(actual_value, list):
                    filter_value_typed = [pd.to_datetime(v) for v in actual_value if v is not None]
                elif isinstance(actual_value, tuple):
                    val1 = pd.to_datetime(actual_value[0]) if actual_value[0] is not None else pd.Timestamp.now()
                    val2 = pd.to_datetime(actual_value[1]) if actual_value[1] is not None else pd.Timestamp.now()
                    filter_value_typed = (val1, val2)
                elif actual_value is not None:
                    filter_value_typed = pd.to_datetime(actual_value)
            except (ValueError, TypeError):
                return (
                    current_filter_set,  # filter_set
                    html.Div(),  # table_container (keep current)
                    '',  # row_count_display (keep current)
                    html.Div("Invalid date format.", style={'color': 'red'}),  # filter_status
                    _generate_conditions_list(current_filter_set.get('conditions', []))  # conditions_list
                )
        
        # Get logic operator from input or filter set (default to AND)
        logic_operator_effective = (
            logic_operator if logic_operator in ("AND", "OR") else current_filter_set.get('logic_operator', 'AND')
        )
        if logic_operator_effective not in ("AND", "OR"):
            logic_operator_effective = "AND"
        current_filter_set['logic_operator'] = logic_operator_effective
        
        # Create FilterCondition
        filter_condition = {
            'column_name': column_name,
            'operator': operator,
            'value': actual_value,
            'data_type': data_type,
            'is_active': True
        }
        
        # Update filter set (replace existing condition for same column or add new)
        conditions = current_filter_set.get('conditions', [])
        conditions = [c for c in conditions if c.get('column_name') != column_name]
        conditions.append(filter_condition)
        current_filter_set['conditions'] = conditions
        
        # Apply filters using unified logic
        filtered_df = _apply_filter_set_to_df(df, current_filter_set, table_data.get('column_types', {}))
        
        filter_set = {
            'conditions': conditions,
            'logic_operator': logic_operator_effective,
            'result_count': len(filtered_df)
        }
        
        # Convert filtered DataFrame to JSON format
        filtered_json = convert_to_json_format(filtered_df)
        
        # Create table component with filtered data
        table_columns = _select_table_columns(list(table_data['column_names']), visible_columns)
        table_component = create_table_component(
            component_id="data-table",
            data=filtered_json,
            columns=table_columns,
            enable_virtual_scrolling=len(filtered_df) > 1000,
            enable_sorting=True
        )
        
        total_rows = table_data['row_count']
        filtered_rows = len(filtered_df)
        row_count_display = format_row_count(total_rows, filtered_rows)
        
        if filtered_rows == 0:
            status_msg = "No results match the current filter(s)."
            status_color = "orange"
        else:
            status_color = "green"
            if len(conditions) > 1:
                status_msg = f"Applied {len(conditions)} filters with {logic_operator_effective} logic ({filtered_rows} rows)"
            else:
                status_msg = f"Filter applied: {column_name} {operator} {actual_value} ({filtered_rows} rows)"
        
        conditions_list = _generate_conditions_list(filter_set['conditions'])
        table_container = _wrap_table_with_empty_state(table_component, filtered_rows)
        
        return (
            filter_set,
            table_container,
            row_count_display,
            html.Div(status_msg, style={'color': status_color}),
            conditions_list
        )
    
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error applying filter: {error_msg}", exc_info=True)
        return (
            current_filter_set,  # filter_set
            html.Div(),  # table_container (keep current)
            '',  # row_count_display (keep current)
            html.Div(f"Error applying filter: {error_msg}", style={'color': 'red'}),  # filter_status
            _generate_conditions_list(current_filter_set.get('conditions', [])) if current_filter_set else []  # conditions_list
        )
    finally:
        try:
            log_filter_operation(
                logger,
                operation="apply_filters",
                filter_count=len(current_filter_set.get("conditions", [])) if current_filter_set else 0,
                result_count=int(current_filter_set.get("result_count", 0)) if current_filter_set else 0,
                duration=time.time() - _t0,
            )
        except Exception:
            # Never let logging break UI callbacks
            pass


@callback(
    [
        Output("filter-set-store", "data", allow_duplicate=True),
        Output("table-container", "children", allow_duplicate=True),
        Output("row-count-display", "children", allow_duplicate=True),
        Output("filter-status", "children", allow_duplicate=True),
        Output("filter-conditions-list", "children", allow_duplicate=True),
        Output("filter-column", "value", allow_duplicate=True),
        Output("filter-operator", "value", allow_duplicate=True),
        Output("filter-value", "value", allow_duplicate=True),
        Output("filter-value-multi", "value", allow_duplicate=True),
        Output("filter-value2", "value", allow_duplicate=True),
    ],
    [Input("filter-clear-btn", "n_clicks")],
    [State("table-data-store", "data"), State("visible-columns-store", "data")],
    prevent_initial_call=True
)
def clear_filter(n_clicks: int, table_data: Dict, visible_columns: list[str]) -> tuple:
    """
    Clear all filters and restore original table data.
    
    Callback contract: clear_filter (see contracts/callbacks.md)
    """
    # Check if table data is available
    if not table_data or 'dataframe_json' not in table_data:
        return (
            {'conditions': [], 'logic_operator': 'AND'},  # filter_set
            html.Div("No data loaded."),  # table_container
            '',  # row_count_display
            html.Div("", style={'color': 'red'}),  # filter_status
            [],  # conditions_list
            None,  # filter_column
            None,  # filter_operator
            '',    # filter_value
            [],    # filter_value_multi
            ''     # filter_value2
        )
    
    _t0 = time.time()
    try:
        # Reconstruct original DataFrame
        df = pd.DataFrame.from_dict(table_data['dataframe_json'])
        
        # Convert to JSON format
        original_json = convert_to_json_format(df)
        
        # Create table component with original data (respect visible columns)
        table_columns = _select_table_columns(list(table_data['column_names']), visible_columns)
        table_component = create_table_component(
            component_id="data-table",
            data=original_json,
            columns=table_columns,
            enable_virtual_scrolling=len(df) > 1000,
            enable_sorting=True
        )
        
        # Update row count display
        total_rows = table_data['row_count']
        row_count_display = format_row_count(total_rows)
        
        log_filter_operation(logger, 'clear', 0, total_rows, time.time() - _t0)
        
        return (
            {'conditions': [], 'logic_operator': 'AND'},  # filter_set
            html.Div([table_component], style={'margin': '20px'}),  # table_container
            row_count_display,  # row_count_display
            html.Div("All filters cleared.", style={'color': 'green'}),  # filter_status
            _generate_conditions_list([]),  # conditions_list
            None,  # filter_column
            None,  # filter_operator
            '',    # filter_value
            [],    # filter_value_multi
            ''     # filter_value2
        )
    
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error clearing filter: {error_msg}", exc_info=True)
        return (
            {'conditions': [], 'logic_operator': 'AND'},  # filter_set
            html.Div(),  # table_container (keep current)
            '',  # row_count_display (keep current)
            html.Div(f"Error clearing filter: {error_msg}", style={'color': 'red'}),  # filter_status
            _generate_conditions_list([]),  # conditions_list
            None,  # filter_column
            None,  # filter_operator
            '',    # filter_value
            [],    # filter_value_multi
            ''     # filter_value2
        )
    finally:
        try:
            log_filter_operation(
                logger,
                operation="clear_filters",
                filter_count=0,
                result_count=int(table_data.get("row_count", 0)) if table_data else 0,
                duration=time.time() - _t0,
            )
        except Exception:
            pass


@callback(
    [
        Output("filter-set-store", "data", allow_duplicate=True),
        Output("filter-conditions-list", "children", allow_duplicate=True),
        Output("filter-column", "value", allow_duplicate=True),
        Output("filter-operator", "value", allow_duplicate=True),
        Output("filter-value", "value", allow_duplicate=True),
        Output("filter-value-multi", "value", allow_duplicate=True),
        Output("filter-value2", "value", allow_duplicate=True),
        Output("filter-status", "children", allow_duplicate=True)
    ],
    [Input("filter-add-btn", "n_clicks")],
    [
        State("filter-column", "value"),
        State("filter-operator", "value"),
        State("filter-value", "value"),
        State("filter-value-multi", "value"),
        State("filter-value2", "value"),
        State("table-data-store", "data"),
        State("filter-set-store", "data")
    ],
    prevent_initial_call=True
)
def add_filter_condition(
    n_clicks: int,
    column_name: Optional[str],
    operator: Optional[str],
    filter_value: Optional[str],
    filter_value_multi: Optional[list],
    filter_value2: Optional[str],
    table_data: Dict,
    current_filter_set: Optional[Dict]
) -> tuple:
    """
    Add a filter condition to the filter set without applying it.
    This allows users to build up multiple filter conditions before applying them.
    """
    # Initialize filter set if None
    if not current_filter_set:
        current_filter_set = {'conditions': [], 'logic_operator': 'AND'}
    
    # Check if table data is available
    if not table_data or 'column_types' not in table_data:
        return (
            current_filter_set,  # filter_set
            _generate_conditions_list(current_filter_set.get('conditions', [])),  # conditions_list
            column_name,  # filter_column (keep current)
            operator,  # filter_operator (keep current)
            filter_value,  # filter_value (keep current)
            filter_value_multi, # filter_value_multi (keep current)
            filter_value2, # filter_value2 (keep current)
            html.Div("Error: No data loaded.", style={'color': 'red'})  # filter_status
        )
    
    # Decide which filter value to use
    actual_value = filter_value
    if operator == 'equals' and filter_value_multi is not None:
        actual_value = filter_value_multi
    elif operator == 'between':
        actual_value = (filter_value, filter_value2)

    # Validate inputs
    if not column_name or not operator or actual_value is None or (isinstance(actual_value, list) and not actual_value):
        return (
            current_filter_set,  # filter_set
            _generate_conditions_list(current_filter_set.get('conditions', [])),  # conditions_list
            column_name,  # filter_column (keep current)
            operator,  # filter_operator (keep current)
            filter_value,  # filter_value (keep current)
            filter_value_multi, # filter_value_multi (keep current)
            filter_value2, # filter_value2 (keep current)
            html.Div("Please select column, operator, and enter/select a value before adding.", style={'color': 'orange'})  # filter_status
        )
    
    try:
        # Get column data type
        column_types = table_data.get('column_types', {})
        data_type = column_types.get(column_name, 'text')
        
        # Validate operator for data type
        if not validate_filter_operator(operator, data_type):
            return (
                current_filter_set,  # filter_set
                _generate_conditions_list(current_filter_set.get('conditions', [])),  # conditions_list
                column_name,  # filter_column (keep current)
                operator,  # filter_operator (keep current)
                filter_value,  # filter_value (keep current)
                filter_value_multi, # filter_value_multi (keep current)
                filter_value2, # filter_value2 (keep current)
                html.Div(f"Invalid operator '{operator}' for {data_type} column.", style={'color': 'red'})  # filter_status
            )
        
        # Create FilterCondition
        filter_condition = {
            'column_name': column_name,
            'operator': operator,
            'value': actual_value,
            'data_type': data_type,
            'is_active': True
        }
        
        # Update filter set (replace existing condition for same column or add new)
        conditions = current_filter_set.get('conditions', [])
        # Remove existing condition for this column if any
        conditions = [c for c in conditions if c.get('column_name') != column_name]
        # Add new condition
        conditions.append(filter_condition)
        
        # Check maximum conditions limit
        MAX_CONDITIONS = 10
        if len(conditions) > MAX_CONDITIONS:
            # Remove the last added condition
            conditions.pop()
            return (
                current_filter_set,  # filter_set
                _generate_conditions_list(conditions),  # conditions_list
                column_name,  # filter_column (keep current)
                operator,  # filter_operator (keep current)
                filter_value,  # filter_value (keep current)
                filter_value_multi, # filter_value_multi (keep current)
                filter_value2, # filter_value2 (keep current)
                html.Div(f"Maximum {MAX_CONDITIONS} filter conditions allowed.", style={'color': 'red'})  # filter_status
            )
        
        filter_set = {
            'conditions': conditions,
            'logic_operator': current_filter_set.get('logic_operator', 'AND'),
            'result_count': 0  # Not applied yet
        }
        
        # Generate conditions list display
        conditions_list = _generate_conditions_list(filter_set['conditions'])
        
        return (
            filter_set,  # filter_set
            conditions_list,  # conditions_list
            None,  # filter_column (clear)
            None,  # filter_operator (clear)
            '',  # filter_value (clear)
            [],  # filter_value_multi (clear)
            '',  # filter_value2 (clear)
            html.Div(f"Filter condition added: {column_name} {operator} ({len(conditions)} total)", style={'color': 'green'})  # filter_status
        )
    
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error adding filter condition: {error_msg}", exc_info=True)
        return (
            current_filter_set,  # filter_set
            _generate_conditions_list(current_filter_set.get('conditions', [])),  # conditions_list
            column_name,  # filter_column (keep current)
            operator,  # filter_operator (keep current)
            filter_value,  # filter_value (keep current)
            html.Div(f"Error adding filter condition: {error_msg}", style={'color': 'red'})  # filter_status
        )


@callback(
    [
        Output("filter-set-store", "data", allow_duplicate=True),
        Output("filter-conditions-list", "children", allow_duplicate=True),
        Output("table-container", "children", allow_duplicate=True),
        Output("row-count-display", "children", allow_duplicate=True),
        Output("filter-status", "children", allow_duplicate=True)
    ],
    [Input({"type": "remove-filter", "index": ALL}, "n_clicks")],
    [
        State("filter-set-store", "data"),
        State("table-data-store", "data"),
        State("visible-columns-store", "data"),
    ],
    prevent_initial_call=True
)
def remove_filter_condition(
    n_clicks_list: list,
    current_filter_set: Optional[Dict],
    table_data: Dict,
    visible_columns: list[str],
) -> tuple:
    """
    Remove a filter condition from the filter set when the × button is clicked.
    """
    _t0 = time.time()
    # Initialize filter set if None
    if not current_filter_set:
        current_filter_set = {'conditions': [], 'logic_operator': 'AND'}
    
    # Check if any button was clicked
    if not any(n_clicks_list):
        # When pattern-matching inputs are dynamically created/removed,
        # this callback can fire even without an actual click.
        # Do NOT overwrite the table in that case.
        return (dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update)
    
    # Get the index of the button that was clicked
    triggered_id = ctx.triggered[0]['prop_id']
    if not triggered_id or 'remove-filter' not in triggered_id:
        return (dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update)
    
    # Parse the index from the triggered ID
    # Format: '{"type":"remove-filter","index":0}.n_clicks'
    import json
    try:
        id_str = triggered_id.split('.')[0]
        button_id = json.loads(id_str)
        index_to_remove = button_id['index']
    except (json.JSONDecodeError, KeyError, IndexError):
        logger.error(f"Error parsing button ID: {triggered_id}")
        return (
            dash.no_update,  # filter_set
            dash.no_update,  # conditions_list
            dash.no_update,  # table_container
            dash.no_update,  # row_count_display
            html.Div("Error removing filter condition.", style={'color': 'red'})  # filter_status
        )
    
    # Remove the condition at the specified index
    conditions = current_filter_set.get('conditions', [])
    if 0 <= index_to_remove < len(conditions):
        removed_condition = conditions.pop(index_to_remove)
        filter_set = {
            'conditions': conditions,
            'logic_operator': current_filter_set.get('logic_operator', 'AND'),
            'result_count': 0
        }
        
        # Generate updated conditions list
        conditions_list = _generate_conditions_list(filter_set['conditions'])
        
        # If no conditions left, restore original data
        if not conditions:
            if table_data and 'dataframe_json' in table_data:
                df = pd.DataFrame.from_dict(table_data['dataframe_json'])
                original_json = convert_to_json_format(df)
                table_columns = _select_table_columns(list(table_data['column_names']), visible_columns)
                table_component = create_table_component(
                    component_id="data-table",
                    data=original_json,
                    columns=table_columns,
                    enable_virtual_scrolling=len(df) > 1000,
                    enable_sorting=True
                )
                total_rows = table_data['row_count']
                row_count_display = format_row_count(total_rows)
                
                return (
                    filter_set,  # filter_set
                    conditions_list,  # conditions_list
                    html.Div([table_component], style={'margin': '20px'}),  # table_container
                    row_count_display,  # row_count_display
                    html.Div("All filters removed. Showing all data.", style={'color': 'green'})  # filter_status
                )
            else:
                return (
                    filter_set,  # filter_set
                    conditions_list,  # conditions_list
                    dash.no_update,  # table_container (keep current)
                    dash.no_update,  # row_count_display (keep current)
                    html.Div("Filter condition removed.", style={'color': 'green'})  # filter_status
                )
        else:
            # Reapply remaining filters
            try:
                df = pd.DataFrame.from_dict(table_data['dataframe_json'])
                logic_operator = filter_set['logic_operator']
                
                # Reapply remaining filters using unified logic
                filtered_df = _apply_filter_set_to_df(df, filter_set, table_data.get('column_types', {}))
                
                # Update filter set with result count
                filter_set['result_count'] = len(filtered_df)
                
                # Convert filtered DataFrame to JSON format
                filtered_json = convert_to_json_format(filtered_df)
                
                # Create table component with filtered data
                table_columns = _select_table_columns(list(table_data['column_names']), visible_columns)
                table_component = create_table_component(
                    component_id="data-table",
                    data=filtered_json,
                    columns=table_columns,
                    enable_virtual_scrolling=len(filtered_df) > 1000,
                    enable_sorting=True
                )
                
                # Update row count display
                total_rows = table_data['row_count']
                filtered_rows = len(filtered_df)
                row_count_display = format_row_count(total_rows, filtered_rows)
                
                if filtered_rows == 0:
                    status_msg = "No results match the current filter(s)."
                    status_color = "orange"
                else:
                    status_msg = f"Filter condition removed. {len(conditions)} filter(s) active ({filtered_rows} rows)"
                    status_color = "green"
                
                return (
                    filter_set,  # filter_set
                    conditions_list,  # conditions_list
                    _wrap_table_with_empty_state(table_component, filtered_rows),  # table_container
                    row_count_display,  # row_count_display
                    html.Div(status_msg, style={'color': status_color})  # filter_status
                )
            
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Error reapplying filters after removal: {error_msg}", exc_info=True)
                return (
                    filter_set,  # filter_set
                    conditions_list,  # conditions_list
                    dash.no_update,  # table_container (keep current)
                    dash.no_update,  # row_count_display (keep current)
                    html.Div(f"Error reapplying filters: {error_msg}", style={'color': 'red'})  # filter_status
                )
    else:
        return (
            dash.no_update,  # filter_set
            dash.no_update,  # conditions_list
            dash.no_update,  # table_container (keep current)
            dash.no_update,  # row_count_display (keep current)
            html.Div("Invalid filter index.", style={'color': 'red'})  # filter_status
        )

    # Performance logging (best-effort)
    try:
        log_filter_operation(
            logger,
            operation="remove_filter",
            filter_count=len(current_filter_set.get("conditions", [])) if current_filter_set else 0,
            result_count=int(current_filter_set.get("result_count", 0)) if current_filter_set else 0,
            duration=time.time() - _t0,
        )
    except Exception:
        pass


if __name__ == '__main__':
    app.run(debug=True, port=8050)

