# Pre-freeze startup-guard preparation attempts

These probes were performed after preregistration and before the frozen successor qualification. They did not execute the candidate runner, ERS code, Contract E, a supervisor, a PIPE case, scientific mutation logic, or a sandbox.

## Seatbelt process-exec profile probes

A basic sandbox-exec profile around /bin/echo with allow-default and deny-network loaded successfully and printed seatbelt-guard-ok.

Attempts to use deny-default with a literal process-exec exception for the construction virtual environment's symlinked Python executable failed before Python startup. Exact error:

    sandbox-exec: execvp() of '/private/tmp/cal-ers05-runner-runtime-successor-20260924/runtime-build/construction-venv/bin/python' failed: Operation not permitted

The same failed with literal exceptions using the real interpreter path and the /tmp-normalized venv path, and with a subpath exception for the venv bin directory. Allowing the exact base interpreter path worked, but that would not execute through the virtual-environment entrypoint. This process-exec profile was rejected.

Copying the interpreter binary into a temporary directory and allowing that path started the binary but could not locate its compiled-in standard library prefix. Exact error included:

    Could not find platform independent libraries <prefix>
    Could not find platform dependent libraries <exec_prefix>
    Fatal Python error: init_fs_encoding
    ModuleNotFoundError: No module named 'encodings'

The copied interpreter was only a temporary probe and is not part of the runtime pack.

## Initial audit-hook filename error

The first Python guard probe used the filename startup_guard_sitecustomize.py. Python only auto-loads a module named sitecustomize.py, so the guard did not load. The harmless probe then ran /bin/echo with argument must-not-run, and its assertion failed because that process completed. Exact observed output:

    must-not-run
    AssertionError: {'network': True, 'filesystem': True}

No scientific or project process ran. The guard log was absent because the hook had not loaded. The filename was corrected to qualification/sitecustomize.py before any frozen qualification.

## Corrected guard self-test

The corrected guard loaded under a macOS sandbox profile that denies network access and file writes outside its dedicated log directory. A self-test deliberately attempted subprocess execution, a localhost socket connection, and a write outside the log directory. The audit hook raised PermissionError before any subprocess, network connection, or file write occurred. Output:

    guard_selftest=PASS ['filesystem', 'network', 'process']

The emitted trace recorded process_attempts=[subprocess.Popen], network_attempts=[socket.getaddrinfo], and filesystem_mutation_attempts=[open:<forbidden path>]. The forbidden file does not exist. These were guard self-tests before freeze; they are not counts from the final frozen qualification. In the final runner --help invocation, all such attempt counters must be zero.

## Exact interpreter whitelist with venv identity

The deny-default process-exec profile can launch the real CPython binary when the literal rule matches its resolved path. A final probe ran that exact CPython binary with __PYVENV_LAUNCHER__ set to the construction venv's Python path. CPython reported sys.prefix as the construction venv and sys.executable as its venv Python entrypoint. Under this profile, the corrected guard self-test printed:

    guard_selftest=PASS ['filesystem', 'network', 'process']

The audit trace recorded the three attempted operations and no child process, socket connection, or forbidden write occurred. The final runner invocation will use the same mechanism with the newly frozen venv, a fresh guard log, and an exact path-specific profile.

The final pre-freeze guard source used in the successful probe has Git blob candidate identity 2d83a971affb62129b535a0537702e10e815d0cb. The final frozen qualification binds the current startup-guard source blob separately and runs a zero-attempt --help trace; this probe's deliberate attempts remain only a guard self-test.
