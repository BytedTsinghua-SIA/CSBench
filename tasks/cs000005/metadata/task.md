## Background (high-level)

In this lab you will design and optimize a pipelined Y86-64 processor and a Y86-64 benchmark to maximize performance.
You are free to make semantics-preserving modifications to the benchmark, enhancements to the pipeline implementation, or both. Completing this lab will deepen your understanding of:

* how instruction-level code transformations interact with microarchitectural features (pipeline, hazards, forwarding, etc.),
* what design choices affect cycles per element (CPE) for a loop-heavy routine,
* using the Y86-64 toolchain (assembler, ISA simulator, pipeline simulator) to test, measure and iterate. 

The lab is divided into **three parts** (A, B, C). Parts A and B prepare you for the optimization work in Part C.

---

## Logistics

* Work individually.
* Any clarifications or updates will be posted on the course web page.
* You will receive a tarball (`archlab-handout.tar`) containing the handout and simulator files. Extract and build as described below. 

Basic setup (example):

```bash
# unpack top-level handout tar
tar xvf archlab-handout.tar

# inside created directory:
tar xvf sim.tar
cd sim
make clean; make
```

All work is done inside the `sim` directory created by unpacking `sim.tar`. 

---

## Part A — Y86-64 programming (directory `sim/misc`)

**Goal:** write simple Y86-64 programs to become familiar with the tools (YAS assembler and YIS ISA simulator).

You must implement three functions/programs (see `sim/misc/examples.c` for C reference versions):

1. **`sum.ys`** — iterative sum over a linked list (function equivalent to `sum_list`).
2. **`rsum.ys`** — recursive sum over a linked list (function equivalent to `rsum_list`).
3. **`copy.ys`** — copy a block of words from `src` to `dest` and return XOR checksum (function equivalent to `copy_block`).

Requirements & hints:

* Follow x86-64 calling conventions in your Y86-64 code (argument registers, callee-saved registers, stack management).
* Test by assembling with `YAS` and running with `YIS`. Example test data (three-element lists/blocks) are provided in the handout. 

**Grading (Part A):** 10 points per program for correctness and proper register/stack handling. 

---

## Part B — Extend the SEQ simulator (directory `sim/seq`)

**Goal:** extend the SEQ (sequential) pipeline control logic to implement a new instruction `iaddq`.

Tasks:

* Modify `seq-full.hcl` to implement the `iaddq` instruction semantics (see CS:APP guidance for `irmovq` and `OPq` for reference).
* Include a header comment with your name/ID and a short description of the `iaddq` computations.
* Build and test a new simulator binary:

```bash
# build full SEQ simulator implementing your HCL
make VERSION=full
# run a small Y86 program in TTY mode
./ssim -t ../y86-code/asumi.yo
# or GUI mode for stepping/debugging
./ssim -g ../y86-code/asumi.yo
```

Regression & testing:

* Use provided `make testssim` in `../y86-code` to check benchmark correctness.
* Use the `ptest` suite to test `iaddq` behavior (with `TFLAGS=-i`). 

**Grading (Part B):**

* 10 pts — description of `iaddq` computations.
* 10 pts — passing benchmark regression tests in `y86-code`.
* 15 pts — passing `ptest` for `iaddq`. 

---

## Part C — Pipeline optimization (directory `sim/pipe`)

**Overview:** This is the core of the lab. You will optimize the `ncopy` function and possibly the pipeline `pipe-full.hcl` to minimize cycles-per-element (CPE) when copying and counting positive words.

Provided baseline:

* A C reference implementation is in the handout (`ncopy`), and a baseline Y86-64 `ncopy.ys` is provided. `pipe-full.hcl` contains PIPE HCL and a constant `IIADDQ`. 

Your deliverables for Part C:

* `ncopy.ys` — your optimized Y86-64 implementation of `ncopy`.
* `pipe-full.hcl` — your modified PIPE HCL (if you change the pipeline).

Both files must begin with a header comment containing your name/ID and a high-level description of modifications and rationale.

**Constraints & rules:**

