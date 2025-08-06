import pandas as pd
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import os
from datos_generados import datos
from datetime import datetime

# Renombrar columnas y limpiar datos
df = pd.DataFrame(datos, columns=["Mes", "IPC"])

# Verificar si hay datos
if df.empty:
    # Crear un DataFrame vacío con la estructura esperada
    df = pd.DataFrame(columns=["Mes", "IPC", "Año", "anual"])
    ultimo_valor = 0
    ultima_fecha = "N/A"
    ultimo_anual = 0
    available_years = []
else:
    # Convertir IPC a float
    df["IPC"] = df["IPC"].astype(str).str.replace(",", ".").astype(float)
    
    # Convertir fechas
    df["Mes"] = pd.to_datetime(df["Mes"], format="%b-%y", errors="coerce")
    
    # Eliminar filas con fechas inválidas
    df = df.dropna(subset=['Mes'])
    
    if df.empty:
        # Si después de limpiar está vacío
        df = pd.DataFrame(columns=["Mes", "IPC", "Año", "anual"])
        ultimo_valor = 0
        ultima_fecha = "N/A"
        ultimo_anual = 0
        available_years = []
    else:
        # Convertir año a entero
        df["Año"] = df["Mes"].dt.year.astype(int)

        # Calcular variación anual
        df["anual"] = df["IPC"].div(df["IPC"].shift(12)).subtract(1).multiply(100)

        # Último valor
        ultimo_valor = df["IPC"].iloc[-1] if not df.empty else 0
        ultima_fecha = df["Mes"].dt.strftime("%b-%Y").iloc[-1] if not df.empty else "N/A"
        ultimo_anual = df["anual"].iloc[-1] if not df.empty and not pd.isna(df["anual"].iloc[-1]) else 0

        # Obtener años disponibles como enteros
        available_years = sorted(df["Año"].unique().tolist()) if not df.empty else []

# App
app = dash.Dash(__name__)
app.title = "Dashboard IPC"

