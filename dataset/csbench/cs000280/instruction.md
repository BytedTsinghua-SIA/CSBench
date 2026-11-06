# Programming Assignment IV: Code Generator for Cool

## Background

This assignment focuses on implementing a code generator for the Cool programming language. The code generator is the final phase of the Cool compiler, building upon the Abstract Syntax Tree (AST) constructed in PA2 and the semantic analysis performed in PA3. When successfully completed, you will have a fully functional Cool compiler that can translate Cool programs into executable MIPS assembly code.

The code generator must produce MIPS assembly code that faithfully implements any correct Cool program. All erroneous Cool programs have already been detected by the front-end phases (scanner, parser, and semantic analyzer), so there is no error recovery needed in code generation.

## Core Tasks

### 1. Code Generation Infrastructure

Your code generator needs to perform the following high-level tasks:

1. **Global Constants**: Determine and emit code for global constants, such as prototype objects for each class.

2. **Global Tables**: Determine and emit code for global tables, including:
   - `class_nameTab`: Table of class name strings
   - `class_objTab`: Table of class prototype objects
   - Dispatch tables: Virtual method dispatch tables for each class

3. **Class Initialization**: Determine and emit code for the initialization method of each class.

4. **Method Definitions**: Determine and emit code for each method definition in the program.

### 2. Design Strategy

A reasonable approach is to perform code generation in two passes:

- **First Pass**: Decide the object layout for each class, particularly the offset at which each attribute is stored in an object.
- **Second Pass**: Recursively walk each feature and generate stack machine code for each expression using the layout information from the first pass.

### 3. Runtime Error Checking

Your generated code must catch and handle the following runtime errors, printing suitable error messages before aborting:

1. **Dispatch on void**: When attempting to call a method on a void object
2. **Case on void**: When attempting to perform case dispatch on a void object
3. **Missing branch**: When a case expression has no matching branch

You may allow SPIM to catch division by zero. The runtime system handles substring out of range and heap overflow errors.

### 4. Garbage Collection Support

To receive full credit, your code generator must work correctly with the generational garbage collector in the Cool runtime system. The garbage collector can be enabled with the `-g` flag. When enabled, the collector:
- Reclaims memory
- Verifies that "-1" separates all objects in the heap
- Can be tested with `-t` flag (performs collections on every allocation)

### 5. Key Implementation Considerations

- **Runtime System Interface**: Your code must work correctly with the Cool runtime system, following the calling conventions and requirements specified in the Cool Runtime manual.
- **Operational Semantics**: Understand the expected behavior of Cool constructs as defined in Section 13 of the Cool Reference Manual.
- **MIPS Instruction Set**: Familiarize yourself with MIPS operations and the format required by SPIM.
- **Register Management**: Decide on register usage conventions and invariants (which registers are saved, which might be overwritten, etc.).

## Requirements

- Your code generator should be implemented primarily in `cgen.cc`, with supporting code in `cgen.h`, `emit.h`, and `cgen_supp.cc`.
- The entry point is the `program_class::cgen(ostream&)` method, called on the root of the AST.
- You may modify `cool-tree.h` to add fields or method declarations to AST node classes.


