SRC = $(wildcard lib/*.c)
INPUT ?= $(wildcard inputs/*/*.x)

.PHONY: all verify clean test

all: sim

sim: $(SRC)
	gcc -g -O2 $^ -o $@

basesim: $(SRC)
	gcc -g -O2 $^ -o $@

test: test_multicore
	./test_multicore

test_python: test_multicore
	python3 test_multicore_python.py

test_multicore: test_multicore.c lib/cache.c lib/pipe.c
	gcc -g -O2 -I. test_multicore.c lib/cache.c lib/pipe.c -o test_multicore

test_cache: test_cache.c lib/cache.c
	gcc -g -O2 -I. test_cache.c lib/cache.c -o test_cache

run: sim
	@python run.py $(INPUT)

clean:
	rm -rf *.o *~ sim basesim test_cache test_multicore *.dSYM

