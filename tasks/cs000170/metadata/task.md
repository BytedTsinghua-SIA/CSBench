# Project Overview
This project asks you to build a user-space clone of the classic `traceroute` tool inside `traceroute.py`. The assignment is split across Project 1A and 1B; both halves extend the same code path.

## Implementation Scope
* Implement the IPv4, ICMP, and UDP header parsers by filling in the constructors inside `traceroute.py`. All fields must be decoded into host byte order using helpers from `util.py`.
* Complete `recv_probe_response` so it filters ICMP Time Exceeded and Port Unreachable replies that correspond to the UDP probes you send. Use the parsed headers to match against `TRACEROUTE_PORT_NUMBER` and report the responding router’s address.
* Finish `traceroute` to drive the probing loop. For each TTL from 1 to `TRACEROUTE_MAX_TTL`, send up to `PROBE_ATTEMPT_COUNT` UDP probes, collect distinct router addresses via `recv_probe_response`, call `util.print_result` to display the hop list, and stop once the destination IP appears in the current hop list.
* The starter supplies the CLI and socket wrappers in `util.py`; do not modify that file.

## Source Layout Expectations
* All required logic lives in `traceroute.py`. Keep the module name unchanged so the autograder can import it. Do not rename the file or add extra modules.
* Only add helper functions or classes inside `traceroute.py` if they preserve the existing API (`traceroute` must return `list[list[str]]`).
* Leave `util.py` untouched. It provides the socket abstractions, DNS helpers, and argument parsing that the tests expect.

## Constraints and Best Practices
* Use only the Python standard library that is already imported in the starter; avoid adding new imports or global state.
* Respect the provided constants (`TRACEROUTE_MAX_TTL`, `TRACEROUTE_PORT_NUMBER`, `PROBE_ATTEMPT_COUNT`). Tests assume these bounds.
* Handle duplicate router addresses by suppressing repeats within a single TTL bucket, but keep separate TTL rounds independent.
* Ensure helper sockets (`util.Socket.make_udp()` / `.make_icmp()`) are used exactly as provided; their behavior is mocked in the tests.
