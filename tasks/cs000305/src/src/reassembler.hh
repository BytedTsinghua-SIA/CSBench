#pragma once

#include "byte_stream.hh"

#include <cstdint>
#include <string>

class Reassembler
{
public:
  explicit Reassembler( ByteStream output );

  void insert( uint64_t first_index, std::string data, bool is_last_substring );

  Reader& reader() { return output_.reader(); }
  const Reader& reader() const { return output_.reader(); }

  Writer& writer() { return output_.writer(); }
  const Writer& writer() const { return output_.writer(); }

  uint64_t count_bytes_pending() const { return 0; }

  uint64_t first_unassembled() const { return output_.writer().bytes_pushed(); }

private:
  ByteStream output_;

  // TODO(Checkpoint 1): add reassembly state here.
};
