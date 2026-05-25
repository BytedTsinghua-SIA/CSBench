// Minimal taichi.h stub for MLS-MPM course assignment (headless-friendly).
// This is NOT the full Taichi GUI header. It only implements the tiny subset
// used by the provided MLS-MPM examples in this repository.
//
// Goals:
// - Make the project self-contained (no external download required)
// - Support deterministic/headless unit tests
// - Keep the API surface compatible enough for the homework code
//
// If you want full GUI features, replace this file with the official taichi.h.

#pragma once

#include <algorithm>
#include <array>
#include <cassert>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <type_traits>
#include <limits>
#include <random>
#include <string>
#include <vector>

namespace taichi {

using real = float;

// literal suffix used by the original taichi.h (e.g. 1e-4_f)
constexpr real operator"" _f(long double v) { return static_cast<real>(v); }
constexpr real operator"" _f(unsigned long long v) { return static_cast<real>(v); }

inline real clamp(real x, real a, real b) {
  return std::min(std::max(x, a), b);
}

template <typename T>
inline T sqr(const T &x) {
  return x * x;
}

// bring min/max into taichi namespace (examples use unqualified min/max)
template <typename T>
inline T min(const T &a, const T &b) {
  return std::min(a, b);
}

template <typename T>
inline T max(const T &a, const T &b) {
  return std::max(a, b);
}

// -----------------------------
// Vector types
// -----------------------------
struct Vector2;
struct Vector3;

struct Vector2i {
  int x{0}, y{0};
  Vector2i() = default;
  Vector2i(int x_, int y_) : x(x_), y(y_) {}

  template <typename T, typename std::enable_if<std::is_integral<T>::value, int>::type = 0>
  Vector2i cast() const {
    return *this;
  }

  template <typename T, typename std::enable_if<!std::is_integral<T>::value, int>::type = 0>
  Vector2 cast() const;
};

struct Vector2 {
  real x{0}, y{0};
  Vector2() = default;
  Vector2(real x_, real y_) : x(x_), y(y_) {}
  explicit Vector2(real v) : x(v), y(v) {}
  explicit Vector2(const Vector3 &v3);

  static Vector2 rand() {
    // Deterministic RNG: fixed seed for stable unit tests.
    static std::mt19937 rng(123456u);
    static std::uniform_real_distribution<real> dist(0.0f, 1.0f);
    return Vector2(dist(rng), dist(rng));
  }

  Vector2 operator+(const Vector2 &o) const { return Vector2(x + o.x, y + o.y); }
  Vector2 operator-(const Vector2 &o) const { return Vector2(x - o.x, y - o.y); }
  // element-wise multiply (required by MLS-MPM kernels)
  Vector2 operator*(const Vector2 &o) const { return Vector2(x * o.x, y * o.y); }
  Vector2 operator*(real s) const { return Vector2(x * s, y * s); }
  Vector2 operator/(real s) const { return Vector2(x / s, y / s); }

  Vector2 &operator+=(const Vector2 &o) {
    x += o.x;
    y += o.y;
    return *this;
  }

  Vector2 &operator-=(const Vector2 &o) {
    x -= o.x;
    y -= o.y;
    return *this;
  }

  template <typename T, typename std::enable_if<std::is_integral<T>::value, int>::type = 0>
  Vector2i cast() const {
    return Vector2i((int)x, (int)y);
  }

  template <typename T, typename std::enable_if<!std::is_integral<T>::value, int>::type = 0>
  Vector2 cast() const {
    return Vector2((real)x, (real)y);
  }
};

inline Vector2 operator*(real s, const Vector2 &v) { return v * s; }

struct Vector3 {
  real v[3]{0, 0, 0};
  Vector3() = default;
  explicit Vector3(real a) { v[0] = v[1] = v[2] = a; }
  Vector3(real x, real y, real z) {
    v[0] = x;
    v[1] = y;
    v[2] = z;
  }
  Vector3(const Vector2 &xy, real z) {
    v[0] = xy.x;
    v[1] = xy.y;
    v[2] = z;
  }

  real &operator[](int i) { return v[i]; }
  const real &operator[](int i) const { return v[i]; }

  Vector3 &operator+=(const Vector3 &o) {
    v[0] += o.v[0];
    v[1] += o.v[1];
    v[2] += o.v[2];
    return *this;
  }

  Vector3 operator+(const Vector3 &o) const {
    return Vector3(v[0] + o.v[0], v[1] + o.v[1], v[2] + o.v[2]);
  }

  Vector3 operator*(real s) const { return Vector3(v[0] * s, v[1] * s, v[2] * s); }

