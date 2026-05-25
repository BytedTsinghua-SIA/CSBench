#include "byte_stream.hh"

using namespace std;

void read( Reader& reader, uint64_t max_len, string& out )
{
  (void)reader;
  (void)max_len;
  (void)out;
}

Reader& ByteStream::reader()
{
  return static_cast<Reader&>( *this );
}

const Reader& ByteStream::reader() const
{
  return static_cast<const Reader&>( *this );
}

Writer& ByteStream::writer()
{
  return static_cast<Writer&>( *this );
}

const Writer& ByteStream::writer() const
{
  return static_cast<const Writer&>( *this );
}
