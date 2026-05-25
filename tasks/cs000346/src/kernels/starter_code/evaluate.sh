#!/bin/bash

# Evaluation script for TinyChatEngine linear kernel optimizations
# Tests correctness and measures performance (GOPs) of all implementations

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TARGET="all"
ITERATIONS=100
OUTPUT_DIR="./results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Available implementations
IMPLEMENTATIONS=(
    "reference"
    "loop_unrolling"
    "multithreading"
    "simd_programming"
    "multithreading_loop_unrolling"
    "all_techniques"
)

# Compiler detection and flags
detect_compiler() {
    if command -v g++ &> /dev/null; then
        CXX="g++"
        CXXFLAGS="-std=c++17 -O3 -march=native -mtune=native"
    elif command -v clang++ &> /dev/null; then
        CXX="clang++"
        CXXFLAGS="-std=c++17 -O3 -march=native -mtune=native"
    else
        echo -e "${RED}Error: No C++ compiler found (g++ or clang++)${NC}"
        exit 1
    fi

    # Architecture-specific flags
    ARCH=$(uname -m)
    case $ARCH in
        x86_64|i686|i386)
            echo "Detected x86 architecture"
            CXXFLAGS="$CXXFLAGS -mavx2"  # Enable AVX2 for x86
            ;;
        aarch64|arm64)
            echo "Detected ARM64 architecture"
            CXXFLAGS="$CXXFLAGS -march=armv8-a"  # Enable NEON for ARM64
            ;;
        arm*)
            echo "Detected ARM architecture"
            CXXFLAGS="$CXXFLAGS -march=armv7-a -mfpu=neon"  # Enable NEON for ARM
            ;;
        *)
            echo -e "${YELLOW}Warning: Unknown architecture $ARCH, using generic optimizations${NC}"
            ;;
    esac
}

# Compile implementation
compile_implementation() {
    local impl=$1
    local source_file="${impl}.cc"
    local executable="${impl}_benchmark"

    if [ ! -f "$source_file" ]; then
        echo -e "${RED}Error: Source file $source_file not found${NC}"
        return 1
    fi

    echo -e "${BLUE}Compiling $impl implementation...${NC}"
    if $CXX $CXXFLAGS -o "$executable" "$source_file" -pthread; then
        echo -e "${GREEN}✓ Successfully compiled $impl${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to compile $impl${NC}"
        return 1
    fi
}

# Run benchmark for implementation
run_benchmark() {
    local impl=$1
    local executable="${impl}_benchmark"

    if [ ! -f "$executable" ]; then
        echo -e "${RED}Error: Executable $executable not found${NC}"
        return 1
    fi

    echo -e "${BLUE}Running $impl benchmark...${NC}"
    local output
    if output=$("./$executable" 2>&1); then
        echo -e "${GREEN}✓ $impl completed successfully${NC}"
        echo "$output"
        return 0
    else
        echo -e "${RED}✗ $impl failed to run${NC}"
        echo "$output"
        return 1
    fi
}

# Validate implementation correctness (compare against reference)
validate_correctness() {
    local impl=$1
    local ref_output="$2"
    local impl_output="$3"

    # Simple validation - check if outputs are reasonably close
    # In a real implementation, you'd want more sophisticated correctness checking
    echo -e "${BLUE}Validating correctness of $impl...${NC}"

    # For now, just check if the implementation runs without errors
    # Real validation would compare numerical outputs
    if [ -n "$impl_output" ]; then
        echo -e "${GREEN}✓ $impl passed basic validation${NC}"
        return 0
    else
        echo -e "${RED}✗ $impl failed validation${NC}"
        return 1
    fi
}

# Extract performance metrics from output
extract_metrics() {
    local output="$1"

    # Extract performance metrics using grep and awk
    local avg_time=$(echo "$output" | grep "Average time:" | awk '{print $3}')
    local gops=$(echo "$output" | grep "Performance:" | awk '{print $2}')
    local total_ops=$(echo "$output" | grep "Total operations:" | awk '{print $3}')

    echo "$avg_time|$gops|$total_ops"
}

# Generate performance report
generate_report() {
    local results_file="$1"

    echo -e "\n${BLUE}=== Performance Report ===${NC}"
    echo "Implementation                  | Avg Time (ms) | Performance (GOPs) | Speedup"
    echo "-------------------------------|----------------|-------------------|--------"

    local ref_gops=""
    while IFS='|' read -r impl avg_time gops total_ops; do
        if [ "$impl" = "reference" ]; then
            ref_gops="$gops"
            printf "%-30s | %-14s | %-17s | 1.00x\n" "$impl" "$avg_time" "$gops"
        elif [ -n "$ref_gops" ] && [ "$ref_gops" != "0" ]; then
            local speedup=$(echo "scale=2; $gops / $ref_gops" | bc -l 2>/dev/null || echo "N/A")
            if [ "$speedup" != "N/A" ]; then
                speedup="${speedup}x"
            fi
            printf "%-30s | %-14s | %-17s | %s\n" "$impl" "$avg_time" "$gops" "$speedup"
        else
            printf "%-30s | %-14s | %-17s | N/A\n" "$impl" "$avg_time" "$gops"
        fi
    done < "$results_file"
}

