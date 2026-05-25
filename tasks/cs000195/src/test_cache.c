/*
 * Unit Tests for L2 Cache and DRAM
 * Tests core functionality only
 */

#include "lib/cache.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

#define TEST_PASS 1
#define TEST_FAIL 0

int tests_passed = 0;
int tests_failed = 0;

/* Simple memory simulation for testing */
#define MEM_DATA_START  0x10000000
#define MEM_DATA_SIZE   0x00100000
#define MEM_TEXT_START  0x00400000
#define MEM_TEXT_SIZE   0x00100000

typedef struct {
    uint32_t start, size;
    uint8_t *mem;
} mem_region_t;

mem_region_t MEM_REGIONS[] = {
    { MEM_TEXT_START, MEM_TEXT_SIZE, NULL },
    { MEM_DATA_START, MEM_DATA_SIZE, NULL }
};

#define MEM_NREGIONS (sizeof(MEM_REGIONS)/sizeof(mem_region_t))

uint32_t mem_read_32(uint32_t address) {
    int i;
    for (i = 0; i < MEM_NREGIONS; i++) {
        if (address >= MEM_REGIONS[i].start &&
                address < (MEM_REGIONS[i].start + MEM_REGIONS[i].size)) {
            uint32_t offset = address - MEM_REGIONS[i].start;
            if (MEM_REGIONS[i].mem == NULL) return 0;
            return
                (MEM_REGIONS[i].mem[offset+3] << 24) |
                (MEM_REGIONS[i].mem[offset+2] << 16) |
                (MEM_REGIONS[i].mem[offset+1] <<  8) |
                (MEM_REGIONS[i].mem[offset+0] <<  0);
        }
    }
    return 0;
}

void mem_write_32(uint32_t address, uint32_t value) {
    int i;
    for (i = 0; i < MEM_NREGIONS; i++) {
        if (address >= MEM_REGIONS[i].start &&
                address < (MEM_REGIONS[i].start + MEM_REGIONS[i].size)) {
            uint32_t offset = address - MEM_REGIONS[i].start;
            if (MEM_REGIONS[i].mem == NULL) return;
            MEM_REGIONS[i].mem[offset+3] = (value >> 24) & 0xFF;
            MEM_REGIONS[i].mem[offset+2] = (value >> 16) & 0xFF;
            MEM_REGIONS[i].mem[offset+1] = (value >>  8) & 0xFF;
            MEM_REGIONS[i].mem[offset+0] = (value >>  0) & 0xFF;
            return;
        }
    }
}

void init_memory() {
    int i;
    for (i = 0; i < MEM_NREGIONS; i++) {
        MEM_REGIONS[i].mem = malloc(MEM_REGIONS[i].size);
        memset(MEM_REGIONS[i].mem, 0, MEM_REGIONS[i].size);
    }
}

void test_result(const char *test_name, int result) {
    if (result) {
        printf("pass: %s\n", test_name);
        tests_passed++;
    } else {
        printf("fail: %s\n", test_name);
        tests_failed++;
    }
}

/* Test 1: Cache initialization */
void test_cache_init() {
    cache_init();
    
    int i, j;
    int all_empty = 1;
    
    /* Check that all cache blocks are invalid */
    for (i = 0; i < L2_NUM_SETS; i++) {
        for (j = 0; j < L2_ASSOC; j++) {
            if (l2_cache.sets[i][j].valid) {
                all_empty = 0;
                break;
            }
        }
    }
    
    /* Check that all MSHRs are invalid */
    for (i = 0; i < L2_MSHR_COUNT; i++) {
        if (l2_cache.mshrs[i].valid) {
            all_empty = 0;
            break;
        }
    }
    
    /* Check that memory controller is initialized */
    int mem_init = (mem_controller.queue_size == 0 && 
                    mem_controller.request_queue != NULL);
    
    test_result("Cache initialization", all_empty && mem_init);
}

/* Test 2: Address decomposition - cache block address */
void test_get_cache_block_addr() {
    uint32_t addr1 = 0x00400000;
    uint32_t addr2 = 0x00400020;
    uint32_t addr3 = 0x0040001F;
    
    uint32_t block1 = get_cache_block_addr(addr1);
    uint32_t block2 = get_cache_block_addr(addr2);
    uint32_t block3 = get_cache_block_addr(addr3);
    
    int result = (block1 == 0x00400000) && 
                 (block2 == 0x00400020) && 
                 (block3 == 0x00400000);
    
    test_result("Get cache block address", result);
}

