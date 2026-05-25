#pragma once

#include "tcp_receiver_message.hh"
#include "tcp_sender_message.hh"

// Combined TCP message containing both sender and receiver information
struct TCPMessage
{
  std::shared_ptr<TCPSenderMessage> sender;
  TCPReceiverMessage receiver;
};

