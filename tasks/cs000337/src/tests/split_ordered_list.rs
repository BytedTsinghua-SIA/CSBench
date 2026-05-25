#![feature(cfg_sanitize)]

use crossbeam_epoch as epoch;
use cs431_homework::test::adt::map;
use cs431_homework::{ConcurrentMap, SplitOrderedList};

#[test]
pub fn smoke() {
    let list = SplitOrderedList::new();

    let guard = epoch::pin();

    assert_eq!(list.insert(37, 37, &guard), Ok(()));
    assert_eq!(list.lookup(&42, &guard), None);
    assert_eq!(list.lookup(&37, &guard), Some(&37));

    assert_eq!(list.insert(42, 42, &guard), Ok(()));
    assert_eq!(list.lookup(&42, &guard), Some(&42));
    assert_eq!(list.lookup(&37, &guard), Some(&37));

    assert_eq!(list.delete(&37, &guard), Ok(&37));
    assert_eq!(list.lookup(&42, &guard), Some(&42));
    assert_eq!(list.lookup(&37, &guard), None);

    assert_eq!(list.delete(&37, &guard), Err(()));
    assert_eq!(list.lookup(&42, &guard), Some(&42));
    assert_eq!(list.lookup(&37, &guard), None);
}

#[test]
fn stress_sequential() {
    const STEPS: usize = 1024;
    map::stress_sequential::<_, _, SplitOrderedList<usize>>(STEPS);
}

#[test]
fn lookup_concurrent() {
    const THREADS: usize = 4;
    const STEPS: usize = 1024;
    map::lookup_concurrent::<_, _, SplitOrderedList<usize>>(THREADS, STEPS);
}

#[test]
fn insert_concurrent() {
    const THREADS: usize = 4;
    const STEPS: usize = 1024;
    map::insert_concurrent::<_, _, SplitOrderedList<usize>>(THREADS, STEPS);
}

#[test]
fn stress_concurrent() {
    const THREADS: usize = if cfg!(sanitize = "thread") { 2 } else { 4 };
    const STEPS: usize = 1024 * if cfg!(sanitize = "thread") { 8 } else { 32 };
    map::stress_concurrent::<_, _, SplitOrderedList<usize>>(THREADS, STEPS);
}

#[test]
fn log_concurrent() {
    const THREADS: usize = if cfg!(sanitize = "thread") { 2 } else { 4 };
    const STEPS: usize = 1024 * if cfg!(sanitize = "thread") { 2 } else { 8 };
    map::log_concurrent::<_, _, SplitOrderedList<usize>>(THREADS, STEPS);
}
