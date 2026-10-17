#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v docker >/dev/null || { echo "Install Docker with Compose first."; exit 1; }
docker compose version >/dev/null
case "${1:-help}" in
  start) docker compose up -d --build --wait ;;
  status) docker compose ps; curl --max-time 8 -i http://127.0.0.1:8080/health ;;
  logs) docker compose logs --tail=100 ;;
  reset)
    cp nginx/healthy.conf nginx/default.conf
    # Only lab containers are recreated. Their temporary data is intentionally cleared.
    docker compose up -d --build --force-recreate --wait ;;
  stop) docker compose down ;;
  inject)
    case "${2:-}" in
      stopped-backend) docker compose stop app ;;
      wrong-port)
        sed 's/app:8000/app:8999/' nginx/healthy.conf > nginx/default.conf
        docker compose exec -T proxy nginx -t
        docker compose exec -T proxy nginx -s reload ;;
      permissions)
        docker compose exec -T app rm -f /data/notes.txt
        docker compose exec -T --user 0 app chmod 500 /data ;;
      disk-full)
        docker compose exec -T app python -c 'from pathlib import Path; Path("/data/filler").write_bytes(b"x" * 1000000)'
        # Fill only the isolated 1 MiB tmpfs, never the host filesystem.
        docker compose exec -T app python -c 'import errno; f=open("/data/filler", "ab")
try:
 while True:
  f.write(b"x" * 4096); f.flush()
except OSError as e:
 if e.errno != errno.ENOSPC: raise
 print("Lab tmpfs is full; expected ENOSPC.")' ;;
      timeout) docker compose exec -T app touch /control/slow ;;
      *) echo "Choose: stopped-backend | wrong-port | permissions | disk-full | timeout"; exit 2 ;;
    esac ;;
  *) echo "Usage: bash scripts/lab.sh {start|status|logs|reset|stop|inject SCENARIO}" ;;
esac
