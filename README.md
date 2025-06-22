# Branch Network Hydraulic Analyzer (BNHA)

**BNHA** is a Python package for advanced **hydraulic analysis and pipe diameter optimization** in branched (tree-like) water distribution networks.

It supports:
- Pressure, velocity, and head loss analysis
- Pipe diameter selection using linear/mixed-integer optimization
- Visualization of hydraulic profiles and branch paths

Designed for civil engineers, hydraulic modelers, and researchers, the package processes structured CSV and Excel inputs and produces rich, branch-aware outputs.

---

## 🚀 Features

- 💧 Analyze hydraulic performance in branched networks
- 🔧 Optimize pipe diameters using:
  - Discrete section-based selection (MIP)
  - Continuous-length optimization (LP)
- 📈 Visualize:
  - Hydraulic Grade Line (HGL), Energy Grade Line (EGL), static head
  - Pipe-level metrics (diameter, velocity, head loss)
- 📊 Perform sensitivity studies on pipe sizing

---

## 📦 Installation

Install using pip:

```bash
pip install branch-network-hydraulics


 Usage
1. Analyze a Network
python
Copy
Edit
import os
import pandas as pd
from branch_calculation.network import BranchNetwork
from branch_calculation.analysis import analyze_network
from branch_calculation.plots import plot_branches

# Load input files
df = pd.read_csv("network_tree_template.csv")
pipe_prices = pd.read_excel("pipe_prices.xlsx")

# Initialize network
net = BranchNetwork()
net.set_system_data(reservoir_elevation=300, reservoir_total_head=300)
net.load_from_dataframe(df)

# Analyze
results = analyze_network(net)
print(results['df_res'])
print(results['summary'])

# Plot results
plot_branches(results['results_branch'], minimum_pressure_constraint=2)
2. Full-Section Diameter Optimization
python
Copy
Edit
from branch_calculation.optimizer import full_section_optimal_diameter

results = full_section_optimal_diameter(net, pipe_prices, minimum_pressure_constraint=2)
print(results['df_res'])

plot_branches(results['results_branch'], minimum_pressure_constraint=2)
3. Classical (Continuous-Length) Optimization
python
Copy
Edit
from branch_calculation.optimizer import classic_optimal_diameter_optimization

results = classic_optimal_diameter_optimization(net, pipe_prices, minimum_pressure_constraint=2)
print(results['df_res'])

plot_branches(results['results_branch'], minimum_pressure_constraint=2)
📁 Example Input Format (network_tree_template.csv)
csv
Copy
Edit
pipe,diameter_m,start_junc,end_junc,length_m,flow_cmh,end_junc_elevation,static_head,hwc,branch_end,end_junc_path
p1,0.5,source,a,900,140,250,300,140,0,p1
p2,0.5,a,b,700,140,270,300,140,0,p1,p2
p3,0.5,b,v1,5000,100,240,300,140,1,p1,p2,p3
p4,0.5,b,v2,100,40,230,300,140,1,p1,p2,p4
📂 Project Layout
bash
Copy
Edit
branch_calculation/
├── network.py              # Network loading and path logic
├── analysis.py             # Head loss, pressure, and velocity analysis
├── optimizer.py            # Discrete and continuous optimization models
├── plots.py                # Branch and HGL/EGL plotting tools
├── hydraulics.py           # Hazen-Williams & Reynolds calculations
📜 License
MIT License © 2025 Roy Elkayam
Head of the Modeling Department, Mekorot Water Company, Lincoln 9, Israel

🌐 Roadmap
✅ Pressure-based hydraulic analysis

✅ Discrete and continuous pipe diameter optimization

✅ Head loss and velocity calculation per branch

✅ Visualization of branch-level HGL/EGL profiles

🔜 EPANET or GIS integration

🔜 Multi-objective optimization (cost, pressure, velocity)



