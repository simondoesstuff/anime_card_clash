## Setup
Run (and install) with uv,
  - `uv run src`
  
## Usage
There is a simple built-in interactive CLI with a few utilities.
To start the macro after running the CLI, use the `all` command.  
Note: `echo "all" | uv run src`.
  
## Limitations
Currently assumes:
  - The camera is perfectly straight. You can get it perfect by joining the game fresh or standing in spawn and using the floor patterns to align with the monitor's edge.
  - You are not currently doing potion tower while boss hour (although it will correct itself eventually).
  - You are not sprinting by default.
  
It will not proc potions. It does not read the moons. It does not assign exploration or upgrades.