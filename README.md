import os
import pandas as pd
from branch_calculation.network import BranchNetwork
from branch_calculation.analysis import analyze_network
from branch_calculation.plots import plot_branches

# Define paths to your input files
project_path = os.path.dirname(os.path.abspath(__file__))
csv_path = "network_tree_template.csv"
pipe_prices_path = "pipe_prices.xlsx"

df = pd.read_csv(os.path.join(project_path, csv_path))
pipe_prices = pd.read_excel(os.path.join(project_path, pipe_prices_path))

# Initialize and configure the network
net = BranchNetwork()
net.set_system_data(reservoir_elevation=300, reservoir_total_head=300)
net.load_from_dataframe(df)

# Run hydraulic analysis
results = analyze_network(net)

# Print results
print(results['df_res'])
print("=== SYSTEM SUMMARY ===")
for k, v in results['summary'].items():
    print(f"{k}: {v}")

# Plot hydraulic profiles per branch
plots = plot_branches(results['results_branch'], minimum_pressure_constraint=2)
