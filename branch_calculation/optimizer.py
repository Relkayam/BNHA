# optimizer.py

import numpy as np
import pandas as pd
import pulp
from pulp import LpProblem, LpMinimize, LpStatus, lpSum, LpVariable, PULP_CBC_CMD

from branch_calculation.cons import Constants
from branch_calculation.build_df_model import build_df_model

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


def update_split_paths(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each row, build 'updated_path' to include only segments up to that 'pipe_updated'.
    """
    from collections import defaultdict

    # Build a mapping: base pipe ID -> list of segment IDs (pipe_updated)
    pipe_segments = defaultdict(list)
    for base_id, seg_id in zip(df['Pipe_ID'], df['pipe_updated']):
        pipe_segments[base_id].append(seg_id)

    # Sort the segment list numerically for each base pipe
    for key in pipe_segments:
        pipe_segments[key] = sorted(
            pipe_segments[key],
            key=lambda x: int(x.split('_')[-1]) if '_' in x else 0
        )

    # Build full segment path from end_junc_path
    def get_full_segment_path(path_str):
        parts = str(path_str).split(',')
        full = []
        for pid in parts:
            full.extend(pipe_segments.get(pid, [pid]))  # fallback if no split
        return full

    # For each row, truncate path up to and including current segment
    updated_paths = []
    for _, row in df.iterrows():
        full_path = get_full_segment_path(row['end_junc_path'])
        try:
            current_idx = full_path.index(row['pipe_updated'])
            updated_path = full_path[:current_idx + 1]
        except ValueError:
            updated_path = full_path
        updated_paths.append(','.join(updated_path))

    df['updated_path'] = updated_paths
    return df


def run_debug(model, df_sections_data, df_model, minimum_pressure_constraint=2):
    # Add this debugging code to your function right before model.solve()
    debug_file = "debug_model.txt"

    model.writeLP("debug_model.lp")

    constraint_types = {}
    for i, (name, constraint) in enumerate(model.constraints.items()):
        # Categorize constraints
        if "pipe_length" in str(constraint) or "==" in str(constraint):
            constraint_type = "Length_Equality"
        elif "<=" in str(constraint):
            constraint_type = "Pressure_Inequality"
        else:
            constraint_type = "Other"

        constraint_types[constraint_type] = constraint_types.get(constraint_type, 0) + 1

    pressure_constraints = []
    for i, (name, constraint) in enumerate(model.constraints.items()):
        if "<=" in str(constraint):  # These should be pressure constraints
            pressure_constraints.append((i, constraint))

    model_pipes = set(df_model['Pipe_ID'].unique())
    sections_pipes = set(df_sections_data['Pipe_ID'].unique())
    path_pipes = set()
    for path in df_sections_data.end_junc_path:
        path_pipes.update(path.split(','))


    print(f"Writing debug information to {debug_file}")
    with open(debug_file, 'w') as f:
        f.write("=== LP MODEL DEBUGGING ===\n")
        f.write(f"Writing debug information to {debug_file}\n")
        f.write("Full model written to debug_model.lp\n")
        f.write(f"Number of variables: {len(model.variables())}\n")
        f.write(f"Number of constraints: {len(model.constraints)}\n\n")
        f.write("=== VARIABLES SAMPLE ===\n")
    for i, var in enumerate(model.variables()[:10]):  # First 10 variables
        with open(debug_file, 'a') as f:
            f.write(f"Var {i}: {var.name} = {var.value()} (bounds: {var.lowBound} to {var.upBound})\n")
    with open(debug_file, 'a') as f:
        f.write("\n=== CONSTRAINT ANALYSIS ===\n")
    constraint_types = {}
    for i, (name, constraint) in enumerate(model.constraints.items()):
        # Categorize constraints
        if "pipe_length" in str(constraint) or "==" in str(constraint):
            constraint_type = "Length_Equality"
        elif "<=" in str(constraint):
            constraint_type = "Pressure_Inequality"
        else:
            constraint_type = "Other"

        constraint_types[constraint_type] = constraint_types.get(constraint_type, 0) + 1

        # Print first few of each type
        if i < 5:
            with open(debug_file, 'a') as f:
                f.write(f"Constraint {i} ({constraint_type}): {constraint}\n")

    with open(debug_file, 'a') as f:
        f.write(f"\nConstraint summary: {constraint_types}\n")
    # 5. Check pressure constraints specifically
    with open(debug_file, 'a') as f:
        f.write("\n=== PRESSURE CONSTRAINT VERIFICATION ===\n")
    pressure_constraints = []
    for i, (name, constraint) in enumerate(model.constraints.items()):
        if "<=" in str(constraint):  # These should be pressure constraints
            pressure_constraints.append((i, constraint))
    with open(debug_file, 'a') as f:
        f.write(f"Found {len(pressure_constraints)} pressure constraints\n")
    # Print details of first few pressure constraints
    for i, (idx, constraint) in enumerate(pressure_constraints[:3]):
        with open(debug_file, 'a') as f:
            f.write(f"\nPressure Constraint {i}:\n")
            f.write(f"  Constraint: {constraint}\n")
            if hasattr(constraint, 'value') and constraint.value() is not None:
                f.write(f"  Current value: {constraint.value():.6f}\n")
                f.write(f"  Satisfied: {constraint.value() <= 1e-6}\n")
    # 6. Cross-check with your data
    with open(debug_file, 'a') as f:
        f.write("\n=== DATA VERIFICATION ===\n")
        f.write("Pressure constraint inputs:\n")
    for i, (path_, dz) in enumerate(zip(df_sections_data.end_junc_path.head(), df_sections_data.dz.head())):
        with open(debug_file, 'a') as f:
            f.write(f"Path {i}: {path_} -> dz={dz}, constraint_limit={dz - minimum_pressure_constraint}\n")
    # 7. Check for pipe name consistency
    with open(debug_file, 'a') as f:
        f.write("\n=== PIPE NAME CONSISTENCY ===\n")
        f.write(f"Pipes in df_model: {len(model_pipes)}\n")
        f.write(f"Pipes in df_sections_data: {len(sections_pipes)}\n")
        f.write(f"Pipes referenced in paths: {len(path_pipes)}\n")
    missing_in_model = path_pipes - model_pipes
    if missing_in_model:
        with open(debug_file, 'a') as f:
            f.write(f"WARNING: Pipes in paths but not in model: {missing_in_model}\n")
    missing_in_paths = model_pipes - path_pipes
    if missing_in_paths:
        with open(debug_file, 'a') as f:
            f.write(f"INFO: Pipes in model but not in any path: {missing_in_paths}\n")
    with open(debug_file, 'a') as f:
        f.write("\n" + "=" * 50 + "\n")

    # Return the debug file path for further use
    print(f"Debug information written to {debug_file}")

    return debug_file


def full_section_optimal_diameter(net, df_pipe_prices, minimum_pressure_constraint = 2):

    result = {}
    df_sections_data = net.sections_data

    # Create model
    model = LpProblem(name="economic_diameter", sense=LpMinimize)

    df_pipe_prices['Diameter_m'] = df_pipe_prices['diameter_mm'] / 1000

    df_model = build_df_model(df_sections_data, df_pipe_prices)
    df_model['lp_vars'] = [LpVariable(var, cat='Binary') for var in df_model.loc[:, 'var_name'].values]

    # Create objective
    model += lpSum(df_model['lp_vars'] * df_model['cost_USD'])

    for p_id in df_sections_data['Pipe_ID'].unique():
        df_section_cut = df_model.loc[df_model['Pipe_ID'] == p_id]
        model += lpSum(df_section_cut.lp_vars) == 1


    for path_, dz in zip(df_sections_data.end_junc_path, df_sections_data.dz):
        path_pipe_list = path_.split(',')
        # print(path_pipe_list)
        df_section_cut = df_model.loc[df_model['Pipe_ID'].isin(path_pipe_list)]
        df_model.loc[df_section_cut.index, 'Distance_from_Source_m'] = df_model.loc[df_section_cut.index, 'length_m'].cumsum()

        # print(df_section_cut)
        model += (lpSum(df_section_cut.lp_vars * df_section_cut.headloss)) <= dz - minimum_pressure_constraint

    # print(model)

    # model.writeLP("opti_d.lp")
    status = model.solve(PULP_CBC_CMD(msg=False))

    slack = {}
    for name, constraint in model.constraints.items():
        if "pressure_path" in name:
            slack[name] = constraint.slack

    result['slack'] = slack
    result['debug'] = run_debug(model, df_sections_data, df_model, minimum_pressure_constraint=2)

    constraint_violations = {}

    for constraint in model.constraints.values():
        if constraint.value() is not None and constraint.value() > 1e-6:
            constraint_violations[constraint.name] = constraint.value()
    result["CONSTRAINT VIOLATION"] = constraint_violations

    result['model'] = model
    result['status'] = LpStatus[status]
    print('=== OPTIMIZATION RESULTS ===')
    print(result['status'])
    print("")


    # Get results
    # print(LpStatus[status])
    # print("")
    for ind, var in zip(df_model.index, df_model.lp_vars):
        df_model.loc[ind, "Results"] = var.value()

    result['df_model'] = df_model
    result['total_cost_of_operation'] = pulp.value(model.objective)

    df_res = df_model.loc[df_model.Results == 1].copy()
    # print(df_res)

    df_res['end_junc_path'] = df_res['end_junc_path'].astype('str')
    for pipe_id, dz, path_ in zip(df_res['Pipe_ID'], df_res['dz'], df_res['end_junc_path']):
        indx = df_res.loc[df_res['Pipe_ID'] == pipe_id].index
        pipe_list = list(path_.split(','))
        total_head_loss_list = [df_res.loc[df_res['Pipe_ID'] == p]['headloss'].values[0] for p in path_.split(',')]
        df_res.loc[indx, 'Total_Head_m'] = df_res.loc[indx, 'static_head'].values[0] - sum(total_head_loss_list)
        df_res.loc[indx, 'Pressure_Head_m'] = dz - sum(total_head_loss_list)
    df_res = df_res.reset_index(drop=True)

    df_res['branch_end'] = 0
    result['branches_end'] = df_sections_data.loc[df_sections_data['branch_end'] == 1, 'end_junc_path'].tolist()

    df_res['pipe_updated'] = df_res['Pipe_ID']
    df_res['flow_cms'] = df_res['flow_cmh'] / 3600
    df_res['Velocity_m_s'] = df_res['flow_cms'] / (df_res['Diameter_m'] ** 2 * np.pi / 4)
    df_res['Diameter_mm'] = df_res['Diameter_m'] / 1000

    df_res['Distance_from_Source_m'] = 0.0
    result['results_branch'] = {}
    for pid, full_path in zip(df_res['Pipe_ID'], df_res['end_junc_path']):
        path_pipes = full_path.split(',')
        path_rows = df_res[df_res['Pipe_ID'].isin(path_pipes)].copy()
        if full_path in result['branches_end']:
            for i, p in enumerate(path_pipes):
                path_rows.loc[path_rows['pipe_updated'] == p, 'sort_index'] = i + 1

            path_rows.sort_values(by='sort_index', inplace=True)
            path_rows['Distance_from_Source_m'] = path_rows['Results'].cumsum()
            result['results_branch'][full_path] = path_rows
            df_res.loc[path_rows.index, 'Distance_from_Source_m'] = path_rows['Distance_from_Source_m'].values




            result['results_branch'][full_path] = path_rows

        # path_rows = df_res[df_res['pipe_updated'].isin(path_pipes)].copy()
        # if full_path in result['branches_end']:
            for i, p in enumerate(path_pipes):
                path_rows.loc[path_rows['pipe_updated'] == p, 'sort_index'] = i + 1

            path_rows.sort_values(by='sort_index', inplace=True)
            path_rows['Distance_from_Source_m'] = path_rows['Results'].cumsum()
            result['results_branch'][full_path] = path_rows
            df_res.loc[df_res['pipe_updated'] == pid, 'Distance_from_Source_m'] = \
            path_rows['Distance_from_Source_m'].values[-1]

    df_res['pipe_updated'] = df_res['Pipe_ID']

    result['df_res'] = df_res

    result['pipes_summery'] = df_res[['Pipe_ID', 'Diameter_mm', 'Velocity_m_s', 'length_m', 'flow_cmh', 'headloss']]



    return result


def classic_optimal_diameter_optimization(net, df_pipe_prices, minimum_pressure_constraint=2):
    result = {}
    df_sections_data = net.sections_data

    # Create model
    model = LpProblem(name="economic_diameter", sense=LpMinimize)

    df_pipe_prices['Diameter_m'] = df_pipe_prices['diameter_mm'] / 1000

    df_model = build_df_model(df_sections_data, df_pipe_prices)
    df_model = df_model.drop(columns=['headloss'], errors='ignore')

    df_model['lp_vars'] = [LpVariable(var, lowBound=0, upBound=len, cat='Continuous') for var, len in
                           zip(df_model.loc[:, 'var_name'].values, df_model.loc[:, 'length_m'])]

    # Create objective
    model += lpSum(df_model['lp_vars'] * df_model['cost_USD_per_meter'])

    #the following constraint ensures that the total length of each pipe is equal to the length of the pipe in the sections data
    for p_id in df_sections_data['Pipe_ID'].unique():
        pipe_length = df_sections_data.loc[df_sections_data['Pipe_ID'] == p_id, 'length_m'].values[0]
        df_section_cut = df_model.loc[df_model['Pipe_ID'] == p_id]
        model += lpSum(df_section_cut.lp_vars) == pipe_length

    # the following constraints ensure that the total head loss in each section is less than or equal to the dz value

    for path_str, dz in zip(df_sections_data['end_junc_path'], df_sections_data['dz']):
        original_pipe_ids = path_str.split(',')

        # Map each original pipe ID to its split segments
        segments_in_path = df_model[df_model['Pipe_ID'].isin(original_pipe_ids)]

        if segments_in_path.empty:
            print(f"[WARNING] No segments found for path: {path_str}")
            continue

        total_headloss_expr = lpSum(segments_in_path['lp_vars'] * segments_in_path['headloss_per_m'])

        model += total_headloss_expr <= dz - minimum_pressure_constraint - Constants.PRESSURE_TOL, f"pressure_path_{path_str}"


    status = model.solve(PULP_CBC_CMD(msg=False))
    slack ={}
    for name, constraint in model.constraints.items():
        if "pressure_path" in name:
            slack[name] = constraint.slack

    result['slack'] = slack
    result['debug'] = run_debug(model, df_sections_data, df_model, minimum_pressure_constraint=2)

    constraint_violations = {}

    for constraint in model.constraints.values():
        if constraint.value() is not None and constraint.value() > 1e-6:
            constraint_violations[constraint.name] = constraint.value()
    result["CONSTRAINT VIOLATION"] = constraint_violations

    result['model'] = model
    result['status'] = LpStatus[status]
    print('=== OPTIMIZATION RESULTS ===')
    print(result['status'])
    print("")
    for ind, var in zip(df_model.index, df_model.lp_vars):
        df_model.loc[ind, "Results"] = var.value()
    df_model['original_pipe_id'] = df_model['Pipe_ID']
    result['df_model'] = df_model
    result['total_cost_of_operation'] = pulp.value(model.objective)

    df_res = df_model.loc[df_model.Results != 0].copy()

    df_res['pipe_updated'] = df_res.groupby('Pipe_ID').cumcount().astype(str).radd('_').radd(df_res['Pipe_ID'])
    # print(df_res['pipe_updated'])
    # exit()
    # df_res['pipe_updated'] = df_res['pipe_updated'].str.replace('_0', '', regex=False)  # Remove suffix '_0' for unique values
    df_res = update_split_paths(df_res)
    df_res['branch_end'] = 0
    # print(df_res[['pipe_updated','end_junc_path', 'updated_path', 'original_pipe_id', 'branch_end']])
    for tb in net.get_terminal_branches():
        temp = df_res.loc[df_res['original_pipe_id'] == tb].copy()
        temp['indx'] = temp['pipe_updated'].str.split('_').str[-1].astype(int)
        temp = temp.loc[temp['indx'] == temp['indx'].max()].copy()
        df_res.loc[temp.index, 'branch_end'] = 1

    result['branches_end'] = df_res.loc[df_res.branch_end == 1, 'updated_path'].tolist()


    df_res['headloss'] = df_res['Results'] * df_res['headloss_per_m']

    # correct the dz and headloss values
    df_res['corrected_dz'] = df_res['hydraulic_gradient_per_m'] * df_res['Results']

    df_res['updated_path'] = df_res['updated_path'].astype('str')

    df_res['Diameter_mm'] = df_res['Diameter_m'] / 1000
    df_res['flow_cms'] = df_res['flow_cmh'] / 3600

    for path in df_res['updated_path'].unique():
        path_df = df_res[df_res['updated_path'] == path]

        # Ensure we only process full paths once
        if path_df.empty:
            continue

        pipe_ids = path.split(',')

        total_headloss = 0.0
        for pid in pipe_ids:
            match = df_res[df_res['pipe_updated'] == pid]
            if not match.empty:
                total_headloss += match['headloss'].values[0]
        final_dz = path_df['dz']

        final_static_head = path_df['static_head'].values[0]  # assuming constant source head

        pressure_head = final_dz - total_headloss
        total_head = final_static_head - total_headloss

        # Apply back to all rows in this path
        df_res.loc[path_df.index, 'total_head_losses'] = total_headloss
        df_res.loc[path_df.index, 'Total_Head_m'] = total_head
        df_res.loc[path_df.index, 'Pressure_Head_m'] = pressure_head


    df_res = df_res.reset_index(drop=True)

    # Create dataframes for each path
    # branch_end_dataframes = create_branch_end_dataframes(df_res)
    df_res['Velocity_m_s'] = df_res['flow_cms'] / (df_res['Diameter_m'] ** 2 * np.pi / 4)

    df_res['Distance_from_Source_m'] = 0.0

    result['results_branch'] = {}
    for pid, full_path in zip(df_res['pipe_updated'] ,df_res['updated_path']):
        path_pipes = full_path.split(',')
        # print(path_pipes)
        path_rows = df_res[df_res['pipe_updated'].isin(path_pipes)].copy()
        if full_path in result['branches_end']:
            for i, p in enumerate(path_pipes):
                path_rows.loc[path_rows['pipe_updated'] == p, 'sort_index'] = i+1

            path_rows.sort_values(by='sort_index', inplace=True)
            path_rows['Distance_from_Source_m'] = path_rows['Results'].cumsum()
            result['results_branch'][full_path] = path_rows
            df_res.loc[path_rows.index, 'Distance_from_Source_m'] = path_rows['Distance_from_Source_m'].values


    result['df_res'] = df_res
    result['pipes_summery'] = df_res[['Pipe_ID', 'Diameter_mm', 'Velocity_m_s', 'length_m', 'flow_cmh', 'headloss']]

    return result

