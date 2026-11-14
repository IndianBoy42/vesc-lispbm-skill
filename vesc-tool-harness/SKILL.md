---
name: vesc-lispbm-harness
description: "Drive the LispBM interpreter on a live VESC from a host script through vesc_tool --loadQml: upload scripts, run REPL expressions, poll stats and plot points. Use when a workflow must be automated or agent-driven instead of clicking in the GUI."
---

# Driving LispBM from a host program (experimental)

> **Status: experimental, partly verified.** The mechanism below was confirmed against
> vesc_tool 7.00 by running the harness with no device attached (script loads, `VescIf`
> resolves, connection loop runs). Every claim tagged **[UNVERIFIED]** needs a real VESC
> to confirm. When you use this, replace those tags with what you observed and append to
> the Refinement log at the bottom. The goal is that this file becomes boring and accurate.

## The problem

vesc_tool's CLI cannot talk to the LispBM interpreter. There is no REPL flag: the option
list in `vesc_tool:main.cpp:75-119` has only `--uploadLisp`, `--eraseLisp`, `--reduceLisp`,
`--packLisp`, `--bridgeAppData`. Nothing connects `Commands::lispPrintReceived` outside the
GUI (`vesc_tool:pages/pagelisp.cpp:204`), so `--uploadLisp` cannot show you what the script
printed, and there is no way to evaluate an expression.

The GUI page is not magic. `PageLisp` is a thin shell over exactly two objects:

- `mVesc` (`VescInterface`) - `commands()`, `isPortConnected()`
- `mLoader` (`CodeLoader`) - pack / erase / upload / stream / read

`vesc_tool --loadQml FILE` runs your own QML in the same engine with the same objects, no
window interaction required. That is the surface. `mobile/Lisp.qml` is the proof: it
implements the whole mobile Lisp editor against it.

## Configure it

The config block at the top of `agent.qml` is the whole interface:

| Property | Meaning |
|---|---|
| `uploadPath` | `.lbm` source to erase + upload + run once connected. Empty = leave flash alone. Destructive. |
| `reduceLisp` | strip comments/spaces/imports before packing |
| `statsIntervalMs` | stats poll period; 1000 is safe, faster is wasted |
| `quitAfterUpload` | call `Qt.quit()` when the upload finishes, for one-shot CLI use |

`Qt.quit()` from the loaded script exits with status 0 (verified), so a shell wrapper can
treat `quitAfterUpload: true` as a normal command.

## Run it

```sh
cd <skill>/vesc-tool-harness
xvfb-run -a vesc_tool --loadQml agent.qml \
    --qmlAutoConn --vescPort /dev/ttyACM0 --retryConn
```

- `--qmlAutoConn` is **required**. Without it nothing ever calls `connectSerial`: the
  reload timer fires at `vesc_tool:main.cpp:1683` but `connTimer` only starts inside that
  `if` block. Verified: without the flag, `isPortConnected()` stays false forever and no
  connection attempt is logged.
- Drop `--vescPort` to autoconnect (scans serial ports).
- `--retryConn` keeps the process alive across failed connects instead of quitting.
- `--offscreen` does **not** help: it is only honoured in the three `QCoreApplication`
  branches (`main.cpp:1096, 1556, 1580`), never in the GUI branch at `main.cpp:1594`.
  Some builds do not ship the offscreen QPA plugin at all, and the static Qt build used
  for the releases has no `offscreen` plugin. Use `xvfb-run`.
- `--canFwd <id>` works as usual and applies to everything the script sends.

## Reading the output

Every `console.log` from the loaded QML reaches stdout prefixed with `qml: `:

```
qml: LBM|STATE|harness loaded
qml: LBM|PRINT|<<END>>
```

`agent.qml` emits one line per event as `LBM|<TAG>|<payload>`:

| Tag | Meaning |
|---|---|
| `STATE` | lifecycle: loaded, connected, upload ok / FAILED |
| `TX` | a REPL expression was sent |
| `PRINT` | `print` output from the interpreter, and REPL results |
| `STAT` | JSON of `{cpu_use, heap_use, mem_use, stack_use, done_ctx_r, globals[{name,value}]}` |
| `RUNNING` | reply to `lispSetRunning` |
| `PLOT`, `PLOTINIT` | LispBM `plot-*` stream |
| `STREAM` | `lispStreamString` progress / result |

