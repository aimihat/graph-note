Current:
- Cell dependency status via colours. + whether code / inputs was edited since last run?
    - cell last execute time
- BUG: if execute quickly twice -> ports are removed -> connections are removed.
- BUG: re-ordering of handles
- BUG: a port can receive only one input
- BUG: create new cell - click it, it only selects it the second time.

Backlog:
- Fix logging across components
- Editing rogiot node: imports & globals.
- Cell execution status -> running, finished, etc.

- Improve UI
    - errors colour the port directly..q
    - For code editing -> re-use jupyter code.
    - Code editing as a window that can be positioned/sized?
    - Edit cell name directly on the cell: when selected, turns into an input.
    - Loading indicator on the cell itself.
- Shortcuts to run / save / etc. Command palette?
- Improve packaging (e.g. run command, download / upload notebook).
- Detect inputs implicitly, as they are undefined variables.
- Think about jumping to the next cell when executing?

Ideas for future:
- Open websocket connection for continual updates from the kernel.
- Both  kernel outputs and compiled functions should use UIDs as a single source of truth. Port names should only be used for display.

Completed:
- Implement outputs (c.f. RFC)
