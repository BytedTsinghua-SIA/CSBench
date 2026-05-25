#include "byte_stream.hh"

#include <cstdint>
#include <string>

using namespace std;

ByteStream::ByteStream( uint64_t capacity ) : capacity_( capacity ) {}

// Push data to stream, but only as much as available capacity allows.
void Writer::push( string data )
{
  (void)data;
  // TODO(Checkpoint 0): implement ByteStream buffering.
}

// Signal that the stream has reached its ending. Nothing more will be written.
void Writer::close()
{
  closed_ = true;
}

// Has the stream been closed?
bool Writer::is_closed() const
{
  return closed_;
}

// How many bytes can be pushed to the stream right now?
uint64_t Writer::available_capacity() const
{
  // TODO(Checkpoint 0): should account for bytes currently buffered.
  return capacity_;
}

// Total number of bytes cumulatively pushed to the stream
uint64_t Writer::bytes_pushed() const
{
  // TODO(Checkpoint 0): track total bytes pushed.
  return 0;
}

// Peek at the next bytes in the buffer -- ideally as many as possible.
// It's not required to return a string_view of the *whole* buffer, but
// if the peeked string_view is only one byte at a time, it will probably force
// the caller to do a lot of extra work.
string_view Reader::peek() const
{
  // TODO(Checkpoint 0): return a view into the buffered bytes.
  return {};
}

// Remove `len` bytes from the buffer.
void Reader::pop( uint64_t len )
{
  (void)len;
  // TODO(Checkpoint 0): remove bytes from the buffer.
}

// Is the stream finished (closed and fully popped)?
bool Reader::is_finished() const
{
  // With an empty placeholder implementation, the stream is considered finished
  // only after close().
  return closed_;
}

// Number of bytes currently buffered (pushed and not popped)
uint64_t Reader::bytes_buffered() const
{
  // TODO(Checkpoint 0): report the number of bytes currently buffered.
  return 0;
}

// Total number of bytes cumulatively popped from stream
uint64_t Reader::bytes_popped() const
{
  // TODO(Checkpoint 0): track total bytes popped.
  return 0;
}
