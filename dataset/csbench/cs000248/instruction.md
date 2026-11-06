## Task Instructions

https://pdos.csail.mit.edu/6.824/labs/lab-kvsrv1.html

### Task Source

MIT 6.824: Distributed Systems Lab 2 - Key/Value Server

### Task Overview

In this lab you will build a key/value server for a single machine that ensures that each Put operation is executed at-most-once despite network failures and that the operations are linearizable. You will use this KV server to implement a lock. Later labs will replicate a server like this one to handle server crashes.

### Detailed Requirements

#### 1. Key/Value Server Implementation

The server must maintain an in-memory map that records for each key a (value, version) tuple. Keys and values are strings. The version number records the number of times the key has been written.

**Put(key, value, version)** operation should:
- Install or replace the value for a key only if the Put's version number matches the server's version number for the key
- If the version numbers match, the server also increments the version number of the key
- If the version numbers don't match, the server should return rpc.ErrVersion
- A client can create a new key by invoking Put with version number 0 (the resulting version stored by the server will be 1)
- If the version number of the Put is larger than 0 and the key doesn't exist, the server should return rpc.ErrNoKey

**Get(key)** operation should:
- Fetch the current value for the key and its associated version
- If the key doesn't exist at the server, the server should return rpc.ErrNoKey

#### 2. Clerk Implementation with Retry Logic

The Clerk must handle network failures that may drop or reorder messages:

- **Get**: Keep retrying the RPC until a reply is received from the server
- **Put**: Keep retrying the RPC until a reply is received. Special handling for rpc.ErrVersion:
  - If the first RPC returns rpc.ErrVersion, return rpc.ErrVersion to the application (the Put was definitely not executed)
  - If a retried RPC returns rpc.ErrVersion, return rpc.ErrMaybe to the application (the earlier RPC might have been executed but the response was lost)
  - Wait 100ms between retries

#### 3. Lock Implementation

Implement a distributed lock layered on the key/value Clerk that supports:
- **Acquire**: Only one client can successfully acquire the lock at a time; other clients must wait until the first client has released the lock
- **Release**: Release the lock so other clients can acquire it
- Use a unique identifier for each lock client (call kvtest.RandValue(8))
- Use a specific key (passed as parameter l to MakeLock) to store the lock state
- The lock must work correctly with unreliable networks

#### 4. Test Requirements

All tests must pass:
- **Reliable tests**: Test basic functionality with no dropped messages
  - TestReliablePut: Basic Put and Get operations
  - TestPutConcurrentReliable: Concurrent clients putting to same key
  - TestMemPutManyClientsReliable: Memory usage check with many clients
  - TestOneClientReliable: Lock with one client
  - TestManyClientsReliable: Lock with multiple clients
- **Unreliable tests**: Test with dropped messages
  - TestUnreliableNet: KV server with unreliable network
  - TestOneClientUnreliable: Lock with one client and unreliable network
  - TestManyClientsUnreliable: Lock with multiple clients and unreliable network

#### 5. Linearizability

The implementation must ensure linearizable operations: if client operations aren't concurrent, each client Get and Put will observe the modifications implied by the preceding sequence of operations. For concurrent operations, the return values and final state will be the same as if the operations had executed one at a time in some order.
