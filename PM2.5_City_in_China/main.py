import csv
import os
import numpy as np
import config


def load_data(data_file, usecols):

    data = []

    with open(data_file, 'r') as csvfile:
        data_reader = csv.DictReader(csvfile)
        # === Step 2. Clean data ===
        for row in data_reader:
            row_data = []
            # csv DictReader reads in string type data
            for col in usecols:
                str_val = row[col]
                row_data.append(float(str_val) if str_val != 'NA' else np.nan)

            # reserve data that does not contain NA
            if not any(np.isnan(row_data)):
                data.append(row_data)

    # transform data to ndarray
    data_arr = np.array(data)
    return data_arr

def polluted_percent(data_arr):
    hour_val = np.mean(data_arr[:, 3:], axis=1)
    n_hours = hour_val.shape[0]
    n_heavy_hours = hour_val[hour_val > 150].shape[0]
    n_medium_hours = hour_val[(hour_val > 75) & (hour_val <= 150)].shape[0]
    n_light_hours = hour_val[(hour_val > 35) & (hour_val <= 75)].shape[0]
    n_good_hours = hour_val[hour_val <= 35].shape[0]
    polluted_hour_percentage = [n_heavy_hours/n_hours, n_medium_hours/n_hours,
                                n_light_hours/n_hours, n_good_hours/n_hours]
    return polluted_hour_percentage

def avg_pm_per_month(data_arr):

    results = []

    years = np.unique(data_arr[:, 0])
    for year in years:
        year_data_arr = data_arr[data_arr[:, 0] == year]
        months = np.unique(year_data_arr[:, 1])
        for month in months:
            month_data_arr = year_data_arr[year_data_arr[:, 1] == month]
            month_avg = np.mean(month_data_arr[:, 3:], axis=0).tolist()

            row_data = ['{:.0f}-{:02.0f}'.format(year, month)] + month_avg
            results.append(row_data)

    results_arr = np.array(results)
    return results_arr

def sort_pollution_by_season(data_arr):

    years = np.unique(data_arr[:, 0])
    seasons_name = ['spring', 'summer', 'autumn', 'winter']
    season_dict = {}
    season_res = []

    for year in years:
        year_data_arr = data_arr[data_arr[:, 0] == year]
        seasons = np.unique(year_data_arr[:, 2])
        for season in seasons:
            season_data_arr = year_data_arr[year_data_arr[:, 2] == season]
            season_avg = np.mean(np.mean(season_data_arr[:, 3:], axis=1)[3:], axis=0)
            season_dict['{:.0f}-{}'.format(year, seasons_name[int(season)-1])] = format(season_avg, '.2f')

    for key, value in sorted(season_dict.items(), key=lambda item: (float(item[1]), item[0])):
        season_res.append((key, value))
    # for key, value in season_dict.items():
    #     season_res.append((key, value))

    season_res_arr = np.array(season_res)
    return season_res_arr

def save_stats_to_csv(result_arr, save_file, headers):
    with open(save_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for row in result_arr.tolist():
            writer.writerow(row)

def main():

    polluted_hour_percentage_list = []

    for city_name, (filename, cols) in config.data_config_dict.items():
        # === Step 1+2. Acquire data + clean data ===
        data_file = os.path.join(config.dataset_path, filename)
        usecols = config.common_cols + ['PM_' + col for col in cols]
        data_arr = load_data(data_file, usecols)

        print('There are {} valid data from {}'.format(data_arr.shape[0], city_name))
        print('Preview the first 10 data from {}'.format(city_name))
        print(data_arr[:10])

        # === Step 3. Data analysis ===
        # Cities polluted hours percentage
        polluted_hour_percentage = polluted_percent(data_arr)
        polluted_hour_percentage_list.append([city_name] + polluted_hour_percentage)
        print('The percentage of polluted hours for {} is {}:'.format(city_name, polluted_hour_percentage_list))

        # Monthly pollution condition for each district in each city_name
        monthly_result_arr = avg_pm_per_month(data_arr)
        print('Preview of monthly average PM2.5 for {}:'.format(city_name))
        print(monthly_result_arr[:10])

        # Sort polluted condition by season for each city
        sorted_by_season_arr = sort_pollution_by_season(data_arr)
        print('Sorted pollution by season for {}: {}'.format(city_name, sort_pollution_by_season))

        # === Step 4.1 Output for monthly pollution condition ===
        save_filename = city_name + '_month_stats.csv'
        save_file = os.path.join(config.output_path, save_filename)
        save_stats_to_csv(monthly_result_arr, save_file, headers=['month']+cols)
        print('Monthly pollution stats has been saved to {}'.format(save_file))
        #print()

        save_filename = city_name + '_season_sorted_stats.csv'
        save_file = os.path.join(config.output_path, save_filename)
        save_stats_to_csv(sorted_by_season_arr, save_file, headers=['year&season', 'PM2.5_avg'])
        print('Pollution stats sorted by season has been saved to {}'.format(save_file))


    # === Step 4.2 Output result ===
    save_file = os.path.join(config.output_path, 'hourly polluted percentage.csv')
    with open(save_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['city', 'heavy', 'medium', 'light', 'good'])
        for row in polluted_hour_percentage_list:
            writer.writerow(row)
    print('Hourly polluted percentage for each city has been saved to {}'.format(save_file))


if __name__ == '__main__':
    main()
