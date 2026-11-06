# Lab 1: Merkle Tree Attacks

## Background
This lab explores weaknesses in an authenticated key-value store that uses a Merkle-tree style hash structure. The client validates proofs from the store, but a malicious store can sometimes craft responses that appear valid.

## Tasks
1. Implement AttackOne in `attack.py` to forge a fake key-value pair after the client inserts a single legitimate pair.
2. Implement AttackTwo in `attack.py` to make many fake keys appear present after the client inserts an attacker-chosen key-value pair.
3. Implement AttackThree in `attack.py` to return forged lookup proofs with exactly one sibling so existing keys appear missing.
4. Optional extra credit: Implement AttackFour in `attack.py` to exploit insert-proof confusion and return a long fake key-value pair after many client inserts.

## Scoring
- AttackOne passes `scenario_one()` in `grader.py`.
- AttackTwo passes `scenario_two()` in `grader.py`.
- AttackThree passes `scenario_three()` in `grader.py`.
