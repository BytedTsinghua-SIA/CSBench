#pragma once

#include "network_interface.hh"
#include "ipv4_datagram.hh"

#include <cstdint>
#include <memory>
#include <vector>

// Simple IP router that forwards datagrams based on routing table
class Router
{
public:
  // Add a network interface
  size_t add_interface( std::shared_ptr<NetworkInterface> interface );

  // Add a route to the routing table
  void add_route( uint32_t route_prefix, uint8_t prefix_length, std::optional<Address> next_hop, size_t interface_num );

  // Route a datagram
  void route();

  // Get interface by index
  std::shared_ptr<NetworkInterface> interface( size_t index )
  {
    if ( index >= interfaces_.size() ) {
      return nullptr;
    }
    return interfaces_[index];
  }

private:
  struct RouteEntry
  {
    uint32_t route_prefix {};
    uint8_t prefix_length {};
    std::optional<Address> next_hop {};
    size_t interface_num {};
  };

  std::vector<std::shared_ptr<NetworkInterface>> interfaces_ {};
  std::vector<RouteEntry> routing_table_ {};

  uint32_t network_mask( uint8_t prefix_length ) const;
  bool matches_route( uint32_t ip, const RouteEntry& route ) const;
  std::optional<RouteEntry> find_best_route( uint32_t ip ) const;
  void send_icmp_error( const InternetDatagram& original_dgram, uint8_t icmp_type, size_t interface_num );
};

