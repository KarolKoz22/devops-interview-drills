#!/usr/bin/env bash
set -euo pipefail
docker rm -f practice-ansible >/dev/null 2>&1 || true
docker run -d --name practice-ansible --privileged --cgroupns=host \
  --tmpfs /tmp --tmpfs /run --tmpfs /run/lock \
  -v /sys/fs/cgroup:/sys/fs/cgroup:rw \
  geerlingguy/docker-ubuntu2204-ansible:latest >/dev/null
echo "waiting for systemd to finish booting..."
sleep 3
docker exec practice-ansible systemctl is-system-running --wait >/dev/null 2>&1 || true
echo "practice-ansible is up."
