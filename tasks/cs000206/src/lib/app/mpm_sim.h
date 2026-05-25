// MLS-MPM 2D simulation helper for CS000206 (SimulationTaichi)

#pragma once

#include <cmath>
#include <cstdint>
#include <cstring>
#include <limits>
#include <string>
#include <unordered_map>
#include <vector>

#include "taichi.h"

namespace cs206 {

using namespace taichi;
using Vec = Vector2;
using Mat = Matrix2;

enum MaterialType : int { Fluid = 0, Jelly = 1, Snow = 2 };

struct SimConfig {
  // Grid resolution (cells)
  int n = 80;
  // Timestep
  real dt = 1e-4_f;
  // Visualization frame timestep
  real frame_dt = 1e-3_f;
  // Gravity (in grid velocity units)
  Vec gravity = Vec(0.0_f, -200.0_f);
  // Boundary thickness in [0,1]
  real boundary = 0.05_f;

  // Particle material constants
  real particle_mass = 1.0_f;
  real vol = 1.0_f;
  real hardening = 10.0_f;
  real nu = 0.2_f;
  bool plastic = true;

  // Default Young's modulus used when not specified per-object
  real E_default = 1e4_f;
  // Fluid compressibility (via lambda0); keep > 0
  real E_fluid = 5e3_f;
  // Jelly stiffness base
  real E_jelly = 2e4_f;
};

struct Particle {
  Vec x, v;
  Mat F;
  Mat C;
  real Jp;
  std::uint32_t color;
  int type; // 0 fluid, 1 jelly, 2 snow

  // Per-particle Lamé base parameters, enabling E comparison in one run.
  real mu0;
  real lambda0;

  Particle(Vec x_, std::uint32_t c_, Vec v_, int type_, real E, real nu)
      : x(x_), v(v_), F(1), C(0), Jp(1), color(c_), type(type_) {
    mu0 = E / (2 * (1 + nu));
    lambda0 = E * nu / ((1 + nu) * (1 - 2 * nu));
  }
};

struct SimStats {
  int total = 0;
  int n_fluid = 0;
  int n_jelly = 0;
  int n_snow = 0;
  bool all_finite = true;
  Vec min_xy = Vec(std::numeric_limits<real>::infinity());
  Vec max_xy = Vec(-std::numeric_limits<real>::infinity());
};

class MpmSim2D {
public:
  explicit MpmSim2D(SimConfig cfg_ = {}) : cfg(cfg_) {
    dx = 1.0_f / cfg.n;
    inv_dx = 1.0_f / dx;
    grid.resize((cfg.n + 1) * (cfg.n + 1));
  }

  void reset() { particles.clear(); }

  // ---------------------------
  // Scene helpers
  // ---------------------------
  void add_circle(Vec center,
                  real radius,
                  std::uint32_t color,
                  int num,
                  Vec velocity,
                  int type,
                  real E_override = -1) {
    int i = 0;
    (void)E_override;
    const real E = default_E_for_type(type);
    while (i < num) {
      auto p = (Vec::rand() * 2.0_f - Vec(1)) * radius;
      if (p.x * p.x + p.y * p.y <= radius * radius) {
        particles.emplace_back(p + center, color, velocity, type, E, cfg.nu);
        i++;
      }
    }
  }

  void add_rect(Vec v1,
                Vec v2,
                std::uint32_t color,
                int num,
                Vec velocity,
                int type,
                real E_override = -1) {
    const Vec box_min(min(v1.x, v2.x), min(v1.y, v2.y));
    const Vec box_max(max(v1.x, v2.x), max(v1.y, v2.y));
    int i = 0;
    (void)E_override;
    const real E = default_E_for_type(type);
    while (i < num) {
      auto p = Vec::rand();
      if (p.x >= box_min.x && p.y >= box_min.y && p.x <= box_max.x && p.y <= box_max.y) {
        particles.emplace_back(p, color, velocity, type, E, cfg.nu);
        i++;
      }
    }
  }

