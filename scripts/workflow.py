
import networkx as nx
import matplotlib.pyplot as plt

# Workflow with dependencies
workflow = [
    {"task": "Design UI", "status": "In Progress", "depends_on": []},
    {"task": "Backend API", "status": "Blocked", "depends_on": ["Database Setup"]},
    {"task": "Database Setup", "status": "Done", "depends_on": []},
    {"task": "Testing", "status": "Not Started", "depends_on": ["Backend API", "Design UI"]},
    {"task": "Deployment", "status": "In Progress", "depends_on": ["Testing"]}
]

# Create graph
G = nx.DiGraph()  # Directed graph to show dependencies

# Add nodes and edges
for item in workflow:
    G.add_node(item["task"], status=item["status"])
    for dep in item["depends_on"]:
        G.add_edge(dep, item["task"])  # edge from dependency → task

# Define colors based on status
color_map = []
for node in G.nodes(data=True):
    status = node[1]['status']
    if status == "Done":
        color_map.append("green")
    elif status == "In Progress":
        color_map.append("blue")
    elif status == "Blocked":
        color_map.append("red")
    else:
        color_map.append("gray")

# Draw graph
pos = {node: (i, 0) for i, node in enumerate(G.nodes())}
nx.draw(G, pos, with_labels=True, node_color=color_map, node_size=4000, font_size=10, font_color="white", arrows=True)
plt.show()
