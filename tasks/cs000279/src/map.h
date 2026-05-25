#ifndef MAP_H_INCLUDED
#define MAP_H_INCLUDED

#include "error.h"
#include <cstddef>
#include <initializer_list>
#include <iterator>
#include <map>
#include <ostream>
#include <utility>

template <typename Key, typename Value>
class Map {
public:
    class KeyIterator {
    public:
        using iterator_category = std::forward_iterator_tag;
        using value_type = Key;
        using difference_type = std::ptrdiff_t;
        using pointer = const Key*;
        using reference = const Key&;

        KeyIterator() = default;
        explicit KeyIterator(typename std::map<Key, Value>::const_iterator it) : it_(it) {}

        reference operator*() const { return it_->first; }
        pointer operator->() const { return &it_->first; }

        KeyIterator& operator++() {
            ++it_;
            return *this;
        }

        KeyIterator operator++(int) {
            KeyIterator temp(*this);
            ++it_;
            return temp;
        }

        bool operator==(const KeyIterator& other) const { return it_ == other.it_; }
        bool operator!=(const KeyIterator& other) const { return it_ != other.it_; }

    private:
        typename std::map<Key, Value>::const_iterator it_;
    };

    Map() = default;

    Map(std::initializer_list<std::pair<const Key, Value>> init) : data_(init) {}

    std::size_t size() const { return data_.size(); }
    bool isEmpty() const { return data_.empty(); }

    bool containsKey(const Key& key) const { return data_.find(key) != data_.end(); }

    Value& operator[](const Key& key) { return data_[key]; }

    const Value& operator[](const Key& key) const {
        auto it = data_.find(key);
        if (it == data_.end()) {
            error("Map: key not found");
        }
        return it->second;
    }

    KeyIterator begin() const { return KeyIterator(data_.begin()); }
    KeyIterator end() const { return KeyIterator(data_.end()); }

    bool operator==(const Map& other) const { return data_ == other.data_; }
    bool operator!=(const Map& other) const { return !(*this == other); }

private:
    std::map<Key, Value> data_;
};

template <typename Key, typename Value>
std::ostream& operator<<(std::ostream& out, const Map<Key, Value>& map) {
    out << "{";
    bool first = true;
    for (const auto& key : map) {
        if (!first) out << ", ";
        first = false;
        out << key << ": " << map[key];
    }
    out << "}";
    return out;
}

#endif
