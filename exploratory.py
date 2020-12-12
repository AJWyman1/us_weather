import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from colour import Color


def longest_drought(df):
    # takes in a dataframe and returns an int of the longest
    # span of consecutive days with light or less rain fall
    max_days = 0
    running_count = 0
    for rain in df.actual_precipitation:
        if rain < 0.05:
            running_count += 1
        else:
            if running_count > max_days:
                max_days = running_count
            running_count = 0
    return max_days


def get_change_in_average(df):
    # Gets means for all columns
    year_df = df.groupby(['location']).mean().reset_index()

    # Get the averages for historical and current data
    year_avg_min = year_df.actual_min_temp[0]
    year_avg_max = year_df.actual_max_temp[0]
    historical_max_avg = year_df.average_max_temp[0]
    historical_min_avg = year_df.average_min_temp[0]

    # Finds the difference
    delta_max = year_avg_max - historical_max_avg
    delta_min = year_avg_min - historical_min_avg

    return delta_max, delta_min


def load_and_transform(path):
    # Loads the data
    df = pd.read_csv(path+'.csv')

    # Adds needed columns and converts str to datetime
    df.date = pd.to_datetime(df.date)
    df['month'] = df['date'].dt.month
    df['week'] = df['date'].dt.week
    df['location'] = path

    # Gets weekly averages
    week_df = df.groupby(['week']).mean().reset_index()

    return df, week_df


def avg_max_min_graph(location, name, save=False):
    df, week_df = load_and_transform(location)

    delta_max, delta_min = get_change_in_average(df)
    max_str = f'Δμ = {delta_max:.2f}°F'
    min_str = f'Δμ = {delta_min:.2f}°F'

    rainfall = longest_drought(df)

    # Create the plots
    fig, ax = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(16, 7))
    # Set the X ticks to month names inplace of week numbers for more clarity
    months = ['Jan', '', '', '', 'May', '', '', 'Aug', '', '', '', 'Dec']
    ticks = np.linspace(1, 54, num=12, endpoint=False)
    plt.setp(ax, xticks=ticks, xticklabels=months)
    ax[0].tick_params(axis="x", labelsize=12)
    ax[1].tick_params(axis="x", labelsize=12)
    # Dashed line and text to show which year the data take place
    ax[0].axvline(df.week[0], ls='--', color='black', alpha=.3)
    ax[1].axvline(df.week[0], ls='--', color='black', alpha=.3)
    plt.text(.423, .005, '2015    2014', fontsize=10,
             transform=ax[1].transAxes, alpha=.5)
    plt.text(.423, .005, '2015    2014', fontsize=10,
             transform=ax[0].transAxes, alpha=.5)

    # Plot lines to visualize the difference
    ax[0].vlines(week_df.week, week_df.average_max_temp,
                 week_df.actual_max_temp, label=max_str)
    ax[1].vlines(week_df.week, week_df.average_min_temp,
                 week_df.actual_min_temp, label=min_str)

    # Plot the weekly historical averages
    ax[0].scatter(week_df.week, week_df.average_max_temp,
                  color='pink', label='Yearly Average Max Temp')
    ax[1].scatter(week_df.week, week_df.average_min_temp,
                  color='skyblue', label='Yearly Average Min Temp')
    # Plot the current weekly averages
    ax[0].scatter(week_df.week, week_df.actual_max_temp,
                  color='red', label='Actual Average Max Temp')
    ax[1].scatter(week_df.week, week_df.actual_min_temp,
                  color='blue', label='Actual Average Min Temp')

    # Show the legends and remove the frame to see the plots better
    ax[0].legend(loc="lower left", framealpha=0)
    ax[1].legend(loc="upper right", framealpha=0)
    # Set Y label and increse text size
    ax[0].set_ylabel('Temperature in °F', fontsize=16)
    # Set text box to describe longest period with only light drizzles or less
    plt.text(-.4, -.13, f'{location} spent {rainfall} consecutive days '
             'with\nless than .05 inches of rainfall per day',
             fontsize=10, transform=ax[1].transAxes)
    # Put a title in the center of the two graphs
    plt.suptitle(f'Weekly average maximum and minimums at {location}\n{name}',
                 fontsize=18)
    # Add ticks and labels to left side
    ax[1].tick_params(labelright=True, right=True, left=False)

    if save:
        plt.savefig('imgs/'+location+'.png')

    plt.show()


