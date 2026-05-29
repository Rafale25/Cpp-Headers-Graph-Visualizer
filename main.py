import argparse
import sys

parser = argparse.ArgumentParser(
            prog='C/C++ Include Grapher',
            description='Makes a graph from the #include directives',
            epilog='')

parser.add_argument('-ho', '--header_only', action='store_true', help='Graph only header files')
parser.add_argument('-all', '--all_includes', action='store_true', help='Also graph files not found in given paths')
parser.add_argument('-b', '--browser', action='store_true', help='Open in browser when program close')
parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
parser.add_argument('-i', '--inline', action='store_true', help='Inline html js and css (for offline viewing)')
parser.add_argument('paths', nargs='+', help='Paths of the folders you want to recursively search in')

if len(sys.argv) == 1:
    parser.print_help(sys.stderr)
    sys.exit(1)

args = parser.parse_args()

from pathlib import Path
from pyvis.network import Network
import networkx as nx
import re

FILES_MATCH = ('.hpp', '.h')
if not args.header_only:
    FILES_MATCH += ('.c', '.cpp')

if (args.verbose):
    print(f'Header only: {args.header_only}')
    print(f'paths: {args.paths}')
    print(f'{FILES_MATCH=}')

src_path = [Path(p) for p in args.paths]

def iter_src_pathes():
    for p in src_path:
        for f in p.rglob("*"):
            yield f

cdn_resources = 'in_line' if args.inline else 'local'

net = Network(notebook=False, cdn_resources=cdn_resources,
                directed=True,
                bgcolor = "#222222",
                font_color = "white",
                height = "750px",
                width = "100%",
)

nodes = set()

for f in iter_src_pathes():
    if not f.is_file(): continue

    if f.suffix in FILES_MATCH:
        nodes.add(f.name)

if args.verbose:
    print(f'Files found: {nodes}')

net.add_nodes(nodes)


COMMENT_RE = re.compile(
    r'//.*?$'                 # line comment
    r'|/\*.*?\*/'             # block comment (spans lines)
    r'|"(?:\\.|[^\\"\n])*"'   # string literal (kept, not stripped)
    r"|'(?:\\.|[^\\'\n])*'",  # char literal   (kept)
    re.DOTALL | re.MULTILINE,
)

def strip_comments(text):
    return COMMENT_RE.sub(lambda m: ' ' if m.group(0).startswith('/') else m.group(0), text)

for f in iter_src_pathes():
    if not f.is_file(): continue
    if f.suffix not in FILES_MATCH: continue

    text = strip_comments(f.read_text())
    includes = re.findall(r'#include\s+(?:"|<)(\S+)(?:"|>)', text)

    if args.verbose:
        print(f'{f.name}: {includes}')

    for include in includes:
        if not args.all_includes:
            if not include in nodes:
                continue
        if not include in nodes:
            net.add_node(include)

        net.add_edge(include, f.name)

import colorsys, random
def random_saturated_hex(s=0.9, v=0.95):
    r, g, b = colorsys.hsv_to_rgb(random.random(), s, v)
    return "#{:02x}{:02x}{:02x}".format(round(r * 255), round(g * 255), round(b * 255))


# Cycle coloring
edge_list = [(e['from'], e['to']) for e in net.get_edges()]
G = nx.DiGraph(edge_list)
for cyc in nx.simple_cycles(G):
    color = random_saturated_hex()
    for node in cyc:
        print(net.node_map[node])
        net.node_map[node]['color'] = color


OUTPUT_NAME = 'graph.html'

html = net.generate_html(notebook=False)
Path(OUTPUT_NAME).write_text(html, encoding="utf-8")
if args.browser:
    import webbrowser
    webbrowser.open(Path(OUTPUT_NAME).resolve().as_uri())

# Doesn't work with cdn_resources='in_line' because it does not open the file utf-8 encoding
# net.write_html(OUTPUT_NAME, notebook=False, open_browser=args.browser)