Grep for `LBM|` and ignore the rest; Qt prints font, EGL and serial noise to the same
stream. **`--debugOutFile F` sends these lines to `F` only, without the `qml:` prefix, and
silences stdout** (`main.cpp:134-141` installs a handler that ignores the stream). Pick one
channel, not both.

## Capability map

| GUI Lisp page feature | QML call | Where it lives |
|---|---|---|
| Upload + run | `loader.lispUploadFromPath(path, reduce)` then `cmd.lispSetRunning(1)` | `vesc_tool:codeloader.cpp:470` |
| Upload from string | `loader.lispUploadString(src, dir, reduce)` - **does not erase** | `codeloader.cpp:459` |
| Pack imports / reduce | second argument is the directory `import` is resolved from | `codeloader.cpp:459` |
| Erase | `loader.lispErase(size)` | `codeloader.cpp:63` |
| Stream code | `loader.lispStreamString(str, mode)` | `codeloader.cpp:489` |
| Read code back | `loader.lispReadWithPath()` | `codeloader.h:48` |
| REPL send | `cmd.lispSendReplCmd(text)` (`COMM_LISP_REPL_CMD` = 138) | `commands.h:289` |
| REPL receive | signal `lispPrintReceived(str)` (`COMM_LISP_PRINT` = 135) | `commands.cpp:1018` |
| Run / stop | `cmd.lispSetRunning(bool)` | `commands.h` public slots |
| CPU / heap / mem / stack / globals | signal `lispStatsRxMap(QVariantMap)` | `commands.cpp:1022` |
| Plot stream | signals `plotInitReceived`, `plotDataReceived`, `plotAddGraphReceived` | `commands.h:135` |
| Device telemetry | `getValues()`, `getStats(mask)`, `getImuData(mask)` + matching signals | `res/qml/Examples/PollValues.qml` |

`CodeLoader` is registered as a QML type named `CodeLoader` (`main.cpp:265`), but it is
**not** importable from the implicit context: you must
`import Vedder.vesc.codeloader 1.0` or creation fails with `CodeLoader is not a type`.
`VescIf`, `QmlUi` and `Utility` are context properties set by `QmlUi::startCustomGui`
(`mobile/qmlui.cpp:95-97`); `Commands` needs `import Vedder.vesc.commands 1.0`.

## Version requirement

The harness needs `lispUploadFromPath`, `lispStreamString`, and (for stats)
`lispStatsRxMap`. The latter is missing from older builds, which log:

```
QML Connections: Detected function "onLispStatsRxMap" in Connections element.
This is probably intended to be a signal handler but no signal of the target matches the name.
```

Probe the binary before trusting it:

```sh
for s in lispUploadFromPath lispUploadString lispStreamString lispReadWithPath lispStatsRxMap; do
    printf '%s: ' "$s"; strings "$(command -v vesc_tool)" | grep -cx "$s"
done
```

Measured `count == 1` (present) on the binaries available when this was written:

| Symbol | 7.00 | 2025-11 beta | 6.06 |
|---|---|---|---|
| `lispUploadFromPath` | yes | yes | yes |
| `lispUploadString` | yes | **no** | **no** |
| `lispStreamString` | yes | yes | yes |
| `lispReadWithPath` | yes | **no** | **no** |
| `lispStatsRxMap` | yes | **no** | **no** |

A `0` is a hint, not proof: a symbol can be absent from `strings` output for unrelated
reasons. The definitive test is running the harness and watching for the QML warning.

On the older builds, use `lispStatsRx(LISP_STATS)` (a `Q_GADGET` with `cpu_use`,
`heap_use`, `mem_use`, `stack_use`, `done_ctx_r` — `datatypes.h:1145`) instead of the map,
and `lispReadCode` + `lispReadCodeRx` instead of `lispReadWithPath`.

## Constraints that bite

