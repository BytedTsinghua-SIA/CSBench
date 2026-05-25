#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Satellite navigation system for Spica
// This program contains a format string vulnerability

void log_navigation_data(char *data) {
}

void adjust_trajectory() {
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <navigation_data>\n", argv[0]);
        return 1;
    }

    return 0;
}
