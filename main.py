from dash import dcc, html
import dash
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd 


df = pd.read_csv('EMSdataset.csv')
df_diff = df.drop(columns=['Date/time']).diff()
df_diff.insert(0, 'Date/time' ,df['Date/time'])
df_diff = df_diff.iloc[1:,:]
df = df_diff
df['Date/time'] = pd.to_datetime(df['Date/time'])
df['Date'] = pd.to_datetime(df['Date/time']).dt.date


fontawesome_stylesheet = "https://use.fontawesome.com/releases/v5.8.1/css/all.css"

app = dash.Dash(
    __name__,
    suppress_callback_exceptions = True,
    external_stylesheets=[dbc.themes.BOOTSTRAP, fontawesome_stylesheet],
 
    )

app.layout = html.Div([
    dbc.Row([
        html.H1(id='heatmap_app', children=['App Title'], style={'textAlign':'center', 'marginBottom':'5vh'}),

    ]),
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Dropdown(id='slct_month', 
                            options=[
                                {'label': m , 'value':m} for m in df['Date/time'].dt.month_name().unique()
                                ],
                            value='June',
                            style={"textAlign": "center", 'border':'transparent'}, 
                            ),

            ], style={ 'marginBottom':'5vh', }),
        ], width=2),
        dbc.Col([
            html.Div([
            dcc.Dropdown(
                id='slct_type2',
                options =[
                    {'label':'Generators', 'value':'generators'},
                    {'label':'receivers', 'value':'receivers'},
                ],
                value='generators',
                style={"textAlign": "center", 'border':'transparent'}, 

                ),
            ],),
        ], width=2),

    ]),
    dbc.Row([
        dbc.Col([
            html.Div([
                dcc.Dropdown(id='slct_column', 
                            options=[],
                            value=df.columns[1],
                            style={"textAlign": "center"}, 
                            ),
            ]),

        ], width=2),
        dbc.Col([
            html.Div([
                dcc.Dropdown(id='slct_chart_type', 
                            options = [
                                {'label':'Based on Day Name'.title(), 'value':'day_name'}, 
                                {'label':'Daily'.title(), 'value':'day_number'},
                            ],
                            value='day_name',

                )

            ]),
        ], width=2),
    ]),
    dbc.Row([
        html.Div([

            dbc.Col(
                dcc.Graph(id='heatmap', figure={}),
                xs=12, sm=12, md=12, lg=12, xl=12

            ),
        ]),
    ]),
])

@app.callback(
    Output('slct_column', 'options'),
    Output('slct_column', 'value'),
    Input('slct_type2', 'value'),

)
def gens_or_rec(slct):
    generators = [g for g in df.columns if g.startswith('Gen')]
    receivers = [r for r in df.columns if r.startswith('Rec')]
    ops = [{'label':i, 'value':i} for i in  eval(slct) ]
    return ops, eval(slct)[0]

@app.callback(
    Output(component_id='heatmap', component_property='figure'),
    Input(component_id='slct_month', component_property='value'),
    Input('slct_chart_type', 'value'),
    Input('slct_column', 'value'),
)
def heatmap(slct_month, chart_type, column):
    temp = df.copy()[['Date/time', column]]

    temp['time'] = temp['Date/time'].dt.time
    temp_m = temp[temp['Date/time'].dt.month_name() == slct_month]
    temp_m['day'] = temp_m['Date/time'].dt.day_name() if chart_type == 'day_name' else temp_m['Date/time'].dt.day
    # print(temp['Date/time'].dt.weeks().value_counts())



    
    temp_m = temp_m.drop(columns= 'Date/time')
    fig = go.Figure(data = [go.Heatmap(
        x = temp_m.day,
        y = temp_m.time.apply(lambda x: ':'.join(str(x).split(':')[:2])),
        z = temp_m[column]
    )])
    fig.update_layout(title='Graph Title', height=700)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, threaded= True)
