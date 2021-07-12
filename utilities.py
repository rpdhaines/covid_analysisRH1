### utility functions ###
import numpy as np
import pandas as pd


def create_pop_age_gps():
    population = pd.read_csv('2019_England_pop.csv')
    population.replace(to_replace='90+', value=90, inplace=True)
    population['age'] = population['age'].astype('int64')
    bins = [0, 17, 64, 84, 90]
    bin_labels = ['0-17 yrs', '18-64 yrs', '65-84 yrs', '85+ yrs']
    population['age_group'] = pd.cut(population['age'], bins=bins, labels=bin_labels, include_lowest=True)
    population.drop(columns='age', axis=1, inplace=True)
    population = population.groupby(by='age_group').sum().T

    return population

def get_pop_by_age(df, bin_list):
    bins, bin_labels = create_bins_labels(bin_list)

    df['age_group'] = pd.cut(df['age'], bins=bins, labels=bin_labels, include_lowest=True)
    df.drop(columns='age', axis=1, inplace=True)
    df = df.groupby(by='age_group').sum().T

    return df

def clean_case_data(df):
    df['date'] = pd.to_datetime(df['date'])

    # filter to post July cases to avoid very low summer period
    df = df[df['date'] > '2020-07-31']

    # filter to age values to be kept
    age_gps = ['00_04', '05_09', '10_14', '15_19',
               '20_24', '25_29', '30_34', '35_39',
               '40_44', '45_49', '50_54', '55_59',
               '60_64', '65_69', '70_74', '75_79',
               '80_84', '85_89', '90+']

    df = df[df['age'].isin(age_gps)]

    # filter to columns to be kept
    cols_to_keep = ['areaName', 'date', 'age', 'cases']
    df = df[cols_to_keep].copy()

    return df


def get_case_age_gps(df):
    df.drop('areaName', axis=1, inplace=True)

    # create df pivot by age
    df = df.groupby(by=['date', 'age']).sum().unstack()
    df.columns = df.columns.droplevel()

    # create list of starting cols to drop later
    starting_cols = df.columns.values.tolist()

    # set age groups to 0-17, 18-64, 65-84 and 85+ (to match only available admissions split)
    cols_0014 = ['00_04', '05_09', '10_14']
    cols_2064 = [f'{5 * i}_{5 * (i + 1) - 1}' for i in range(4, 13)]
    cols_6584 = [f'{5 * i}_{5 * (i + 1) - 1}' for i in range(13, 17)]
    cols_85plus = ['85_89', '90+']
    df['0-17 yrs'] = df[cols_0014].sum(axis=1) + 0.6 * df['15_19']
    df['18-64 yrs'] = 0.4 * df['15_19'] + df[cols_2064].sum(axis=1)
    df['65-84 yrs'] = df[cols_6584].sum(axis=1)
    df['85+ yrs'] = df[cols_85plus].sum(axis=1)

    # drop original cols
    df.drop(starting_cols, axis=1, inplace=True)

    return df

def prepare_case_data(df):
    # from utilities import clean_case_data, get_case_age_gps, create_pop_age_gps

    cases_per_10k = clean_case_data(df)
    cases_per_10k = get_case_age_gps(cases_per_10k)

    population = create_pop_age_gps()
    
    # multiply every row in cases df by the population multipliers by applying .mul to population turned into a series
    cases_per_10k = cases_per_10k.div(population.iloc[0], axis='columns')

    cases_per_10k = cases_per_10k * 10000
    
    return cases_per_10k

def clean_vax_data(df):
    df['date'] = pd.to_datetime(df['date'])

    # filter to post July cases to avoid very low summer period
    df = df[df['date'] > '2020-07-31']

    # filter to columns to be kept
    cols_to_keep = ['date',
                    'age',
                    'cumPeopleVaccinatedFirstDoseByVaccinationDate',
                    'cumPeopleVaccinatedSecondDoseByVaccinationDate']
    df = df[cols_to_keep].copy()

    return df

