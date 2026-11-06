## Task Instructions

https://pdos.csail.mit.edu/6.S081/2021/labs/net.html

### Task Source

MIT 6.S081: Operating System Engineering Lab: Networking

### Task Overview

This lab involves implementing a network stack in the xv6 operating system, including device driver for the E1000 network card, packet transmission and reception, and support for basic networking protocols. The goal is to enable xv6 to communicate with a host server via UDP, perform ping tests, and handle DNS queries.

### Detailed Requirements

1. **E1000 Driver**: Implement the E1000 network card driver to handle initialization, transmit and receive descriptors, and interrupt handling.
2. **Network Stack**: Add networking system calls (e.g., `connect`, `send`, `recv`) and integrate with the xv6 file system to allow user‑level programs to use sockets.
3. **Packet Handling**: Implement UDP packet construction and parsing, including checksum verification and IP header handling.
4. **Testing**: Ensure the implementation passes the provided test suite (`nettests`), which includes:
   - Ping test (sending and receiving ICMP‑like echo requests)
   - Single‑process ping test
   - Multi‑process concurrent ping test
   - DNS resolution test (querying a local server)
5. **Performance**: The network stack should be efficient enough to pass the tests within the time limits and without packet loss under normal conditions.
6. **Documentation**: Update the `time.txt` file with the number of hours spent on the lab.