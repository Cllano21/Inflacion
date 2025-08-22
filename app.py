import pandas as pd
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import os
from datos_generados import datos
from datetime import datetime

# Rename columns and clean data
df = pd.DataFrame(datos, columns=["Mes", "CPI"])

# Convert CPI to float
df["CPI"] = df["CPI"].astype(str).str.replace(",", ".").astype(float)

# Convert dates: now we use the format the data has
df["Mes"] = pd.to_datetime(df["Mes"], format="%Y-%m-%d %H:%M:%S", errors="coerce")

# Drop rows with invalid dates
df = df.dropna(subset=['Mes'])

# Extract the year
df["Año"] = df["Mes"].dt.year

# Calculate annual change
df["anual"] = df["CPI"].div(df["CPI"].shift(12)).subtract(1).multiply(100)

# Calculate 12-month moving average of annual change
df["anual_ma_12m"] = df["anual"].rolling(window=12, min_periods=1).mean()

# Inflación mensual en %
df["mensual"] = df["CPI"].pct_change().multiply(100)

# Last value
ultimo_valor = df["CPI"].iloc[-1] if not df.empty else 0
ultima_fecha = df["Mes"].iloc[-1].strftime("%b-%Y") if not df.empty else "N/A"
ultimo_anual = df["anual"].iloc[-1] if not df.empty and not pd.isna(df["anual"].iloc[-1]) else 0

# Get available years as integers
available_years = sorted(df["Año"].unique().tolist()) if not df.empty else []

# App
app = dash.Dash(__name__)
app.title = "CPI Dashboard"

