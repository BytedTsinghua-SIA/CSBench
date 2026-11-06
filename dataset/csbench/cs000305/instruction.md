# Lab Checkpoint 2: The TCP Receiver

## Overview
In this checkpoint, you will implement the `TCPReceiver`. This module handles incoming TCP segments (messages from the peer's sender), reassembles the byte stream using the `Reassembler` (from Checkpoint 1), and generates acknowledgment messages (Ackno and Window Size) back to the sender.

## Core Responsibilities

The `TCPReceiver` has two main roles:

1.  **Process Incoming Segments (`receive`)**:
    -   Receive messages from the TCP sender.
    -   Extract the sequence number and payload.
    -   Push the data into the `Reassembler`, which writes to the incoming `ByteStream`.
    -   Handle the `SYN` (start of stream) and `FIN` (end of stream) flags.

2.  **Generate Receiver Messages (`send`)**:
    -   Provide the **Acknowledgment Number (Ackno)**: The sequence number corresponding to the "first unassembled" index (the next byte needed).
    -   Provide the **Window Size**: The available capacity in the output `ByteStream`.

## Sequence Numbers vs. Stream Indices
A major part of this assignment is handling the translation between two indexing systems:
-   **Stream Index (64-bit)**: Used by the `Reassembler` and `ByteStream`. Starts at 0.
-   **Sequence Number (32-bit)**: Used in TCP headers. Wraps around $2^{32}$. Starts at a random Initial Sequence Number (ISN).

### Rules for Translation:
-   **SYN**: Occupies 1 sequence number. If ISN is $X$, the SYN is at $X$. The first byte of data is at $X+1$.
-   **Payload**: Each byte of data occupies 1 sequence number.
-   **FIN**: Occupies 1 sequence number, occurring after the last byte of data.
-   **Wrapping**: You must handle the 32-bit wrap-around correctly.

## Implementation Details
-   You will likely modify:
    -   `src/tcp_receiver.hh`
    -   `src/tcp_receiver.cc`
    
## Specific Tasks
1.  Implement the `receive` method to handle incoming `TCPSenderMessage`s.
    -   Detect `SYN` to set the ISN.
    -   Translate 32-bit sequence numbers to 64-bit stream indices (handling wrap-around to find the "closest" absolute index).
    -   Insert data into the `Reassembler`.
2.  Implement the `send` method to generate a `TCPReceiverMessage`.
    -   Calculate `ackno` (fetching `first_unassembled_index` from reassembler and converting back to 32-bit seqno).
    -   Calculate `window_size` (capped at UINT16_MAX).