# Lab Checkpoint 1: Stitching Substrings into a Byte Stream

## Overview
This lab involves implementing a TCP receiver module, specifically the `Reassembler` class, which stitches received substrings into a contiguous byte stream. Additionally, there is a hands-on component involving raw network sockets and packet analysis.

## Components

### 1. Hands-on Component: Private Network & Raw Sockets
-   **Setup**: Join the CS144 private network using WireGuard.
-   **Analysis**:
    -   Ping a groupmate's VM and analyze round-trip delay, delivery rate, and loss rate.
    -   Capture packets using `tcpdump` and inspect them with Wireshark.
    -   Compare captured datagrams from sender and receiver perspectives.
-   **Coding**:
    -   Implement `apps/ip_raw.cc` to send an Internet datagram (protocol 5) and a UDP datagram (protocol 17) using a raw socket.
    -   Verify reception with a groupmate.

### 2. Implementation Component: The Reassembler
-   **Goal**: Implement the `Reassembler` class in `src/reassembler.hh` and `src/reassembler.cc`.
-   **Functionality**:
    -   Receive substrings (segments) of a byte stream, potentially out of order, duplicated, or overlapping.
    -   Reassemble them into a contiguous stream of bytes.
    -   Write available bytes to the `ByteStream` (implemented in Checkpoint 0) as soon as they are known.
    -   Store "unassembled" bytes that fit within the capacity but cannot be written yet.
    -   Discard bytes that lie beyond the stream's available capacity.
-   **Interface**:
    -   `void insert(uint64_t first_index, std::string data, bool is_last_substring)`: Insert a new substring.
    -   `uint64_t count_bytes_pending() const`: Return the number of bytes stored in the Reassembler.
    -   `Reader& reader()`: Access the output stream reader.
-   **Constraints**:
    -   Do not change the public interface.
    -   Internal storage must handle overlapping substrings efficiently (store only one copy of data).
    -   Respect the capacity limit for both buffered bytes in `ByteStream` and unassembled substrings.
    -   Performance benchmark: > 0.1 Gbit/s (10 Gbit/s is top-tier).

## Development & Debugging
-   **Build & Test**:
    -   `cmake -S . -B build`
    -   `cmake --build build`
    -   `cmake --build build --target check1`
-   **Style**: Follow Modern C++ guidelines.
