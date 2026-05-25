#pragma once

#include "wrapping_integers.hh"

#include <string>

struct TCPSenderMessage
{
  Wrap32 seqno {};
  bool SYN {};
  bool FIN {};
  bool RST {};
  std::string payload {};

  size_t sequence_length() const
  {
    return static_cast<size_t>( SYN ) + payload.size() + static_cast<size_t>( FIN );
  }
};
