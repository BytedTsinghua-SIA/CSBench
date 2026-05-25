#include "path.h"

using namespace std;

using namespace std;

path::path(const string& startPlayer) : startPlayer(startPlayer) {}

void path::addConnection(const film& movie, const string& player) {}

void path::undoConnection() {}

const string& path::getLastPlayer() const {
  // This is a stub. It should return the last player in the path.
  // For now, we return the start player.
  return startPlayer;
}

void path::reverse() {}

ostream& operator<<(ostream& os, const path& p) {
  return os;
}
