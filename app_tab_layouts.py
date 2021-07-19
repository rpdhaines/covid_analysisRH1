# contains children layouts for tabs in main app file

# make necessary imports
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from style_creator import create_div_style
from utilities import *
from info_boxes import *

# read in Govt cases data
cases_by_age_region = pd.read_csv("https://api.coronavirus.data.gov.uk/v2/data?areaType=region&metric=newCasesBySpecimenDateAgeDemographics&format=csv")

# read in population data
pop_by_region = pd.read_csv("2019_pop_by_region.csv")

# data tidying
cases_by_age_region = clean_case_data(cases_by_age_region)

# read in Govt cases data for England not split by region
cases_by_age = pd.read_csv("https://api.coronavirus.data.gov.uk/v2/data?areaType=nation&areaCode=E92000001&metric=newCasesBySpecimenDateAgeDemographics&format=csv")

# read in Govt vaccines data for England
vaccines_by_age = pd.read_csv("https://api.coronavirus.data.gov.uk/v2/data?areaType=nation&areaCode=E92000001&metric=vaccinationsAgeDemographics&format=csv")

# read in Govt hospital admissions data for England
cum_admissions_by_age = pd.read_csv("https://api.coronavirus.data.gov.uk/v2/data?areaType=nation&areaCode=E92000001&metric=cumAdmissionsByAge&format=csv")

# data tidying
cases_per_10k = prepare_case_data(cases_by_age)

vax_per_10k = prepare_vax_data(vaccines_by_age)

admissions_per_10k = prepare_admissions_data(cum_admissions_by_age)

# equalise end dates
df_list = equalise_end_dates(cases_per_10k, vax_per_10k, admissions_per_10k)
cases_per_10k = df_list[0].copy()
vax_per_10k = df_list[1].copy()
admissions_per_10k = df_list[2].copy()

# create list of region names
region_names = cases_by_age_region['areaName'].unique().tolist()
region_names.append('England')

# create list of monthly date labels for starting date up to and including last available equalised dates
start_date = pd.to_datetime("2020-08-01")
end_date = cases_per_10k.index[-1]
dates = get_month_starts(start_date, end_date)
dates.append(end_date)

# create lists to use to select columns in eventual dataframe
groupings = ['date', 'age_group', 'areaName']
groups_and_cases = ['date', 'age_group', 'areaName', 'cases']

national_groupings = ['date', 'age_group']
national_groups_and_cases = ['date', 'age_group', 'cases']

# create layout for tab 0
tab0_layout = html.Div([
    dcc.Markdown(tab0_info)
], style=create_div_style(fs=16, ml=8, borderb='black solid 1px', bordert='black solid 1px'))

