document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("graph");
    if (!container) return;

    fetch("/graph-data")
        .then(response => response.json())
        .then(data => {
            const nodes = new vis.DataSet(data.nodes);
            const edges = new vis.DataSet(data.edges);

            const options = {
                physics: {
                    enabled: true,
                    barnesHut: {
                        gravitationalConstant: -4000,
                        centralGravity: 0.3,
                        springLength: 150,
                        springConstant: 0.01,
                    }
                },
                interaction: {
                    hover: true,
                    dragNodes: true,
                    zoomView: true,
                    selectConnectedEdges: true,
                },
                nodes: {
                    shape: "dot",
                    size: 14,
                },
                edges: {
                    arrows: "to",
                    smooth: true,
                }
            };

            new vis.Network(container, { nodes, edges }, options);
        })
        .catch(err => {
            console.error("Error loading graph data:", err);
        });
});
