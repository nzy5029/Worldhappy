# import
# essential imports
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input

import plotly.express as px
import math
from dash import no_update

import pandas as pd
import numpy as np
import json


# read primary data
df_country = pd.read_csv('world-happiness-report.csv')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# this is new
available_indicators = ['Life Ladder',	'Log GDP per capita',	'Social support', 'Healthy life expectancy at birth', 'Freedom to make life choices', 'Generosity']

df_country_code = pd.read_csv('code.csv')
df_country_code['Code3'] = df_country_code['Code3'].apply(lambda s : s.replace('"', ""))
# a helper function
def get_country_name(country_code):
  one_row = df_country_code[df_country_code['Code3'].str.strip() == country_code]
  if not one_row.empty:
    # display(one_row)
    return one_row['Country'].values[0]
  else:
    return ''

# end

## Uncomment the following line for running in a webbrowser
app = dash.Dash(__name__)

app.layout = html.Div([
    # first row: header
    html.H4('A World happiness Dashboard', style={'textAlign':'centre'}),

    # second row: two drop-downs and radio-boxes.
    html.Div([
      html.Div([
        dcc.Dropdown(
          id='xaxis-column',
          options=[{'label': i, 'value': i} for i in available_indicators],
          value='Life Ladder'
        ),

        dcc.RadioItems(
          id='xaxis-type',
          options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
          value='Linear',
          labelStyle={'display': 'inline-block'}
        )
      ], className='four columns'),


      html.Div([
        dcc.Dropdown(
          id='yaxis-column',
          options=[{'label': i, 'value': i} for i in available_indicators],
          value='Generosity'
        ),
        dcc.RadioItems(
          id='yaxis-type',
          options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
          value='Linear',
          labelStyle={'display': 'inline-block'}
        )
      ], className='four columns')

    ], className='row'),


    # third row:
    html.Div([

      # first item: scatter plot
      html.Div([

        # add scatter plot
        dcc.Graph(
          id='scatter-graph',
          figure=px.scatter() # we'll create one inside update_figure function
        ),

        # add slider
        dcc.Slider(
          id='year-slider',
          min=df_country['year'].min(),
          max=df_country['year'].max(),
          value=df_country['year'].min(),
          marks={str(year): str(year) for year in df_country['year'].unique()},
          step=None

        )

      ], className='seven columns'),

      # second item: one blank column
      html.Div([
          html.Div(id='empty-div', children='')
      ], className='one column'),

      # third item: bar chart
      html.Div([
        dcc.Graph(
          id='bar-chart',
          figure=px.bar()
        )
      ], className='five columns')

    ], className = 'row'),

    # fourth row: colored map
    #https://plotly.com/python/maps/
    html.Div([
        dcc.Graph(
          id='colored-map',
          figure=px.scatter_geo() # px.choropleth scatter_geo
           # we'll create one inside update_figure function
        )
    ], className = 'row'),

    # fifth row
    html.Div([
      html.Div([
          dcc.Graph(
            id='line-graph',
            figure=px.line()
             # we'll create one inside update_figure function
          )
      ], className = 'seven columns'),

        html.Div([
          html.H3('Debug'),
          #html.Br(),
          html.P(id='output_text_1', children='Total:'),
          html.P(id='output_text_2', children='Details:'),
          html.P(id='output_text_3', children='Details:'),
          html.P(id='output_text_4', children='Details:')
        ], className = 'five columns')

    ], className = 'row')

])

# callback definition
@app.callback(
  Output('scatter-graph', 'figure'),
  Output('output_text_1', 'children'), #debug
  Input('year-slider', 'value'),
  Input('xaxis-column', 'value'),
  Input('yaxis-column', 'value'),
  Input('xaxis-type', 'value'),
  Input('yaxis-type', 'value'),
)

# first callback function
def update_graph(selected_year, xaxis_column_name, yaxis_column_name, xaxis_type, yaxis_type):
  # print all input params
  debug_params ='Input: {0}, {1}, {2}, {3}, {4}'.format(selected_year, xaxis_column_name, yaxis_column_name, xaxis_type, yaxis_type)

  # filter data frame by year
  filtered_df = df_country[df_country.year == selected_year]

  fig_scatter = px.scatter(
    data_frame = filtered_df,
    x=str(xaxis_column_name),
    y=str(yaxis_column_name),
    hover_name="Country name",
    color="Country name",
    size = 'Life Ladder',
    size_max=35,
    ### this is new --> adding a customdata that would be picked up during mouse hover
    custom_data = ["Code"],
    title= "{0}  vs {1} of Countries".format(xaxis_column_name, yaxis_column_name)
  )

  fig_scatter.update_layout(transition_duration=500)

  fig_scatter.update_xaxes(
    title=xaxis_column_name,
    type='linear' if xaxis_type == 'Linear' else 'log'
  )

  fig_scatter.update_yaxes(
    title=yaxis_column_name,
    type='linear' if yaxis_type == 'Linear' else 'log'
  )

  # return
  return fig_scatter, debug_params
