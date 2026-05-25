#pragma once

#include <cstdint>
#include <cstdlib>

class Wrap32
{
public:
  explicit Wrap32( uint32_t raw_value = 0 ) : raw_value_( raw_value ) {}

  uint32_t raw_value() const { return raw_value_; }

  static Wrap32 wrap( uint64_t absolute, Wrap32 isn )
  {
    (void)absolute;
    (void)isn;
    // TODO(Checkpoint 2): implement wrapping.
    return Wrap32 {};
  }

  uint64_t unwrap( Wrap32 isn, uint64_t checkpoint ) const
  {
    (void)isn;
    (void)checkpoint;
    // TODO(Checkpoint 2): implement unwrapping.
    return 0;
  }

  friend bool operator==( Wrap32 a, Wrap32 b ) { return a.raw_value_ == b.raw_value_; }

  friend Wrap32 operator+( Wrap32 a, uint64_t b )
  {
    return Wrap32 { static_cast<uint32_t>( a.raw_value_ + static_cast<uint32_t>( b ) ) };
  }

  friend Wrap32 operator+( uint64_t a, Wrap32 b ) { return b + a; }

protected:
  uint32_t raw_value_ {};
};
