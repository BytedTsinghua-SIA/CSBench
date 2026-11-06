## Background (Excerpts from CS431 Course Materials)

This repository contains homework assignments for CS431 Concurrent Programming. You will implement various concurrent data structures and systems using Rust. The assignments cover topics from basic thread pools to advanced lock-free data structures and memory reclamation techniques.

Outcomes you will gain from these labs include:
*   You will gain a deeper understanding of Rust's concurrency primitives (Threads, Arc, Mutex, Channels).
*   You will learn how to use unsafe Rust and raw pointers to implement low-level data structures.
*   You will gain experience implementing fine-grained locking and lock-free data structures.
*   You will understand memory models and synchronization primitives (SeqCst, Acquire/Release).
*   You will gain experience with tools like Loom (model checker), AddressSanitizer, and ThreadSanitizer.

Note: In this course, you will build concurrent systems from scratch. Our purpose is to help you learn about the runtime operation of concurrent programs and to understand the nature of data races and memory safety so that you can write robust system code.

---

### Phase 1: Parallel web server with cache

#### Expected outcome

- Execute `cargo run --features="build-bin" hello_server`. A web server should run.
- Run `curl http://localhost:7878/alice`. It should wait for a few seconds, and return a web page.
- Run `curl http://localhost:7878/alice` again. It should instantly return a web page.
- Run `curl http://localhost:7878/bob`. It should wait for a few seconds, and return a web page.
- Press `Ctrl-C`. The web server should gracefully shut down after printing statistics.

#### Guide

