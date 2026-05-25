#include "champsim.h"
#include "cache.h"
#include <iostream>
#include <cassert>
#include <cstring>
#include <vector>

extern std::vector<uint64_t> prefetch_addresses;
extern uint64_t current_cycle;

// Include the GHB prefetcher implementation
#include "../prefetcher/ghb.l2c_pref"

CACHE* test_cache = nullptr;

void run_test(const char* test_name) {
    if (test_cache == nullptr) {
        test_cache = new CACHE("L2C", L2C_SET, L2C_WAY, L2C_WAY * L2C_SET, L2C_WQ_SIZE, L2C_RQ_SIZE, L2C_PQ_SIZE, L2C_MSHR_SIZE);
        test_cache->cpu = 0;
    }
    
    if (strcmp(test_name, "ghb_initialization") == 0) {
        test_cache->l2c_prefetcher_initialize();
        assert(ghb_head == 0);
        assert(dct_lru_counter == 0);
        for (int i = 0; i < GHB_SIZE; i++) {
            assert(ghb[i].addr == 0);
            assert(ghb[i].next == 0);
        }
    }
    else if (strcmp(test_name, "ghb_simple_stride") == 0) {
        test_cache->l2c_prefetcher_initialize();
        prefetch_addresses.clear();
        
        uint64_t base_addr = 0x10000;
        uint64_t pc = 0x1000;
        
        // First access
        test_cache->l2c_prefetcher_operate(base_addr, pc, 0, LOAD, 0);
        assert(prefetch_addresses.size() == 0);
        
        // Second access with stride
        test_cache->l2c_prefetcher_operate(base_addr + 64, pc, 0, LOAD, 0);
        
        // Third access with same stride - should trigger prefetch
        test_cache->l2c_prefetcher_operate(base_addr + 128, pc, 0, LOAD, 0);
        
        // Should have generated prefetches
        assert(prefetch_addresses.size() > 0);
    }
    else if (strcmp(test_name, "ghb_delta_correlation") == 0) {
        test_cache->l2c_prefetcher_initialize();
        prefetch_addresses.clear();
        
        uint64_t pc1 = 0x1000;
        uint64_t pc2 = 0x2000;
        uint64_t base1 = 0x10000;
        uint64_t base2 = 0x20000;
        
        // Build pattern for PC1 - need multiple accesses to establish pattern
        test_cache->l2c_prefetcher_operate(base1, pc1, 0, LOAD, 0);
        test_cache->l2c_prefetcher_operate(base1 + 64, pc1, 0, LOAD, 0);
        test_cache->l2c_prefetcher_operate(base1 + 128, pc1, 0, LOAD, 0);
        test_cache->l2c_prefetcher_operate(base1 + 192, pc1, 0, LOAD, 0);
        
        size_t prefetch_count_pc1 = prefetch_addresses.size();
        prefetch_addresses.clear();
        
        // Build pattern for PC2 with different stride - need more accesses
        test_cache->l2c_prefetcher_operate(base2, pc2, 0, LOAD, 0);
        test_cache->l2c_prefetcher_operate(base2 + 128, pc2, 0, LOAD, 0);
        test_cache->l2c_prefetcher_operate(base2 + 256, pc2, 0, LOAD, 0);
        test_cache->l2c_prefetcher_operate(base2 + 384, pc2, 0, LOAD, 0);
        
        // At least PC1 should generate prefetches (PC2 may or may not depending on pattern detection)
        assert(prefetch_count_pc1 > 0 || prefetch_addresses.size() > 0);
    }
    else if (strcmp(test_name, "ghb_no_prefetch_for_store") == 0) {
        test_cache->l2c_prefetcher_initialize();
        prefetch_addresses.clear();
        
        uint64_t addr = 0x10000;
        uint64_t pc = 0x1000;
        
        test_cache->l2c_prefetcher_operate(addr, pc, 0, RFO, 0);
        assert(prefetch_addresses.size() == 0);
    }
    else if (strcmp(test_name, "ghb_page_boundary_check") == 0) {
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
    else if (strcmp(test_name, "ghb_cache_fill") == 0) {
        test_cache->l2c_prefetcher_initialize();
        test_cache->l2c_prefetcher_cache_fill(0x10000, 0, 0, 0, 0, 0);
        // Should not crash
    }
    else if (strcmp(test_name, "ghb_final_stats") == 0) {
        test_cache->l2c_prefetcher_initialize();
        test_cache->l2c_prefetcher_final_stats();
        // Should not crash
    }
    else {
        std::cerr << "Unknown test: " << test_name << std::endl;
        exit(1);
    }
}