  Vector3 operator/(real s) const { return Vector3(v[0] / s, v[1] / s, v[2] / s); }
  Vector3 &operator/=(real s) {
    v[0] /= s;
    v[1] /= s;
    v[2] /= s;
    return *this;
  }
};

inline Vector3 operator*(real s, const Vector3 &v) { return v * s; }

inline Vector2::Vector2(const Vector3 &v3) : x(v3.v[0]), y(v3.v[1]) {}

template <typename T, typename std::enable_if<!std::is_integral<T>::value, int>::type>
inline Vector2 Vector2i::cast() const {
  return Vector2((real)x, (real)y);
}

// -----------------------------
// Matrix2
// -----------------------------
struct Matrix2 {
  // row-major: m[r][c]
  real m[2][2]{{0, 0}, {0, 0}};

  Matrix2() = default;
  explicit Matrix2(real diag) {
    m[0][0] = diag;
    m[1][1] = diag;
    m[0][1] = 0;
    m[1][0] = 0;
  }

  static Matrix2 outer_product(const Vector2 &a, const Vector2 &b) {
    Matrix2 r;
    r.m[0][0] = a.x * b.x;
    r.m[0][1] = a.x * b.y;
    r.m[1][0] = a.y * b.x;
    r.m[1][1] = a.y * b.y;
    return r;
  }

  real *operator[](int r) { return m[r]; }
  const real *operator[](int r) const { return m[r]; }

  Matrix2 operator+(const Matrix2 &o) const {
    Matrix2 r;
    r.m[0][0] = m[0][0] + o.m[0][0];
    r.m[0][1] = m[0][1] + o.m[0][1];
    r.m[1][0] = m[1][0] + o.m[1][0];
    r.m[1][1] = m[1][1] + o.m[1][1];
    return r;
  }

  Matrix2 &operator+=(const Matrix2 &o) {
    m[0][0] += o.m[0][0];
    m[0][1] += o.m[0][1];
    m[1][0] += o.m[1][0];
    m[1][1] += o.m[1][1];
    return *this;
  }

  // Add scalar to diagonal (matches taichi.h behavior used by MLS-MPM code)
  Matrix2 operator+(real s) const {
    Matrix2 r = *this;
    r.m[0][0] += s;
    r.m[1][1] += s;
    return r;
  }

  Matrix2 operator-(const Matrix2 &o) const {
    Matrix2 r;
    r.m[0][0] = m[0][0] - o.m[0][0];
    r.m[0][1] = m[0][1] - o.m[0][1];
    r.m[1][0] = m[1][0] - o.m[1][0];
    r.m[1][1] = m[1][1] - o.m[1][1];
    return r;
  }

  Matrix2 &operator-=(const Matrix2 &o) {
    m[0][0] -= o.m[0][0];
    m[0][1] -= o.m[0][1];
    m[1][0] -= o.m[1][0];
    m[1][1] -= o.m[1][1];
    return *this;
  }

  Matrix2 operator*(real s) const {
    Matrix2 r;
    r.m[0][0] = m[0][0] * s;
    r.m[0][1] = m[0][1] * s;
    r.m[1][0] = m[1][0] * s;
    r.m[1][1] = m[1][1] * s;
    return r;
  }

  Matrix2 operator*(const Matrix2 &o) const {
    Matrix2 r;
    r.m[0][0] = m[0][0] * o.m[0][0] + m[0][1] * o.m[1][0];
    r.m[0][1] = m[0][0] * o.m[0][1] + m[0][1] * o.m[1][1];
    r.m[1][0] = m[1][0] * o.m[0][0] + m[1][1] * o.m[1][0];
    r.m[1][1] = m[1][0] * o.m[0][1] + m[1][1] * o.m[1][1];
    return r;
  }

