#!/usr/bin/env bash
set -euo pipefail
docker rm -f practice-ansible >/dev/null 2>&1 || true
echo "removed practice-ansible"
