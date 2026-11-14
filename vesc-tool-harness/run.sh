#!/usr/bin/env bash
# Drive the LispBM interpreter on a VESC through a VESC Tool window's TCP server.
#
#   ./run.sh                          attach to 127.0.0.1:65102 and stay up
#   ./run.sh 192.168.1.50 65102
#   ./run.sh once [host] [port]       run config.json, print replies, exit
#   ./run.sh send '<expr>'            queue one command into a running session
#   ./run.sh ask '<expr>' [timeout]   send one command, block for its reply,
#                                     print the record. No more sleep-guessing.
#   ./run.sh wait '<regex>' [timeout] block until a matching LBM| line appears
#   ./run.sh wait -a '<regex>'        ...search the whole log, not just new lines
#
# This is a launcher, not a service manager. Run it as a background job with the
# agent's own job facility (named job, ready-regex, kill by id) — do not add
# pidfiles. In daemon mode the process stays up for the whole session, hides its
# own window, and reads commands appended to commands.txt.
#
# Daemon output is appended to harness.log (and still goes to stdout, which the
# job facility captures). `ask` and `wait` block on that file, so a second shell
# can synchronise with the running session without polling its stdout.
#
# Prerequisite: the VESC Tool window you are watching has
# Connection -> TCP Server enabled. Only ONE client is accepted at a time —
# if you also want a visible panel, run panel.qml so one process fills both
# roles instead of competing for the slot.

set -euo pipefail

DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
usage() { sed -n '2,25p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'; }
QML="$DIR/agent.qml"
CMD="$DIR/commands.txt"
LOG="$DIR/harness.log"
TOOL="${VESC_TOOL:-vesc_tool}"
need_tool() {
    command -v "$TOOL" >/dev/null || { echo "vesc_tool not on PATH; set VESC_TOOL" >&2; exit 1; }
    [[ -f "$QML" ]] || { echo "missing $QML" >&2; exit 1; }
    [[ -n "${DISPLAY:-}" ]] || { echo "no DISPLAY; run this where your VESC Tool window is" >&2; exit 1; }
}

# Drop Qt's "qml: " prefix and unrelated chatter, and stay line-buffered so a
# reader tailing the job sees events as they happen. Daemon mode also appends
# everything to harness.log for `ask` / `wait`.
attach() {
    local url="$1" logmode="$2"
    if [[ "$logmode" == "tee" ]]; then
        exec "$TOOL" --loadQml "$QML" --vescPort "$url" 2>&1 \
            | stdbuf -oL sed -u -e 's/^qml: //' -e '/^LBM|/!d' \
            | tee -a -- "$LOG"
    else
        exec "$TOOL" --loadQml "$QML" --vescPort "$url" 2>&1 \
            | stdbuf -oL sed -u -e 's/^qml: //' -e '/^LBM|/!d'
    fi
}

# Poll the log from byte OFFSET for the first reply/fault record after a
# fresh tx record. Literal index() matching: a regex passed through awk -v
# gets its escapes eaten, which once made this match the tx line itself.
ask_scan() {
    local off="$1"
    tail -c +"$((off + 1))" -- "$LOG" 2>/dev/null \
        | awk '
            index($0, "\"k\":\"tx\"") { seen_tx = 1 }
            seen_tx && (index($0, "\"k\":\"reply\"") || index($0, "\"k\":\"fault\"")) {
                print; exit
            }'
}

ask() {
    local expr="$1" tms="${2:-15000}"
    local off
    off=$(stat -c %s -- "$LOG" 2>/dev/null || echo 0)
    printf '%s\n' "$expr" >> "$CMD"
    local deadline=$(( $(date +%s%3N) + tms ))
    local line
    while (( $(date +%s%3N) < deadline )); do
        line=$(ask_scan "$off") || true
        if [[ -n "$line" ]]; then
            printf '%s\n' "$line"
            return 0
        fi
        sleep 0.1
    done
    echo "ask: no reply within ${tms} ms (is the daemon running and connected?)" >&2
    return 1
}

wait_for() {
    local from_start="$1" pat="$2" tms="$3"
    local off=0
    if [[ "$from_start" != "yes" ]]; then
        off=$(stat -c %s -- "$LOG" 2>/dev/null || echo 0)
    fi
    local deadline=$(( $(date +%s%3N) + tms ))
    local line
    while (( $(date +%s%3N) < deadline )); do
        line=$(tail -c +"$((off + 1))" -- "$LOG" 2>/dev/null | grep -m1 -E -- "$pat") || true
        if [[ -n "$line" ]]; then
            printf '%s\n' "$line"
            return 0
        fi
        sleep 0.1
    done
    echo "wait: no match for /$pat/ within ${tms} ms" >&2
    return 1
}

# A bare first argument is a host, not a verb: "./run.sh 192.168.1.50 65102".
verb="attach"
case "${1:-}" in
    ""|attach|daemon|once|send|ask|wait) verb="${1:-attach}" ;;
    -h|--help) usage; exit 0 ;;
    *) ;;
esac

case "$verb" in
    attach|daemon)
        [[ "${1:-}" == "$verb" ]] && shift
        need_tool
        host="${1:-127.0.0.1}"; port="${2:-65102}"
        : > "$CMD"
        : > "$LOG"
        echo "attaching to $host:$port; commands via: $0 send|ask '<expr>'" >&2
        echo "replies also append to $LOG" >&2
        # The "#daemon" fragment carries the mode, because vesc_tool refuses
        # any flag it does not define, so it cannot be a separate --flag.
        attach "tcp://$host:$port#daemon" "tee"
        ;;
    once)
        need_tool
        shift
        host="${1:-127.0.0.1}"; port="${2:-65102}"
        attach "tcp://$host:$port#once" "plain"
        ;;
    send)
        shift
        [[ $# -ge 1 ]] || { echo "usage: $0 send '<expression>'" >&2; exit 1; }
        printf '%s\n' "$*" >> "$CMD"
        echo "queued: $*" >&2
        ;;
    ask)
        shift
        [[ $# -ge 1 ]] || { echo "usage: $0 ask '<expression>' [timeout_ms]" >&2; exit 1; }
        ask "$@"
        ;;
    wait)
        shift
        from_start="no"
        [[ "${1:-}" == "-a" || "${1:-}" == "--all" ]] && { from_start="yes"; shift; }
        [[ $# -ge 1 ]] || { echo "usage: $0 wait [-a] '<regex>' [timeout_ms]" >&2; exit 1; }
        tms="${2:-30000}"
        wait_for "$from_start" "$1" "$tms"
        ;;
    *) usage; exit 1 ;;
esac
