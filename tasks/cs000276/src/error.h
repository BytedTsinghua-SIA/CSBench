#ifndef ERROR_H_INCLUDED
#define ERROR_H_INCLUDED

#include <stdexcept>
#include <string>

class ErrorException : public std::runtime_error {
public:
    explicit ErrorException(const std::string& message)
        : std::runtime_error(message) {}
};

[[noreturn]] inline void error(const std::string& message) {
    throw ErrorException(message);
}

[[noreturn]] inline void error(const char* message) {
    throw ErrorException(message ? std::string(message) : std::string());
}

#endif
