import dash
from dash import html, Dash, dcc, Input, Output, State
from dash_bootstrap_components.themes import BOOTSTRAP
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template



import plotly.graph_objects as go
import plotly.express as px
from plotly.express import data
import pandas as pd

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"



nh_facil_level = pd.read_csv(
    'data/data_post_proc/nh_latest_sub_2_y.csv', sep='|', parse_dates=True, low_memory=False)

names_dict = {
    'county': 'County',
    'provider_state': 'State',
    'provider_city': 'City',
    # 'provider_name': 'Facility Name',
    # 'rev_pct_res_utd_c19_vax': 'Residents up-to-date with COVID-19 Vaccinations',
    # 'rev_pct_hcp_utd_c19_vax': 'Healthcare Providers up-to-date with COVID-19 Vaccinations'
}

nh_facil_level.rename(columns=names_dict, inplace=True)
nh_facil_level['provider_name'] = nh_facil_level['provider_name'].fillna('-')
nh_facil_level['City'] = nh_facil_level['City'].fillna('-')
nh_facil_level = nh_facil_level.sort_values(
    ['State', 'County', 'City', 'provider_name'])

# state_options = nh_facil_level['State'].sort_values().unique()
# county_options = nh_facil_level['County'].sort_values().unique()
# city_options = nh_facil_level['City'].sort_values().unique()
# facility_options = nh_facil_level['provider_name'].sort_values().unique()

# state_to_city = nh_facil_level.groupby('State')['City'].agg(list).to_dict()
# city_to_fac = nh_facil_level.groupby(
#     'City')['provider_name'].agg(list).to_dict()
# state_to_fac = nh_facil_level.groupby(
#     'State')['provider_name'].agg(list).to_dict()

# nh_facil_level = nh_facil_level.loc[(nh_facil_level['County'] == 'Nelson') & (
#     nh_facil_level['State'] == 'KY') & (nh_facil_level['Facility Name']=='LANDMARK OF BARDSTOWN REHABILITATION AND NURSING')]

# Initialise the app
app = Dash(external_stylesheets=[dbc.themes.LUX, dbc_css])


# Creates a list of dictionaries, which have the keys 'label' and 'value'.
# def get_options(list_facs):
#     dict_list = []
#     for i in list_facs:
#         dict_list.append({'label': i, 'value': i})
#     return dict_list


# create dropdowns
state_dropdown = dcc.Dropdown(id='state-dropdown',
                              options=[{'label': i, 'value': i}
                                       for i in nh_facil_level['State'].unique()],
                              value=nh_facil_level['State'].unique()[0],
                              placeholder='Type a state abbreviation or select from list',
                              clearable=False
                              )

city_dropdown = dcc.Dropdown(id='city-dropdown',
                             options=[{'label': i, 'value': i}
                                      for i in nh_facil_level['City'].unique()],
                             value=nh_facil_level['City'].unique()[0],
                             placeholder='Type a city name or select from list',
                             clearable=False
                             )

fac_dropdown = dcc.Dropdown(id='fac-dropdown',
                            options=[{'label': i, 'value': i}
                                     for i in nh_facil_level['provider_name'].unique()],
                            value=nh_facil_level['provider_name'].unique()[0],
                            placeholder='Type a facility name or select from list',
                            clearable=False
                            )
fig = go.Figure()

def blank_figure():
    fig = go.Figure(go.Scatter(x=[], y = []))
    fig.update_layout(template = None)
    fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
    fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)
    
    return fig

# Define the app layout
app.layout = html.Div(children=[
    html.H1(children='COVID-19 vaccination rates in Nursing Homes: Staff and residents',
            style={
                'textAlign': 'left',
                'color': 'black',
                'font-family': 'sans-serif',
                'margin': '2rem'}),
    html.Div(children=[
        state_dropdown,
        city_dropdown,
        fac_dropdown,
    ], style={'textAlign': 'left',
              'color': 'black',
              'font-family': 'sans-serif',
              'margin': '2rem'

              }),
    dcc.Loading(
        id="loading-2",
        type='circle',
        children=[
                dcc.Graph(id='utd_hcp_res_ts_fig',figure=blank_figure()),
                dcc.Graph(id='at_hcp_res_ts_fig',figure=blank_figure()),

                ]
    )
])


# callback to update the city dropdown options from state dropdown options
@app.callback(
    Output('city-dropdown', 'options'),
    [Input('state-dropdown', 'value')])
def set_city_options(selected_state):
    if len(selected_state) > 0:
        selected_states = selected_state
        return [{'label': i, 'value': i} for i in sorted(set(nh_facil_level['City'].loc[nh_facil_level['State'] == selected_states]))]
    else:
        selected_states = []
        return [{'label': i, 'value': i} for i in sorted(set(nh_facil_level['City'].loc[nh_facil_level['State'] == selected_states]))]


@app.callback(
    Output('city-dropdown', 'value'),
    [Input('city-dropdown', 'options')])
def set_city_value(available_cities):
    return available_cities[0]['value']


# callback to update the facility dropdown options from city dropdown options
@app.callback(
    Output('fac-dropdown', 'options'),
    [Input('city-dropdown', 'value')])
