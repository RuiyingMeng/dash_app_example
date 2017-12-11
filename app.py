
# coding: utf-8

# # Final Project
# 
# Create a Dashboard taking data from [Eurostat, GDP and main components (output, expenditure and income)](http://ec.europa.eu/eurostat/web/products-datasets/-/nama_10_gdp). 
# The dashboard will have two graphs: 
# 
# * The first one will be a scatterplot with two DropDown boxes for the different indicators. It will have also a slide for the different years in the data. 
# * The other graph will be a line chart with two DropDown boxes, one for the country and the other for selecting one of the indicators. (hint use Scatter object using mode = 'lines' [(more here)](https://plot.ly/python/line-charts/) 

# In[1]:

import pandas as pd

df = pd.read_csv('nama_10_gdp.tsv',sep=r'[,\t]',engine='python')
df.rename(columns = {'geo\\time':'geo'}, inplace = True)
df.rename(columns = {column: column.strip() for column in df.columns}, inplace = True) # delete space in columns' name
df.head()


# In[3]:

# Use regular expression to clean the data i.e. delete charts behind numbers. It will take several minutes
# not necessary to run. it doesn't influence the graphs below

#import re
#for row in range(len(df)):
#    for column in range(3, len(df.columns)):
#        df.iloc[row,column] = re.sub(pattern = "\s[a-z]+", repl = "", string = df.iloc[row, column])
#df.head()


# In[5]:

# Code for dashboard
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

#app = dash.Dash()
app = dash.Dash(__name__)
server = app.server
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})


available_units = df['unit'].unique()            # available options for "unit of measure"
available_na_items = df['na_item'].unique()      # available options for "national accounts indicator"
available_countries = df['geo'].unique()        # available countries

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in available_na_items],
                value='D21'
            ),
            dcc.RadioItems(
                id='xaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '30%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='yaxis-column',
                options=[{'label': i, 'value': i} for i in available_na_items],
                value='B1G'
            ),
            dcc.RadioItems(
                id='yaxis-type',
                options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
                value='Linear',
                labelStyle={'display': 'inline-block'}
            )
        ], style={'width': '30%', 'float': 'middle', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Dropdown(
                id='unit-of-measure',
                options=[{'label': i, 'value': i} for i in available_units],
                value='CLV05_MEUR'
            )
        ], style={'width': '30%',  'float': 'right', 'display': 'inline-block'})
    ]),
    
    dcc.Graph(id='Eurostat'),
    
    dcc.Slider(
        id = 'year-slider',
        min = 1975,
        max = 2016,
        value = 2016,
        step = None,
        marks = {str(year): str(year) for year in range(1975,2017)}
    ),
    
    html.Hr(),   ### dividing line, above is scatter chart, below is line chart
    
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='country',
                options=[{'label': i, 'value': i} for i in available_countries], 
                value= 'AL'
            )
        ], style={'width': '30%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='na-item',
                options=[{'label': i, 'value': i} for i in available_na_items],
                value='B1G'
            )
        ], style={'width': '30%', 'float': 'middle', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Dropdown(id='unit-of-measure-lc') # for line chart 
        ], style={'width': '30%',  'float': 'right', 'display': 'inline-block'})
    ]),
    
    dcc.Graph(id='country_stat')
])

# update scatter chart
@app.callback(
    dash.dependencies.Output('Eurostat', 'figure'),
    [dash.dependencies.Input('xaxis-column', 'value'),
     dash.dependencies.Input('yaxis-column', 'value'),
     dash.dependencies.Input('xaxis-type', 'value'),
     dash.dependencies.Input('yaxis-type', 'value'),
     dash.dependencies.Input('unit-of-measure', 'value'),
     dash.dependencies.Input('year-slider', 'value')])
def update_figure(xaxis_column_value, yaxis_column_value, xaxis_type, yaxis_type,
                  unit_of_measure,year_value):
    return {
        'data': [go.Scatter(
            x=df[(df['na_item'] == xaxis_column_value) & (df['unit'] == unit_of_measure)][str(year_value)],
            y=df[(df['na_item'] == yaxis_column_value) & (df['unit'] == unit_of_measure)][str(year_value)],
            text=df[df['na_item'] == xaxis_column_value]['geo'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': go.Layout(
            xaxis={
                'title': xaxis_column_value,
                'type': 'linear' if xaxis_type == 'Linear' else 'log'
            },
            yaxis={
                'title': yaxis_column_value,
                'type': 'linear' if yaxis_type == 'Linear' else 'log'
            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }

### below are for line chart

# Change unit_of_measure options according to the selected na_item and selected country
# Because not all unit_of_measure options are available for each combination of na_item and country
@app.callback(
    dash.dependencies.Output('unit-of-measure-lc', 'options'),
    [dash.dependencies.Input('na-item', 'value')],
    [dash.dependencies.State('country', 'value')] 
)
# set unit_of_measure options
def set_unit(na_item_value, country_value):    
    
    available_units = [{'label': i, 'value': i} for i in df[(df['geo'] == country_value) & (df['na_item']== na_item_value)]['unit'].unique()]
    
    # if available_units is not null, return it; else no available data 
    # Note: It may still get error information when running codes below.(e.g.for na_item P61 and country LI)
    if available_units:
        return available_units
    else:
        print("No available data for selected na_item {} and country {}!".format(na_item_value, country_value))

# set unit_of_measure values
@app.callback(
    dash.dependencies.Output('unit-of-measure-lc', 'value'),
    [dash.dependencies.Input('unit-of-measure-lc', 'options')])
def set_unit_value(available_units):
    return available_units[0]['value']

# update line chart
@app.callback(
    dash.dependencies.Output('country_stat', 'figure'),
    [dash.dependencies.Input('country', 'value'),
     dash.dependencies.Input('na-item', 'value'),
     dash.dependencies.Input('unit-of-measure-lc', 'value')
    ])
def update_line_chart(country_value, na_item_value, unit_of_measure):   
    return {
        'data': [go.Scatter(
            x = [str(i) for i in range(1975, 2017)],
            y = df[(df['geo'] == country_value) & (df['na_item']== na_item_value)&(df['unit'] == unit_of_measure)].iloc[0,3:][::-1],
            text = country_value,
            mode='lines',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': go.Layout(
            xaxis={'title': 'year'},
            yaxis={'title': na_item_value},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }

if __name__ == '__main__':
    app.run_server()


# In[ ]:



