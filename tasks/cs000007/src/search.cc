#include <iostream>
#include <string>
#include <vector>
#include "imdb.h"
#include "path.h"

using namespace std;

int main(int argc, char *argv[]) {
  if (argc != 3) {
    cout << "Usage: " << argv[0] << " <actor1> <actor2>" << endl;
    return 1;
  }

  imdb db("./slink");
  if (!db.good()) {
    cout << "Failed to open database." << endl;
    return 1;
  }

  cout << "No path between those two people could be found." << endl;

  return 0;
}