* `ncopy.ys` must be correct for arbitrary array sizes (not hardwired to a single size).
* Assembled `ncopy` must be ≤ **1000 bytes**. Use `./check-len.pl < ncopy.yo` to validate.
* `pipe-full.hcl` must pass the regression tests in `../y86-code` and `../ptest` (unless you intentionally implement features excluded from grading). 

**Testing & drivers:**

* Build driver programs with:

```bash
make drivers
# produces sdriver.yo (small) and ldriver.yo (large)
```

* Run in GUI or TTY:

```bash
# GUI
./psim -g sdriver.yo
# or run the pipeline simulator in non-GUI
./psim sdriver.yo
```

* Use `correctness.pl` to test ncopy across many lengths and `benchmark.pl` to compute average CPE across lengths 1..64 (the average CPE is the metric for grading). 

**Performance & grading (Part C):**

* Lab measures average **CPE** across block lengths 1–64 (run `./benchmark.pl`).
* Baseline average CPE ≈ **15.18** (baseline example). The graders expect you to reach an average CPE **< 9.00** if possible; excellent solutions reach ~7.48. 

Scoring (performance portion):

```
If average CPE c:
  c > 10.5  ->  0 points (performance)
  7.50 ≤ c ≤ 10.50 -> score = 20 * (10.5 - c)
  c < 7.50 -> 60 points
```

Other Part C points:

* 20 pts for quality of header descriptions in `ncopy.ys` and `pipe-full.hcl` and implementation quality.
* 60 pts based on performance as above (total 100 pts for Part C). 

---

## Building & Regression Testing (summary)

Useful build & test commands:

```bash
# Build the tools in sim
cd sim
make

# Build full ssim/psim after HCL edits
make VERSION=full      # builds ssim/psim for seq/pipe respectively with VERSION=full
make psim VERSION=full # rebuild psim for pipe-full.hcl changes

# Generate drivers and test
make drivers
./psim -g sdriver.yo
../misc/yis sdriver.yo    # test with ISA simulator

# Run exhaustive correctness and performance scripts
./correctness.pl          # default uses YIS
./correctness.pl -p       # test on pipeline simulator
./benchmark.pl            # compute average CPE for ncopy.ys
```

Return codes from correctness script indicate status:

* `0xaaaa`: all tests pass
* `0xbbbb`: incorrect count
* `0xcccc`: function too long (>1000 bytes)
* `0xdddd`: source data not copied
* `0xeeee`: memory corruption around destination
  (See handout for details.) 

---

## Handin Instructions

You will submit three parts separately. Include your name and ID as comments at the top of each submitted file.

* **Part A:** `sum.ys`, `rsum.ys`, `copy.ys`
* **Part B:** `seq-full.hcl`
* **Part C:** `ncopy.ys`, `pipe-full.hcl`

Example handin command (site-specific — adjust to your course infrastructure):

```bash
# from archlab-handout directory
make handin-parta TEAM=teamname
make handin-partb TEAM=teamname
make handin-partc TEAM=teamname
# to resubmit revised versions:
make handin-partX TEAM=teamname VERSION=2
```

Verify handin by checking the course handin area as described on your site. 

---

## Hints & Recommendations

* Use GUI mode to debug small drivers (`sdriver.yo`, `ldriver.yo`).
* Initialize `DISPLAY` if running GUI on a remote server.
* Debug pipeline behavior by stepping in GUI mode; observe program code and memory windows.
* When optimizing `ncopy`, consider typical compiler/microarchitecture optimizations: loop unrolling, instruction scheduling to avoid hazards, using register temporaries, reducing branch mispredictions, and minimizing pipeline stalls. But keep correctness and generality.
* Make one change at a time, re-run `correctness.pl` and `benchmark.pl` after each change to measure impact. 

---

## Deliverables checklist

* [ ] `sum.ys`, `rsum.ys`, `copy.ys` (Part A)
* [ ] `seq-full.hcl` (Part B)
* [ ] `ncopy.ys`, `pipe-full.hcl` (Part C)
* [ ] Short report/header comments describing what you changed and why (especially for Part C)
* [ ] Evidence of testing: `benchmark.pl` output and `correctness.pl` results
