#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# This test recreates only this lab's containers and temporary data.
trap 'bash scripts/lab.sh stop' EXIT
bash scripts/lab.sh reset
python3 scripts/verify.py healthy
python3 scripts/verify.py write-ok
for scenario in stopped-backend wrong-port permissions disk-full timeout; do
  bash scripts/lab.sh reset
  bash scripts/lab.sh inject "$scenario"
  # Allow Nginx workers to adopt a reloaded configuration.
  if [[ "$scenario" == wrong-port ]]; then sleep 1; fi
  python3 scripts/verify.py "$scenario"
  bash scripts/lab.sh reset
  python3 scripts/verify.py healthy
  python3 scripts/verify.py write-ok
done
