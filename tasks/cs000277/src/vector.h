#ifndef VECTOR_H_INCLUDED
#define VECTOR_H_INCLUDED

#include <initializer_list>
#include <ostream>
#include <utility>
#include <vector>

template <typename T>
class Vector {
public:
    using iterator = typename std::vector<T>::iterator;
    using const_iterator = typename std::vector<T>::const_iterator;

    Vector() = default;
    Vector(std::initializer_list<T> init) : data_(init) {}

    std::size_t size() const { return data_.size(); }
    bool isEmpty() const { return data_.empty(); }

    T& operator[](std::size_t index) { return data_[index]; }
    const T& operator[](std::size_t index) const { return data_[index]; }

    iterator begin() { return data_.begin(); }
    const_iterator begin() const { return data_.begin(); }
    iterator end() { return data_.end(); }
    const_iterator end() const { return data_.end(); }

    void add(const T& value) { data_.push_back(value); }
    void add(T&& value) { data_.push_back(std::move(value)); }

    Vector& operator+=(const T& value) {
        data_.push_back(value);
        return *this;
    }

    Vector& operator+=(T&& value) {
        data_.push_back(std::move(value));
        return *this;
    }

    Vector& operator+=(const Vector& other) {
        data_.insert(data_.end(), other.data_.begin(), other.data_.end());
        return *this;
    }

    bool operator==(const Vector& other) const {
        return data_ == other.data_;
    }

    bool operator!=(const Vector& other) const {
        return !(*this == other);
    }

private:
    std::vector<T> data_;
};

template <typename T>
std::ostream& operator<<(std::ostream& out, const Vector<T>& vec) {
    out << "{";
    for (std::size_t i = 0; i < vec.size(); i++) {
        if (i != 0) out << ", ";
        out << vec[i];
    }
    out << "}";
    return out;
}

#endif
