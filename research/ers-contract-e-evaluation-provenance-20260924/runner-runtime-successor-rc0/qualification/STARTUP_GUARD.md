# Harmless runner startup guard

The final runner check uses only the frozen successor runner with --help. It supplies none of the matrix execution arguments and exits in argparse before any runner function starts.

The process runs under an external macOS Seatbelt profile with deny-default policy. The profile allows reads, allows writes only inside a dedicated guard-log directory, and allows process execution only of the exact resolved CPython 3.11.15 binary used by the venv. The environment sets __PYVENV_LAUNCHER__ to the venv's Python entrypoint; CPython then reports the venv and loads its site packages while the profile permits only the resolved base executable. All network access, other process execution, and other writes remain denied. The applied profile text and SHA-256 are recorded in the final qualification trace.

Python loads sitecustomize.py from this qualification directory before importing the runner. Its audit hook records and blocks process launches, network calls, filesystem mutation, dynamic source loading, and imports of scientific execution modules. This records attempted child creation before the process can start. Bytecode writing and user site packages are disabled.

Only the runner's harmless module-load imports of jsonschema, rfc8785, and cryptography are allowed. The guard records both import requests and loaded submodules. The separate dependency smoke records its own explicitly authorized imports. No private signing key is read or used.

Expected counts during --help are zero for process attempts, network attempts, filesystem mutation attempts, dynamic source loads, forbidden scientific imports, Contract E evaluations, supervisor launches, PIPE cases, scientific mutations, and sandbox creation.