1. **The REPL has no request/response correlation.** `lispSendReplCmd` returns `void` and
   replies arrive as undifferentiated `COMM_LISP_PRINT` packets. The harness brackets each
   expression with `(print "<<END>>")`. Ordering over one serial link makes this work
   **[UNVERIFIED for CAN-forwarded devices and for multi-device setups]**.
2. **Uploads block in nested event loops.** Erase waits up to 8 s, each 384-byte write up
   to 1 s with 5 retries (`codeloader.cpp:74-92, 398-420`). The QML item's timers stall
   during an upload, so do not expect stats polling to continue.
3. **`lispUploadFromPath` erases, `lispUploadString` does not.** The GUI erases explicitly
   before calling `lispUpload` (`pagelisp.cpp:686-695`). Use the FromPath variant or erase
   yourself, with `size + 100` as the GUI does.
4. **Size cap**: 128 KiB on STM32, 512 KiB on ESP32 (`codeloader.cpp:380-388`).
5. **Stats requests are dropped, not queued.** `lispGetStats` returns immediately while a
   previous request is in flight (`commands.cpp:2240`). 1 Hz is safe; faster is wasted.
6. **Long expressions must be streamed, not sent.** The GUI switches at 400 characters
   (`pagelisp.cpp:369`): `lispStreamString` above that, `lispSendReplCmd` below.
7. **Root element must be an `Item`.** `main.cpp:1681-1683` prepends
   `import "qrc:/mobile"`, `import Vedder.vesc.vescinterface 1.0` and
   `import "file:<dir>"`, then hands the string to `DynamicLoader.qml`, which calls
   `Qt.createQmlObject` inside an `Item` container. A `Window` root will not work.
8. **Cosmetic teardown error.** `DynamicLoader.qml:50: TypeError: Cannot call method
   'getAppHexColor' of null` appears on exit. Ignore it; it comes from the loader's
   background rectangle, not from your script.
9. **No filesystem escape by default.** `console.log` is the only output. If a real file or
   socket is needed, `SysCmd.executeCommand` (`main.cpp:267`, Linux only) runs a shell and
   emits the output as signals.

## Extending the harness

`agent.qml` is deliberately small: a config block at the top, a `repl()` helper, an
`upload()` helper, signal handlers, and one polling timer. Add to it rather than writing a
new file, so improvements accumulate in one place.

Useful next additions, in the order they usually get wanted:

- A work queue driven from a file or a socket instead of the hardcoded `uploadPath`.
- A `mode` switch for `lispErase` + read-back, so an agent can diff what is on the device.
- A `SysCmd` output sink so results land in a file without `--debugOutFile` swallowing
  stdout.
- CAN scan (`scanCan`, `getCanDevsLast`) and a per-device prefix via `(set-print-prefix ...)`.

## Alternatives, and why they are worse

| Route | Verdict |
|---|---|
| `--uploadLisp`, `--eraseLisp`, `--bridgeAppData` | One-shot only. No REPL, no `print` capture, no stats. |
| `--tcpServer` / `--tcpHub` + own protocol client | Full capability but you reimplement framing, CRC, chunked writes with per-chunk acks, and every `COMM_LISP_*` payload. `CodeLoader` already does it. |
| "QML Scripting" page in the GUI | Same engine, gated behind clicks. `--loadQml` is that engine without the gate. |
| `display_tool`, `application/template` | Unrelated. |

If you need this without a display server at all, the remaining gap is a `QCoreApplication`
+ `QQmlEngine` mode in `main.cpp` that skips `QmlUi`; it does not exist today.

## Refinement log

Append one dated entry per session that uses this. State what you ran, what broke, and what
you changed. Delete the `[UNVERIFIED]` tags above as they get confirmed.

- **2026-11-14** - Harness created. Verified with vesc_tool 7.00, no device: QML loads,
  `VescIf.commands()` resolves, `--qmlAutoConn` drives the connect loop, `console.log`
  reaches stdout as `qml: ...`, `--debugOutFile` suppresses stdout, `--offscreen` fails
  (no plugin in the release build), `CodeLoader` needs the explicit import,
  `lispStatsRxMap` missing from the 6.06 and Nov-2025 beta binaries. Upload, REPL exchange,
  stats and plot paths all still `[UNVERIFIED]` against hardware.
