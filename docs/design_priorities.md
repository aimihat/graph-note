Current:
- Update cell connections, in UI & proto.

Bugs:
- Selected cell gets unselected.

Backlog:
- Fix logging across components
- Implement outputs (c.f. RFC)
- Editing root node: imports & globals.
- Cell execution status -> running, finished, etc.
- Cell dependency status via colours.
- Improve UI
    - For code editing -> re-use jupyter code.
    - Code editing as a window that can be positioned/sized?
    - Edit cell name directly on the cell: when selected, turns into an input.
    - Loading indicator on the cell itself.
- Shortcuts to run / save / etc. Command palette?
- Improve packaging (e.g. run command, download / upload notebook).
- Detect inputs implicitly, as they are undefined variables.

Ideas for future:
- Open websocket connection for continual updates from the kernel.

Completed:
