# Problem Set 2: Introduction to Algorithms (6.006)

## Course Information
- **Course**: 6.006 Introduction to Algorithms
- **Institution**: Massachusetts Institute of Technology
- **Instructors**: Professors Erik Demaine and Srini Devadas
- **Due Date**: Tuesday, September 27 at 11:59PM

## Background

This problem set explores algorithmic analysis and optimization through two practical applications:
1. Fractal rendering algorithms and their computational complexity
2. Digital circuit simulation performance optimization

## Problem 2-1: Fractal Rendering [40 points]

### Background
You are consulting for Gopple, which is developing new mobile phones with Retina HD displays (infinite resolution). The executives want the Koch snowflake fractal as the phone's background. However, since processing power is finite, the fractal must be rendered at a fixed depth (Level of Detail, LoD) \(n\).

The Koch snowflake is generated recursively:
- At LoD 0, it's just an equilateral triangle
- At higher LoDs, each edge is subdivided and replaced with a smaller triangle pattern

### Core Tasks

#### Part 1: 3D Hardware-Accelerated Rendering
Analyze the computational requirements when rendering triangles:
- (a) Determine the height of the recursion tree
- (b) Calculate the number of nodes at each level \(i\)
- (c) Find the asymptotic rendering time (triangle count) for a node at level \(i\)
- (d) Find the asymptotic rendering time at each level \(i\)
- (e) Determine the total asymptotic cost for the CPU

#### Part 2: 2D Hardware-Accelerated Rendering
Analyze the computational requirements when rendering line segments (paths):
- Determine recursion tree height
- Calculate nodes at each level
- Analyze rendering time per node at different levels
- Analyze rendering time at the last level
- Calculate total asymptotic cost

#### Part 3: 2D Software Rendering
Analyze the computational requirements when the CPU rasterizes line segments:
- Consider line segment count and total length
- Calculate asymptotic costs at different levels
- Determine total asymptotic cost

#### Part 4: 3D Software Rendering
Analyze the computational requirements when the CPU rasterizes triangles:
- Consider triangle area (proportional to side length squared)
- Calculate total asymptotic cost
- Provide a proof using the recursion-tree method

## Problem 2-2: Digital Circuit Simulation [60 points]

### Background
You are interning at AMDtel, a chip manufacturer. The hardware verification team's circuit simulator is too slow, and you need to optimize it.

A combinational circuit consists of:
- **Gates**: Devices that take Boolean inputs and produce outputs based on Boolean functions
- **Delays**: Each gate has a delay \(\delta\); output at time \(\tau\) reflects inputs at time \(\tau - \delta\)
- **Wires**: Connect gate outputs to other gate inputs, propagating signals instantly

The simulator takes a circuit layout file describing:
- Gates and their delays
- Probes (gates to monitor)
- External inputs

It simulates transitions at all gate outputs over time and outputs transitions at probed gates in chronological order.

### Core Tasks

1. **Profiling [8 points]**
   - Run the code under Python profiler with: `python -m cProfile -s time circuit.py < tests/5devadas13.in`
   - Identify the method with the highest CPU usage
   - Note: This may take 15-30 minutes and use 100% CPU on one core

2. **Analysis [6 points]**
   - Count how many times the problematic method is called

3. **Complexity Analysis [8 points]**
   - Identify the data structure class containing the bottleneck
   - Determine the tightest asymptotic bound for the worst-case running time of the problematic method
   - Express in terms of \(n\), the number of elements

4. **Optimal Complexity [8 points]**
   - Determine what the tightest asymptotic bound would be if the data structure were implemented using the most efficient method learned in class

5. **Implementation [30 points]**
   - Rewrite the data structure class using the most efficient implementation
   - **Constraint**: Cannot import any additional Python libraries
   - The test suite will verify this constraint

## Deliverables

1. **Problem 2-1**: Answers to all multiple-choice questions and a proof for the 3D software rendering case
2. **Problem 2-2**: Optimized `circuit.py` that passes all tests and runs efficiently (tests should complete in less than 30 seconds)


