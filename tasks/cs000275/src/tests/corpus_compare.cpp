#include "RosettaStone.h"

bool operator< (const Corpus& lhs, const Corpus& rhs) {
    return lhs.name < rhs.name;
}
