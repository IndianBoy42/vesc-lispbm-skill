---
name: vesc-lispbm
description: "Write, test and debug lispBM scripts and native C extensions for VESC motor controllers. Use when coding in lispbm for VESC firmware, interfacing with motors/CAN/GPIO/IMU/thermal sensors, building native C extensions, or running a script off-target in the bundled lispBM REPL."
---

# VESC LispBM Skill

Write lispBM (LBM) scripts and native C extensions for VESC motor controllers.

## Quick Start

LispBM scripts run on VESC firmware via VESC-Tool. Scripts are uploaded to flash and run autonomously. Native C extensions are compiled separately and loaded as binary blobs.

### Minimal LispBM Script
```lisp
; Runs once on upload, then loop-fn runs repeatedly
(define loop-fn (lambda ()
    (progn
        (define rpm (get-rpm))
        (define duty (get-duty))
        (print "RPM: " rpm " Duty: " duty)
        (sleep 0.5))))

(loop-fn)
```

### Minimal Native C Extension
```c
#include "vesc_c_if.h"

HEADER

static lbm_value ext_my_func(lbm_value *args, lbm_uint argn) {
    if (argn != 1 || !VESC_IF->lbm_is_number(args[0])) {
        return VESC_IF->lbm_enc_sym_eerror;
    }
    return VESC_IF->lbm_enc_i(VESC_IF->lbm_dec_as_i32(args[0]) * 2);
}

INIT_FUN(lib_info *info) {
    INIT_START
    (void)info;
    VESC_IF->lbm_add_extension("ext-my-func", ext_my_func);
    return true;
}
```

## Deploying and watching a script

1. VESC Tool → *LispBM Scripting* → load the `.lbm` source and upload. The script starts
   running as soon as it is uploaded; a top-level infinite `loopwhile` blocks that thread,
   `loopwhile-thd` (a macro over `spawn`) leaves the main thread free for the console.
2. The script image is stored in flash and runs again on boot. `lbm-erase` clears it,
   `image-save` writes the current heap out, `lbm-write`/`lbm-run` manage it by hand.
3. Watch it: `plot-init` / `plot-add-graph` / `plot-send-points` feed VESC Tool's plot tab,
   `print` goes to the terminal, `(send-data ...)` sends custom app data (also readable
   from a Qml script), and `log-config-field` + `log-start` + `log-send-f32` writes a
   proper log: `-1` streams it into VESC Tool, `-2` records to the Express SD card
   (`express-logging/SKILL.md`).
4. `(stats)` in the terminal gives heap use, GC counters and the GC stack high-water mark —
   the first thing to check when a long-running script behaves oddly or restarts.
5. **An upload can report `FAILED` and still have worked.** The firmware stops LispBM and
   erases two flash regions before streaming a byte, then runs the whole restart and parse
   inside the first chunk's acknowledgement (`comm/commands.c:1403`, `lispBM/lispif.c:494`),
   while the host waits 8 s for the erase and 4 s per chunk. Verified: four uploads spaced
   45 s apart succeeded in ~3 s each, const block or not; three back-to-back failed 3/3. So:
   keep the uploaded file small (strip comments), do one upload at a time, do not queue
   commands behind it — they run against a half-built image and fail as
   `variable_not_bound` — and confirm by calling a function rather than trusting the verdict.
   Numbers and the mechanism: `ref/performance-and-memory.md`; harness detail:
   `vesc-tool-harness/SKILL.md`.

### Driving the interpreter from a host script

vesc_tool has **no REPL on the command line**: `--uploadLisp` uploads and runs, but nothing
prints what the script says and there is no way to evaluate an expression.

The way to script it while still watching it is `vesc-tool-harness/SKILL.md`: keep a VESC
Tool window open on the Scripting page, enable its *TCP Server*, then start the harness
**once** as a background job. It hides its own window and stays up for the whole session, so
nothing flashes open and shut; commands are appended to `commands.txt` (`./run.sh send
'(get-vin)'`) and replies come back on the job's stdout. The window keeps rendering the
console, plot and stats, so you see what the agent is doing.

