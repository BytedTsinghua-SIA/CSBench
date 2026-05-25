#include "reassembler.hh"

using namespace std;

Reassembler::Reassembler( ByteStream output ) : output_( std::move( output ) ) {}

void Reassembler::insert( uint64_t first_index, std::string data, bool is_last_substring )
{
  (void)first_index;
  (void)data;
  (void)is_last_substring;
  // TODO(Checkpoint 1): implement stream reassembly.
}
