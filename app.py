import plotly.figure_factory as ff
import datetime
from datetime import datetime
import pandas as pd
from plotly.express import data
import plotly.express as px
import plotly.graph_objects as go
from dash_bootstrap_templates import load_figure_template
import dash
from dash import html, Dash, dcc, Input, Output, State
from dash_bootstrap_components.themes import BOOTSTRAP
import dash_bootstrap_components as dbc
import plotly.io as pio
pio.templates


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
# convert week_ending col to datetime format
nh_facil_level['week_ending'] = pd.to_datetime(
    nh_facil_level['week_ending'], format='%Y/%m/%d').dt.strftime('%m-%d-%Y')

nh_facil_level.rename(columns=names_dict, inplace=True)
nh_facil_level['provider_name'] = nh_facil_level['provider_name'].fillna('-')
nh_facil_level['County'] = nh_facil_level['County'].fillna('-')
nh_facil_level['City'] = nh_facil_level['City'].fillna('-')
nh_facil_level = nh_facil_level.sort_values(
    ['State', 'County', 'City', 'provider_name'])

# make a dataframe to get the values of 'rev_pct_hcp_utd_c19_vax' for each location at the latest week ending
ltnn_rev_pct_hcp_utd_c19_vax = (
    nh_facil_level.sort_values('week_ending', ascending=False)
    .groupby('provider_name')
    .apply(lambda x: x[x['rev_pct_hcp_utd_c19_vax'].notnull()].iloc[0] if x['rev_pct_hcp_utd_c19_vax'].notnull().any() else x.iloc[0])
    .reset_index(drop=True)
    .loc[:, ['provider_name', 'week_ending', 'rev_pct_hcp_utd_c19_vax']]
)

# Set app theme
app = Dash(external_stylesheets=[dbc.themes.LUX])


# create dropdowns
state_dropdown = dcc.Dropdown(id='state-dropdown',
                              options=[{'label': i, 'value': i}
                                       for i in nh_facil_level['State'].unique()],
                              value=nh_facil_level['State'].unique()[0],
                              placeholder='Type a state abbreviation or select from list',
                              clearable=False,
                              style={
                                  #'border-style': 'ridge',
                                  'border-radius': '30px',
                                  'border-color': '#00000020',
                                  'height': '5rem',
                                  

                                  'margin-left': '3.5rem',
                                  'margin-right': '7rem'
                              }
                              )

city_dropdown = dcc.Dropdown(id='city-dropdown',
                             options=[{'label': i, 'value': i}
                                      for i in nh_facil_level['City'].unique()],
                             value=nh_facil_level['City'].unique()[0],
                             placeholder='Type a city name or select from list',
                             clearable=False,
                             style={
                                 #'border-style': 'ridge',
                                 'border-radius': '30px',
                                 'border-color': '#00000020',
                                 'height': '5rem',
                                 'margin-left': '3.5rem',
                                 'margin-right': '7rem',
                                 
                             }
                             )

fac_dropdown = dcc.Dropdown(id='fac-dropdown',
                            options=[{'label': i, 'value': i}
                                     for i in nh_facil_level['provider_name'].unique()],
                            value=nh_facil_level['provider_name'].unique()[0],
                            placeholder='Type a facility name or select from list',
                            clearable=False,
                            style={
                                #'border-style': 'ridge',
                                'border-radius': '30px',
                                'border-color': '#00000020',
                                'height': '5rem',
                                'margin-left': '3.5rem',
                                'margin-right': '7rem'
                            }
                            )
fig = go.Figure()


def blank_figure():
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template="none")
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    return fig


def blank_cards():
    card = dbc.Card(dbc.CardBody(
        [
                    html.H5("")
                    ]
    )
    )
    return card


