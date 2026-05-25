#include "network_interface.hh"

#include "arp_message.hh"
#include "ethernet_header.hh"
#include "ipv4_header.hh"

using namespace std;

NetworkInterface::NetworkInterface( const string& name,
                                   shared_ptr<OutputPort> output,
                                   const EthernetAddress& ethernet_address,
                                   const Address& ip_address )
  : name_( name ), output_( output ), ethernet_address_( ethernet_address ), ip_address_( ip_address )
{}

void NetworkInterface::send_datagram( const InternetDatagram& dgram, const Address& next_hop )
{
  (void)dgram;
  (void)next_hop;
}

void NetworkInterface::recv_frame( const EthernetFrame& frame )
{
  (void)frame;
}

void NetworkInterface::tick( uint64_t ms_since_last_tick )
{
  (void)ms_since_last_tick;
}
