#include "champsim.h"
#include "cache.h"
#include <iostream>
#include <cassert>
#include <cstring>
#include <vector>

extern std::vector<uint64_t> prefetch_addresses;
extern uint64_t current_cycle;

// Include the Task3 prefetcher implementation
#include "../prefetcher/task3.l2c_pref"

CACHE* test_cache = nullptr;

void run_test(const char* test_name) {
    if (test_cache == nullptr) {
        test_cache = new CACHE("L2C", L2C_SET, L2C_WAY, L2C_WAY * L2C_SET, L2C_WQ_SIZE, L2C_RQ_SIZE, L2C_PQ_SIZE, L2C_MSHR_SIZE);
        test_cache->cpu = 0;
    }
    
    if (strcmp(test_name, "task3_initialization") == 0) {
        test_cache->l2c_prefetcher_initialize();
        for (int i = 0; i < IP_TRACKER_COUNT; i++) {
            assert(trackers[i].lru == i);
        }
        for (int i = 0; i < SPATIAL_PATTERN_SIZE; i++) {
            assert(spatial_pattern_lru[i] == i);
        }
    }
    else if (strcmp(test_name, "task3_stride_detection") == 0) {
        test_cache->l2c_prefetcher_initialize();
        prefetch_addresses.clear();
        
        uint64_t base_addr = 0x10000;
        uint64_t pc = 0x1000;
        
        test_cache->l2c_prefetcher_operate(base_addr, pc, 0, LOAD, 0);
        test_cache->l2c_prefetcher_operate(base_addr + 64, pc, 0, LOAD, 0);
        test_cache->l2c_prefetcher_operate(base_addr + 128, pc, 0, LOAD, 0);
        
        int tracker_index = -1;
        for (int i = 0; i < IP_TRACKER_COUNT; i++) {
            if (trackers[i].ip == pc) {
                tracker_index = i;
                break;
            }
        }
        assert(tracker_index >= 0);
        assert(trackers[tracker_index].stride_confidence >= CONFIDENCE_THRESHOLD);
    }
    else if (strcmp(test_name, "task3_confidence_mechanism") == 0) {
        test_cache->l2c_prefetcher_initialize();
        prefetch_addresses.clear();
        
        uint64_t base_addr = 0x10000;
        uint64_t pc = 0x1000;
        
        test_cache->l2c_prefetcher_operate(base_addr, pc, 0, LOAD, 0);
        test_cache->l2c_prefetcher_operate(base_addr + 64, pc, 0, LOAD, 0);
        
        int tracker_index = -1;
        for (int i = 0; i < IP_TRACKER_COUNT; i++) {
            if (trackers[i].ip == pc) {
                tracker_index = i;
                break;
            }
        }
        assert(tracker_index >= 0);
        uint32_t confidence1 = trackers[tracker_index].stride_confidence;
        
        test_cache->l2c_prefetcher_operate(base_addr + 128, pc, 0, LOAD, 0);
        uint32_t confidence2 = trackers[tracker_index].stride_confidence;
        
        assert(confidence2 > confidence1);
    }
    else if (strcmp(test_name, "task3_spatial_pattern") == 0) {
        test_cache->l2c_prefetcher_initialize();
        prefetch_addresses.clear();
        
        uint64_t pc = 0x1000;
        uint64_t page_addr = 0x10000;
        
        // Access multiple blocks in same page
        for (int i = 0; i < 5; i++) {
            test_cache->l2c_prefetcher_operate(page_addr + i * 64, pc, 0, LOAD, 0);
        }
        
        // Should have spatial pattern
        int spatial_index = -1;
        for (int i = 0; i < SPATIAL_PATTERN_SIZE; i++) {
            if (spatial_patterns[i].base_addr == (page_addr >> LOG2_PAGE_SIZE)) {
                spatial_index = i;
                break;
            }
        }
        assert(spatial_index >= 0);
        assert(spatial_patterns[spatial_index].access_count >= 4);
        assert(spatial_patterns[spatial_index].pattern_mask > 0);
    }
    else if (strcmp(test_name, "task3_no_prefetch_for_store") == 0) {
        test_cache->l2c_prefetcher_initialize();
        prefetch_addresses.clear();
        
        uint64_t addr = 0x10000;
        uint64_t pc = 0x1000;
        
        test_cache->l2c_prefetcher_operate(addr, pc, 0, RFO, 0);
        assert(prefetch_addresses.size() == 0);
    }
    else if (strcmp(test_name, "task3_page_boundary_check") == 0) {
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
    else if (strcmp(test_name, "task3_cache_fill") == 0) {
        test_cache->l2c_prefetcher_initialize();
        test_cache->l2c_prefetcher_cache_fill(0x10000, 0, 0, 0, 0, 0);
    }
    else if (strcmp(test_name, "task3_final_stats") == 0) {
        test_cache->l2c_prefetcher_initialize();
        test_cache->l2c_prefetcher_final_stats();
    }
    else {
        std::cerr << "Unknown test: " << test_name << std::endl;
        exit(1);
    }
}

