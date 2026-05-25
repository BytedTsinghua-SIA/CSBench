# CS000343: ABC Player

## Background
ABC is a text-based music notation that lets you write melodies in plain text and share them easily. In this project, you will build a player that parses abc files and schedules notes for playback using the Java MIDI API.

## Core Tasks
- Define an immutable music abstract data type (ADT) and document its abstraction function, representation invariant, and safety from rep exposure.
- Use ANTLR grammar stubs (Abc.g4, Xyz.g4, Configuration.g4) to parse a specified subset of abc notation, then translate the parse tree into your music ADT.
- Implement the player pipeline that reads an input file, interprets headers (meter, default note length, tempo, key), and plays the resulting music via SequencePlayer; provide a working entry point in `abc/player/Main.java`.
- Write unit tests that partition input cases and validate core components independently.

## Scoring
- Correct parsing and interpretation of headers and note syntax for the required abc subset.
- Accurate timing and pitch scheduling in the playback sequence for valid inputs.
- Clear, well-partitioned unit tests and documented invariants for your data types.