# Layout
app.layout = html.Div(style={
    "fontFamily": "Arial, sans-serif",
    "minHeight": "100vh",
    "minWidth": "100vw",
    "background": "linear-gradient(to bottom right, #93c5fd, #1d4ed8, #0f172a)",
    "margin": "0",
    "padding": "0",
    "overflow": "hidden"
}, children=[

    # Navbar
    html.Div(style={
        "position": "fixed",
        "top": "0",
        "left": "0",
        "width": "100%",
        "background": "linear-gradient(to bottom right, #fff700, #facc15, #b45309)",
        "padding": "10px 10px",
        "color": "white",
        "fontSize": "20px",
        "fontWeight": "bold",
        "zIndex": "1000",
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
    }, children=[html.Span("Inflación en Ecuador", style={"margin": "40px"})]),

    # Botón hamburguesa
    html.Div(className="hamburger", id="menu-button", n_clicks=0, children=[
        html.Span(), html.Span(), html.Span()
    ]),

    # Sidebar
    html.Div(id="sidebar", style={
        "position": "fixed",
        "top": "0",
        "left": "0",
        "height": "100vh",
        "width": "250px",
        "backgroundColor": "#1e3a8a",
        "padding": "20px",
        "display": "none",
        "zIndex": "1500",
        "color": "white"
    }, children=[
        html.H3("Menú"),
        html.Ul([
            html.Li("Inicio"),
            html.Li("Datos"),
            html.Li("Gráficos")
        ])
    ]),

    # Contenido principal
    html.Div(style={"padding": "40px 20px 0px 20px" }, children=[
        html.Div(style={
           "display": "flex",
            "flexDirection": "row",
            "flexWrap": "wrap",
            "gap": "30px",
            "overflowX": "auto",
            "paddingBottom": "10px"
            }, children=[
            
            # 🔹 Tarjeta 1 - Índice General
            html.Div(style={
                "display": "flex",
                "flexDirection": "column",
                "height": "120px",
                "minHeight": "100px",
                "minWidth": "90px"
            }, children=[
                html.P("Información Junio", style={
                    "fontWeight": "bold", "color": "#fff", "marginBottom": "6px",
                    "fontSize": "18px", "textAlign": "center", 
                    "height": "30px",
                    "display": "flex", "alignItems": "center", "justifyContent": "center"
                }),
                html.Div(style={
                    "background": "rgba(255, 255, 255, 0.1)", "padding": "10px",
                    "borderRadius": "12px", "boxShadow": "0 10px 15px rgba(0, 0, 0, 0.1)",
                    "backdropFilter": "blur(4px)", "WebkitBackdropFilter": "blur(4px)",
                    "width": "100%",
                    "color": "#fff", "textAlign": "center",
                    "display": "flex", "flexDirection": "column", "justifyContent": "center",
                    "flex": "1"
                }, children=[
                    html.H4("Índice General", style={"margin": "4px 0 2px 0", "fontSize": "16px"}),
                    html.P(ultima_fecha, style={"fontSize": "14px", "margin": "2px 0"}),
                    html.H2(f"{ultimo_valor:.2f}", style={"color": "#FFEE8C", "fontSize": "18px", "margin": "2px 0"})
                ])
            ]),
            
            # 🔹 Tarjeta 2 - Inflación Anual
            html.Div(style={
                "display": "flex",
                "flexDirection": "column",
                "height": "120px",
                "minHeight": "100px",
                "minWidth": "90px"
            }, children=[
                html.P("Información Junio", style={
                    "visibility": "hidden", "fontSize": "18px",
                    "height": "30px",
                    "marginBottom": "6px"
                }),
                html.Div(style={
                    "background": "rgba(255, 255, 255, 0.1)", "padding": "10px",
                    "borderRadius": "12px", "boxShadow": "0 10px 15px rgba(0, 0, 0, 0.1)",
                    "backdropFilter": "blur(4px)", "WebkitBackdropFilter": "blur(4px)",
                    "width": "100%",
                    "color": "#fff", "textAlign": "center",
                    "display": "flex", "flexDirection": "column", "justifyContent": "center",
                    "flex": "1"
                }, children=[
                    html.H4("Inflación Anual", style={"margin": "4px 0", "fontSize": "16px"}),
                    html.P(ultima_fecha, style={"fontSize": "14px", "margin": "2px 0"}),
                    html.H2(f"{ultimo_anual:.2f}%", style={"color": "#FFEE8C", "fontSize": "18px", "margin": "2px 0"})
                ])
            ]),
            
            # 🔹 Tarjeta 3 - IPC Seleccionado
            html.Div(style={
                "display": "flex",
                "flexDirection": "column",
                "height": "120px",
                "minHeight": "100px",
                "minWidth": "90px"
            }, children=[
                html.P("Información Seleccionada", style={
                    "fontWeight": "bold", "color": "#fff", "fontSize": "18px",
                    "textAlign": "center", 
                    "height": "30px",
                    "display": "flex", "alignItems": "center", "justifyContent": "center",
                    "marginBottom": "6px"
                }),
                html.Div(id="card-ipc-seleccionado", style={
                    "background": "rgba(255, 255, 255, 0.1)", "padding": "10px",
                    "borderRadius": "12px", "boxShadow": "0 10px 15px rgba(0, 0, 0, 0.1)",
                    "backdropFilter": "blur(4px)", "WebkitBackdropFilter": "blur(4px)",
                    "width": "100%",
                    "color": "#fff", "textAlign": "center",
                    "display": "flex", "flexDirection": "column", "justifyContent": "center",
                    "flex": "1"
                }, children=[
                    html.H4("IPC Seleccionado", style={"margin": "4px 0", "fontSize": "16px"}),
                    html.P(id="fecha-ipc", style={"fontSize": "12px", "margin": "2px 0"}),
                    html.H2(id="valor-ipc", style={"fontSize": "18px", "margin": "2px 0"})
                ])
            ]),
            
            # 🔹 Tarjeta 4 - Inflación Anual Seleccionada
            html.Div(style={
                "display": "flex",
                "flexDirection": "column",
                "height": "120px",
                "minHeight": "100px",
                "minWidth": "90px"
            }, children=[
                html.P("Información Seleccionada", style={
                    "visibility": "hidden", "fontSize": "18px",
                    "height": "30px",
                    "marginBottom": "6px"
                }),
                html.Div(id="card-acumulada", style={
                    "background": "rgba(255, 255, 255, 0.1)", "padding": "10px",
                    "borderRadius": "12px", "boxShadow": "0 10px 15px rgba(0, 0, 0, 0.1)",
                    "backdropFilter": "blur(4px)", "WebkitBackdropFilter": "blur(4px)",
                    "width": "100%",
                    "color": "#fff", "textAlign": "center",
                    "display": "flex", "flexDirection": "column", "justifyContent": "center",
                    "flex": "1"
                }, children=[
                    html.H4("Inflación Anual Seleccionada", style={"margin": "4px 0", "fontSize": "16px"}),
                    html.P(id="fecha-anual", style={"fontSize": "12px", "margin": "2px 0"}),
                    html.H2(id="anual", style={"fontSize": "18px", "margin": "2px 0"})
                ])
            ])
        ]),
        # 🔹 NUEVAS TARJETAS DE SELECCIÓN DE AÑOS POR RANGO
        html.Div(style={"display": "flex", "gap": "15px", "marginTop": "10px"}, children=[
            # Tarjeta 2006-2016
            html.Div(id="card-2006-2016", n_clicks=0, style={
                "background": "rgba(255, 255, 255, 0.1)",
                "padding": "3px",
                "borderRadius": "12px",
                "boxShadow": "0 10px 15px rgba(0, 0, 0, 0.1)",
                "backdropFilter": "blur(4px)",
                "WebkitBackdropFilter": "blur(4px)",
                "textAlign": "center",
                "width": "160px",
                "height": "70px",
                "color": "#fff",
                "cursor": "pointer"
            }, children=[
                html.H4("2006-2016", style={"margin": "4px 0 2px 0"}),
                html.P("Rango de Años", style={"fontSize": "14px", "margin": "2px 0"}),
                html.H2("Década 1", style={"color": "#FFEE8C", "margin": "2px 0", "fontSize": "18px"})
            ]),
            # Tarjeta 2017-2021
            html.Div(id="card-2017-2021", n_clicks=0, style={
                "background": "rgba(255, 255, 255, 0.1)",
                "padding": "3px",
                "borderRadius": "12px",
                "boxShadow": "0 10px 15px rgba(0, 0, 0, 0.1)",
                "backdropFilter": "blur(4px)",
                "WebkitBackdropFilter": "blur(4px)",
                "textAlign": "center",
                "width": "160px",
                "height": "90px",
                "color": "#fff",
                "cursor": "pointer"
            }, children=[
                html.H4("2017-2021", style={"margin": "4px 0 2px 0"}),
                html.P("Rango de Años", style={"fontSize": "14px", "margin": "2px 0"}),
                html.H2("Quinquenio", style={"color": "#FFEE8C", "margin": "2px 0", "fontSize": "18px"})
            ]),
            # Tarjeta 2022-2025
            html.Div(id="card-2022-2025", n_clicks=0, style={
                "background": "rgba(255, 255, 255, 0.1)",
                "padding": "3px",
                "borderRadius": "12px",
                "boxShadow": "0 10px 15px rgba(0, 0, 0, 0.1)",
                "backdropFilter": "blur(4px)",
                "WebkitBackdropFilter": "blur(4px)",
                "textAlign": "center",
                "width": "160px",
                "height": "90px",
                "color": "#fff",
                "cursor": "pointer"
            }, children=[
                html.H4("2022-2025", style={"margin": "4px 0 2px 0"}),
                html.P("Rango de Años", style={"fontSize": "14px", "margin": "2px 0"}),
                html.H2("Actualidad", style={"color": "#FFEE8C", "margin": "2px 0", "fontSize": "18px"})
            ]),
        ]),

        # 🔹 TARJETAS DE IPC Y VARIACIÓN ACUMULADA (EXISTENTES)
    
       # Dropdown + gráfico
        html.Div(style={"display": "flex", "gap": "10px", "marginTop": "20px"}, children=[
            html.Div(style={"width": "200px"}, children=[
                html.H4("Escoge Año", style={"margin": "4px 0 2px 0", "color": "white"}),
                dcc.Dropdown(
                    id="selector-anios",
                    options=[{"label": str(y), "value": y} for y in available_years],
                    value=[max(available_years)] if available_years else None,
                    multi=True,
                    placeholder="Selecciona uno o varios años..."
                )
            ]),
            html.Div([
                dcc.Graph(id="grafico-lineas")
            ], style={"width": "90%", "borderRadius": "12px", "overflow": "hidden","height": "350px", "minHeight": "250px"})
        ])
    ])
])

