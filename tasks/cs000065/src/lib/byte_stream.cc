#include "byte_stream.hh"

using namespace std;

ByteStream::ByteStream( uint64_t capacity ) : capacity_( capacity ) {}

void Writer::push( string data )
{
  (void)data;
}

void Writer::close()
{}

bool Writer::is_closed() const
{
  return {};
}

uint64_t Writer::available_capacity() const
{
  return {};
}

uint64_t Writer::bytes_pushed() const
{
  return {};
}

string_view Reader::peek() const
{
  return {};
}

void Reader::pop( uint64_t len )
{
  (void)len;
}

bool Reader::is_finished() const
{
  return {};
}

uint64_t Reader::bytes_buffered() const
{
  return {};
}

uint64_t Reader::bytes_popped() const
{
  return {};
}
