#include "debug.hh"
#include "socket.hh"

#include <cstdlib>
#include <iostream>
#include <span>
#include <string>

using namespace std;

namespace {
void get_URL( const string& host, const string& path )
{
  // Create a TCP socket and connect to the host
  TCPSocket socket;
  Address server_address;
  
  // Try to parse port from host (format: host:port)
  size_t colon_pos = host.find( ':' );
  if ( colon_pos != string::npos ) {
    string hostname = host.substr( 0, colon_pos );
    uint16_t port = static_cast<uint16_t>( stoul( host.substr( colon_pos + 1 ) ) );
    server_address = Address( hostname, port );
  } else {
    // Default to HTTP port 80
    server_address = Address( host, "http" );
  }
  
  socket.connect( server_address );
  
  // Send HTTP GET request
  string request = "GET " + path + " HTTP/1.1\r\n";
  request += "Host: " + host + "\r\n";
  request += "Connection: close\r\n";
  request += "\r\n";
  
  socket.write_all( request );
  socket.shutdown( SHUT_WR );
  
  // Read and print the response
  string response;
  while ( !socket.eof() ) {
    socket.read( response );
    cout << response;
    response.clear();
  }
}
} // namespace

int main( int argc, char* argv[] )
{
  try {
    if ( argc <= 0 ) {
      abort(); // For sticklers: don't try to access argv[0] if argc <= 0.
    }

    auto args = span( argv, argc );

    // The program takes two command-line arguments: the hostname and "path" part of the URL.
    // Print the usage message unless there are these two arguments (plus the program name
    // itself, so arg count = 3 in total).
    if ( argc != 3 ) {
      cerr << "Usage: " << args.front() << " HOST PATH\n";
      cerr << "\tExample: " << args.front() << " stanford.edu /class/cs144\n";
      return EXIT_FAILURE;
    }

    // Get the command-line arguments.
    const string host { args[1] };
    const string path { args[2] };

    // Call the student-written function.
    get_URL( host, path );
  } catch ( const exception& e ) {
    cerr << e.what() << "\n";
    return EXIT_FAILURE;
  }

  return EXIT_SUCCESS;
}
