from datetime import datetime
import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error
from analyze.read_from_db import read_data_with_time_period



def resample_data(df, names):
    # Create an empty list to hold the resampled data
    resampled_data = []
    # Set the initial time for the first data point
    last_time = df.iloc[0][names.df_time] -  pd.Timedelta(seconds=30)
    
    for index, row in df.iterrows():
        # Only append the row if it's 30 seconds after the last appended row
        if (row[names.df_time] - last_time) >=  pd.Timedelta(seconds=30):
            resampled_data.append(row)
            last_time = row[names.df_time]
    
    # Convert the list back to a DataFrame
    resampled_df = pd.DataFrame(resampled_data)
    
    return resampled_df


def augment_data(df, shift_days, num_augmentations):
    augmented_dfs = [df]
    for i in range(1, num_augmentations + 1):
        augmented_df = df.copy()
        augmented_df['ds'] -= pd.Timedelta(days=shift_days * i)
        augmented_df['y'] += np.random.normal(0, 1, size=len(augmented_df))
        augmented_dfs.append(augmented_df)
    return pd.concat(augmented_dfs)


def forecast_data(InfluxDB, names, device_id, day):
    """
    We will forecast the values for the next day given the one of the previous 3 days.
    Day is the day for which we will forecast the values.
    """

    # conpute start_time and end_time 
    # i.e. the period from which read the values from the DB
    start_time_train    = pd.to_datetime(day.date()) - pd.Timedelta(days=5) + pd.Timedelta(hours=20)
    end_time_train      = pd.to_datetime(day.date()) - pd.Timedelta(days=1) + pd.Timedelta(hours=20)
    end_time_test       = pd.to_datetime(day.date())                        + pd.Timedelta(hours=20)
    
    train_df    = read_data_with_time_period(InfluxDB, names, device_id, start_time_train, end_time_train)
    test_df     = read_data_with_time_period(InfluxDB, names, device_id, end_time_train, end_time_test)

    # select the columns of interest
    train_df = train_df[[names.df_time, names.df_pressure_value]]
    test_df = test_df[[names.df_time, names.df_pressure_value]]

    # the dataframe could contain an inconsistent sampling rate,
    # i.e. sometimes we augment it,
    # so we will resample the values such that successive datapoints are shifted by 30 seconds 
    train_df = resample_data(train_df, names)
    test_df = resample_data(test_df, names)

    # rename the columns
    train_df.rename(columns={names.df_time: 'ds', names.df_pressure_value: 'y'}, inplace=True)
    test_df.rename(columns={names.df_time: 'ds', names.df_pressure_value: 'y'}, inplace=True)

    # remove timezone
    train_df['ds'] = train_df['ds'].dt.tz_localize(None)
    test_df['ds'] = test_df['ds'].dt.tz_localize(None)

    # Round the timestamps to the nearest 30 seconds
    train_df['ds'] = train_df['ds'].dt.round('30S')

    # Augment the training data (shift by 1 day)
    augmented_train_df = augment_data(train_df, shift_days=4, num_augmentations=10)

    model = Prophet()
    model.fit(augmented_train_df)

    # Create a DataFrame to hold the future dates for which we want predictions
    # Ensure it starts from the end of the training data and covers the test period exactly
    future_start = train_df['ds'].max()
    future_end = test_df['ds'].max()
    future_dates = pd.date_range(start=future_start, end=future_end, freq='30S')
    future = pd.DataFrame({'ds': future_dates})

    # # Create a DataFrame to hold the future dates for which we want predictions
    # future = model.make_future_dataframe(periods=len(test_df), freq='30S')

    # Make predictions
    forecast = model.predict(future)

    # Round the forecast timestamps to the nearest 30 seconds
    test_df['ds'] = test_df['ds'].dt.round('30S')
    forecast['ds'] = forecast['ds'].dt.round('30S')

    #print(f"Test data range: {test_df['ds'].min()} to {test_df['ds'].max()}")
    # print(f"Forecast data range: {forecast['ds'].min()} to {forecast['ds'].max()}\n\n")


    # Evaluate the model
    # Merge the forecast with the test data to compare
    forecast = forecast.set_index('ds')
    test_df = test_df.set_index('ds')
    results = test_df.join(forecast[['yhat', 'yhat_lower', 'yhat_upper']], how='inner')

    # print("test_df: ", test_df.head, "\n", test_df.tail)
    # print("\n\forecast: ", forecast.head, "\n", forecast.tail)
    # print("\n\results: ", results.head, "\n", results.tail)

    # Print evaluation metrics
    mse = mean_squared_error(results['y'], results['yhat'])
    mae = mean_absolute_error(results['y'], results['yhat'])

    print(f'Mean Squared Error: {mse}')
    print(f'Mean Absolute Error: {mae}')

    # Plot the actual vs predicted values
    plt.figure(figsize=(10, 6))
    plt.plot(results['y'], label='Actual')
    plt.plot(results['yhat'], label='Predicted')
    plt.fill_between(results.index, results['yhat_lower'], results['yhat_upper'], color='gray', alpha=0.2)
    plt.legend()
    # plt.show()
    plt.savefig(f'data/images/data_forecasting.png')



