#pragma once

#include <cstdint>
#include <optional>

// Wrapper for 32-bit sequence numbers that handles wrapping
class Wrap32
{
public:
  explicit Wrap32( uint32_t raw_value ) : raw_value_( raw_value ) {}

  // Wrap an absolute sequence number (n) around a checkpoint (isn)
  static Wrap32 wrap( uint64_t n, Wrap32 isn );

  // Unwrap a sequence number to the nearest absolute sequence number
  // given a checkpoint and the absolute sequence number of the checkpoint
  uint64_t unwrap( Wrap32 isn, uint64_t checkpoint ) const;

  // Get the raw 32-bit value
  uint32_t raw_value() const { return raw_value_; }

  // Comparison operators
  bool operator==( const Wrap32& other ) const { return raw_value_ == other.raw_value_; }
  bool operator!=( const Wrap32& other ) const { return raw_value_ != other.raw_value_; }
  bool operator<( const Wrap32& other ) const { return raw_value_ < other.raw_value_; }

  // Arithmetic operators
  Wrap32 operator+( uint32_t n ) const { return Wrap32( raw_value_ + n ); }
  Wrap32 operator-( uint32_t n ) const { return Wrap32( raw_value_ - n ); }
  uint32_t operator-( const Wrap32& other ) const
  {
    return raw_value_ >= other.raw_value_ ? raw_value_ - other.raw_value_
                                          : ( UINT32_MAX - other.raw_value_ + raw_value_ + 1 );
  }

private:
  uint32_t raw_value_ {};
};

