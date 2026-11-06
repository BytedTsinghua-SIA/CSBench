#include "GUI/SimpleTest.h"
#include "GUI/TestDriver.h"
#include <string>

int main(int argc, char** argv) {
    std::string group;
    if (argc == 3 && std::string(argv[1]) == "--group") {
        group = argv[2];
    } else if (argc != 1) {
        return 2;
    }

    Vector<SimpleTest::TestGroup> lastGroups;
    SimpleTest::TestReporter reporter = [&](const Vector<SimpleTest::TestGroup>& groups) {
        lastGroups = groups;
    };

    SimpleTest::TestFilter filter;
    if (!group.empty()) {
        filter = [group](const std::string& groupName, const SimpleTest::Test&) {
            return groupName == group;
        };
    } else {
        filter = [](const std::string&, const SimpleTest::Test&) { return true; };
    }

    SimpleTest::run(reporter, filter);

    int total = 0;
    int passed = 0;
    for (const auto& groupEntry : lastGroups) {
        for (const auto& test : groupEntry.tests) {
            total++;
            if (test.result == SimpleTest::TestResult::PASS) {
                passed++;
            }
        }
    }

    if (!group.empty() && total == 0) {
        return 1;
    }

    return total == passed ? 0 : 1;
}
