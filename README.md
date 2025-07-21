## Setup
Run (and install) with uv,
  - `uv run src`
  
See [Limitations](#Limitations)
  
## Usage
There is a simple built-in interactive CLI with a few utilities.
To start the macro after running the CLI, use the `all` command.  
Note: `echo "all" | uv run src`.
  
## Limitations
Currently assumes:
  - **You are using follow camera.**
  - You are using the default pitch. Do not touch it after join.
  - It will only adjust the scroll once; do not touch it often.
  - You may change yaw; it resets it often.
  - You are not currently doing potion tower while boss hour (although it will correct itself eventually).
  - You are not sprinting by default.
  
It will not proc potions. It does not read the moons. It does not assign exploration or upgrades.