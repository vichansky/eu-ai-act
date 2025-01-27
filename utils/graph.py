import networkx as nx
import pandas as pd
from utils.formatting import format_node_output

class EUAIActGraph:
    def __init__(self, dataframe):
        # Create copy of DataFrame purposely to make a network graph with
        self.graph_df = dataframe.copy()

        # Initialise a directed graph
        self.G = nx.DiGraph()

    # Convert columns 'Type' to Object type
    def prepare_graph_dataframe(self):
        self.graph_df['Type'] = self.graph_df['Type'].astype('object')

    # Add nodes with node_type attribute and remove empty spaces as was having trouble due to this
    def add_nodes(self):
        for index, row in self.graph_df.iterrows():
            if row['ID']:  # Ensure ID is not empty or contains whitespace
                self.G.add_node(row['ID'], node_type=row['Type'])

        # Remove empty nodes in the graph
        empty_nodes = [node for node in self.G.nodes if node == '']
        self.G.remove_nodes_from(empty_nodes)

    # Add edges based on the DataFrame columns containing information on referenced Articles and Recitals
    def add_edges(self):
        for index, row in self.graph_df.iterrows():
            for col in self.graph_df.columns:
                if col.isdigit() and pd.notna(row[col]):  # Check if the column name is a digit and not NaN
                    self.G.add_edge(row['ID'], row[col])

    def create_graph(self):
        self.prepare_graph_dataframe()
        self.add_nodes()
        self.add_edges()

        print("\n Network graph is created! \n")

        return self.G

def run_graph(dataframe):

    # Initialise the EUAIActGraph Class()
    graph_maker = EUAIActGraph(dataframe)

    # Create the network graph
    network_graph = graph_maker.create_graph()

    print("Successfully created network graph for the EU AI Act articles and recitals! \n")

    return network_graph
