; BFS takes a single argument, a list representing a tree where a leaf is
; represented as an atom and a non-leaf is represented by a list of its
; child nodes.  If the list is empty, it returns an empty list.  It inspects
; the head; if it is an atom, append it to the front of a recursive call on
; the rest of the list.  If not, move it to the back of the list (appending
; it will unwrap it by one level, so it approaches the base case). By iterating
; as such, each level in the tree is represented by one pair of parentheses,
; so we traverse left-to-right by level
(defun bfs (L)
  ; TODO: Implement breadth-first search traversal
  )

; DFS functions much like BFS, except that an atom is appended to the front
; of the return value of the recursive call, and that when we move a sublist
; to the back of the list, we make a recursive call on that as well.  By
; doing so, we dive into the right first, and traverse depths right-to-left
(defun dfs (L)
  ; TODO: Implement depth-first search traversal
  )

; DLDFS takes two arguments: a list of the same format as above and a maximum
; depth to search is a depth-limited depth first search.  If the depth is zero,
; or if the list is empty, it returns an empty list. If the first item is an
; atom, it appends that to the front of a recursive call on the rest of the
; list.  Otherwise, it calls itself with a decremented depth and appends
; that to a recursive call on the rest of the list
(defun dldfs (L depth)
  ; TODO: Implement depth-limited depth-first search
  )

; DFID takes two arguments: a list of the format above and a maximum depth
; to iterate toward when searching.  It is a depth first iterative deepening
; search that returns an empty list if the depth is zero, and otherwise
; appends a DLDFS call with the passed depth to the back of a recursive call
; with a decremented depth.
(defun dfid (L depth)
  ; TODO: Implement depth-first iterative deepening search
  )


; MISSIONARY AND CANNIBAL PROBLEM SOLUTION BELOW

; FINAL-STATE takes a single argument s, the current state, and returns T if it
; is the goal state (3 3 NIL) and NIL otherwise. It does this by direct
; comparison to the hard-coded final state
(defun final-state (s)
  ; TODO: Implement final state check for (3 3 NIL)
  )

; NEXT-STATE returns the state that results from applying an operator to the
; current state. It takes three arguments: the current state (s), a number of
; missionaries to move (m), and a number of cannibals to move (c). It returns a
; list containing the state that results from moving that number of missionaries
; and cannibals from the current side of the river to the other side of the
; river. If applying this operator results in an invalid state (because there
; are more cannibals than missionaries on either side of the river, or because
; it would move more missionaries or cannibals than are on this side of the
; river) it returns NIL.
(defun next-state (s m c)
  ; TODO: Implement next state generation with validation
  )

; SUCC-FN returns all of the possible legal successor states to the current
; state. It takes a single argument (s), which encodes the current state, and
; returns a list of each state that can be reached by applying legal operators
; to the current state.
(defun succ-fn (s)
  ; TODO: Implement successor function that returns all legal moves
  )

; ON-PATH checks whether the current state is on the stack of states visited by
; this depth-first search. It takes two arguments: the current state (s) and the
; stack of states visited by MC-DFS (states). It returns T if s is a member of
; states and NIL otherwise.
(defun on-path (s states)
  ; TODO: Implement path membership check
  )

; MULT-DFS is a helper function for MC-DFS. It takes two arguments: a stack of
; states from the initial state to the current state (path), and the legal
; successor states from the current state (states).
; MULT-DFS does a depth-first search on each element of states in
; turn. If any of those searches reaches the final state, MULT-DFS returns the
; complete path from the initial state to the goal state. Otherwise, it returns
; NIL.
(defun mult-dfs (states path)
  ; TODO: Implement multiple DFS helper function
  )

; MC-DFS does a depth first search from a given state to the goal state. It
; takes two arguments: a state (S) and the path from the initial state to S
; (PATH). If S is the initial state in our search, PATH should be NIL. MC-DFS
; performs a depth-first search starting at the given state. It returns the path
; from the initial state to the goal state, if any, or NIL otherwise. MC-DFS is
; responsible for checking if S is already the goal state, as well as for
; ensuring that the depth-first search does not revisit a node already on the
; search path.
(defun mc-dfs (s path)
  ; TODO: Implement depth-first search for missionary/cannibal problem
  )
