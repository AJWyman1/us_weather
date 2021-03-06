import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from colour import Color


class weather_examiner(object):

    def __init__(self):
        self.locs = ['KCLT', 'KCQT', 'KHOU', 'KIND',
                     'KJAX', 'KMDW', 'KNYC',
                     'KPHL', 'KPHX', 'KSEA']

        self.locations = {'KCLT': 'Charlotte, NC',
                          'KCQT': 'Los Angeles, CA',
                          'KHOU': 'Houston, TX',
                          'KIND': 'Indianapolis, IN',
                          'KJAX': 'Jacksonville, FL',
                          'KMDW': 'Chicago, IL',
                          'KNYC': 'New York City, NY',
                          'KPHL': 'Philadelphia, PA',
                          'KPHX': 'Phoenix, AZ',
                          'KSEA': 'Seattle, WA'}

    def load_and_transform(self, path):
        # Loads the data
        df = pd.read_csv('data/'+path+'.csv')

        # Adds needed columns and converts str to datetime
        df.date = pd.to_datetime(df.date)
        df['month'] = df['date'].dt.month
        df['week'] = df['date'].dt.week
        df['location'] = path

        return df

    def longest_drought(self, df, rain_tresh=0.05):
        # takes in a dataframe and returns an int of the longest
        # span of consecutive days with light or less rain fall
        max_days = 0
        running_count = 0
        for rain in df.actual_precipitation:
            if rain < rain_tresh:
                running_count += 1
            else:
                if running_count > max_days:
                    max_days = running_count
                running_count = 0
        return max_days

    def get_change_in_average(self, df):
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

    def avg_max_min_graph(self, location, name, save=False):
        df = self.load_and_transform(location)
        week_df = df.groupby(['week']).mean().reset_index()

        week_df['adjusted_week'] = week_df.apply(
            lambda row: row.week - 26 if row.week - 26 > 0 else row.week + 26,
            axis=1)
        delta_max, delta_min = self.get_change_in_average(df)
        max_str = f'Δμ = {delta_max:.2f}°F'
        min_str = f'Δμ = {delta_min:.2f}°F'

        # Create the plots
        fig, ax = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(16, 7))
        # Set the X ticks to month names increasing clarity
        months = ['Jul', '', 'Sep', '', 'Nov', '',
                  'Jan', '', 'Mar', '', 'May', '']
        ticks = np.linspace(1, 54, num=12, endpoint=False)
        plt.setp(ax, xticks=ticks, xticklabels=months)
        ax[0].tick_params(axis="x", labelsize=12)
        ax[1].tick_params(axis="x", labelsize=12)

        # Plot lines to visualize the difference
        ax[0].vlines(week_df.adjusted_week, week_df.average_max_temp,
                     week_df.actual_max_temp, label=max_str)
        ax[1].vlines(week_df.adjusted_week, week_df.average_min_temp,
                     week_df.actual_min_temp, label=min_str)

        # Plot the weekly historical averages
        ax[0].scatter(week_df.adjusted_week, week_df.average_max_temp,
                      color='pink', label='Average Max Temp')
        ax[1].scatter(week_df.adjusted_week, week_df.average_min_temp,
                      color='skyblue', label='Average Min Temp')
        # Plot the current weekly averages
        ax[0].scatter(week_df.adjusted_week, week_df.actual_max_temp,
                      color='red', label='Actual Max Temp')
        ax[1].scatter(week_df.adjusted_week, week_df.actual_min_temp,
                      color='blue', label='Actual Min Temp')

        # Show the legends and remove the frame to see the plots better
        ax[0].legend(loc="lower left", framealpha=0)
        ax[1].legend(loc="upper right", framealpha=0)
        # Set Y label and increse text size
        ax[0].set_ylabel('Temperature in °F', fontsize=16)

        # Put a title in the center of the two graphs
        plt.suptitle(f'Weekly Average Maximum and Minimums in'
                     f' {name}',
                     fontsize=18)
        # Add ticks and labels to left side
        ax[1].tick_params(labelright=True, right=True, left=False)
        plt.tight_layout(pad=3)
        if save:
            plt.savefig('imgs/'+location+'.png')

        plt.show()

    def graph_rainfall(self, save=False):
        # Set up initial df to append to later
        df = self.load_and_transform('KCQT')
        df_month = df.groupby(['month']).sum().reset_index()
        df_month['location'] = 'KCQT'

        # Load rest of the dfs and append to initial df
        for place in ['KCLT', 'KHOU', 'KIND',
                      'KJAX', 'KMDW', 'KNYC',
                      'KPHL', 'KPHX', 'KSEA']:
            df2 = self.load_and_transform(place)
            df_month2 = df2.groupby(['month']).sum().reset_index()
            df_month2['location'] = place
            df_month = df_month.append(df_month2, ignore_index=True)

        # Pivot table setup to create stacked bar chart
        pivot_df = df_month.pivot_table(index='location',
                                        columns='month',
                                        values='actual_precipitation',
                                        aggfunc='sum',
                                        margins=True)
        # Sort values to increase readability and drop unused rows and cols
        pivot_df = pivot_df.sort_values('All',
                                        ascending=False,
                                        axis=0).drop('All').drop('All', axis=1)

        # Create color gradient and list for stack of months
        blue = Color('skyblue')
        colors = list(blue.range_to(Color('darkblue'), 12))
        colors = [color.rgb for color in colors]
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        pivot_df.plot.bar(stacked=True, figsize=(10, 7), color=colors)

        # Reordering the legend to match the stack of the bar chart for
        # increased readability
        # Get legend handles
        handles, _ = plt.gca().get_legend_handles_labels()
        # List of indicies for new order
        order = [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        # Set up the legend to display Jan at bottom of legend
        plt.legend([handles[idx] for idx in order],
                   [months[idx] for idx in order], bbox_to_anchor=(1.0, 1))

        plt.xlabel('Location', fontsize=16)
        plt.ylabel('Cumulative Precipitation in Inches', fontsize=16)
        plt.xticks(np.arange(10), [self.locations[i] for i in pivot_df.index])
        plt.title('Total Precipitation Across all Locations', fontsize=18)
        plt.tight_layout()

        if save:
            plt.savefig('imgs/rainfall.png')

        plt.show()

    def graph_records(self, save=False):
        # Empty lists to gather the data
        hot_records = []
        cold_records = []
        rain_records = []
        # Loops through locations, create masks, appends to list
        for place in self.locs:
            df = self.load_and_transform(place)
            # checks if record year = current year or if record temp = actual
            c_mask = ((df['record_min_temp_year'] == df.date.dt.year) |
                      (df['record_min_temp'] == df['actual_min_temp']))
            h_mask = ((df['record_max_temp_year'] == df.date.dt.year) |
                      (df['record_max_temp'] == df['actual_max_temp']))
            # No record year for precipitation so checks if actual=record
            # and if the record is not 0
            r_mask = ((df['record_precipitation'] == df.actual_precipitation) &
                      (df['record_precipitation'] != 0))
            hot_records.append(df[h_mask].record_min_temp.count())
            cold_records.append(df[c_mask].record_max_temp.count())
            rain_records.append(df[r_mask].record_precipitation.count())
        # Set ticks for x axis and width of bars
        ind = np.arange(10)
        width = .2
        # Sort by most record highs and reorder lists accordingly
        sorted_idx = np.argsort(hot_records)
        rain_records = [rain_records[i] for i in sorted_idx]
        hot_records = [hot_records[i] for i in sorted_idx]
        cold_records = [cold_records[i] for i in sorted_idx]
        # Plot the data
        plt.bar(ind-width, rain_records, width=width, label='Record Rain',
                color='skyblue')  # 35 total
        plt.bar(ind, hot_records, width=width, label='Record High',
                color='red')  # 53 total
        plt.bar(ind+width, cold_records, width=width, label='Record Low',
                color='blue')  # 18 total
        # place xticks with reordered location names
        plt.xticks(ind + width / 3,
                   [self.locations[self.locs[i]] for i in sorted_idx],
                   fontsize=10, rotation=90)
        plt.yticks(np.linspace(4, 20, 5))
        # Set labels and titles
        plt.ylabel('Number of Days', fontsize=14)
        plt.xlabel('Locations', fontsize=14)
        plt.title(f'Number of Record Setting Days in the Past Year',
                  fontsize=16)
        plt.legend()
        plt.tight_layout()

        if save:
            plt.savefig('imgs/record_days.png')

        plt.show()

    def graph_longest_drought(self, save):
        # Create list of lengths of days w/o precipitation
        drought = [self.longest_drought(self.load_and_transform(place))
                   for place in self.locs]
        # Load into a df and sort by number of days
        df = pd.DataFrame({'locations': [self.locations[i] for i in self.locs],
                          'drought': drought})
        df.sort_values('drought', inplace=True)
        # Create plot
        df.plot(kind='bar', y='drought', x='locations',
                color='skyblue', legend=None)
        plt.ylabel('Days', fontsize=14)
        plt.xlabel('Location', fontsize=14)
        plt.xticks(rotation=90)
        plt.title('Number of Consecutive Days with No Significant Rainfall',
                  fontsize=16)
        plt.tight_layout()

        if save:
            plt.savefig('imgs/consecutive_days.png')

        plt.show()


if __name__ == "__main__":
    weather_ex = weather_examiner()
    # Bools to control which graphs are produced and if they are saved
    make_temp_graphs = True
    only_one = False
    graph_rain = False
    graph_record = False
    graph_consecutive = False
    save = True

    if make_temp_graphs:
        for code, name in weather_ex.locations.items():
            weather_ex.avg_max_min_graph(code, name, save=save)
            if only_one:
                break

    if graph_rain:
        weather_ex.graph_rainfall(save=save)

    if graph_record:
        weather_ex.graph_records(save=save)

    if graph_consecutive:
        weather_ex.graph_longest_drought(save)
