#ifndef STRLIB_H_INCLUDED
#define STRLIB_H_INCLUDED

#include "error.h"
#include "random.h"
#include "vector.h"
#include <cctype>
#include <string>

inline std::string toLowerCase(const std::string& input) {
    std::string result = input;
    for (char& ch : result) {
        ch = static_cast<char>(std::tolower(static_cast<unsigned char>(ch)));
    }
    return result;
}

inline std::string toUpperCase(const std::string& input) {
    std::string result = input;
    for (char& ch : result) {
        ch = static_cast<char>(std::toupper(static_cast<unsigned char>(ch)));
    }
    return result;
}

inline bool startsWith(const std::string& text, const std::string& prefix) {
    return text.size() >= prefix.size() && text.compare(0, prefix.size(), prefix) == 0;
}

inline Vector<std::string> stringSplit(const std::string& input, const std::string& delimiter) {
    Vector<std::string> result;
    if (delimiter.empty()) {
        result += input;
        return result;
    }

    std::size_t start = 0;
    while (start <= input.size()) {
        std::size_t pos = input.find(delimiter, start);
        if (pos == std::string::npos) {
            std::string token = input.substr(start);
            if (!token.empty()) result += token;
            break;
        }

        std::string token = input.substr(start, pos - start);
        if (!token.empty()) result += token;
        start = pos + delimiter.size();
    }

    return result;
}

inline double stringToDouble(const std::string& input) {
    try {
        std::size_t idx = 0;
        double value = std::stod(input, &idx);
        if (idx != input.size()) {
            error("stringToDouble: invalid trailing characters");
        }
        return value;
    } catch (const std::exception&) {
        error("stringToDouble: invalid number");
    }
}

inline double stringToReal(const std::string& input) {
    return stringToDouble(input);
}

inline int stringToInteger(const std::string& input, int base) {
    try {
        std::size_t idx = 0;
        int value = std::stoi(input, &idx, base);
        if (idx != input.size()) {
            error("stringToInteger: invalid trailing characters");
        }
        return value;
    } catch (const std::exception&) {
        error("stringToInteger: invalid number");
    }
}

inline int stringToInteger(const std::string& input) {
    return stringToInteger(input, 10);
}

inline int stringToInt(const std::string& input) {
    return stringToInteger(input, 10);
}

#endif
