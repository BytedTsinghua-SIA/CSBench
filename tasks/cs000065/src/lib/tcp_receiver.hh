#pragma once

#include "reassembler.hh"
#include "tcp_receiver_message.hh"
#include "tcp_sender_message.hh"
#include "wrapping_integers.hh"

#include <cstdint>
#include <optional>

// Receives and reassembles TCP segments into a byte stream
class TCPReceiver
{
public:
  explicit TCPReceiver( Reassembler&& reassembler ) : reassembler_( std::move( reassembler ) ) {}

  // Receive a TCP segment from the sender
  void receive( TCPSenderMessage msg );

  // Send a message to the sender (acknowledgment and window size)
  TCPReceiverMessage send() const;

  // Access the reassembled byte stream
  Reader& reader() { return reassembler_.reader(); }
  const Reader& reader() const { return reassembler_.reader(); }

  // Access the reassembler
  Reassembler& reassembler() { return reassembler_; }
  const Reassembler& reassembler() const { return reassembler_; }

  // Access the writer interface
  Writer& writer() { return reassembler_.stream_out().writer(); }
  const Writer& writer() const { return reassembler_.stream_out().writer(); }

private:
  Reassembler reassembler_;
  std::optional<Wrap32> isn_ {};
  bool syn_received_ {};
  uint64_t checkpoint_ {};
};

