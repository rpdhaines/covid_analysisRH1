### covid analysis app ###

# make necessary imports
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objects as go
import pandas as pd
import datetime
from pandas.tseries.offsets import DateOffset
from style_creator import create_div_style, create_graph_layout
from utilities import *
from app_tab_layouts import *

# create app

# bring in a custom style for dashboard
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#initialise dashboard with stylesheet
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

server = app.server

app.layout = html.Div([
    html.Div([
        # heading and blurb
        dcc.Markdown('''
        ### Analysis of England COVID data  
        ##### Richard Haines       
        ''', style=create_div_style(mb=0, mt=0, borderb='solid grey 1px',  bc='rgba(52, 184, 220, 0.3)',
                                    gradient='linear-gradient(to right, #008080, #FFFFFF)')),

    ]),

    html.Div([

        dcc.Tabs(id='tabs', value='tab-0', children=[
            dcc.Tab(label='Information', value='tab-0'),
            dcc.Tab(label='Case analysis by age and region', value='tab-1'),
            dcc.Tab(label='Impact of vaccinations on hospital admissions', value='tab-2'),
            dcc.Tab(label='Analysis of case to admission lag', value='tab-3'),
        ], style=create_div_style(fs=18, mb=3), vertical=True),
        html.Div(id='tabs-content')
    ]),

    html.Div([
    dcc.Markdown('''
    This app is provided 'as is' without warranty of any kind. No reliance can be placed on the contents of this app. The data used is public data from:  
    The gov.uk coronavirus dashboard [https://coronavirus.data.gov.uk/]  
    The data accessed from the coronavirus dashboard is cases by specimen date, available as a csv download from
     [https://api.coronavirus.data.gov.uk/v2/data?areaType=region&metric=newCasesBySpecimenDateAgeDemographics&format=csv]  
    The ONS 2019 population estimates available from [https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatesforukenglandandwalesscotlandandnorthernireland]  
    The code for this app can be found on GitHub: [https://github.com/rpdhaines/covid_analysisRH1]  
    Questions? Contact me on rpdhaines2@yahoo.co.uk 
    ''')
    ], style=create_div_style(fs=16))
])

# set callback to choose tab
@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-0':
        return tab0_layout
    elif tab == 'tab-1':
        return tab1_layout
    elif tab == 'tab-2':
        return tab2_layout
    elif tab == 'tab-3':
        return tab3_layout


