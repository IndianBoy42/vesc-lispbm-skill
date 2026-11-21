---
name: vesc-express-logging
description: "Record lispBM data to a VESC Express SD card: the log-* API (can-id -2), feeding it from CAN status polls or custom CAN frames, at-boot logging with EEPROM settings, and the failure modes that leave a log empty. Use when a run must be recorded without a host, or when log-start produces nothing."
---

# Logging to the Express SD card

`log-*` writes VESC-format logs, which VESC Tool's log page reads. The target is
the `can-id` argument of every call:

| can-id | destination |
|---|---|
| `-2` | the Express' local SD card (Express only) |
| `-1` | streamed to VESC Tool |
| `0..254` | another bus device running the log |

Minimum shape, in this order:

```lisp
; id, field index, key, name, unit, decimals, relative, timestamp
(log-config-field -2 0 "rpm" "RPM"     ""  0 false false)
(log-config-field -2 1 "cur" "Current" "A" 2 false false)
; id, field count, rate Hz, append time, append GNSS
(log-start -2 2 50.0 true false)
; id, from-field, samples (numbers or one list, 1..100)
(log-send-f32 -2 0 (list (canget-rpm 3) (canget-current 3)))
(log-stop -2)
```

## What decides the file

- Configure **every** index before `log-start`; the field count passed there tells the
  writer how many columns a sample carries. `key` identifies the column; `name`, `unit`
  and `decimals` are display; `relative` plots from the first sample; `timestamp` formats
  as hh:mm:ss.
- `append-time` adds a per-sample timestamp. Keep it true for anything compared across
  runs.
- `append-gnss` is functional, not cosmetic: with it true the log does not start until a
  GNSS fix exists.
- `log-send-f32` takes 1..100 samples (f64: 1..50) and maps them to consecutive fields
  from the given index. The sample rate is your call rate.
- Re-run the config before every start. That is the `vesc_pkg/logui` pattern, and it
  keeps a reconfigured field set from meeting stale metadata.

## Where the samples come from

- **Standard VESC status of a CAN node**: `canget-rpm`, `canget-current`, `canget-duty`,
  `canget-temp-fet`, `canget-temp-motor`, `canget-vin`, ... Each one is a CAN poll, so
  read slow signals once a second into a global and log the global. Never poll per
  sample.
- **Custom frames**: `event-can-eid` delivers `(id . data)`. Compare against the expected
  base (`fb_base + node * 65536`) and take `id - base` as the frame index, then
  `bufget-*` with `'little-endian`. 29-bit ids fit in i32, so integer arithmetic stays
  exact; do not let an id meet a float, because float32 rounds above 2^24 and that is
  inside the 29-bit id space.
- Read `ref/can-commands.md` before relying on events: the handler's mailbox drops frames
  silently when it is full, and `event-can-eid` is a firehose on a busy bus. Log
  **sampled state** at a fixed rate, where the sample sequence is yours, rather than
  trying to log every frame.

## Rates, threads, heap

50 Hz x 14 floats is ~2.8 kB/s of SD write, trivial for any card. What bites is threads:
every `spawn` closure lives in the heap. A five-thread logger exhausted the bundled host
REPL (`Heap cells free: 1631, Mem longest free: 225`); folding the 1 Hz battery poll into
the sample loop (every Nth tick) fixed it. Use one loop per rate class, not one thread
per signal.

## Settings and boot

Persist what a production run needs, never the run state:

```lisp
(def eeprom-addrs '((ver . (0 i)) (node . (1 i)) (rate . (2 f)) (boot . (3 b))))
; offset = (first (assoc eeprom-addrs name)), type = (second ...)  -> 'i 'f 'b
; (eeprom-read-i addr) / (eeprom-read-f addr), (eeprom-store-i addr v) / (eeprom-store-f addr v)
(def settings-ver 1i32)   ; mismatch -> write defaults, as logui does
(if (not-eq (read-setting 'ver) settings-ver) (restore-settings))
```

`(trap (image-save))` after `@const-end` stores the script as an image, so a reboot starts
it without a parse. A boot-time log should wait for the bus and the card first: logui
waits 10 s, 3 s was enough with one peer.

## Driving it from a package UI

`pkgLisp` owns the device's script slot, so a logger package is the Express' script. The
UI half sends lisp source as NUL-terminated custom app data; the script evaluates it from
`event-data-rx` and answers with `send-data` (see `qml-ui/SKILL.md`, "Driving the device").
Start, stop, rate and start-at-boot are then ordinary lisp calls.

## Failure modes, measured

- **A missing `}` in a `{ ... }` block passes packaging and kills the script.**
  `--buildPkgFromDesc` prints "Package LispBM found and parsed!"; the device (and the host
  VM) then fails with `read_error`, `Reason: End of parse stream`, naming the last
  function it was building. Count braces as well as parentheses.
- **An empty log is usually the card, not the API.** Prove the mount by writing a file
  (`fileBlockWrite`; the LogUI "Test SD-card" button does exactly this) before debugging
  the script. Wrong filesystem or write protection is the common cause.
- **`send-data` is the only path to the tool.** It takes a string or a byte array of at
  most 100 bytes, and both arrive on one `customAppDataReceived` signal. Tell binary
  frames from text replies by length plus a version byte.
- **`-2` exists only on the Express.** On an ESC the same calls need `-1`, because there
  is no local card.

Worked examples: `vesc_pkg/logui/logger.lisp` (CAN polls, BMS fields, at-boot logging) and
`fishi-h7-nxt/VescTail/ui/tail_express.lisp` (custom EIDs, forwarding a binary telemetry
frame, and a CAN command loop that keeps a downstream controller's deadman fed while the
log records).

Status: API behaviour from the firmware source and the host VM; the SD write itself needs
an Express with a card.
