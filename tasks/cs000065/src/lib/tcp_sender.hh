#pragma once

#include "byte_stream.hh"
#include "tcp_config.hh"
#include "tcp_receiver_message.hh"
#include "tcp_sender_message.hh"
#include "wrapping_integers.hh"

#include <cstdint>
#include <deque>
#include <functional>
#include <optional>

// Sends TCP segments reliably with retransmission and congestion control
class TCPSender
{
public:
  explicit TCPSender( ByteStream&& stream, Wrap32 isn, uint16_t retx_timeout )
    : stream_( std::move( stream ) ), isn_( isn ), retx_timeout_( retx_timeout ), next_seqno_( isn )
  {}

  // Push data from the stream and send segments
  void push( const std::function<void( TCPSenderMessage )>& transmit );

  // Handle time passing
  void tick( uint64_t ms_since_last_tick, const std::function<void( TCPSenderMessage )>& transmit );

  // Receive an acknowledgment from the receiver
  void receive( const TCPReceiverMessage& msg );

  // Make an empty message (for keep-alive or acknowledgment)
  TCPSenderMessage make_empty_message() const;

  // Access the byte stream
  Reader& reader() { return stream_.reader(); }
  const Reader& reader() const { return stream_.reader(); }
  Writer& writer() { return stream_.writer(); }
  const Writer& writer() const { return stream_.writer(); }

  // Get the number of sequence numbers in flight
  uint64_t sequence_numbers_in_flight() const;

  // Get the number of consecutive retransmissions
  uint64_t consecutive_retransmissions() const { return consecutive_retransmissions_; }

private:
  ByteStream stream_;
  Wrap32 isn_;
  uint16_t retx_timeout_;
  Wrap32 next_seqno_;
  
  struct OutstandingSegment
  {
    TCPSenderMessage msg {};
    uint64_t abs_seqno {};
    uint64_t time_sent {};
  };
  
  std::deque<OutstandingSegment> outstanding_segments_ {};
  uint64_t time_elapsed_ {};
  uint64_t consecutive_retransmissions_ {};
  
  std::optional<Wrap32> ackno_ {};
  uint16_t window_size_ { 1 }; // Start with window size of 1
  
  bool syn_sent_ {};
  bool fin_sent_ {};
  
  void send_segment( const std::function<void( TCPSenderMessage )>& transmit, bool syn, bool fin, std::string payload );
  uint64_t abs_seqno( Wrap32 seqno ) const;
};

