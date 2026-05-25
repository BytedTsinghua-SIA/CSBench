#ifndef PRIORITYQUEUE_H_INCLUDED
#define PRIORITYQUEUE_H_INCLUDED

#include "error.h"
#include <queue>
#include <vector>

template <typename T>
class PriorityQueue {
public:
    void enqueue(const T& value, double priority) {
        data_.push(Node{priority, nextOrder_++, value});
    }

    T dequeue() {
        if (data_.empty()) {
            error("PriorityQueue: dequeue from empty queue");
        }
        T value = data_.top().value;
        data_.pop();
        return value;
    }

    bool isEmpty() const { return data_.empty(); }

    std::size_t size() const { return data_.size(); }

private:
    struct Node {
        double priority;
        std::size_t order;
        T value;
    };

    struct Compare {
        bool operator()(const Node& lhs, const Node& rhs) const {
            if (lhs.priority != rhs.priority) {
                return lhs.priority > rhs.priority;
            }
            return lhs.order > rhs.order;
        }
    };

    std::priority_queue<Node, std::vector<Node>, Compare> data_;
    std::size_t nextOrder_ = 0;
};

#endif