# set callback to populate graphs 1_1 and 1_2
@app.callback(
    [Output('cases_per_10,000_by_age_group', 'figure'),
     Output('daily_growth_rate_by_age_group', 'figure')],
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
def update_graphs1(Region, start_date, rolling_avge_length, growth_rate_length, growth_rate_average_length,
                  age_bins_list1, age_bins_list2, age_bins_list3, age_bins_list4, age_bins_list5):

    fig1_1 = go.Figure()
    fig1_2 = go.Figure()

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

    df_rolling = df.rolling(rolling_avge_length).mean()


    # create region population by age group
    region_pop = pop_by_region.copy()
    region_pop = get_region_pop(region_pop, Region, age_bins_list)

    # turn df into per 10,000 population
    df_per_pop = get_df_per_pop(df_rolling, region_pop)

    growth_rate = (df_rolling / df_rolling.shift(growth_rate_length)).apply(lambda x: x ** (1 / growth_rate_length) - 1)
    growth_rate = growth_rate.rolling(growth_rate_average_length, center=True).mean()

    # filter to start date
    df_per_pop = df_per_pop.loc[pd.to_datetime(dates[start_date]):]
    growth_rate = growth_rate.loc[pd.to_datetime(dates[start_date]):]

    for col in df_per_pop.columns:
        fig1_1.add_trace(go.Scatter(
            x=df_per_pop.index,
            y=df_per_pop[col],
            mode='lines',
            name=col
        )
        )

    fig1_1.update_layout(create_graph_layout(title=f'Daily cases per 10,000 population over time in {Region}',
                                           xtitle='date',
                                           ytitle='daily cases per 10,000 population'))


    for col in growth_rate.columns:
        fig1_2.add_trace(go.Scatter(
            x=growth_rate.index,
            y=growth_rate[col],
            mode='lines',
            name=col
        )
        )

    fig1_2.update_layout(create_graph_layout(title=f'Smoothed daily growth rate by age over time in {Region}',
                                           xtitle='date',
                                           ytitle='smoothed growth rate'))

    return fig1_1, fig1_2

# set callback to populate graph2_1
@app.callback(
    Output('cumulative_vax_ppn', 'figure'),
    [Input('start_date', 'value'),
     Input('age_gps', 'value')])
def update_graph2_1(start_date, age_gps):

    fig2_1 = go.Figure()

    df = vax_per_10k.copy()

    # convet start_date to datetime and pad df to start_date
    start_date = pd.to_datetime(dates[start_date])
    df = backfill_start(df, start_date)

    for col in age_gps:
        col1 = col + ' dose1'
        col2 = col + ' dose2'
        fig2_1.add_trace(go.Scatter(
            x=df.index,
            y=df[col1],
            mode='lines',
            name=col1
        )
        )

        fig2_1.add_trace(go.Scatter(
            x=df.index,
            y=df[col2],
            mode='lines',
            name=col2
        )
        )

    fig2_1.update_layout(create_graph_layout(title='Cumulative vaccinations dose 1 and dose 2',
                                           xtitle='date',
                                           ytitle='Vaccinate per 10,000'))

    return fig2_1

# set callback to populate graph2
@app.callback(
    Output('compare_ratio', 'figure'),
    [Input('start_date', 'value'),
     Input('rolling_avge_length', 'value'),
     Input('offset_days', 'value'),
     Input('age_gps', 'value')])
def update_graph2_2(start_date, rolling_avge_length, offset_days, age_gps):

    fig2_2 = go.Figure()

    df1 = admissions_per_10k.copy()
    df2 = cases_per_10k.copy()

    df1 = df1.shift(-offset_days)

    # turn start_date to datetime
    start_date = pd.to_datetime(dates[start_date])

    df = get_ratio(df1, df2, start_date, rolling_avge_length)

    for col in age_gps:
        fig2_2.add_trace(go.Scatter(
            x=df.index,
            y=df[col],
            mode='lines',
            name=col + '      '
        )
        )

    fig2_2.update_layout(create_graph_layout(title='Admissions to cases ratio',
                                           xtitle='Date',
                                           ytitle='Admissions to cases ratio'))

    return fig2_2

# set callback to populate graph3_1
@app.callback(
    [Output('admission-vs-case-scatter', 'figure'),
     Output('admission-case-ratio', 'figure'),
     Output('admission-case-overlay', 'figure')],
    [Input('date_range', 'value'),
     Input('rolling_avge_length', 'value'),
     Input('admission_lag', 'value'),
     Input('age_gps', 'value')])
def update_graphs3(date_range, rolling_avge_length, admission_lag, age_gps):

    # get dfs filtered to just chose age_gps
    df1 = admissions_per_10k[age_gps].copy()
    df2 = cases_per_10k[age_gps].copy()

    df1 = df1.shift(-admission_lag)

    # turn start_date and end_date to datetime
    start_date = pd.to_datetime(dates[date_range[0]])
    end_date = pd.to_datetime(dates[date_range[1]])

    final_admissions = get_rolling_total(df1, start_date=start_date, end_date=end_date, rolling=rolling_avge_length)
    final_cases = get_rolling_total(df2, start_date=start_date, end_date=end_date, rolling=rolling_avge_length)

    graph_data = pd.DataFrame(data={'date': final_cases.index,
                                    'cases': final_cases['total'],
                                    'admissions': final_admissions['total']})

    # really convoluted way to create a list of dates (as strings) to use as colorbar tick labels
    min_date = graph_data['date'].min()
    graph_data['days'] = graph_data['date'].apply(lambda x: (x - min_date).days)
    max_days = graph_data['days'].max()
    fig1ticks = np.arange(0, (int(max_days / 28) + 1) * 28, 28)
    fig1datetimes = [min_date + datetime.timedelta(days=i) for i in fig1ticks.tolist()]
    fig1text = [i.strftime("%d-%b-%Y") for i in fig1datetimes]

    # add a ratio column
    graph_data['ratio'] = graph_data['admissions'] / graph_data['cases']

    # add a rescaled cases column
    scale_factor = graph_data['admissions'].sum() / graph_data['cases'].sum()
    graph_data['scaled_cases'] = graph_data['cases'] * scale_factor

    # cut off the last 'lag' days to avoid NANs at end
    graph_data = graph_data.iloc[:-admission_lag]

    fig3_1 = go.Figure()

    fig3_1.add_trace(go.Scatter(
        x=graph_data['cases'],
        y=graph_data['admissions'],
        mode='markers',
        marker={
            'size': 8,
            'opacity': 0.95,
            'line': {'width': 0.5, 'color': 'white'},
            'color': graph_data['days'],
            'colorbar': {'title': 'Date',
                         'tickvals': fig1ticks,
                         'ticktext': fig1text,
                         },
            'colorscale': 'Viridis'
        }
    )
    )

    fig3_1.update_layout(create_graph_layout(title=f'Admissions vs cases for lag {admission_lag} days',
                                             xtitle='Cases',
                                             ytitle='Admissions',
                                             height=600))

    fig3_2 = go.Figure()

    fig3_2.add_trace(go.Scatter(
        x=graph_data['date'],
        y=graph_data['ratio'],
        mode='lines'
    )
    )

    fig3_2.update_layout(create_graph_layout(title=f'Admissions to cases ratio for lag {admission_lag} days',
                                             xtitle='Date',
                                             ytitle='Admission to case ratio',
                                             height=300))
    fig3_3 = go.Figure()

    fig3_3.add_trace(go.Scatter(
        x=graph_data['date'],
        y=graph_data['admissions'],
        mode='lines',
        name='admissions',
        fill='tonexty'))
    fig3_3.add_trace(go.Scatter(
        x=graph_data['date'],
        y=graph_data['scaled_cases'],
        mode='lines',
        name='scaled cases',
        fill='tonexty'))

    fig3_3.update_layout(create_graph_layout(title=f'Relative change in admissions to cases over time for lag {admission_lag} days',
                                             xtitle='Date',
                                             ytitle='Admission and rescaled cases',
                                             height=300))

    return fig3_1, fig3_2, fig3_3

if __name__ == '__main__':
    app.run_server(debug=True)


