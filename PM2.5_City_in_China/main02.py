import os
import pandas as pd
import numpy as np
import config
import mpld3
from mpld3 import plugins
from pyecharts import Bar

def preprocess_data(data_df, city_name):
    cln_data_df = data_df.dropna()
    cln_data_df = cln_data_df.reset_index(drop=True)
    cln_data_df['city'] = city_name

    print('There are totally {} data for {}, among which {} is valid data'.format(data_df.shape[0], city_name, cln_data_df.shape[0]))
    print('Preview for data in {}'.format(city_name))
    print(cln_data_df.head())

    return cln_data_df


def get_china_us_pm_df(cln_data_df, cols):
    pm_cols = ['PM_' + col for col in cols]
    cln_data_df['PM_China'] = cln_data_df[pm_cols].mean(axis=1)
    proc_data_df = cln_data_df[config.common_cols + ['city', 'PM_China']]

    print('Data preview: ')
    print(proc_data_df.head())

    return proc_data_df


def add_polluted_level(day_stats):
    proc_day_stats = day_stats.copy()
    bins = [-np.inf, 35, 75, 150, np.inf]
    level_labels = ['good', 'light', 'medium', 'heavy']

    proc_day_stats['Polluted level CH'] = pd.cut(proc_day_stats['PM_China'], bins=bins, labels=level_labels)
    proc_day_stats['Polluted level US'] = pd.cut(proc_day_stats['PM_US Post'], bins=bins, labels=level_labels)

    return proc_day_stats


def compare_stats_by_day_num(day_stats):
    city_names = config.data_config_dict.keys()
    city_comparison_result = []
    for city_name in city_names:
        city_df = day_stats[day_stats['city'] == city_name]
        city_polluted_days_count_ch = pd.value_counts(city_df['Polluted level CH']).to_frame(name=city_name + '_CH')
        city_polluted_days_count_us = pd.value_counts(city_df['Polluted level US']).to_frame(name=city_name + '_US')

        city_comparison_result.append(city_polluted_days_count_ch)
        city_comparison_result.append(city_polluted_days_count_us)

    comparison_result = pd.concat(city_comparison_result, axis=1)
    return comparison_result


def main():

    city_data_list = []

    for city_name, (filename, cols) in config.data_config_dict.items():
        # === Step 1. Import data ===
        data_file = os.path.join(config.dataset_path, filename)
        usecols = config.common_cols + ['PM_' + col for col in cols]
        data_df = pd.read_csv(data_file, usecols=usecols)

        # === Step 2. Data preprocess ===
        cln_data_df = preprocess_data(data_df, city_name)
        # Get PM2.5 data from China and US_Post
        proc_data_df = get_china_us_pm_df(cln_data_df, cols)
        city_data_list.append(proc_data_df)

    # After all city data are merged
    all_data_df = pd.concat(city_data_list)
    all_data_df[['year', 'month', 'day']] = all_data_df[['year', 'month', 'day']].astype('str')
    all_data_df['date'] = all_data_df['year'].str.cat([all_data_df['month'], all_data_df['day']], sep='-')
    all_data_df = all_data_df.drop(['year', 'month', 'day'], axis=1)
    all_data_df = all_data_df[['date', 'city', 'PM_China', 'PM_US Post']]

    # === Step 3. Data analysis ===
    day_stats = all_data_df.groupby(['city', 'date'])[['PM_China', 'PM_US Post']].mean()
    day_stats.reset_index(inplace=True)

    day_stats = add_polluted_level(day_stats)
    comparison_result = compare_stats_by_day_num(day_stats)

    # === Step 4. Output results ===
    all_data_df.to_csv(os.path.join(config.output_path, 'all_cities_pm.csv'), index=False)
    day_stats.to_csv(os.path.join(config.output_path, 'day_stats.csv'))
    comparison_result.to_csv(os.path.join(config.output_path, 'comparison_result.csv'))


if __name__ == '__main__':
    main()
