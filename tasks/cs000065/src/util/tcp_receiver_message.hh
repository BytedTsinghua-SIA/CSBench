#pragma once

#include "wrapping_integers.hh"

#include <cstdint>
#include <optional>

// Message sent from TCPReceiver to TCPSender
struct TCPReceiverMessage
{
  std::optional<Wrap32> ackno {};
  uint16_t window_size {};
  bool RST {};
};

