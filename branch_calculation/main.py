# main.py
from platform import system

import pandas as pd
from branch_calculation.network import BranchNetwork
from branch_calculation.analysis import analyze_network
from branch_calculation.plots import detect_branches

if __name__ == "__main__":
    # Load example network CSV (user must provide this)
    import os
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = "network_tree_template.csv"
    df = pd.read_csv(os.path.join(project_path, csv_path))

    # Initialize network and system settings
    net = BranchNetwork()
    net.set_system_data(reservoir_elevation=300, reservoir_total_head=320)
    net.load_from_dataframe(df)


    # Analyze network
    df_results, summary = analyze_network(net)
    # print(df_results)

    # Print summary
    print("\n=== SYSTEM SUMMARY ===")
    for k, v in summary.items():
        print(f"{k}: {v}")

    # Show hydraulic profiles (multiple figures for multiple branches)
    # Generate all plots
    # add first row to df_results for plotting the row contains the following: {'Pipe_ID': Source, 'Start_Junction': Source , 'End_Junction': Source, 'Distance_m': 0,
    #        'Elevation_m': reservoir_total_head, 'Total_Head_m':reservoir_total_head, 'Pressure_Head_m':reservoir_total_head, 'Velocity_m_s': 0,
    #        'Reynolds':0 , 'Diameter_mm': 0, 'Flow_L_s':0}
    # print(df_results)


    system_data = net.system_data
    # get all df_result data to dict where key is Pipe_ID and value is a dict of the row data
    # pipes_dict = {row['Pipe_ID']: row.to_dict() for _, row in df_results.iterrows()}
    # pipes_dict = net.pipes
    df_source = pd.DataFrame({'Pipe_ID': 'Source', 'Start_Junction': 'Source', 'End_Junction': 'Source', 'Distance_m': 0,'Elevation_m': system_data['reservoir_total_head'],
                              'Total_Head_m': system_data['reservoir_total_head'], 'Pressure_Head_m': system_data['reservoir_total_head'], 'Velocity_m_s': 0, 'Reynolds': 0, 'Diameter_mm': 0, 'Flow_L_s': 0}, index=[0])
    df_results = pd.concat([df_source, df_results], ignore_index=True)
    # print(df_results.columns)
    plots = detect_branches(df_results, net)
    # print(dir(plots))
    # Show individual plots



    # plots = generate_all_plots(df_results, net)

    # Show individual plots
    for fig in plots['hydraulic_profiles']:
        fig.show()

    plots['pipe_performance'].show()
    # plots['branch_comparison'].show()
    # plots['system_summary'].show()