# create layout for tab 1
tab1_layout = html.Div([

            dcc.Markdown("""
            #### Exploration of case levels and case growth. As well as varying region and age groups, you can play with some smoothing parameters as described below.
            """, style=create_div_style(borderb='black solid 1px')),

            # create div box for all options
            html.Div([
                # label for dropdown
                html.Label('Choose region',
                           style=create_div_style(fs=18, mr=10)),

                # dropdown for choosing Region
                dcc.Dropdown(
                    id='Region',
                    options=[{'label': i, 'value': i} for i in region_names],
                    value='England',
                    style=create_div_style(mb=5, mr=10, w='90%', fs=16)
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
                            max=len(dates)-1,
                            step=1,
                            marks={2*i: dates[2*i].strftime('%Y-%m-%d') for i in range(int((len(dates) / 2) + 1))},
                            value=3
                        )
                    ], style=create_div_style(mb=5))

                ]),

                html.Div([
                    # label for slider
                    html.Label('Set size of rolling average window for cases (in weeks)',
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
                        marks={i*7: f'{str(i)} weeks' for i in range(1, 4)},
                        value=7
                    )
                    ], style=create_div_style(mb=5))
                ]),

                html.Div([
                    # label for slider
                    html.Label('Set length of time to calculate average daily growth rate over',
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
                    ], style=create_div_style(mb=5))
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
                    ], style=create_div_style(mb=5))
                ]),

                html.Div([
                    # label for checklist
                    html.Label('Choose age group dividers',
                               style=create_div_style(fs=18)),

                    dcc.Markdown('''
                    Check all boxes you want to use as start and end of age group ranges.
                    Eg just choosing 40 will create 2 groups: 0-39 yrs and 40+ yrs''',
                                 style=create_div_style(fs=14, w='95%')),

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
            ], style=create_div_style(w='32%', borderr='solid black 1px')),

            # create div box for info boxes and graphs
            html.Div([

                # info box
                html.Div([
                    dash_table.DataTable(
                        id='table',
                        columns=[{"name": 'Hover here for case discussion', "id": 'col_1'},
                                 {"name": 'Hover here for growth rate discussion', 'id': 'col_2'}],
                        style_cell={'textAlign': 'center', 'font_family': 'Arial'},
                        tooltip_header={'col_1': {'value': box1_1, 'type': 'markdown'},
                                        'col_2': {'value': box1_2, 'type': 'markdown'}},
                        tooltip_duration=None
                    )
                ], style=create_div_style(fs=20, borderb='solid black 1px',
                                                 borderl='solid black 1px', borderr='solid black 1px',
                                                 bordert='solid black 1px')),

                html.Div([

                    dcc.Graph(id='cases_per_10,000_by_age_group'),
                    dcc.Graph(id='daily_growth_rate_by_age_group')
                    ], style=create_div_style())
            ], style=create_div_style(w='66%')),
        ])

