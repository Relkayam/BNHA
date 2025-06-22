import pandas as pd



def build_df_model(df_sections_data, df_pipe_prices):
    """
    Build the DataFrame model for branch calculation.

    Returns:
        pd.DataFrame: DataFrame containing the branch calculation model.
    """

    df_model = pd.DataFrame()
    # our_system_branches_lists = net.system_branches_lists
    ind = 0
    for pipe in df_sections_data['Pipe_ID'].unique():
        for diam in df_pipe_prices.Diameter_m:
            pipe_data = df_pipe_prices.loc[df_pipe_prices['Diameter_m'] == diam]
            section_data = df_sections_data.loc[df_sections_data['Pipe_ID'] == pipe]
            df_model.loc[ind, 'var_name'] = '{}_{}'.format(str(pipe), str(diam))
            df_model.loc[ind, 'Pipe_ID'] = pipe
            df_model.loc[ind, 'Diameter_m'] = diam
            df_model.loc[ind, 'cost_USD_per_meter'] = pipe_data.loc[:, 'cost_USD_per_meter'].values[0]
            df_model.loc[ind, 'Start_Junction'] = section_data.loc[:, 'Start_Junction'].values[0]
            df_model.loc[ind, 'End_Junction'] = section_data.loc[:, 'End_Junction'].values[0]
            df_model.loc[ind, 'length_m'] = section_data.loc[:, 'length_m'].values[0]
            df_model.loc[ind, 'cost_USD'] = df_model.loc[ind, 'cost_USD_per_meter'] * df_model.loc[ind, 'length_m']
            df_model.loc[ind, 'End_Junction_Elevation_m'] = section_data.loc[:, 'End_Junction_Elevation_m'].values[0]
            df_model.loc[ind, 'static_head'] = section_data.loc[:, 'static_head'].values[0]
            df_model.loc[ind, 'Flow_cms'] = section_data.loc[:, 'flow_cms'].values[0]
            df_model.loc[ind, 'flow_cmh'] = section_data.loc[:, 'flow_cmh'].values[0]
            df_model.loc[ind, 'dz'] = section_data.loc[:, 'dz'].values[0]
            df_model.loc[ind, 'hwc'] = section_data.loc[:, 'hwc'].values[0]
            df_model.loc[ind, 'end_junc_path'] = section_data.loc[:, 'end_junc_path'].values
            df_model.loc[ind, 'hydraulic_gradient_per_m'] = section_data.loc[:, 'hydraulic_gradient_per_m'].values[0]

            # df_model.loc[ind, 'distance_from_source'] = section_data.loc[:, 'distance_from_source'].values[0]

            # df_model.loc[ind, 'head_loss'] = 1.13 * (10**12) * (df_model.loc[ind, 'flow']/df_model.loc[ind, 'hw_constant']) ** 1.852 * df_model.loc[ind, 'diameter_mm'] ** -4.87 * df_model.loc[ind, 'lenth_km']
            # df_model.loc[ind, 'total_head'] =  elevation_0 - df_model['head_loss'].sum()

            ind += 1

    df_model['headloss'] = (10.67 * df_model['length_m'] * df_model['Flow_cms'] ** 1.852) / (
            df_model['hwc'] ** 1.852 * df_model['Diameter_m'] ** 4.8704)
    # df_model['total_head'] =  df_model['dz'] - df_model['head_loss']
    df_model['headloss_per_m'] = (10.67 * df_model['Flow_cms'] ** 1.852) / (
                df_model['hwc'] ** 1.852 * df_model['Diameter_m'] ** 4.8704)

    return df_model