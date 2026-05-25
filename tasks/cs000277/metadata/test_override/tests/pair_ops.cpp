#include "Matchmaker.h"
#include <ostream>

std::ostream& operator<< (std::ostream& out, const Pair& pair) {
    return out << "{" << pair.first() << ", " << pair.second() << "}";
}
