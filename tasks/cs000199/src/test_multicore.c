#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "lib/cache.h"
#include "lib/pipe.h"

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
    { MEM_DATA_START, MEM_DATA_SIZE, NULL },
};

#define MEM_NREGIONS (sizeof(MEM_REGIONS)/sizeof(mem_region_t))

uint32_t mem_read_32(uint32_t address) {
    int i;
    for (i = 0; i < MEM_NREGIONS; i++) {
        if (address >= MEM_REGIONS[i].start &&
                address < (MEM_REGIONS[i].start + MEM_REGIONS[i].size)) {
            uint32_t offset = address - MEM_REGIONS[i].start;
            return (MEM_REGIONS[i].mem[offset+3] << 24) |
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

uint32_t stat_cycles = 0, stat_inst_retire = 0, stat_inst_fetch = 0;
uint32_t stat_squash = 0;

int test_multicore_init() {
    printf("Test 1: Multicore Initialization\n");
    
    init_memory();
    pipe_init();
    
    if (pipes[0].PC != 0x00400000) return 1;
    if (pipes[1].PC != 0x00400000) return 1;
    if (pipes[2].PC != 0x00400000) return 1;
    if (pipes[3].PC != 0x00400000) return 1;
    
    if (cpu_running[0] != 1) return 1;
    if (cpu_running[1] != 0) return 1;
    if (cpu_running[2] != 0) return 1;
    if (cpu_running[3] != 0) return 1;
    
    printf("  PASS: All CPUs initialized correctly\n");
    return 0;
}

int test_l1_cache_basic() {
    printf("Test 2: L1 Cache Basic Access\n");
    
    init_memory();
    cache_init();
    
    uint32_t data = 0x12345678;
    uint32_t read_data = 0;
    uint32_t addr = 0x10000000;
    
    int hit = l1_cache_access(0, addr, 1, &data, 0);
    if (hit != 0) return 1;
    
    for (int i = 0; i < 200; i++) {
        memory_controller_cycle();
        hit = l1_cache_access(0, addr, 0, &read_data, 0);
        if (hit == 1) break;
    }
    
    if (hit != 1) return 1;
    
    printf("  PASS: L1 cache write and read successful\n");
    return 0;
}

int test_mesi_exclusive() {
    printf("Test 3: MESI Exclusive State\n");
    
    init_memory();
    cache_init();
    
    uint32_t data = 0xABCDEF00;
    uint32_t read_data = 0;
    uint32_t addr = 0x10000100;
    
    int hit = l1_cache_access(0, addr, 0, &read_data, 0);
    if (hit != 0) return 1;
    
    for (int i = 0; i < 200; i++) {
        memory_controller_cycle();
        hit = l1_cache_access(0, addr, 0, &read_data, 0);
        if (hit == 1) break;
    }
    
    if (hit != 1) return 1;
    
    uint32_t set = get_l1_set_index(addr);
    uint32_t tag = get_l1_tag(addr);
    int found = 0;
    int mesi_state = -1;
    
    for (int i = 0; i < L1_ASSOC; i++) {
        if (l1_dcache[0].sets[set][i].valid && 
            l1_dcache[0].sets[set][i].tag == tag) {
            found = 1;
            mesi_state = l1_dcache[0].sets[set][i].mesi_state;
            break;
        }
    }
    
    if (found != 1) return 1;
    if (mesi_state != MESI_EXCLUSIVE) return 1;
    
    printf("  PASS: Block in Exclusive state after read\n");
    return 0;
}

int test_mesi_shared() {
    printf("Test 4: MESI Shared State\n");
    
    init_memory();
    cache_init();
    
    uint32_t addr = 0x10000200;
    uint32_t data1 = 0, data2 = 0;
    
    int hit1 = l1_cache_access(0, addr, 0, &data1, 0);
    if (hit1 != 0) return 1;
    
    for (int i = 0; i < 200; i++) {
        memory_controller_cycle();
        hit1 = l1_cache_access(0, addr, 0, &data1, 0);
        if (hit1 == 1) break;
    }
    if (hit1 != 1) return 1;
    
    int hit2 = l1_cache_access(1, addr, 0, &data2, 0);
    if (hit2 != 0) return 1;
    
    for (int i = 0; i < 200; i++) {
        memory_controller_cycle();
        hit2 = l1_cache_access(1, addr, 0, &data2, 0);
        if (hit2 == 1) break;
    }
    if (hit2 != 1) return 1;
    
    uint32_t set = get_l1_set_index(addr);
    uint32_t tag = get_l1_tag(addr);
    
    int state0 = -1, state1 = -1;
    for (int i = 0; i < L1_ASSOC; i++) {
        if (l1_dcache[0].sets[set][i].valid && 
            l1_dcache[0].sets[set][i].tag == tag) {
            state0 = l1_dcache[0].sets[set][i].mesi_state;
        }
        if (l1_dcache[1].sets[set][i].valid && 
            l1_dcache[1].sets[set][i].tag == tag) {
            state1 = l1_dcache[1].sets[set][i].mesi_state;
        }
    }
    
    if (state0 != MESI_SHARED) return 1;
    if (state1 != MESI_SHARED) return 1;
    
    printf("  PASS: Both caches in Shared state\n");
    return 0;
}

int test_mesi_modified() {
    printf("Test 5: MESI Modified State\n");
    
    init_memory();
    cache_init();
    
    uint32_t addr = 0x10000300;
    uint32_t write_data = 0xDEADBEEF;
    uint32_t read_data = 0;
    
    int hit = l1_cache_access(0, addr, 0, &read_data, 0);
    if (hit != 0) return 1;
    
    for (int i = 0; i < 200; i++) {
        memory_controller_cycle();
        hit = l1_cache_access(0, addr, 0, &read_data, 0);
        if (hit == 1) break;
    }
    if (hit != 1) return 1;
    
    hit = l1_cache_access(0, addr, 1, &write_data, 0);
    if (hit != 1) return 1;
    
    uint32_t set = get_l1_set_index(addr);
    uint32_t tag = get_l1_tag(addr);
    int mesi_state = -1;
    
    for (int i = 0; i < L1_ASSOC; i++) {
        if (l1_dcache[0].sets[set][i].valid && 
            l1_dcache[0].sets[set][i].tag == tag) {
            mesi_state = l1_dcache[0].sets[set][i].mesi_state;
            break;
        }
    }
    
    if (mesi_state != MESI_MODIFIED) return 1;
    
    printf("  PASS: Block upgraded to Modified state after write\n");
    return 0;
}

int test_mesi_invalidation() {
    printf("Test 6: MESI Invalidation\n");
    
    init_memory();
    cache_init();
    
    uint32_t addr = 0x10000400;
    uint32_t data = 0;
    
    int hit0 = l1_cache_access(0, addr, 0, &data, 0);
    if (hit0 != 0) return 1;
    for (int i = 0; i < 200; i++) {
        memory_controller_cycle();
        hit0 = l1_cache_access(0, addr, 0, &data, 0);
        if (hit0 == 1) break;
    }
    if (hit0 != 1) return 1;
    
    int hit1 = l1_cache_access(1, addr, 0, &data, 0);
    if (hit1 != 0) return 1;
    for (int i = 0; i < 200; i++) {
        memory_controller_cycle();
        hit1 = l1_cache_access(1, addr, 0, &data, 0);
        if (hit1 == 1) break;
    }
    if (hit1 != 1) return 1;
    
    uint32_t write_data = 0xCAFEBABE;
    l1_cache_access(0, addr, 1, &write_data, 0);
    
    uint32_t set = get_l1_set_index(addr);
    uint32_t tag = get_l1_tag(addr);
    
    int found_in_cpu1 = 0;
    for (int i = 0; i < L1_ASSOC; i++) {
        if (l1_dcache[1].sets[set][i].valid && 
            l1_dcache[1].sets[set][i].tag == tag) {
            found_in_cpu1 = 1;
            break;
        }
    }
    
    if (found_in_cpu1 != 0) return 1;
    
    printf("  PASS: CPU 1 cache invalidated when CPU 0 writes\n");
    return 0;
}

int test_l1_mshr() {
    printf("Test 7: L1 MSHR Functionality\n");
    
    init_memory();
    cache_init();
    
    uint32_t addr = 0x10000500;
    uint32_t data = 0;
    
    if (l1_dcache[0].mshr.valid != 0) return 1;
    
    int hit = l1_cache_access(0, addr, 0, &data, 0);
    if (hit != 0) return 1;
    if (l1_dcache[0].mshr.valid != 1) return 1;
    if (l1_dcache[0].mshr.addr != get_cache_block_addr(addr)) return 1;
    
    for (int i = 0; i < 200; i++) {
        memory_controller_cycle();
        if (l1_dcache[0].mshr.valid == 0) break;
    }
    
    if (l1_dcache[0].mshr.valid != 0) return 1;
    
    printf("  PASS: L1 MSHR allocated and released correctly\n");
    return 0;
}

int test_multicore_independence() {
    printf("Test 8: Multicore Register Independence\n");
    
    init_memory();
    pipe_init();
    
    pipes[0].REGS[5] = 0x11111111;
    pipes[1].REGS[5] = 0x22222222;
    pipes[2].REGS[5] = 0x33333333;
    pipes[3].REGS[5] = 0x44444444;
    
    if (pipes[0].REGS[5] != 0x11111111) return 1;
    if (pipes[1].REGS[5] != 0x22222222) return 1;
    if (pipes[2].REGS[5] != 0x33333333) return 1;
    if (pipes[3].REGS[5] != 0x44444444) return 1;
    
    printf("  PASS: Each CPU has independent register file\n");
    return 0;
}

int test_l2_cache_dirty_bit() {
    printf("Test 9: L2 Cache Dirty Bit\n");
    
    init_memory();
    cache_init();
    
    uint32_t addr = 0x10000600;
    uint32_t write_data = 0x12345678;
    
    int hit = l1_cache_access(0, addr, 1, &write_data, 0);
    if (hit != 0) return 1;
    
    for (int i = 0; i < 200; i++) {
        memory_controller_cycle();
        hit = l1_cache_access(0, addr, 0, &write_data, 0);
        if (hit == 1) break;
    }
    
    uint32_t set = get_l2_set_index(addr);
    uint32_t tag = get_l2_tag(addr);
    
    int found = 0;
    int dirty = 0;
    for (int i = 0; i < L2_ASSOC; i++) {
        if (l2_cache.sets[set][i].valid && 
            l2_cache.sets[set][i].tag == tag) {
            found = 1;
            dirty = l2_cache.sets[set][i].dirty;
            break;
        }
    }
    
    if (found != 1) return 1;
    
    printf("  PASS: L2 cache dirty bit functionality\n");
    return 0;
}

int test_instruction_cache() {
    printf("Test 10: L1 Instruction Cache\n");
    
    init_memory();
    cache_init();
    
    uint32_t addr = 0x00400000;
    uint32_t instruction = 0;
    
    int hit = l1_cache_access(0, addr, 0, &instruction, 1);
    if (hit != 0) return 1;
    
    for (int i = 0; i < 200; i++) {
        memory_controller_cycle();
        hit = l1_cache_access(0, addr, 0, &instruction, 1);
        if (hit == 1) break;
    }
    
    if (hit != 1) return 1;
    
    uint32_t set = get_l1_set_index(addr);
    uint32_t tag = get_l1_tag(addr);
    int found = 0;
    
    for (int i = 0; i < L1_ASSOC; i++) {
        if (l1_icache[0].sets[set][i].valid && 
            l1_icache[0].sets[set][i].tag == tag) {
            found = 1;
            break;
        }
    }
    
    if (found != 1) return 1;
    
    printf("  PASS: Instruction cache working correctly\n");
    return 0;
}

int main(int argc, char *argv[]) {
    int test_num = -1;
    int result = 0;
    
    if (argc > 1) {
        test_num = atoi(argv[1]);
    }
    
    if (test_num == -1) {
        printf("=== Multicore and Cache Coherence Unit Tests ===\n\n");
        
        result |= test_multicore_init();
        result |= test_l1_cache_basic();
        result |= test_mesi_exclusive();
        result |= test_mesi_shared();
        result |= test_mesi_modified();
        result |= test_mesi_invalidation();
        result |= test_l1_mshr();
        result |= test_multicore_independence();
        result |= test_l2_cache_dirty_bit();
        result |= test_instruction_cache();
        
        if (result == 0) {
            printf("\n=== All Tests Passed ===\n");
        } else {
            printf("\n=== Some Tests Failed ===\n");
        }
    } else {
        switch (test_num) {
            case 1: result = test_multicore_init(); break;
            case 2: result = test_l1_cache_basic(); break;
            case 3: result = test_mesi_exclusive(); break;
            case 4: result = test_mesi_shared(); break;
            case 5: result = test_mesi_modified(); break;
            case 6: result = test_mesi_invalidation(); break;
            case 7: result = test_l1_mshr(); break;
            case 8: result = test_multicore_independence(); break;
            case 9: result = test_l2_cache_dirty_bit(); break;
            case 10: result = test_instruction_cache(); break;
            default:
                fprintf(stderr, "Invalid test number: %d\n", test_num);
                return 1;
        }
    }
    
    return result;
}

