C/C++ Include Grapher

Makes a graph from the #include directives

<pre>
positional arguments:
  paths                 Paths of the folders you want to recursively search in

Options:
  -h   --help           show this help message and exit
  -ho  --header_only    Graph only header files
  -all --all_includes   Also graph files not found in given paths
  -b   --browser        Open in browser when program close
  -v   --verbose        Verbose output
</pre>

## How to compile (Pyinstaller)

`pyinstaller .\main.py --onefile -n cppgrapher`
