from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import os
from werkzeug.utils import secure_filename

from parser import parse_all_notes
from graph_builder import (
    build_graph,
    find_orphans,
    find_broken_links,
    find_hubs,
    avg_connections,
    get_stats,
    get_adjacency_matrix,
    get_shortest_path,
    save_snapshot,
    get_snapshots
)


app = Flask(__name__)
app.secret_key = "change_this_secret_key"

# Folder where uploaded markdown files will be stored
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------------------- HOME ---------------------- #
@app.route("/")
def home():
    return render_template("home.html")


# ---------------------- UPLOAD ---------------------- #
@app.route("/upload", methods=["GET", "POST"])
def upload_notes():
    if request.method == "POST":
        # Check both inputs
        files = request.files.getlist("files")
        folder_files = request.files.getlist("folder_files")
        
        all_files = files + folder_files
        
        # Filter empty
        valid_files = [f for f in all_files if f.filename != ""]

        if not valid_files:
            flash("Please select at least one Markdown file.")
            return redirect(url_for("upload_notes"))

        # Clear existing uploads? 
        # For now, let's keep it additive or maybe clear it to avoid stale data mixing.
        # Ideally we'd have sessions or projects. For this simple app, we might want to clear.
        # But let's just overwrite.
        
        for file in valid_files:
            if file and file.filename.endswith(".md"):
                # file.filename might contain paths like "folder/sub/file.md"
                # We want to preserve this structure relative to UPLOAD_FOLDER
                
                # Sanitize the path components
                filename = file.filename.replace("\\", "/") # Normalize separators
                parts = filename.split("/")
                safe_parts = [secure_filename(part) for part in parts]
                safe_filename = os.path.join(*safe_parts)
                
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                file.save(save_path)

        flash(f"{len(valid_files)} files uploaded successfully!")
        return redirect(url_for("analyze"))

    return render_template("upload.html")


# ---------------------- RESET ---------------------- #
@app.route("/reset", methods=["POST"])
def reset_notes():
    folder = app.config["UPLOAD_FOLDER"]
    try:
        # Delete all files and subdirectories in the uploads folder
        for root, dirs, files in os.walk(folder, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        flash("All notes and data cleared successfully!")
    except Exception as e:
        flash(f"Error clearing data: {str(e)}")
    
    return redirect(url_for("upload_notes"))


# ---------------------- ANALYSIS PAGE ---------------------- #
@app.route("/analyze")
def analyze():
    folder = app.config["UPLOAD_FOLDER"]

    parsed_notes = parse_all_notes(folder)
    if not parsed_notes:
        flash("No Markdown files found. Please upload some first.")
        return redirect(url_for("upload_notes"))

    G = build_graph(parsed_notes)

    orphans = find_orphans(G)
    broken = find_broken_links(parsed_notes)
    hubs = find_hubs(G)
    avg_conn = avg_connections(parsed_notes)
    stats = get_stats(G)

    context = {
        "parsed_notes": parsed_notes,
        "orphans": orphans,
        "broken": broken,
        "hubs": hubs,
        "avg_conn": avg_conn,
        "stats": stats,
    }

    return render_template("analysis.html", **context)


# ---------------------- GRAPH DATA (JSON) ---------------------- #
@app.route("/graph-data")
def graph_data():
    folder = app.config["UPLOAD_FOLDER"]
    parsed_notes = parse_all_notes(folder)
    G = build_graph(parsed_notes)

    nodes = []
    for n in G.nodes():
        # Get metadata from parsed_notes if available
        meta = parsed_notes.get(n, {})
        nodes.append({
            "id": n, 
            "label": n,
            "headings": meta.get("headings", []),
            "links": meta.get("links", [])
        })
    
    edges = [{"from": u, "to": v} for u, v in G.edges()]

    return jsonify({"nodes": nodes, "edges": edges})


# ---------------------- GRAPH PAGE ---------------------- #
@app.route("/graph")
def graph_view():
    return render_template("graph.html")

# ---------------------- SHORTEST PATH ---------------------- #
@app.route("/shortest-path", methods=["POST"])
def shortest_path():
    data = request.json
    source = data.get("source")
    target = data.get("target")
    
    folder = app.config["UPLOAD_FOLDER"]
    parsed_notes = parse_all_notes(folder)
    G = build_graph(parsed_notes)
    
    path = get_shortest_path(G, source, target)
    
    if path:
        return jsonify({"path": path, "length": len(path) - 1})
    else:
        return jsonify({"error": "No path found or invalid nodes"}), 404


# ---------------------- ADJACENCY MATRIX ---------------------- #
@app.route("/adjacency-matrix")
def adjacency_matrix():
    folder = app.config["UPLOAD_FOLDER"]
    parsed_notes = parse_all_notes(folder)
    G = build_graph(parsed_notes)
    
    data = get_adjacency_matrix(G)
    return jsonify(data)


# ---------------------- SNAPSHOTS ---------------------- #
@app.route("/snapshots", methods=["GET", "POST"])
def snapshots():
    folder = app.config["UPLOAD_FOLDER"]
    
    if request.method == "POST":
        parsed_notes = parse_all_notes(folder)
        G = build_graph(parsed_notes)
        filename = save_snapshot(G, folder)
        return jsonify({"message": "Snapshot saved", "filename": filename})
    
    data = get_snapshots(folder)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