# Define the app layout
app.layout = html.Div(children=[
    html.H1(children='COVID-19 vaccination rates in U.S. nursing homes',
            style={
                'text-align': 'center',
                'background-color': '#55595c',
                'color': '#ffffff',
                'title-font-family': 'sans-serif',
                'font-family': 'sans-serif',
                'font-size': '30px',
                'padding': '4rem',
                'margin-bottom': '6rem'}
            ),
    html.Div(children=[
        html.Div(children=[
            html.H6("1. Select a state",
                    style={'font-weight': 'bold',
                           'font-style': 'italic',
                           'margin-left': '4rem',
                           'margin-right': '5rem'
                           }
                    ),
            state_dropdown],
        ),
        html.Br(),
        html.Div(children=[
            html.H6("2. Select a city",
                    style={
                        'font-weight': 'bold',
                        'font-style': 'italic',
                        'margin-left': '4rem',
                        'margin-right': '5rem'
                    }),
            city_dropdown],
        ),
        html.Br(),
        html.Div(children=[
            html.H6("3. Select a nursing home",
                    style={
                        'font-weight': 'bold',
                        'font-style': 'italic',
                         'margin-left': '4rem',
                        'margin-right': '5rem'
                    }),
            fac_dropdown],
        )
    ],
        style={'textAlign': 'left',
               'color': '#55595c',
               'title-font-family': 'sans-serif',
               'font-family': 'sans-serif',
               'margin': '3rem',
               }
    ),

    dcc.Loading(
        id="loading-1",
        type='circle',
        children=[

            dbc.Row(children=[
                dbc.Row(id='latest_week', style={
                    'margin-top': '4rem',
                    'margin-left': '2rem',
                        'margin-right': '1rem',
                        }),

                dbc.Col(id='cards', style={
                    'margin-left': '5rem',
                        'margin-right': '5rem',
                        'margin-bottom': '4rem'
                        }),
            ]),

            dbc.Row(id='long', style={
                'margin-top': '4rem',
                'margin-left': '4rem',
                'margin-right': '2rem'
            }),
            dbc.Spinner(delay_hide=5, children=[
                dcc.Graph(id='at_hcp_res_ts_fig',
                          figure=blank_figure(),
                          style={
                              'margin-left': '5rem',
                              'margin-right': '5rem',
                              #'width': '90vh',
                              'height': '90vh'
                          }
                          ),
                dcc.Graph(id='utd_hcp_res_ts_fig',
                          figure=blank_figure(),
                          style={
                              'margin-left': '5rem',
                              'margin-right': '5rem',
                              #'width': '90vh',
                              'height': '90vh'
                          }
                          ),
                dcc.Graph(id='at_hcp_nh_rank_bar',
                          figure=blank_figure(),
                          style={
                              'margin-left': '6rem',
                              'margin-right': '5rem',
                              #'width': '90vh',
                              'height': '90vh'
                          }
                          ),
            ],

            ),
            html.Br(),

            dbc.Row(children=([html.P("SOURCES: ", ''),
                              (html.A("CMS Covid-19 Nursing Home Data",
                                      href="https://data.cms.gov/covid-19/covid-19-nursing-home-data",
                                      target="_blank", style={
                                          'color': '#1237E4'
                                      })
                               )]),
                    style={'textAlign': 'left',
                           'color': '#1237E4',
                           'title-font-family': 'sans-serif',
                           'font-family': 'sans-serif',
                           'margin': '4rem'
                           },

                    ),


        ],
        style={'textAlign': 'left',
               'color': '#55595c',
               'font-weight': 'bold',
               'title-font-family': 'sans-serif',
               'font-family': 'sans-serif',
               'margin': '4rem'
               }
    ),
]
)


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
    Output('at_hcp_nh_rank_bar','figure'),
    [Input('city-dropdown', 'value'),Input('fac-dropdown', 'value')])