def graph_rainfall(save=False):
    df, _ = load_and_transform('KCQT')
    df_month = df.groupby(['month']).sum().reset_index()
    df_month['location'] = 'KCQT'

    for place in ['KCLT', 'KHOU', 'KIND',
                  'KJAX', 'KMDW', 'KNYC',
                  'KPHL', 'KPHX', 'KSEA']:
        df2, _ = load_and_transform(place)
        df_month2 = df2.groupby(['month']).sum().reset_index()
        df_month2['location'] = place
        df_month = df_month.append(df_month2, ignore_index=True)

    # Create color gradient and
    blue = Color('skyblue')
    colors = list(blue.range_to(Color('darkblue'), 12))
    colors = [color.rgb for color in colors]
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    pivot_df = df_month.pivot(index='location', columns='month',
                              values='actual_precipitation')
    pivot_df.plot.bar(stacked=True, figsize=(10, 7), color=colors)

    plt.legend(bbox_to_anchor=(1.0, 1), loc='upper left', labels=months)
    plt.xlabel('Location', fontsize=16)
    plt.ylabel('Cumulative Precipitation in Inches', fontsize=16)
    plt.title('Total Precipitation Across all Locations', fontsize=18)
    plt.tight_layout()

    if save:
        plt.savefig('imgs/rainfall.png')

    plt.show()


def graph_records(save=False, years=5):
    locs = ['KCLT', 'KCQT', 'KHOU', 'KIND',
            'KJAX', 'KMDW', 'KNYC',
            'KPHL', 'KPHX', 'KSEA']
    hot_records = []
    cold_records = []
    for place in locs:
        df, _ = load_and_transform(place)
        cold_mask = ((df['record_min_temp_year'] >= df.date.dt.year - years) |
                     (df['record_min_temp'] == df['actual_min_temp']))
        hot_mask = ((df['record_max_temp_year'] >= df.date.dt.year - years) |
                    (df['record_max_temp'] == df['actual_max_temp']))
        hot_records.append(df[hot_mask].record_min_temp.count())
        cold_records.append(df[cold_mask].record_max_temp.count())
    ind = np.arange(10)
    width = .35
    plt.bar(ind, hot_records, width=width, label='Record Heat Days',
            color='red')
    plt.bar(ind+width, cold_records, width=width, label='Record Cold Days',
            color='blue')
    plt.xticks(ind + width / 2, locs, fontsize=10, rotation=40)
    plt.ylabel('Number of Days', fontsize=14)
    plt.xlabel('Locations', fontsize=14)
    plt.title(f'Number of Record Setting days in the past {years} Years',
              fontsize=16)
    plt.legend()
    plt.tight_layout()

    if save:
        plt.savefig('imgs/record_days.png')

    plt.show()


if __name__ == "__main__":
    # Dict containing weather station codes and physical locations
    locations = {'KCLT': 'Charlotte, NC',
                 'KCQT': 'Los Angeles, CA',
                 'KHOU': 'Houston, TX',
                 'KIND': 'Indianapolis, IN',
                 'KJAX': 'Jacksonville, FL',
                 'KMDW': 'Chicago, IL',
                 'KNYC': 'New York City, NY',
                 'KPHL': 'Philadelphia, PA',
                 'KPHX': 'Phoenix, AZ',
                 'KSEA': 'Seattle, WA'}

    # Bools to control which graphs are produced and if they are saved
    make_temp_graphs = False
    graph_rain = False
    graph_record = True
    save = False

    if make_temp_graphs:
        for code, name in locations.items():
            avg_max_min_graph(code, name, save=save)

    if graph_rain:
        graph_rainfall(save=save)

    if graph_record:
        graph_records(save=save)