# Callback unificado corregido para el gráfico
@app.callback(
    Output("grafico-lineas", "figure"),
    [Input("selector-anios", "value"),
     Input("card-2006-2016", "n_clicks"),
     Input("card-2017-2021", "n_clicks"),
     Input("card-2022-2025", "n_clicks")]
)
def actualizar_grafico(anios_seleccionados_dropdown, n_clicks_06_16, n_clicks_17_21, n_clicks_22_25):
    ctx = dash.callback_context
    anios_a_mostrar = anios_seleccionados_dropdown if anios_seleccionados_dropdown else []

    # Detectar qué input disparó el callback
    if ctx.triggered:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if button_id == "card-2006-2016":
            anios_a_mostrar = list(range(2006, 2017))
        elif button_id == "card-2017-2021":
            anios_a_mostrar = list(range(2017, 2022))
        elif button_id == "card-2022-2025":
            anios_a_mostrar = list(range(2022, 2026))

    # Si no hay años seleccionados, mostrar el último año por defecto
    if not anios_a_mostrar:
        if available_years:
            anios_a_mostrar = [max(available_years)]
        else:
            anios_a_mostrar = [datetime.now().year]

    # Filtrar datos y crear gráfico
    df_filtrado = df[df["Año"].isin(anios_a_mostrar)].copy()
    df_filtrado = df_filtrado.sort_values(by="Mes")

    fig = go.Figure()
    if not df_filtrado.empty:
        fig.add_trace(go.Scatter(
            x=df_filtrado["Mes"],
            y=df_filtrado["IPC"],
            mode="lines+markers",
            name="IPC General",
            yaxis="y1",
            line=dict(color="#FFDE21")
        ))
        fig.add_trace(go.Scatter(
            x=df_filtrado["Mes"],
            y=df_filtrado["anual"],
            mode="lines+markers",
            name="Variación Anual (%)",
            yaxis="y2",
            line=dict(color="#00FFFF", dash="dash")
        ))
    
    fig.update_layout(
        title=dict(text="IPC y Variación Anual", font=dict(color="white"), pad=dict(b=0)),
        font=dict(color="white"),
        height=350,
        xaxis=dict(title="Fecha", color="white", tickfont=dict(color="white")),
        yaxis=dict(title=dict(text="Índice General (IPC)", font=dict(color="white")), tickfont=dict(color="white")),
        yaxis2=dict(
            title=dict(text="Variación Anual (%)", font=dict(color="white")),
            tickfont=dict(color="white"),
            overlaying="y",
            side="right"
        ),
        legend=dict(font=dict(color="white"), x=0, y=1.1, orientation="h"),
        template="plotly_white",
        plot_bgcolor="rgba(255, 255, 255, 0.1)",
        paper_bgcolor="rgba(255, 255, 255, 0.1)"
    )
    
    return fig

