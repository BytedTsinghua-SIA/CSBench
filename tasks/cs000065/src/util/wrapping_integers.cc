#include "wrapping_integers.hh"

#include <cstdint>

Wrap32 Wrap32::wrap( uint64_t n, Wrap32 isn )
{
  uint64_t offset = n - isn.raw_value();
  return Wrap32( isn.raw_value() + static_cast<uint32_t>( offset ) );
}

uint64_t Wrap32::unwrap( Wrap32 isn, uint64_t checkpoint ) const
{
  uint32_t offset = *this - isn;
  uint64_t result = checkpoint + offset;

  // Adjust for wrapping
  const uint64_t UINT32_MAX_PLUS_1 = static_cast<uint64_t>( UINT32_MAX ) + 1;
  
  if ( result > checkpoint + UINT32_MAX_PLUS_1 / 2 ) {
    result -= UINT32_MAX_PLUS_1;
  } else if ( result < checkpoint - UINT32_MAX_PLUS_1 / 2 ) {
    result += UINT32_MAX_PLUS_1;
  }

  return result;
}

