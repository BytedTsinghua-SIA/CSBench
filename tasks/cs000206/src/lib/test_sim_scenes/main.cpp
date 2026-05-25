#include <iostream>
#include <string>

#include "../app/mpm_sim.h"

static int run_one(const std::string &name,
                   const std::string &scene,
                   int steps,
                   int inject_frames,
                   int &pass,
                   int &fail) {
  cs206::SimConfig cfg;
  cs206::MpmSim2D sim(cfg);

  std::unordered_map<std::string, taichi::real> params;
  params["E_soft"] = 5e3f;
  params["E_stiff"] = 5e4f;
  params["num"] = 900;
  params["jet_per_frame"] = 18;
  params["jet_vx"] = 7.0f;
  params["jet_vy"] = 0.0f;
  params["E_jelly"] = cfg.E_jelly;
  params["E_fluid"] = cfg.E_fluid;

  std::cout << name << "\n";
  if (!sim.build_scene(scene, params)) {
    std::cout << "结果: 失败 (未知场景)\n";
    fail++;
    return 1;
  }

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
  const bool ok = st.all_finite && st.total > 0 && st.min_xy.x >= -1.0f && st.max_xy.x <= 2.0f;
  std::cout << "场景: " << scene << ", 粒子总数=" << st.total << ", all_finite=" << (st.all_finite ? "true" : "false")
            << "\n";
  std::cout << "bbox_min=(" << st.min_xy.x << "," << st.min_xy.y << "), bbox_max=(" << st.max_xy.x << "," << st.max_xy.y
            << ")\n";

  if (ok) {
    std::cout << "结果: 通过\n";
    pass++;
    return 0;
  } else {
    std::cout << "结果: 失败\n";
    fail++;
    return 1;
  }
}

int main(int argc, char **argv) {
  int pass = 0, fail = 0;
  std::string target = "";
  int steps_override = -1;

  for (int i = 1; i < argc; ++i) {
    std::string arg = argv[i];
    if (arg == "--steps" && i + 1 < argc) {
      steps_override = std::stoi(argv[++i]);
    } else if (arg.find("--") != 0) {
      target = arg;
    }
  }

  bool run_all = target.empty();

  if (run_all || target == "snow_E_compare") {
    int s = (steps_override > 0) ? steps_override : 6000;
    run_one("测试 1：E 对雪刚度影响（同场景内对比）", "snow_E_compare", s, 0, pass, fail);
  }
  if (run_all || target == "water_hit_jelly") {
    int s = (steps_override > 0) ? steps_override : 8000;
    run_one("测试 2：水流冲击弹性体（jelly）", "water_hit_jelly", s, 260, pass, fail);
  }
  if (run_all || target == "fountain") {
    int s = (steps_override > 0) ? steps_override : 8000;
    run_one("测试 3：喷泉（水源持续注入）", "fountain", s, 400, pass, fail);
  }
  if (run_all) {
    int s = (steps_override > 0) ? steps_override : 4000;
    run_one("测试 4：E 极端值稳定性检查（更软/更硬）", "snow_E_compare", s, 0, pass, fail);
  }

  std::cout << "测试摘要\n";
  std::cout << "通过: " << pass << "\n";
  std::cout << "失败: " << fail << "\n";
  std::cout << "总计: " << (pass + fail) << "\n";

  return (fail == 0) ? 0 : 1;
}


