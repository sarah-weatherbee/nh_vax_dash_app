import dash
from dash import html, Dash, dcc, Input, Output, State
from dash_bootstrap_components.themes import BOOTSTRAP
import dash_bootstrap_components as dbc
# from dash_bootstrap_templates import load_figure_template

import plotly.graph_objects as go
import plotly.express as px
from plotly.express import data
import pandas as pd


nh_facil_level = pd.read_csv(
    'data/data_post_proc/nh_latest_sub_end_22_y.csv', sep='|', parse_dates=True)

dict = {'county': 'County',
        'provider_state': 'State',
         'provider_city': 'City',
        'provider_name': 'Facility Name',
        'rev_pct_res_utd_c19_vax': 'Residents up-to-date with COVID-19 Vaccinations',
        'rev_pct_hcp_utd_c19_vax': 'Healthcare Providers up-to-date with COVID-19 Vaccinations'}

nh_facil_level.rename(columns=dict, inplace=True)
nh_facil_level['Facility Name'] = nh_facil_level['Facility Name'].fillna('-')
nh_facil_level['City'] = nh_facil_level['City'].fillna('-')
nh_facil_level = nh_facil_level.sort_values(
    ['State', 'County', 'City', 'Facility Name'])

state_options = nh_facil_level['State'].sort_values().unique()
county_options = nh_facil_level['County'].sort_values().unique()
city_options = nh_facil_level['City'].sort_values().unique()
facility_options = nh_facil_level['Facility Name'].sort_values().unique()

state_to_city =nh_facil_level.groupby('State')['City'].agg(list).to_dict()
city_to_fac = nh_facil_level.groupby('City')['Facility Name'].agg(list).to_dict()
state_to_fac = nh_facil_level.groupby('State')['Facility Name'].agg(list).to_dict()

# nh_facil_level = nh_facil_level.loc[(nh_facil_level['County'] == 'Nelson') & (
#     nh_facil_level['State'] == 'KY') & (nh_facil_level['Facility Name']=='LANDMARK OF BARDSTOWN REHABILITATION AND NURSING')]


# Initialise the app
app = Dash()


# Creates a list of dictionaries, which have the keys 'label' and 'value'.
def get_options(list_facs):
    dict_list = []
    for i in list_facs:
        dict_list.append({'label': i, 'value': i})
    return dict_list

# create dropdowns
state_dropdown = dcc.Dropdown(id='state-dropdown',
                            options=[{'label': i,'value': i} for i in nh_facil_level['State'].unique()],
                            value='KY',
                            placeholder='Type a state abbreviation or select from list',
                            clearable=False
                            )

city_dropdown = dcc.Dropdown(id='city-dropdown',
                            options=[{'label': i,'value': i} for i  in nh_facil_level['City'].unique()],
                            value=[],
                            placeholder='Type a city name or select from list',
                            clearable=False
                            )

fac_dropdown = dcc.Dropdown(id='fac-dropdown',
                            options=[{'label': i,'value': i} for i in nh_facil_level['Facility Name'].unique()],
                            value=[],
                            placeholder='Type a facility name or select from list',
                            clearable=False
                            )


# Define the app layout
app.layout = html.Div(children=[
    html.H1(children='COVID-19 vaccination rates in Nursing Homes: Staff and residents',
            style={
                'textAlign': 'left',
                'color': 'black',
                'font-family': 'sans-serif',
                'margin': '2rem'}),
    state_dropdown,
    city_dropdown,
    fac_dropdown,
    html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
    html.Div(id='output-state', children =[
    dcc.Loading(
        id="loading-1",
        children=[dcc.Graph(id='ts-c19vax-graph')],
        type='circle')
    ])
])


# callback to update the city dropdoown options from state dropdown options
@app.callback(
        Output('ts-c19vax-graph', 'figure'),
        Input('submit-button-state', 'n_clicks'),
        State('fac-dropdown', 'value'),
        State('city-dropdown', 'value'),
        State('state-dropdown', 'value'),
        )

def update_graph(selected_fac,selected_city, selected_state):
    filtered_nh_data = nh_facil_level[nh_facil_level['Facility Name']
                                      == selected_fac]
    ts_c19vax_fig = px.line(filtered_nh_data,
                            x='week_ending', y=['Healthcare Providers up-to-date with COVID-19 Vaccinations',
                                                'Residents up-to-date with COVID-19 Vaccinations'],
                            # plot_bgcolor='rgba(0,0,0,0)',
                            # paper_bgcolor='rgba(0,0,0,0)',
                            # font_color='white',
                            # xaxis_showgrid=False,
                            # yaxis_showgrid=False,
                            # yaxis_title='Percent Vaccinated',
                            # xaxis_title='',
                            # legend_title='',
                            title=f'Facility: {selected_fac}')
    return ts_c19vax_fig

def set_city_options(selected_state): 
        if len(selected_state) > 0:
             selected_states = selected_state
             return [{'label': i, 'value': i} for i in sorted(set(nh_facil_level['City'].loc[nh_facil_level['State']==selected_states]))]
        else:
            selected_states = []
            return [{'label': i, 'value': i} for i in sorted(set(nh_facil_level['City'].loc[nh_facil_level['State']==selected_states]))]

# callback to update the facility dropdoown options from city dropdown options
@app.callback(
        Output('fac-dropdown','options'),
        [
        Input('city-dropdown','value'),
         ])          

def set_fac_options(selected_city):
        if len(selected_city) > 0:
             selected_cities = selected_city
             return [{'label': i, 'value': i} for i in sorted(set(nh_facil_level['Facility Name'].loc[nh_facil_level['City']==selected_cities]))]
        else:
            selected_cities = []
            return [{'label': i, 'value': i} for i in sorted(set(nh_facil_level['Facility Name'].loc[nh_facil_level['City']==selected_cities]))]



# callback to update the figure for the graph
@app.callback(
    Output('ts-c19vax-graph', 'figure'),
    [Input('fac-dropdown', 'value')]
)
def update_graph(selected_fac):
    filtered_nh_data = nh_facil_level[nh_facil_level['Facility Name']
                                      == selected_fac]
    ts_c19vax_fig = px.line(filtered_nh_data,
                            x='week_ending', y=['Healthcare Providers up-to-date with COVID-19 Vaccinations',
                                                'Residents up-to-date with COVID-19 Vaccinations'],
                            # plot_bgcolor='rgba(0,0,0,0)',
                            # paper_bgcolor='rgba(0,0,0,0)',
                            # font_color='white',
                            # xaxis_showgrid=False,
                            # yaxis_showgrid=False,
                            # yaxis_title='Percent Vaccinated',
                            # xaxis_title='',
                            # legend_title='',
                            title=f'Facility: {selected_fac}')
    return ts_c19vax_fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
