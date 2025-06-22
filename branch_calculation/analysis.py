# analysis.py

import pandas as pd
from branch_calculation.hydraulics import calculate_head_loss, calculate_velocity, calculate_reynolds_number


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
    analysis_dict = {}
    # Extract data from the network instance
    pipes_dict, system_data = network.to_dict()


    reservoir_head = system_data['reservoir_total_head']
    reservoir_elevation = system_data['reservoir_elevation']
    min_pressure = system_data['min_pressure_head']
    max_velocity = system_data['max_velocity']

    # Map end_junc -> pipe_id for lookup
    node_table = {}
    for pid, pipe in pipes_dict.items():
        node_table[pipe['End_Junction']] = pid
    # print(node_table, "node_table")

    # First, calculate hydraulic properties for all pipes
    for pid, pipe in pipes_dict.items():
        head_loss = calculate_head_loss(pipe['length_m'], pipe['flow_cms'], pipe['hwc'], pipe['Diameter_m'])
        velocity = calculate_velocity(pipe['flow_cms'], pipe['Diameter_m'])
        reynolds = calculate_reynolds_number(pipe['flow_cms'], pipe['Diameter_m'])

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
            # 'Pipe_ID': pipe_id,
            # 'Start_Junction': pipe_data['Start_Junction'],
            # 'End_Junction': pipe_data['End_Junction'],
            # 'Distance_from_Source_m': distance,
            # 'End_Junction_Elevation_m': pipe_data['End_Junction_Elevation_m'],
            # 'Total_Head_m': total_head,
            # 'Pressure_Head_m': total_head - pipe_data['End_Junction_Elevation_m'],
            # 'Velocity_m_s': pipe_data['velocity'],
            # 'Reynolds': pipe_data['reynolds'],
            # 'Diameter_mm': pipe_data['Diameter_m'] * 1000,
            # 'Flow_cms': pipe_data['flow_cms'],
            # 'branch_end': pipe_data['branch_end'],
            # 'end_junc_path': pipe_data['end_junc_path'],
            # ##################################
            'var_name': [None],
            'Pipe_ID': pipe_id,
            'Diameter_m': pipe_data['Diameter_m'],
            'Diameter_mm': pipe_data['Diameter_m'] * 1000,
            'Velocity_m_s': pipe_data['velocity'],
            'Reynolds': pipe_data['reynolds'],
            'cost_USD_per_meter': [None],
            'Start_Junction': pipe_data['Start_Junction'],
            'End_Junction': pipe_data['End_Junction'],
            'length_m': pipe_data['length_m'],
            'cost_USD': [None],
            'End_Junction_Elevation_m': pipe_data['End_Junction_Elevation_m'],
            'static_head': total_head,
            'Flow_cms': pipe_data['flow_cms'],
            'flow_cmh': pipe_data['flow_cms'] * 3600,
            'dz': [None],
            'hwc': pipe_data['hwc'],
            'end_junc_path': pipe_data['end_junc_path'],
            'hydraulic_gradient_per_m': [None],
            'headloss_per_m': [None],
            'lp_vars': [None],
            'Results': [None],
            'pipe_updated': [None],
            'headloss': [None],
            'end_junc_path_updated': [None],
            'branch_end': pipe_data['branch_end'],
            'corrected_dz': [None],
            'total_head_losses':  total_head - pipe_data['End_Junction_Elevation_m'],
            'Total_Head_m': total_head,
            'Pressure_Head_m': total_head - pipe_data['End_Junction_Elevation_m'],
            'Distance_from_Source_m': distance

        })

    df_results = pd.DataFrame(results)

    # Aggregate system-level stats
    analysis_dict['summary'] = {
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
    analysis_dict['branches_end'] = df_results.loc[df_results.branch_end == 1, 'end_junc_path'].tolist()
    # print(analysis_dict['branches_end'])
    df_results['Distance_from_Source_m'] = 0.0

    analysis_dict['results_branch'] = {}
    for pid, full_path in zip(df_results['end_junc_path'], df_results['end_junc_path']):
        # print(full_path)
        path_pipes = full_path.split(',')
        # print(path_pipes)
        path_rows = df_results[df_results['Pipe_ID'].isin(path_pipes)].copy()
        if full_path in analysis_dict['branches_end']:
            # print(full_path)
            for i, p in enumerate(path_pipes):
                path_rows.loc[path_rows['Pipe_ID'] == p, 'sort_index'] = i + 1

            path_rows.sort_values(by='sort_index', inplace=True)
            path_rows['Distance_from_Source_m'] = path_rows['length_m'].cumsum()
            analysis_dict['results_branch'][full_path] = path_rows
            # print(path_rows[['Pipe_ID', 'Distance_from_Source_m']])
            df_results.loc[path_rows.index, 'Distance_from_Source_m'] = path_rows['Distance_from_Source_m'].values

    df_results.sort_values(by='Distance_from_Source_m').reset_index(drop=True)
    analysis_dict['df_res'] = df_results
    # print(df_results)
    # exit()
    return analysis_dict