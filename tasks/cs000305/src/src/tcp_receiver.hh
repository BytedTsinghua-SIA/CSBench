#pragma once

#include "reassembler.hh"
#include "tcp_receiver_message.hh"
#include "tcp_sender_message.hh"
#include "wrapping_integers.hh"

#include <cstdint>
#include <optional>

class TCPReceiver
{
public:
  explicit TCPReceiver( Reassembler reassembler ) : reassembler_( std::move( reassembler ) ) {}

  void receive( TCPSenderMessage message );

  TCPReceiverMessage send() const;

  Reassembler& reassembler() { return reassembler_; }
  const Reassembler& reassembler() const { return reassembler_; }

  Writer& writer() { return reassembler_.writer(); }
  const Writer& writer() const { return reassembler_.writer(); }

  Reader& reader() { return reassembler_.reader(); }
  const Reader& reader() const { return reassembler_.reader(); }

private:
  Reassembler reassembler_;
  std::optional<Wrap32> isn_ {};
};
