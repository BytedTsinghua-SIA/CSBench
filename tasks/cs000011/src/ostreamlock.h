// Minimal header-only ostream locking utilities compatible with oslock/osunlock manipulators.
#pragma once

#include <mutex>
#include <ostream>

namespace ostream_locking {
  inline std::mutex& getMutex() {
    static std::mutex mtx;
    return mtx;
  }

  struct OStreamLockManipulator {};
  struct OStreamUnlockManipulator {};
}

static const ostream_locking::OStreamLockManipulator oslock{};
static const ostream_locking::OStreamUnlockManipulator osunlock{};

inline std::ostream& operator<<(std::ostream& os, const ostream_locking::OStreamLockManipulator&) {
  ostream_locking::getMutex().lock();
  return os;
}

inline std::ostream& operator<<(std::ostream& os, const ostream_locking::OStreamUnlockManipulator&) {
  ostream_locking::getMutex().unlock();
  return os;
}


