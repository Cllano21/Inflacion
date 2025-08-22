# Corrected unified callback for the chart
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

    # Filter data and create chart
    df_filtrado = df[df["Año"].isin(anios_a_mostrar)].copy()
    df_filtrado = df_filtrado.sort_values(by="Mes")
    
    # Calculate 6-month moving average of annual change
    df_filtrado["anual_ma_6m"] = df_filtrado["anual"].rolling(window=6, min_periods=1).mean()

    fig = go.Figure()
    if not df_filtrado.empty:
        fig.add_trace(go.Scatter(
            x=df_filtrado["Mes"],
            y=df_filtrado["CPI"],
            mode="lines+markers",
            name="General CPI",
            yaxis="y1",
            line=dict(color="#FFDE21")
        ))
        fig.add_trace(go.Scatter(
            x=df_filtrado["Mes"],
            y=df_filtrado["anual"],
            mode="lines+markers",
            name="Annual Change (%)",
            yaxis="y2",
            line=dict(color="#00FFFF", dash="dash")
        ))
        fig.add_trace(go.Scatter(
            x=df_filtrado["Mes"],
            y=df_filtrado["anual_ma_6m"],
            mode="lines",
            name="6-Month MA of Annual Change",
            yaxis="y2",
            line=dict(color="#FF6B6B", width=3)
        ))
    
    fig.update_layout(
        title=dict(text="CPI, Annual Change, and 6-Month Moving Average", font=dict(color="white"), pad=dict(b=0)),
        font=dict(color="white"),
        height=350,
        xaxis=dict(title="Date", color="white", tickfont=dict(color="white")),
        yaxis=dict(title=dict(text="General Index (CPI)", font=dict(color="white")), tickfont=dict(color="white")),
        yaxis2=dict(
            title=dict(text="Annual Change (%)", font=dict(color="white")),
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