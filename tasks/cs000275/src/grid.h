#ifndef GRID_H_INCLUDED
#define GRID_H_INCLUDED

#include <initializer_list>
#include <ostream>
#include <vector>

struct GridLocation {
    int row;
    int col;
};

template <typename T>
class Grid {
public:
    Grid() = default;

    Grid(int rows, int cols, const T& value = T()) {
        if (rows < 0 || cols < 0) {
            rows = 0;
            cols = 0;
        }
        rows_.assign(static_cast<std::size_t>(rows), std::vector<T>(static_cast<std::size_t>(cols), value));
    }

    Grid(std::initializer_list<std::initializer_list<T>> init) {
        for (const auto& row : init) {
            rows_.emplace_back(row);
        }
    }

    int numRows() const {
        return static_cast<int>(rows_.size());
    }

    int numCols() const {
        return rows_.empty() ? 0 : static_cast<int>(rows_[0].size());
    }

    bool inBounds(int row, int col) const {
        return row >= 0 && col >= 0 && row < numRows() && col < numCols();
    }

    bool inBounds(const GridLocation& loc) const {
        return inBounds(loc.row, loc.col);
    }

    std::vector<T>& operator[](int row) {
        return rows_[static_cast<std::size_t>(row)];
    }

    const std::vector<T>& operator[](int row) const {
        return rows_[static_cast<std::size_t>(row)];
    }

    T get(int row, int col) const {
        return rows_[static_cast<std::size_t>(row)][static_cast<std::size_t>(col)];
    }

    T get(const GridLocation& loc) const {
        return get(loc.row, loc.col);
    }

    void set(int row, int col, const T& value) {
        rows_[static_cast<std::size_t>(row)][static_cast<std::size_t>(col)] = value;
    }

    void set(const GridLocation& loc, const T& value) {
        set(loc.row, loc.col, value);
    }

    bool operator==(const Grid& other) const {
        return rows_ == other.rows_;
    }

    bool operator!=(const Grid& other) const {
        return !(*this == other);
    }

private:
    std::vector<std::vector<T>> rows_;
};

template <typename T>
std::ostream& operator<<(std::ostream& out, const Grid<T>& grid) {
    out << "{";
    for (int r = 0; r < grid.numRows(); r++) {
        if (r != 0) out << ", ";
        out << "{";
        for (int c = 0; c < grid.numCols(); c++) {
            if (c != 0) out << ", ";
            out << grid[r][c];
        }
        out << "}";
    }
    out << "}";
    return out;
}

#endif