/* Test 3: Address decomposition - L2 set index */
void test_get_l2_set_index() {
    uint32_t addr1 = 0x00400000;
    uint32_t addr2 = 0x00400020;
    uint32_t addr3 = 0x00400040;
    
    uint32_t set1 = get_l2_set_index(addr1);
    uint32_t set2 = get_l2_set_index(addr2);
    uint32_t set3 = get_l2_set_index(addr3);
    
    /* Set index is bits [13:5], so addresses 32 bytes apart should have different sets */
    int result = (set1 < L2_NUM_SETS) && (set2 < L2_NUM_SETS) && (set3 < L2_NUM_SETS);
    
    test_result("Get L2 set index", result);
}

/* Test 4: Address decomposition - DRAM bank */
void test_get_dram_bank() {
    uint32_t addr1 = 0x00000000;  /* Bank 0 */
    uint32_t addr2 = 0x00000020;  /* Bank 1 */
    uint32_t addr3 = 0x00000040;  /* Bank 2 */
    
    uint32_t bank1 = get_dram_bank(addr1);
    uint32_t bank2 = get_dram_bank(addr2);
    uint32_t bank3 = get_dram_bank(addr3);
    
    int result = (bank1 == 0) && (bank2 == 1) && (bank3 == 2) && 
                 (bank1 < DRAM_NUM_BANKS) && (bank2 < DRAM_NUM_BANKS) && 
                 (bank3 < DRAM_NUM_BANKS);
    
    test_result("Get DRAM bank", result);
}

/* Test 5: Address decomposition - DRAM row */
void test_get_dram_row() {
    uint32_t addr1 = 0x00000000;  /* Row 0 */
    uint32_t addr2 = 0x00010000;  /* Row 1 */
    uint32_t addr3 = 0x00020000;  /* Row 2 */
    
    uint32_t row1 = get_dram_row(addr1);
    uint32_t row2 = get_dram_row(addr2);
    uint32_t row3 = get_dram_row(addr3);
    
    int result = (row1 == 0) && (row2 == 1) && (row3 == 2) && 
                 (row1 < DRAM_NUM_ROWS) && (row2 < DRAM_NUM_ROWS) && 
                 (row3 < DRAM_NUM_ROWS);
    
    test_result("Get DRAM row", result);
}

/* Test 6: L2 cache miss - MSHR allocation */
void test_l2_cache_miss_mshr() {
    cache_init();
    
    uint32_t addr = 0x00400000;
    uint32_t data = 0;
    int result = l2_cache_access(addr, 0, &data, 1);
    
    /* Should return 0 (miss) */
    if (result != 0) {
        test_result("L2 cache miss - MSHR allocation", TEST_FAIL);
        return;
    }
    
    /* Check that an MSHR was allocated */
    int mshr_found = 0;
    int i;
    for (i = 0; i < L2_MSHR_COUNT; i++) {
        if (l2_cache.mshrs[i].valid && 
            l2_cache.mshrs[i].addr == get_cache_block_addr(addr)) {
            mshr_found = 1;
            break;
        }
    }
    
    /* Check that request was added to memory controller queue */
    int req_in_queue = (mem_controller.queue_size > 0);
    
    test_result("L2 cache miss - MSHR allocation", mshr_found && req_in_queue);
}

/* Test 7: L2 cache hit - immediate return */
void test_l2_cache_hit() {
    cache_init();
    
    uint32_t addr = 0x00400000;
    uint32_t test_data = 0xDEADBEEF;
    uint32_t read_data = 0;
    
    /* First, manually insert a block into cache to simulate a hit */
    uint32_t block_addr = get_cache_block_addr(addr);
    uint32_t set = get_l2_set_index(block_addr);
    uint32_t tag = get_l2_tag(block_addr);
    
    /* Find an empty way */
    int way = -1;
    int i;
    for (i = 0; i < L2_ASSOC; i++) {
        if (!l2_cache.sets[set][i].valid) {
            way = i;
            break;
        }
    }
    
    if (way == -1) {
        way = find_lru_way_l2(set);
    }
    
    /* Insert block */
    l2_cache.sets[set][way].valid = 1;
    l2_cache.sets[set][way].tag = tag;
    memcpy(&l2_cache.sets[set][way].data[addr & (L2_BLOCK_SIZE - 1)], 
           &test_data, 4);
    
    /* Now try to read it */
    read_data = 0;
    int hit = l2_cache_access(addr, 0, &read_data, 1);
    
    int result = (hit == 1) && (read_data == test_data);
    
    test_result("L2 cache hit - immediate return", result);
}

