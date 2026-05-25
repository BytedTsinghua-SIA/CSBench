#pragma once

#include "byte_stream.hh"

#include <cstdint>
#include <string>

class Reassembler
{
public:
  // Construct Reassembler to write into given ByteStream.
  explicit Reassembler( ByteStream&& output ) : output_( std::move( output ) ) {}

  /*
   * Insert a new substring to be reassembled into a ByteStream.
   *   first_index: the index of the first byte of the string
   *   data: the substring itself
   *   is_last_substring: this substring represents the end of the stream
   *
   * The Reassembler's job is to reassemble the indexed substrings (possibly out-of-order
   * and possibly overlapping) back into the original ByteStream. As soon as the Reassembler
   * learns the next byte in the stream, it should write it to the output.
   *
   * If the Reassembler learns about bytes that fit within the stream's available capacity
   * but can't yet be written (because earlier bytes remain unknown), it should store them
   * internally until the gaps are filled in.
   *
   * The Reassembler should discard any bytes that lie beyond the stream's available capacity
   * (i.e., bytes that couldn't be written even if earlier gaps get filled in).
   *
   * The Reassembler should close the stream after writing the last byte.
   */
  void insert( uint64_t first_index, std::string data, bool is_last_substring );

  // Return a reference to the reassembler's output stream reader.
  Reader& reader() { return output_.reader(); }

  // How many bytes are stored in the Reassembler itself?
  // (i.e., not yet pushed to the output stream)
  uint64_t count_bytes_pending() const;

private:
  ByteStream output_; // The reassembler writes to this stream
};
