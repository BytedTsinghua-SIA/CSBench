# Lab 1: Buffer Overflows

## Introduction

This lab provides practical experience with buffer overflow vulnerabilities and attacks. You will explore buffer overflow attacks in the context of the **zookws** web server, which runs a simple Python web application called **zoobar** where users transfer "zoobars" (credits) between each other.

The lab focuses on:
- Finding buffer overflow vulnerabilities in the zookws web server code
- Writing exploits for buffer overflows to inject code into the server over the network
- Bypassing non-executable stack protection mechanisms
- Understanding return-to-libc attacks
- Finding and fixing security vulnerabilities

## Background

Buffer overflows are a common class of security vulnerabilities that occur when a program writes data beyond the boundaries of a buffer in memory. Attackers can exploit these vulnerabilities to:
- Overwrite return addresses on the stack
- Inject malicious code
- Gain control over program execution
- Compromise system security

Modern defenses include:
- Stack canaries (e.g., GCC's Stack-Smashing Protector/SSP)
- Non-executable stacks (NX bit)
- Address Space Layout Randomization (ASLR)

Understanding these attacks is crucial for developing secure software and implementing effective defenses.

## Core Tasks

### Part 1: Getting Started

**Exercise 1**: Familiarize yourself with the lab infrastructure
- Set up the virtual machine environment
- Clone the lab repository
- Compile the zookws web server
- Understand the web server structure and functionality

### Part 2: Exploiting Buffer Overflows

**Exercise 2**: Find and exploit buffer overflow vulnerabilities
- Identify buffer overflow vulnerabilities in the zookws web server code
- Write exploits that overflow buffers and crash the server
- Understand how buffer overflows can overwrite return addresses

**Exercise 3**: Inject shellcode
- Develop exploits that inject shellcode through buffer overflows
- Execute arbitrary code on the server by redirecting control flow to injected shellcode
- Understand the mechanics of code injection attacks

**Exercise 4**: Bypass stack protection
- Work with stack-protected binaries that include canary values
- Develop exploits that bypass stack canary protection
- Understand the limitations of stack canaries

### Part 3: Return-to-libc Attacks

**Exercise 5**: Implement return-to-libc attack
- Exploit buffer overflows when the stack is non-executable
- Redirect control flow to existing library functions (e.g., `unlink`)
- Use ROP (Return-Oriented Programming) gadgets to set up function arguments
- Execute attacks without injecting any new code into the server

**Challenge (Optional)**: Perform return-to-libc attack without using the `accidentally` function
- Find alternative ROP gadgets in the codebase or loaded libraries
- Understand misaligned instruction parsing techniques
- Use tools like ROPgadget to discover useful instruction sequences

### Part 4: Fixing Buffer Overflows and Other Bugs

**Exercise 6**: Find additional vulnerabilities
- Analyze the source code for security vulnerabilities beyond buffer overflows
- Trace attacker-controlled input through the server code
- Identify at least two additional vulnerabilities
- Document attacks, their limitations, potential impact, and prevention methods

**Exercise 7**: Fix vulnerabilities
- Fix all buffer overflow vulnerabilities exploited in Exercises 2, 4, and 5
- Implement proper input validation and bounds checking
- Ensure fixes prevent exploits from working (do not rely on compile-time protections)
- Verify that fixes do not break existing functionality

## Key Concepts

- **Buffer Overflow**: Writing beyond buffer boundaries to overwrite adjacent memory
- **Stack Layout**: Understanding how local variables, saved registers, and return addresses are stored on the stack
- **Shellcode**: Machine code injected and executed to perform attacker-controlled actions
- **Stack Canaries**: Values placed before return addresses to detect stack corruption
- **Return-to-libc**: Attack technique that redirects execution to existing library functions instead of injected code
- **ROP Gadgets**: Short sequences of existing instructions that can be chained to perform desired operations
- **x86-64 Calling Conventions**: Understanding how function arguments are passed in registers

## Learning Objectives

Upon completing this lab, you should be able to:
1. Identify buffer overflow vulnerabilities in C code
2. Understand memory layout and stack structure
3. Craft buffer overflow exploits to overwrite return addresses
4. Write and inject shellcode for code execution
5. Bypass common defense mechanisms (stack canaries, non-executable stacks)
6. Implement return-to-libc attacks using ROP gadgets
7. Find security vulnerabilities through code analysis
8. Fix buffer overflow vulnerabilities through proper programming practices

