# utility functions used to do chunks of database manipulation. most functions are tailored
# to the specifics of this app

import numpy as np
import pandas as pd
from pandas.tseries.offsets import DateOffset


def create_pop_age_gps():
    """
    function specifically for getting England population split by the age groups that hospital
    admissions are provided in, from the 2019 population file which is housed in the root folder
    :return: dataframe with a single row of population figures, columns are the age groups
    """

    # read in population file
    population = pd.read_csv('2019_England_pop.csv')

    # tidy data
    population.replace(to_replace='90+', value=90, inplace=True)
    population['age'] = population['age'].astype('int64')

    # create age-group columns for age groups in which the admissions data is provided
    bins = [0, 17, 64, 84, 90]
    bin_labels = ['0-17 yrs', '18-64 yrs', '65-84 yrs', '85+ yrs']
    population['age_group'] = pd.cut(population['age'], bins=bins, labels=bin_labels, include_lowest=True)
    population.drop(columns='age', axis=1, inplace=True)
    # as the only cols left are age group and population, a simple groupby and transpose gives us the df in
    # desired form
    population = population.groupby(by='age_group').sum().T

    return population


def clean_case_data(df):
    """
    takes loaded cases dataframe in expected format and tidies it to remove early dates and unwanted cols etc
    :param df: DataFrame - expect in format of loaded cases data
    :return:
    """
    # ensure date column is DateTime
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
    """
    takes tidied case datframe and returns one with columns for age groups
    :param df: Dataframe - expects tidied case df
    :return: Dataframe - rows are dates, columns are cases by age group (hospital admissions groupings)
    """
    # 'areaName' col can be dropped for this purpose
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
    # approximate split of the 15-19 age group given in the case date to 15-17 an 18-19
    df['0-17 yrs'] = df[cols_0014].sum(axis=1) + 0.6 * df['15_19']
    df['18-64 yrs'] = 0.4 * df['15_19'] + df[cols_2064].sum(axis=1)
    df['65-84 yrs'] = df[cols_6584].sum(axis=1)
    df['85+ yrs'] = df[cols_85plus].sum(axis=1)

    # drop original cols
    df.drop(starting_cols, axis=1, inplace=True)

    return df


def prepare_case_data(df):
    """
    wrapper function to wrangle population and case data to required format and create a 'cases per 10k' file
    :param df: Dataframe - expected in the form of the England cases data file on .gov website
    :return: Dataframe - rows are dates and cols are age groups. data is cases per 10k of population
    """

    # clean case data and put into age groups
    cases_per_10k = clean_case_data(df)
    cases_per_10k = get_case_age_gps(cases_per_10k)

    # put population data into age groups
    population = create_pop_age_gps()
    
    # multiply every row in cases df by the population multipliers by applying .mul to population
    # turned into a series, and multiply up by 10,000
    cases_per_10k = cases_per_10k.div(population.iloc[0], axis='columns')
    cases_per_10k = cases_per_10k * 10000
    
    return cases_per_10k


def clean_vax_data(df):
    """
    apply some tidy to raw loaded vaccinations dataframe
    :param df: DataFrame - expected in form of vaccinations data downloaded from .gov website
    :return: DataFrame - rows are dates, only necessary columns kept
    """
    # ensure dates are DateTime
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
    """
    create vaccinations data by (hospital admissions) age_groups
    :param df: DataFrame - expects cleaned vaccinations data
    :return: 2 DataFrames - rows are dates, columns are age_groups for dose 1 cumulative vaccinated
    and dose 2 cumulative vaccinated
    """
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
    """
    wrapper function to create cumulative vaccinations per 10k of population
    :param df: DataFrame - expected in form of vaccinations data downloaded from .gov website
    :return: Dataframe - rows are data and columns are dose1 age groups and dose2 age groups. data
    is cumulative vaccinations per 10K of population
    """
    # create vax data by age groups
    vax_data = clean_vax_data(df)
    dose1, dose2 = set_vax_age_gps(vax_data)

    # create population by age group
    population = create_pop_age_gps()

    # multiply every row in vax df by the population multipliers by applying .mul to population turned into a series
    dose1 = dose1.div(population.iloc[0], axis='columns')
    dose1 = dose1 * 10000

    dose2 = dose2.div(population.iloc[0], axis='columns')
    dose2 = dose2 * 10000

    dose1_2 = dose1.merge(dose2, how='inner', left_index=True, right_index=True, suffixes=(' dose1', ' dose2'))

    return dose1_2


