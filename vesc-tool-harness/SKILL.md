---
name: vesc-tool-harness
description: "Drive a VESC Tool window over its TCP server from a host script: send lispBM expressions, upload scripts and packages, and read structured replies. Use when an agent must control or observe a VESC interactively, or when no hardware is available and fake_vesc.py is enough."
---

# Attaching to a VESC Tool window over TCP (experimental)

> **Status: experimental, but well exercised.** Verified on vesc_tool 7.00: end to end
> against real hardware (fw 7.0, connect, REPL, stats, values) and, since 2026-11-15, end
> to end against `fake_vesc.py` with no device at all (connect, `ask`, `:stats`, `:ping`,
> `:quit`, panel mode, reconnect, fault path). Remaining `[UNVERIFIED]`: `uploadPath` and
> `plot-*` capture on the fake. Keep appending to the Refinement log as you use it.

## The idea

Keep a VESC Tool window open, connected to the VESC, on the Scripting page, where you can
watch. Then run `agent.qml` in a **second** vesc_tool process that connects to that window's
TCP server. The second process drives the interpreter; you watch the first.

**No window available? Attach over USB directly.** The same harness accepts
`serial:///dev/ttyACM0` (or a bare `/dev/...` path) in `--vescPort` and calls
`VescIf.connectSerial` itself — no VESC Tool window, no TCP server, and no
single-client slot involved. Use this when the user's window is gone (a
crashed tool, a rebooted machine) or when the agent owns the only USB port:

```sh
nohup ./run.sh serial:///dev/ttyACM0#daemon >> harness.log 2>&1 &
```

Only one process can hold the port: stop the harness (send `:quit`) before
the user's own VESC Tool connects, and expect its AutoConnect to fail while
the harness holds the device.

Nothing is hidden. The window's `TcpServerSimple` is spliced into its own `Packet` in both
directions (`vescinterface.cpp:218-224`), so:

- **Harness → device:** the packet goes out to the VESC from the window's serial/CAN link.
- **Device → window:** every reply is fed to the window's `Commands`
  (`VescInterface::packetReceived`) *and* forwarded to the harness.

So agent-triggered `print` output appears in the window's console, and the window's stats
bars update from the harness's polls even though the harness is the one asking. What the
window does **not** see is the harness's request packets as commands, because those bypass
`mCommands` on the way out.

```
   agent.qml  ──TCP──▶  your window  ──serial/CAN──▶  VESC
   (process 2)          (process 1)                  (LispBM)
        ▲                    │
        └──── same replies ──┴──▶ Scripting page, plot, stats
```

## Starting the window with the TCP server on

`--tcpServer` does **not** do this. It is a separate headless mode: no main window, no
Scripting page, nothing to watch (`main.cpp:1555` is a `QCoreApplication` branch). It is only
useful for a relay with no GUI.

The server you want is started **from the window**, and vesc_tool does not remember the
checkbox (`pageconnection.cpp:681` is the only writer, `pageconnection.ui:461` is the only
control, and nothing in the page uses `QSettings`). So once per launch:

1. Launch `vesc_tool` normally, with `DISPLAY` set. A desktop launcher is fine.
2. **Connection** page (left sidebar) → **Connect** to the VESC. Autoconnect over USB is
   usually enough.
3. Scroll to the **TCP Server** group and tick **Enable TCP Server**. The port spinbox
   defaults to `65102` and greys out once enabled.
4. Confirm under *Connected Clients* that the harness's IP appears after you start it.

```sh
vesc_tool                      # from PATH, or your desktop launcher
# then, in the GUI: Connection -> Connect, then Enable TCP Server
```

`:cfg` reports the device's custom (VESC Tool) configuration pages as the
*tool* decoded them — the tool fetches them on every connect
(`fwVersionReceived` -> `customConfigGet`), so this needs no raw packet client
and no exclusive port. `num` 0 while `connected` is true means the firmware
never dispatched `COMM_GET_CUSTOM_CONFIG` to the extension, which is what
hides the page in the GUI; `hasB0`/`b0`/`b0Min`/`b0Max` then show whether the
page's defaults and ranges arrived intact.

