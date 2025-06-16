# analysis.py

import pandas as pd
from hydraulics import calculate_head_loss, calculate_velocity, calculate_reynolds_number


def analyze_network(network):
    """
    Perform hydraulic analysis on a branched network using cumulative head loss.

    Parameters:
        network (BranchNetwork): BranchNetwork instance containing pipe definitions
                                and system-level parameters.

    Returns:
        df_results (DataFrame): Per-node hydraulic and geometric data.
        summary (dict): System-wide performance metrics.
    """

    # Extract data from the network instance
    pipes_dict, system_data = network.to_dict()

    reservoir_head = system_data['reservoir_total_head']
    reservoir_elevation = system_data['reservoir_elevation']
    min_pressure = system_data['min_pressure_head']
    max_velocity = system_data['max_velocity']

    # Map end_junc -> pipe_id for lookup
    node_table = {}
    for pid, pipe in pipes_dict.items():
        node_table[pipe['end_junc']] = pid
    # print(node_table, "node_table")

    # First, calculate hydraulic properties for all pipes
    for pid, pipe in pipes_dict.items():
        head_loss = calculate_head_loss(pipe['length_m'], pipe['flow_cms'], pipe['hwc'], pipe['diameter_m'])
        velocity = calculate_velocity(pipe['flow_cms'], pipe['diameter_m'])
        reynolds = calculate_reynolds_number(pipe['flow_cms'], pipe['diameter_m'])

        # Store values in pipe dict
        pipe['head_loss'] = head_loss
        pipe['velocity'] = velocity
        pipe['reynolds'] = reynolds
        pipe['head_loss_per_km'] = head_loss / (pipe['length_m'] / 1000)

    # Now build unique results - one row per pipe
    results = []
    processed_pipes = set()

    # Get all unique pipes from all paths
    all_pipes_in_network = set()
    for pid, pipe in pipes_dict.items():
        if pipe.get('branch_end'):
            path = network.get_branch_paths()[pid]
            all_pipes_in_network.update(path)

    # Calculate cumulative head and distance for each pipe
    for pipe_id in all_pipes_in_network:
        # Find the shortest path from source to this pipe
        # (assumes pipes are ordered sequentially in paths)
        shortest_path = None
        for terminal_pid, terminal_pipe in pipes_dict.items():
            if terminal_pipe.get('branch_end'):
                path = network.get_branch_paths()[terminal_pid]
                if pipe_id in path:
                    pipe_index = path.index(pipe_id)
                    path_to_pipe = path[:pipe_index + 1]
                    if shortest_path is None or len(path_to_pipe) < len(shortest_path):
                        shortest_path = path_to_pipe

        # Calculate cumulative values along the shortest path
        total_head = reservoir_head
        distance = 0

        for path_pid in shortest_path:
            p = pipes_dict[path_pid]
            total_head -= p['head_loss']
            distance += p['length_m']

        # Add result for this pipe
        pipe_data = pipes_dict[pipe_id]
        results.append({
            'Pipe_ID': pipe_id,
            'Start_Junction': pipe_data['start_junc'],
            'End_Junction': pipe_data['end_junc'],
            'Distance_m': distance,
            'Elevation_m': pipe_data['end_junc_elevation'],
            'Total_Head_m': total_head,
            'Pressure_Head_m': total_head - pipe_data['end_junc_elevation'],
            'Velocity_m_s': pipe_data['velocity'],
            'Reynolds': pipe_data['reynolds'],
            'Diameter_mm': pipe_data['diameter_m'] * 1000,
            'Flow_L_s': pipe_data['flow_cms'] * 1000
        })

    df_results = pd.DataFrame(results)

    # Aggregate system-level stats
    summary = {
        'total_head_loss': reservoir_head - df_results['Total_Head_m'].min(),
        'min_pressure_head': df_results['Pressure_Head_m'].min(),
        'max_velocity': df_results['Velocity_m_s'].max(),
        'pressure_adequate': df_results['Pressure_Head_m'].min() >= min_pressure,
        'velocity_acceptable': df_results['Velocity_m_s'].max() <= max_velocity,
        'critical_node': df_results.loc[df_results['Pressure_Head_m'].idxmin(), 'End_Junction']
    }
    # print(df_results)
    # print(df_results.Distance_m)
    # print(df_results.info())
    # sort dataframe by Distance_m and reindex
    df_results = df_results.sort_values(by='Distance_m').reset_index(drop=True)
    return df_results, summary