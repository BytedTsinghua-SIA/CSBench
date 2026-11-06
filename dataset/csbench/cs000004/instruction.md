## Buffer Lab (bufbomb) — Offline Handout

This assignment asks you to craft five exploit payloads against the program `bufbomb`, each demonstrating a different buffer-overflow or control-flow hijacking technique. By completing it, you will:

- Learn how attackers exploit stack-based buffers and how modern defenses affect exploit design.
- Deepen your understanding of the x86-64 System V calling convention, the stack layout, and instruction encodings.
- Practice with GDB/objdump and with constructing raw byte payloads.
- Experience both code-injection (executable stack) and no-execute-stack constraints.

Important ethics note: The goal is to understand vulnerabilities so you can prevent them. Do not use these techniques outside the lab environment.

---

## Running bufbomb and tests

Run everything from the `src/` directory.

- Required flag: `-u <user>` — identify yourself; it determines your cookie value. For local testing you can use any string (e.g., `temp`) consistently.
- No-exec mode: `-n` — enables the “non-executable stack” variant used in Level 4.

Payloads are authored as ASCII hex bytes in `levelN.txt`, then piped through `hex2raw` into `bufbomb`:

```
cat level0.txt | ./hex2raw | ./bufbomb -u temp
```

For Level 4, both tools use `-n`:

```
cat level4.txt | ./hex2raw -n | ./bufbomb -n -u temp
```

Tips for `hex2raw`:

- Use two hex digits per byte, separated by spaces or newlines (e.g., `ef be ad de`).
- Little-endian: a 64-bit address 0x401234567890abcd must be written least-significant byte first.
- Avoid inserting unintended newline byte `0x0a` in the middle of your raw string unless you intend to terminate `Gets`/input early.
- You may add C-style block comments to annotate sections of your payload.

Run the provided tests from `src/`:

```
./test.sh
```

Each test reads `levelN.txt`, runs the appropriate command, and checks for success strings.

---

## The bufbomb interface (conceptual)

The vulnerable function resembles:

```c
unsigned getbuf(void) {
    char buf[BUFFER_SIZE];
    Gets(buf);     // unsafe input
    return 1;
}
```

The program prints validation messages like:

- Level 0: `You called smoke()`
- Level 1: `You called fizz(<cookie>)`
- Level 2: `You set global_value to 0x373e31da`
- Level 3: `getbuf returned 0x373e31da`
- Level 4: `getbufn returned 0x373e31da`

Your job is to overflow `buf` and take control of the return path and/or registers to trigger each success condition.

---

## Getting your cookie

Use `./makecookie -u <user>` to obtain your per-user cookie. Tests use the user string `temp`, so for consistency:

```
./makecookie -u temp
```

Record the printed hex value; you’ll need it for Level 1. The fixed constant used in Levels 2–4 is `0x373e31da` (already encoded in the tests).

---

## Payload workflow (recommended)

1) Disassemble functions: `objdump -d ./bufbomb | less`
2) Find key symbols and addresses: `nm -n ./bufbomb | grep -E 'smoke|fizz|getbuf|getbufn|global_value'`
3) Prototype the payload in `levelN.txt` using annotated hex and generous spacing/newlines.
4) Convert and run via `hex2raw` → `bufbomb`; iterate in GDB when needed.
5) Keep byte order and exact sizes in mind. Use breakpoints at `getbuf` return for control-flow checks.

GDB quickies:

- `break getbuf` / `finish` to stop at the return and inspect `%rip` target and `%rax`.
- `x/20gx $rsp-0x80` to inspect the stack around your payload.

---

## Levels and success criteria

Each level has a contract: goal, constraints, and what to submit (the payload file). All payloads are ASCII hex stored in `src/levelN.txt`.

### Level 0 — Call smoke()

Goal: When `getbuf` returns, control should transfer to function `smoke`, producing `You called smoke()` and a `VALID` line.

Constraints:

- Executable stack is allowed for Levels 0–3, but you don’t need code injection here.
- Overwrite the saved return address in `getbuf`’s frame with the address of `smoke`.

Hints:

- Determine the offset from the start of `buf` to the saved return address (buffer size + saved RBP if present).
- Use little-endian encoding of `&smoke` in your payload tail.

Deliverable: `level0.txt`.

### Level 1 — Call fizz(cookie)

Goal: Call `fizz` with your cookie as its first argument (x86-64: `%rdi`), yielding output containing `You called fizz` and `VALID`.