# Layout
app.layout = html.Div(style={
    "fontFamily": "Arial, sans-serif",
    "minHeight": "100vh",
    "minWidth": "100vw",
    "background": "linear-gradient(to bottom right, #93c5fd, #1d4ed8, #0f172a)",
    "margin": "0",
    "padding": "0",
    "overflow": "hidden",
    "position": "relative"  # Added for sidebar positioning
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
    }, children=[html.Span("Inflation in Ecuador", style={"margin": "40px"})]),

    # Hamburger button
    html.Div(className="hamburger", id="menu-button", n_clicks=0, children=[
        html.Span(), html.Span(), html.Span()
    ], style={
        "position": "fixed",
        "top": "15px",
        "left": "15px",
        "zIndex": "1600",
        "cursor": "pointer",
        "width": "30px",
        "height": "22px",
    }),
    
    # Overlay for closing menu
    html.Div(id="overlay", style={
        "position": "fixed",
        "top": "0",
        "left": "0",
        "width": "100%",
        "height": "100%",
        "background": "rgba(0,0,0,0.5)",
        "zIndex": "1400",
        "display": "none",
        "transition": "opacity 0.3s ease",
        "opacity": "0"
    }),

    # Sidebar with smooth transition
    html.Div(id="sidebar", style={
        "position": "fixed",
        "top": "0",
        "left": "-250px",  # Start off-screen
        "height": "100vh",
        "width": "250px",
        "backgroundColor": "#7E92D3",
        "padding": "20px",
        "zIndex": "1500",
        "color": "white",
        "transition": "left 0.3s ease",
        "overflowY": "auto",
        "boxShadow": "2px 0 5px rgba(0,0,0,0.2)"
    }, children=[
        html.H3("Menu", style={"marginTop": "20px"}),
        html.Ul(style={"listStyleType": "none", "padding": "0"}, children=[
            html.Li(html.A("Home", href="#", style={"color": "white", "textDecoration": "none", "display": "block", "padding": "10px 0"})),
            html.Li(html.A("Data", href="#", style={"color": "white", "textDecoration": "none", "display": "block", "padding": "10px 0"})),
            html.Li(html.A("Charts", href="#", style={"color": "white", "textDecoration": "none", "display": "block", "padding": "10px 0"}))
        ]),
        html.Div(style={"position": "absolute", "top": "15px", "right": "15px", "cursor": "pointer"}, 
                 id="close-menu", children="✕")
    ]),

    # Main content with shift effect
    html.Div(id="main-content", style={
        "padding": "40px 20px 0px 20px",
        "transition": "transform 0.3s ease",
        "transform": "translateX(0)"
    }, children=[
        html.Div(style={
           "display": "flex",
            "flexDirection": "row",
            "flexWrap": "wrap",
            "gap": "30px",
            "overflowX": "auto",
            "paddingBottom": "10px"
            }, children=[
            
            # 🔹 Card 1 - General Index
            html.Div(style={
                "display": "flex",
                "flexDirection": "column",
                "height": "120px",
                "minHeight": "100px",
                "minWidth": "90px"
            }, children=[
                html.P("Latest Information", style={
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
                    html.H4("General Index", style={"margin": "4px 0 2px 0", "fontSize": "16px"}),
                    html.P(ultima_fecha, style={"fontSize": "14px", "margin": "2px 0"}),
                    html.H2(f"{ultimo_valor:.2f}", style={"color": "#FFEE8C", "fontSize": "18px", "margin": "2px 0"})
                ])
            ]),
            
            # 🔹 Card 2 - Annual Inflation
            html.Div(style={
                "display": "flex",
                "flexDirection": "column",
                "height": "120px",
                "minHeight": "100px",
                "minWidth": "90px"
            }, children=[
                html.P("Latest Information", style={
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
                    html.H4("Annual Inflation", style={"margin": "4px 0", "fontSize": "16px"}),
                    html.P(ultima_fecha, style={"fontSize": "14px", "margin": "2px 0"}),
                    html.H2(f"{ultimo_anual:.2f}%", style={"color": "#FFEE8C", "fontSize": "18px", "margin": "2px 0"})
                ])
            ]),
            
            # 🔹 Card 3 - Selected CPI
            html.Div(style={
                "display": "flex",
                "flexDirection": "column",
                "height": "120px",
                "minHeight": "100px",
                "minWidth": "90px"
            }, children=[
                html.P("Selected Information", style={
                    "fontWeight": "bold", "color": "#fff", "fontSize": "18px",
                    "textAlign": "center", 
                    "height": "30px",
                    "display": "flex", "alignItems": "center", "justifyContent": "center",
                    "marginBottom": "6px"
                }),
                html.Div(id="card-CPI-seleccionado", style={
                    "background": "rgba(255, 255, 255, 0.1)", "padding": "10px",
                    "borderRadius": "12px", "boxShadow": "0 10px 15px rgba(0, 0, 0, 0.1)",
                    "backdropFilter": "blur(4px)", "WebkitBackdropFilter": "blur(4px)",
                    "width": "100%",
                    "color": "white", "textAlign": "center",
                    "display": "flex", "flexDirection": "column", "justifyContent": "center",
                    "flex": "1"
                }, children=[
                    html.H4("Selected CPI", style={"margin": "4px 0", "fontSize": "16px"}),
                    html.P(id="fecha-CPI", style={"fontSize": "12px", "margin": "2px 0"}),
                    html.H2(id="valor-CPI", style={"fontSize": "18px", "margin": "2px 0"})
                ])
            ]),
            
            # 🔹 Card 4 - Selected Annual Inflation
            html.Div(style={
                "display": "flex",
                "flexDirection": "column",
                "height": "120px",
                "minHeight": "100px",
                "minWidth": "90px"
            }, children=[
                html.P("Selected Information", style={
                    "visibility": "hidden", "fontSize": "18px",
                    "height": "30px",
                    "marginBottom": "6px"
                }),
                html.Div(id="card-acumulada", style={
                    "background": "rgba(255, 255, 255, 0.1)", "padding": "10px",
                    "borderRadius": "12px", "boxShadow": "0 10px 15px rgba(0, 0, 0, 0.1)",
                    "backdropFilter": "blur(4px)", "WebkitBackdropFilter": "blur(4px)",
                    "width": "100%",
                    "color": "white", "textAlign": "center",
                    "display": "flex", "flexDirection": "column", "justifyContent": "center",
                    "flex": "1"
                }, children=[
                    html.H4("Selected Annual Inflation", style={"margin": "4px 0", "fontSize": "16px"}),
                    html.P(id="fecha-anual", style={"fontSize": "12px", "margin": "2px 0"}),
                    html.H2(id="anual", style={"fontSize": "18px", "margin": "2px 0"})
                ])
            ])
        ]),
        # 🔹 NEW YEAR RANGE SELECTION CARDS
        html.Div(style={"display": "flex", "gap": "15px", "marginTop": "10px"}, children=[
            # Card 2006-2016
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
                html.P("Year Range", style={"fontSize": "14px", "margin": "2px 0"}),
                html.H2("Decade 1", style={"color": "#FFEE8C", "margin": "2px 0", "fontSize": "18px"})
            ]),
            # Card 2017-2021
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
                html.P("Year Range", style={"fontSize": "14px", "margin": "2px 0"}),
                html.H2("Five-Year Period", style={"color": "#FFEE8C", "margin": "2px 0", "fontSize": "18px"})
            ]),
            # Card 2022-2025
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
                html.P("Year Range", style={"fontSize": "14px", "margin": "2px 0"}),
                html.H2("Present", style={"color": "#FFEE8C", "margin": "2px 0", "fontSize": "18px"})
            ]),
        ]),

        # 🔹 NEW: Series selector dropdown
        html.Div(style={"display": "flex", "gap": "10px", "marginTop": "20px", "alignItems": "center"}, children=[
            html.Div(style={"width": "200px"}, children=[
                html.H4("Select Year", style={"margin": "4px 0 2px 0", "color": "white"}),
                dcc.Dropdown(
                    id="selector-anios",
                    options=[{"label": str(y), "value": y} for y in available_years],
                    value=[max(available_years)] if available_years else None,
                    multi=True,
                    placeholder="Select one or more years..."
                )
            ]),
            html.Div(style={"width": "300px"}, children=[
                html.H4("Select Series", style={"margin": "4px 0 2px 0", "color": "white"}),
                dcc.Dropdown(
                    id="series-selector",
                    options=[
                        {"label": "CPI", "value": "CPI"},
                        {"label": "Annual Change (%)", "value": "anual"},
                        {"label": "Monthly Change (%)", "value": "mensual"},
                        {"label": "12-Month Moving Average", "value": "anual_ma_12m"}
                    ],
                    value=["CPI", "anual"],  # Default selected
                    multi=True,
                    placeholder="Select series to display..."
                )
            ]),
        ]),
        
        # 🔹 Chart
        html.Div([
            dcc.Graph(id="grafico-lineas")
        ], style={"width": "100%", "borderRadius": "12px", "overflow": "hidden", "height": "400px", "marginTop": "20px"})
    ])
])

