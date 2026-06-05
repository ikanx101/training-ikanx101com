#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/.server.pid"

if [ ! -f "$PID_FILE" ]; then
  echo "Server tidak sedang berjalan."
  exit 0
fi

PID=$(cat "$PID_FILE")
if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  rm -f "$PID_FILE"
  echo "Server berhasil dihentikan (PID: $PID)."
else
  echo "Server tidak ditemukan. Menghapus PID file."
  rm -f "$PID_FILE"
fi
