import plotly.figure_factory as ff
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

load_figure_template("LUX")

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

# make a dataframe to get the values of 'rev_pct_hcp_utd_c19_vax' for each location at the latest week ending
ltnn_rev_pct_hcp_utd_c19_vax = (
    nh_facil_level.sort_values('week_ending', ascending=False)
    .groupby('provider_name')
    .apply(lambda x: x[x['rev_pct_hcp_utd_c19_vax'].notnull()].iloc[0] if x['rev_pct_hcp_utd_c19_vax'].notnull().any() else x.iloc[0])
    .reset_index(drop=True)
    .loc[:,['provider_name','week_ending','rev_pct_hcp_utd_c19_vax']]
)
ltnn_rev_pct_hcp_utd_c19_vax.head(30)

# Set app theme
app = Dash(external_stylesheets=[dbc.themes.LUX])


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
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template="LUX")
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    return fig


# Define the app layout
app.layout =dbc.Container(html.Div(children=[
    html.H1(children='COVID-19 vaccination rates in Nursing Homes',
            style={
                'textAlign': 'left',
                'color': '#55595c',
                'title-font-family': 'sans-serif',
                'font-family': 'sans-serif',
                'margin': '2rem'}
            ),
    html.Div(children=[
        state_dropdown,
        city_dropdown,
        fac_dropdown
    ],
        style={'textAlign': 'left',
               'color': '#55595c',
               'title-font-family': 'sans-serif',
               'font-family': 'sans-serif',
                'margin': '2rem'
               }
    ),
    dcc.Loading(
        id="loading-2",
        type='circle',
        children=[
    #    dbc.Row(
    #             #dbc.Col(dcc.Graph(id='ind_utd_hcp_c19_vax', figure=blank_figure())),
    #            [dbc.Col(dcc.Graph(id='ind_utd_hcp_c19_vax', figure=blank_figure())),
    #             dbc.Col(dcc.Graph(id='ind_at_hcp_c19_vax', figure=blank_figure()))]
    #             ),
        
            #dcc.Graph(id='ind_utd_hcp_c19_vax', figure=blank_figure()),
            dcc.Graph(id='utd_hcp_res_ts_fig', figure=blank_figure()),
            dcc.Graph(id='at_hcp_res_ts_fig', figure=blank_figure()),
            # dcc.Graph(id='ind_latest_dt', figure=blank_figure()),
            
                          
           html.Div(children=[html.P("Data Source: ",''),
                    (html.A("CMS Covid-19 Nursing Home Data",
                            href="https://data.cms.gov/covid-19/covid-19-nursing-home-data",
                              target="_blank")
                  ),
                  ],
                          style={'textAlign': 'left',
                          'color': '#55595c',
                          'title-font-family': 'sans-serif',
                          'font-family': 'sans-serif',
                          'margin': '3rem'
                          }
            ),
            
   
],
 style={'textAlign': 'left',
                          'color': '#55595c',
                          'title-font-family': 'sans-serif',
                          'font-family': 'sans-serif',
                          
                          }
),
]))


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
    # Output("staff-vaccination-rate", "children"),
    # Output('ind_at_res_c19_vax','figure'),
    # Output('ind_utd_res_c19_vax','figure'),
    # Output('ind_at_hcp_c19_vax','figure'),
    # Output('ind_utd_hcp_c19_vax','figure'),
    [Output('utd_hcp_res_ts_fig', 'figure'),
    Output('at_hcp_res_ts_fig', 'figure')],
    [Input('fac-dropdown', 'value')]
)


