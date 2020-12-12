import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


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
    year_df = df.groupby(['location']).mean().reset_index()

    year_avg_min = year_df.actual_min_temp[0]
    year_avg_max = year_df.actual_max_temp[0]

    historical_max_avg = year_df.average_max_temp[0]
    historical_min_avg = year_df.average_min_temp[0]

    delta_max = year_avg_max - historical_max_avg
    delta_min = year_avg_min - historical_min_avg

    return delta_max, delta_min


def load_and_transform(path):
    df = pd.read_csv(path+'.csv')

    df.date = pd.to_datetime(df.date)
    df['month'] = df['date'].dt.month
    df['week'] = df['date'].dt.week
    df['location'] = path

    week_df = df.groupby(['week']).mean().reset_index()

    return df, week_df


def avg_max_min_graph(location, name, save=False):
    df, week_df = load_and_transform(location)
    
    delta_max, delta_min = get_change_in_average(df)
    max_str = f'Δμ = {delta_max:.2f}°F'
    min_str = f'Δμ = {delta_min:.2f}°F'

    rainfall = longest_drought(df)

    #Create the plots
    fig, ax = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(16, 7))
    # Set the X ticks to month names inplace of week numbers for more clarity
    months = ['Jan', '', '', '', 'Apr', '', '', 'Aug', '', '', '', 'Dec']
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
    # Plot lines to visualize the difference
    ax[0].vlines(week_df.week, week_df.average_max_temp,
                 week_df.actual_max_temp, label=max_str)
    ax[1].vlines(week_df.week, week_df.average_min_temp,
                 week_df.actual_min_temp, label=min_str)
    # Show the legends and remove the frame to see the plots better
    ax[0].legend(loc='best', framealpha=0)
    ax[1].legend(loc='best', framealpha=0)
    # Set Y label and increse text size
    ax[0].set_ylabel('Temperature in °F', fontsize=16)
    # Set text box to describe longest period with only light drizzles or less
    plt.text(-.4, -.13, f'{location} spent {rainfall} consecutive days '
             'with\nless than .05 inches of rainfall per day',
             fontsize=10, transform=ax[1].transAxes)
    # Put a title in the center of the two graphs
    plt.suptitle(f'Weekly average maximum and minimums at {location}\n{name}',
                 fontsize=18)
    # Add ticks and 
    ax[1].tick_params(labelright=True, right=True, left=False)

    if save:
        plt.savefig('imgs/'+location+'.png')

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

    for code, name in locations.items():
        avg_max_min_graph(code, name, save=False)
