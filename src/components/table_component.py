"""Table component wrapper for dash_table.DataTable."""

from dash import dash_table
from typing import List, Dict, Optional


def create_table_component(
    component_id: str = "data-table",
    data: Optional[List[Dict]] = None,
    columns: Optional[List[Dict]] = None,
    enable_virtual_scrolling: bool = True,
    enable_sorting: bool = True
) -> dash_table.DataTable:
    """
    Create dash_table.DataTable component with configuration.
    
    Args:
        component_id: Unique ID for the component
        data: Table data as list of dictionaries (DataFrame.to_dict('records') format)
        columns: Column definitions (auto-generated if None)
        enable_virtual_scrolling: Enable virtual scrolling for large datasets
        enable_sorting: Enable column sorting
    
    Returns:
        Configured dash_table.DataTable component
    """
    # Default empty data if not provided
    if data is None:
        data = []
    
    # Auto-generate columns from data if not provided
    if columns is None and len(data) > 0:
        columns = [{"name": col, "id": col} for col in data[0].keys()]
    elif columns is None:
        columns = []
    
    # Configure DataTable
    # NOTE:
    # - For large datasets, prefer virtualization (smooth scroll) over pagination.
    # - For small datasets, keep native paging to reduce DOM load.
    use_virtualization = bool(enable_virtual_scrolling)

    table_config = {
        'id': component_id,
        'data': data,
        'columns': columns,
        'sort_action': 'native' if enable_sorting else 'none',
        'sort_mode': 'multi' if enable_sorting else 'single',
        'filter_action': 'none',  # We'll implement custom filtering via callbacks
        # Virtual scrolling optimization:
        # - If virtualization is enabled: disable paging and enable DataTable virtualization
        # - Else: use native paging
        'page_action': 'none' if use_virtualization else 'native',
        'page_size': 50,  # Used only when page_action='native'
        'virtualization': use_virtualization,
        'fixed_rows': {'headers': True},
        'style_table': {
            'height': '600px',
            'overflowY': 'auto',
            'overflowX': 'auto'
        },
        'style_cell': {
            'textAlign': 'left',
            'padding': '10px',
            'minWidth': '100px',
            'width': '150px',
            'maxWidth': '300px',
            'whiteSpace': 'normal',
            'height': 'auto'
        },
        'style_header': {
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        'style_data': {
            'whiteSpace': 'normal',
            'height': 'auto'
        },
        'export_format': 'csv',  # Enable CSV export
        'export_headers': 'display'  # Export with display headers
    }
    
    return dash_table.DataTable(**table_config)

