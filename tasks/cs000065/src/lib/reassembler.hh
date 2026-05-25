#pragma once

#include "byte_stream.hh"

#include <cstdint>
#include <map>
#include <string>

// Reassembles a byte stream (in substrings, possibly out-of-order) into an in-order byte stream.
class Reassembler
{
public:
  // Construct a `Reassembler` that will store up to `capacity` bytes.
  explicit Reassembler( ByteStream&& output ) : output_( std::move( output ) ) {}

  // Receive a substring and write any newly contiguous bytes into the stream.
  // `first_index`: the index of the first byte in `data`
  // `data`: the substring itself
  // `is_last_substring`: this substring represents the end of the stream
  void insert( uint64_t first_index, std::string data, bool is_last_substring );

  // Access the reassembled ByteStream (your code shouldn't call this directly)
  ByteStream& stream_out() { return output_; }
  const ByteStream& stream_out() const { return output_; }

  // The number of bytes in the substrings stored but not yet reassembled
  uint64_t count_bytes_pending() const;

  // Access the output ByteStream Reader interface
  Reader& reader() { return output_.reader(); }
  const Reader& reader() const { return output_.reader(); }

private:
  ByteStream output_; // The reassembled in-order byte stream
  uint64_t first_unassembled_ {};
  uint64_t first_unacceptable_ {};
  bool eof_received_ {};
  std::map<uint64_t, std::string> pending_segments_ {};
  
  void try_merge();
};

