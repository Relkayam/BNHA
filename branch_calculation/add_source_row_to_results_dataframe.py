# helper for optimizer.py
from branch_calculation.cons import Constants
import pandas as pd


def add_source_row_for_plot(df):
    start_junc = Constants.SOURCE_NAME
    if 'pipe_updated' not in df.columns:
        df['pipe_updated'] = df['Pipe_ID']

    start_row = pd.DataFrame({
        'sort_index': [0],
        'Pipe_ID': ['P_0'],
        'Distance_from_Source_m': [0],
        'End_Junction_Elevation_m': [df.iloc[0]['static_head']],
        'static_head': [df.iloc[0]['static_head']],
        'Total_Head_m': [df.iloc[0]['static_head']],
        'Pressure_Head_m': [0]
    })

    results = pd.concat([start_row, df], ignore_index=True)
    results.sort_values(by='sort_index', inplace=True)
    return results