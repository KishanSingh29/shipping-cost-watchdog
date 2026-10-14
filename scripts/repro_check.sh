#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="src"
mkdir -p outputs/repro docs
for run in 1 2 3; do
  python -m watchdog.cli --config config.yaml
  cp outputs/watchlist.csv "outputs/repro/watchlist_run${run}.csv"
done
sha256sum outputs/repro/watchlist_run*.csv > outputs/repro/sha256.txt
if cmp -s outputs/repro/watchlist_run1.csv outputs/repro/watchlist_run2.csv && cmp -s outputs/repro/watchlist_run1.csv outputs/repro/watchlist_run3.csv; then
  printf '# Reproducibility report\n\nPASS: all three CSV outputs are byte-identical.\n\n' > docs/repro_report.md
  cat outputs/repro/sha256.txt >> docs/repro_report.md
  echo 'PASS: three outputs are byte-identical.'
else
  printf '# Reproducibility report\n\nFAIL: output CSVs differ.\n' > docs/repro_report.md
  diff -u outputs/repro/watchlist_run1.csv outputs/repro/watchlist_run2.csv || true
  exit 1
fi
