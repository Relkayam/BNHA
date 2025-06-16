# network.py

import pandas as pd

class BranchNetwork:
    """
    Represents a branched water distribution network.
    Allows loading from structured CSV containing both hydraulic and topological data.
    """

    def __init__(self):
        self.pipes = {}           # Stores pipe data keyed by pipe ID
        self.system_data = {      # System-wide parameters
            'reservoir_elevation': None,
            'reservoir_total_head': None,
            'min_pressure_head': 25,
            'max_velocity': 2.5
        }
        self.nodes = set()        # Set of unique junctions
        self.paths = {}           # Pipe ID -> full path to that pipe

    def set_system_data(self, *, reservoir_elevation, reservoir_total_head, min_pressure_head=25, max_velocity=2.5):
        """
        Define overall system parameters such as reservoir conditions and design limits.
        """
        self.system_data.update({
            'reservoir_elevation': reservoir_elevation,
            'reservoir_total_head': reservoir_total_head,
            'min_pressure_head': min_pressure_head,
            'max_velocity': max_velocity
        })

    def load_from_dataframe(self, df):
        """
        Load network from a structured DataFrame (like network_tree_template.csv).
        Expects columns: pipe, diameter_m, start_junc, end_junc, length_m, flow_cmh,
                        end_junc_elevation, static_head, hwc, branch_end, end_junc_path
        """
        for _, row in df.iterrows():
            pipe_id = row['pipe']
            self.pipes[pipe_id] = {
                'diameter_m': row['diameter_m'],
                'start_junc': row['start_junc'],
                'end_junc': row['end_junc'],
                'length_m': row['length_m'],
                'flow_cms': row['flow_cmh'] / 3600,
                'end_junc_elevation': row['end_junc_elevation'],
                'static_head': row['static_head'],
                'hwc': row['hwc'],
                'branch_end': bool(row['branch_end'])
            }
            self.nodes.add(row['start_junc'])
            self.nodes.add(row['end_junc'])
            self.paths[pipe_id] = row['end_junc_path'].split(',')

    def to_dict(self):
        """
        Export internal structure as dictionaries for analysis.
        Returns:
            - pipes_dict: dict of pipe attributes
            - system_data: dict of system-wide settings
        """
        return self.pipes, self.system_data

    def get_branch_paths(self):
        """
        Return a dictionary mapping each pipe to its full path as a list.
        Useful for plotting, traversal, or branch-specific checks.
        """
        return self.paths

    def get_nodes(self):
        """
        Return a set of all unique nodes (junctions) in the network.
        """
        return self.nodes

    def get_terminal_branches(self):
        """
        Identify and return all terminal branches in the network.
        A terminal branch is where 'branch_end' is True.

        Returns:
            List of pipe IDs marking the ends of branches.
        """
        return [pid for pid, pdata in self.pipes.items() if pdata.get('branch_end')]

    def count_terminal_branches(self):
        """
        Count the number of end (leaf) branches in the network.

        Returns:
            Integer count of terminal branches.
        """
        return len(self.get_terminal_branches())



if __name__ == "__main__":
    # Example usage
    import os
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    df = pd.read_csv(os.path.join(project_path, 'network_tree_template.csv'))
    print(df)
    network = BranchNetwork()
    network.load_from_dataframe(df)
    network.set_system_data(reservoir_elevation=100, reservoir_total_head=120)

    pipes, system_data = network.to_dict()
    print("Pipes:", pipes)
    print("System Data:", system_data)
    print("Nodes:", network.get_nodes())
    print("Branch Paths:", network.get_branch_paths())
    print("Terminal Branches:", network.get_terminal_branches())
    print("Count of Terminal Branches:", network.count_terminal_branches())
