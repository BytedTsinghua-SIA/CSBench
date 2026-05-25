#pragma once

#include "wrapping_integers.hh"

#include <cstdint>

// Configuration for TCP
struct TCPConfig
{
  static constexpr size_t DEFAULT_CAPACITY = 64000; // 64KB
  static constexpr uint16_t TIMEOUT_DFLT = 100;     // 100ms default timeout
  static constexpr uint8_t MAX_RETX_ATTEMPTS = 8;    // Maximum retransmission attempts

  size_t send_capacity = DEFAULT_CAPACITY;
  size_t recv_capacity = DEFAULT_CAPACITY;
  uint16_t rt_timeout = TIMEOUT_DFLT;
  Wrap32 isn { 0 };
};