  // Predefined scenes requested by assignment
  bool build_scene(const std::string &scene,
                   const std::unordered_map<std::string, real> &params = {}) {
    (void)params;
    reset();
    jet_cfg.enabled = false;

    if (scene == "demo") {
      add_rect(Vec(0.25_f, 0.10_f), Vec(0.75_f, 0.18_f), 0xED553B, 900, Vec(0, 0), Snow);
      add_circle(Vec(0.50_f, 0.65_f), 0.06_f, 0x87CEFA, 1200, Vec(0, 0), Snow);
      return true;
    }
    return false;
  }

  // ---------------------------
  // Simulation stepping
  // ---------------------------
  void step() { advance(cfg.dt); }

  // For scenes with jet injection: call once per visualization frame
  void inject_if_enabled() {
    if (!jet_cfg.enabled) return;
    add_rect(jet_cfg.p1, jet_cfg.p2, jet_cfg.color, jet_cfg.per_frame, jet_cfg.v, jet_cfg.type, jet_cfg.E);
  }

  void set_jet_enabled(bool en) { jet_cfg.enabled = en; }

  SimStats stats() const {
    SimStats s;
    s.total = (int)particles.size();
    for (const auto &p : particles) {
      if (!std::isfinite(p.x.x) || !std::isfinite(p.x.y) || !std::isfinite(p.v.x) || !std::isfinite(p.v.y)) {
        s.all_finite = false;
      }
      s.min_xy.x = std::min(s.min_xy.x, p.x.x);
      s.min_xy.y = std::min(s.min_xy.y, p.x.y);
      s.max_xy.x = std::max(s.max_xy.x, p.x.x);
      s.max_xy.y = std::max(s.max_xy.y, p.x.y);
      if (p.type == Fluid) s.n_fluid++;
      else if (p.type == Jelly) s.n_jelly++;
      else if (p.type == Snow) s.n_snow++;
    }
    return s;
  }

  const std::vector<Particle> &get_particles() const { return particles; }

private:
  SimConfig cfg{};
  real dx{0}, inv_dx{0};
  std::vector<Particle> particles;
  std::vector<Vector3> grid; // flattened (n+1)*(n+1)

  struct JetConfig {
    bool enabled = false;
    int per_frame = 0;
    Vec p1, p2;
    Vec v;
    std::uint32_t color = 0;
    int type = Fluid;
    real E = 0;
  } jet_cfg;

  static real get_param(const std::unordered_map<std::string, real> &m, const std::string &k, real def) {
    auto it = m.find(k);
    return it == m.end() ? def : it->second;
  }

  real default_E_for_type(int type) const {
    if (type == Fluid) return cfg.E_fluid;
    if (type == Jelly) return cfg.E_jelly;
    return cfg.E_default;
  }

  inline Vector3 &G(int i, int j) { return grid[i * (cfg.n + 1) + j]; }
  inline const Vector3 &G(int i, int j) const { return grid[i * (cfg.n + 1) + j]; }

  static bool finite_mat2(const Mat &A) {
    return std::isfinite(A.m[0][0]) && std::isfinite(A.m[0][1]) && std::isfinite(A.m[1][0]) && std::isfinite(A.m[1][1]);
  }

  void clamp_particle_to_domain(Particle &p) {
    const real lo = cfg.boundary;
    const real hi = 1.0_f - cfg.boundary;
    bool clamped = false;
    if (p.x.x < lo) {
      p.x.x = lo;
      clamped = true;
    }
    if (p.x.x > hi) {
      p.x.x = hi;
      clamped = true;
    }
    if (p.x.y < lo) {
      p.x.y = lo;
      clamped = true;
    }
    if (p.x.y > hi) {
      p.x.y = hi;
      clamped = true;
    }
    if (clamped) p.v = Vec(0);
  }