Constraints:

- You must set up the argument register before control reaches `fizz`.

Hints (two common approaches):

- Inject a small code stub on the stack that loads `%rdi` with the cookie and jumps to `fizz`.
- Or build a short ROP chain using `pop rdi; ret` gadget to load `%rdi` and then return to `fizz`.

Get your cookie with `./makecookie -u temp` (or your chosen `-u`).

Deliverable: `level1.txt`.

### Level 2 — Set global_value to 0x373e31da

Goal: Cause the message `You set global_value to 0x373e31da`.

Constraints:

- Either call a helper that writes to `global_value`, or inject/chain code that writes the constant into the global’s address.

Hints:

- Find the symbol address of `global_value` via `nm`.
- With code injection, use a `movl $0x373e31da, <addr>` sequence and then return to the program’s continuation point.
- With ROP, use a `pop rax`/`pop rdx` plus `mov [rdx], eax` style gadget sequence if available, or call an existing setter if present.

Deliverable: `level2.txt`.

### Level 3 — Make getbuf return 0x373e31da

Goal: The function `getbuf` should return the value `0x373e31da`, so the program prints `getbuf returned 0x373e31da`.

Constraints:

- On x86-64, integer return values are passed in `%rax` at the `ret`.

Hints:

- Inject a stub that sets `%rax` to `0x373e31da` and then executes a `ret` to the caller of `getbuf`.
- Or assemble a ROP sequence ending with `ret` after loading `%rax`.
- Ensure the final `ret` target is the instruction after the original call to `getbuf` (i.e., back to the normal control flow so printing occurs).

Deliverable: `level3.txt`.

### Level 4 — No-exec stack: make getbufn return 0x373e31da

Goal: Under non-executable stack constraints, cause `getbufn` to “return” `0x373e31da` (printed as `getbufn returned 0x373e31da`). Run with `./hex2raw -n | ./bufbomb -n -u temp`.

Constraints:

- You cannot execute injected bytes on the stack; use ROP or ret2libc using gadgets within `bufbomb` or linked libraries allowed by the setup.

Hints:

- Search for gadgets: `objdump -d ./bufbomb | grep -n "pop rdi" -n` and similar. Common pattern: `pop rax; ret` to load `%rax`, then return to the caller.
- Keep the stack 16-byte aligned at call/ret boundaries to avoid crashes on some sequences.

Deliverable: `level4.txt`.

---

## Payload file format (levelN.txt)

- ASCII hex bytes, two hex digits per byte, separated by spaces and/or newlines.
- Little-endian for multi-byte integers and addresses.
- You may include `/* comments */` anywhere; `hex2raw` will strip them.

Example (toy):

```
/* padding up to saved RIP */
41 41 41 41  41 41 41 41  /* ... */
/* overwrite RIP with &smoke */
ef be ad de 00 00 00 00
```

---

## Grading and submission (this repo)

Your submission consists of the five payload files in `src/`:

- `level0.txt` … `level4.txt`

The provided tests will validate them locally. We consider a level passed when the expected success string appears and the program prints `VALID`.

Run locally:

```
cd src
./test.sh
```

---

## Rules and guidance

- Work within the provided environment. Don’t try to alter `bufbomb` itself.
- Don’t brute-force addresses; use disassembly and symbols to reason precisely.
- Keep your payloads minimal and well-commented to help future debugging.
- Respect the lab’s educational intent; do not use these skills outside controlled settings.

---

## Troubleshooting

- Crash before success message: verify the offset to the saved return address and alignment.
- Garbage argument to `fizz`: confirm `%rdi` is correctly set (register view in GDB) and cookie endianness.
- Silent returns on Level 3/4: check that `%rax` is set to `0x373e31da` right before the final `ret`.
- Level 4 only works with `-n`: ensure you used `./hex2raw -n` and `./bufbomb -n` together.

---

## Quick reference

- Disassemble: `objdump -d ./bufbomb | less`
- Symbols: `nm -n ./bufbomb | grep -E 'smoke|fizz|getbuf|getbufn|global_value'`
- Run a level: `cat levelN.txt | ./hex2raw | ./bufbomb -u temp`
- Run Level 4: `cat level4.txt | ./hex2raw -n | ./bufbomb -n -u temp`
- Run tests: `./test.sh`

This handout mirrors the structure of the Buffer Lab description (buflab32.pdf), adapted to this offline repository and the included automated tests.