CC = gcc
CFLAGS = -O2 -Wall -Wextra
OMPFLAGS = -fopenmp
LIBS = -lm

SERIAL = quake_serial
OMP = quake_omp

SERIAL_SRC = quake_serial.c
OMP_SRC = quake_omp.c

.PHONY: all clean serial omp

all: serial omp

serial: $(SERIAL)

omp: $(OMP)

$(SERIAL): $(SERIAL_SRC)
	$(CC) $(CFLAGS) -o $@ $< $(LIBS)

$(OMP): $(OMP_SRC)
	$(CC) $(CFLAGS) $(OMPFLAGS) -o $@ $< $(LIBS)

clean:
	rm -f $(SERIAL) $(OMP)
