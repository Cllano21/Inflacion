import dash
from dash import html

app = dash.Dash(__name__)
app.layout = html.H1("Hola mundo")

if __name__ == '__main__':
    app.run_server()