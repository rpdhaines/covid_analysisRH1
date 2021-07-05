### covid analysis app ###

# make necessary imports
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objects as go
import pandas as pd
from pandas.tseries.offsets import DateOffset
from style_creator import create_div_style, create_graph_layout
from utilities import clean_case_data, bin_ages_from_list, get_region_pop, get_df_per_pop

# read in Govt cases data
cases_by_age_region = pd.read_csv("https://api.coronavirus.data.gov.uk/v2/data?areaType=region&metric=newCasesBySpecimenDateAgeDemographics&format=csv")

# read in population data
pop_by_region = pd.read_csv("2019_pop_by_region.csv")

### data tidying ###
cases_by_age_region = clean_case_data(cases_by_age_region)

# create list of region names
region_names = cases_by_age_region['areaName'].unique().tolist()
region_names.append('England')

# create list of date labels for starting date
date1 = pd.to_datetime("2020-08-01")
dates = [date1 + DateOffset(months=x) for x in range(11)]

# create lists to use to select columns in eventual dataframe
groupings = ['date', 'age_group', 'areaName']
groups_and_cases = ['date', 'age_group', 'areaName', 'cases']

national_groupings = ['date', 'age_group']
national_groups_and_cases = ['date', 'age_group', 'cases']

# create app

# bring in a custom style for dashboard
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#initialise dashboard with stylesheet
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
    html.Div([
        # heading and blurb
        dcc.Markdown('''
        # Analysis of COVID case levels and growth rates by age and region
        
        #### The first figure shows cases per 10,000 of population and the second shows the average daily growth rate smoothed according to the selected parameters.
        
        #### As well as varying Region and age groups, you can play with some smoothing parameters described below.
        
        ''', style=create_div_style(borderb='solid black 1px')),

        # create Div box to house 2 further div boxes, a LHS one housing the options and a RHS one housing the graphs
        html.Div([
            # create div box for all options
            html.Div([
                # label for dropdown
                html.Label('Choose Region',
                           style=create_div_style(fs=18)),

                # dropdown for choosing Region
                dcc.Dropdown(
                    id='Region',
                    options=[{'label': i, 'value': i} for i in region_names],
                    value='England',
                    style=create_div_style(mb=10)
                ),

                # first create a div box for it as it seems to be the only way to set margins for it
                html.Div([
                    # label for RangeSlider
                    html.Label('Set earliest date to consider',
                               style=create_div_style(fs=18)),

                    #create another div box to house the slider itself as you can't set the margins or style elements
                    # as part of the slider component itself

                    html.Div([
                        # Range slider for setting earliest date considered
                        dcc.Slider(
                            id='start_date',
                            min=0,
                            max=12,
                            step=1,
                            marks={2*i: dates[2*i].strftime('%Y-%m-%d') for i in range(6)},
                            value=0
                        )
                    ], style=create_div_style(mb=10))

                ]),

                html.Div([
                    # label for slider
                    html.Label('Set size of rolling average window for cases (must be multiple of 7)',
                               style=create_div_style(fs=18)),

                    dcc.Markdown('''
                    Daily case numbers are averaged over the *previous* n days''',
                                 style=create_div_style(fs=14)),

                    html.Div([
                    # slider for choosing rolling average length
                    dcc.Slider(
                        id='rolling_avge_length',
                        min=7,
                        max=21,
                        step=7,
                        marks={i*7: str(i*7) for i in range(1, 4)},
                        value=7
                    )
                    ], style=create_div_style(mb=10))
                ]),

                html.Div([
                    # label for slider
                    html.Label('Set length of time to calculate avge daily growth rate over',
                               style=create_div_style(fs=18)),

                    dcc.Markdown('''
                    Average daily growth rate will be calculated by comparing the rolling cases n days apart''',
                                 style=create_div_style(fs=14)),

                    html.Div([
                    # slider for choosing growth rate length
                    dcc.Slider(
                        id='growth_rate_length',
                        min=7,
                        max=42,
                        step=7,
                        marks={7*i: str(7*i) for i in range(1, 7)},
                        value=21
                    )
                    ], style=create_div_style(mb=10))
                ]),

                html.Div([
                    # label for slider
                    html.Label('Set size of rolling average window for growth rate',
                               style=create_div_style(fs=18)),

                    dcc.Markdown('''
                    Calculated growth rate can be smoothed over n days as a final smoothing step''',
                                 style=create_div_style(fs=14)),

                    html.Div([
                    # slider for choosing growth rate averaging period
                    dcc.Slider(
                        id='growth_rate_avge_length',
                        min=1,
                        max=10,
                        step=1,
                        marks={i: str(i) for i in range(1, 11)},
                        value=5
                    )
                    ], style=create_div_style(mb=10))
                ]),

                html.Div([
                    # label for checklist
                    html.Label('Choose age group dividers',
                               style=create_div_style(fs=18)),

                    dcc.Markdown('''
                    Check all boxes you want to use as start and end of age group ranges.
                    First range will start at 0 and last range will cover all older ages''',
                                 style=create_div_style(fs=14)),

                    html.Div([
                        dcc.Checklist(
                            id='age_bins_list1',
                            options=[
                                {'label': str(5*i), 'value': 5*i} for i in range(1,5)
                            ],
                            value=[20]),
                        ], style=create_div_style(mb=15, w='10%')),

                    html.Div([
                        dcc.Checklist(
                            id='age_bins_list2',
                            options=[
                                {'label': str(5 * i), 'value': 5 * i} for i in range(5, 9)
                            ],
                            value=[40]),
                    ], style=create_div_style(mb=15, w='10%')),

                    html.Div([
                        dcc.Checklist(
                            id='age_bins_list3',
                            options=[
                                {'label': str(5 * i), 'value': 5 * i} for i in range(9, 13)
                            ],
                            value=[60]),
                    ], style=create_div_style(mb=15, w='10%')),

                    html.Div([
                        dcc.Checklist(
                            id='age_bins_list4',
                            options=[
                                {'label': str(5 * i), 'value': 5 * i} for i in range(13, 17)
                            ],
                            value=[]),
                    ], style=create_div_style(mb=15, w='10%')),

                    html.Div([
                        dcc.Checklist(
                            id='age_bins_list5',
                            options=[
                                {'label': str(5 * i), 'value': 5 * i} for i in range(17, 19)
                            ],
                            value=[]),
                    ], style=create_div_style(mb=15, w='10%'))

                ], style=create_div_style(mb=15))
            ], style=create_div_style(w='32%')),

            # create div box for graphs
            html.Div([
                # graph1
                dcc.Graph(id='cases_per_10,000_by_age_group'),
                dcc.Graph(id='daily_growth_rate_by_age_group')
            ], style=create_div_style(w='66%')),
        ]),

    ]),

    html.Div([
        dcc.Markdown('''
        This work is the author's own. No reliance can be placed on the contents of this app. The data used is public data from:  
        The gov.uk coronavirus dashboard [https://coronavirus.data.gov.uk/]  
        The data accessed from the coronavirus dashboard is cases by specimen date, available as a csv download from
         [https://api.coronavirus.data.gov.uk/v2/data?areaType=region&metric=newCasesBySpecimenDateAgeDemographics&format=csv]  
         The ONS 2019 population estimates available from [https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatesforukenglandandwalesscotlandandnorthernireland] 
        ''')
    ], style=create_div_style())
])


