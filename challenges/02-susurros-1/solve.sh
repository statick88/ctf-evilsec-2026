#!/usr/bin/env bash
# solve.sh — Susurros 1 (EASY)
# Extracts FLAGPART fragments from server.log in timestamp order and reconstructs the flag.
# The fragments repeat in cycles; we take the first occurrence of each unique fragment.

set -euo pipefail

LOG_FILE="server.log"

# Extract FLAGPART lines, get fragment after "FLAGPART: ", before " es la onda"
# Use awk to track seen fragments and only print first occurrence
awk '
  /FLAGPART:/ {
    match($0, /FLAGPART: ([^ ]+) es la onda/, arr)
    if (arr[1] != "" && !seen[arr[1]]++) {
      printf "%s", arr[1]
    }
  }
  END { print "" }
' "$LOG_FILE"