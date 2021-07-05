### covid vaccination analysis app ###

# make necessary imports
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.graph_objects as go
import pandas as pd
from pandas.tseries.offsets import DateOffset
from style_creator import create_div_style
from utilities import prepare_case_data, prepare_vax_data, prepare_admissions_data, equalise_end_dates, backfill_start, get_ratio

# read in Govt cases data for England
cases_by_age = pd.read_csv("https://api.coronavirus.data.gov.uk/v2/data?areaType=nation&areaCode=E92000001&metric=newCasesBySpecimenDateAgeDemographics&format=csv")

# read in Govt vaccines data for England
vaccines_by_age = pd.read_csv("https://api.coronavirus.data.gov.uk/v2/data?areaType=nation&areaCode=E92000001&metric=vaccinationsAgeDemographics&format=csv")

# read in Govt hosptial admissions data for England
cum_admissions_by_age = pd.read_csv("https://api.coronavirus.data.gov.uk/v2/data?areaType=nation&areaCode=E92000001&metric=cumAdmissionsByAge&format=csv")

### data tidying ###
cases_per_10k = prepare_case_data(cases_by_age)

vax_per_10k = prepare_vax_data(vaccines_by_age)

admissions_per_10k = prepare_admissions_data(cum_admissions_by_age)

# equalise end dates
df_list = equalise_end_dates(cases_per_10k, vax_per_10k, admissions_per_10k)
cases_per_10k = df_list[0].copy()
vax_per_10k = df_list[1].copy()
admissions_per_10k = df_list[2].copy()


# create list of date labels for starting date
date1 = pd.to_datetime("2020-08-01")
dates = [date1 + DateOffset(months=x) for x in range(11)]

# create list of ratio options
ratio_options = ['admissions to cases ratio', 'admissions to ONS incidence ratio', 'cases to ONS incidence ratio']

# create app

# bring in a custom style for dashboard
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#initialise dashboard with stylesheet
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
    # heading
    html.H1('Analysis of vaccination impacts on COVID'),

    # create Div box to house 2 further div boxes, a LHS one housing the options and a RHS one housing the graphs
    html.Div([
        # create div box for all options
        html.Div([

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
                        value=3
                    )
                ], style=create_div_style(mb=20))
            ]),

            html.Div([
                # label for slider
                html.Label('Set size of rolling average window for ratio comparison (must be multiple of 7)',
                           style=create_div_style(fs=18)),

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
                ], style=create_div_style(mb=20))
            ]),

            html.Div([
                # label for slider
                html.Label('Set time offset between comparators 1 and 2 (+7 means comparator 2 shifts 7 days later)',
                           style=create_div_style(fs=18)),

                html.Div([
                # slider for choosing offset between comparators 1 and 2
                dcc.Slider(
                    id='offset_days',
                    min=-10,
                    max=10,
                    step=1,
                    marks={i: str(i) for i in range(-10, 11)},
                    value=0
                )
                ], style=create_div_style(mb=20))
            ]),

            html.Div([
                # label for checklist
                html.Label('Choose age groups',
                           style=create_div_style(fs=18)),

                dcc.Checklist(
                    id='age_gps',
                    options=[
                        {'label': '0-17 yrs', 'value': '0-17 yrs'},
                        {'label': '18-64 yrs', 'value': '18-64 yrs'},
                        {'label': '65-84 yrs', 'value': '65-84 yrs'},
                        {'label': '85+ yrs', 'value': '85+ yrs'}
                    ],
                    value=['65-84 yrs']),

            ], style=create_div_style(mb=20))
        ], style=create_div_style(w='32%')),

        # create div box for graphs
        html.Div([
            # graph1
            dcc.Graph(id='cumulative_vax_ppn'),
            dcc.Graph(id='compare_ratio')
        ], style=create_div_style(w='66%')),
    ])
])


# set callback to populate graph1
@app.callback(
    Output('cumulative_vax_ppn', 'figure'),
    [Input('start_date', 'value'),
     Input('age_gps', 'value')])
def update_graph1(start_date, age_gps):

    fig1 = go.Figure()

    df = vax_per_10k.copy()

    # convet start_date to datetime and pad df to start_date
    start_date = pd.to_datetime(dates[start_date])
    df = backfill_start(df, start_date)

    for col in age_gps:
        col1 = col + ' dose1'
        col2 = col + ' dose2'
        fig1.add_trace(go.Scatter(
            x=df.index,
            y=df[col1],
            mode='lines',
            name=col1
        )
        )

        fig1.add_trace(go.Scatter(
            x=df.index,
            y=df[col2],
            mode='lines',
            name=col2
        )
        )

    fig1.update_layout(
        xaxis={
            'title': 'date',
            'gridcolor': 'lightgrey'
        },
        yaxis={
            'title': 'vaccinated per 10,000',
            'gridcolor': 'lightgrey'
        },
        title={'text': 'Cumulative vaccinations dose 1 and dose 2',
               'x': 0.5, 'y': 0.98},
        margin={'l': 40, 'b': 40, 't': 30, 'r': 0},
        hovermode='closest',
        plot_bgcolor='white',
        height=400,
        legend = dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01)
    )

    return fig1

# set callback to populate graph2
@app.callback(
    Output('compare_ratio', 'figure'),
    [Input('start_date', 'value'),
     Input('rolling_avge_length', 'value'),
     Input('offset_days', 'value'),
     Input('age_gps', 'value')])
def update_graph2(start_date, rolling_avge_length, offset_days, age_gps):

    fig2 = go.Figure()

    df1 = admissions_per_10k.copy()
    df2 = cases_per_10k.copy()

    df1 = df1.shift(offset_days)

    # turn start_date to datetime
    start_date = pd.to_datetime(dates[start_date])

    df = get_ratio(df1, df2, start_date, rolling_avge_length)

    for col in age_gps:
        fig2.add_trace(go.Scatter(
            x=df.index,
            y=df[col],
            mode='lines',
            name=col + '      '
        )
        )

    fig2.update_layout(
        xaxis={
            'title': 'date',
            'gridcolor': 'lightgrey'
        },
        yaxis={
            'title': 'Admissions to cases ratio',
            'gridcolor': 'lightgrey'
        },
        title={'text': 'Admissions to cases ratio',
               'x': 0.5, 'y': 0.98},
        margin={'l': 40, 'b': 40, 't': 30, 'r': 0},
        hovermode='closest',
        plot_bgcolor='white',
        height=400,
        legend = dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01),
        showlegend=True
    )

    return fig2


if __name__ == '__main__':
    app.run_server(debug=True)