def update_graph(selected_city, selected_fac):
    
    
    latest_wk = nh_facil_level.loc[(nh_facil_level['City'] == selected_city) & (
    nh_facil_level['rev_pct_res_anytime_c19_vax'].notnull())].sort_values('week_ending', ascending=True).iloc[0]['week_ending']

    utd_ts_data = nh_facil_level[(
    nh_facil_level['City'] == selected_city) & (nh_facil_level['week_ending']==latest_wk)]

    at_hcp_nh_rank_bar = go.Figure(go.Bar(
        x=utd_ts_data['rev_pct_hcp_anytime_c19_vax'],
        y=utd_ts_data['provider_name'].unique(),
        orientation='h',
        marker_color='#727ff2'
        )
        )

    at_hcp_nh_rank_bar.update_layout(
        yaxis={
        'categoryorder':'total ascending'
        },
        bargap=0.1,  # Gap between bars
        margin=dict(l=100), 
        title=dict(
            text='Healthcare Staff Vaccination Rates by Facility Ranked',
            y=.9,
            yanchor='bottom'
        ),
        #title_font_family="open sans semi bold",
        showlegend=False,
        plot_bgcolor='#ffffff',
        yaxis_title='Nursing Home',
        xaxis_title='Percent',
        font=dict(
            size=12
        ),
    
        legend=dict(
            #title_text='',
            orientation="h",
            yanchor="middle",
            y=1.1,
            xanchor="left",
            x=.03  
        ),
        
    )

    at_hcp_nh_rank_bar.update_yaxes(
        showgrid=False,
        # griddash='dash',
        gridwidth=1,
        gridcolor='LightGray',
        autorange=True,
        showline=True,
        linewidth=1,
        linecolor='LightGray'
        # automargin=True
    )

    at_hcp_nh_rank_bar.update_xaxes(
        range=(0, 100),
        showgrid=True,
        automargin=False,
        #tickangle=45,
        showline=True,
        linewidth=1,
        linecolor='LightGray'

    )
    return at_hcp_nh_rank_bar


@app.callback(
    Output('fac-dropdown', 'value'),
    [Input('fac-dropdown', 'options')])
def set_fac_value(available_facs):
    return available_facs[0]['value']

