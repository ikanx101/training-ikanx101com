#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PID_FILE="$SCRIPT_DIR/.server.pid"
LOG_FILE="$SCRIPT_DIR/server.log"

if [ -f "$PID_FILE" ]; then
  OLD_PID=$(cat "$PID_FILE")
  if kill -0 "$OLD_PID" 2>/dev/null; then
    echo "Server sudah berjalan (PID: $OLD_PID) di http://localhost:209"
    exit 0
  fi
  rm -f "$PID_FILE"
fi

echo "Memulai Study Data with ikanx101.com..."
mkdir -p uploads app/static/img

nohup sudo env PYTHONPATH=/home/ikanx101/.local/lib/python3.13/site-packages python3 -m uvicorn app.main:app --host 0.0.0.0 --port 209 --reload > "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

sleep 2
if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "Server berhasil dimulai!"
  echo "URL: http://localhost:209"
  echo "Admin: http://localhost:209/admin/"
  echo "   Email: admin@ikanx101.com"
  echo "   Password: admin123"
  echo "Log: $LOG_FILE"
  echo "Hentikan server dengan: ./stop.sh"
else
  echo "Server gagal dimulai. Cek log: $LOG_FILE"
  cat "$LOG_FILE"
  exit 1
fi
