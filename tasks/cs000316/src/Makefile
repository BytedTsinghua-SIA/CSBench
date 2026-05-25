# Makefile for CS 161 Project 1: Exploiting Memory Safety Vulnerabilities
# Compile all vulnerable satellite control programs

CC = gcc
CFLAGS = -Wall -Wextra -g -Wno-format-security
LDFLAGS = -pthread

# Programs to build
PROGRAMS = remus spica polaris vega deneb antares rigel

all: $(PROGRAMS)

# Individual program compilation
remus: remus.c
	$(CC) $(CFLAGS) -o $@ $<

spica: spica.c
	$(CC) $(CFLAGS) -o $@ $<

polaris: polaris.c
	$(CC) $(CFLAGS) -o $@ $<

vega: vega.c
	$(CC) $(CFLAGS) -o $@ $<

deneb: deneb.c
	$(CC) $(CFLAGS) -o $@ $<

antares: antares.c
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $<

rigel: rigel.c
	$(CC) $(CFLAGS) -o $@ $<

# Clean up compiled programs
clean:
	rm -f $(PROGRAMS) *.log

# Compile with address sanitizer for testing (optional)
asan: CFLAGS += -fsanitize=address -fsanitize=undefined
asan: clean all

.PHONY: all clean asan