def set_vax_age_gps(df):
    # create separate first dose and second dose dataframes
    first_dose = df.drop('cumPeopleVaccinatedSecondDoseByVaccinationDate', axis=1)
    second_dose = df.drop('cumPeopleVaccinatedFirstDoseByVaccinationDate', axis=1)

    # helper function to create pivoted vax data by required age groups
    def group_vax(vax_df):
        # create first dose pivot by age
        vax_df = vax_df.groupby(by=['date', 'age']).sum().unstack()
        vax_df.columns = vax_df.columns.droplevel()

        starting_cols = vax_df.columns.values.tolist()

        # set age groups to 0-17, 18-64, 65-84 and 85+ (to match only available admissions split)
        vax_df['0-17 yrs'] = 0
        cols_1864 = ['18_24'] + [f'{5*i}_{5*(i+1) - 1}' for i in range(5,13)]
        cols_6584 = [f'{5*i}_{5*(i+1) - 1}' for i in range(13,17)]
        cols_85plus = ['85_89', '90+']
        vax_df['18-64 yrs'] = vax_df[cols_1864].sum(axis=1)
        vax_df['65-84 yrs'] = vax_df[cols_6584].sum(axis=1)
        vax_df['85+ yrs'] = vax_df[cols_85plus].sum(axis=1)

        # drop original cols
        vax_df.drop(starting_cols, axis=1, inplace=True)

        return vax_df

    # create first dose pivot by age
    first_dose = group_vax(first_dose)

    # create second dose pivot by age
    second_dose = group_vax(second_dose)

    return first_dose, second_dose


def prepare_vax_data(df):
    vax_data = clean_vax_data(df)
    dose1, dose2 = set_vax_age_gps(vax_data)
    
    population = create_pop_age_gps()

    # multiply every row in vax df by the population multipliers by applying .mul to population turned into a series
    dose1 = dose1.div(population.iloc[0], axis='columns')
    dose1 = dose1 * 10000

    dose2 = dose2.div(population.iloc[0], axis='columns')
    dose2 = dose2 * 10000

    dose1_2 = dose1.merge(dose2, how='inner', left_index=True, right_index=True, suffixes=(' dose1', ' dose2'))

    return dose1_2

def clean_admission_data(df):
    df['date'] = pd.to_datetime(df['date'])

    # filter to post July cases to avoid very low summer period
    df = df[df['date'] > '2020-07-31']

    # filter to columns to be kept
    cols_to_keep = ['date', 'age', 'value']
    df = df[cols_to_keep].copy()

    return df

def admissions_cum_to_new(df):
    df = df.groupby(by=['date', 'age']).sum().unstack()
    df.columns = df.columns.droplevel()

    df = df - df.shift(1)

    return df

def set_admissions_age_gps(df):
    df['0-17 yrs'] = df['0_to_5'] + df['6_to_17']
    col_name_map = {'18_to_64' : '18-64 yrs',
                    '65_to_84' : '65-84 yrs',
                    '85+' : '85+ yrs'}
    df.rename(columns=col_name_map, inplace=True)
    cols_to_drop = ['0_to_5', '6_to_17']
    df.drop(cols_to_drop, axis=1, inplace=True)

    return df


def prepare_admissions_data(df):
    admissions_per_10k = clean_admission_data(df)
    admissions_per_10k = admissions_cum_to_new(admissions_per_10k)
    admissions_per_10k = set_admissions_age_gps(admissions_per_10k)

    population = create_pop_age_gps()

    # multiply every row in cases df by the population multipliers by applying .mul to population turned into a series
    admissions_per_10k = admissions_per_10k.div(population.iloc[0], axis='columns')

    admissions_per_10k = admissions_per_10k * 10000

    return admissions_per_10k

def bin_ages(df, *args):
    # requires ages in multiples of less than 5, highest one 90 or less
    # add col with start age of age col
    df['start_age'] = df['age'].apply(lambda x: int(x[:2]))

    # convert tuple into array and order
    bins = np.asarray(args)
    bins = np.sort(bins)

    # create array including 0 and order
    bins_with_0 = np.append(bins, 0)
    bins_with_0_120 = np.append(bins_with_0, 120)
    bins_with_0_120 = np.sort(bins_with_0_120)

    bin_labels = [str(bins_with_0_120[x]) + "-" + str(bins_with_0_120[x + 1] - 1) + " yrs" for x in range(len(bins_with_0_120) - 2)]
    bin_labels.append(f'{bins_with_0_120[-2]}+ yrs')
    df['age_group'] = pd.cut(x=df['start_age'], bins=bins_with_0_120.tolist(), right=False, labels=bin_labels)

    return df

def create_bins_labels(bin_list):
    # ensure bin_list in order
    bin_list = np.array(bin_list)
    bin_list = np.sort(bin_list).tolist()

    # create full list with 0 and 120 on ends
    bins = [0]
    for i in range(len(bin_list)):
        bins.append(bin_list[i])
    bins.append(120)

    bin_labels = [str(bins[x]) + "-" + str(bins[x + 1] - 1) + " yrs" for x in range(len(bins) - 2)]
    bin_labels.append(f'{bins[-2]}+ yrs')

    return bins, bin_labels

