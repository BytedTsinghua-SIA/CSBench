// CS000206 - SimulationTaichi
// 在现有 MLS-MPM 2D 框架上构建多场景/多材料示例，并提供 headless 接口便于单元测试。

#include <cstdlib>
#include <iostream>
#include <string>
#include <unordered_map>

#include "mpm_sim.h"

static bool has_flag(int argc, char **argv, const std::string &flag) {
  for (int i = 1; i < argc; i++) {
    if (argv[i] == flag) return true;
  }
  return false;
}

static std::string get_opt(int argc, char **argv, const std::string &key, const std::string &def) {
  for (int i = 1; i + 1 < argc; i++) {
    if (argv[i] == key) return std::string(argv[i + 1]);
  }
  return def;
}

static float get_opt_f(int argc, char **argv, const std::string &key, float def) {
  for (int i = 1; i + 1 < argc; i++) {
    if (argv[i] == key) return std::strtof(argv[i + 1], nullptr);
  }
  return def;
}

static int get_opt_i(int argc, char **argv, const std::string &key, int def) {
  for (int i = 1; i + 1 < argc; i++) {
    if (argv[i] == key) return std::atoi(argv[i + 1]);
  }
  return def;
}

int main(int argc, char **argv) {
  const bool headless = has_flag(argc, argv, "--headless");
  const std::string scene = get_opt(argc, argv, "--scene", "snow_E_compare");
  const int steps = get_opt_i(argc, argv, "--steps", 20000);
  const int inject_frames = get_opt_i(argc, argv, "--inject_frames", 300);

  cs206::SimConfig cfg;
  cfg.E_default = get_opt_f(argc, argv, "--E", cfg.E_default);
  cfg.E_jelly = get_opt_f(argc, argv, "--E_jelly", cfg.E_jelly);
  cfg.E_fluid = get_opt_f(argc, argv, "--E_fluid", cfg.E_fluid);

  cs206::MpmSim2D sim(cfg);
  std::unordered_map<std::string, taichi::real> params;
  params["E_soft"] = get_opt_f(argc, argv, "--E_soft", 5e3f);
  params["E_stiff"] = get_opt_f(argc, argv, "--E_stiff", 5e4f);
  params["num"] = (taichi::real)get_opt_i(argc, argv, "--num", 1200);
  params["jet_per_frame"] = (taichi::real)get_opt_i(argc, argv, "--jet_per_frame", 20);
  params["jet_vx"] = get_opt_f(argc, argv, "--jet_vx", 7.0f);
  params["jet_vy"] = get_opt_f(argc, argv, "--jet_vy", 0.0f);
  params["E_jelly"] = cfg.E_jelly;
  params["E_fluid"] = cfg.E_fluid;

  if (!sim.build_scene(scene, params)) {
    std::cerr << "未知场景: " << scene << "\n";
    std::cerr << "可选场景: snow_E_compare, water_hit_jelly, fountain\n";
    return 1;
  }

  if (headless) {
    // headless：固定步数运行，便于自动测试
    int frame = 0;
    for (int s = 0; s < steps; s++) {
      sim.step();
      if (s % int(cfg.frame_dt / cfg.dt) == 0) {
        if (scene == "water_hit_jelly" || scene == "fountain") {
          if (scene == "fountain" || frame < inject_frames) sim.inject_if_enabled();
        }
        frame++;
      }
    }
    auto st = sim.stats();
    std::cout << "场景: " << scene << "\n";
    std::cout << "粒子总数: " << st.total << " (fluid=" << st.n_fluid << ", jelly=" << st.n_jelly
              << ", snow=" << st.n_snow << ")\n";
    std::cout << "all_finite: " << (st.all_finite ? "true" : "false") << "\n";
    std::cout << "bbox_min: (" << st.min_xy.x << ", " << st.min_xy.y << ")\n";
    std::cout << "bbox_max: (" << st.max_xy.x << ", " << st.max_xy.y << ")\n";
    return st.all_finite ? 0 : 1;
  }

  // GUI模式：实时展示
  const int window_size = 800;
  taichi::GUI gui("CS000206 MLS-MPM Scenes", window_size, window_size);
  auto &canvas = gui.get_canvas();

  for (int step = 0, frame = 0;; step++) {
    sim.step();
    if (step % int(cfg.frame_dt / cfg.dt) == 0) {
      canvas.clear(0x112F41);
      canvas.rect(cs206::Vec(cfg.boundary), cs206::Vec(1.0f - cfg.boundary))
          .radius(2)
          .color(0x4FB99F)
          .close();
      for (const auto &p : sim.get_particles()) {
        canvas.circle(p.x).radius(2).color(p.color);
      }
      gui.update();

      if (scene == "water_hit_jelly" || scene == "fountain") {
        if (scene == "fountain" || frame < inject_frames) sim.inject_if_enabled();
      }
      frame++;
    }
  }
}

