# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import psycopg2, os
from dash.dependencies import Input, Output
from requests import put

# read database connection url from the environment variable we just set.
DATABASE_URL = os.environ.get('DATABASE_URL')

app = Dash(__name__)
server = app.server

colors = {
    'background': '#111111',
    'text': '#bd1919'
}

dbcon = psycopg2.connect(DATABASE_URL)
          
sql_query = pd.read_sql_query ('''
                               SELECT
                               *
                               FROM accel
                               ''', dbcon)

df = pd.DataFrame(sql_query, columns = ['id', 'axis', 'value', 'ts'])

#fig = px.bar(df, x="axis", y="value", color="id", barmode="group")

fig = px.scatter(df, x="ts", y="value", color="id",
                 facet_col="axis", trendline="ols", title="Fenix Productions")

fig.update_traces(
    line=dict(dash="dot", width=4),
    selector=dict(type="scatter", mode="lines"))

dbcon.close()

fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

app.layout = html.Div(    
    style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Trabalho de ISCF',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Gráficos de posições', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(
        id='fenix-graph',
        figure=fig
    ),

    html.Div([
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ]),

    html.H1(
        children='Change the value in the text box to see callbacks in action!',
        style={
            'textAlign': 'left',
            'color': colors['text']
        }
    ),
    html.Div([
        "Input: ",
        dcc.Input(id='my-input', value='initial value', type='text')
    ]),
    
    #codigo extra
    html.Div([
        dcc.ConfirmDialog(
            id='alerta',
            message='valor muito alto',
        ),
    ]),

    # dcc.Store stores the intermediate value
    dcc.Store(id='intermediate-value')
])

@app.callback(
    Output(component_id='interval-component', component_property='interval'),
    Input(component_id='my-input', component_property='value')
)
def update_output_div(input_value):
    con = psycopg2.connect(DATABASE_URL)
    cursor = con.cursor()

    if input_value.isdigit():
        cursor.execute("INSERT INTO timer(id, value) VALUES (DEFAULT, %s);"% (input_value))
        con.commit()
        con.close()
        #put('http://localhost:8050/update_rate/' + input_value)
        return int(float(input_value)) * 1000
    
    cursor.execute("INSERT INTO timer(id, value) VALUES (DEFAULT, %s);"% (1))
    con.commit()
    con.close()
    #put('http://localhost:8050/update_rate/1')
    return 1000

@app.callback(Output('fenix-graph', 'figure'),
              Input('interval-component', 'n_intervals'))

def update_graph_live(n):
    colors = {
        'background': '#111111',
        'text': '#bd1919'
    }

    dbcon = psycopg2.connect(DATABASE_URL)
            
    sql_query = pd.read_sql_query ('''
                                SELECT
                                *
                                FROM accel
                                ''', dbcon)

    df = pd.DataFrame(sql_query, columns = ['id', 'axis', 'value', 'ts'])
    
    #fig = px.bar(df, x="axis", y="value", color="id", barmode="group")

    fig = px.scatter(df, x="ts", y="value", color="id",
                    facet_col="axis", trendline="ols", title="Fenix Productions")

    fig.update_traces(
        line=dict(dash="dot", width=4),
        selector=dict(type="scatter", mode="lines"))

    dbcon.close()

    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )
    return fig

@app.callback(Output('alerta', 'displayed'),
              Input('interval-component', 'n_intervals'))
              
def display_confirm(value):
    dbcon = psycopg2.connect(DATABASE_URL)
            
    sql_query = pd.read_sql_query ('''
                                SELECT
                                *
                                FROM accel
                                ''', dbcon)

    df = pd.DataFrame(sql_query, columns = ['id', 'axis', 'value', 'ts'])
    value = df.iloc[len(df)-1]['value']
    bol = False
    if value > 1:
        bol = True
    if value < -11:
        bol = True

    value = df.iloc[len(df)-2]['value']

    if value > 4:
        bol = True
    if value < -9:
        bol = True

    value = df.iloc[len(df)-3]['value']

    if value > 7:
        bol = True
    if value < -10:
        bol = True
    return bol

@app.callback(Output('alerta', 'message'),
              Input('interval-component', 'n_intervals'))

def message_output(value):
    dbcon = psycopg2.connect(DATABASE_URL)
            
    sql_query = pd.read_sql_query ('''
                                SELECT
                                *
                                FROM accel
                                ''', dbcon)

    df = pd.DataFrame(sql_query, columns = ['id', 'axis', 'value', 'ts'])
    value = df.iloc[len(df)-1]['value']
    axis = ''
    
    if value > 1:
        axis = 'x'
    if value < -11:
        axis = 'x'

    value = df.iloc[len(df)-2]['value']

    if value > 4:
        axis = 'y'
    if value < -9:
        axis = 'y'

    value = df.iloc[len(df)-3]['value']

    if value > 7:
        axis = 'z'
    if value < -10:
        axis = 'z' 
    return axis + 'ultrapassou o limite'



if __name__ == '__main__':
    app.run_server(debug=True)