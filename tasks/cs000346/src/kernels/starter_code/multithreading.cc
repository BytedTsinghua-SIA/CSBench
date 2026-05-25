#include <iostream>
#include <vector>
#include <chrono>
#include <cstring>
#include <thread>

inline uint8_t dequantize_weight(uint8_t quantized_weight, float scale, int8_t zero_point) {
}

void linear_kernel_worker(const int8_t* input, const uint8_t* weights,
                         int32_t* output, int input_size, int output_start, int output_end,
                         const float* scales, const int8_t* zero_points) {
}

void linear_kernel_multithreading(const int8_t* input, const uint8_t* weights,
                                int32_t* output, int input_size, int output_size,
                                const float* scales, const int8_t* zero_points) {
}

double benchmark_kernel(void (*kernel_func)(const int8_t*, const uint8_t*, int32_t*, int, int, const float*, const int8_t*),
                       const int8_t* input, const uint8_t* weights, int32_t* output,
                       int input_size, int output_size, const float* scales, const int8_t* zero_points,
                       int iterations = 100) {
}

int main() {
}
