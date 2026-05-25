## Task Instructions

https://inst.eecs.berkeley.edu/~cs188/sp21/projects/logic/logic/

### Task Source

UC Berkeley CS188: Introduction to AI - Project 3: Logic & Pacman

### Task Overview

This project involves implementing logic-based AI agents for Pacman using propositional logic. The student must implement functions to construct logical expressions, convert them to CNF (Conjunctive Normal Form), and use SAT solvers to plan Pacman's actions. The project covers basic logic operations, successor state axioms, and more advanced problems like localization, mapping, and SLAM (Simultaneous Localization and Mapping).

### Detailed Requirements

1. **Question 1: Logic Expressions**: Implement basic logic functions including:
   - `sentence1()`, `sentence2()`, `sentence3()`: Create logical expressions from English descriptions
   - `entails()`: Check if one logical expression entails another
   - `plTrueInverse()`: Check the truth value of negated expressions
   - `findModelUnderstandingCheck()`: Understand how the SAT solver works

2. **Question 2: CNF Helper Functions**: Implement functions to create CNF expressions:
   - `atLeastOne(literals)`: Returns CNF for "at least one literal is true"
   - `atMostOne(literals)`: Returns CNF for "at most one literal is true"
   - `exactlyOne(literals)`: Returns CNF for "exactly one literal is true"

3. **Question 3: Successor Axioms**: Implement Pacman's successor state axioms:
   - `pacmanSuccessorAxiomSingle()`: Axiom for how Pacman can move to a position
   - `pacphysicsAxioms()`: General physics axioms for Pacman at a given timestep
   - `checkLocationSatisfiability()`: Check if a location is logically possible

4. **Question 4: Position Planning**: Implement logic-based pathfinding:
   - `positionLogicPlan()`: Find a sequence of actions to move Pacman from start to goal using only propositional logic

5. **Question 5: Food Planning**: Extend planning to food collection:
   - `foodLogicPlan()`: Find a plan to eat all food on the map using logic

6. **Question 6: Localization**: Implement probabilistic localization:
   - `localization()`: Track possible Pacman positions given sensor readings

7. **Question 7: Mapping**: Implement simultaneous localization and mapping:
   - `mapping()`: Build a map of the environment while tracking Pacman's position

8. **Question 8: SLAM**: Full SLAM implementation:
   - `slam()`: Simultaneous Localization and Mapping with unknown initial position and map

### Testing

All implementations are tested using the provided autograder which runs test cases for each question. The final implementation must:
- Pass the tests for logic expressions (q1)
- Pass the CNF helper tests (q2)
- Pass successor axiom tests (q3)
- Work correctly for planning problems (q4, q5)
- Handle localization and mapping tasks (q6, q7, q8)

### Key Constraints

- All logical expressions must be in valid CNF form for the SAT solver
- The planning functions must find valid action sequences
- Localization and mapping must correctly update beliefs based on sensor information
- The SLAM function must handle uncertainty in both position and map structure