def clean_admission_data(df):
    """
    apply some tidy to raw loaded hospital admissions dataframe
    :param df: DataFrame - expected in form of admissions data downloaded from .gov website
    :return: DataFrame - rows are dates, only necessary columns kept
    """
    # ensure date is DateTime
    df['date'] = pd.to_datetime(df['date'])

    # filter to post July cases to avoid very low summer period
    df = df[df['date'] > '2020-07-31']

    # filter to columns to be kept
    cols_to_keep = ['date', 'age', 'value']
    df = df[cols_to_keep].copy()

    return df


def admissions_cum_to_new(df):
    """
    admissions data only comes as cumulative. this function converts this to new admissions each day
    :param df: DataFrame - expects cleaned admissions data
    :return:
    """
    # create column of cumulative admissions by age
    df = df.groupby(by=['date', 'age']).sum().unstack()
    df.columns = df.columns.droplevel()

    # calculate new admissions as cumulative admissions today less cumulative admissions yesterday
    df = df - df.shift(1)

    return df


def set_admissions_age_gps(df):
    """
    create admissions data by age_groups
    :param df: DataFrame - expects cleaned 'daily new admissions' data
    :return: DataFrames - rows are dates, columns are age_groups
    """
    # admissions already essentially in the right age groups - just need to combine the 2 youngest age groups
    df['0-17 yrs'] = df['0_to_5'] + df['6_to_17']

    # rename columns for consistency and drop unnecessary ones
    col_name_map = {'18_to_64' : '18-64 yrs',
                    '65_to_84' : '65-84 yrs',
                    '85+' : '85+ yrs'}
    df.rename(columns=col_name_map, inplace=True)
    cols_to_drop = ['0_to_5', '6_to_17']
    df.drop(cols_to_drop, axis=1, inplace=True)

    return df


def prepare_admissions_data(df):
    """
    wrapper function to create new hospital admissions per 10k of population
    :param df: DataFrame - expected in form of hospital admissions data downloaded from .gov website
    :return: Dataframe - rows are data and columns are age groups. data is hospital admissions
    per 10K of population
    """

    # use helper functions to clean data and put into age groups
    admissions_per_10k = clean_admission_data(df)
    admissions_per_10k = admissions_cum_to_new(admissions_per_10k)
    admissions_per_10k = set_admissions_age_gps(admissions_per_10k)

    # create population by age group
    population = create_pop_age_gps()

    # multiply every row in cases df by the population multipliers by applying .mul to population
    # turned into a series
    admissions_per_10k = admissions_per_10k.div(population.iloc[0], axis='columns')

    admissions_per_10k = admissions_per_10k * 10000

    return admissions_per_10k


def create_bins_labels(bin_list):
    """
    helper function to create list of age group labels for given set of bin edges
    :param bin_list: List - bin edges. Assumes excludes 0, and maximum is below 120
    :return: 2 Lists - the first being the full list of bin edges including 0 and 120, and
    the second being age group labels in the form 'x-y yrs'
    """
    # ensure bin_list in order
    bin_list = np.array(bin_list)
    bin_list = np.sort(bin_list).tolist()

    # create full list with 0 and 120 on ends
    bins = [0]
    for i in range(len(bin_list)):
        bins.append(bin_list[i])
    bins.append(120)

    # create list of bin labels
    bin_labels = [str(bins[x]) + "-" + str(bins[x + 1] - 1) + " yrs" for x in range(len(bins) - 2)]
    bin_labels.append(f'{bins[-2]}+ yrs')

    return bins, bin_labels


