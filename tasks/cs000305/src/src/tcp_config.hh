#pragma once

#include "wrapping_integers.hh"

#include <cstdint>

struct TCPConfig
{
  // Upper bound used by tests to generate random-sized segments.
  // (Typical MTU-ish payload size; exact value isn't important as long as > 1.)
  static constexpr uint16_t MAX_PAYLOAD_SIZE = 1452;

  // Receiver-side buffer capacity (bytes).
  uint64_t recv_capacity { 65535 };

  // Sender-side settings (present for compatibility with tcp_peer.hh / sender harness).
  uint64_t send_capacity { 65535 };
  Wrap32 isn { 0 };
  uint64_t rt_timeout { 1000 };
};
