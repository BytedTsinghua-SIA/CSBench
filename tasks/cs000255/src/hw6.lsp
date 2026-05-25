;
; CS161 Spring 2020 HW6 Problem 3: Graph coloring to SAT conversion
;
; All functions you need to write are marked with 'EXERCISE' in their header comments.
;

;;;;;;;;;;;;;;;;;;;;;;
; General util.
;
(defun reload()
  (load "hw6.lsp")
)

; EXERCISE
; returns the index of the variable
; that corresponds to the fact that
; "node n gets color c" (when there are k possible colors).
;
(defun node2var (n c k)
  ;; TODO: implement
  NIL
)

; EXERCISE
; returns *a clause* for the constraint:
; "node n gets at least one color from the set {c,c+1,...,k}."
;
(defun at-least-one-color (n c k)
  ;; TODO: implement
  NIL
)

; EXERCISE
; returns *a list of clauses* for the constraint:
; "node n gets at most one color from the set {c,c+1,...,k}."
;
(defun at-most-one-color (n c k)
  ;; TODO: implement
  NIL
)

(defun dual (L)
  (if (null L) NIL
    (cons (* -1 (first L)) (dual (rest L)))))

(defun get-all-pairs (L)
  (if (= (length L) 1) NIL
    (append (get-pairs (first L) (rest L))
            (get-all-pairs (rest L)))))

(defun get-pairs (e L)
  (if (null L) NIL
    (cons (list e (first L))
          (get-pairs e (rest L)))))

; EXERCISE
; returns *a list of clauses* to ensure that
; "node n gets exactly one color from the set {1,2,...,k}."
;
(defun generate-node-clauses (n k)
  ;; TODO: implement
  NIL
)

; EXERCISE
; returns *a list of clauses* to ensure that
; "the nodes at both ends of edge e cannot have the same color
;  from the set {1,2,...,k}."
;
(defun generate-edge-clauses (e k)
  ;; TODO: implement
  NIL
)

(defun collapse (list1 list2)
  (if (or (null list1) (null list2)) NIL
    (cons (list (first list1) (first list2))
          (collapse (rest list1) (rest list2)))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; Your exercises end here. Below are top-level
; and utility functions that you do not need to understand.
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(defun graph-coloring-to-sat (fname out-name k)
  (progn
    (setf in-path (make-pathname :name fname))
    (setf in (open in-path :direction :input))
    (setq info (get-number-pair-from-string (read-line in) #\ ))
    (setq cnf nil)

    (do ((node 1 (+ node 1)))
        ((> node (car info)))
      (setq cnf (append (generate-node-clauses node k) cnf)))

    (do ((line (read-line in nil 'eof)
               (read-line in nil 'eof)))
        ((eql line 'eof) (close in))
      (let ((edge (get-number-pair-from-string line #\ )))
        (setq cnf (append (generate-edge-clauses edge k) cnf))))

    (close in)
    (write-cnf-to-file out-name (* (car info) k) cnf)
    cnf
  )
)

(defun get-number-pair-from-string (string token)
  (if (and string token)
      (do* ((delim-list (if (and token (listp token)) token (list token)))
            (char-list (coerce string 'list))
            (limit (list-length char-list))
            (char-count 0 (+ 1 char-count))
            (char (car char-list) (nth char-count char-list)))
           ((or (member char delim-list)
                (= char-count limit))
            (return
             (if (= char-count limit)
                 (list string nil)
                 (list
                  (parse-integer
                   (coerce (butlast char-list (- limit char-count)) 'string))
                  (parse-integer
                   (coerce (nthcdr (+ char-count 1) char-list) 'string))))))))

(defun write-clause-to-file (out clause)
  (cond ((null clause) (format out "0~%"))
        (t (progn
             (format out "~A " (car clause))
             (write-clause-to-file out (cdr clause))))))

(defun write-cnf-to-file (fname vc cnf)
  (progn
    (setf path (make-pathname :name fname))
    (setf out (open path :direction :output))
    (setq cc (length cnf))
    (format out "p cnf ~A ~A~%" vc cc)
    (dolist (clause cnf)
      (write-clause-to-file out clause))
    (close out)))