/* -----------------------------------------------------------------------------
** Reference: A Moving Least Squares Material Point Method with Displacement
              Discontinuity and Two-Way Rigid Body Coupling (SIGGRAPH 2018)

  By Yuanming Hu (who also wrote this 88-line version), Yu Fang, Ziheng Ge,
           Ziyin Qu, Yixin Zhu, Andre Pradhana, Chenfanfu Jiang


** Build Instructions:

Step 1: Download and unzip mls-mpm88.zip (Link: http://bit.ly/mls-mpm88)
        Now you should have "mls-mpm88.cpp" and "taichi.h".

Step 2: Compile and run

* Linux:
    g++ mls-mpm88-explained.cpp -std=c++14 -g -lX11 -lpthread -O3 -o mls-mpm
    ./mls-mpm


* Windows (MinGW):
    g++ mls-mpm88-explained.cpp -std=c++14 -lgdi32 -lpthread -O3 -o mls-mpm
    .\mls-mpm.exe


* Windows (Visual Studio 2017+):
  - Create an "Empty Project"
  - Use taichi.h as the only header, and mls-mpm88-explained.cpp as the only source
  - Change configuration to "Release" and "x64"
  - Press F5 to compile and run


* OS X:
    g++ mls-mpm88-explained.cpp -std=c++14 -framework Cocoa -lpthread -O3 -o mls-mpm
    ./mls-mpm


** FAQ:
Q1: What does "1e-4_f" mean?
A1: The same as 1e-4f, a float precision real number.

Q2: What is "real"?
A2: real = float in this file.

Q3: What are the hex numbers like 0xED553B?
A3: They are RGB color values.
    The color scheme is borrowed from
    https://color.adobe.com/Copy-of-Copy-of-Core-color-theme-11449181/

Q4: How can I get higher-quality?
A4: Change n to 320; Change dt to 1e-5; Change E to 2e4;
    Change particle per cube from 500 to 8000 (Ln 72).
    After the change the whole animation takes ~3 minutes on my computer.

Q5: How to record the animation?
A5: Uncomment Ln 2 and 85 and create a folder named "tmp".
    The frames will be saved to "tmp/XXXXX.png".

    To get a video, you can use ffmpeg. If you already have taichi installed,
    you can simply go to the "tmp" folder and execute

      ti video 60

    where 60 stands for 60 FPS. A file named "video.mp4" is what you want.

Q6: How is taichi.h generated?
A6: Please check out my #include <taichi> talk:
    http://taichi.graphics/wp-content/uploads/2018/11/include_taichi.pdf
    and the generation script:
    https://github.com/yuanming-hu/taichi/blob/master/misc/amalgamate.py
    You can regenerate it using `ti amal`, if you have taichi installed.

Questions go to yuanming _at_ mit.edu
                            or https://github.com/yuanming-hu/taichi_mpm/issues.

                                                      Last Update: March 6, 2019
                                                      Version 1.5

----------------------------------------------------------------------------- */
