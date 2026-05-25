#include "imdb.h"
#include <string>
#include <vector>
#include <sys/stat.h>

using namespace std;

const char *const imdb::kActorFileName = "actordata";
const char *const imdb::kMovieFileName = "moviedata";

imdb::imdb(const string& directory) {
  // For now, we'll just pretend we're loading the data.
}

bool imdb::good() const {
  // In this minimal implementation, we'll always return true.
  return true;
}

bool imdb::getCredits(const string& player, vector<film>& films) const {
  return false; // Always return false for now.
}

bool imdb::getCast(const film& movie, vector<string>& players) const {
  return false; // Always return false for now.
}

imdb::~imdb() {}

const void *imdb::acquireFileMap(const std::string& fileName, struct fileInfo& info) {
    return NULL;
}

void imdb::releaseFileMap(struct fileInfo& info) {
}
