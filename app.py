import dash
from dash import html, Dash, dcc, Input, Output, State
from dash_bootstrap_components.themes import BOOTSTRAP
import plotly.graph_objects as go
import plotly.express as px
from plotly.express import data
import pandas as pd


nh_facil_level = pd.read_csv(
    'data/data_post_proc/nh_latest_sub_end_22_y.csv', sep='|', parse_dates=True)

dict = {'county': 'County',
        'provider_state': 'State',
        'provider_name': 'Facility Name',
        'rev_pct_res_utd_c19_vax': 'Residents up-to-date with COVID-19 Vaccinations',
        'rev_pct_hcp_utd_c19_vax': 'Healthcare Providers up-to-date with COVID-19 Vaccinations'}

nh_facil_level.rename(columns=dict, inplace=True)
nh_facil_level['Facility Name'] = nh_facil_level['Facility Name'].fillna('-')
nh_facil_level = nh_facil_level.sort_values(
    ['State', 'County', 'Facility Name'])


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


fac_dropdown = dcc.Dropdown(id='fac-dropdown',
                            options=get_options(
                                nh_facil_level['Facility Name'].unique()),

                            #value=nh_facil_level['Facility Name'].sort_values()[0],
                            value='LANDMARK OF BARDSTOWN REHABILITATION AND NURSING',
                            placeholder='Start typing a facility name or select from list',
                            # multi=True
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
    fac_dropdown,
    dcc.Loading(
        id="loading-1",
        children=[dcc.Graph(id='ts-c19vax-graph')],
        type='circle')
])


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
                            title=f'COVID-19 Vaccination Rates for Residents and Healthcare Providers: {selected_fac}')
    return ts_c19vax_fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
