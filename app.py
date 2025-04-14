import dash
from dash import html, Dash, dcc
import dash_bootstrap_components as dbc

app = Dash(
    __name__, 
    use_pages = True, 
    suppress_callback_exceptions = True,
    prevent_initial_callbacks = True,
    external_stylesheets = [
        dbc.themes.BOOTSTRAP,
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css",
    ],
)

app.layout = html.Div([
    # html.H1('Dashboard'),
    # html.Div([
    #     html.Div(
    #         dcc.Link(f"{page['name']}", href=f"{page['relative_path']}"),
    #     ) for page in dash.page_registry.values()
    # ]),
    dash.page_container
])

server = app.server

if __name__ == '__main__':
    app.run(debug = False, port = 8050)
