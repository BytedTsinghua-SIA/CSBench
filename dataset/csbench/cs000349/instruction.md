# Lab 2: Bad Randomness

## Background
Bad randomness can break cryptographic systems. In this lab you will analyze ECDSA key generation and signature nonces, and exploit weaknesses in WEP's stream-cipher integrity design.

## Tasks
1. Implement ECDSA key recovery in `ecdsa/sol.py` (`problem_1a` and `problem_2b`).
2. Implement WEP forgery attacks in `wep/attacker.py` (`attack_one`, `attack_two`; `attack_three` optional).

## Scoring
- Correctly recover ECDSA secret keys for both problems.
- Produce valid forged WEP packets for `attack_one` and `attack_two`.
- Optional: recover the full plaintext in `attack_three`.
