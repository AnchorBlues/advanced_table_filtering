"""Filter UI components for Dash application."""

from dash import dcc, html
from typing import List, Dict, Optional


def get_text_operators() -> List[Dict[str, str]]:
    """Get available text filter operators."""
    return [
        {'label': 'Equals', 'value': 'equals'},
        {'label': 'Contains', 'value': 'contains'},
        {'label': 'Starts with', 'value': 'starts_with'},
        {'label': 'Ends with', 'value': 'ends_with'}
    ]


def get_numeric_operators() -> List[Dict[str, str]]:
    """Get available numeric filter operators."""
    return [
        {'label': 'Equals', 'value': 'equals'},
        {'label': 'Greater than', 'value': 'greater_than'},
        {'label': 'Less than', 'value': 'less_than'},
        {'label': 'Between', 'value': 'between'}
    ]


def get_date_operators() -> List[Dict[str, str]]:
    """Get available date filter operators."""
    return [
        {'label': 'Equals', 'value': 'equals'},
        {'label': 'Before', 'value': 'before'},
        {'label': 'After', 'value': 'after'},
        {'label': 'Between', 'value': 'between'}
    ]


def get_operators_for_type(data_type: str) -> List[Dict[str, str]]:
    """
    Get filter operators for a given data type.
    
    Args:
        data_type: Column data type ('text', 'numeric', 'date')
    
    Returns:
        List of operator dictionaries
    """
    if data_type == 'text':
        return get_text_operators()
    elif data_type == 'numeric':
        return get_numeric_operators()
    elif data_type == 'date':
        return get_date_operators()
    else:
        return []


def create_filter_ui(
    component_id_prefix: str = "filter",
    column_names: Optional[List[str]] = None,
    column_types: Optional[Dict[str, str]] = None
) -> html.Div:
    """
    Create filter UI component with column dropdown, operator dropdown, value input, and apply button.
    
    Args:
        component_id_prefix: Prefix for component IDs
        column_names: List of available column names
        column_types: Dictionary mapping column names to data types
    
    Returns:
        html.Div containing filter UI components
    """
    # Default empty options
    column_options = []
    if column_names:
        column_options = [{'label': col, 'value': col} for col in column_names]

    visible_columns_options = column_options
    visible_columns_default = [col["value"] for col in column_options]
    
    return html.Div([
        html.H3("Filter Data", style={'margin': '20px 0 10px 0'}),
        
        # Column visibility controls
        html.Div([
            html.Label("Visible columns:", style={'display': 'inline-block', 'width': '150px', 'marginRight': '10px', 'verticalAlign': 'top', 'paddingTop': '8px', 'flexShrink': 0}),
            html.Div([
                dcc.Dropdown(
                    id=f"{component_id_prefix}-visible-columns",
                    options=visible_columns_options,
                    value=visible_columns_default,
                    multi=True,
                    searchable=True,  # 候補表示のための検索を明示的に有効化
                    placeholder="Select visible columns...",
                    style={
                        'width': '100%',
                    },
                    # 候補リストが表示されるように zIndex を調整し、
                    # クリップされないように設定
                    clearable=True,
                ),
            ], style={
                'flex': '1',
                'minWidth': '400px',
                # 候補リスト（メニュー）が枠外に出られるように overflow は設定しない
            }),
        ], style={
            'margin': '10px 0',
            'display': 'flex',
            'flexWrap': 'wrap', # 横スクロールではなく、自然に折り返すように変更
            'alignItems': 'flex-start',
            'width': '100%',
        }),

        # Column selection
        html.Div([
            html.Label("Column:", style={'display': 'inline-block', 'width': '100px', 'marginRight': '10px'}),
            dcc.Dropdown(
                id=f"{component_id_prefix}-column",
                options=column_options,
                placeholder="Select column...",
                style={'width': '200px', 'display': 'inline-block'}
            )
        ], style={'margin': '10px 0'}),
        
        # Operator selection (will be updated based on column type)
        html.Div([
            html.Label("Operator:", style={'display': 'inline-block', 'width': '100px', 'marginRight': '10px'}),
            dcc.Dropdown(
                id=f"{component_id_prefix}-operator",
                options=[],
                placeholder="Select operator...",
                disabled=True,
                style={'width': '200px', 'display': 'inline-block'}
            )
        ], style={'margin': '10px 0'}),
        
        # Value input
        html.Div([
            html.Label("Value:", style={'display': 'inline-block', 'width': '100px', 'marginRight': '10px'}),
            # Container for dynamic value input (Input or Dropdown)
            html.Div([
                dcc.Input(
                    id=f"{component_id_prefix}-value",
                    type='text',
                    placeholder="Enter filter value...",
                    disabled=True,
                    style={'width': '100%', 'display': 'inline-block'}
                ),
                dcc.Dropdown(
                    id=f"{component_id_prefix}-value-multi",
                    multi=True,
                    placeholder="Select values...",
                    style={'width': '100%', 'display': 'none'}
                ),
            ], id=f"{component_id_prefix}-value-container", style={'width': '300px', 'display': 'inline-block', 'verticalAlign': 'middle', 'marginRight': '10px'}),
            
            # Additional input for 'between' operator
            html.Span(
                dcc.Input(
                    id=f"{component_id_prefix}-value2",
                    type='text',
                    placeholder="Max value...",
                    disabled=True,
                    style={'width': '200px', 'display': 'none'}
                ),
                id=f"{component_id_prefix}-value2-container"
            )
        ], style={'margin': '10px 0'}),
        
        # Logic operator selection (for multiple filters)
        html.Div([
            html.Label("Combine filters with:", style={'display': 'inline-block', 'width': '150px', 'marginRight': '10px'}),
            dcc.RadioItems(
                id=f"{component_id_prefix}-logic",
                options=[
                    {'label': 'AND (all conditions)', 'value': 'AND'},
                    {'label': 'OR (any condition)', 'value': 'OR'}
                ],
                value='AND',
                inline=True,
                style={'display': 'inline-block'}
            )
        ], style={'margin': '10px 0'}),
        
        # Action buttons
        html.Div([
            html.Button(
                "Add Filter",
                id=f"{component_id_prefix}-add-btn",
                n_clicks=0,
                style={'marginRight': '10px', 'padding': '8px 16px', 'backgroundColor': '#28a745', 'color': 'white', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}
            ),
            html.Button(
                "Apply Filters",
                id=f"{component_id_prefix}-apply-btn",
                n_clicks=0,
                disabled=True,
                style={'marginRight': '10px', 'padding': '8px 16px', 'backgroundColor': '#007bff', 'color': 'white', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}
            ),
            html.Button(
                "Clear All Filters",
                id=f"{component_id_prefix}-clear-btn",
                n_clicks=0,
                style={'marginRight': '10px', 'padding': '8px 16px', 'backgroundColor': '#6c757d', 'color': 'white', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}
            ),
            html.Button(
                "Export CSV",
                id=f"{component_id_prefix}-export-btn",
                n_clicks=0,
                style={'padding': '8px 16px', 'backgroundColor': '#198754', 'color': 'white', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer'}
            )
        ], style={'margin': '10px 0'}),
        
        # Filter conditions list (for multiple filters)
        html.Div(id=f"{component_id_prefix}-conditions-list", style={'margin': '10px 0'}),
        
        # Filter status message
        html.Div(id=f"{component_id_prefix}-status", style={'margin': '10px 0', 'color': '#666'})
    ], style={'margin': '20px', 'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9'})

