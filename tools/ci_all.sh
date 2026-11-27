#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 tools/release_check.py --check --skip-channel
python3 services/skillhub-402/build_client.py --selftest
python3 -m unittest discover -s services/skillhub-402/tests
(
  cd services/skillhub-402/client
  node --test
)
bash services/skillhub-402/tests/cross_language_e2e.sh