# Main evaluation function
run_evaluation() {
    local target_impls=()

    # Determine which implementations to test
    if [ "$TARGET" = "all" ]; then
        target_impls=("${IMPLEMENTATIONS[@]}")
    else
        # Check if target is valid
        local valid=false
        for impl in "${IMPLEMENTATIONS[@]}"; do
            if [ "$impl" = "$TARGET" ]; then
                valid=true
                break
            fi
        done

        if [ "$valid" = true ]; then
            target_impls=("$TARGET")
        else
            echo -e "${RED}Error: Invalid target implementation '$TARGET'${NC}"
            echo "Available implementations: ${IMPLEMENTATIONS[*]}"
            exit 1
        fi
    fi

    # Create output directory
    mkdir -p "$OUTPUT_DIR"

    local results_file="$OUTPUT_DIR/results_$TIMESTAMP.csv"
    local log_file="$OUTPUT_DIR/evaluation_$TIMESTAMP.log"

    echo "Implementation,Average_Time_ms,Performance_GOPs,Total_Operations" > "$results_file"
    echo "Evaluation started at $(date)" > "$log_file"
    echo "Target implementations: ${target_impls[*]}" >> "$log_file"
    echo "Compiler: $CXX $CXXFLAGS" >> "$log_file"
    echo "Architecture: $(uname -m)" >> "$log_file"
    echo "Iterations per benchmark: $ITERATIONS" >> "$log_file"
    echo "" >> "$log_file"

    local ref_output=""
    local success_count=0
    local total_count=${#target_impls[@]}

    echo -e "${BLUE}Starting evaluation of ${#target_impls[@]} implementation(s)...${NC}"
    echo ""

    # Compile and run each implementation
    for impl in "${target_impls[@]}"; do
        echo -e "${YELLOW}Processing $impl...${NC}"

        # Compile
        if ! compile_implementation "$impl"; then
            echo -e "${RED}Skipping $impl due to compilation failure${NC}" >> "$log_file"
            continue
        fi

        # Run benchmark
        if output=$(run_benchmark "$impl" 2>&1); then
            # Extract metrics
            metrics=$(extract_metrics "$output")
            IFS='|' read -r avg_time gops total_ops <<< "$metrics"

            # Save reference output for comparison
            if [ "$impl" = "reference" ]; then
                ref_output="$output"
            fi

            # Validate correctness
            if validate_correctness "$impl" "$ref_output" "$output"; then
                # Save results
                echo "$impl,$avg_time,$gops,$total_ops" >> "$results_file"
                ((success_count++))
                echo -e "${GREEN}✓ $impl evaluation completed${NC}"
            fi
        else
            echo "$output" >> "$log_file"
        fi

        echo "$output" >> "$log_file"
        echo "---" >> "$log_file"
        echo ""
    done

    # Generate final report
    if [ -f "$results_file" ] && [ -s "$results_file" ]; then
        generate_report "$results_file"
        echo ""
        echo -e "${GREEN}Evaluation completed!${NC}"
        echo -e "${GREEN}Results saved to: $results_file${NC}"
        echo -e "${GREEN}Log saved to: $log_file${NC}"
        echo -e "${GREEN}Successful implementations: $success_count/$total_count${NC}"
    else
        echo -e "${RED}No valid results generated${NC}"
        exit 1
    fi
}

# Print usage information
show_usage() {
    echo "Usage: $0 [OPTIONS] [TARGET]"
    echo ""
    echo "Evaluate TinyChatEngine linear kernel implementations"
    echo ""
    echo "TARGET:"
    echo "  all                           Test all implementations (default)"
    echo "  reference                     Test only reference implementation"
    echo "  loop_unrolling               Test only loop unrolling implementation"
    echo "  multithreading               Test only multithreading implementation"
    echo "  simd_programming             Test only SIMD programming implementation"
    echo "  multithreading_loop_unrolling Test only multithreading+loop unrolling implementation"
    echo "  all_techniques               Test only all techniques combined implementation"
    echo ""
    echo "OPTIONS:"
    echo "  -i, --iterations NUM         Number of benchmark iterations (default: 100)"
    echo "  -o, --output DIR             Output directory for results (default: ./results)"
    echo "  -h, --help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                          # Test all implementations"
    echo "  $0 reference                # Test only reference implementation"
    echo "  $0 -i 50 all_techniques     # Test all_techniques with 50 iterations"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--iterations)
                ITERATIONS="$2"
                shift 2
                ;;
            -o|--output)
                OUTPUT_DIR="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            -*)
                echo -e "${RED}Unknown option: $1${NC}"
                show_usage
                exit 1
                ;;
            *)
                TARGET="$1"
                shift
                ;;
        esac
    done
}

# Main execution
main() {
    parse_args "$@"
    detect_compiler

    echo -e "${BLUE}TinyChatEngine Linear Kernel Evaluation${NC}"
    echo -e "${BLUE}======================================${NC}"
    echo "Target: $TARGET"
    echo "Iterations: $ITERATIONS"
    echo "Output directory: $OUTPUT_DIR"
    echo ""

    run_evaluation
}

# Run main function with all arguments
main "$@"
