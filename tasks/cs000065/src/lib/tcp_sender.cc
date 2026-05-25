#include "tcp_sender.hh"

using namespace std;

void TCPSender::push( const function<void( TCPSenderMessage )>& transmit )
{
  (void)transmit;
}

void TCPSender::tick( uint64_t ms_since_last_tick, const function<void( TCPSenderMessage )>& transmit )
{
  (void)ms_since_last_tick;
  (void)transmit;
}

void TCPSender::receive( const TCPReceiverMessage& msg )
{
  (void)msg;
}

TCPSenderMessage TCPSender::make_empty_message() const
{
  return {};
}

uint64_t TCPSender::sequence_numbers_in_flight() const
{
  return {};
}
