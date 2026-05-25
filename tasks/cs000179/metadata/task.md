# Project 2 – BYOG Engine

## Overview
Create a fully playable "Build Your Own Game" (BYOG) world generator. The reference solution inside `` provides a complete implementation; your job is to reproduce its behaviour using the same file layout and public APIs so that automated tests can drive the game via strings or keyboard input.

All Java sources live under `byog/` and must preserve their package declarations. Key classes include:

* `byog.Core.Game` – entry point that parses input, drives the simulation, and exposes `playWithKeyboard()` / `playWithInputString(String input)`.
* `byog.Core.World`, `RoomGenerator`, `Room`, `Outdoor`, and `Player` – build and manage the world grid, procedurally generate rooms and hallways, track the exit, and move the player.
* `byog.Core.Toward` – enum describing legal movement directions.
* `byog.TileEngine` – Princeton tile rendering engine (`TETile`, `Tileset`, `TERenderer`).
* Support code in `byog.lab5`, `byog.lab6`, and `byog.SaveDemo` must continue to compile but is not invoked by the harness.

## Functional Requirements
* **Seeded world generation** – `Game.playWithInputString` and `Game.playWithKeyboard` must accept a new game command (`n`/`N`), parse an arbitrary-length numeric seed, build a `World` with deterministic layout, and optionally process movement commands. Multiple runs with identical seed+commands should produce identical tile arrays.
* **Input parsing** – `Game` should accept lower/upper case commands. Use `:Q` to trigger `quitAndSaving()`, which writes a serialised `World` to `savefile.txt` and terminates the current session without crashing.
* **Loading** – When the input starts with `l`/`L`, or the keyboard menu selects Load, deserialize the saved world, reinitialise transient tile state via `World.resetLoad()`, and resume command processing.
* **Movement** – Implement `World.move(Toward direction)` and `Player.move(...)` so that the avatar walks only on floor tiles, does not leave the generated map, and updates the tile grid (erasing the previous location, redrawing the player, and preserving the exit tile).
* **Rendering contract** – When driving via `playWithInputString`, do not open a window or draw frames. Instead, return the `TETile[][]` representing the final world so the harness can inspect it. Keyboard play should still render via `StdDraw` and `TERenderer`.

The provided world generator uses randomised room placement, hallways, and a single exit tile (`Tileset.UNLOCKED_DOOR`). Preserve the high-level flow: initialise the tile array to `Tileset.NOTHING`, call `RoomGenerator.generateRooms`, place a `Player` randomly on a floor tile, and drop the exit in a valid corridor.

## Testing Expectations
Our automated suite compiles the entire BYOG project (Core, TileEngine, lab helpers) against the Princeton libraries in `library-sp18/javalib`. Python tests then invoke custom Java harnesses to verify the behaviours above:

1. **Deterministic world generation** – two `Game` instances fed the same `N...S` command sequence must yield identical tile layouts.
2. **Save/Load fidelity** – running `Game.playWithInputString("n<seed>...:Q")` must persist the game state so that a fresh instance loaded with `"l"` reproduces the saved world exactly.

Both harnesses use reflection to access the internal `World` object and serialise tile grids into strings for comparison. They also clean up `savefile.txt` after validating save/load. Tests execute from `` so all relative paths (e.g., for assets) must remain valid.
