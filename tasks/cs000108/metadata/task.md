# CS50 AI Parser Refactoring Task

## Background
The parser project is part of CS50's Introduction to Artificial Intelligence with Python. The goal is to build a context-free grammar (CFG) based parser that can analyze English sentences drawn from the provided corpus. Parsing allows the program to infer sentence structure, making it possible to extract noun phrases that describe key entities in the text.

## Objective
Develop the missing portions of `parser.py` so that the program can parse every sentence included in the `sentences/` directory and correctly extract minimal noun phrase (NP) chunks. The solution must operate under Python 3.12 and use NLTK's tokenization utilities and tree APIs.

## Specification
- Complete `preprocess(sentence)`:
  - Tokenize `sentence` via `nltk.word_tokenize`.
  - Lowercase all tokens.
  - Exclude tokens that do not contain at least one alphabetic character.
- Redefine the `NONTERMINALS` grammar:
  - Provide sufficient CFG rules to parse every sentence in `sentences/`.
  - You may invent new nonterminal symbols, but the start symbol must remain `S`.
  - Use the `NP` symbol for noun phrases.
- Implement `np_chunk(tree)`:
  - Return a list of `nltk.tree.Tree` objects, each representing a noun phrase chunk.
  - A chunk is an `NP` subtree that does not contain another `NP` subtree.
- Retain the given `TERMINALS` rules.
- Do not modify other parts of `parser.py`, aside from creating helper functions if needed.

## Implementation Notes
- Expect multiple parses for some sentences due to grammar ambiguity.
- Avoid over-generating invalid sentences while ensuring all provided sentences parse successfully.
- Use NLTK's `Tree` utilities (`label`, `subtrees`, etc.) to inspect and manipulate parse trees.
- You may iterate incrementally: first design a grammar that parses the sentences, then refine `np_chunk`.

## Provided Assets
- `parser.py`: Starter implementation with placeholders for `preprocess`, `NONTERMINALS`, and `np_chunk`.
- `sentences/*.txt`: Input sentences used for both development and testing.