# Callback for menu toggle
@app.callback(
    [Output("sidebar", "style"),
     Output("overlay", "style"),
     Output("main-content", "style")],
    [Input("menu-button", "n_clicks"),
     Input("close-menu", "n_clicks"),
     Input("overlay", "n_clicks")],
    [State("sidebar", "style"),
     State("overlay", "style"),
     State("main-content", "style")]
)
def toggle_menu(menu_clicks, close_clicks, overlay_clicks, sidebar_style, overlay_style, content_style):
    ctx = dash.callback_context
    if not ctx.triggered:
        return sidebar_style, overlay_style, content_style
        
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # If menu button is clicked
    if trigger_id == "menu-button":
        # Toggle menu open
        if menu_clicks % 2 == 1:
            sidebar_style["left"] = "0"
            overlay_style["display": "block"
            overlay_style["opacity"] = "1"
            content_style["transform"] = "translateX(250px)"
        else:
            sidebar_style["left"] = "-250px"
            overlay_style["opacity"] = "0"
            content_style["transform"] = "translateX(0)"
    
    # If close button or overlay is clicked
    elif trigger_id in ["close-menu", "overlay"]:
        sidebar_style["left"] = "-250px"
        overlay_style["opacity"] = "0"
        content_style["transform"] = "translateX(0)"
        
        # Set menu clicks to even number to sync state
        return sidebar_style, overlay_style, content_style
    
    # After overlay animation completes, hide it completely
    if overlay_style.get("opacity") == "0":
        # Add a small delay to allow the transition to complete
        overlay_style["display"] = "none"
    
    return sidebar_style, overlay_style, content_style

# Updated callback for the chart with series selector
@app.callback(
    Output("grafico-lineas", "figure"),
    [Input("selector-anios", "value"),
     Input("series-selector", "value"),
     Input("card-2006-2016", "n_clicks"),
     Input("card-2017-2021", "n_clicks"),
     Input("card-2022-2025", "n_clicks")]
)
def actualizar_grafico(anios_seleccionados_dropdown, series_seleccionadas, n_clicks_06_16, n_clicks_17_21, n_clicks_22_25):
    ctx = dash.callback_context
    anios_a_mostrar = anios_seleccionados_dropdown if anios_seleccionados_dropdown else []

    # Detect which input triggered the callback
    if ctx.triggered:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if button_id == "card-2006-2016":
            anios_a_mostrar = list(range(1969, 2025))
        elif button_id == "card-2017-2021":
            anios_a_mostrar = list(range(2017, 2022))
        elif button_id == "card-2022-2025":
            anios_a_mostrar = list(range(2022, 2026))

    # If no years are selected, show the last year by default
    if not anios_a_mostrar:
        if available_years:
            anios_a_mostrar = [max(available_years)]
        else:
            anios_a_mostrar = [datetime.now().year]

    # If no series are selected, show CPI and annual by default
    if not series_seleccionadas:
        series_seleccionadas = ["CPI", "anual"]

    # Filter data and create chart
    df_filtrado = df[df["Año"].isin(anios_a_mostrar)].copy()
    df_filtrado = df_filtrado.sort_values(by="Mes")
    
    # Calculate 12-month moving average of annual change for filtered data
    df_filtrado["anual_ma_12m"] = df_filtrado["anual"].rolling(window=12, min_periods=1).mean()

    fig = go.Figure()
    
    # Define colors and styles for each series
    series_styles = {
        "CPI": {"color": "#FFDE21", "yaxis": "y1", "dash": "solid", "width": 2},
        "anual": {"color": "#00FFFF", "yaxis": "y2", "dash": "dash", "width": 2},
        "mensual": {"color": "#FFA500", "yaxis": "y2", "dash": "dot", "width": 2},
        "anual_ma_12m": {"color": "#FF6B6B", "yaxis": "y2", "dash": "solid", "width": 3}
    }
    
    # Add traces for selected series
    if not df_filtrado.empty:
        for serie in series_seleccionadas:
            if serie in df_filtrado.columns:
                style = series_styles.get(serie, {})
                fig.add_trace(go.Scatter(
                    x=df_filtrado["Mes"],
                    y=df_filtrado[serie],
                    mode="lines+markers",
                    name=serie.replace("_", " ").title(),
                    yaxis=style.get("yaxis", "y1"),
                    line=dict(
                        color=style.get("color", "#000000"),
                        dash=style.get("dash", "solid"),
                        width=style.get("width", 2)
                    )
                ))
    
    fig.update_layout(
        title=dict(
            text="CPI and Related Indicators",
            font=dict(color="white"),
            pad=dict(b=0)
        ),
        font=dict(color="white"),
        height=400,
        xaxis=dict(
            title="Date",
            color="white",
            tickfont=dict(color="white")
        ),
        yaxis=dict(
            title=dict(text="General Index (CPI)", font=dict(color="white")),
            tickfont=dict(color="white"),
            zeroline=True,
            zerolinecolor="red",
            zerolinewidth=2
        ),
        yaxis2=dict(
            title=dict(text="Percentage Change (%)", font=dict(color="white")),
            tickfont=dict(color="white"),
            overlaying="y",
            side="right",
            zeroline=True,
            zerolinecolor="red",
            zerolinewidth=2
        ),
        legend=dict(font=dict(color="white"), x=0, y=1.1, orientation="h"),
        template="plotly_white",
        plot_bgcolor="rgba(255, 255, 255, 0.1)",
        paper_bgcolor="rgba(255, 255, 255, 0.1)"
    )
    
    return fig

# Callback to update cards on chart click
@app.callback(
    [Output("fecha-CPI", "children"),
     Output("valor-CPI", "children"),
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
        CPI_actual = fila_seleccionada["CPI"]
        anual_actual = fila_seleccionada["anual"]

        return (
            fecha_display,
            f"{CPI_actual:.2f}",
            fecha_display,
            f"{anual_actual:.2f}%" if pd.notna(anual_actual) else "Not available"
        )
    return "", "Select a point", "", "Select a point"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(host='0.0.0.0', port=port, debug=True)