#include "string-utils.h"

#include <cctype>

static inline bool isSpace(char c) {
  return std::isspace(static_cast<unsigned char>(c)) != 0;
}

std::string& trim(std::string& s) {
  size_t start = 0;
  while (start < s.size() && isSpace(s[start])) start++;
  size_t end = s.size();
  while (end > start && isSpace(s[end - 1])) end--;
  if (start == 0 && end == s.size()) return s;
  s.assign(s.substr(start, end - start));
  return s;
}