  void advance(real dt) {
    std::memset(grid.data(), 0, grid.size() * sizeof(Vector3));

    // P2G
    for (auto &p : particles) {
      Vector2i base = (p.x * inv_dx - Vec(0.5_f)).cast<int>();
      Vec fx = p.x * inv_dx - base.cast<real>();
      Vec w[3] = {
          Vec(0.5_f) * sqr(Vec(1.5_f) - fx),
          Vec(0.75_f) - sqr(fx - Vec(1.0_f)),
          Vec(0.5_f) * sqr(fx - Vec(0.5_f)),
      };

      real e = std::exp(cfg.hardening * (1.0_f - p.Jp));
      if (p.type == Jelly) e = 0.3_f;

      real mu = p.mu0 * e;
      real lambda = p.lambda0 * e;
      if (p.type == Fluid) mu = 0.0_f;

      const real J = determinant(p.F);
      Mat r, s;
      polar_decomp(p.F, r, s);

      // Note: scalar term added to diagonal via Matrix2 + scalar
      const Mat PF = (2 * mu * (p.F - r) * transposed(p.F) + lambda * (J - 1) * J);
      const real Dinv = 4 * inv_dx * inv_dx;
      const Mat stress = -(dt * cfg.vol) * (Dinv * PF);
      const Mat affine = stress + cfg.particle_mass * p.C;

      for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
          const int gx = base.x + i;
          const int gy = base.y + j;
          if (gx < 0 || gx > cfg.n || gy < 0 || gy > cfg.n) continue;
          const Vec dpos = (Vec(i, j) - fx) * dx;
          Vector3 mv(p.v * cfg.particle_mass, cfg.particle_mass);
          G(gx, gy) += w[i].x * w[j].y * (mv + Vector3(affine * dpos, 0));
        }
      }
    }

    // Grid operations
    for (int i = 0; i <= cfg.n; i++) {
      for (int j = 0; j <= cfg.n; j++) {
        auto &g = G(i, j);
        if (g[2] > 0) {
          g /= g[2];
          g += dt * Vector3(cfg.gravity, 0);

          const real x = (real)i / cfg.n;
          const real y = (real)j / cfg.n;

          if (x < cfg.boundary || x > 1 - cfg.boundary || y > 1 - cfg.boundary) {
            g = Vector3(0);
          }
          if (y < cfg.boundary) {
            g[1] = std::max(0.0_f, g[1]);
          }
        }
      }
    }

    // G2P
    for (auto &p : particles) {
      Vector2i base = (p.x * inv_dx - Vec(0.5_f)).cast<int>();
      Vec fx = p.x * inv_dx - base.cast<real>();
      Vec w[3] = {
          Vec(0.5_f) * sqr(Vec(1.5_f) - fx),
          Vec(0.75_f) - sqr(fx - Vec(1.0_f)),
          Vec(0.5_f) * sqr(fx - Vec(0.5_f)),
      };

      p.C = Mat(0);
      p.v = Vec(0);
      for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
          const int gx = base.x + i;
          const int gy = base.y + j;
          if (gx < 0 || gx > cfg.n || gy < 0 || gy > cfg.n) continue;
          const Vec dpos = (Vec(i, j) - fx);
          const Vec grid_v = Vec(G(gx, gy));
          const real weight = w[i].x * w[j].y;
          p.v += weight * grid_v;
          p.C += 4 * inv_dx * Mat::outer_product(weight * grid_v, dpos);
        }
      }

      p.x += dt * p.v;
      clamp_particle_to_domain(p);

      // Deformation gradient update (type-specific)
      const Mat F = (Mat(1) + dt * p.C) * p.F;
      if (p.type == Fluid) {
        const real detF = determinant(F);
        p.F = Mat(1) * std::sqrt(std::max(detF, 1e-12_f));
      } else if (p.type == Jelly) {
        p.F = F;
      } else { // Snow
        if (!finite_mat2(F)) {
          // hard reset for numerical robustness
          p.F = Mat(1);
          p.C = Mat(0);
          p.Jp = 1.0_f;
          continue;
        }
        Mat U, Sig, V;
        svd(F, U, Sig, V);
        for (int k = 0; k < 2 * int(cfg.plastic); k++) {
          Sig[k][k] = clamp(Sig[k][k], 1.0_f - 2.5e-2_f, 1.0_f + 7.5e-3_f);
        }
        const real oldJ = determinant(F);
        const Mat F_clamped = U * Sig * transposed(V);
        const real detFc = determinant(F_clamped);
        const real safe_det = std::isfinite(detFc) ? std::max(std::abs(detFc), 1e-12_f) : 1e-12_f;
        const real safe_oldJ = std::isfinite(oldJ) ? oldJ : 1.0_f;
        p.Jp = clamp(p.Jp * safe_oldJ / safe_det, 0.6_f, 20.0_f);
        p.F = F_clamped;
      }
    }
  }
};

} // namespace cs206


