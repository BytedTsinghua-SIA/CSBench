#ifndef SET_H_INCLUDED
#define SET_H_INCLUDED

#include <initializer_list>
#include <ostream>
#include <set>

template <typename T>
class Set {
public:
    using iterator = typename std::set<T>::iterator;
    using const_iterator = typename std::set<T>::const_iterator;

    Set() = default;
    Set(std::initializer_list<T> init) : data_(init) {}

    std::size_t size() const { return data_.size(); }
    bool isEmpty() const { return data_.empty(); }

    bool contains(const T& value) const { return data_.find(value) != data_.end(); }

    void add(const T& value) { data_.insert(value); }

    iterator begin() { return data_.begin(); }
    const_iterator begin() const { return data_.begin(); }
    iterator end() { return data_.end(); }
    const_iterator end() const { return data_.end(); }

    bool operator==(const Set& other) const { return data_ == other.data_; }
    bool operator!=(const Set& other) const { return !(*this == other); }

private:
    std::set<T> data_;
};

template <typename T>
std::ostream& operator<<(std::ostream& out, const Set<T>& set) {
    out << "{";
    bool first = true;
    for (const auto& value : set) {
        if (!first) out << ", ";
        first = false;
        out << value;
    }
    out << "}";
    return out;
}

#endif
