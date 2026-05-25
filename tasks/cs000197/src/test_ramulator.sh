#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${ROOT_DIR}"

RAMULATOR_BIN="./ramulator"

if [[ ! -x "${RAMULATOR_BIN}" ]]; then
  echo "Error: ramulator binary not found. Please run 'make' first in the src directory."
  exit 1
fi

BASE_CONFIG="configs/test-config.cfg"
TRACE_FILE="cpu.trace"

if [[ ! -f "${BASE_CONFIG}" ]]; then
  echo "Error: base config '${BASE_CONFIG}' not found."
  exit 1
fi

if [[ ! -f "${TRACE_FILE}" ]]; then
  echo "Error: trace file '${TRACE_FILE}' not found."
  exit 1
fi

echo "Running instruction_throughput test with default config..."
"${RAMULATOR_BIN}" "${BASE_CONFIG}" --mode=cpu --stats test_default.stats "${TRACE_FILE}"

it_value="$(grep 'ramulator.instruction_throughput' test_default.stats | awk '{print $2}')"
if [[ -z "${it_value}" ]]; then
  echo "Error: instruction_throughput not found in test_default.stats"
  exit 1
fi

if [[ "${it_value}" == "0" || "${it_value}" == "0.000000" ]]; then
  echo "Error: instruction_throughput is zero, which is unexpected."
  exit 1
fi

echo "instruction_throughput test passed (value=${it_value})."

echo "Running scheduler tests for FCFS, FRFCFS, FRFCFS_Cap, ATLAS, BLISS..."

for sched in FCFS FRFCFS FRFCFS_Cap ATLAS BLISS; do
  cfg="configs/test-${sched}.cfg"
  stats_file="test_${sched}.stats"

  # Create a temporary config with the desired scheduler
  sed '/^scheduler[[:space:]]\+/d' "${BASE_CONFIG}" > "${cfg}"
  echo "scheduler ${sched}" >> "${cfg}"

  echo "  - Testing scheduler=${sched}..."
  "${RAMULATOR_BIN}" "${cfg}" --mode=cpu --stats "${stats_file}" "${TRACE_FILE}"

  if ! grep -q 'ramulator.instruction_throughput' "${stats_file}"; then
    echo "Error: instruction_throughput not found in ${stats_file} for scheduler=${sched}"
    exit 1
  fi
done

echo "All scheduler tests passed."


