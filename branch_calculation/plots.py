# plots.py - Enhanced Branch Network Analysis Plotting

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from collections import defaultdict
import math
from cons import Constants


def detect_branches(df_results, net):
    """
    Automatically detect all branches in the network by analyzing the connectivity

    Parameters:
        df_results (DataFrame): Results from network analysis
        pipes_dict (dict): Dictionary of pipe data

    Returns:
        dict: Dictionary where keys are branch names and values are lists of nodes in order
    """
    print('Detecting branches...')
    # print(df_results.info())

    leading_branches = net.get_terminal_branches()
    branches_path = net.get_branch_paths()
    for lb in leading_branches:
        branch = branches_path[lb]
        df = df_results[df_results['Pipe_ID'].isin(branch)].copy()
        fig = plot_branch(df)
        fig.show()


def plot_branch(df_results):
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
            x=df_results['Distance_m'],
            y=df_results['Elevation_m'],
            mode='lines+markers',
            name='Ground Elevation',
            line=dict(color='brown', width=3),
            marker=dict(size=8)
        ),
        secondary_y=False
    )

    fig.add_trace(
        go.Scatter(
            x=df_results['Distance_m'],
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
            x=df_results['Distance_m'],
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
            x=df_results['Distance_m'],
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
    fig.add_hline(y=25, line_dash="dot", line_color="red",
                  annotation_text="Min Pressure (25m)", secondary_y=True)

    # Update layout
    fig.update_xaxes(title_text="Distance from Reservoir (m)")
    fig.update_yaxes(title_text="Elevation / Head (m)", secondary_y=False)
    fig.update_yaxes(title_text="Pressure Head (m)", secondary_y=True)

    fig.update_layout(
        title="Hydraulic Profile - Branch Network Analysis",
        width=1000,
        height=600,
        legend=dict(x=0.02, y=0.98),
        hovermode='x unified'
    )

    return fig