def bin_ages_from_list(df, bin_list):
    df['start_age'] = df['age'].apply(lambda x: int(x[:2]))

    bins, bin_labels = create_bins_labels(bin_list)

    df['age_group'] = pd.cut(x=df['start_age'], bins=bins, right=False, labels=bin_labels)

    return df

def equalise_end_dates(*args):
    """
    function to cut end date of set of datetime dfs to be the earliest last date within the set of dataframes passed
    :param args: must all be dataframes with datetime indices
    :return: dataframes with equalised end-dates, wrapped in a list
    """

    end_dates = [df.index[-1] for df in args]
    earliest_end_date = min(end_dates)

    df_list = [df.loc[:earliest_end_date] for df in args]

    return df_list

def backfill_start(df, start_date):
    """
    create earlier rows in dataframe filled with nans from an earlier start date than that in the df
    :param df: dataframe with datetime index and first date later than the start date
    :param start_date: datetime - chosen start date to backfill to
    :return: df with additional nan rows from new start date to original start date, and same rows thereafter
    """

    new_index = pd.date_range(start=start_date, end=df.index[-1], freq='D')
    df = df.reindex(new_index)

    return df

def get_ratio(df1, df2, start_date, rolling=7):

    # cut to start date (assumes start date already datetime)
    # assumes end date of dfs already matches
    df1 = df1.loc[start_date:]
    df2 = df2.loc[start_date:]
    
    # create rolling avge dfs
    df1 = df1.rolling(rolling).mean()
    df2 = df2.rolling(rolling).mean()
    
    # create ratio df
    ratio = df1 / df2
    
    return ratio

def get_region_pop(df, region, age_bins_list):
    """
    from population by single and and region df, create df by given age groups for given region
    :param df: dataframe containing population data. expected to be in the form loaded from '2019_pop_by_region.csv'
    :param region: chosen England region to filter population by. if set to 'England', sums all regions
    :param age_bins_list: list of integer age group dividers - expected to be in the form from the age_group checklist
    :return: df with single row for required region, and a column for eag required age group, containing population
    """
    if region == 'England':
        region_pop = pd.DataFrame(df.sum(axis=0)).T
    else:
        region_pop = df[df['Name'] == region].copy()


    cols_to_drop = region_pop.copy().columns
    bins, bin_labels = create_bins_labels(age_bins_list)

    # create new columns with population for age groups
    for i in range(len(bins)-2):
        sum_cols = [str(j) for j in range(bins[i], bins[i+1])]
        region_pop[bin_labels[i]] = region_pop[sum_cols].sum(axis=1)

    #special case for last age group, to allow for it possibly being 90
    if bins[-2] == 90:
        region_pop[bin_labels[-1]] = region_pop['90+']
    else:
        sum_cols = [str(j) for j in range(bins[-2], 90)]
        sum_cols.append('90+')
        region_pop[bin_labels[-1]] = region_pop[sum_cols].sum(axis=1)

    region_pop.set_index('Name', drop=False, inplace=True)
    region_pop.drop(columns=cols_to_drop, axis=1, inplace=True)

    return region_pop

def get_df_per_pop(df, pop_df, per=10000):
    """
    helper fn to turn df with pure numbers in numbers per x of population
    :param df: df with numbers (eg cases). assumes columns match columns for pop_df
    :param pop_df: df with pop numbers in. assumes 1 row and columns match those for df
    :param per: int - set per 'what' of population. default =10,000
    :return: df of same shape as df, with number converted to per x of population
    """
    df_per_pop = df.div(pop_df.iloc[0], axis='columns')

    df_per_pop = df_per_pop * per

    return df_per_pop


def get_rolling_total(df, start_date, end_date, rolling=1):
    """
    cut df to between start and end date, apply rolling average and then sum df cols
    :param df: dataframe - datetime index and only columns you want to sum
    :param start_date: datetime - start date to cut index by
    :param end_date: datetime - end date to cut index by
    :param rolling: int - rolling average window length
    :return:
    """
    # cut to start and end date (assumes start date already datetime)
    # assumes end date of dfs already matches
    df = df.loc[start_date: end_date]

    # create rolling avge dfs
    df = df.rolling(rolling).mean()

    # create sum column
    df['total'] = df.sum(axis=1)

    return pd.DataFrame(df['total'])