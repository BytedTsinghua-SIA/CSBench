/*
 * Cache and Memory Hierarchy Implementation
 * Lab 6: Multicore and Cache Coherence
 */

#ifndef _CACHE_H_
#define _CACHE_H_

#include <stdint.h>

#define NUM_CPUS 4

/* L1 Cache Configuration */
#define L1_SIZE (16 * 1024)  /* 16KB */
#define L1_BLOCK_SIZE 32  /* 32 bytes */
#define L1_ASSOC 4  /* 4-way set-associative */
#define L1_NUM_SETS (L1_SIZE / (L1_BLOCK_SIZE * L1_ASSOC))  /* 128 sets */
#define L1_MSHR_COUNT 1  /* 1 MSHR per L1 cache */

/* L2 Cache Configuration */
#define L2_SIZE (256 * 1024)  /* 256KB */
#define L2_BLOCK_SIZE 32  /* 32 bytes */
#define L2_ASSOC 16  /* 16-way set-associative */
#define L2_NUM_SETS (L2_SIZE / (L2_BLOCK_SIZE * L2_ASSOC))  /* 512 sets */
#define L2_MSHR_COUNT 16  /* 16 MSHRs */
#define L2_HIT_LATENCY 15  /* 15 cycles */
#define L2_TO_MEM_LATENCY 5  /* 5 cycles to send request to memory */
#define L2_FROM_MEM_LATENCY 5  /* 5 cycles from memory to L2 */

/* MESI Protocol States */
#define MESI_INVALID 0
#define MESI_MODIFIED 1
#define MESI_EXCLUSIVE 2
#define MESI_SHARED 3

/* DRAM Configuration */
#define DRAM_NUM_BANKS 8
#define DRAM_NUM_ROWS 65536  /* 64K rows */
#define DRAM_ROW_SIZE (8 * 1024)  /* 8KB per row */
#define DRAM_BANK_INDEX_BITS 3  /* bits [7:5] */
#define DRAM_ROW_INDEX_BITS 16  /* bits [31:16] */

/* DRAM Timing Parameters */
#define DRAM_tRCD 12  /* Row to Column Delay */
#define DRAM_tCL 12  /* Column Access Strobe Latency */
#define DRAM_tRP 12  /* Row Precharge Time */
#define DRAM_tRAS 28  /* Row Active Time */
#define DRAM_BUS_BYTES 8  /* 8 bytes per bus transfer */
#define DRAM_BURST_LENGTH 4  /* 4 transfers per burst */

/* L1 Cache Block Structure */
typedef struct {
    int valid;
    uint32_t tag;
    uint8_t data[32];  /* 32-byte block */
    int mesi_state;  /* MESI protocol state */
    int lru_counter;  /* for LRU replacement */
} L1_Cache_Block;

/* L2 Cache Block Structure */
typedef struct {
    int valid;
    uint32_t tag;
    uint8_t data[32];  /* 32-byte block */
    int dirty;  /* dirty bit for L2 */
    int lru_counter;  /* for LRU replacement */
} L2_Cache_Block;

/* L1 MSHR Entry */
typedef struct {
    int valid;
    uint32_t addr;  /* cache block address */
    int is_write;  /* 0 = read, 1 = write */
    int cycles_until_ready;  /* cycles until data is ready */
} L1_MSHR_Entry;

/* L2 MSHR Entry */
typedef struct {
    int valid;
    uint32_t addr;  /* cache block address */
    int done;  /* fill notification received */
    int cycles_until_mem_req;  /* cycles until memory request sent */
    int cycles_until_fill;  /* cycles until fill completes */
    int is_instruction;  /* 0 = instruction, 1 = data */
    int is_hit;  /* 1 if L2 hit, 0 if L2 miss */
} L2_MSHR_Entry;

/* L1 Cache Structure */
typedef struct {
    L1_Cache_Block sets[L1_NUM_SETS][L1_ASSOC];
    L1_MSHR_Entry mshr;  /* single MSHR per L1 cache */
} L1_Cache;

/* L2 Cache Structure */
typedef struct {
    L2_Cache_Block sets[L2_NUM_SETS][L2_ASSOC];
    L2_MSHR_Entry mshrs[L2_MSHR_COUNT];
} L2_Cache;

/* DRAM Bank State */
typedef struct {
    int row_buffer_valid;  /* is row buffer valid? */
    uint32_t open_row;  /* currently open row */
    int cycles_until_ready;  /* cycles until bank is ready for next command */
    int last_command_cycle;  /* cycle when last command was issued */
} DRAM_Bank;

/* Memory Request */
typedef struct {
    uint32_t addr;  /* address */
    int is_write;  /* 0 = read, 1 = write */
    int bank;  /* bank index */
    uint32_t row;  /* row index */
    int row_buffer_hit;  /* 1 if row buffer hit, 0 otherwise */
    int cycles_until_ready;  /* cycles until request can be scheduled */
    int scheduled;  /* 1 if scheduled, 0 otherwise */
    int mshr_id;  /* MSHR ID for this request */
} Mem_Request;

/* Memory Controller */
typedef struct {
    Mem_Request *request_queue;  /* infinite queue (we'll use a large array) */
    int queue_size;
    int queue_capacity;
    DRAM_Bank banks[DRAM_NUM_BANKS];
    int current_cycle;
} Memory_Controller;

/* Global cache and memory structures */
extern L1_Cache l1_icache[NUM_CPUS];  /* L1 instruction caches */
extern L1_Cache l1_dcache[NUM_CPUS];  /* L1 data caches */
extern L2_Cache l2_cache;
extern Memory_Controller mem_controller;

/* Function declarations */
void cache_init();
int l1_cache_access(int cpu_id, uint32_t addr, int is_write, uint32_t *data, int is_instruction);
int l2_cache_access(uint32_t addr, int is_write, uint32_t *data, int is_instruction);
void memory_controller_cycle();
void process_memory_requests();
int is_request_schedulable(Mem_Request *req);
void schedule_dram_access(Mem_Request *req);
uint32_t get_cache_block_addr(uint32_t addr);
uint32_t get_l1_set_index(uint32_t addr);
uint32_t get_l1_tag(uint32_t addr);
uint32_t get_l2_set_index(uint32_t addr);
uint32_t get_l2_tag(uint32_t addr);
uint32_t get_dram_bank(uint32_t addr);
uint32_t get_dram_row(uint32_t addr);
void update_lru_l1(L1_Cache *cache, int set, int way);
int find_lru_way_l1(L1_Cache *cache, int set);
void promote_to_mru_l1(L1_Cache *cache, int set, int way);
void update_lru_l2(int set, int way);
int find_lru_way_l2(int set);
void promote_to_mru_l2(int set, int way);

#endif /* _CACHE_H_ */

