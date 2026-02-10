# Copilot Instructions for C_Love_Coding

## Project Overview
A Python-based workflow dependency visualization tool that models project tasks with status tracking and dependency relationships. The codebase uses NetworkX for graph construction and Matplotlib for visualization.

## Architecture & Core Pattern
**Single responsibility structure:**
- **workflow.py**: Defines workflow tasks as a list of dictionaries with dependencies, constructs a directed graph using NetworkX, and visualizes it with Matplotlib

**Data model:**
- Each task is a dict: `{"task": string, "status": string, "depends_on": list[string]}`
- Status values: "Done", "In Progress", "Blocked", "Not Started"
- Dependencies reference task names as strings

**Graph construction approach:**
- Uses directed graphs (DiGraph) where edges flow from dependency → dependent task (opposite of typical parent→child)
- Example: `{"task": "Testing", "depends_on": ["Backend API"]}` creates edge Backend API → Testing

## Key Implementation Details

### Status-to-Color Mapping
- "Done" → green
- "In Progress" → blue
- "Blocked" → red
- Other → gray

Apply this mapping when rendering nodes or generating status reports.

### Visualization
- Uses `nx.spring_layout()` for automatic node positioning
- Node size: 2000, font size: 10, arrows enabled for edge direction
- Color coding must be applied before drawing to reflect current status

## Common Workflows
- **Adding a task**: Append to workflow list, add dependencies by task name
- **Changing status**: Modify the "status" field directly in the workflow list
- **Viewing dependencies**: Iterate `G.nodes(data=True)` for node data or `G.edges()` for relationships
- **Running visualization**: Execute the script directly - `plt.show()` displays the dependency graph

## Programmatic Examples

### Querying the Graph
```python
# Get all blockers for a task (incoming edges - tasks this depends on)
blockers = list(G.predecessors("Testing"))  # ["Backend API", "Design UI"]

# Get all dependents (tasks blocked by this one - outgoing edges)
dependents = list(G.successors("Database Setup"))  # ["Backend API"]

# Get node status
status = G.nodes["Testing"]["status"]

# Find all tasks with a specific status
done_tasks = [node for node, data in G.nodes(data=True) if data["status"] == "Done"]

# Check if graph has cycles (indicates circular dependencies)
has_cycle = not nx.is_directed_acyclic_graph(G)
```

### Modifying the Graph
```python
# Add a new task to both workflow list and graph
new_task = {"task": "Documentation", "status": "Not Started", "depends_on": ["Testing"]}
workflow.append(new_task)
G.add_node("Documentation", status="Not Started")
G.add_edge("Testing", "Documentation")

# Update a task's status
task_name = "Backend API"
for item in workflow:
    if item["task"] == task_name:
        item["status"] = "Done"
        break
G.nodes[task_name]["status"] = "Done"

# Remove a task (requires cleanup)
task_to_remove = "Documentation"
workflow = [t for t in workflow if t["task"] != task_to_remove]
G.remove_node(task_to_remove)
```

## Important Notes
- Do not modify task names after adding dependencies (breaks graph linking)
- The graph direction (dependency → task) may differ from intuitive ordering - verify edge direction when adding features
- NetworkX uses string-based node references; ensure task names are unique
- When modifying tasks, keep workflow list and graph in sync - update both sources