# callback to update the figure for the single facility data graphs
@app.callback(
    [Output('latest_week', 'children'),
     Output('long', 'children'),
     Output('cards', 'children'),
     Output('utd_hcp_res_ts_fig', 'figure'),
     Output('at_hcp_res_ts_fig', 'figure')],
    [Input('fac-dropdown', 'value')]
)
def update_graph(selected_fac):
    utd_ts_data = nh_facil_level[(
        nh_facil_level['provider_name'] == selected_fac)]
    
    ltnn_rev_pct_res_at_c19_vax = utd_ts_data.loc[(utd_ts_data['provider_name'] == selected_fac) & (
        utd_ts_data['rev_pct_res_anytime_c19_vax'].notnull())].sort_values('week_ending', ascending=False).iloc[0]['rev_pct_res_anytime_c19_vax'].round()
    ltnn_rev_pct_res_utd_c19_vax = utd_ts_data.loc[(utd_ts_data['provider_name'] == selected_fac) & (
        utd_ts_data['rev_pct_res_utd_c19_vax'].notnull())].sort_values('week_ending', ascending=False).iloc[0]['rev_pct_res_utd_c19_vax'].round()

    ltnn_rev_pct_hcp_utd_c19_vax = utd_ts_data.loc[(utd_ts_data['provider_name'] == selected_fac) & (
        utd_ts_data['rev_pct_hcp_utd_c19_vax'].notnull())].sort_values('week_ending', ascending=False).iloc[0]['rev_pct_hcp_utd_c19_vax'].round()
    min4_pct_hcp_utd_c19_vax = utd_ts_data.loc[(utd_ts_data['provider_name'] == selected_fac) & (
        utd_ts_data['rev_pct_hcp_utd_c19_vax'].notnull())].sort_values('week_ending', ascending=False).iloc[4]['rev_pct_hcp_utd_c19_vax'].round()
    ltnn_rev_pct_hcp_at_c19_vax = utd_ts_data.loc[(utd_ts_data['provider_name'] == selected_fac) & (
        utd_ts_data['rev_pct_hcp_anytime_c19_vax'].notnull())].sort_values('week_ending', ascending=False).iloc[0]['rev_pct_hcp_anytime_c19_vax'].round()

    # (ltnn_rev_pct_hcp_utd_c19_vax-min4_pct_hcp_utd_c19_vax) /

    # utd_ts_data.sort_values('week_ending', ascending=False)

    latest_wk = utd_ts_data.loc[(utd_ts_data['provider_name'] == selected_fac) & (
        utd_ts_data['rev_pct_res_anytime_c19_vax'].notnull())].sort_values('week_ending', ascending=False).iloc[0]['week_ending']
  

    latest_week = dbc.Container(

        html.H4('As of Sunday, 'f'{latest_wk}',
                className="display-left fs-1 font-weight-bold flex"),
        className="mb-5"),

    cards = dbc.CardGroup([
        dbc.Card(
            dbc.CardBody(
                [
                    html.P("Healthcare Staff Vaccinated at Any Time",
                           className="card-title text-center"),
                    html.H2(""),
                    html.H1(f'{ltnn_rev_pct_hcp_at_c19_vax:,.0f}%',
                            className="display-2 text-center font-weight-bold",
                            style={
                                'color': '#727ff2'
                            }
                            ),
                ], className="justify-content-end"
            ), className="g-0 d-flex align-items-center",
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.P("Facility Residents Vaccinated at Any Time",
                           className="card-title text-center"),
                    html.H2(""),
                    html.H1(f'{ltnn_rev_pct_res_at_c19_vax:,.0f}%',
                            className="display-2 text-center font-weight-bold",
                            style={
                                'color': '#b0841c'
                            }
                            ),
                ]
            ), className="g-0 d-flex align-items-center",
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.P("Healthcare Staff Vaccinations Up To Date",
                           className="card-title text-center"),
                    html.H2(""),
                    html.H1(f'{ltnn_rev_pct_hcp_utd_c19_vax:,.0f}%',
                            className="display-2 text-center font-weight-bold",
                            style={
                                'color': '#727ff2'
                            }
                            ),
                ]
            ), className="g-0 d-flex align-items-center",
        ),
        dbc.Card(
            dbc.CardBody(
                [
                    html.P("Facility Residents Vaccinations Up To Date",
                           className="card-title text-center"),
                    html.H2(""),
                    html.H1(f'{ltnn_rev_pct_res_utd_c19_vax:,.0f}%',
                            className="display-2 text-center font-weight-bold ",
                            style={
                                'color': '#b0841c'
                            }
                            ),
                ]
            ), className="g-0 d-flex align-items-center",
        ),
    ], className="mb-3",
    ),
    long = html.H4(
        'From Sunday, 7-10-2022 through Sunday, 'f'{latest_wk}', className="display-left fs-1 font-weight-bold flex")

    utd_hcp_res_ts_fig = go.Figure()

    utd_hcp_res_ts_fig.add_trace(
        go.Scatter(
            x=utd_ts_data['week_ending'],
            y=utd_ts_data['rev_pct_hcp_utd_c19_vax'],
            name="Healthcare Staff",
            mode='lines+markers',
            # marker_size=10,
            # marker_symbol='diamond',
            text='<b>Week Ending Date:</b> ' +
            utd_ts_data['week_ending']+'<br><b>Healthcare staff Up To Date</b> ' +
            utd_ts_data['rev_pct_hcp_utd_c19_vax'].round().astype(
                str)+'%',
            hoverinfo='text',
            #fill='tozeroy',
            line=dict(color='#727ff2', width=3)
        ),
    )

    utd_hcp_res_ts_fig.add_trace(
        go.Scatter(
            x=utd_ts_data['week_ending'],
            y=utd_ts_data['rev_pct_res_utd_c19_vax'],
            name="Residents",
            mode='lines+markers',
            # marker_size=10,
            # marker_symbol='diamond',
            text='<b>Week Ending Date:</b> ' +
            utd_ts_data['week_ending']+'<br><b>Residents Up To Date</b> ' +
            utd_ts_data['rev_pct_res_utd_c19_vax'].round().astype(
                str)+'%',
            hoverinfo='text',
            #fill='tonexty',
            line=dict(color='#b0841c', width=3)
        ),
    )

    at_hcp_res_ts_fig = go.Figure()

    at_hcp_res_ts_fig.add_trace(
        go.Scatter(
            x=utd_ts_data['week_ending'],
            y=utd_ts_data['rev_pct_hcp_anytime_c19_vax'],
            name="Healthcare Staff",
            mode='lines+markers',
            # marker_size=10,
            # marker_symbol='diamond',
            text='<b>Week Ending Date:</b> ' +
            utd_ts_data['week_ending']+'<br><b>Healthcare staff Anytime</b> ' +
            utd_ts_data['rev_pct_hcp_anytime_c19_vax'].round().astype(
                str)+'%',
            hoverinfo='text',
            #fill='tozeroy',
            line=dict(color='#727ff2', width=3)
        ),
    )

    at_hcp_res_ts_fig.add_trace(
        go.Scatter(
            x=utd_ts_data['week_ending'],
            y=utd_ts_data['rev_pct_res_anytime_c19_vax'],
            name="Residents",
            mode='lines+markers',
            # marker_size=10,
            # marker_symbol='diamond',
            text='<b>Week Ending Date:</b> ' +
            utd_ts_data['week_ending']+'<br><b>Residents Anytime</b> ' +
            utd_ts_data['rev_pct_res_anytime_c19_vax'].round().astype(
                str)+'%',
            hoverinfo='text',
            #fill='tonexty',
            line=dict(color='#b0841c', width=3,
                      )
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
        # template='lux',
        title=dict(
            text='Vaccinations & Boosters <b><em>Up To Date</em></b>',
            y=.9,
            yanchor='bottom'
        ),
        showlegend=True,
        plot_bgcolor='#ffffff',
        yaxis_title='Percent',
        xaxis_title='Week Ending Date',
        xaxis_dtick=2,
        font=dict(
            size=12
        ),
        legend=dict(
            title_text='',
            orientation="h",
            yanchor="middle",
            y=1,
            xanchor="left",
            x=.05
        )
    )

    at_hcp_res_ts_fig.update_layout(

        title=dict(
            text='Received a Vaccination <b><em>at Any Time</em></b>',
            y=.9,
            yanchor='bottom'
        ),
        #title_font_family="open sans semi bold",
        showlegend=True,
        plot_bgcolor='#ffffff',
        yaxis_title='Percent',
        xaxis_title='Week Ending Date',
        xaxis_dtick=2,
        font=dict(
            size=12
        ),
        legend=dict(
            title_text='',
            orientation="h",
            yanchor="middle",
            y=1,
            xanchor="left",
            x=.05
        )
    )

    utd_hcp_res_ts_fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='LightGray',
        range=(-10, 110),
        autorange=False,
        showline=True,
        linewidth=1,
        linecolor='LightGray'
        # automargin=True
    )

    utd_hcp_res_ts_fig.update_xaxes(
        showgrid=False,
        # automargin=True,
        tickangle=45,
        showline=True,
        linewidth=1,
        linecolor='LightGray'
    )

    at_hcp_res_ts_fig.update_yaxes(
        showgrid=True,
        # griddash='dash',
        gridwidth=1,
        gridcolor='LightGray',
        range=(-10, 110),
        autorange=False,
        showline=True,
        linewidth=1,
        linecolor='LightGray'
        # automargin=True
    )

    at_hcp_res_ts_fig.update_xaxes(
        showgrid=False,
        # automargin=True,
        tickangle=45,
        showline=True,
        linewidth=1,
        linecolor='LightGray'
    )

    # return ind_utd_res_c19_vax, ind_utd_hcp_c19_vax, ind_at_hcp_c19_vax,
    return latest_week, long, cards, utd_hcp_res_ts_fig, at_hcp_res_ts_fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
    server = app.server
