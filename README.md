# Branch Network Hydraulic Analyzer (BNHA)

A Python package for **hydraulic analysis and optimization** of branched water distribution networks. Supports pressure, head loss, velocity, and economic assessments for branched systems defined via CSV input.

---

## 🚀 Features

* Analyze multi-branch pipe networks from simple `.csv` files
* Compute:

  * Head losses (Hazen-Williams)
  * Pressure and total head at all nodes
  * Flow velocities and Reynolds numbers
* Visualize:

  * Hydraulic profiles per branch (HGL, EGL, static head)
  * Pipe performance metrics
* Run pipe diameter sensitivity analysis

---

## 📦 Installation

### From Local `.whl` File

1. Copy the generated `.whl` file to your working directory (e.g. `dist/branch_network_hydraulics-0.1.0-py3-none-any.whl`)
2. In terminal or Jupyter Notebook:

```bash
pip install ./branch_network_hydraulics-0.1.0-py3-none-any.whl
```

---

## 🛠 Usage

### 1. Prepare Your Network CSV

Use the template format:

```csv
pipe,diameter_m,start_junc,end_junc,length_m,flow_cmh,end_junc_elevation,static_head,hwc,branch_end,end_junc_path
p1,0.5,source,a,900,140,250,300,140,0,p1
p2,0.5,a,b,700,140,270,300,140,0,p1,p2
p3,0.5,b,v1,5000,100,240,300,140,1,p1,p2,p3
p4,0.5,b,v2,100,40,230,300,140,1,p1,p2,p4
```

Save it as `network.csv`

---

### 2. Example Script

```python
import pandas as pd
from branch_optimizer.network import BranchNetwork
from branch_optimizer.analysis import analyze_network
from branch_optimizer.plots import plot_hydraulic_profile

# Load network from CSV
df = pd.read_csv("network.csv")

# Initialize the network
net = BranchNetwork()
net.set_system_data(reservoir_elevation=300, reservoir_total_head=320)
net.load_from_dataframe(df)

# Inject paths to each pipe (for branch recognition)
for pid, path in net.get_branch_paths().items():
    net.pipes[pid]['path'] = path

# Analyze
df_results, summary = analyze_network(*net.to_dict())

# Plot
figs = plot_hydraulic_profile(df_results, net.system_data)
for fig in figs:
    fig.show()
```

---

## 📊 Sensitivity Optimization

```python
from branch_optimizer.optimizer import diameter_sensitivity_analysis

# Run sensitivity on all pipes between 100mm and 600mm
df_test = diameter_sensitivity_analysis(net.pipes, net.system_data, diameter_range=(0.1, 0.6, 0.1))
print(df_test)
```

---

## 📁 Directory Layout (When Cloned)

```
branch_optimizer/
├── hydraulics.py      # Core fluid equations
├── network.py         # Data model for network
├── analysis.py        # Node-by-node head + velocity calcs
├── plots.py           # Visualization tools
├── optimizer.py       # Sensitivity analysis
```

---

## 📜 License

MIT License (c) 2025 Your Name

---

## 🌐 Future Plans

* Pipe cost optimization
* Automated diameter selection
* Integration with EPANET or pressure zone mapping