def set_fac_options(selected_city):
    if len(selected_city) > 0:
        selected_cities = selected_city
        return [{'label': i, 'value': i} for i in sorted(set(nh_facil_level['provider_name'].loc[nh_facil_level['City'] == selected_cities]))]
    else:
        selected_cities = []
        return [{'label': i, 'value': i} for i in sorted(set(nh_facil_level['provider_name'].loc[nh_facil_level['City'] == selected_cities]))]


@app.callback(
    Output('fac-dropdown', 'value'),
    [Input('fac-dropdown', 'options')])
def set_fac_value(available_facs):
    return available_facs[0]['value']

# callback to update the figure for the graph

@app.callback(
    [Output('utd_hcp_res_ts_fig', 'figure'),
    Output('at_hcp_res_ts_fig', 'figure')],
    [Input('fac-dropdown', 'value')]
)
def update_graph(selected_fac):
    utd_ts_data = nh_facil_level[(
        nh_facil_level['provider_name'] == selected_fac) & (nh_facil_level['week_ending']>'2022-07-03')]

    utd_hcp_res_ts_fig = go.Figure()

    utd_hcp_res_ts_fig.add_trace(
        go.Scatter(
            x=utd_ts_data['week_ending'],
            y=utd_ts_data['rev_pct_hcp_utd_c19_vax'],
            name="Healthcare Staff",
            mode='lines',
            text='<b>Week Ending Date:</b> ' +
            utd_ts_data['week_ending']+'<br><b>Healthcare staff up-to-date</b> ' +
            utd_ts_data['rev_pct_hcp_utd_c19_vax'].round().astype(
                str)+'%',
            hoverinfo='text',
            line=dict(color='#727ff2', width=3)
        ),
    )

    utd_hcp_res_ts_fig.add_trace(
        go.Scatter(
            x=utd_ts_data['week_ending'],
            y=utd_ts_data['rev_pct_res_utd_c19_vax'],
            name="Residents",
            mode='lines',
            text='<b>Week Ending Date:</b> ' +
            utd_ts_data['week_ending']+'<br><b>Residents up-to-date</b> ' +
            utd_ts_data['rev_pct_res_utd_c19_vax'].round().astype(
                str)+'%',
            hoverinfo='text',
            line=dict(color='#b0841c', width=3)
        ),
    )

    at_hcp_res_ts_fig = go.Figure()

    at_hcp_res_ts_fig.add_trace(
        go.Scatter(
            x=utd_ts_data['week_ending'],
            y=utd_ts_data['rev_pct_hcp_anytime_c19_vax'],
            name="Healthcare Staff",
            mode='lines',
            text='<b>Week Ending Date:</b> ' +
            utd_ts_data['week_ending']+'<br><b>Healthcare staff Anytime</b> ' +
            utd_ts_data['rev_pct_hcp_anytime_c19_vax'].round().astype(
                str)+'%',
            hoverinfo='text',
            line=dict(color='#727ff2', width=3)
        ),
    )

    at_hcp_res_ts_fig.add_trace(
        go.Scatter(
            x=utd_ts_data['week_ending'],
            y=utd_ts_data['rev_pct_res_anytime_c19_vax'],
            name="Residents",
            mode='lines',
            text='<b>Week Ending Date:</b> ' +
            utd_ts_data['week_ending']+'<br><b>Residents Anytime</b> ' +
            utd_ts_data['rev_pct_res_anytime_c19_vax'].round().astype(
                str)+'%',
            hoverinfo='text',
            line=dict(color='#b0841c', width=3)
        ),
    )

    # fig.add_annotation(text='<b>Residents</b>',
    #                    x=filtered_nh_data['week_ending'].iat[-1], y=filtered_nh_data['rev_pct_res_utd_c19_vax'].iat[-1],
    #                    ax=70, ay=30,
    #                    xshift=50,
    #                    font=dict(
    #                        family="sans-serif, bold",
    #                        size=14,
    #                        color='#b0841c'
    #                    ),
    #                    showarrow=False,
    #                    align='left')

    # fig.add_annotation(text='<b>Healthcare<br>Staff</b>',
    #                    x=filtered_nh_data['week_ending'].iat[-1], y=filtered_nh_data['rev_pct_hcp_utd_c19_vax'].iat[-1],
    #                    ax=0, ay=0,
    #                    xshift=10,
    #                    font=dict(
    #                        family="sans-serif, bold",
    #                        size=14,
    #                        color='#727ff2'
    #                    ),
    #                    showarrow=False,
    #                    align='left')

    utd_hcp_res_ts_fig.update_layout(
        showlegend=True,
        legend={'title_text': ''},
        plot_bgcolor='#ffffff',
        yaxis_title='Percent',
        xaxis_title='Week Ending Date'
    )

    at_hcp_res_ts_fig.update_layout(
        showlegend=True,
        legend={'title_text': ''},
        plot_bgcolor='#ffffff',
        yaxis_title='Percent',
        xaxis_title='Week Ending Date'
    )

    utd_hcp_res_ts_fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='LightGray'
    )
    at_hcp_res_ts_fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='LightGray'
    )

    return utd_hcp_res_ts_fig, at_hcp_res_ts_fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
