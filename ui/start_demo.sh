#!/usr/bin/env bash
# Start the demo server detached from the launching terminal/session, so it
# survives editor/session restarts. Idempotent: does nothing if the port
# already answers, and flock guards against concurrent starts (many shells can
# invoke this at once via the ~/.bashrc keepalive). Logs to ui/logs/server.log.
#   ui/start_demo.sh          start (or no-op if live)
#   ui/start_demo.sh stop     stop and remove the keepalive's target
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${PORT:-8765}"
LOG="$ROOT/ui/logs/server.log"
PIDFILE="$ROOT/ui/logs/server.pid"
LOCK="$ROOT/ui/logs/.start.lock"

if [ "${1:-}" = "stop" ]; then
  [ -f "$PIDFILE" ] && kill "$(cat "$PIDFILE")" 2>/dev/null && rm -f "$PIDFILE" \
    && echo "stopped" || echo "not running"
  exit 0
fi

alive() { curl -s -o /dev/null --max-time 2 "http://127.0.0.1:$PORT/live"; }

alive && { echo "already live: http://127.0.0.1:$PORT/live"; exit 0; }

mkdir -p "$ROOT/ui/logs"
exec 9>"$LOCK"
if ! flock -n 9; then
  # another shell is starting it right now; wait briefly and report
  for _ in 1 2 3 4 5 6; do sleep 0.5; alive && { echo "live (started by peer)"; exit 0; }; done
  echo "peer start in progress; check $LOG" >&2
  exit 0
fi

# re-check under the lock (a peer may have finished between checks)
alive && { echo "already live: http://127.0.0.1:$PORT/live"; exit 0; }

setsid nohup python "$ROOT/ui/server.py" --port "$PORT" >> "$LOG" 2>&1 < /dev/null &
echo $! > "$PIDFILE"
for _ in 1 2 3 4 5 6 7 8; do sleep 0.5; alive && break; done
if alive; then
  echo "live: http://127.0.0.1:$PORT/live (pid $(cat "$PIDFILE"), log $LOG)"
else
  echo "FAILED to start - see $LOG" >&2
  exit 1
fi