# Callback para actualizar tarjetas al hacer clic en el gráfico
@app.callback(
    [Output("fecha-ipc", "children"),
     Output("valor-ipc", "children"),
     Output("fecha-anual", "children"),
     Output("anual", "children")],
    Input("grafico-lineas", "clickData")
)
def actualizar_tarjetas(clickData):
    if clickData and not df.empty:
        fecha_str_click = clickData["points"][0]["x"]
        fecha_dt = pd.to_datetime(fecha_str_click)
        
        idx_cercano = (df["Mes"] - fecha_dt).abs().argsort()[0]
        fila_seleccionada = df.iloc[idx_cercano]

        fecha_display = fila_seleccionada["Mes"].strftime("%b-%Y")
        ipc_actual = fila_seleccionada["IPC"]
        anual_actual = fila_seleccionada["anual"]

        return (
            fecha_display,
            f"{ipc_actual:.2f}",
            fecha_display,
            f"{anual_actual:.2f}%" if pd.notna(anual_actual) else "No disponible"
        )
    return "", "Seleccione punto", "", "Seleccione punto"

# Sidebar toggle
@app.callback(
    Output("sidebar", "style"),
    Input("menu-button", "n_clicks"),
    State("sidebar", "style")
)
def toggle_sidebar(n_clicks, style):
    if n_clicks is None:
        return style or {"display": "none"}
    
    if n_clicks % 2 == 1:
        style["display"] = "block"
    else:
        style["display"] = "none"
    return style

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(host='0.0.0.0', port=port, debug=True)