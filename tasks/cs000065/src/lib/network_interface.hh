#pragma once

#include "address.hh"
#include "arp_message.hh"
#include "ethernet_frame.hh"
#include "ipv4_datagram.hh"

#include <cstdint>
#include <map>
#include <memory>
#include <optional>
#include <queue>
#include <string>

// Network interface that handles ARP and Ethernet frames
class NetworkInterface
{
public:
  // Abstract base class for output ports
  class OutputPort
  {
  public:
    virtual ~OutputPort() = default;
    virtual void transmit( const NetworkInterface& interface, const EthernetFrame& frame ) = 0;
  };

  NetworkInterface( const std::string& name,
                   std::shared_ptr<OutputPort> output,
                   const EthernetAddress& ethernet_address,
                   const Address& ip_address );

  // Send an Internet datagram to the specified next hop
  void send_datagram( const InternetDatagram& dgram, const Address& next_hop );

  // Receive an Ethernet frame
  void recv_frame( const EthernetFrame& frame );

  // Access received datagrams
  std::queue<InternetDatagram>& datagrams_received() { return datagrams_received_; }
  const std::queue<InternetDatagram>& datagrams_received() const { return datagrams_received_; }

  // Tick the interface (for ARP cache timeout)
  void tick( uint64_t ms_since_last_tick );

private:
  std::string name_;
  std::shared_ptr<OutputPort> output_;
  EthernetAddress ethernet_address_;
  Address ip_address_;

  struct ARPEntry
  {
    EthernetAddress ethernet_address;
    uint64_t time_added;
  };

  static constexpr uint64_t ARP_ENTRY_TTL = 30000; // 30 seconds
  static constexpr uint64_t ARP_REQUEST_TTL = 5000; // 5 seconds

  std::map<uint32_t, ARPEntry> arp_table_ {};
  std::map<uint32_t, uint64_t> pending_arp_requests_ {};
  std::map<uint32_t, std::queue<std::pair<InternetDatagram, Address>>> pending_datagrams_ {};
  std::queue<InternetDatagram> datagrams_received_ {};

  uint64_t time_elapsed_ {};

  void send_arp_request( uint32_t target_ip );
  void send_arp_reply( const EthernetAddress& target_ethernet, uint32_t target_ip );
  void send_ethernet_frame( const EthernetAddress& dst, uint16_t type, const std::vector<Ref<std::string>>& payload );
};