def bin_ages_from_list(df, bin_list):
    """
    helper function to create age group columns in a dataframe for given age group edges
    :param df: DataFrame - expects cleaned cases by age and region dataframe
    :param bin_list: List - age group edges - expected to exclude 0 and maximum age to be below 120
    :return: DataFrame - original df with extra columns for 'start age' of the age group and a column with the
    age group label
    """
    # expecting age labels to be in a form where the first 2 characters are the starting age for that band
    # eg 05to10.
    df['start_age'] = df['age'].apply(lambda x: int(x[:2]))

    # create full bin list and labels, and create age_group column using pd.cut
    bins, bin_labels = create_bins_labels(bin_list)
    df['age_group'] = pd.cut(x=df['start_age'], bins=bins, right=False, labels=bin_labels)

    return df


def equalise_end_dates(*args):
    """
    function to cut end date of set of datetime dfs to be the earliest last date within the set of dataframes passed
    :param args: must all be dataframes with datetime indices with latest date at bottom
    :return: dataframes with equalised end-dates, wrapped in a list
    """

    # get list of all end dates in indices of passed dataframes
    end_dates = [df.index[-1] for df in args]

    # find the earliest end date
    earliest_end_date = min(end_dates)

    # create list of dataframes all sliced to finish at earliest end date
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
    """
    takes ratio of 2 dataframes with identical shape and column order, after first taking a rolling average,
    and then slices to begin at start_date
    :param df1: DataFrame - with same columns in same order as df2
    :param df2: DataFrame - with same columns in same order as df1
    :param start_date: DateTime - needs to be later than the start date of the dfs, which is currently set to
    1 August 2020
    :param rolling: Int - length of window for rolling average
    :return: DataFrame - same columns as df1 and df2, with values being ratio of the rolling avges, sliced to
    begin at passed start_date
    """

    # create rolling avge dfs
    df1 = df1.rolling(rolling).mean()
    df2 = df2.rolling(rolling).mean()
    
    # create ratio df
    ratio = df1 / df2

    # cut to start date (assumes start date already datetime)
    # assumes end date of dfs already matches
    ratio = ratio.loc[start_date:]
    
    return ratio


def get_region_pop(df, region, age_bins_list):
    """
    from population by single and and region df, create df by given age groups for given region
    :param df: dataframe containing population data. expected to be in the form loaded from '2019_pop_by_region.csv'
    :param region: chosen England region to filter population by. if set to 'England', sums all regions
    :param age_bins_list: list of integer age group dividers - expected to be in the form from the age_group checklist
    :return: df with single row for required region, and a column for eag required age group, containing population
    """
    # allow for special case of region being England, requiring a sum of all regions, else just slice to region
    if region == 'England':
        region_pop = pd.DataFrame(df.sum(axis=0)).T
    else:
        region_pop = df[df['Name'] == region].copy()

    # new cols will be created which will be the ones to keep, after which the starting columns can all be dropped
    cols_to_drop = region_pop.copy().columns

    # create bins and bin labels for age groups
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

    # turn region name column into index. don't drop as it is in the list of cols to drop in the next step
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
    apply rolling average and then sum df cols, cut df to between start and end date
    :param df: dataframe - datetime index and only columns you want to sum
    :param start_date: datetime - start date to cut index by
    :param end_date: datetime - end date to cut index by
    :param rolling: int - rolling average window length
    :return:
    """

    # create rolling avge dfs
    df = pd.DataFrame(df.rolling(rolling).mean())

    # create sum column
    df['total'] = df.sum(axis=1)

    # cut to start and end date (assumes start date already datetime)
    # assumes end date of dfs already matches
    df = df.loc[start_date: end_date]

    return pd.DataFrame(df['total'])


def get_month_starts(start_date, end_date):
    """
    get list of dates which will be the 1st of every month from the start-date month to end-date month
    :param start_date: Datetime - date to start list with first of month
    :param end_date: Datetime - date to end list with first of month
    :return: list of first of months
    """

    # change start and end date to be first of the month
    start_date = start_date.replace(day=1)
    end_date = end_date.replace(day=1)

    # count number of months between start and end
    num_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

    # create a list of dates all being 1st of month, ending with the 1st of the month of end-date
    dates = [start_date + DateOffset(months=x) for x in range(num_months+1)]

    return dates