##### Reading Rust book
This homework requires a good understanding of the materials covered in [the Rust book §20](https://doc.rust-lang.org/book/ch20-00-final-project-a-web-server.html).
This is the minimal path for understanding §20: §1, 2, 3, 4, 5, 6, 8, 9, 10, 13.1, 13.2, **15**, **16**, **20**.

Specifically, make sure that you understand the following topics.
* [`Drop`](https://doc.rust-lang.org/std/ops/trait.Drop.html) trait and [`drop`](https://doc.rust-lang.org/std/mem/fn.drop.html) function
* Type signature of [`std::thread::spawn`](https://doc.rust-lang.org/std/thread/fn.spawn.html) and the meaning of [`std::thread::JoinHandle`](https://doc.rust-lang.org/std/thread/struct.JoinHandle.html).
* The meaning and usage of [`Arc<`](https://doc.rust-lang.org/std/sync/struct.Arc.html)[`Mutex<T>>`](https://doc.rust-lang.org/std/sync/struct.Mutex.html).
* [Channels](https://doc.rust-lang.org/std/sync/mpsc/index.html).
<!-- * The fact that there is no non-trivial way to break out of `TcpListener::incoming` loop. -->

See also: Rust book with quiz. <https://rust-book.cs.brown.edu/>

##### Major differences between HW1 thread pool and Rust book §20 thread pool
1. We use [`crossbeam_channel`](https://docs.rs/crossbeam-channel/) instead of [<code>std::sync::<strong>mpsc</strong></code>](https://doc.rust-lang.org/std/sync/mpsc/index.html). Since crossbeam's channels are **mpmc**, you don't need to wrap the `Receiver` inside a `Mutex`.
1. We do not use explicit exit messages for the thread pool. Instead, we disconnect the channel by `drop`ping the receiver/sender.
    * Our message type is simply the `Job` itself:
      ```rust
      struct Job(Box<dyn FnOnce() + Send + 'static>);
      ```
    * Each worker thread automatically breaks out of the loop if the channel is disconnected.
1. We `join()` each thread in the destructor of `Worker`, not in the destructor of `ThreadPool`. Since `ThreadPool` has field `workers: Vec<Worker>`, the worker destructor will be called when the pool is dropped. Note that the channel should be disconnected before `join()`ning the worker threads. (Otherwise, `join` will block.) This means that the `Sender` should be dropped before `Vec<Worker>`. You can specify the drop order in many ways. In this homework, we use `ThreadPool::job_sender` of type `Option<Sender<Job>>`, whose content can be `take()`n and `drop()`ped explicitly in `<ThreadPool as Drop>::drop`.

##### Tips
* Cache: Start with `Mutex<HashMap<K, V>>`. To fully implement the specification, you will need a more complicated type. The simplest solution makes use of all the things imported in `cache.rs`.
* Interrupt handler: just follow the comments.
* Thread pool: Ignore `ThreadPoolInner` first (it's used for `ThreadPool::join`), and implement the changes discussed above.
* If you have questions, try looking up the [issue tracker](https://github.com/kaist-cp/cs431/issues).
  There are many Q&A's from the previous iterations of this course, and they are labeled by the topic.
  For example, ["homework - cache" label](https://github.com/kaist-cp/cs431/issues?q=label%3A%22homework+-+cache%22+) lists the questions about `cache.rs`.
  Here are some Q&A's you may find useful for this homework:
    * https://github.com/kaist-cp/cs431/issues/339
    * https://github.com/kaist-cp/cs431/issues/85#issuecomment-696888546
    * https://github.com/kaist-cp/cs431/issues/81

---

### Phase 2: Doubly linked list
**Implement doubly linked list in unsafe Rust.**

This homework serves as a brief tutorial for unsafe Rust with a focus on the basic raw pointer operations.

The skeleton code `linked_list.rs` is slightly modified version of [the linked list from Rust standard library](https://doc.rust-lang.org/std/collections/struct.LinkedList.html).
We already provided implementation for several methods e.g. `push_front_node`.
Your job is to implement their symmetric counterparts
e.g. `push_back_node` and some methods of `IterMut` struct (see `todo!()`s).

You can look up its implementation from the standard library,
but we encourage you do it yourself
so that you can build enough skill set for upcoming homeworks.
We also recommend you to play around with AddressSanitizer and debugger.

#### Guide

##### Learn the basics of unsafe Rust
1. Read [Rust Book §19.1](https://doc.rust-lang.org/book/ch19-01-unsafe-rust.html)
1. Skim through [Nomicon §1](https://doc.rust-lang.org/nomicon/meet-safe-and-unsafe.html)
1. Read [raw pointer type documentation](https://doc.rust-lang.org/std/primitive.pointer.html) and some of its methods (`is_null`, `as_ref`, `read`, `write`, `replace`, `swap`)
1. Read [`std::mem`](https://doc.rust-lang.org/std/mem/index.html) and [`std::ptr`](https://doc.rust-lang.org/std/ptr/index.html) documentations.
1. Read [`std::iter`](https://doc.rust-lang.org/std/iter/index.html) documentation.

##### Tips for debugging
When `cargo test` fails with error messages like this,
```
thread panicked while panicking. aborting.
error: test failed, to rerun pass '--test linked_list'

Caused by:
  process didn't exit successfully: ... (signal: 4, SIGILL: illegal instruction)
```
try running the test like this
<pre>
cargo test --test linked_list <strong>-- --nocapture --test-threads 1</strong>
</pre>
This will give you more informative error messages.

##### Other useful resources
* [`*` operator](https://doc.rust-lang.org/stable/reference/expressions/operator-expr.html#the-dereference-operator)
* [`.` operator](https://doc.rust-lang.org/stable/reference/expressions/call-expr.html)
* [type coercion (weakening)](https://doc.rust-lang.org/nomicon/coercions.html)
* [type casting](https://doc.rust-lang.org/nomicon/casts.html)
* [`Box<T>` is special](https://doc.rust-lang.org/stable/reference/special-types-and-traits.html#boxt)
* [`*const T` vs. `*mut T`](https://internals.rust-lang.org/t/what-is-the-real-difference-between-const-t-and-mut-t-raw-pointers/6127)

---

### Phase 3: Concurrent set based on Lock-coupling linked list
**Implement concurrent set data structures with sorted singly linked list using fine-grained lock-coupling.**

Suppose you want a set data structure that supports concurrent operations.
The simplest possible approach would be taking a non-concurrent set implementation and protecting it with a global lock.
However, this is not a great idea if the set is accessed frequently because a thread's operation blocks all the other threads' operations.

In this homework, you will write an implementation of the set data structure based on singly linked list protected by fine-grained locks.
* The nodes in the list are sorted by their value, so that one can efficiently check if a value is in the set.
* Each node has its own lock that protects its `next` field.
  When traversing the list, the locks are acquired and released in the hand-over-hand manner.
  This allows multiple operations run more concurrently.

Fill in the `todo!()`s in `list_set/fine_grained.rs` (about 40 lines of code).
As in the [Linked List homework](#phase-2-doubly-linked-list), you will need to use some unsafe operations.

#### Advanced (optional)
**Note**: This is an *optional* homework, meaning that it will not be graded and not be asked in the exam.

Consider a variant of the homework that uses `SeqLock` instead of `Mutex`.
This allows read operations to run optimistically without actually locking.
Therefore, read operations are more efficient in read-most scenario, and
they do not block other operations.
However, more care must be taken to ensure correctness.
  * You need to validate read operations and handle the failure.
      * Do not use `ReadGuard::restart()`.
        Using this correctly requires some extra synchronization
        (to be covered in lock-free list lecture),
        which makes `SeqLock` somewhat pointless.
        The tests assume that `ReadGuard::restart()` is not used.
  * Since each node can be read and modified to concurrently,
    you should use atomic operations to avoid data races.
    Specifically, you will use `crossbeam_epoch`'s `Atomic<T>` type
    (instead of `std::sync::AtomicPtr<T>`, due to the next issue).
    For `Ordering`, use `SeqCst` everywhere.
    (In the later part of this course, you will learn that `Relaxed` is sufficient.
    But don't use `Relaxed` in this homework, because that would break `cargo_tsan`.)
  * Since a node can be removed while another thread is reading,
    reclamation of the node should be deferred.
    You can handle this semi-automatically with `crossbeam_epoch`.

**Instruction**: Fill in the `todo!()`s in `list_set/optimistic_fine_grained.rs` (about 80 lines of code).

---

### Phase 4: Core Arc
**Implement a simplified version of `Arc` without support for `Weak`.**

In this homework, you will practice release-acquire synchronization in weak memory
by implementing a simplified version of `Arc`.
Specifically, you will use atomic operations of `AtomicUsize`
to synchronize the accesses to the underlying data.

Fill in the `todo!()`s in `arc.rs`.
The total lines of code to be written is about 25.
The skeleton code is a heavily modified version of `Arc` from the standard library.
We don't recommend reading the original source code before finishing this homework
because that version is more complex.

#### ***2024 spring semester notice: Use `SeqCst`***
We won't cover the weak memory semantics in this semester.
So you may ignore the instructions on `Ordering` stuff below and
use `Ordering::SeqCst` for `ordering: Ordering` parameters for `std::sync::atomic` functions.

#### Guide

Follow [the Arc section of the Rustnomicon (the book on unsafe Rust)][nomicon-arc].

Some food for thought on Rustnomicon's description:
* Quiz: Why does `Arc<T> : Sync` require `T : Send`?
* The [Layout section](https://doc.rust-lang.org/nomicon/arc-mutex/arc-layout.html) explains
  why [`NonNull`](https://doc.rust-lang.org/std/ptr/struct.NonNull.html) and `PhantomData` are necessary.
  We don't care about them in this course and will not ask about them in the exams
  (it's quite interesting, though).
* Their implementation uses `fence(Acquire)`, which we may not be able cover in the lecture due to time constraints.
  You can implement (a slightly inefficient version of) Arc only with `AtomicUsize`'s methods and the concepts we covered in the lecture
  (you will need to use `Ordering::AcqRel` in some places).
  Using `fence(Acquire)` is not required in the homework and exam.
  If you want to fully understand the `fence(Acquire)` version,
  read §4 of the [Promising semantics paper](https://sf.snu.ac.kr/publications/promising.pdf).


##### Synchronization requirements of `Arc`

To ensure that data race does not occur in the implementation of Arc and the clients of Arc,
add enough synchronization operations to the Arc implementation:
* The initialization of the `ArcInner` memory block (in `new()`) happens before the accesses of its fields.
  (Guaranteeing this doesn't require extra synchronization operation in Arc. Quiz: Why?)
* Accesses to the fields of `ArcInner` happen before the deallocation of the `ArcInner` memory block (in the last `drop()`).
* Non-atomic writes to the data (via `&mut T` from `get_mut()`, `make_mut()`, `try_unwrap()`) happen after/before all the other accesses (via `&T` from `deref()`).
  More strictly, `&mut T` to the data must not concurrently coexist with `&T` (Rust's aliasing rule).

#### Other Tips
* Read
  [`sync::atomic::AtomicUsize`](https://doc.rust-lang.org/std/sync/atomic/struct.AtomicUsize.html) and
  [`sync::Ordering`](https://doc.rust-lang.org/std/sync/atomic/enum.Ordering.html).
  The semantics covered in the lectures applies to these.
* You may need to use
  [`std::mem::forget`](https://doc.rust-lang.org/std/mem/fn.forget.html)
  in `try_unwrap`.
* If the test failure message is not descriptive enough,
  try adding `-- --nocapture --test-threads 1`.

##### FAQ: AddressSanitizer reports a memory leak in my implementation.
It might be the case that
you're not deallocating the heap memory block in your `Drop` implementation.
For example, if you call functions like `drop_in_place` on `*mut ArcInner<_>`,
it only runs the destructor of `ArcInner`
without freeing the memory where that `ArcInner` lived.

The standard method to free the heap memory block is to convert the pointer
`*mut T` to `Box<T>` whose destructor runs the destructor of `T` and frees the
heap memory occupied by `T`.
For example, `pop_front_node` from HW2 uses `Box::from_raw` to convert the head
pointer into `Box<Node<_>>` and dereferences it,
moving it out of the heap to a temporary location and freeing the memory block in the heap.

For more information, see
<https://github.com/kaist-cp/cs431/issues/125>,
<https://doc.rust-lang.org/reference/destructors.html>, and
<https://doc.rust-lang.org/std/boxed/index.html>.


[nomicon-arc]: https://doc.rust-lang.org/nomicon/arc-mutex/arc.html
[ORC11]: https://plv.mpi-sws.org/rustbelt/rbrlx/

---

### Phase 5: Hazard pointers
**Implement Hazard Pointers.**

Fill in the `todo!()`s in`hazard.rs` and `retire.rs` (approx 75 lines).

This homework is in 2 parts:
1. Functionality:
   Implement hazard pointers with `Ordering::SeqCst` for every atomic access.
   With this, we can pretend that we are on a sequentially consistent memory model.
2. Performance:
   After you learn about relaxed memory semantics,
   optimize the implementation by relaxing the ordering.
   We recommend working on this part after finishing the [Arc homework](#phase-4-core-arc).

#### ***2024 spring semester notice: Part 2 is cancelled***
We won't cover the weak memory semantics in this semester.
To ensure that the grader works properly, you must use `Ordering:SeqCst` for all operations.

#### Part 1: Hazard pointers in the sequentially consistent memory model

Read [this paper](https://ieeexplore.ieee.org/document/1291819).
While this paper is sufficient for understanding Hazard Pointers,
you may also want to take a look at [WG21 P2530](https://wg21.link/p2530),
the proposal for adding Hazard Pointers to the C++ standard library.
The rest of this section summarizes the algorithm and correctness argument of hazard pointers.


Suppose a data structure has a memory block b.
A thread (T1) wants to read the value written in b and
another thread (T2) wants to remove b from the data structure and free the memory.
To prevent use-after-free,
T1 has to ensure that b is not freed before reading b and
T2 has to check that no other threads are accessing b before freeing b.
The hazard pointer library implements this mechanism as follows:

```
(T1-1) Add b to the hazard list       | (T2-1) Unlink b and `retire(b)`
       (`Shield::try_protect()`)      |
(T1-2) Check if b is still reachable  | (T2-2) Check if b is in the hazard list
       if so, deref b                 |        if not, free b
(T1-3) Remove b from the hazard list  |
       (`Shield::drop()`)             |
```

To show that the algorithm prevents use-after-free,
let's consider all possible interleavings of each step
(in the sequentially consistent memory model).

First, if `T1-3 → T2-2` (`T2-2` is executed after `T1-3`),
then b is freed after all accesses.

Second, in all the remaining cases,
either `T1-1 → T2-2` or `T2-1 → T1-2` holds
(otherwise, there is a cycle `T1-1 → T1-2 → T2-1 → T2-2 → T1-1`).
- If `T1-1 → T2-2`, then b is not freed.
- If `T2-1 → T1-2`, then the validation fails, so `T1` will not dereference b.

Therefore, the algorithm is correct in the sequentially consistent memory model.


#### Part 2: Relaxing the orderings

If you use `Ordering::Relaxed`,
the correctness argument from the previous section doesn't hold.
The problem is that in the relaxed memory model,
`→` ("executed before") doesn't imply that
the latter instruction sees the effect of the earlier instruction.
To fix this, we should add some synchronization operations
so that `→` implies "happens-before".

First, if `T2-2` saw the result of `T1-3`,
then we want to enforce `deref b @ T1` happens before `free b @ T2`
To enforce this,
it suffices to add release-acquire synchronization between `T1-3` and `T2-2`
(recall the synchronization in `Arc::drop`).

For the second case, release-acquire doesn't guarantee
"either `T1-1` happens before `T2-2` or `T2-1` happens before `T1-2`".
Because of that, `T1-2` may not read the message of `T2-1`
and `T2-2` may not read the message of `T1-2` at the same time,
leading to concurrent `deref b` and `free b`.
To make this work, we should insert an SC fence (`fence(SeqCst)`)
between `T1-1` and `T1-2`, and another between `T2-1` and `T2-2`.
<!-- This should be explained in the lecture.
Recall that an SC fence joins the executing thread's view and the global SC view.
This means that
the view of a thread after executing its SC fence
is entirely included in the view of another thread after its SC fence.
If we insert an SC fence between
`T1-1` and `T1-2`, and another between `T2-1` and `T2-2`,
then either `T1's fence ⊑ T2's fence` or `T2's fence ⊑ T1's fence` holds.
Therefore, `T1-1 ⊑ T2-2` or `T2-1 ⊑ T1-2`.
-->

---

### Phase 6: Lock-free hashtable
**Implement a lock-free hash table based on recursive split-ordered list.**

This homework is in 2 parts:
1. Functionality:
   Implement the hash table with `Ordering::SeqCst` for every atomic access.
   With this, we can pretend that we are on a sequentially consistent memory model.
2. Performance:
   After you learn about relaxed memory semantics,
   optimize the implementation by relaxing the ordering on the atomic accesses.
   We recommend working on this part after finishing the [Arc homework](#phase-4-core-arc).

#### ***2024 spring semester notice: Part 2 is cancelled***
We won't cover the weak memory semantics in this semester.

#### Part 1: Split-ordered list in sequentially consistent memory model
1. Fully understand the following reading materials.
    + [The original paper on the split-ordered list](https://dl.acm.org/doi/abs/10.1145/1147954.1147958).
      You can skip the correctness proof and performance evaluation section.
      Alternatively, read the chapter 13.3 of [The Art of Multiprocessor Programming](https://dl.acm.org/doi/book/10.5555/2385452).
      It presents the same stuff, but is more readable.
    + The [lock-free linked list](https://github.com/kaist-cp/cs431/blob/main/src/lockfree/list.rs) interface and implementation.
1. Implement `GrowableArray` in `growable_array.rs` (about 100 LOC)
    * You'll need to properly use [Rust `union`s](https://doc.rust-lang.org/reference/items/unions.html).
    * To represent the height of the segment tree, [tag](https://en.wikipedia.org/wiki/Tagged_pointer) the `root` pointer with the height.
      Use [`tag`](https://docs.rs/crossbeam/*/crossbeam/epoch/struct.Shared.html#method.tag) and [`with_tag`](https://docs.rs/crossbeam/*/crossbeam/epoch/struct.Shared.html#method.with_tag).
      See [`lockfree/list.rs`](https://github.com/kaist-cp/cs431/blob/main/src/lockfree/list.rs) for example usage.
      See also: [#226](https://github.com/kaist-cp/cs431/issues/226)
1. Implement `SplitOrderedList` in `split_ordered_list.rs`. (about 80 LOC)
    * You can use bitwise operations on `usize` e.g. `<<`, `&`, `|`, `^`, ...
      See also: [`leading_zeros`](https://doc.rust-lang.org/std/primitive.usize.html#method.leading_zeros), [`reverse_bits`](https://doc.rust-lang.org/std/primitive.usize.html#method.reverse_bits), [`size_of`](https://doc.rust-lang.org/std/mem/fn.size_of.html)
    * We provided type signatures for 2 helper methods for `SplitOrderedList`.
      You can modify/remove them or add more private methods if you want to.
      Just make sure you don't change the public interface. You can import other stuff from the `core` or `crossbeam_epoch` crates (but not necessary).

#### Part 2: Relaxing the orderings
Use release-acquire synchronization for atomic accesses, just like many other data structures covered in the lecture.

---

### Phase 7: Behaviour-Oriented Concurrency (BoC)
**Implement a runtime for Behaviour-Oriented Concurrency**

> *The Behaviour-Oriented Concurrency paradigm: a concurrency paradigm
> that achieves flexible coordination over multiple resources, and ordered execution, and scalability.* (from §1 of the BoC [paper](https://doi.org/10.1145/3622852))

First, read [the original BoC paper](https://doi.org/10.1145/3622852) and understand its algorithm.

Fill in the `todo!()`s in `boc.rs`.
The total lines of code to be written is about 70.
Your implementation should satisfy the following criterias:
* when clauses should be scheduled in the correct order of the *dependency graph* (§4.1).
* Your implementation of the BoC runtime should ensure *deadlock freedom*.
  We will test the deadlock freedom by several stress tests with timeouts.
* Whenever you want to spawn a new thread, **don't use** [`std::thread::spawn`](https://doc.rust-lang.org/std/thread/fn.spawn.html).
  Instead, use [`rayon::spawn`](https://docs.rs/rayon/latest/rayon/fn.spawn.html).

We provide several ways of using the when clause in Rust, illustrated below.

1.  Using the `when!` macro. Below is a representative example describing its use:

    ```rust
    when!(c1, c2; g1, g2; {
        ... // thunk
    });
    ```
    This results in a when clause that schedules a new behavior for two `CownPtr`s `c1` and `c2`.
    `g1` and `g2` are mutable references to the shared resources protected by given `CownPtr`s
    and can be used in the thunk.
2.  Using the `run_when` function directly. Use this if you want to create a new behavior with an arbitrary number of `CownPtr`s.
    For example,

    ```rust
    run_when(vec![c1.clone(), c2.clone(), c3.clone()], move |mut acc| {
        ... // thunk
    });
    ```
    The first argument is a `Vec` of cowns with the same type.
    `acc` is a vector of mutable references to the shared resources protected by the cowns,
    and it is guaranteed that `acc` has the same length as the specified given `Vec` of `CownPtr`s.
