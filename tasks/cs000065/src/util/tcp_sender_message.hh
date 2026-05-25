#pragma once

#include "wrapping_integers.hh"

#include <cstdint>
#include <string>
#include <vector>

// Message sent from TCPSender
struct TCPSenderMessage
{
  Wrap32 seqno { 0 };
  bool SYN {};
  std::string payload {};
  bool FIN {};
  bool RST {};

  // Calculate the sequence length (number of bytes this segment occupies in sequence space)
  uint64_t sequence_length() const
  {
    uint64_t len = payload.size();
    if ( SYN ) {
      len++;
    }
    if ( FIN ) {
      len++;
    }
    return len;
  }
};

