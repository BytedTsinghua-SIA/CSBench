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
L2_Cache l2_cache;
Memory_Controller mem_controller;

#define MAX_MEM_REQUESTS 1000  /* large enough for infinite queue */

/* Initialize all caches and memory */
void cache_init() {
    int i;
    
    /* Initialize L2 cache */
    memset(&l2_cache, 0, sizeof(L2_Cache));
    
    /* Initialize memory controller */
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
    return addr & ~(L2_BLOCK_SIZE - 1);
}

/* L2 cache address decomposition */
uint32_t get_l2_set_index(uint32_t addr) {
    return L2_NUM_SETS;
}

uint32_t get_l2_tag(uint32_t addr) {
    return 0;
}

/* DRAM address decomposition */
uint32_t get_dram_bank(uint32_t addr) {
    return 0;
}

uint32_t get_dram_row(uint32_t addr) {
    return 0;
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
    return -1;
}

/* Promote block to MRU in L2 cache */
void promote_to_mru_l2(int set, int way) {
    return;
}

/* L2 cache access - returns 1 on hit, 0 on miss (stall required) */
int l2_cache_access(uint32_t addr, int is_write, uint32_t *data, int is_instruction) {
    return 0;
}

/* Check if a memory request is schedulable */
int is_request_schedulable(Mem_Request *req) {
    DRAM_Bank *bank = &mem_controller.banks[req->bank];
    
    if (bank->cycles_until_ready > 0) {
        return 0;  /* Bank not ready */
    }
    
    return 1;  /* Schedulable */
}

/* Schedule DRAM access for a request */
void schedule_dram_access(Mem_Request *req) {
    DRAM_Bank *bank = &mem_controller.banks[req->bank];
    int cycles_needed = 0;
    
    /* Check row buffer status */
    if (!bank->row_buffer_valid || bank->open_row != req->row) {
        /* Row buffer miss - need to precharge and activate */
        if (bank->row_buffer_valid) {
            /* Precharge current row */
            cycles_needed = DRAM_tRP;
            bank->cycles_until_ready = DRAM_tRP;
        }
        /* Activate new row */
        cycles_needed += DRAM_tRCD;
        bank->row_buffer_valid = 1;
        bank->open_row = req->row;
        bank->cycles_until_ready += DRAM_tRCD;
    } else {
        /* Row buffer hit */
        cycles_needed = 0;
    }
    
    /* Column access */
    cycles_needed += DRAM_tCL;
    bank->cycles_until_ready += DRAM_tCL;
    
    /* Burst transfer (4 transfers * 8 bytes = 32 bytes) */
    int burst_cycles = DRAM_BURST_LENGTH;
    bank->cycles_until_ready += burst_cycles;
    
    /* Update request */
    req->scheduled = 1;
    req->cycles_until_ready = bank->cycles_until_ready;
    bank->last_command_cycle = mem_controller.current_cycle;
}

/* Process memory requests */
void process_memory_requests() {
    int i;
    
    /* Update bank states */
    for (i = 0; i < DRAM_NUM_BANKS; i++) {
        if (mem_controller.banks[i].cycles_until_ready > 0) {
            mem_controller.banks[i].cycles_until_ready--;
        }
    }
    
    /* Process completed requests */
    for (i = 0; i < mem_controller.queue_size; i++) {
        Mem_Request *req = &mem_controller.request_queue[i];
        if (req->scheduled && req->cycles_until_ready > 0) {
            req->cycles_until_ready--;
            if (req->cycles_until_ready == 0) {
                /* Request completed - send fill to L2 */
                int mshr_id = req->mshr_id;
                if (mshr_id >= 0 && mshr_id < L2_MSHR_COUNT && l2_cache.mshrs[mshr_id].valid) {
                    l2_cache.mshrs[mshr_id].done = 1;
                    l2_cache.mshrs[mshr_id].cycles_until_fill = L2_FROM_MEM_LATENCY;
                }
            }
        }
    }
    
    /* Schedule new requests (FR-FCFS policy) */
    /* First priority: row buffer hits */
    for (i = 0; i < mem_controller.queue_size; i++) {
        Mem_Request *req = &mem_controller.request_queue[i];
        if (!req->scheduled && is_request_schedulable(req)) {
            DRAM_Bank *bank = &mem_controller.banks[req->bank];
            if (bank->row_buffer_valid && bank->open_row == req->row) {
                req->row_buffer_hit = 1;
                schedule_dram_access(req);
                break;  /* Schedule one at a time */
            }
        }
    }
    
    /* Second priority: oldest ready request */
    if (i >= mem_controller.queue_size) {
        for (i = 0; i < mem_controller.queue_size; i++) {
            Mem_Request *req = &mem_controller.request_queue[i];
            if (!req->scheduled && is_request_schedulable(req)) {
                schedule_dram_access(req);
                break;
            }
        }
    }
}

/* Memory controller cycle */
void memory_controller_cycle() {
    return;
}
