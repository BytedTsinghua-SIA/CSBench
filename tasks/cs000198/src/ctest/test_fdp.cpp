#include "champsim.h"
#include "cache.h"
#include <iostream>
#include <cassert>
#include <cstring>
#include <vector>

extern std::vector<uint64_t> prefetch_addresses;
extern uint64_t current_cycle;

// Include the FDP prefetcher implementation
#include "../prefetcher/fdp.l2c_pref"

CACHE* test_cache = nullptr;

void run_test(const char* test_name) {
    if (test_cache == nullptr) {
        test_cache = new CACHE("L2C", L2C_SET, L2C_WAY, L2C_WAY * L2C_SET, L2C_WQ_SIZE, L2C_RQ_SIZE, L2C_PQ_SIZE, L2C_MSHR_SIZE);
        test_cache->cpu = 0;
    }
    
    if (strcmp(test_name, "fdp_initialization") == 0) {
        test_cache->l2c_prefetcher_initialize();
        assert(prefetch_tracker_head == 0);
        for (int i = 0; i < IP_TRACKER_COUNT; i++) {
            assert(trackers[i].lru == i);
        }
    }
    else if (strcmp(test_name, "fdp_stride_detection") == 0) {
        test_cache->l2c_prefetcher_initialize();
        prefetch_addresses.clear();
        
        uint64_t base_addr = 0x10000;
        uint64_t pc = 0x1000;
        
        test_cache->l2c_prefetcher_operate(base_addr, pc, 0, LOAD, 0);
        test_cache->l2c_prefetcher_operate(base_addr + 64, pc, 0, LOAD, 0);
        test_cache->l2c_prefetcher_operate(base_addr + 128, pc, 0, LOAD, 0);
        
        assert(prefetch_addresses.size() > 0);
    }
    else if (strcmp(test_name, "fdp_aggressiveness_levels") == 0) {
        test_cache->l2c_prefetcher_initialize();
        
        assert(MAX_AGGRESSIVENESS == 5);
        assert(aggressiveness_configs[0].distance == 4);
        assert(aggressiveness_configs[0].degree == 1);
        assert(aggressiveness_configs[4].distance == 48);
        assert(aggressiveness_configs[4].degree == 4);
    }
    else if (strcmp(test_name, "fdp_feedback_mechanism") == 0) {
        test_cache->l2c_prefetcher_initialize();
        prefetch_addresses.clear();
        
        uint64_t base_addr = 0x10000;
        uint64_t pc = 0x1000;
        
        // Generate prefetches
        for (int i = 0; i < 10; i++) {
            test_cache->l2c_prefetcher_operate(base_addr + i * 64, pc, 0, LOAD, 0);
        }
        
        // Simulate cache fill for prefetched addresses
        for (uint64_t pf_addr : prefetch_addresses) {
            test_cache->l2c_prefetcher_cache_fill(pf_addr, 0, 0, 0, 0, 0);
        }
        
        // Check that feedback mechanism is working
        int tracker_index = -1;
        for (int i = 0; i < IP_TRACKER_COUNT; i++) {
            if (trackers[i].ip == pc) {
                tracker_index = i;
                break;
            }
        }
        assert(tracker_index >= 0);
    }
    else if (strcmp(test_name, "fdp_no_prefetch_for_store") == 0) {
        test_cache->l2c_prefetcher_initialize();
        prefetch_addresses.clear();
        
        uint64_t addr = 0x10000;
        uint64_t pc = 0x1000;
        
        test_cache->l2c_prefetcher_operate(addr, pc, 0, RFO, 0);
        assert(prefetch_addresses.size() == 0);
    }
    else if (strcmp(test_name, "fdp_page_boundary_check") == 0) {
        test_cache->l2c_prefetcher_initialize();
        prefetch_addresses.clear();
        
        uint64_t pc = 0x1000;
        uint64_t page_size = 4096;
        uint64_t base_addr = page_size - 256;
        
        test_cache->l2c_prefetcher_operate(base_addr, pc, 0, LOAD, 0);
        test_cache->l2c_prefetcher_operate(base_addr + 64, pc, 0, LOAD, 0);
        test_cache->l2c_prefetcher_operate(base_addr + 128, pc, 0, LOAD, 0);
        
        uint64_t page_num = base_addr >> LOG2_PAGE_SIZE;
        for (uint64_t pf_addr : prefetch_addresses) {
            uint64_t pf_page = pf_addr >> LOG2_PAGE_SIZE;
            assert(pf_page == page_num);
        }
    }
    else if (strcmp(test_name, "fdp_cache_fill") == 0) {
        test_cache->l2c_prefetcher_initialize();
        prefetch_addresses.clear();
        
        uint64_t base_addr = 0x10000;
        uint64_t pc = 0x1000;
        
        test_cache->l2c_prefetcher_operate(base_addr, pc, 0, LOAD, 0);
        test_cache->l2c_prefetcher_operate(base_addr + 64, pc, 0, LOAD, 0);
        test_cache->l2c_prefetcher_operate(base_addr + 128, pc, 0, LOAD, 0);
        
        if (prefetch_addresses.size() > 0) {
            test_cache->l2c_prefetcher_cache_fill(prefetch_addresses[0], 0, 0, 0, 0, 0);
            test_cache->l2c_prefetcher_cache_fill(prefetch_addresses[0], 0, 0, 1, 0, 0);
        }
    }
    else if (strcmp(test_name, "fdp_final_stats") == 0) {
        test_cache->l2c_prefetcher_initialize();
        test_cache->l2c_prefetcher_final_stats();
    }
    else {
        std::cerr << "Unknown test: " << test_name << std::endl;
        exit(1);
    }
}

