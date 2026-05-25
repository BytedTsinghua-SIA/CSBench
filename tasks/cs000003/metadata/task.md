## Background (Excerpts from the Bomb Lab Handout)

This assignment involves **defusing a binary bomb** composed of several phases, each of which requires analyzing and understanding assembly code. Through this lab, you will gain practical experience in **reverse engineering**, **debugging**, and **understanding program control flow** at the machine-code level.

Outcomes you will gain from this lab include:

* You will learn how to carefully read and interpret **x86-64 assembly code**.
* You will understand how data is stored and manipulated at the **stack and memory** level.
* You will gain hands-on experience using **GDB (GNU Debugger)** to trace and control program execution.
* You will strengthen your understanding of **conditional branching**, **function calls**, and **parameter passing** mechanisms.
* You will develop systematic methods for analyzing **control-flow logic** and preventing program crashes.

Your binary bomb will be provided as an executable named **`bomb`** (or **`bomb[ID]`**), which you will analyze and defuse by entering the correct input strings for each phase.

---

## The Nature of the Bomb

Your bomb consists of **six phases**, each one being a small puzzle that expects a specific input line.
If you provide incorrect input to any phase, the bomb will **“explode”**, ending the program with an error message.

Each phase tests a different aspect of your understanding of assembly and logic:

| Phase | Topic                 | Common Skills Required                          |
| ----- | --------------------- | ----------------------------------------------- |
| 1     | String matching       | Using GDB to inspect constants and memory       |
| 2     | Simple arithmetic     | Observing registers and stack variables         |
| 3     | Switch/case logic     | Understanding jump tables and indirect branches |
| 4     | Recursion             | Analyzing recursive calls and base cases        |
| 5     | Bitwise manipulation  | Understanding masks and shifts                  |
| 6     | Linked list / sorting | Recognizing structures and pointer operations   |

Example of execution:

```bash
unix> ./bomb
Welcome to the Binary Bomb Lab.
Phase 1: Input string? hello world
BOOM!!! The bomb has blown up.
```

Your goal is to discover and provide the correct input for each phase so that the program prints:

```
Phase 1 defused.
That's number 2.
...
Congratulations! You've defused the bomb!
```

---

## Tools and Workflow

You will mainly use **GDB** to analyze the binary.

### Useful Commands

| Command          | Description                                             |
| ---------------- | ------------------------------------------------------- |
| `disas`          | Disassemble a function                                  |
| `break main`     | Set a breakpoint at the start of `main()`               |
| `run`            | Start the program                                       |
| `stepi`          | Execute one assembly instruction at a time              |
| `x/s $rdi`       | Display string at the address stored in register `$rdi` |
| `info registers` | View current register values                            |
| `x/20x $rsp`     | View 20 words from the stack                            |

For example, you might start like this:

```bash
unix> gdb bomb
(gdb) break main
(gdb) run
(gdb) disas phase_1
(gdb) x/s 0x401080
```

You can also use `objdump -d bomb > bomb.S` to generate a full disassembly file.

---

## Strategy and Advice

* **Work incrementally:** defuse one phase before moving to the next.
* **Use breakpoints** at the beginning of each `phase_X` function.
* **Watch input comparisons** (usually `strcmp`, `cmp`, or `test` instructions).
* **Trace control flow** to understand decision logic.
* **Understand the call graph:** `main → phase_1 → phase_2 → …`
* **Write down your correct inputs** in a file (e.g., `ans.txt`).

Example structure of `ans.txt`:

```
Border relations with Canada have never been better.
1 2 4 8 16 32
0 q 777
...
```

---

## Final Submission (Offline Mode)

When submitting locally (offline), please follow these steps:

1. Run your bomb with the `-q` flag to disable server reporting:

   ```bash
   ./bomb -q < ans.txt
   ```
2. Ensure all phases print:

   ```
   Phase X defused.
   ```
3. Compress your working directory (excluding large binaries):

   ```bash
   tar -czvf bomblab.tar.gz bomb ans.txt README.md
   ```

---

## Notes

* Each bomb binary is **unique** to your account.
* Avoid copying answers from others; your bomb may have different constants or logic.
* If your bomb “explodes,” review the last few assembly instructions to understand why.
* The lab emphasizes **learning to think like the machine** — tracing data flow and control flow logically.