# end update_

# second callback
@app.callback(
  Output('bar-chart', 'figure'),
  Output('output_text_2', 'children'), #debug
  Input('scatter-graph', 'clickData'), # hoverData
  Input('xaxis-column', 'value'),
  Input('xaxis-type', 'value')
)
# second callback definition
def update_bar_graph(clickData, xaxis_column_name, axis_type):
  if not clickData:
    return no_update

  debug_params ='Input: {0}, {1}, {2}'.format(clickData['points'], xaxis_column_name, axis_type)

  country_code = str(clickData['points'][0]['customdata'][0])

  filtered_df = df_country[df_country['Code'] == country_code]

  fig_bar = px.bar(
    data_frame = filtered_df,
    x="year",
    y=str(xaxis_column_name),
    title= "{0} of {1} in different year".format(xaxis_column_name, get_country_name(country_code))
  )

  fig_bar.update_yaxes(
    title=xaxis_column_name,
    type='linear' if axis_type == 'Linear' else 'log'
  )

  # return
  return fig_bar, debug_params
# end

# third callback definition
@app.callback(
  Output('colored-map', 'figure'),
  Output('output_text_3', 'children'), #debug
  Input('year-slider', 'value'),
  Input('scatter-graph', 'clickData'), #clickData hoverData
  Input('xaxis-column', 'value')
)

# third callback function
def update_map(selected_year, clickData, xaxis_column_name):

  # return if not hovering
  if not clickData:
      return no_update

  # print all input params
  debug_params ='Input: {0} {1} {2}'.format(selected_year, clickData['points'], xaxis_column_name)
  country_code = str(clickData['points'][0]['customdata'][0])


  # filter data frame by year
  filtered_df = df_country[df_country.year == selected_year].copy()
  filtered_df['color'] = 'Other Countries'
  filtered_df.loc[filtered_df['Code'] == country_code, 'color'] = 'Selected Country'

  #px.choropleth scatter_geo
  # fig_map = px.choropleth(
  #   data_frame = filtered_df,
  #   locations='iso_alpha', # very important key
  #   color = str(xaxis_column_name),
  #   hover_name='country',
  #   width = 1200,
  #   height = 600,
  #   title= "Life Expectance in {0}".format(selected_year)
  # )

  fig_map = px.scatter_geo(
    data_frame = filtered_df,
    locations='Code', # very important key
    size = str(xaxis_column_name),
    hover_name='Country name',
    color = 'color',
    width = 1100,
    height = 600,
    title= "Global happiness in {0}".format(selected_year)
  )


  #fig_map.update_geos(fitbounds="locations")
  # link: https://plotly.com/python/map-configuration/
  fig_map.update_geos(
    resolution=50,
    showcountries=True,
    countrycolor="RebeccaPurple",
    # showcoastlines=True,
    # coastlinecolor="RebeccaPurple",
    showland=True,
    landcolor="White",
    showocean=True,
    oceancolor="LightBlue",
    showlakes=True,
    lakecolor="Blue",
    showrivers=True,
    rivercolor="Blue"
)

  # return
  return fig_map, debug_params
# end callback

# fourth callback definition
@app.callback(
  Output('line-graph', 'figure'),
  Output('output_text_4', 'children'),
  Input('colored-map', 'clickData'), #hoverData
  Input('xaxis-column', 'value'),
  Input('xaxis-type', 'value')
)

def update_bar_graph_from_map(clickData, xaxis_column_name, axis_type): #hoverData
  if not clickData:
    return no_update

  debug_params ='Input: {0}, {1}, {2}'.format(clickData['points'], xaxis_column_name, axis_type)

  country_code = str(clickData['points'][0]['location'])

  filtered_df = df_country[df_country['Code'] == country_code]

  fig_bar = px.line(
    data_frame = filtered_df,
    x="year",
    y=str(xaxis_column_name),
    title= "{0} of {1} in different year".format(xaxis_column_name, get_country_name(country_code))
  )

  fig_bar.update_yaxes(
    title=xaxis_column_name,
    type='linear' if axis_type == 'Linear' else 'log'
  )

  return fig_bar, debug_params

# uncomment the following lines to run in Browser via command line/terminal
if __name__ == '__main__':
 app.run_server(debug=True)
