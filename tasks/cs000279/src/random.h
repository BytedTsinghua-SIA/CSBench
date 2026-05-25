#ifndef RANDOM_H_INCLUDED
#define RANDOM_H_INCLUDED

#include <random>
#include <utility>

inline int randomInteger(int low, int high) {
    if (low > high) {
        std::swap(low, high);
    }
    static std::mt19937 rng(std::random_device{}());
    std::uniform_int_distribution<int> dist(low, high);
    return dist(rng);
}

inline double randomReal(double low, double high) {
    if (low > high) {
        std::swap(low, high);
    }
    static std::mt19937 rng(std::random_device{}());
    std::uniform_real_distribution<double> dist(low, high);
    return dist(rng);
}

#endif
