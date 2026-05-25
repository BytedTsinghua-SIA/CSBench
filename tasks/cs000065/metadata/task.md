# CS144：Minnow

## Background

Introduction to Computer Networking is a hands-on course that teaches students the fundamentals of computer networking through practical implementation. The lab project is based on a codebase called "Minnow," where students build a simplified TCP/IP protocol stack from scratch. This project helps students understand the design and implementation details of network protocols by implementing and testing various network components.

# Core Tasks/Functionality

The lab project is divided into multiple checkpoints, each focusing on implementing specific network functionality modules:

## Checkpoint 0: Networking Warmup

- **Objective**: Familiarize with the networking programming environment and master basic network tools and operations.
- **Tasks**:
  - Use `telnet` to manually fetch web content, understanding the basic flow of HTTP requests and responses.
  - Implement a program called `webget` that uses the operating system's TCP sockets to fetch web content via HTTP protocol.

## Checkpoint 1: Stitching Substrings into a Byte Stream

- **Objective**: Implement a stream reassembler that correctly assembles received byte stream fragments into a continuous byte stream in the correct order.
- **Tasks**:
  - Handle out-of-order byte stream fragments, ensuring data integrity and ordering.
  - Manage buffers, handle duplicate data and fragments that exceed the window.

## Checkpoint 2: The TCP Receiver

- **Objective**: Implement the receiving side of the TCP protocol, processing incoming TCP segments and managing the receive window.
- **Tasks**:
  - Parse TCP segments, extracting key information such as sequence numbers and acknowledgment numbers.
  - Collaborate with the stream reassembler to ensure correct data reception and delivery.

## Checkpoint 3: The TCP Sender

- **Objective**: Implement the sending side of the TCP protocol, managing data transmission, retransmission, and congestion control.
- **Tasks**:
  - Implement the sliding window protocol, managing data that has been sent but not yet acknowledged.
  - Handle timeout retransmission to ensure reliable data transmission.
  - Implement basic congestion control mechanisms to avoid network congestion.

## Checkpoint 4: Measuring the Real World

- **Objective**: Measure and analyze real-world network performance using the implemented TCP/IP stack.
- **Tasks**:
  - Test the TCP implementation against real network conditions.
  - Measure and analyze network performance metrics.
  - Compare implementation behavior with real-world network protocols.

## Checkpoint 5: Down the Stack (The Network Interface)

- **Objective**: Implement the network interface layer, including address resolution and lower-level protocol handling.
- **Tasks**:
  - Implement the Address Resolution Protocol (ARP) to resolve IP addresses to MAC addresses.
  - Handle ARP requests and replies, maintain an ARP cache table.
  - Handle ARP cache timeout and update mechanisms.
  - Implement network interface functionality for packet transmission and reception.

## Checkpoint 6: Building an IP Router

- **Objective**: Implement a simple router that can forward IP packets according to a routing table.
- **Tasks**:
  - Parse IP packets, extract source address, destination address, and other information.
  - Look up the next hop address according to the routing table and forward packets.
  - Handle ICMP error messages, such as destination unreachable.

## Checkpoint 7: Making an Internet + Something Creative!

- **Objective**: Integrate all implemented components to create a functional network and add a creative extension.
- **Tasks**:
  - Combine all previous checkpoints to build a complete, working network stack.
  - Test the full implementation in a network environment.
  - Design and implement a creative extension or application that demonstrates the network stack's capabilities.



