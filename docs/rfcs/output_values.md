An output port can have an associated runtime value, stored in OUT_PORT_VALUES.
Each kernel session starts with ports initially empty.
When a cell runs, we update all the output ports to the timestamp
This timestamp informs both the last update time of the port, but also whether the port has a runtime value

- When validating a cell can be run: check run time value exists.
- (ok): When starting a new session -> reset all ports to have empty timestamp.
- When a cell executes -> capture what outputs were written to OUT_PORT_VALUES, as the new ports + capture the runtime value timestamp