# set callback to populate graph1
@app.callback(
    Output('cases_per_10,000_by_age_group', 'figure'),
    [Input('Region', 'value'),
     Input('start_date', 'value'),
     Input('rolling_avge_length', 'value'),
     Input('age_bins_list1', 'value'),
     Input('age_bins_list2', 'value'),
     Input('age_bins_list3', 'value'),
     Input('age_bins_list4', 'value'),
     Input('age_bins_list5', 'value')])
def update_graph1(Region, start_date, rolling_avge_length, age_bins_list1,
                  age_bins_list2, age_bins_list3, age_bins_list4, age_bins_list5):

    fig1 = go.Figure()

    df = cases_by_age_region.copy()

    age_bins_list = age_bins_list1 + age_bins_list2 + age_bins_list3 + age_bins_list4 + age_bins_list5

    ### aggregate age groups ###
    df = bin_ages_from_list(df, age_bins_list)

    # turn into required pivot
    if Region == 'England':
        df = df[national_groups_and_cases].groupby(by=national_groupings).sum().unstack()
        df.columns = df.columns.droplevel()
    else:
        df = df[groups_and_cases].groupby(by=groupings).sum().unstack().unstack()
        df.columns = df.columns.droplevel()

    # filter by region
    if Region == 'England':
        pass
    else:
        df = df[Region].copy()

    # filter to start-date
    df = df[pd.to_datetime(dates[start_date]):]

    df_rolling = df.rolling(rolling_avge_length).mean()

    # create region population by age group
    region_pop = pop_by_region.copy()
    region_pop = get_region_pop(region_pop, Region, age_bins_list)

    # turn df into per 10,000 population
    df_rolling = get_df_per_pop(df_rolling, region_pop)

    for col in df_rolling.columns:
        fig1.add_trace(go.Scatter(
            x=df_rolling.index,
            y=df_rolling[col],
            mode='lines',
            name=col
        )
        )

    fig1.update_layout(create_graph_layout(title=f'Daily cases per 10,000 population over time in {Region}',
                                           xtitle='date',
                                           ytitle='daily cases per 10,000 population'))

    return fig1

# set callback to populate graph2
@app.callback(
    Output('daily_growth_rate_by_age_group', 'figure'),
    [Input('Region', 'value'),
     Input('start_date', 'value'),
     Input('rolling_avge_length', 'value'),
     Input('growth_rate_length', 'value'),
     Input('growth_rate_avge_length', 'value'),
     Input('age_bins_list1', 'value'),
     Input('age_bins_list2', 'value'),
     Input('age_bins_list3', 'value'),
     Input('age_bins_list4', 'value'),
     Input('age_bins_list5', 'value')])
def update_graph2(Region, start_date, rolling_avge_length, growth_rate_length, growth_rate_average_length,
                  age_bins_list1, age_bins_list2, age_bins_list3, age_bins_list4, age_bins_list5):

    fig2 = go.Figure()

    df = cases_by_age_region.copy()
    age_bins_list = age_bins_list1 + age_bins_list2 + age_bins_list3 + age_bins_list4 + age_bins_list5

    ### aggregate age groups ###
    df = bin_ages_from_list(df, age_bins_list)

    # turn into required pivot
    if Region == 'England':
        df = df[national_groups_and_cases].groupby(by=national_groupings).sum().unstack()
        df.columns = df.columns.droplevel()
    else:
        df = df[groups_and_cases].groupby(by=groupings).sum().unstack().unstack()
        df.columns = df.columns.droplevel()

    # filter by region
    if Region == 'England':
        pass
    else:
        df = df[Region].copy()

    # filter to start-date
    df = df[pd.to_datetime(dates[start_date]):]

    df_rolling = df.rolling(rolling_avge_length).mean()

    growth_rate = (df_rolling / df_rolling.shift(growth_rate_length)).apply(lambda x: x ** (1 / growth_rate_length) - 1)
    growth_rate = growth_rate.rolling(growth_rate_average_length, center=True).mean()

    for col in growth_rate.columns:
        fig2.add_trace(go.Scatter(
            x=growth_rate.index,
            y=growth_rate[col],
            mode='lines',
            name=col
        )
        )

    fig2.update_layout(create_graph_layout(title=f'Smoothed daily growth rate by age over time in {Region}',
                                           xtitle='date',
                                           ytitle='smoothed growth rate'))

    return fig2


if __name__ == '__main__':
    app.run_server(debug=True)


