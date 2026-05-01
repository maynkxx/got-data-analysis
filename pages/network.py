import json

import pandas as pd

import networkx as nx

from pyvis.network import Network

from collections import defaultdict

import os

with open("data/raw/episodes.json") as f:

    episodes_json = json.load(f)

chars_df = pd.read_csv("data/cleaned/characters_clean.csv")

screentime_df = pd.read_csv("data/cleaned/screentime_total.csv")

top_n = 120

top_chars_list = (

    screentime_df[screentime_df["total_screentime_overall"] > 0]

    .nlargest(top_n, "total_screentime_overall")["character"]

    .tolist()

)

top_chars_set = set(top_chars_list)

screentime_lookup = dict(zip(screentime_df["character"], screentime_df["total_screentime_overall"]))

house_colors = {

    "house stark":       "#A8A8A8",

    "house lannister":   "#FFD700",

    "house targaryen":   "#CC0000",

    "house baratheon":   "#F4C430",

    "house tyrell":      "#228B22",

    "house martell":     "#FF8C00",

    "house greyjoy":     "#5F7A8A",

    "house tully":       "#4169E1",

    "house arryn":       "#87CEEB",

    "house bolton":      "#8B0000",

    "house frey":        "#A0522D",

    "night's watch":     "#444444",

    "wildling":          "#8B4513",

    "house mormont":     "#556B2F",

    "house reed":        "#2E8B57",

}

def get_house_color(house):

    h = str(house).lower()

    for key, color in house_colors.items():

        if key in h:

            return color

    return "#888888"

def hex_to_rgba(hex_color, alpha=0.35):

    """Convert hex color to rgba string for dead characters"""

    hex_color = hex_color.lstrip("#")

    r = int(hex_color[:2], 16)

    g = int(hex_color[2:4], 16)

    b = int(hex_color[4:6], 16)

    return f"rgba({r},{g},{b},{alpha})"

edge_weights = defaultdict(int)

for ep in episodes_json["episodes"]:

    for scene in ep.get("scenes", []):

        chars_in_scene = [

            c["name"] for c in scene.get("characters", [])

            if c.get("name") and c["name"] in top_chars_set

        ]

        for i in range(len(chars_in_scene)):

            for j in range(i + 1, len(chars_in_scene)):

                a, b = sorted([chars_in_scene[i], chars_in_scene[j]])

                edge_weights[(a, b)] += 1

min_scenes = 5

filtered_edges = {k: v for k, v in edge_weights.items() if v >= min_scenes}

print(f"Nodes: {len(top_chars_set)} | Edges (>={min_scenes} scenes): {len(filtered_edges)}")

chars_lookup = {}

for _, row in chars_df.iterrows():

    chars_lookup[row["name"]] = row

G = nx.Graph()

chars_in_graph = set()

for (a, b) in filtered_edges:

    chars_in_graph.add(a)

    chars_in_graph.add(b)

for char in chars_in_graph:

    screentime = screentime_lookup.get(char, 0)

    node_size = max(12, min(55, int(screentime / 800)))

    char_info = chars_lookup.get(char, None)

    house = char_info["house"] if char_info is not None else "Unknown"

    is_alive = int(char_info["is_alive"]) if char_info is not None else 1

    actually_died = int(char_info["actually_died"]) if char_info is not None else 0

    base_color = get_house_color(house)

    color = base_color if is_alive == 1 else hex_to_rgba(base_color, 0.35)

    label = char if screentime > 8000 else ""

    status = "Alive" if is_alive == 1 else "Dead"

    screen_mins = round(screentime / 60, 1)

    G.add_node(

        char,

        size=node_size,

        color=color,

        label=label,

        title=f"<b>{char}</b><br>House: {house}<br>Status: {status}<br>Screen time: {screen_mins} min",

        borderWidth=2 if is_alive == 1 else 1,

    )

for (a, b), weight in filtered_edges.items():

    width = max(0.5, min(8, weight / 5))

    G.add_edge(a, b, weight=weight, value=width, title=f"Shared scenes: {weight}")

print(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

def build_network(graph):

    net = Network(

        height="750px",

        width="100%",

        bgcolor="#0D1117",

        font_color="white",

    )

    net.from_nx(graph)

    net.set_options("""
    {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -80,
          "centralGravity": 0.005,
          "springLength": 120,
          "springConstant": 0.05,
          "damping": 0.9
        },
        "solver": "forceAtlas2Based",
        "stabilization": {
          "enabled": true,
          "iterations": 200,
          "updateInterval": 25
        }
      },
      "edges": {
        "smooth": { "type": "continuous" },
        "color": { "opacity": 0.3 }
      },
      "nodes": {
        "font": {
          "size": 13,
          "strokeWidth": 3,
          "strokeColor": "#0D1117"
        }
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 80,
        "hideEdgesOnDrag": true,
        "navigationButtons": true
      }
    }
    """)

    return net

os.makedirs("assets", exist_ok=True)

net = build_network(G)

net.save_graph("assets/network.html")

print("Saved to assets/network.html")

if __name__ == "__main__":

    import webbrowser

    webbrowser.open("file://" + os.path.abspath("assets/network.html"))
