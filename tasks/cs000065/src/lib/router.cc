#include "router.hh"

using namespace std;

size_t Router::add_interface( shared_ptr<NetworkInterface> interface )
{
  interfaces_.push_back( interface );
  return interfaces_.size() - 1;
}

void Router::add_route( uint32_t route_prefix, uint8_t prefix_length, optional<Address> next_hop, size_t interface_num )
{
  (void)route_prefix;
  (void)prefix_length;
  (void)next_hop;
  (void)interface_num;
}

void Router::route()
{}