# layout for tab 2
tab2_layout = html.Div([


    dcc.Markdown("""
    #### Explore vaccination coverage vs hospital admission to case ratio. As well as varying the date range and rolling average length, you can vary the 'lag' as described below.
    """, style=create_div_style(borderb='black solid 1px')),

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
                    max=len(dates) - 1,
                    step=1,
                    marks={2*i: dates[2*i].strftime('%Y-%m-%d') for i in range(int((len(dates) / 2) + 1))},
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
                value=14
            )
            ], style=create_div_style(mb=20))
        ]),

        html.Div([
            # label for slider
            html.Label('Set time lag between cases and admissions (7 means compare cases to admissions 7 days later)',
                       style=create_div_style(fs=18, w='95%')),

            html.Div([
            # slider for choosing lag between cases and admissions
            dcc.Slider(
                id='offset_days',
                min=0,
                max=15,
                step=1,
                marks={i: str(i) for i in range(16)},
                value=7
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

        # info box
        html.Div([
            dash_table.DataTable(
                id='table',
                columns=[{"name": 'Hover here for discussion', "id": 'col_1'},
                         {"name": 'Offset parameter', "id": 'col_2'}],
                style_cell={'textAlign': 'center', 'font_family': 'Arial'},
                tooltip_header={'col_1': {'value': box2_1, 'type': 'markdown'},
                                'col_2': {'value': box2_2, 'type': 'markdown'}},
                tooltip_duration=None
#                 css=[{'selector': '.dash-table-tooltip',
#                       'rule': 'width: 350px !important; max-width: 350px !important;'}]
            )
        ], style=create_div_style(fs=20, borderb='solid black 1px',
                                  borderl='solid black 1px', borderr='solid black 1px',
                                  bordert='solid black 1px')),

        # graphs
        html.Div([
            dcc.Graph(id='cumulative_vax_ppn'),
            dcc.Graph(id='compare_ratio')
            ], style=create_div_style())
    ], style=create_div_style(w='66%', borderl='black solid 1px'))
])

# layout for tab 3
tab3_layout = html.Div([


    dcc.Markdown("""
    #### Explore lag between cases and admissions. As well as varying the date range and lag length, different age group combinations can be selected.
    """, style=create_div_style(borderb='black solid 1px')),

    # create div box for all options
    html.Div([

        # first create a div box for it as it seems to be the only way to set margins for it
        html.Div([
            # label for RangeSlider
            html.Label('Set date range to consider',
                       style=create_div_style(fs=18)),

            #create another div box to house the slider itself as you can't set the margins or style elements
            # as part of the slider component itself

            html.Div([
                # Range slider for setting earliest date considered
                dcc.RangeSlider(
                    id='date_range',
                    min=0,
                    max=len(dates) - 1,
                    step=1,
                    marks={2*i: dates[2*i].strftime('%Y-%m-%d') for i in range(int((len(dates) / 2) + 1))},
                    value=[3, len(dates)-1]
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
                value=14
            )
            ], style=create_div_style(mb=20))
        ]),

        html.Div([
            # label for slider
            html.Label('Set the lag between cases and admissions you would like to analyse',
                       style=create_div_style(fs=18)),

            html.Div([
            # slider for choosing lag between cases and admissions
            dcc.Slider(
                id='admission_lag',
                min=0,
                max=15,
                step=1,
                marks={i: str(i) for i in range(16)},
                value=7
            )
            ], style=create_div_style(mb=20))
        ]),

        html.Div([
            # label for checklist
            html.Label('Choose age group',
                       style=create_div_style(fs=18)),

            dcc.RadioItems(
                id='age_gps',
                options=[
                    {'label': '0-17 yrs', 'value': '0-17 yrs'},
                    {'label': '18-64 yrs', 'value': '18-64 yrs'},
                    {'label': '65-84 yrs', 'value': '65-84 yrs'},
                    {'label': '85+ yrs', 'value': '85+ yrs'}
                ],
                value='65-84 yrs'),

        ], style=create_div_style(mb=20)),

        html.Div([
            # label for checklist
            html.Label('Choose scatter colour-scale',
                       style=create_div_style(fs=18)),

            dcc.RadioItems(
                id='scatter_colour',
                options=[
                    {'label': 'date', 'value': 'date'},
                    {'label': 'dose 1 coverage', 'value': 'dose1'},
                    {'label': 'dose 2 coverage', 'value': 'dose2'}
                ],
                value='date'),

        ], style=create_div_style(mb=20))

    ], style=create_div_style(w='32%')),

    # create div box for graphs and info boxes
    html.Div([
        # info box
        html.Div([
            dash_table.DataTable(
                id='table',
                columns=[{"name": 'Hover for discussion on lag', "id": 'col_1'},
                         {"name": 'Emergence of Alpha variant', "id": 'col_2'},
                         {"name": 'Impact of vaccination', "id": 'col_3'}],
                style_cell={'textAlign': 'center', 'font_family': 'Arial'},
                tooltip_header={'col_1': {'value': box3_1, 'type': 'markdown'},
                                'col_2': {'value': box3_2, 'type': 'markdown'},
                                'col_3': {'value': box3_3, 'type': 'markdown'}},
                tooltip_duration=None
#                 css=[{'selector': '.dash-table-tooltip',
#                       'rule': 'width: 350px !important; max-width: 350px !important;'}]
            )
        ], style=create_div_style(fs=20, borderb='solid black 1px',
                                  borderl='solid black 1px', borderr='solid black 1px',
                                  bordert='solid black 1px')),

        html.Div([
            html.Div([
                # placeholder for scatter graph
                dcc.Graph(id='admission-vs-case-scatter')
                # set width of Div bo to 49%% to put 2 further graphs on RHS
                ], style=create_div_style(w='49%', display='inline-block')),
            # div box for housing 2 further graphs
            html.Div([
                # placeholder for graph of cases to admissions ratio for given lag
                dcc.Graph(id='admission-case-ratio'),
                # placeholder for graph of overlaid case and admission numbers for given lag
                dcc.Graph(id='admission-case-overlay')
                # set width of Div box to 49% and push to RHS
                ], style=create_div_style(w='49%', display='inline-block', float='right'))
            ])
        ], style=create_div_style(w='66%', borderl='black solid 1px'))
])
