import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import psycopg2
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

USER = "postgres"
PASSWORD = "proyecto"
HOST = "proy3.crou4eqqiv8w.us-east-1.rds.amazonaws.com"
PORT = "5432"
DBNAME = "data"

# Título del dashboard
app.title = "Analítica de Resultados de Lectura Crítica en Pruebas SABER 11"


#############################################################################################################
#################################### SIN MODELO #############################################################
#############################################################################################################

@app.callback(
    Output('global-score', 'children'),
    [Input('refresh-button', 'n_clicks')]
)

# Función para promedio puntaje LC
def update_global_score(n_clicks):
    conn = psycopg2.connect(
        dbname=DBNAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )
    
    query = "SELECT AVG(punt_lectura_critica) FROM icfes;"
    
    cursor = conn.cursor()
    cursor.execute(query)
    average_global_score = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return f"Promedio del Puntaje de Lectura Crítica Nacional: {average_global_score:.2f}"

# Función de municipio
def get_cole_mcpio_options():
    conn = psycopg2.connect(
        dbname=DBNAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT cole_mcpio_ubicacion FROM icfes;")
    options = [{'label': row[0], 'value': row[0]} for row in cursor.fetchall()]
    conn.close()
    return options

@app.callback(
    Output('mcpio-average', 'children'),
    [Input('mcpio-dropdown', 'value')]
)

def update_mcpio_average(selected_mcpio):
    conn = psycopg2.connect(
        dbname=DBNAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )

    query = f"SELECT AVG(punt_lectura_critica) FROM icfes WHERE cole_mcpio_ubicacion = '{selected_mcpio}';"
    
    cursor = conn.cursor()
    cursor.execute(query)
    average_mcpio_score = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    
    return f"Promedio del Puntaje de Lectura Crítica en {selected_mcpio}: {average_mcpio_score:.2f}"


# Función para gráficos de caja e histogramas
@app.callback(
    Output('boxplots', 'children'),
    [Input('refresh-button', 'n_clicks')]
)
def update_boxplots(n_clicks):
    conn = psycopg2.connect(
        dbname=DBNAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )
    
    query = """
    SELECT fami_tieneautomovil, fami_tienecomputador, fami_tieneinternet, fami_tienelavadora, punt_lectura_critica,
           fami_cuartoshogar, fami_estratovivienda, fami_personashogar, cole_bilingue, cole_jornada, estu_estudiante, cole_mcpio_ubicacion

    FROM icfes;
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    df = df[ #especificando valores de cada variable
        (df['fami_tieneautomovil'].isin(['Si', 'No'])) & 
        (df['fami_tienecomputador'].isin(['Si', 'No'])) & 
        (df['fami_tieneinternet'].isin(['Si', 'No'])) & 
        (df['fami_tienelavadora'].isin(['Si', 'No'])) &
        (df['fami_cuartoshogar'].isin(['1', '2', '3', '4', '5', '6 o más'])) &
        (df['fami_estratovivienda'].isin(['1', '2', '3', '4', '5', '6'])) &
        (df['fami_personashogar'].isin(['1', '2', '3', '4', '5', '6', '7', '8', '9 o más'])) &
        (df['cole_bilingue'].isin(['S', 'N'])) &
        (df['cole_jornada'].notnull()) &
        (df['cole_mcpio_ubicacion'].notnull())
    ]
    
    def add_mean_line(fig, df, column): # Promedio de categoría
        mean_values = df.groupby(column)['punt_lectura_critica'].mean().reset_index()
        for i, val in enumerate(mean_values.itertuples()):
            x_pos = i # Separación entre las cajas
            
            
            fig.add_annotation(
                x=x_pos,
                y=val.punt_lectura_critica,
                text=f"Promedio: {val.punt_lectura_critica:.2f}",
                showarrow=False,
                yshift=10
            )
        return fig

    # Gráficos
    fig1 = px.box(df, x='fami_tieneautomovil', y='punt_lectura_critica', title='¿La familia tiene automóvil?')
    fig1 = add_mean_line(fig1, df, 'fami_tieneautomovil')
    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    fig2 = px.box(df, x='fami_tienecomputador', y='punt_lectura_critica', title='¿La familia tiene computador?')
    fig2 = add_mean_line(fig2, df, 'fami_tienecomputador')
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    fig3 = px.box(df, x='fami_tieneinternet', y='punt_lectura_critica', title='¿La familia tiene internet?')
    fig3 = add_mean_line(fig3, df, 'fami_tieneinternet')
    fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    fig4 = px.box(df, x='fami_tienelavadora', y='punt_lectura_critica', title='¿La familia tiene lavadora?')
    fig4 = add_mean_line(fig4, df, 'fami_tienelavadora')
    fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    fig8 = px.box(df, x='cole_bilingue', y='punt_lectura_critica', title='¿El colegio es bilingue?')
    fig8 = add_mean_line(fig8, df, 'cole_bilingue')
    fig8.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    fig9 = px.box(df, x='cole_jornada', y='punt_lectura_critica', title='¿Cuál es la jornada del colegio?')
    fig9 = add_mean_line(fig9, df, 'cole_jornada')
    fig9.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')


    def create_combined_histogram(df, column, title, category_order): # Gráfico mixto histograma y líneas
        histogram = go.Histogram(
            x=df[column],
            name='Frecuencia',
            marker=dict(color='lightblue')
        )
        
        mean_values = df.groupby(column)['punt_lectura_critica'].mean().reset_index()
        line = go.Scatter(
            x=mean_values[column],
            y=mean_values['punt_lectura_critica'],
            name='Promedio Puntaje',
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='darkblue'),
            marker=dict(size=8)
        )
        
        layout = go.Layout(
            title=title,
            xaxis=dict(title=column),
            yaxis=dict(title='Frecuencia'),
            yaxis2=dict(title='Promedio Puntaje Lectura Crítica', overlaying='y', side='right'),
            legend=dict(x=1.3, y=1.0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        fig = go.Figure(data=[histogram, line], layout=layout)
        fig.update_xaxes(categoryorder='array', categoryarray=category_order)
        return fig
    
    fig5 = create_combined_histogram(df, 'fami_cuartoshogar', 'Número de Cuartos en el Hogar', ['1', '2', '3', '4', '5', '6 o más'])
    fig6 = create_combined_histogram(df, 'fami_estratovivienda', 'Estrato de la Vivienda', ['1', '2', '3', '4', '5', '6'])
    fig7 = create_combined_histogram(df, 'fami_personashogar', 'Número de Personas en el Hogar', ['1', '2', '3', '4', '5', '6', '7', '8', '9 o más'])



    return html.Div([
        html.H2("Relación entre características socioeconómicas y puntaje en lectura crítica", style={'textAlign': 'center'}),
        html.Div([
            html.Div(dcc.Graph(figure=fig1), style={'width': '25%'}),
            html.Div(dcc.Graph(figure=fig2), style={'width': '25%'}),
            html.Div(dcc.Graph(figure=fig3), style={'width': '25%'}),
            html.Div(dcc.Graph(figure=fig4), style={'width': '25%'})
        ], style={'display': 'flex'}),
    
        html.Div([
            html.Div(dcc.Graph(figure=fig5), style={'width': '33%'}),
            html.Div(dcc.Graph(figure=fig6), style={'width': '33%'}),
            html.Div(dcc.Graph(figure=fig7), style={'width': '33%'}),
        ], style={'display': 'flex'}),
        html.H2("Relación entre características de la institución educativa y puntaje en lectura crítica", style={'textAlign': 'center'}),
        html.Div([
            html.Div(dcc.Graph(figure=fig8), style={'width': '40%'}),
            html.Div(dcc.Graph(figure=fig9), style={'width': '60%'}),
        ], style={'display': 'flex'})
    ], style={'flex-direction': 'column'})


#############################################################################################################
#################################### Modelo Predictivo#######################################################
#############################################################################################################

import joblib
#modelo = joblib.load('modelo_regresion_lineal.pkl')


#############################################################################################################
app.layout = html.Div([
    html.Div(
        html.H1(app.title),
        style={'textAlign': 'center'}
    ),
    html.Button("Actualizar", id="refresh-button"),
    html.Div(id="global-score", style={'textAlign': 'center'}),
    html.Div(id="boxplots"),
    html.Div([
        dcc.Dropdown(
            id='mcpio-dropdown',
            options=get_cole_mcpio_options(),
            value=get_cole_mcpio_options()[0]['value']
        ),
        html.Div(id='mcpio-average')
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)

