"""File upload component for Dash application."""

from dash import dcc, html


def create_upload_component(component_id: str = "upload-data") -> dcc.Upload:
    """
    Create file upload component with drag-and-drop support.
    
    Args:
        component_id: Unique ID for the component
    
    Returns:
        dcc.Upload component configured for CSV, Excel, and JSON files
    """
    return dcc.Upload(
        id=component_id,
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple file types
        accept='.csv,.xlsx,.xls,.json',
        # Disable multiple file uploads for MVP
        multiple=False
    )

