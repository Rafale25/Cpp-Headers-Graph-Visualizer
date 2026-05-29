import sys
from pathlib import Path
from pyvis.network import Network
import re
import argparse

parser = argparse.ArgumentParser(
            prog='C/C++ Header Graphing',
            description='Makes a graph from the #include directives',
            epilog='')

parser.add_argument('-ho', '--header_only', action='store_true', help='Graph only header files')
parser.add_argument('-all', '--all_includes', action='store_true', help='Also graph files not found in given paths')
parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
parser.add_argument('folderpath', nargs='+', help='Path of the top folder you want to recursively search in')

args = parser.parse_args()

FILES_MATCH = ('.hpp', '.h')
if not args.header_only:
    FILES_MATCH += ('.c', '.cpp')

if (args.verbose):
    print(f'Header only: {args.header_only}')
    print(f'paths: {args.folderpath}')
    print(f'{FILES_MATCH=}')

src_path = [Path(p) for p in args.folderpath]

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

    if f.suffix in FILES_MATCH:
        nodes.add(f.name)

if args.verbose:
    print(f'Files found: {nodes}')

net.add_nodes(nodes)

for f in iter_src_pathes():
    if not f.is_file(): continue
    if f.suffix not in FILES_MATCH: continue

    text = f.read_text()
    # includes = re.findall(r'#include\s+"(\w+.(?:hpp|h))"', text)
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


net.show("graph.html")
