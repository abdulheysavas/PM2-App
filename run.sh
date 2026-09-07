#!/usr/bin/env bash
# pm2-app launcher
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
cd "$APP_DIR"
exec /usr/bin/python3 "$APP_DIR/main.py" "$@"
