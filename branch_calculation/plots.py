# plots.py - Enhanced Branch Network Analysis Plotting

import plotly.graph_objects as go
from matplotlib.pyplot import title
from plotly.subplots import make_subplots
from branch_calculation.add_source_row_to_results_dataframe import add_source_row_for_plot
import pandas as pd
import numpy as np
from collections import defaultdict
import math


# def get_branch_pipes_list(df_results):
#     """
#     Extracts branch pipes from the results DataFrame.
#     This function identifies branches in the hydraulic network based on the
#     'branch_end' column and returns a dictionary where keys are branch names
#     and values are lists of pipe IDs that belong to each branch.
#
#     Parameters:
#     df_results (pd.DataFrame): DataFrame containing hydraulic analysis results.
#
#     Returns:
#     dict: Dictionary with branch names as keys and lists of pipe IDs as values.
#
#     :param df_results:
#     :return: dict with branch names as keys and lists of pipe IDs as values.
#     """
#     result = {}
#     df_cut = df_results[df_results['branch_end'] == 1].copy()
#     for branch in df_cut['end_junc_path']:
#         print(branch)
#
#         result[branch] = branch.split(',')
#         print(branch)
#
#     return result


def plot_branches(branches, minimum_pressure_constraint=2, analysis_type=""):
    """
    Plot branches of the hydraulic network with hydraulic profiles.
    This function takes a DataFrame of results from the hydraulic analysis,
    identifies branches, and generates plots for each branch showing the
    hydraulic profile including elevation, hydraulic grade line (HGL),
    energy grade line (EGL), and pressure head.
    Parameters:
    df_results (pd.DataFrame): DataFrame containing hydraulic analysis results.
    minimum_pressure_constraint (float): Minimum pressure head constraint for the system.
    Returns:
    None: Displays plots for each branch.


    """

    # df_results.sort_values(by='Distance_from_Source_m', inplace=True)
    #
    # model_branches = get_branch_pipes_list(df_results)
    # df_results = add_source_row(df_results.copy())
    #
    # print('Detected branches:', model_branches.keys())

    for lb, df_ in branches.items():
        # sort by distance from source
        df_.sort_values(by='Distance_from_Source_m', inplace=True)
        print('========Plot Branch: ', lb, '========')
        # print(df_.columns)
        # exit()
        df = df_[['sort_index', 'Pipe_ID','Distance_from_Source_m', 'End_Junction_Elevation_m','static_head','Total_Head_m', 'Pressure_Head_m']].copy()
        df = add_source_row_for_plot(df)
        print()
        p_title = f"{analysis_type} - {lb}" if analysis_type else lb
        fig = create_figures(df, minimum_pressure_constraint, p_title)
        fig.show()


def create_figures(df_results, minimum_pressure_constraint, p_title=None):
    """
    Create hydraulic profile plot showing elevation, HGL, and EGL
    """
    fig = make_subplots(
        rows=1, cols=1,
        subplot_titles=['Hydraulic Profile'],
        specs=[[{"secondary_y": True}]]
    )

    # Primary y-axis: Elevations and heads
    fig.add_trace(
        go.Scatter(
            x=df_results['Distance_from_Source_m'],
            y=df_results['End_Junction_Elevation_m'],
            mode='lines+markers',
            name='Ground Elevation',
            line=dict(color='brown', width=3),
            marker=dict(size=8)
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=df_results['Distance_from_Source_m'],
            y=df_results['Total_Head_m'],
            mode='lines+markers',
            name='Energy Grade Line (EGL)',
            line=dict(color='red', width=2, dash='dash'),
            marker=dict(size=6)
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=df_results['Distance_from_Source_m'],
            y=df_results['Total_Head_m'],
            mode='lines+markers',
            name='Hydraulic Grade Line (HGL)',
            line=dict(color='blue', width=2),
            marker=dict(size=6),
            fill='tonexty',
            fillcolor='rgba(0,100,255,0.1)'
        ),
        secondary_y=False
    )

    # Secondary y-axis: Pressure head
    fig.add_trace(
        go.Scatter(
            x=df_results['Distance_from_Source_m'],
            y=df_results['Pressure_Head_m'],
            mode='lines+markers',
            name='Pressure Head',
            line=dict(color='green', width=2),
            marker=dict(size=6),
            yaxis='y2'
        ),
        secondary_y=True
    )

    # Add minimum pressure line
    fig.add_hline(y=minimum_pressure_constraint, line_dash="dot", line_color="red",
                  annotation_text=f"Min Pressure ({minimum_pressure_constraint}m)", secondary_y=True)

    fig.add_hline(y=df_results.iloc[0]['static_head'], line_dash="dot", line_color="blue",
                  annotation_text=f"Static Head ({df_results.iloc[0]['static_head']} m)", secondary_y=False)

    # Update layout
    fig.update_xaxes(title_text="Distance from Reservoir (m)")
    fig.update_yaxes(title_text="Elevation / Head (m)", secondary_y=False)
    fig.update_yaxes(title_text="Pressure Head (m)", secondary_y=True)

    fig.update_layout(
        title=f"Hydraulic Profile - {p_title}",
        # width=1000,
        # height=600,
        legend=dict(x=0.02, y=0.98),
        hovermode='x unified'
    )

    return fig

