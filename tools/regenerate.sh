#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CACHE="$1"
case "$CACHE" in /*) ;; *) echo "cache must be absolute" >&2; exit 2;; esac
case "$CACHE/" in "$ROOT/"*) echo "cache must be outside the submission" >&2; exit 2;; esac
REV=eb11aec4be8cb2122afe713a4816662c3f0fb2fa
mkdir -p "$CACHE"
curl -fL "https://codeload.github.com/tobymao/sqlglot/tar.gz/$REV" -o "$CACHE/base.tar.gz"
echo "93b2445f15f395b81c20556777ece19a6c7507df950f13fa9fac4a3be739af0d  $CACHE/base.tar.gz" | sha256sum --check
tar -xzf "$CACHE/base.tar.gz" -C "$CACHE"
test ! -e "$CACHE/raw"
mkdir "$CACHE/raw"
docker build --platform linux/amd64 -f "$ROOT/tools/Bootstrap.Dockerfile" \
  -t blast-map-reproducer "$ROOT"
docker run --rm --platform linux/amd64 --network none --cpus 2 --cpuset-cpus 0,1 \
  --memory 4096m --memory-swap 4096m --pids-limit 256 \
  -e SKIP_INTEGRATION=0 -e PYTHONPATH=/src -e BLAST_RAW_DIR=/raw \
  -v "$CACHE/sqlglot-$REV:/src:ro" -v "$ROOT/tools:/tools:ro" -v "$CACHE/raw:/raw" \
  blast-map-reproducer python /tools/collect_coverage.py
docker run --rm --platform linux/amd64 --network none --cpus 2 --cpuset-cpus 0,1 \
  --memory 4096m --memory-swap 4096m --pids-limit 256 \
  -v "$CACHE/sqlglot-$REV:/src:ro" -v "$ROOT/tools:/tools:ro" \
  -v "$CACHE/raw:/raw" -v "$ROOT/maps:/maps" \
  blast-map-reproducer python /tools/generate_maps.py --source /src --raw /raw --out /maps