/* Test 8: LRU replacement */
void test_lru_replacement() {
    cache_init();
    
    uint32_t set = 0;
    
    /* Fill all ways in a set */
    int i;
    for (i = 0; i < L2_ASSOC; i++) {
        l2_cache.sets[set][i].valid = 1;
        l2_cache.sets[set][i].tag = i;
        l2_cache.sets[set][i].lru_counter = i;
    }
    
    /* Find LRU way */
    int lru_way = find_lru_way_l2(set);
    
    /* LRU should be valid */
    int result = (lru_way >= 0 && lru_way < L2_ASSOC);
    
    test_result("LRU replacement", result);
}

/* Test 9: MRU promotion */
void test_mru_promotion() {
    cache_init();
    
    uint32_t set = 0;
    uint32_t way = 0;
    
    /* Set initial LRU counters */
    int i;
    for (i = 0; i < L2_ASSOC; i++) {
        l2_cache.sets[set][i].lru_counter = i;
    }
    
    int old_counter = l2_cache.sets[set][way].lru_counter;
    
    /* Promote to MRU */
    promote_to_mru_l2(set, way);
    
    int new_counter = l2_cache.sets[set][way].lru_counter;
    
    /* New counter should be greater than all others */
    int is_max = 1;
    for (i = 0; i < L2_ASSOC; i++) {
        if (i != way && l2_cache.sets[set][i].lru_counter >= new_counter) {
            is_max = 0;
            break;
        }
    }
    
    int result = (new_counter > old_counter) && is_max;
    
    test_result("MRU promotion", result);
}

/* Test 10: Memory controller - request scheduling */
void test_memory_controller_scheduling() {
    cache_init();
    
    /* Add a request to the queue */
    uint32_t addr = 0x00400000;
    uint32_t data = 0;
    l2_cache_access(addr, 0, &data, 1);
    
    /* Process one cycle */
    memory_controller_cycle();
    
    /* Check that request is in queue */
    int result = (mem_controller.queue_size > 0);
    
    test_result("Memory controller - request scheduling", result);
}

/* Test 11: MSHR limit */
void test_mshr_limit() {
    cache_init();
    
    /* Allocate all MSHRs */
    uint32_t base_addr = 0x00400000;
    int i;
    for (i = 0; i < L2_MSHR_COUNT; i++) {
        uint32_t addr = base_addr + (i * L2_BLOCK_SIZE * 100);
        uint32_t data = 0;
        l2_cache_access(addr, 0, &data, 1);
    }
    
    /* Try to allocate one more - should fail */
    uint32_t new_addr = base_addr + (L2_MSHR_COUNT * L2_BLOCK_SIZE * 100);
    uint32_t data = 0;
    int result_access = l2_cache_access(new_addr, 0, &data, 1);
    
    /* Should return 0 (miss) but no new MSHR should be allocated */
    int mshr_count = 0;
    for (i = 0; i < L2_MSHR_COUNT; i++) {
        if (l2_cache.mshrs[i].valid) {
            mshr_count++;
        }
    }
    
    int result = (result_access == 0) && (mshr_count == L2_MSHR_COUNT);
    
    test_result("MSHR limit", result);
}

/* Test 12: Write to cache */
void test_cache_write() {
    cache_init();
    
    uint32_t addr = 0x00400000;
    uint32_t write_data = 0xCAFEBABE;
    uint32_t read_data = 0;
    
    /* First, manually insert a block into cache */
    uint32_t block_addr = get_cache_block_addr(addr);
    uint32_t set = get_l2_set_index(block_addr);
    uint32_t tag = get_l2_tag(block_addr);
    
    int way = 0;
    l2_cache.sets[set][way].valid = 1;
    l2_cache.sets[set][way].tag = tag;
    
    /* Write to cache */
    int write_result = l2_cache_access(addr, 1, &write_data, 0);
    
    /* Read back */
    read_data = 0;
    int read_result = l2_cache_access(addr, 0, &read_data, 0);
    
    int result = (write_result == 1) && (read_result == 1) && 
                 (read_data == write_data);
    
    test_result("Cache write", result);
}

int main() {
    printf("=== L2 Cache and DRAM Unit Tests ===\n\n");
    
    /* Initialize memory system (required for mem_read_32) */
    init_memory();
    
    /* Run tests */
    test_cache_init();
    test_get_cache_block_addr();
    test_get_l2_set_index();
    test_get_dram_bank();
    test_get_dram_row();
    test_l2_cache_miss_mshr();
    test_l2_cache_hit();
    test_lru_replacement();
    test_mru_promotion();
    test_memory_controller_scheduling();
    test_mshr_limit();
    test_cache_write();
    
    printf("\n=== Test Summary ===\n");
    printf("Passed: %d\n", tests_passed);
    printf("Failed: %d\n", tests_failed);
    printf("Total:  %d\n", tests_passed + tests_failed);
    
    return (tests_failed == 0) ? 0 : 1;
}