That directory is **experimental**; read `vesc-tool-harness/SKILL.md` and its Refinement log
before relying on it.

Two facts about the device that matter whichever way you drive it:

- `COMM_LISP_GET_STATS` suspends the evaluator (`vesc/lispBM/lispif.c:252` calls
  `pause_eval(0, 2000)`), so stats polling is jitter in your script's sample period.
- Nothing can poll it faster than 1 Hz: `Commands::lispGetStats` self-throttles for 1 s
  (`vesc_tool:commands.cpp:2244`). The GUI's poll-rate spinbox is cosmetic.

## Architecture

### How It Works
1. **LispBM** is a lisp/scheme-like scripting language for microcontrollers
2. **VESC firmware** embeds LispBM as its scripting engine
3. **VESC-Tool** provides the IDE for writing/uploading scripts
4. **Native extensions** are C functions compiled to ARM thumb binaries, uploaded as byte arrays, and loaded with `load-native-lib`

### Where things are
This skill lives inside a VESC firmware checkout, so paths below are relative to the skill
directory (`<fw>/lispBM/skill`).

- `../README.md` — **the ESC/Express extension reference**: every function a script can
  call, with signature, platform (ESC vs Express) and minimum firmware version. It is the
  only complete list; this skill does not duplicate it.
- `../lispif_vesc_extensions.c` — ground truth for which names the firmware registers
  (`lbm_add_extension("name", ...)`) and with what argument handling.
- `../lispif.c` — script heap sizing, image save/restore, the `(stats)` counters.
- `../lispBM/` — upstream lispBM: `src/`, `include/`, `doc/` (language, runtime, display and
  dynlib references), `repl/` (a working x86-64 REPL: `repl/repl`), `tests/`.
- `../c_libs/` — native extension SDK: `vesc_c_if.h`, `rules.mk`, `examples/`.
- `../lispif_c_lib.c` — implementation of the C interface (`VESC_IF`) inside the firmware.

### Loading Native Extensions from Lisp
```lisp
; The byte array comes from the compiled .lisp output
(def my-lib [0x01 0x02 ...])  ; compiled binary
(load-native-lib my-lib)       ; call init, register extensions
(ext-my-func 42)               ; call the extension
(unload-native-lib my-lib)     ; cleanup
```

## Language Essentials

See `ref/` directory for section-by-section language reference extracted from `lbmref.md`.

### Key Differences from Common Lisp
- **Case-insensitive** symbols: `foo` == `FOO`
- **28-bit integers** by default (not 64-bit)
- **Extensions** must start with `ext-` prefix
- **`setq`** not `set!` for variable assignment
- **`progn`** / `{}` for sequences; `atomic` for critical sections
- **`trap`** for error handling (returns `'(exit-ok val)` or `'(exit-error sym)`)
- **Byte arrays** `[1 2 3]` are distinct from lisp arrays `[| 1 2 3 |]`
- **Concurrency** via `spawn`/`send`/`recv` (Erlang-style)
- Numbers are **float32** on VESC (`lbm_float = float`): a single precision sum over a long
  window loses the variance the fit is made of, so keep accumulators small (centre them on
  a window reference rather than on zero) or use fewer samples.

### Traps that fail silently or cryptically
- **`t` and `nil` are self-evaluating constants.** `(defun f (t) (+ t 5))` compiles and then
  throws `type_error` on every call. Never bind `t`.
- **`defun` takes exactly one body expression.** `(defun f (x) a b)` defines the body as `a`
  and silently drops `b`; wrap multi-statement bodies in `{ ... }`.
- **No scientific notation.** `1e-9` reads as the symbol `e-9`, not a number.
- **Integers above 2^24 are not exact through a float.** A 29-bit CAN EID
  (3.5e8) in float32 has a spacing of 32, so `(+ eid 1)` returns `eid` and
  six frames all go out with the same id. The snapshot getters return
  floats; run ids, counters and frame offsets through `to-i32` first.
