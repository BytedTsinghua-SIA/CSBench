#include "Shift.h"
#include <functional>
#include <ostream>
#include <sstream>
using namespace std;

namespace {
    int dayValue(Day day) {
        return static_cast<int>(day);
    }
}

bool operator< (const Shift& lhs, const Shift& rhs) {
    if (lhs.day != rhs.day) return dayValue(lhs.day) < dayValue(rhs.day);
    if (lhs.startHour != rhs.startHour) return lhs.startHour < rhs.startHour;
    if (lhs.endHour != rhs.endHour) return lhs.endHour < rhs.endHour;
    return lhs.value < rhs.value;
}

bool operator== (const Shift& lhs, const Shift& rhs) {
    return lhs.day == rhs.day &&
           lhs.startHour == rhs.startHour &&
           lhs.endHour == rhs.endHour &&
           lhs.value == rhs.value;
}

bool overlapsWith(const Shift& one, const Shift& two) {
    return one.day == two.day &&
           ((one.startHour <= two.startHour && two.startHour < one.endHour) ||
            (two.startHour <= one.startHour && one.startHour < two.endHour));
}

int lengthOf(const Shift& shift) {
    return shift.endHour - shift.startHour;
}

int valueOf(const Shift& shift) {
    return shift.value;
}

int hashCode(const Shift& shift) {
    size_t seed = 0;
    auto hashCombine = [&seed](size_t value) {
        seed ^= value + 0x9e3779b9 + (seed << 6) + (seed >> 2);
    };

    hashCombine(std::hash<int>{}(dayValue(shift.day)));
    hashCombine(std::hash<int>{}(shift.startHour));
    hashCombine(std::hash<int>{}(shift.endHour));
    hashCombine(std::hash<int>{}(shift.value));

    return static_cast<int>(seed);
}

ostream& operator<< (ostream& out, Day day) {
    switch (day) {
    case Day::SUNDAY:    return out << "Sunday";
    case Day::MONDAY:    return out << "Monday";
    case Day::TUESDAY:   return out << "Tuesday";
    case Day::WEDNESDAY: return out << "Wednesday";
    case Day::THURSDAY:  return out << "Thursday";
    case Day::FRIDAY:    return out << "Friday";
    case Day::SATURDAY:  return out << "Saturday";
    default:             return out << "(unknown day)";
    }
}

ostream& operator<< (ostream& out, const Shift& shift) {
    ostringstream builder;
    builder << "{ " << shift.day << ", "
            << shift.startHour << "-" << shift.endHour
            << ", value " << shift.value << " }";
    return out << builder.str();
}
