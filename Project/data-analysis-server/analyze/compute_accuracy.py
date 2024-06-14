from datetime import datetime
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np


def compute_metrics(df):
    # Calculate metrics
    accuracy = accuracy_score(df['sleep_gt'], df['sleep'])
    precision = precision_score(df['sleep_gt'], df['sleep'])
    recall = recall_score(df['sleep_gt'], df['sleep'])
    f1 = f1_score(df['sleep_gt'], df['sleep'])

    return accuracy, precision, recall, f1


# def create_plot(names, df, end_time):
#     df['color'] = df.apply(lambda row: 'red' if row['sleep'] != row['sleep_gt'] else 'blue', axis=1)

#     # Plotting
#     plt.figure(figsize=(12, 6))
#     #plt.scatter(df[names.df_time], df[names.df_pressure_value], color=df['color'])
    
#     # Plot each color separately
#     for color in df['color'].unique():
#         df_color = df[df['color'] == color]
#         plt.plot(df_color[names.df_time], df_color[names.df_pressure_value], color=color, label=f'{color} points')

#     plt.xlabel('Timestamp')
#     plt.ylabel('Pressure values')
#     plt.title('Datapoints with mismatched detections in red')
#     plt.grid(True)

#     # Save the plot
#     date_str = end_time.strftime('%Y-%m-%d')
#     plt.savefig(f'data/images/data_points_plot{date_str}.png')


def create_plot(names, df, end_time):
    # determine the color of each datapoint
    df['color'] = df.apply(lambda row: 'red' if row['sleep'] != row['sleep_gt'] else 'blue', axis=1)

    # Convert Timestamp to numeric values
    df['numeric_time'] = pd.to_numeric(df[names.df_time])

    # Create segments for the line plot
    points = np.array([df['numeric_time'], df[names.df_pressure_value]]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    # Create a LineCollection
    lc = LineCollection(segments, colors=df['color'].values, linewidth=2)
    
    # Plotting
    plt.figure(figsize=(15, 12))
    plt.gca().add_collection(lc)
    plt.xlim(df['numeric_time'].min(), df['numeric_time'].max())
    plt.ylim(df[names.df_pressure_value].min(), df[names.df_pressure_value].max())
    
    # Convert numeric_time back to Timestamp for x-tick labels
    plt.gca().set_xticks(df['numeric_time'][::len(df)//10])
    plt.gca().set_xticklabels(df[names.df_time].dt.strftime('%Y-%m-%d %H:%M:%S')[::len(df)//10], rotation=45)

    plt.xlabel('Timestamp')
    plt.ylabel('Pressure values')
    plt.title('Datapoints with mismatched detections in red')
    plt.grid(True)


    # Save the plot
    date_str = end_time.strftime('%Y_%m_%d')
    plt.savefig(f'data/images/datapoints_plot_{date_str}.png')



def compute_metrics_in_detecting_presence(names, sleep_periods, pressure_data, end_time):
    """
    In order to compute the accuracy we need to be sure about the ground truth labels.
    Our subject used for collecting the data and testing the alarm, 
    usually go to sleep after midnight and wake up before 11 a.m.
    so we will extract the sleep_periods detected in this time 
    and we will consider them as ground truth indicating that the person is on the bed.
    """

    if len(sleep_periods) > 0:

        # extract the start of the first sleep period
        first_sleeping_period_idx = 0

        for i in range(len(sleep_periods)):
            if sleep_periods[i][0].hour > 0:
                first_sleeping_period_idx = i
                break

        start_sleep = sleep_periods[first_sleeping_period_idx][0]
        
        # detect the last sleeping period before 11 a.m.
        last_sleeping_period_idx = 0

        # print("sleep_periods: ", len(sleep_periods))
        for i in range(len(sleep_periods)):
            if sleep_periods[i][1].hour < 11:
                last_sleeping_period_idx = i

        end_sleep = sleep_periods[last_sleeping_period_idx][1]

        # update the dataframe 
        # insert a new column with sleep_gt at 1 in this period
        # and sleep_gt at 0 in the others
        pressure_data['sleep_gt'] = (pressure_data[names.df_time] >= start_sleep) & (pressure_data[names.df_time] <= end_sleep)

        # # compute the real sleep duration
        # real_sleep_duration = (end_sleep - start_sleep).total_seconds()
        # # compute the recorded sleep duration
        # recorded_sleep_duration = sum((end - start).total_seconds() for start, end in sleep_periods[:last_sleeping_period_idx+1])
        # accuracy = recorded_sleep_duration * 100 / real_sleep_duration

        accuracy, precision, recall, f1 = compute_metrics(pressure_data)

        create_plot(names, pressure_data, end_time)

        return accuracy, precision, recall, f1
    
    else:
        # no sleep period detected
        return -1, -1, -1, -1


