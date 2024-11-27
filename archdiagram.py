import matplotlib.pyplot as plt
import networkx as nx
# do  pip install matplotlib networkx
# Initialize directed graph
G = nx.DiGraph()

# Define nodes (components in the system)
nodes = [
    "User Input", 
    "NLP Processing (spaCy)", 
    "Meal Type Analyzer", 
    "Recipe Recommendation Engine", 
    "Recipe Suggestions", 
    "User Profile Management", 
    "Weight Decay Mechanism", 
    "Recipe Database"
]

# Add nodes to the graph
G.add_nodes_from(nodes)

# Define edges (flow of data between components)
edges = [
    ("User Input", "NLP Processing (spaCy)"),
    ("NLP Processing (spaCy)", "Meal Type Analyzer"),
    ("Meal Type Analyzer", "Recipe Recommendation Engine"),
    ("Meal Type Analyzer", "User Profile Management"),
    ("User Profile Management", "Weight Decay Mechanism"),
    ("User Profile Management", "Recipe Recommendation Engine"),
    ("Recipe Recommendation Engine", "Recipe Database"),
    ("Recipe Recommendation Engine", "Recipe Suggestions")
]

# Add edges to the graph
G.add_edges_from(edges)

# Set up node positions for a clearer layout
pos = {
    "User Input": (0, 3),
    "NLP Processing (spaCy)": (1, 3),
    "Meal Type Analyzer": (2, 3),
    "Recipe Recommendation Engine": (3, 3),
    "Recipe Suggestions": (4, 3),
    "User Profile Management": (2, 2),
    "Weight Decay Mechanism": (1, 2),
    "Recipe Database": (3, 2)
}

# Draw the network
plt.figure(figsize=(14, 8))
nx.draw(G, pos, with_labels=True, node_size=3500, node_color="lightblue", font_size=10, font_weight="bold", arrows=True)
nx.draw_networkx_edges(G, pos, edgelist=edges, arrowstyle="->", arrowsize=20)

# Show plot
plt.title("Architecture Diagram for Recipe Suggestion System")
plt.show()
