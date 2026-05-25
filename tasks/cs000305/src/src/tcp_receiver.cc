#include "tcp_receiver.hh"

using namespace std;

void TCPReceiver::receive( TCPSenderMessage message )
{
  (void)message;
  // TODO(Checkpoint 2): implement TCP receiver.
}

TCPReceiverMessage TCPReceiver::send() const
{
  // TODO(Checkpoint 2): implement advertised window and ACKno.
  return TCPReceiverMessage {};
}
