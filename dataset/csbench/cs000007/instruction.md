## Background (Excerpts from Assignment 1 Handout)

This assignment is first and foremost a low-level systems programming assignment, but it’s also an opportunity to review your C++ while simultaneously exercising your software engineering and low-level memory manipulation skills. You’ll also get to see that low-level C coding and high-level C++ data structuring can coexist in the same application.

The assignment is based on the "Six Degrees of Kevin Bacon" parlor game. The game takes the form of a trivia challenge: propose two actor names, and you must come up with a sequence of movies and mutual co-stars connecting the two. In this case, your opponent takes on the form of an executable, and that executable is shockingly good.

For example:
```
poohbear@myth10$ ./search "Meryl Streep" "Jack Nicholson (I)"
Meryl Streep was in "Heartburn" (1986) with Jack Nicholson (I).
```

A more complex example:
```
poohbear@myth10$ ./search "Mary Tyler Moore" "Red Buttons"
Mary Tyler Moore was in "Change of Habit" (1969) with Regis Toomey.
Regis Toomey was in "C.H.O.M.P.S" (1979) with Red Buttons.
```

There are two major components to this assignment:
*   You need to provide the implementation for an `imdb` class, which allows you to determine who appeared in what. You’ll tap your sophisticated understanding of data representation and learn about memory mapping in order to look up movie and actor information from a prepared data structure that’s been saved to disk in its binary form.
*   You also need to implement a breadth-first search algorithm that consults your `imdb` class to find the shortest path connecting any two actor/actresses.

---

### Task I: The `imdb` class

First, you must complete the implementation of the `imdb` class. Here’s the reduced interface from `imdb.h`:

```cpp
class imdb {
public:
  imdb(const string& directory);
  bool good() const;
  bool getCredits(const string& player, vector<film>& films) const;
  bool getCast(const film& movie, vector<string>& players) const;
  ~imdb();
private:
  const void *actorFile;
  const void *movieFile;
};

struct film {
  string title;
  int year;
};
```

The constructor and destructor, which use `mmap` to handle memory-mapped files, are already implemented for you. Your task is to implement the `getCredits` and `getCast` methods by manually crawling over these binary images to produce vectors of movies and actor names.

The private `actorFile` and `movieFile` fields each address gigantic blocks of memory, which are pointers to database images.

#### Data File Format

The data files are structured to allow for fast binary searching. An array of integer offsets is stored at the beginning of each file, followed by the actual records.

*   **`actorFile`**:
    1.  `int`: number of actors.
    2.  `int[]`: array of offsets to each actor record.
    3.  `actor_records[]`: The actual actor records, sorted by name.

*   **`movieFile`**:
    1.  `int`: number of movies.
    2.  `int[]`: array of offsets to each movie record.
    3.  `movie_records[]`: The actual movie records, sorted by title and then year.

You must use the STL `lower_bound` algorithm with a C++11 lambda function to perform binary searches on these offsets.

#### Actor Record Format

Each actor record is of variable size and contains:
1.  The actor's name as a null-terminated C-string. Padded with an extra `\0` if the name length is even.
2.  A `short` (2 bytes) for the number of movies they appeared in. Padded to a 4-byte boundary if necessary.
3.  An array of `int` offsets into the `movieFile`.

#### Movie Record Format

Each movie record is also of variable size:
1.  The movie title as a null-terminated C-string.
2.  A single `byte` for the year of release (as an offset from 1900). Padded with an extra `\0` if the total bytes so far is odd.
3.  A `short` (2 bytes) for the number of actors in the film. Padded to a 4-byte boundary if necessary.
4.  An array of `int` offsets into the `actorFile`.

---

### Task II: Implementing Search

With a working `imdb` class, you will implement a breadth-first search (BFS) to find the shortest path between two actors in `search.cc`.

Leverage STL containers as much as possible:
*   `vector`: Required by the `imdb` class interface.
*   `list` or `queue`: To manage the nodes to visit in your BFS.
*   `set`: To keep track of previously visited actors and films to avoid cycles and redundant work.

You will use the provided `path` class to construct and store the path as you find it. If a path search becomes too long (length 7 or more), you can assume no path exists.

---

### Provided Files

*   `imdb-utils.h`: Defines the `film` struct. Do not modify.
*   `imdb.h`: The interface for the `imdb` class. Do not modify the public interface.
*   `imdb.cc`: **Implement `getCast` and `getCredits` here.**
*   `imdbtest.cc`: A test harness to exercise your `imdb` class. Do not modify.
*   `search.cc`: **Implement your BFS algorithm here.**
*   `path.h` / `path.cc`: The `path` class. You can add to it if needed.
*   `Makefile`: Used to build your executables. Do not modify.

---

## Special reminders for this repository

*   To test your `imdb` class implementation, build and run the test harness:
    ```bash
    make imdbtest
    ./imdbtest
    ```
*   To build the main `search` application:
    ```bash
    make search
    ```
*   Run your search program like this:
    ```bash
    ./search "Actor Name 1" "Actor Name 2"
    ```
*   You can compare your results against the solution executable:
    ```bash
    ./slink/search_soln "Actor Name 1" "Actor Name 2"
    ```
    Your solution does not need to produce the *exact* same path, but the path *lengths* must match.
*   Ensure your code is free of memory leaks and errors. We will use `valgrind` for grading.