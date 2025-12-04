import networkx as nx
import json
import time
import os


def build_graph(parsed_notes):
    """
    Build a directed graph from parsed markdown notes.
    Nodes = filenames
    Edges = outgoing links between notes
    """
    G = nx.DiGraph()

    # Add nodes
    for name in parsed_notes:
        G.add_node(name)

    # Add edges for valid links
    for file, data in parsed_notes.items():
        for link in data["links"]:
            if link in parsed_notes:
                G.add_edge(file, link)

    return G


def find_orphans(G):
    """Orphan pages: no incoming AND no outgoing edges."""
    return [
        node for node in G.nodes()
        if G.in_degree(node) == 0 and G.out_degree(node) == 0
    ]


def find_broken_links(parsed_notes):
    """
    Broken links = links pointing to files that do not exist.
    Returns a list of (source_file, missing_target).
    """
    broken = []
    all_files = set(parsed_notes.keys())

    for file, data in parsed_notes.items():
        for link in data["links"]:
            if link not in all_files:
                broken.append((file, link))

    return broken


def find_hubs(G, top=5):
    """Hubs = nodes with highest incoming link count."""
    hubs = sorted(G.in_degree(), key=lambda x: x[1], reverse=True)
    return hubs[:top]


def avg_connections(parsed_notes):
    """Average number of outgoing links per page."""
    if not parsed_notes:
        return 0
    total = sum(len(data["links"]) for data in parsed_notes.values())
    return total / len(parsed_notes)


def get_stats(G):
    """Basic statistics for dashboard."""
    return {
        "total_pages": G.number_of_nodes(),
        "total_links": G.number_of_edges(),
        "connected_components": nx.number_weakly_connected_components(G)
        if G.number_of_nodes() > 0 else 0,
    }

def get_adjacency_matrix(G):
    """Returns the adjacency matrix as a list of lists (and the nodelist)."""
    nodes = list(G.nodes())
    matrix = nx.to_numpy_array(G, nodelist=nodes)
    return {"nodes": nodes, "matrix": matrix.tolist()}

def get_shortest_path(G, source, target):
    """Finds the shortest path between two nodes."""
    try:
        path = nx.shortest_path(G, source=source, target=target)
        return path
    except nx.NetworkXNoPath:
        return None
    except nx.NodeNotFound:
        return None

def save_snapshot(G, folder):
    """Saves a snapshot of the current graph stats."""
    stats = get_stats(G)
    stats["timestamp"] = time.time()
    stats["date"] = time.strftime("%Y-%m-%d %H:%M:%S")
    
    snapshot_dir = os.path.join(folder, "snapshots")
    os.makedirs(snapshot_dir, exist_ok=True)
    
    filename = f"snapshot_{int(stats['timestamp'])}.json"
    with open(os.path.join(snapshot_dir, filename), "w") as f:
        json.dump(stats, f, indent=4)
    return filename

def get_snapshots(folder):
    """Retrieves all saved snapshots."""
    snapshot_dir = os.path.join(folder, "snapshots")
    if not os.path.exists(snapshot_dir):
        return []
    
    snapshots = []
    for f in os.listdir(snapshot_dir):
        if f.endswith(".json"):
            with open(os.path.join(snapshot_dir, f), "r") as file:
                snapshots.append(json.load(file))
    
    return sorted(snapshots, key=lambda x: x["timestamp"], reverse=True)
