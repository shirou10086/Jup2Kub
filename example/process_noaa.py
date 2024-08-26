# Cell 1: Setup and Import Libraries

import pandas as pd
import numpy as np
import time

print(time.time())
# This setting helps to display all the columns in the dataframe
pd.set_option('display.max_columns', None)


# Cell 2: Load the Data

# Define the CSV file path
file_path = './data/noaa.csv'

# Define column names as there are no headers in the CSV file
columns = ['STATION', 'DATE', 'LATITUDE', 'LONGITUDE', 'ELEVATION', 'NAME', 'TEMP',
           'TEMP_ATTRIBUTES', 'DEWP', 'DEWP_ATTRIBUTES', 'SLP', 'SLP_ATTRIBUTES',
           'STP', 'STP_ATTRIBUTES', 'VISIB', 'VISIB_ATTRIBUTES', 'WDSP', 'WDSP_ATTRIBUTES',
           'MXSPD', 'GUST', 'MAX', 'MAX_ATTRIBUTES', 'MIN', 'MIN_ATTRIBUTES',
           'PRCP', 'PRCP_ATTRIBUTES', 'SNDP', 'FRSHTT']

# Read the CSV file
data = pd.read_csv(file_path, header=None, names=columns, low_memory=False)
print(data.head())


# Cell 3: Filter out unnecessary columns

# Dropping columns that are not required for the analysis
data = data.drop(columns=['TEMP_ATTRIBUTES', 'DEWP_ATTRIBUTES', 'SLP_ATTRIBUTES', 'STP_ATTRIBUTES',
                          'VISIB_ATTRIBUTES', 'WDSP_ATTRIBUTES', 'MAX_ATTRIBUTES', 'MIN_ATTRIBUTES',
                          'PRCP_ATTRIBUTES', 'SNDP', 'FRSHTT'])
print(data.head())


# Cell 4: Handle Missing Values

# Replace placeholder values with NaN
placeholder_values = [9999.9, 999.9]  # Adjust as needed
for value in placeholder_values:
    data.replace(value, np.nan, inplace=True)

# Fill missing values or drop them based on the analysis requirement
# For instance, filling missing temperature values with the average temperature
data['TEMP'] = data['TEMP'].fillna(data['TEMP'].mean())
print(data.head())


# Cell 5: Filter for Extreme Conditions

# Filter for days with extremely high or low temperatures
extreme_temps = data[(data['TEMP'] > 35) | (data['TEMP'] < -20)]
print(extreme_temps.head())


# Cell 6: Export the Cleaned Data

extreme_temps.to_csv('extreme_weather_conditions.csv', index=False)

print(time.time())