def update_graph(selected_fac):
    utd_ts_data = nh_facil_level[(
        nh_facil_level['provider_name'] == selected_fac) & (nh_facil_level['week_ending'] > '2022-07-03')]
    
    ltnn_rev_pct_res_at_c19_vax = utd_ts_data.loc[(utd_ts_data['provider_name'] == selected_fac) & (utd_ts_data['rev_pct_res_anytime_c19_vax'].notnull())].sort_values('week_ending', ascending=False).iloc[0]['rev_pct_res_anytime_c19_vax'].round()
    ltnn_rev_pct_res_utd_c19_vax = utd_ts_data.loc[(utd_ts_data['provider_name'] == selected_fac) & (utd_ts_data['rev_pct_res_utd_c19_vax'].notnull())].sort_values('week_ending', ascending=False).iloc[0]['rev_pct_res_utd_c19_vax'].round()


    ltnn_rev_pct_hcp_utd_c19_vax = utd_ts_data.loc[(utd_ts_data['provider_name'] == selected_fac) & (utd_ts_data['rev_pct_hcp_utd_c19_vax'].notnull())].sort_values('week_ending', ascending=False).iloc[0]['rev_pct_hcp_utd_c19_vax'].round()
    min4_pct_hcp_utd_c19_vax = utd_ts_data.loc[(utd_ts_data['provider_name'] == selected_fac) & (utd_ts_data['rev_pct_hcp_utd_c19_vax'].notnull())].sort_values('week_ending', ascending=False).iloc[4]['rev_pct_hcp_utd_c19_vax'].round()
    ltnn_rev_pct_hcp_at_c19_vax = utd_ts_data.loc[(utd_ts_data['provider_name'] == selected_fac) & (utd_ts_data['rev_pct_hcp_anytime_c19_vax'].notnull())].sort_values('week_ending', ascending=False).iloc[0]['rev_pct_hcp_anytime_c19_vax'].round()
   

    # (ltnn_rev_pct_hcp_utd_c19_vax-min4_pct_hcp_utd_c19_vax) /

    # utd_ts_data.sort_values('week_ending', ascending=False)

    # latest_week = utd_ts_data.loc[utd_ts_data['rev_pct_res_utd_c19_vax'].last_valid_index(),'week_ending']
    # metric_value = utd_ts_data.loc[utd_ts_data['week_ending']==latest_week, 'rev_pct_res_utd_c19_vax']
    # return metric_value, f'Latest Week: {latest_week}'


    # ind_latest_dt = go.Figure()

    # ind_latest_dt.add_trace(go.Indicator(
    # mode = "number+delta",
    # value = utd_ts_data.loc[utd_ts_data['week_ending'].iloc[-1],'rev_pct_hcp_utd_c19_vax'].round().astype(
    #             str)+'%',
    # title = {"text": "Accounts<br><span style='font-size:0.8em;color:gray'>Subtitle</span><br><span style='font-size:0.8em;color:gray'>Subsubtitle</span>"},
    # delta = {'reference': 400, 'relative': True},
    # domain = {'x': [0.6, 1], 'y': [0, 1]}
    # )
    # )
    
    # ind_utd_res_c19_vax = go.Figure()

    # ind_utd_res_c19_vax.add_trace(
    #     go.Indicator(
    #      mode="number",
    #     value = ltnn_rev_pct_res_utd_c19_vax.round(),
    #     number = {"suffix": "%"},
    #     domain = {'row': 1, 'column': 1}
    #         )
    #     )
    
    # ind_utd_res_c19_vax.update_layout(
    # #grid = {'rows': 1, 'columns': 4, 'pattern': "independent"},
    # template = {'data' : {'indicator': [{
    #     'title': {'text': "Res<br>vaccinations up-to-date"},
    #     'mode' : "number",
    #     'domain' : {'x': [0.6, 1], 'y': [0, 1]}}]
    #                      }})
    
    
    # ind_utd_hcp_c19_vax = go.Figure()

    # ind_utd_hcp_c19_vax.add_trace(
    #     go.Indicator(
    #      mode="number",
    #     value = ltnn_rev_pct_hcp_utd_c19_vax.round(),
    #     number = {"suffix": "%"},
    #     domain = {'row': 1, 'column': 1}
    #         )
    #     )
    
    # ind_utd_hcp_c19_vax.update_layout(
    # #grid = {'rows': 1, 'columns': 4, 'pattern': "independent"},
    # template = {'data' : {'indicator': [{
    #     'title': {'text': "Health Care Personnel<br>vaccinations up-to-date"},
    #     'mode' : "number",
    #     'domain' : {'x': [0.6, 1], 'y': [0, 1]}}]
    #                      }})
    
    # ind_at_hcp_c19_vax = go.Figure()

    # ind_at_hcp_c19_vax.add_trace(
    #     go.Indicator(
    #      mode="number",
    #     value = ltnn_rev_pct_hcp_at_c19_vax.round(),
    #     number = {"suffix": "%"},
    #     domain = {'row': 1, 'column': 1}
    #         )
    #     )
    
    # ind_at_hcp_c19_vax.update_layout(
    # #grid = {'rows': 1, 'columns': 4, 'pattern': "independent"},
    # template = {'data' : {'indicator': [{
    #     'title': {'text': "Health Care Personnel<br>vaccinated at any time"},
    #     'mode' : "number",
    #     'domain' : {'x': [0.6, 1], 'y': [0, 1]}}]
    #                      }})

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

        # title_font_family="Arial",
        showlegend=True,
        plot_bgcolor='#ffffff',
        yaxis_title='Percent',
        xaxis_title='Week Ending Date',
        font=dict(
            size=12
        ),
            legend=dict(
            title_text='',
            orientation="h",
            yanchor="middle",
            y=1.1,
            xanchor="left",
            x=.03
        )
    )

    at_hcp_res_ts_fig.update_layout(
        
        # margin=dict(
        #     l=20,
        #     r=20,
        #     t=100,
        #     # b=20,
        #     # pad=4
        # ),
        
        #template = load_figure_template('LUX'),
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
        font=dict(
            size=12
        ),
        legend=dict(
            title_text='',
            orientation="h",
            yanchor="middle",
            y=1.1,
            xanchor="left",
            x=.03
        )
    )

    utd_hcp_res_ts_fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='LightGray',
        range=(0, 100),
        autorange=False,
        automargin=True
    )

    utd_hcp_res_ts_fig.update_xaxes(
        showgrid=False,
        automargin=True
    )

    at_hcp_res_ts_fig.update_yaxes(
        showgrid=True,
        # griddash='dash',
        gridwidth=1,
        gridcolor='LightGray',
        range=(0, 100),
        autorange=False,
        automargin=True
    )

    at_hcp_res_ts_fig.update_xaxes(
        showgrid=False,
        automargin=True
    )



    #return ind_utd_res_c19_vax, ind_utd_hcp_c19_vax, ind_at_hcp_c19_vax, 
    return utd_hcp_res_ts_fig, at_hcp_res_ts_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)