  Vector2 operator*(const Vector2 &v) const {
    return Vector2(m[0][0] * v.x + m[0][1] * v.y, m[1][0] * v.x + m[1][1] * v.y);
  }
};

inline Matrix2 operator*(real s, const Matrix2 &A) { return A * s; }
inline Matrix2 operator+(real s, const Matrix2 &A) { return A + s; }

inline Matrix2 transposed(const Matrix2 &A) {
  Matrix2 r;
  r.m[0][0] = A.m[0][0];
  r.m[0][1] = A.m[1][0];
  r.m[1][0] = A.m[0][1];
  r.m[1][1] = A.m[1][1];
  return r;
}

inline real determinant(const Matrix2 &A) {
  return A.m[0][0] * A.m[1][1] - A.m[0][1] * A.m[1][0];
}

inline Matrix2 identity2() { return Matrix2(1.0f); }

// Eigen decomposition for 2x2 symmetric matrix.
// Input: S = [[a,b],[b,c]]
// Output: eigenvalues l0>=l1 and orthonormal eigenvectors (columns) in V.
inline void eig_sym_2x2(real a, real b, real c, real &l0, real &l1, Matrix2 &V) {
  const real tr = a + c;
  const real det = a * c - b * b;
  const real disc = std::sqrt(std::max(real(0), tr * tr * 0.25f - det));
  l0 = tr * 0.5f + disc;
  l1 = tr * 0.5f - disc;

  // Eigenvector for l0
  Vector2 v0;
  if (std::abs(b) > 1e-12f) {
    v0 = Vector2(l0 - c, b);
  } else {
    v0 = (a >= c) ? Vector2(1, 0) : Vector2(0, 1);
  }
  const real n0 = std::sqrt(v0.x * v0.x + v0.y * v0.y);
  v0 = (n0 > 0) ? v0 / n0 : Vector2(1, 0);
  // Orthonormal v1
  Vector2 v1(-v0.y, v0.x);

  V.m[0][0] = v0.x;
  V.m[1][0] = v0.y;
  V.m[0][1] = v1.x;
  V.m[1][1] = v1.y;
}

inline Matrix2 mul_cols(const Matrix2 &A, real s0, real s1) {
  Matrix2 r;
  r.m[0][0] = A.m[0][0] * s0;
  r.m[1][0] = A.m[1][0] * s0;
  r.m[0][1] = A.m[0][1] * s1;
  r.m[1][1] = A.m[1][1] * s1;
  return r;
}

inline Matrix2 inv_2x2(const Matrix2 &A) {
  const real detA = determinant(A);
  Matrix2 r;
  if (std::abs(detA) < 1e-12f) {
    // Fallback to identity if nearly singular.
    return identity2();
  }
  const real inv = 1.0f / detA;
  r.m[0][0] = A.m[1][1] * inv;
  r.m[0][1] = -A.m[0][1] * inv;
  r.m[1][0] = -A.m[1][0] * inv;
  r.m[1][1] = A.m[0][0] * inv;
  return r;
}

// Polar decomposition: F = R * S (R rotation, S symmetric PSD)
inline void polar_decomp(const Matrix2 &F, Matrix2 &R, Matrix2 &S) {
  // S = sqrt(F^T F), R = F * S^{-1}
  const Matrix2 Ft = transposed(F);
  const Matrix2 FtF = Ft * F;
  real l0, l1;
  Matrix2 V;
  eig_sym_2x2(FtF.m[0][0], FtF.m[0][1], FtF.m[1][1], l0, l1, V);
  l0 = std::max(l0, real(0));
  l1 = std::max(l1, real(0));
  const real s0 = std::sqrt(l0);
  const real s1 = std::sqrt(l1);

  // S = V * diag(s0,s1) * V^T
  Matrix2 VD = mul_cols(V, s0, s1);
  S = VD * transposed(V);

  // R = F * S^{-1}
  R = F * inv_2x2(S);
}

// 2x2 SVD: F = U * Sig * V^T
inline void svd(const Matrix2 &F, Matrix2 &U, Matrix2 &Sig, Matrix2 &V) {
  const Matrix2 FtF = transposed(F) * F;
  real l0, l1;
  eig_sym_2x2(FtF.m[0][0], FtF.m[0][1], FtF.m[1][1], l0, l1, V);
  l0 = std::max(l0, real(0));
  l1 = std::max(l1, real(0));
  const real s0 = std::sqrt(l0);
  const real s1 = std::sqrt(l1);

  Sig = Matrix2(0);
  Sig.m[0][0] = s0;
  Sig.m[1][1] = s1;

  // U = F * V * Sig^{-1}
  Matrix2 Vinv = V; // orthonormal -> inverse = transpose
  Matrix2 FV = F * V;

  Matrix2 SigInv(0);
  SigInv.m[0][0] = (s0 > 1e-12f) ? (1.0f / s0) : 0.0f;
  SigInv.m[1][1] = (s1 > 1e-12f) ? (1.0f / s1) : 0.0f;
  U = FV * SigInv;
}

// -----------------------------
// Minimal GUI stubs (headless)
// -----------------------------
class Canvas {
public:
  struct ShapeProxy {
    ShapeProxy &radius(real) { return *this; }
    ShapeProxy &color(std::uint32_t) { return *this; }
    void close() {}
  };

  void clear(std::uint32_t) {}
  ShapeProxy rect(const Vector2 &, const Vector2 &) { return ShapeProxy(); }
  ShapeProxy circle(const Vector2 &) { return ShapeProxy(); }
};

class GUI {
public:
  GUI(const std::string &, int, int) {}
  Canvas &get_canvas() { return canvas_; }
  void update() {}

private:
  Canvas canvas_;
};

} // namespace taichi


