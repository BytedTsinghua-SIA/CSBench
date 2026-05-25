#include "tcp_receiver.hh"

using namespace std;

void TCPReceiver::receive( TCPSenderMessage msg )
{
  (void)msg;
}

TCPReceiverMessage TCPReceiver::send() const
{
  return {};
}
