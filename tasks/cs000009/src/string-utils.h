/**
 * File: string-utils.h
 * ---------------------
 * Minimal, header-only string utility functions used by the codebase.
 * Provides trim and startsWith to avoid external dependencies.
 */

#pragma once

#include <string>
#include <algorithm>
#include <cctype>

namespace strutils {
  inline bool startsWith(const std::string& s, const std::string& prefix) {
    return s.size() >= prefix.size() && s.compare(0, prefix.size(), prefix) == 0;
  }

  inline std::string trim(const std::string& s) {
    auto is_space = [](unsigned char ch) { return std::isspace(ch) != 0; };
    auto begin = std::find_if_not(s.begin(), s.end(), is_space);
    auto end = std::find_if_not(s.rbegin(), s.rend(), is_space).base();
    if (begin >= end) return std::string();
    return std::string(begin, end);
  }
}

// Provide un-namespaced helpers to match existing usage.
inline bool startsWith(const std::string& s, const std::string& prefix) {
  return strutils::startsWith(s, prefix);
}

inline std::string trim(const std::string& s) {
  return strutils::trim(s);
}

