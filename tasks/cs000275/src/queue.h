#ifndef QUEUE_H_INCLUDED
#define QUEUE_H_INCLUDED

#include "error.h"
#include <deque>

template <typename T>
class Queue {
public:
    void enqueue(const T& value) {
        data_.push_back(value);
    }

    T dequeue() {
        if (data_.empty()) {
            error("Queue: dequeue from empty queue");
        }
        T value = data_.front();
        data_.pop_front();
        return value;
    }

    bool isEmpty() const { return data_.empty(); }

    std::size_t size() const { return data_.size(); }

private:
    std::deque<T> data_;
};

#endif