**The server takes exactly one client, silently.** `TcpServerSimple::newTcpConnection`
closes and deletes any connection that arrives while a client is registered
(`tcpserversimple.cpp:130-136`), with no log line and no "busy" reply, so a
second client sees its socket closed at once. There is also no keepalive: the
slot is freed only when Qt reports `disconnected()`/`error()`, so a client
process that is killed (or vanishes without FIN) holds the slot until then.
Two things follow: never diagnose "the VESC is dead" from a second client
failing to get replies -- check `ss -tan | grep 65102` for who is connected,
and close the harness before using a raw client. If **no** client can get a
reply, including the harness, the fault is downstream of the server (the
window's own VESC link), not the TCP layer; the GUI's Connection page shows
that state.

**Raw clients must speak the VESC packet framing.** `[type][length...][payload][crc16_hi][crc16_lo][0x03]`
with type 2 for a one-byte length and 3 for a two-byte one, CRC over the
payload only (`packet.cpp:72-104`). Sending a big-endian length as the first
byte -- the natural guess -- makes the receiver drop every frame, which is
indistinguishable from a dead link. That mistake cost an afternoon here.

Observed on 7.00: the port and last connection type persist in
`~/.config/VESC/VESC Tool.conf` (`tcp_port`, `connection_type`), but the enable checkbox
does not, and a plain launch opens no listener. Verified by starting the GUI and checking
`ss -ltn`.

If you want the Scripting page in front, open it and load the script before starting the
harness, so you can see the console fill up.

### Watching

| In the window | What it shows |
|---|---|
| Scripting → console | every `print`, including from the harness's REPL expressions |
| Scripting → CPU / Heap / Mem bars | update from the harness's polls too, because replies fan out to both processes (`vescinterface.cpp:223`) |
| Scripting → plot | `plot-*` output from whatever is running |
| Connection → TCP Server → Connected Clients | the harness, once attached |

### Poll All is fine, and the spinbox lies

Enabling **Poll All** or **Poll VT** to watch values is the right call. It costs about 1
request per second, not the "10 Hz" the spinbox suggests.

`Commands::lispGetStats` refuses to send while a previous request is outstanding
(`vesc_tool:commands.cpp:2244`), and that flag only clears when the reply arrives (`:1023`)
or when a 10 ms tick counter drains (`:2371`). `mTimeoutCount = 100`, so the floor is
**1 s per request whatever `pollRateBox` says**. `pagelisp.cpp:135` still sets the timer to
`1000 / value`, so nine of ten firings at the 10 Hz default do nothing.

Do not run both pollers at once expecting more resolution: with the GUI at 1 Hz and the
harness at `statsIntervalMs: 1000`, each silently drops about half its intended requests.
Pick one — the GUI if you want to watch, the harness if you want the numbers in its output.

What the request actually costs the device, from `vesc/lispBM/lispif.c:210-286`:

| Cost | Detail |
|---|---|
| Reply size | up to ~300 bytes; the global-env walk stops at `ind > 300` |
| Bandwidth | negligible |
| **The real cost** | `pause_eval(0, 2000)` at line 252 **halts the LispBM evaluator** and polls at 1 ms granularity until the VM pauses or 2 s elapse |

So the interference is **jitter, not throughput**: at 1 Hz, a few milliseconds per second
while your script's loop is suspended. A script with a tight sample period will see the
hitch; a control loop will not care. Poll VT filters which globals are copied but takes the
same pause, so it is not cheaper.

If you want the GUI's view *and* a timing-sensitive script, leave the page on Poll Off and
raise the harness's `statsIntervalMs` instead — the harness's replies still populate the
window's bars.

### If you need a visible panel: run panel.qml, not a second process

The window's TCP server takes exactly one client, so "a panel for me" and "a harness for
the agent" cannot be two processes: whichever connects second is refused, and the first
one silently owns the link. A real session hit exactly this — the panel took the slot, the
agent's REPL sends went nowhere, and the only fix was killing one to free the other.

`panel.qml` is the fix: the full driver plus a visible UI in one process. You interact
with the panel; `commands.txt` still reaches the same connection. It is a template —
copy it to your project, replace the UI, keep the `Driver { ... }` root, and you keep
the whole command protocol. Run it like agent.qml minus the hiding:

```sh
vesc_tool --loadQml <abs path>/panel.qml --vescPort tcp://127.0.0.1:65102
```

The file layout is: `Driver.qml` (everything), `agent.qml` (headless entry, hides its
window), `panel.qml` (visible entry). The entries are three lines each; add behaviour in
`Driver.qml`, never by forking the driver.

## Multiple VESCs and Express over one CAN bus

One mechanism covers all of it: `COMM_FORWARD_CAN` (34). Every LispBM packet is a normal
VESC command, so `Commands::emitData` wraps it in `[COMM_FORWARD_CAN, id]`
(`vesc_tool:commands.cpp:2392-2397`) and the attached ESC relays it
(`vesc/comm/commands.c:731-745`). Replies, `print` output, stats and upload acks come back
through the same ESC, so a single harness process drives the whole bus and still occupies
only the one TCP slot.

Numbers that shape the design:

| Item | Value |
|---|---|
| Max payload per forwarded packet | 512 B (`vesc/comm/packet.h:28`) |
| Fragmentation | 7 bytes/frame, then 6 bytes/frame above 256 B (`comm_can.c:443-500`) |
| Concurrent large transfers per node | 3 RX buffers (`RX_NUM = 3`) |
| A 384-byte LispBM write chunk | ~55 CAN frames |
| `:can all` | 2 round trips per node (print prefix + expression) |

VESC Express is a normal node: its `controller_id` is a config value
(`vesc_express:main/config/settings.xml:28`, 1-254), it answers `CAN_PACKET_PING/PONG`
(`main/comm_can.c:289,1337`), it handles `COMM_FORWARD_CAN` itself (`main/commands.c:378`)
and it registers its own LispBM command set (`main/commands.c:820-892`). Its extension
surface differs from an ESC — see `ref/vesc-express-extensions.md` in the parent skill.

### Commands

| Line | Effect |
|---|---|
| `:can scan` | ping sweep; emits `{k:"can", ids:[…]}` |
| `:can <id>` | make `<id>` the session target, and set `(set-print-prefix "can<id>| ")` on it |
| `:can <id> <expr>` | run one expression there; session target unchanged |
| `:can all <expr>` | prefix + expression on every discovered node, serialised |
| `:can upload <id> <path>` | erase + upload + run on that node |
| `:can off` | back to the attached device |

Every `tx`, `reply`, `upload` and `stats` record carries `can: <id>` (`-1` = attached
device), so a caller never has to infer the source from ordering. That matters because
`Commands` has exactly one `mCanId`: the driver applies the target per queue item and only
between commands, so a late reply can never be attributed to the next node.

Prints are the other attribution channel. If several nodes print, each needs its own
prefix (`vesc/lispBM/README.md:139`, ≤50 bytes, fw 6.06+); `:can <id>` sets one, and
`:can all` sets one per node before its expression.

Uploads over CAN are the expensive operation, not the REPL: 55 frames per 384-byte chunk,
and a node only has 3 reassembly buffers. Space uploads and never queue anything behind
one — the driver's upload queue already enforces that.

### Verified, without a bus

`fake_vesc.py --nodes=1,2,3` plays the attached ESC and the nodes behind it (forwarded
packets are dispatched per id, replies are returned unwrapped, unknown ids stay silent).
Against it: `:can scan` → `[1,2,3]`; `:can 2` then a bare expression → `{"can":2,
"lines":["> node2:4f32"]}`; `:can all` → one reply each for `can:1`, `can:2`, `can:3`;
`:can upload 3` → `{"k":"upload","ok":true,"can":3}` with the fake logging forwarded
erase/write packets; `:can off` → a bare expression answers with `can:-1`. **Not yet run
against a real CAN bus**: bitrate, termination, duplicate ids and per-node upload timing
still need hardware.

## Run it as ONE persistent session

Start it once per working session and leave it up. The process hides its own window
(verified: the X window goes `IsUnMapped` and the script keeps running), so there is nothing
to minimise and nothing that flickers. Commands arrive through a file it watches; replies go
out on its stdout.

Run it as a **background job with the agent's job facility**, which already provides a name,
readiness detection and kill-by-id:

```
bash(name="lbmharness", ready={"log": "\"k\":\"connected\""}, pty=true,
     command="cd <skill>/vesc-tool-harness && ./run.sh 127.0.0.1 65102")
```

Then, from any later turn:

```sh
cd <skill>/vesc-tool-harness
./run.sh ask '(+ 1 2)'          # send, block for the reply, print the record
./run.sh send ':multi (get-vin) ; (get-rpm)'
./run.sh send ':upload test.lbm'
./run.sh wait '"k":"upload"'    # block until a record matches a pattern
./run.sh ask '(get-rpm)' 20000  # upload verdicts are slow; raise the budget
./run.sh send ':quit'
```

**`ask` is the default verb.** It exists because the alternative — `send` followed by a
guessed `sleep 8` — was measured in a real session to cost the whole timeout for every
single command. `ask` returns as soon as the reply record lands (≈0.9 s on a local link),
and fails loudly after its budget instead of silently.

How it works: the daemon tees its filtered output to `harness.log`, and `ask`/`wait` tail
that file from the byte offset they captured *before* sending, so they can never match an
older record. Caveat: `ask` assumes the queue is idle when called — the reply it pairs
with is the first one after the next `tx` record. If several commands are in flight, use
`wait` on a distinctive pattern instead.

Read the live stream from the job (`proc://lbmharness`); `harness.log` is the same lines
on disk for cross-shell synchronisation. Adding a pidfile, `setsid`, or a service manager
is redundant: the job facility already owns the lifecycle, and a foreground pipeline's
`$!` is the *last* stage, so hand-rolled tracking reports "not running" while vesc_tool is
still alive. That mistake was made and removed.

Do **not** wrap this in a shell loop that starts a fresh `--loadQml` per command. That is
what this design replaces: each launch builds a new window and a new TCP connection, and
the window flashes open and shut. A real session did exactly this 31 times in one
afternoon and had to work around its own window churn; the launcher is the fix.

### commands.txt

Append one command per line. `:multi` splits on ` ; `.

| Line | Effect |
|---|---|
| `<expr>` | evaluate through the REPL |
| `:multi <a> ; <b>` | several expressions, queued |
| `:run <path>` | evaluate a whole file |
| `:upload <path>` | erase + upload + run a `.lbm` (path relative to this directory) |
| `:pkg <path>` | install a `.vescpkg` through the connected tool's own installer; emits `{k:"pkg", path, ok}` and refreshes the firmware records |
| `:stats` | request one stats sample |
| `:ping` | emit `{k:"pong", connected:…}` |
| `:quit` | exit cleanly |
| `# ...` | ignored |

The watcher tracks a byte offset, so restarting keeps its place and old commands do not
replay; a half-written line is buffered until its newline arrives. Both verified.

### One-shot mode

```sh
./run.sh once [host] [port]      # run config.json, print, exit
```

Same script, no file watching; exits when the queue drains.

### Details

- `--loadQml` **must be an absolute path**. The script is injected through
  `Qt.createQmlObject`, so its base URL is `qrc:/res/qml/`; a relative path breaks both the
  sidecar config lookup and any file read. `run.sh` handles it.
- The mode rides in the URL fragment (`tcp://host:port#daemon`). vesc_tool rejects any flag
  it does not define (`main.cpp:756-763`, exit 1 plus help), so it cannot be `--lbmMode`.
- The harness is a second GUI-app process, so it needs the same `DISPLAY` as your window.
  `run.sh` refuses to start without one.
- Only TCP is supported. `--vescPort /dev/ttyACM0` makes `agent.qml` exit immediately: two
  processes cannot share one serial port, and driving it directly defeats the point.
- `--canFwd <id>` targets a different CAN node than the window is talking to. The two
  processes have independent `Commands`, so `setSendCan` does not leak between them.
- On disconnect the harness notices within one poll period, logs `disconnected`, and
  reconnects every 2 s. Verified by killing and restarting the relay underneath it: the same
  process served a command before and after.

## Configure it

`agent.qml` reads `config.json` from its own directory at startup, then lets the command
line override the connection. See `config.example.json`.

| Key | Default | Meaning |
|---|---|---|
| `expr` / `expressions` | `[]` | REPL expressions to run on connect, in order; string or array |
| `uploadPath` | `""` | `.lbm` file to erase + upload + run on connect. Destructive |
| `reduceLisp` | `false` | strip comments/spaces/imports before packing |
| `statsIntervalMs` | `1000` | stats poll period, only used when `stayConnected` is true; the device path floors at 1 s regardless |
| `replPaceMs` | `700` | minimum gap between REPL sends; below ~700 ms replies are lost |
| `replQuietMs` | `700` | no output for this long counts as "reply finished" |
| `canFwd` | `-1` | CAN node to target, `-1` = the window's own device |
| `stayConnected` | `false` | poll stats every `statsIntervalMs`; off by default because one record per second drowns the command stream — use `:stats` or the GUI |
| `quitWhenDone` | `false` | exit 0 when the queue drains (`once` mode) |
| `pollFileMs` | `400` | how often `commands.txt` is checked |
| `hideWindow` | `true` | unmap this process's own window at startup |
| `port` | — | only accepted as `tcp://host:port`; `--vescPort` overrides |

Config is read **once**, at startup. To change behaviour mid-session, send commands; to
change config, restart the job. Editing `config.json` under a running session does nothing.

```json
{
  "uploadPath": "/home/me/lbm/test.lbm",
  "expr": ["(set-print-prefix \"agent| \")", "(+ 1 2)"],
  "statsIntervalMs": 1000
}
```

The script never writes files. In `daemon` mode even `uploadPath` and `expr` are better sent
through `commands.txt` (`:upload`, bare expressions), so you do not have to restart to try
something.

## Reading the output

Each event is one line, `LBM|<TAG>|<payload>`, on stdout. `run.sh` strips Qt's `qml: `
prefix and everything that is not a harness line, so what the job stream shows is already
clean:

```
LBM|STATE|connected
LBM|OUT|{"k":"cmd","line":"(+ 1 2)"}
LBM|OUT|{"k":"tx","expr":"(+ 1 2)","tag":""}
LBM|PRINT|> 3
LBM|OUT|{"k":"reply","tag":"","lines":["> 3"]}
LBM|REPL|done (1 line(s))
```

`PRINT` is for humans; `OUT` is the machine channel. `OUT` is one JSON object per event, so
a caller parses replies without unpacking `|`-separated strings:

| `k` | Payload |
|---|---|
| `hello` | mode, port, on startup |
| `cmd` | `line` — a command read from `commands.txt` |
| `tx` | `expr`, `tag` — sent to the device |
| `reply` | `tag`, `lines[]`, optional `timeout` |
| `fault` | `why`, `hint` — two REPL timeouts in a row; the hint names the three known causes (slot taken, stale server, upload in flight) |
| `stats` | `stats` — the same map the GUI shows |
| `plot` | `x`, `y` |
| `upload` | `path`, `ok` |
| `connected` / `disconnected` | link state changes |
| `pong` | reply to `:ping`, with `connected` |

Every record carries `t`, epoch milliseconds.

| Tag | Meaning |
|---|---|
| `OUT` | structured record, table above — **parse this** |
| `STATE` | human lifecycle log: loaded, hidden, target, connected, upload |
| `CONF` | sidecar config loaded / missing / invalid |
| `TX` | a REPL expression was sent |
| `REPL` | reply finished (line count) or timed out |
| `PRINT` | interpreter output, including REPL results |
| `RUNNING` | reply to `lispSetRunning` |
| `STREAM` | `lispStreamString` progress / result |

`run.sh` filters to `LBM|` and strips the `qml: ` prefix. Do **not** add
`--debugOutFile`: it installs a handler that writes only to the file and silences stdout
(`main.cpp:134-141`).

## Capability map

Everything the Scripting page does, through the same two objects the page itself uses:

| GUI feature | Call | Source |
|---|---|---|
| Upload + run | `loader.lispUploadFromPath(path, reduce)` then `cmd.lispSetRunning(1)` | `codeloader.cpp:470` |
| Upload from string | `loader.lispUploadString(src, dir, reduce)` — does **not** erase | `codeloader.cpp:459` |
| Import resolution | second argument is the directory `import` is resolved from | `codeloader.cpp:240-290` |
| Erase | `loader.lispErase(size)` | `codeloader.cpp:63` |
| Stream code | `loader.lispStreamString(str, mode)` | `codeloader.cpp:489` |
| Read code back | `loader.lispReadWithPath()` (7.00 only) | `codeloader.h:48` |
| REPL send | `cmd.lispSendReplCmd(text)` — `COMM_LISP_REPL_CMD` = 138 | `commands.h:289` |
| REPL receive | `lispPrintReceived(str)` — `COMM_LISP_PRINT` = 135 | `commands.cpp:1018` |
| Run / stop | `cmd.lispSetRunning(bool)` | `commands.h` public slots |
| Stats + bindings | `lispStatsRxMap(QVariantMap)` | `commands.cpp:1040-1052` |
| Plot stream | `plotInitReceived`, `plotDataReceived`, `plotAddGraphReceived` | `commands.h:135-138` |
| Device telemetry | `getValues()`, `getStats(mask)`, `getImuData(mask)` | `res/qml/Examples/PollValues.qml` |

Two imports are required or nothing works: `Vedder.vesc.commands` for `Commands`, and
`Vedder.vesc.codeloader` for `CodeLoader` (otherwise `CodeLoader is not a type`). `VescIf`
and `QmlUi` are context properties from `QmlUi::startCustomGui`
(`vesc_tool:mobile/qmlui.cpp:95-97`).

## Constraints that bite

1. **One TCP client.** `TcpServerSimple::newTcpConnection` closes the second socket
   (`tcpserversimple.cpp:134-137`). Close the harness before pointing anything else at the
   port.
2. **The window must stay open and connected.** Closing it strands the harness; the harness
   then reconnects in a loop every 2 s and logs `connectTcp` until you restore it.
3. **The harness sees `isPortConnected()` only after the firmware version comes back.**
   `VescInterface::tcpInputConnected` sets `mTcpConnected = true` immediately, but the fw
   retry timer disconnects after ~2 s of silence (`vescinterface.cpp:3242-3260`). So with a
   window that has no device attached, the harness connects and then drops, forever.
3a. **A window with no device is a trap, and there is a one-line fix.** When the window's
   serial link is gone, `fuser /dev/ttyACM0` shows no holder, the window still listens, and
   the harness connects and drops forever (item 3). Reconnect without touching the GUI:

   ```sh
   vesc_tool --vescPort /dev/ttyACM0 --tcpServer 65103 --retryConn
   ```

   That single process connects to the ESC and serves TCP, so the harness attaches to it
   directly. Check the link before blaming the script:

   ```sh
   fuser -v /dev/ttyACM0        # must show the vesc_tool pid
   ss -ltnp | grep 65103        # must be LISTEN on that pid
   ```

4. **Do not touch the same script from both sides.** An erase/upload from the window while
   the harness uploads produces interleaved chunked writes on one link.
5. **REPL replies are easy to lose, and there is no correlation id.**
   `lispSendReplCmd` returns `void` and answers arrive as undifferentiated
   `COMM_LISP_PRINT`. Measured on 7.00 + fw 7.0 against a real ESC:
   - sending four expressions back to back answered only the first;
   - pacing at 250 ms lost every second one;
   - **700 ms answered 8/8**, with stats polling both on and off.

   Root cause, firmware side: `COMM_LISP_REPL_CMD` is *silently dropped* when the previous
   command is younger than half a second — `if (UTILS_AGE_S(repl_time) <= 0.5) return;`
   (`vesc/lispBM/lispif.c:288-290`). No error, no echo, nothing. That is why 250 ms loses
   every second one and 700 ms loses none, and why nothing on the host side can fix it.

   So the driver serialises: one expression in flight, next one only after the reply has
   been quiet for `replQuietMs`. Completion is "no output for 700 ms", not "one line", because
   `(print "x")` emits the printed line *and* the echo `> t`. There is no `<<END>>`
   sentinel any more: it was measured to arrive while later expressions were still
   unanswered, so it cannot be trusted. Expect ~1.4 s per expression round trip.
6. **Uploads block in nested event loops, and the device blocks inside the acks.** Erase up
   to 8 s, each 384-byte write up to 1 s with 5 retries (`codeloader.cpp:74-92, 398-420`).
   Timers and stats polling stall for the duration, in the harness's process only.

   The host timeouts are only half of it. On the device, `COMM_LISP_ERASE_CODE` calls
   `lispif_stop()` and erases **both** the const region and the code region before a byte is
   streamed (`vesc/comm/commands.c:1403`), and the **first stream chunk** runs the entire
   restart and parse synchronously before it acks (`vesc/lispBM/lispif.c:494`). So that ack
   has to cover stop + two sector erases + parse of the whole script.

   Measured on an STM32 ESC: 7 KB uploads in 2.9 s, 10 KB in 3.1-3.5 s — identical with and
   without a `@const-start` block. Consequences you will hit:

   - **Failures are timeouts, not rejections.** A `FAILED` verdict usually means the ack
     arrived after the 8 s erase / 4 s chunk budget, or the TCP session dropped inside that
     window (52 disconnect/reconnect cycles observed in one failed attempt), while the
     firmware finished the work anyway. Verify by *calling a function*, never by the verdict.
   - **Never queue anything behind an upload.** The next command executes against a
     half-built image and fails with `variable_not_bound`; the tell is that it looks like a
     missing definition rather than an upload problem.
   - **One upload at a time, spaced.** Four uploads 45 s apart succeeded 4/4; three
     back-to-back failed 3/3, const block or not.
   - **Keep the artifact small.** Comments are shipped and re-parsed (the ESC stores the
     script as text), so strip them for the file you upload.
7. **`lispUploadFromPath` erases, `lispUploadString` does not.** The GUI erases explicitly
   with `size + 100` before `lispUpload` (`pagelisp.cpp:686-695`).
8. **Size cap is derived from the fw params the harness read**: 128 KiB STM32, 512 KiB
   ESP32, and 128 KiB if the type is unknown (`codeloader.cpp:380-388`).
9. **Stats requests are dropped, not queued, and the client caps them at 1 Hz.**
   `lispGetStats` returns immediately while a request is in flight (`commands.cpp:2244`),
   and that flag clears only on the reply or after 100 × 10 ms ticks (`:1023`, `:2371`). So
   nothing — not `statsIntervalMs`, not the GUI's `pollRateBox` — can exceed 1 request/s.
   Running two pollers halves each one's effective rate rather than doubling resolution.
   Each request costs a `pause_eval(0, 2000)` on the device (`vesc/lispBM/lispif.c:252`),
   which suspends the evaluator for a few ms; that is jitter, not throughput loss.
10. **Long expressions must be streamed.** The GUI switches at 400 characters
    (`pagelisp.cpp:369`); `runBlock()` does the same.
11. **`--qmlAutoConn` destroys the script.** Its reconnect timer reloads
    `DynamicLoader.qml` every second while disconnected (`main.cpp:1059-1067`), which tears
    down the object tree your script lives in, and the script is never re-injected.
    `agent.qml` owns its own connect timer for this reason. This applies whether or not you
    use TCP.
12. **A killed client leaves the window's server half-dead.** After a harness or panel is
    killed (SIGKILL, `timeout`, a `proc://…/kill`), the window's `TcpServerSimple` can end
    up *accepting* new connections that relay nothing — observed twice on hardware, and it
    looks exactly like "the VESC stopped answering". Recovery: re-tick
    *Connection → TCP Server* in the window. Prevention: stop sessions with `:quit` or a
    clean SIGTERM — `Driver.qml` closes the TCP client from `Component.onDestruction`, and
    `run.sh ask` after an unclean kill is the fastest way to notice (it times out and says
    so).
13. **A crashed vesc_tool leaves `/var/lock/LCK..ttyACM0`.** The window then cannot reopen
    the serial port and everything downstream looks broken. Removing the lock needs the
    user's say-so — it is a shared-resource decision, not a debugging step. Ask.
14. **`vesc_tool` on PATH may be old.** `run.sh` uses `$VESC_TOOL` or `vesc_tool` from
    PATH. The 6.06 release silently lacks `lispStatsRxMap`, so REPL and `:ping` work while
    `:stats` never produces a record — verified against both binaries. If stats vanish,
    check the version first: `vesc_tool --version`, or set
    `VESC_TOOL=/path/to/vesc_tool_7.00`.

## Extending the harness

Add to `Driver.qml` rather than forking it. The shape is: config block, `log()`, `emit()`,
`repl()`, `replFile()`, `runBlock()`, `upload()`, `handleLine()`, one connect timer, one poll
timer, one `Connections` block. To add a command, extend `handleLine()`; to add an event,
emit a new `k`.

The watch loop reads whole files with a byte offset from the previous read, because QML
cannot seek. `commands.txt` is therefore expected to grow, not to be rewritten with the same
or smaller content — shrinking resets the offset, which is handled but means a rewrite
replays nothing. If you want a queue rather than a log, move the file aside and rename it
back (a "consume" pattern) and handle the inode change.

Wanted next, roughly in order:

- A "consume" queue instead of an append-only log, so `commands.txt` does not grow unbounded
  over a long session.
- A small file-replay queue: drop `*.lbm` into a watched directory and upload each in turn.
- Read-back diff: erase nothing, `lispReadWithPath()`, and compare against the local file so
  an agent can tell whether the device matches the repo.
- Probe whether a *host-side* delay is really required, or whether the loss comes from
  `lispSendReplCmd` queueing inside `Commands`. If a reply-driven schedule alone suffices,
  drop `replPaceMs` to 0 and the round trip halves.
- `scanCan()` / `getCanDevsLast()` plus per-device prefixes, for multi-VESC benches.

## Testing without hardware

Two layers, both already in this tree:

1. **`fake_vesc.py` in this directory** — a TCP server speaking the real packet protocol
   (start byte, length, CRC-16/CCITT, stop byte), answering `COMM_FW_VERSION`,
   `COMM_LISP_REPL_CMD`, `COMM_LISP_GET_STATS`, `COMM_LISP_SET_RUNNING`. The harness
   attaches to it exactly as it would to your window, so connect, `ask`, `:stats`,
   `:ping`, `:quit`, reconnect and the fault path can all be exercised with no device:

   ```sh
   python3 fake_vesc.py 65199 &
   VESC_TOOL=<vesc_tool_7.00> xvfb-run -a ./run.sh 127.0.0.1 65199   # as a background job
   ./run.sh ask '(+ 1 2)'
   ```

   Extend a handler when a test needs it; do not add realism you will not assert on. One
   trap it already encodes for you: every reply starts with its own command id —
   forgetting that byte makes vesc_tool connect but never accept the firmware version.
2. **Host dry-run of the script itself** — `ref/testing.md` in the parent skill: stub the
   VESC-only functions and run the `.lbm` in the bundled x86-64 REPL before ever
   uploading. A real session used exactly this (`host/stubs_probe.lisp`) and it caught
   protocol bugs with zero hardware.

## Why not the alternatives

| Route | Verdict |
|---|---|
| `--uploadLisp`, `--eraseLisp`, `--bridgeAppData` | One-shot only. No REPL, no `print` capture, no stats. |
| Own protocol client against the TCP server | Full capability, but you reimplement framing, CRC, chunked writes with per-chunk acks, and every `COMM_LISP_*` payload. `CodeLoader` already does all of it. |
| "QML Scripting" page inside the window | Same engine, but the script would share the window's process; no isolation, and no second stdout. |
| Serial `--vescPort /dev/ttyACM0` from the harness | Two processes cannot share one serial port, and driving it directly loses the observation loop. `agent.qml` refuses. |

If you ever need this with no window at all, the gap is a `QCoreApplication` +
`QQmlEngine` mode in `main.cpp` that skips `QmlUi`; it does not exist today.

## Refinement log

Append one dated entry per session that uses this. Say what you ran, what broke, what you
changed. Drop the `[UNVERIFIED]` tags as they get confirmed.

- **2026-11-14 (persistent session)** - Replaced the per-command launch with one long-lived
  process. `agent.qml` gained a file-driven command protocol (`commands.txt` with
  `<expr>`, `:multi`, `:run`, `:upload`, `:stats`, `:ping`, `:quit`), structured `OUT`
  records on stdout, `hideWindow`, and reconnect-on-drop; `run.sh` became a launcher with
  `attach` / `once` / `send`.

  Two design mistakes found and removed:

  1. **Reinvented process supervision.** The first version added `setsid`, a pidfile, and
     `status`/`stop` verbs. Unnecessary: the agent's job facility already provides names,
     readiness detection and kill-by-id. Worse, it was *broken*: `$!` after backgrounding a
     pipeline is the last stage, so the pidfile tracked `sed` and `status` said "not
     running" while vesc_tool was alive, leaving orphaned processes. Deleted.
  2. **An `out.jsonl` side file.** The shell re-derived it from stdout with
     `tee | grep | sed`. Redundant: the job's stdout is already the channel, and `run.sh`
     filters it to `LBM|` lines. Deleted.

  Verified live against a relay: window unmapped but script running; commands served with
  replies (`(+ 2 3)` → `> 5`, `(get-vin)` → `> 23.41f32`); `:multi` split and serialised;
  `:stats` and `:ping` answered; half-written lines buffered until newline; disconnect
  detected and reconnected with the same process serving commands before and after. Still
  `[UNVERIFIED]`: upload and plot capture.

  Two more things learned the hard way: continuous stats polling is off by default because
  one record per second buried the command stream, and `pkill -f agent.qml` kills the shell
  that runs it (its own command line matches). Use `pkill -f 'vesc_tool.*agent[.]qml'`.

- **2026-11-14 (polling correction)** - The earlier claim that GUI polling "runs at 10 Hz
  and swallows the harness's calls" was wrong on both halves. `pollRateBox` is cosmetic:
  `Commands::lispGetStats` self-throttles at `mTimeoutCount = 100` × 10 ms, so both the GUI
  and the harness are capped at 1 request/s no matter what they ask for
  (`commands.cpp:2244`, `:2371`). Reverse-engineered the real device cost from
  `vesc/lispBM/lispif.c:210-286`: the reply is ≤300 bytes and cheap, but each request calls
  `pause_eval(0, 2000)` and suspends the evaluator while walking 32 global-env roots at 1 ms
  polling granularity. Conclusion changed from "leave it off" to "Poll All is fine" —
  ~1 Hz of a few-ms jitter. Not measured live: `/dev/ttyACM0` was held by an unrelated
  `fish-api` process at the time, so this entry is source-derived, not empirical.

- **2026-11-14 (hardware pass, fw 7.0 / 60_MK6 on /dev/ttyACM0)** - Ran the harness end to
  end against a live ESC through a `--tcpServer` relay. Confirmed working: connect, queued
  REPL expressions, `set-print-prefix`, stats map, and real values
  (`(get-vin)` → `23.44f32`, `(get-rpm)` → `0.0f32`).

  Found and fixed a real bug: **REPL replies are dropped under back-to-back sends.** Bursting
  four expressions answered only the first. The first version of the harness sent every
  configured expression immediately and used a `<<END>>` sentinel, which does not work: the
  sentinel arrived while later expressions were still unanswered. Replaced with a serialised
  queue plus a quiet-window completion detector. Pacing sweep, same expressions each run:

  | Pace | Replies lost |
  |---|---|
  | no gap (burst) | 3 of 4 |
  | 250 ms | every second one |
  | 700 ms | 0 of 8 |
  | 1000 ms | 0 of 8 |

  700 ms is the default. Stats polling is not the cause; the boundary is the REPL itself.

  Also verified: `--tcpServer` is a separate headless mode with no main window, so it is not
  how you start the observable setup; the GUI checkbox is the only way and it is not
  persisted (a plain launch opens no listener). Still `[UNVERIFIED]`: `uploadPath` and
  `plot-*` capture.

- **2026-11-15 (learnings from a real agent session + no-hardware verification)** - Read
  the "Research Feetech servo TTL protocol" session end to end (2026-11-14, 10:43-16:10)
  and folded in what it cost that session to learn:

  1. It never ran `run.sh`, hand-rolling four throwaway harness instances
     (`lbm-harness`, `lbm-bench`, `lbm-bench2`, `lbm-diag`) instead.
  2. It launched `vesc_tool --loadQml` 31 times, one per bash call, each opening a
     "VESC Custom GUI" window that closed when the call ended.
  3. Its command loop was `cat >> commands.txt && sleep 8` — no reply correlation.
  4. Its own panel and its REPL probe fought over the single TCP slot ("The panel holds
     the TCP slot, so those sends went nowhere").
  5. A killed client left the window's server accepting-but-not-relaying.

  Changes made for each: `run.sh ask`/`wait` with a tee'd `harness.log` (3); `panel.qml`
  so one process is both panel and driver (4); a `fault` record naming the three causes
  of a silent link plus `STATE|suspect` (5, partly); `Driver.qml` closes the TCP client
  from `Component.onDestruction` and `:quit` (5); constraints 12-14 document the stale
  server, the serial lock file, and the 6.06-binary `lispStatsRxMap` gap; the REPL gate
  got its firmware root cause (`lispif.c:288-290`); `fake_vesc.py` shipped.

  Everything above was then verified without hardware, against `fake_vesc.py` with
  `vesc_tool_700` under Xvfb: connect and stay connected; `ask` returns the reply record
  in 0.85 s; `:stats` returns the parsed map; `:ping`; `:quit` closes the TCP client and
  exits 0; `panel.qml` loads, connects, and serves `commands.txt`; killing the fake
  triggers disconnect/reconnect; a mute fake (fw handshake but no REPL replies) produces
  two `timeout:true` replies and then the `fault` record with the hint.

  Two testing traps found while doing that: passing a regex through `awk -v` eats its
  escapes (the first `ask_scan` matched the `tx` line itself — now literal `index()`
  matching), and `run.sh` picked the 6.06 `vesc_tool` from PATH, where `lispStatsRxMap`
  does not exist — REPL worked, stats silently did not. That binary gap is now
  constraint 14.

  The fake also encoded one protocol lesson the hard way: replies must start with their
  own command id. Without it, `fwVersionReceived` never fires, `isPortConnected()` still
  reads true (it only means the TCP socket is up), and VESC Tool just keeps polling until
  "No firmware read response" — a failure that looks like a dead device.
