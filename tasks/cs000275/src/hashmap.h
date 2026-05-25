#ifndef HASHMAP_H_INCLUDED
#define HASHMAP_H_INCLUDED

#include <unordered_map>

template <typename Key, typename Value>
using HashMap = std::unordered_map<Key, Value>;

#endif