- **Sleep granularity is a scheduler tick, not the seconds you asked for.**
  A 5 ms `sleep` on the Express behaves like 10 ms (or coarser), so a
  lisp loop that must outpace a 200 Hz consumer cannot; pace the consumer
  lower or send two samples per period.
- **`def`/`define` write the global environment**, from anywhere, including inside a
  function or a `{}` block. Use `let` for anything local.
- **`bufget-f32`/`bufset-f32` index in bytes**, not elements: element `i` is at `(* 4 i)`.
- **`mod` follows the sign of the dividend**; add the modulus before the `mod` if the result
  must be non-negative.
- **`loopwhile-thd` takes three arguments:** `(loopwhile-thd <stack-size>
  <cond> <body>)`, e.g. `(loopwhile-thd 100 t { ... })`. It is not
  `(loopwhile-thd t body)`.
- **`ext-` names are reserved.** `defun` of anything starting with `ext-`
  errors with "Cannot redefine built-in", even on the host REPL — the
  firmware binds those symbols at `load-native-lib`. Stub them under
  different names for host tests.
- **Extension functions run on a 2048-byte C stack** (the evaluator
  thread's). No newlib trig, no `%f` printf, no deep call chains — see
  `ref/performance-and-memory.md`, which also covers the one-packet
  recovery for a crash-looping device.
- **A native-lib byte array above ~20 KB of code fails to parse at boot**
  (`out_of_memory`, "Mem longest free"): the literal reader reserves only
  0.9x the longest free pool block. The failed parse **leaks** that
  scratch array - `:reset` does not reclaim it, the next boot fails
  again, and only an MCU reboot (or an upload, which resets the VM, e.g.
  a tiny stub script) clears it. Measured ceilings and the decimal-token
  packing trick that lifts the flash limit are in
  `ref/performance-and-memory.md`.
- **Interpreter costs are now measured**: ~56 us per `looprange`
  iteration (the loop machinery is the dominant term), +7-12 us for a
  zero-argument call, **+29 us for a one-argument call**, +4 us for a
  trivial ext entry, and an 8-10x GC cliff once live cons cells pass
  ~30%. Prediction table and the split-lisp-vs-C guidance:
  `ref/performance-and-memory.md`.
- **Check the units before dividing a counter.** `systime` is 10 kHz
  (100 us ticks), `timer_time_now` is TIM5 at 14 MHz (**divide by 14**
  for us), sleeps round up to 100 us. Getting this wrong twice already
  produced figures that were 10x and 14x off. Full table with sources:
  `ref/performance-and-memory.md` section 0.
- The full verified table, with symptoms, is in `ref/testing.md`. Read it before a long
  debugging session.

### Default: put everything you can in the const heap

**This is the default guideline, not a tuning step.** Anything that is not mutated at
runtime belongs in an `@const-start` / `@const-end` block: function definitions, tables,
string constants, and the native-extension image itself. It costs nothing at call time and
buys back the 22 KB cons heap and the 28 KB array pool.

```clj
@const-start
(defun control (x) (+ x 1))
(def lut [1 2 3 4])
(load-native-lib [ ...extension image bytes... ])   ; image lives in flash
@const-end
(def mutable-state (bufcreate 64))                  ; stays in the pool
```

Measured on a VESC 6 MK6 (fw 6.06-era):

| | in the heap/pool | in the const heap |
|---|---|---|
| 30-function driver | 2497 live cells, 0 free | 178 live cells, 2563 free |
| 18.6 KB extension image | occupies 18.6 KB of the 28 KB pool | **0 bytes of it**; `bufcreate 20000` succeeds where it previously failed with `Mem longest free: 0` |
| same kernel, 20 k iterations | 356.8 ms | **295.6 ms** (−17 %, the F4 ART accelerator covers flash but not SRAM) |

Rules and limits:

- Only the **incremental reader** honours the markers, so this works for an uploaded
  script (VESC Tool / `:upload`), not for a streamed or REPL-entered one.
- On boot the script is re-parsed from flash, so the block re-runs: a
  `(load-native-lib ...)` inside it re-registers the extension while the array stays a
  flash const (verified: `:reset` prints "Parsing <n> characters", the extension is back,
  and the pool is still free).
- The const heap is **write-once**. A changed image needs that flash region erased, which
  the firmware does when it recreates the image (`const_write_error`, app-CRC change) or
  on an upload; iterating on an image otherwise reports "Attempted to write to const heap
  at N, but it is already occupied".
- Nothing in a flash image can be written: lisp refuses (`type_error`) and a C store gives
  `fatal_error`. A native extension therefore may hold **no writable statics** — no
  globals, no `static` counters — if it is to live there. Callbacks with no context
  argument (`can_set_eid_cb`, `imu_set_read_callback`) cannot reach heap state from flash
  code, so such an extension splits into a flash part (logic) plus a tiny RAM part holding
  the state and the callback; see `ref/performance-and-memory.md`.
- `move-to-flash` does the same for one value after the fact, and `dm-create` regions stay
  in the pool by design (they exist to be compactable).

### Cost and lifetime of a script
- Memory: 2753 cons cells (22024 B) plus a separate 28672 B pool for arrays and byte
  buffers (`../lispif.c`). A ring buffer of N floats costs `4*N` bytes of the pool.
- **The script's code lives in that heap.** Every `defun` body is parsed into cons cells and
  stays live through its closure, so ~9-12 bytes of source costs one 8-byte cell: a 23 KB
  script fills the heap and every allocation then pays a full GC. Wrap the definitions in
  `@const-start` / `@const-end` (the uploaded-script path uses the incremental reader, so it
  works) and they move to flash instead — 2497 live cells fell to 178 on the bench driver,
  with no call-time penalty. The same applies to a native extension image. Full numbers
  and caveats: the section above and `ref/performance-and-memory.md`.
- The script's globals live in one global environment that outlives the script's own
  thread and is shared with anything else loaded, so prefix names with something script
  specific rather than using `n`, `dt`, `i`.
- A script is uploaded to flash and runs on boot; `(stats)` reports heap use, GC counters
  and the GC stack high-water mark. To avoid the collector entirely, do not allocate in the
  loop: mutate buffers with `bufset-*` and lists/arrays with `setix`.

### VESC-Specific LispBM Functions
Available only on VESC firmware, not in standalone lispBM. Names below are verified against
`../lispif_vesc_extensions.c`; `ref/vesc-esc-extensions.md` maps the whole surface by group.

- Motor state: `get-rpm`, `get-rpm-fast`, `get-duty`, `get-current`, `get-current-in`,
  `get-id`, `get-iq`, `get-vd`, `get-vq`, `get-pos`, `get-batt`, `get-vin`, `get-fault`
- Thermal: `get-temp-fet` (argument selects sensor 1..3, 0/omitted = hottest), `get-temp-mot`
- Control: `set-current`, `set-current-rel`, `set-duty`, `set-brake`, `set-rpm`, `set-pos`,
  `set-kill-sw`, `select-motor`, `app-disable-output`
- Timing: `systime` (**100 us ticks** — 10 kHz on the ESC, microseconds on the Linux
  REPL), `secs-since` (seconds, wrap-safe), `sleep` (seconds; effective resolution
  100 us + the evaluator's 200 us poll, so `(sleep 0.002)` lands ~2.1 ms)
- Config: `conf-get`, `conf-set`, `conf-store`, `eeprom-store-f`, `eeprom-read-f`
- CAN: `can-send-sid`, `can-send-eid`, `can-recv-sid`, `can-recv-eid`, `canget-*`, `canset-*`
- IO: `gpio-configure`, `gpio-write`, `gpio-read`, `pwm-set-duty`, `icu-width`, `get-adc`,
  `i2c-start`, `i2c-tx-rx`, `uart-start`, `uart-write`
- IMU: `get-imu-rpy`, `get-imu-quat`, `get-imu-acc`, `get-imu-gyro`, `get-imu-mag`
- Instrumentation: `plot-init`, `plot-add-graph`, `plot-send-points`, `send-data`,
  `log-config-field`, `log-start`, `log-send-f32`, `stats`, `sysinfo`

Do not guess a name from another platform: there is no `can-send`, `disp-render` or
`get-imu-accel`, and the CAN temperature getters (`canget-temp-motor`) are spelled
differently from the local one (`get-temp-mot`).

## Reference Files

Regenerate from upstream sources:
```bash
# Language reference sections from lbmref.md
python3 gen_ref.py --lispbm-root ~/dev/vesc/lispBM/lispBM

# VESC C interface API docs from vesc_c_if.h
python3 gen_vesc_c_if_docs.py --header ~/dev/vesc/lispBM/c_libs/vesc_c_if.h

# Express extension tables from a vesc_express checkout
python3 gen_express_extensions.py --express-root ~/dev/vesc_express

# Device-QML API and component tables from a vesc_tool checkout
python3 qml-ui/gen_qml_refs.py --vesc-tool-root ~/dev/vesc_tool
```

- `ref/INDEX.md` — Master index of all language sections
- `ref/NN-*.md` — Individual sections from lbmref.md
- `ref/vesc-esc-extensions.md` — the ESC-side API map, where to look up a name, memory
  budget, and the traps around naming
- `ref/can-commands.md` — **CAN commands end to end**: the rx order (`decode_msg` before any
  Lisp copy), wire format and address matching, observing frames from Lisp with
  `can-recv-*`/`event-can-*` and the traps that make them unreliable samplers, and
  intercepting `SET_RPM`/`SET_POS` with a native lib's `can_set_eid_cb` to run your own
  control loop instead of the built-in PID. Read before writing anything that reacts to CAN
  or replaces firmware motor control
- `ref/vesc-express-extensions.md` — **generated**: every name the Express firmware
  registers (display, WiFi/TCP, BLE, NVS, crypto, board `hwconf`), with the C handler,
  signature comment where the source has one, and file:line. Express-only names are not
  on an ESC, so check here before assuming a function exists on both
- `ref/testing.md` — **how to run a script headlessly** on the bundled x86-64 REPL, how to
  stub the VESC-only functions with a synthetic signal, and the verified gotcha table
- `ref/performance-and-memory.md` — **the measured cost model**: heap and pool sizes on the
  ESC, what each construct costs, `@const-start`/`move-to-flash`/`dm` with numbers, the
  profiling toolkit, and the rules that follow
- `ref/doc/lbmref.md` — Full language reference
- `ref/doc/runtimeref.md` — Runtime extensions
- `ref/doc/gotchas.md` — Gotchas and caveats
- `ref/doc/displayref.md` — Display library
- `ref/doc/dynref.md` — Dynamic loadable functions
- `vesc-tool-harness/SKILL.md` — **experimental**: drive the interpreter from a host script
  over a VESC Tool window's TCP server, watching what it does in that window.
  `run.sh ask` is the entry point; `panel.qml` is the visible variant; `fake_vesc.py`
  tests it all with no hardware
- `qml-ui/SKILL.md` — **custom GUIs**: writing a QML UI that any VESC Tool renders
  (desktop, Android, iOS), the flash slot and package format that deploy it, a
  working template package, and generated tables of the QML API. Read before
  touching a package's `ui.qml` or debugging a GUI that does not appear
- `express-logging/SKILL.md` — **SD logging**: the `log-*` API with `can-id -2`,
  feeding fields from CAN status polls or custom `event-can-eid` frames, EEPROM
  settings and at-boot logging, and why a log comes out empty
- `native-extensions/SKILL.md` — C extension development guide
- `native-extensions/vesc_c_if_api.md` — Auto-generated VESC C interface API reference
