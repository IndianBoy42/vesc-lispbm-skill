#!/usr/bin/env bash
# Drive the LispBM interpreter on a VESC through a VESC Tool window's TCP server.
#
#   ./run.sh                     attach to 127.0.0.1:65102 and stay attached
#   ./run.sh 192.168.1.50 65102
#   ./run.sh once [host] [port]  run config.json, print replies, exit
#   ./run.sh send '<expression>' queue one command into a running session
#
# This is a launcher, not a service manager. Run it as a background job with the
# agent's own job facility (named job, ready-regex, kill by id) — do not add
# pidfiles. In daemon mode the process stays up for the whole session, hides its
# own window, and reads commands appended to commands.txt.
#
# Prerequisite: the VESC Tool window you are watching has
# Connection -> TCP Server enabled. Only one client is accepted at a time.

set -euo pipefail

DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
QML="$DIR/agent.qml"
CMD="$DIR/commands.txt"
TOOL="${VESC_TOOL:-vesc_tool}"

usage() { sed -n '2,17p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }

need_tool() {
    command -v "$TOOL" >/dev/null || { echo "vesc_tool not on PATH; set VESC_TOOL" >&2; exit 1; }
    [[ -f "$QML" ]] || { echo "missing $QML" >&2; exit 1; }
    [[ -n "${DISPLAY:-}" ]] || { echo "no DISPLAY; run this where your VESC Tool window is" >&2; exit 1; }
}

# Drop Qt's "qml: " prefix and unrelated chatter, and stay line-buffered so a
# reader tailing the job sees events as they happen.
attach() {
    local url="$1"
    exec "$TOOL" --loadQml "$QML" --vescPort "$url" 2>&1 \
        | stdbuf -oL sed -u -e 's/^qml: //' -e '/^LBM|/!d'
}

# A bare first argument is a host, not a verb: "./run.sh 192.168.1.50 65102".
verb="attach"
case "${1:-}" in
    ""|attach|daemon|once|send) verb="${1:-attach}" ;;
    -h|--help) usage; exit 0 ;;
    *) ;;
esac

case "$verb" in
    attach|daemon)
        [[ "${1:-}" == "$verb" ]] && shift
        need_tool
        host="${1:-127.0.0.1}"; port="${2:-65102}"
        : > "$CMD"      # fresh command stream for this session
        echo "attaching to $host:$port; commands via: $0 send '<expr>'" >&2
        # The "#daemon" fragment carries the mode, because vesc_tool refuses
        # any flag it does not define, so it cannot be a separate --flag.
        attach "tcp://$host:$port#daemon"
        ;;
    once)
        need_tool
        shift
        host="${1:-127.0.0.1}"; port="${2:-65102}"
        attach "tcp://$host:$port#once"
        ;;
    send)
        shift
        [[ $# -ge 1 ]] || { echo "usage: $0 send '<expression>'" >&2; exit 1; }
        printf '%s\n' "$*" >> "$CMD"
        echo "queued: $*" >&2
        ;;
    *) usage; exit 1 ;;
esac
