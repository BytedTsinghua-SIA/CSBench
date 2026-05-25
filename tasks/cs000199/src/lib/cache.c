/*
 * Cache and Memory Hierarchy Implementation
 * Lab 2: Memory Hierarchy - L2 Cache and DRAM
 */

#include "cache.h"
#include "shell.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

/* Global cache and memory structures */
L1_Cache l1_icache[NUM_CPUS];
L1_Cache l1_dcache[NUM_CPUS];
L2_Cache l2_cache;
Memory_Controller mem_controller;

#define MAX_MEM_REQUESTS 1000  /* large enough for infinite queue */

void cache_init() {
    int i;
    
    for (i = 0; i < NUM_CPUS; i++) {
        memset(&l1_icache[i], 0, sizeof(L1_Cache));
        memset(&l1_dcache[i], 0, sizeof(L1_Cache));
    }
    
    memset(&l2_cache, 0, sizeof(L2_Cache));
    
    mem_controller.request_queue = malloc(sizeof(Mem_Request) * MAX_MEM_REQUESTS);
    mem_controller.queue_size = 0;
    mem_controller.queue_capacity = MAX_MEM_REQUESTS;
    mem_controller.current_cycle = 0;
    for (i = 0; i < DRAM_NUM_BANKS; i++) {
        mem_controller.banks[i].row_buffer_valid = 0;
        mem_controller.banks[i].open_row = 0;
        mem_controller.banks[i].cycles_until_ready = 0;
        mem_controller.banks[i].last_command_cycle = 0;
    }
}

/* Get cache block address (aligned to block size) */
uint32_t get_cache_block_addr(uint32_t addr) {
    return addr & ~(L1_BLOCK_SIZE - 1);
}

/* L1 cache address decomposition */
uint32_t get_l1_set_index(uint32_t addr) {
    return (addr >> 5) & (L1_NUM_SETS - 1);  /* bits [12:5] */
}

uint32_t get_l1_tag(uint32_t addr) {
    return addr >> (5 + 7);  /* bits [31:13] */
}

/* L2 cache address decomposition */
uint32_t get_l2_set_index(uint32_t addr) {
    return (addr >> 5) & (L2_NUM_SETS - 1);  /* bits [13:5] */
}

uint32_t get_l2_tag(uint32_t addr) {
    return addr >> (5 + 9);  /* bits [31:14] */
}

/* DRAM address decomposition */
uint32_t get_dram_bank(uint32_t addr) {
    return (addr >> 5) & 0x7;  /* bits [7:5] */
}

uint32_t get_dram_row(uint32_t addr) {
    return (addr >> 16) & 0xFFFF;  /* bits [31:16] */
}

/* Update LRU for L1 cache */
void update_lru_l1(L1_Cache *cache, int set, int way) {
    int i;
    int max_lru = 0;
    for (i = 0; i < L1_ASSOC; i++) {
        if (cache->sets[set][i].lru_counter > max_lru)
            max_lru = cache->sets[set][i].lru_counter;
    }
    cache->sets[set][way].lru_counter = max_lru + 1;
}

/* Find LRU way in L1 cache */
int find_lru_way_l1(L1_Cache *cache, int set) {
    int i, lru_way = 0;
    int min_lru = cache->sets[set][0].lru_counter;
    for (i = 1; i < L1_ASSOC; i++) {
        if (cache->sets[set][i].lru_counter < min_lru) {
            min_lru = cache->sets[set][i].lru_counter;
            lru_way = i;
        }
    }
    return lru_way;
}

/* Promote block to MRU in L1 cache */
void promote_to_mru_l1(L1_Cache *cache, int set, int way) {
    int i;
    int max_lru = 0;
    for (i = 0; i < L1_ASSOC; i++) {
        if (cache->sets[set][i].lru_counter > max_lru)
            max_lru = cache->sets[set][i].lru_counter;
    }
    cache->sets[set][way].lru_counter = max_lru + 1;
}

/* Update LRU for L2 cache */
void update_lru_l2(int set, int way) {
    int i;
    int max_lru = 0;
    for (i = 0; i < L2_ASSOC; i++) {
        if (l2_cache.sets[set][i].lru_counter > max_lru)
            max_lru = l2_cache.sets[set][i].lru_counter;
    }
    l2_cache.sets[set][way].lru_counter = max_lru + 1;
}

/* Find LRU way in L2 cache */
int find_lru_way_l2(int set) {
    int i, lru_way = 0;
    int min_lru = l2_cache.sets[set][0].lru_counter;
    for (i = 1; i < L2_ASSOC; i++) {
        if (l2_cache.sets[set][i].lru_counter < min_lru) {
            min_lru = l2_cache.sets[set][i].lru_counter;
            lru_way = i;
        }
    }
    return lru_way;
}

/* Promote block to MRU in L2 cache */
void promote_to_mru_l2(int set, int way) {
    int i;
    int max_lru = 0;
    for (i = 0; i < L2_ASSOC; i++) {
        if (l2_cache.sets[set][i].lru_counter > max_lru)
            max_lru = l2_cache.sets[set][i].lru_counter;
    }
    l2_cache.sets[set][way].lru_counter = max_lru + 1;
}


int l1_cache_access(int cpu_id, uint32_t addr, int is_write, uint32_t *data, int is_instruction) {
    return 0;
}

int l2_cache_access(uint32_t addr, int is_write, uint32_t *data, int is_instruction) {
    return 0;
}

int is_request_schedulable(Mem_Request *req) {
    return 0;
}

void schedule_dram_access(Mem_Request *req) {
}

void process_memory_requests() {
}

void memory_controller_cycle() {
    mem_controller.current_cycle++;
}
