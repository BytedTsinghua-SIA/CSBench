#include <iostream>
#include <string>
#include <cstring>
#include <cstdlib>

extern void run_test(const char* test_name);

int main(int argc, char* argv[]) {
    if (argc > 1) {
        std::string test_name = argv[1];
        std::cout << "Running test: " << test_name << "..." << std::endl;
        run_test(test_name.c_str());
        std::cout << "PASSED" << std::endl;
        return 0;
    } else {
        std::cerr << "Usage: " << argv[0] << " <test_name>" << std::endl;
        return 1;
    }
}

