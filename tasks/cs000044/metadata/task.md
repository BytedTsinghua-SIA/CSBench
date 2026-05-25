# GAMES101 作业 2 任务说明

## 基本信息
- 课程：GAMES101（2020 春季）
- 作业主题：Triangles and Z-buffering（三角形栅格化与深度缓冲）
- 发布时间：2020-03-03 10:00（北京时间）
- 截止时间：2020-03-10 10:00（北京时间）
- 提交平台：SmartChair（http://smartchair.org/GAMES2020Course-YLQ）

## 必做目标
1. 在 `rasterize_triangle(const Triangle& t)` 中完成三角形栅格化：
   - 构建三角形的 2D bounding box。
   - 遍历 bounding box 内所有像素中心，判断是否在三角形内。
   - 若在三角形内，插值得到深度，与深度缓冲区比较，更新更近者的颜色与深度。
2. 完成 `insideTriangle` 判定逻辑（可调整函数签名）。
3. 使用已给的深度插值结果 `z_interpolated`，注意 z 值为反转的正数且越大离视点越远。
4. 模型变换返回单位矩阵；`get_projection_matrix()` 需沿用作业 1 的实现。
5. 使用框架中提供的两个三角形进行正确渲染，得到实心三角形输出。

## 评分要点
- 5 分：提交文件齐全且可编译运行。
- 20 分：正确实现三角形栅格化。
- 10 分：正确的点内判定。
- 10 分：正确的 z-buffer 按序绘制。
- 提高项 5 分：实现 2×2 super-sampling 抗锯齿，每像素维护独立样本及深度，避免黑边。

## 提交要求
- 清理项目后提交，包含 CMakeLists.txt 与所有源文件。
- 提交渲染结果图片；若完成提高项，另附对应结果图。
- 提交 README.md 说明各函数实现与是否完成提高项。
- 打包命名：`姓名 Homework2.zip`，上传至 SmartChair。

## 参考流程
1. 完成投影矩阵与单位模型矩阵设置，运行框架。
2. 实现 `insideTriangle` 与 `rasterize_triangle` 的 bounding box 遍历、点内判定、深度测试与写入。
3. 验证基础渲染结果，再选择性实现 super-sampling 提升边缘质量。
