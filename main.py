import sys
from pathlib import Path
from pyvis.network import Network
import re

src_path = [Path(p) for p in sys.argv[1:]]

def iter_src_pathes():
    for p in src_path:
        for f in p.rglob("*"):
            yield f

net = Network(notebook = True, cdn_resources = "remote",
                directed=True,
                bgcolor = "#222222",
                font_color = "white",
                height = "750px",
                width = "100%",
)

nodes = set()

for f in iter_src_pathes():
    if not f.is_file(): continue

    if f.suffix in ('.hpp', '.h'):
        nodes.add(f.name)
    # if f.suffix == '.cpp':
    #     nodes.add(f.name)

net.add_nodes(nodes)

for f in iter_src_pathes():
    if not f.is_file(): continue
    if f.suffix not in ('.hpp', '.h'): continue

    text = f.read_text()
    includes = re.findall(r'#include\s+"(\w+.hpp)"', text)

    for include in includes:
        if not include in nodes:
            net.add_nodes(include)
        net.add_edge(include, f.name)


net.show("graph.html")
