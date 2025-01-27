import networkx as nx
import pandas as pd
import pickle as pk
import streamlit as st
from pyvis.network import Network
from utils.scraper import run_scraper, load_articles_and_recitals_to_dataframe
from utils.formatting import run_dataframe_processor, alphanumeric_sort_key, format_node_output
from utils.graph import run_graph

if __name__=="__main__":
    # To scrape the articles and recitals every run, uncomment the line below with function run_scraper()
    # Otherwise, if file is found, it will load via the below function load_articles_and_recitals_to_dataframe()
    # run_scraper()

    # Load or create a network graph if one is not found
    try:
        # Load the graph from pickle file
        with open("./data/eu-ai-act-graph.pkl", "rb") as pickle_file:
            G = pk.load(pickle_file)

    except FileNotFoundError:
        # Load DataFrame and if needed run scraper
        df = load_articles_and_recitals_to_dataframe()

        # Show preview of DataFrame
        print(df.head(), "\n")

        # Run data processing steps
        result_df = run_dataframe_processor(df)

        # Show preview of formatted and processed DataFrame
        print(result_df.head(), "\n")

        # Create a network graph with nodes and connecting edges
        G = run_graph(result_df)

        # Save the graph to a pickle file for efficiency
        with open("./data/eu-ai-act-graph.pkl", "wb") as pickle_file:
            pk.dump(G, pickle_file)

print("Successfully loaded network graph! Creating a PyVis network now \n"
      "............................................................... \n")

# Set the page configuration to wide mode
st.set_page_config(layout="wide")

# Create a PyVis network
net = Network(notebook=False, width="100%", height="700px")

# Enable the force atlas 2 physics layout directly
net.force_atlas_2based()

# Recalculate layout only once and store positions in session state
if 'positions' not in st.session_state:
    positions = nx.spring_layout(G, seed=1)
    st.session_state.positions = positions

# Add nodes and edges from the graph to the PyVis network
for node in G.nodes():
    net.add_node(node, label=str(node), x=st.session_state.positions[node][0], y=st.session_state.positions[node][1],
                 title=f"Node {node}", size=10)

for edge in G.edges():
    net.add_edge(edge[0], edge[1])

# Sort the nodes (articles and recitals) alphabetically and create dropdown menu to select a node
st.sidebar.markdown('<div style="font-size:24px; font-weight:bold; color:#003399;">Select a node to highlight (or search using the menu)</div>', unsafe_allow_html=True)
selected_node = st.sidebar.selectbox("Note: Nodes beginning with A stand for Article, with R standing for Recital", sorted(list(G.nodes()), key=alphanumeric_sort_key))

# Display the selected node information together with its neighbours
if selected_node is not None:
    # Format and show selected node in a sidebar
    st.sidebar.write(f"Neighbours of {format_node_output(selected_node)}:")

    # Order and show neighbouring nodes to the selected node in the sidebar
    neighbouring_nodes = sorted(list(G.neighbors(selected_node)), key=alphanumeric_sort_key)

    for neighbour in neighbouring_nodes:
        st.sidebar.write(format_node_output(neighbour))

# Highlight selected node and its neighbours
highlighted_nodes = [selected_node] + list(G.neighbors(selected_node))

# Create a set of edges directly connected to the selected node
highlighted_edges = {(selected_node, neighbour) for neighbour in neighbouring_nodes} | {(neighbour, selected_node) for neighbour in neighbouring_nodes}

# Update node colors and size based on selection
for node in G.nodes():
    if node == selected_node:
        # Set the node border color and width
        net.get_node(node)['color'] = {
            'border': '#FFD700',  # European gold for the border
            'background': '#FFD700',  # Highlight the selected node
        }
        net.get_node(node)['borderWidth'] = 2  # Set the border width
        net.get_node(node)['size'] = 30  # Slightly larger size for selected node
    elif node in neighbouring_nodes:
        net.get_node(node)['color'] = {
            'border': '#FFD700',  # European gold for the border
            'background': '#4169E1',  # Highlight neighbours
        }
        net.get_node(node)['size'] = 15  # Slightly larger size for neighbours
    else:
        net.get_node(node)['color'] = '#003399' # Navy blue colour for all other nodes in graph
        net.get_node(node)['size'] = 10  # Default size

# Update edge colors based on selection
for edge in net.edges:
    if (edge['from'], edge['to']) in highlighted_edges or (edge['to'], edge['from']) in highlighted_edges:
        edge['color'] = '#FFD700' # European gold for highlighted edges
        edge['width'] = 2  # Thicker width for highlighted edges
    else:
        edge['color'] = '#C0C0C0'

# Generate the HTML for the graph
html_content = net.generate_html()

# Display the graph in Streamlit
st.components.v1.html(html_content, height=700)