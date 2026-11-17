# LispBM on the VESC: memory and performance

What a LispBM script costs on this firmware, measured on a VESC 6 MK6 (fw 7.0), and
what to do about it. Every number here was measured on hardware, not derived — the
bench driver behind it is `~/dev/feetech/vesc-lispbm/hd_gui.lbm`.

Companion material: `20-defragmentable-memory.md` and `28-flash-memory.md` are the
upstream reference chapters for `dm` and the const heap; this file is the practical,
measured view of when to reach for which.

The one-sentence version: **the script's code is the heap**, so a 22 KB script fills the
22 KB cons heap and every allocation then pays for a full GC — moving the code to flash
with `@const-start` took this driver from 2497 live cells and 0 free to 188 live cells and
2563 free, and made feedback 6x faster without touching the bus.

## 0. Time units — read this before dividing any counter

Two independent unit mistakes have already been made in this project, and both produced
plausible-looking numbers: tick counts read as milliseconds (10x too big) and TIM5 ticks
read as microseconds (14x too big). Before dividing a counter, find its rate in the
firmware source. Every clock available to a script or an extension, verified:

| clock | implementation | unit | limits |
|---|---|---|---|
| `systime` (lisp) | `ext_systime` → `chVTGetSystemTimeX()`, `chconf.h: CH_CFG_ST_FREQUENCY = 10000` | **1 tick = 100 µs** | 32-bit, wraps every 119.3 h (~5 days) |
| `secs-since`, `VESC_IF->ts_to_age_s` | `UTILS_AGE_S(x)` = `chVTTimeElapsedSinceX(x) / CH_CFG_ST_FREQUENCY` | seconds, float | wrap-safe |
| evaluator `timestamp()`, hence `(sleep s)` | `platform/chibios/platform_timestamp.c`: ticks × (1e6 / ST_FREQUENCY) | **µs, but 100 µs granularity** | see the sleep row |
| `timer_time_now()` | TIM5, `driver/timer.c: TIMER_HZ = 1.4e7` | **1 count = 1/14 µs** | µs = count × 1e6/1.4e7, i.e. **divide by 14**; 32-bit, wraps every 306.8 s |
| `timer_seconds_elapsed_since(t)` | same counter / `TIMER_HZ` | seconds, float | wrap-safe |
| `VESC_IF->sleep_us()`, `chThdSleepMicroseconds()` | `chThdSleep(US2ST(us))`; `US2ST` rounds **up** (`os/rt/include/chvt.h`) | multiples of 100 µs | `sleep_us(1)` sleeps one tick, i.e. 100 µs |
| `VESC_IF->sleep_ms()` | `chThdSleepMilliseconds` | 100 µs resolution | integer milliseconds are exact |
| `sleep_ticks(ticks)` | `chThdSleep` | 100 µs per tick | — |
| `(systime)` on the **Linux** REPL | `repl/repl_exts.c: timestamp()` | **microseconds** | different platform: never port arithmetic between the two |

`(sleep s)` therefore takes multiples of 100 µs plus the evaluator's own polling interval
(`EVAL_CPS_MIN_SLEEP = 200` µs), so a control loop written as `(sleep 0.002)` lands at
~2.1 ms, not 2.000 ms. That is the 2-5 % overshoot seen in the sleep rows below, not a
scheduler bug.

## 1. The memory pools

| pool | size on this firmware | holds | set by |
|---|---|---|---|
| cons heap | **22024 B = 2753 cells** (8 B each: car + cdr, 32-bit) | lists, pairs, closures, `let` bindings | `HEAP_SIZE`, `lispif.c:47` |
| `LBM_MEMORY` | **28672 B**, bitmap allocator | arrays, strings, boxed floats, `dm` regions | `LISP_MEM_SIZE`, `lispif.c:48` |
| flash image region | **128 KiB** | image, symbol table, const heap | `lbm_image_init`, `lispif.c:738` |
| symbol table | 756 B (flash) | symbol names | — |
| GC stack | 160 words | mark stack | `GC_STACK_SIZE`, `lispif.c:51` |

The cons heap has no fragmentation problem (all cells are the same size), which is why
lists are cheap and arrays are not. `LBM_MEMORY` is fragmentation-prone; `dm-create`
exists to carve out a compactable region inside it.

Both are fixed at compile time. A script cannot grow them; it can only use less.

### The evaluator's C stack (extension writers, read this first)

The LispBM evaluator thread runs on a **2048-byte C stack** (`lispif.c:73`,
`eval_thread_wa`). Every extension function called from lisp executes on
it. A call chain that needs more than that corrupts the thread: the REPL
stops answering while the console keeps flushing prints, a stored image
restart-loops, and a firmware reboot follows. Verified on hardware with
an extension doing newlib trig (`cosf` -> `__ieee754_rem_pio2f` ->
`__kernel_rem_pio2f`, which has large stack locals) plus `%f` printf
(doubles): it wedged the evaluator on the first call.

Rules for `ext-*` entry points:

- No newlib trig; no `printf` with `%f`/doubles (integer formats only).
- No deep call chains — keep entry points flat.
- Long-running or allocation-heavy work goes in your own
  `VESC_IF->spawn` thread, which has its own stack and is not bound by
  this. Drive it from a shallow ext function.

Side benefit, measured: dropping newlib trig and double printf halved the
extension binary (11.5 -> 6.5 KiB) — libm machinery is the bulk of a
small extension.

Related: if a crash already stored in the image makes the device
reboot-loop on USB (enumerates ~1 s, drops, repeats), a full upload
cannot fit the window, but a single `COMM_LISP_ERASE_CODE` (132) packet
can: open `/dev/ttyACM*` the moment it appears and send it; retry each
cycle until the device stays enumerated, then re-upload. The port must be
free (stop any relay/GUI holding it) and the packet is
`[0x02 0x01 0x84 crc_hi crc_lo 0x03]` (CRC16-XMODEM of the payload).

## 2. Where a script's bytes actually go

Every `defun` body is parsed into cons cells, and the closure keeps them live for as long
as it is bound. Source length therefore maps to heap occupancy at roughly **9-12 bytes of
source per cell**.

Measured with 30 small functions, live cells after `(gc)`:

| how the 30 functions were defined | live cons cells | const heap |
|---|---|---|
| plain `(defun ...)` | **312** | 240 B |
| inside `@const-start` / `@const-end` | **80** | 2128 B |
| plain, then `(move-to-flash ...)` at runtime | **72** | 2160 B |

And the whole servo driver, which is ~23 KB of source:

| | live cells | free cells | GC events | `(hgu-read)` |
|---|---|---|---|---|
| everything on the heap | 2497 | **0** | 4801 | 870 ticks |
| code in a const block | **188** | **2563** | 2 | **~150 ticks** |

With 0 free cells every allocation triggers a full mark-sweep: `(hgu-read)` spent ~68 ms
in GC per call and occasionally failed outright mid-transaction with `out_of_memory`
(`Heap cells free: 2`). Headroom is not a tuning nicety, it is the difference between a
driver that works and one that randomly stops.

## 3. Moving code and data out of the heap

### `@const-start` / `@const-end` — the default choice for code

```clj
@const-start
(defun rs-flush () ...)
(defun hgu-read () ...)
@const-end
```

- Each global definition inside the block is copied to the const heap **as the reader
  parses it**, and the global is rebound to the flash copy.
- Requires the incremental reader. VESC's `:upload` uses
  `lbm_load_and_eval_program_incremental` (`lispif.c:829`), so it works there and not with
  plain `:load`-style reading.
- Blocks **cannot nest**, and each needs its closing `@const-end`.
- **No measurable call-time penalty**: 2000 calls of a one-line function took 2126 ticks
  from the heap, 2139 from a const block, 2128 after `move-to-flash` — 1.06-1.07 ticks per
  call in all three. The ART accelerator makes flash reads effectively free here.

### `move-to-flash` — runtime, for values created later

```clj
(define TABLE '(1 2 3 ...))
(move-to-flash TABLE)
```

Moves the value of each named global to flash and rebinds it. Use it immediately after
creation: anything still holding the old heap value keeps it alive.

### What must stay out of flash

Buffers and `dm` regions you intend to **write**. Flash cells are append-only; rewriting a
value in place is not what that path is for. Keep every mutable array, `bufcreate` and
`dm-create` outside the block — that is what the driver does.

### The flash budget and the reboot caveat

`:info` reports `Const Heap`, `Image` and `Free`. A fresh image has ~128 KiB free.

**Each reboot re-appends the const block.** Measured with `:reset`: 2128 → 3984 → 5840 B,
i.e. +1856 B per boot for a 1.8 KB block. The pointer saved at image creation is restored
on boot and the block is read again from the same code in flash, so the new copy lands
after the old one; the old copy is dead but unreclaimed.

### What an upload costs, and why it is not the const heap's fault

Every LispBM upload calls `COMM_LISP_ERASE_CODE`, which stops LispBM and erases **both**
the const region and the code region before streaming a byte (`comm/commands.c:1403`),
and the first stream chunk runs the whole restart and parse **synchronously** before
acking (`lispBM/lispif.c:494`). The host allows 8 s for the erase ack and 4 s per chunk
ack (`vesc_tool/codeloader.cpp`).

Measured on a stable link: a 7 KB script uploads in 2.9 s, a 10 KB one in 3.1-3.5 s,
identical with and without a const block. A four-way test (const vs heap × two files,
spaced) succeeded 4/4, each parsing its full length; three back-to-back uploads failed
3/3, again regardless of const blocks. Failures come from the host link dropping while
the device is blocked (52 disconnects seen in one attempt), not from const data. Keep
uploads small and spaced, and never queue REPL commands behind one.

Consequences for a ~23 KB driver: roughly **5 reboots** fit in the 128 KiB region. When the
region fills, the const write fails, `lispif` erases the const region on the next restart
(`lispif.c:710`) and rebuilds it — a slower boot plus a flash erase cycle, self-healing but
not free. `:upload` that creates a new image erases first, so development is unaffected.
Budget reboots accordingly, or wrap only the largest definitions.

## 4. Buffers: `dm-create` beats `bufcreate`

```clj
(define RS_DM (dm-create 240))        ; a compactable region in LBM_MEMORY
(define RS_RX (bufcreate RS_DM 40))   ; an array inside it, not on the heap
```

- `dm-create n` reserves `n` bytes; `dm-alloc`/`bufcreate` inside it hands out byte arrays
  that are **defragmented as a group** when an allocation fails, so a long-running script
  cannot lose `LBM_MEMORY` to fragmentation.
- Each array takes **12 bytes of header** inside the region (`lbm_defrag_mem.c:35`), so
  size the region with that overhead: 90 bytes of buffers needed `dm-create 256`; 224 and
  240 both failed.
- Buffers cost **zero cons cells** (only the pointer binding). Plain `bufcreate n` also
  lives in `LBM_MEMORY` but in the general allocator, where fragmentation can make
  allocation fail with free bytes still present.
- Use a `dm` for anything allocated once and written forever: UART frames, receive
  windows, scratch. This driver keeps nine buffers in one 240-byte region.

## 5. Measured costs

Taken with `(systime)` (100 µs ticks) on the bench ESC.

| operation | cost |
|---|---|
| call a one-line function (loop overhead included) | 1.06 ticks |
| 8-byte UART frame write | ~23 ticks of wire at 38400 |
| one read transaction, 8-byte block (22 B on the wire) | 70 ticks |
| one read transaction, 15-byte exchange | 48 ticks |
| `(gc)` with a small live set | 16 ticks |
| allocate a 2-element list **with headroom** | 0.88 ticks |
| allocate a 2-element list **with 0 free cells** | 128 ticks |
| build and print one output line (`str-from-n` + `str-join`) | 6 ticks |
| `(hgu-read)`, code on heap / in flash | 870 / ~150 ticks |

## 6. Rules

0. **Put everything that is not mutated in the const heap** (`@const-start`): code, tables,
   strings, and the native-extension image. It is free at call time and it is the only way
   to keep a 18 KB image out of the 28 KB array pool; measured 0 bytes of pool and 17 %
   faster execution. A flash image may hold no writable statics (writes give
   `fatal_error`), so extension state moves to `malloc` plus a small RAM module when a
   context-less callback is needed. SKILL.md has the full guideline.

1. **Keep free cells high.** Check `:info`; a heap above ~80% live means every allocation
   pays a GC. Target several hundred free cells minimum.
2. **Put code in `@const-start`;** keep the heap for mutable state and buffers.
3. **Never allocate in a control loop:** no `let`, no `list`, no `append`, no `str-*`
   formatting. Preallocate buffers and mutate them with `bufset-u8`.
4. **Collapse register reads into contiguous blocks.** Transaction count, not baud, sets
   feedback rate: seven single-register reads were 7x one block read.
5. **Prefer `loopwhile` / `looprange` to recursion;** the evaluator is CPS and each level
   costs stack and environment cells.
6. **Build strings only when you print.** `str-from-n` and `str-join` allocate in
   `LBM_MEMORY`; a hot loop that formats is a hot loop that fragments.
7. **Verify after every change** with `:info` — `Free cons cells`, `GC counter` and
   `Const Heap` tell you whether a rewrite actually helped.

## 7. Profiling on hardware

| tool | what it gives |
|---|---|
| `:info` | heap used/free, GC counter, recovered, marked, memory free/longest block, arrays, symbol table, const heap, image, flash free |
| `(gc)` | force a collection; time it with `systime` |
| `(systime)` | raw 10 kHz ticks (100 µs) — verified 32,048 ticks over 3.200 s |
| `(secs-since t)` | float seconds since a tick stamp |
| `:prof start` / `:prof report` | C-level profiler thread |
| `:reset` | restart LispBM (heap reset, const heap pointer restored) |

A useful pattern: wrap the call under test in a throwaway `defun` that prints
`(- (systime) t0)`, call it twice (the first call often warms the instruction cache), and
compare ticks. Keep those scratch closures out of the shipped script — on this heap two of
them used to be enough to exhaust it.

## 8. Gotchas

- **Closures capture their defining environment** by reference, so a closure created in a
  loop keeps that loop's bindings alive (`doc/gotchas.md`, "Closure Gotcha").
- `@const-start` cannot nest; an unclosed block swallows the rest of the file.
- **A frame's checksum is not a discriminator on its own.** In this driver the read
  request's checksum covers exactly the span a "headless" reply would cover, so the echo
  of our own request validated as a reply and `uart-read` returned the request's address
  byte. Requiring `ERR == 0` fixes it, at the cost of reading error frames as nil.
- The REPL line buffer rejects long expressions (`read_error`, "End of parse stream") well
  before the parser does. Upload a file, or define a function and call it, when a one-liner
  stops working.
- `sleep` and `uart-read` timeouts are honest seconds here; the earlier belief that they
  were 10x came from reading tick counts as milliseconds.

## 9. Interpreter cost model (measured, VESC 6 MK6 / fw 6.06-era)

All numbers below are wall-clock microseconds measured on one MK6 (168 MHz Cortex-M4F)
with a 1 kHz priority+2 control thread running in the background, which steals about
12-17% of the CPU; subtract roughly that share for pure interpreter time. Method: a
self-contained script uploaded as the image (`systime` ticks = 100 us, large `n` to beat
the tick resolution), printing one line per bench at load. That is the robust pattern:
REPL `ask` lines are truncated/desynchronized above ~1 KB, while an uploaded script has no
length limit and resets the VM.

### Per-form costs

| operation (per iteration) | us |
|---|---|
| `looprange` iteration with empty body (baseline) | 56 |
| trivial call `(f0)` | +12.5 |
| one-argument call `(f1 i)` (re-measured, no background thread) | +29 |
| call with 4 args and arithmetic in the body | +68 total |
| `(+ 1.2 3.4)` with literal args | +18 |
| `(+ ga gb)` with global lookups | +25 |
| `(cons 1 2)` discarded, garbage reclaimable by GC | +11 |
| `(bufset-u16 buf 0 1234)` / `(bufget-u16 buf 0)` | +21 / +18 |
| call a trivial native extension (`ext-probe`) | +11 |
| build a 10-element float list (`ext-tail-status`) | +52 |
| `(print "x")` | 365 |
| `(spawn 128 f)` (thread create) | 488 |
| `(sleep 0.001)` | 1046 (4.6% over nominal) |
| `(sleep 0.01)` | 10240 (2.4% over nominal) |

Predictions: `T_iter ~= 56 us + sum(form costs)`. A 40-form control iteration lands at
~2-2.5 ms, matching the CRSF script's 2-6 ms/iteration at 37-89% evaluator load. Note the
loop machinery dominates, not the call: a zero-argument call adds ~7-12 us, a
**one-argument** call ~29 us, and a trivial native-extension entry ~4 us (re-measured on
fw 6.06-era, floor-subtracted, `n = 5000`, no background thread). The old "~100 us per
call" figure was a call plus its surrounding loop, and "a call costs 12.5 us" is only true
for the zero-argument case.

### The GC cliff

`def`-shaped retention of cons cells while the heap fills (2753 cells, 22 KiB):

| live cells | us per additional cons |
|---|---|
| garbage-reclaimable (steady state) | ~11 |
| 800 live (~29%) | 84 |
| 1600 live (~58%) | 91 |
| 2400 live (~87%) | 106 |

Retaining live data makes every allocation pay a mark-sweep: a 8-10x cliff, and past
2753 live cells allocation fails outright. Budget live cells, not just allocations.

### Split guidance that falls out of it

- Deadlines or per-sample work: C (native extension or its own thread). The 1 kHz thread
  is unaffected by interpreter state; per-call ext entry costs only ~11 us, so calling C
  is cheap - it is the forms *around* it that cost.
- 10-50 Hz supervision, telemetry shaping, tuning procedures: lisp. A 10 Hz watchdog with
  one status call is <0.2% of the evaluator.
- Batch boundary crossings: one 10-field status call (52 us) beats ten scalar calls
  (10 x 11 us + ten loop iterations).

## 10. LBM pool and image-size limits (measured)

The script is stored as text in a ~131 KB flash region, and the byte array for a native
library must fit the 28 KiB LBM array pool *while being parsed*.

- **Array-literal parse ceiling.** The reader reserves `0.9 x longest_free_block` when it
  sees the first number of `[ ... ]` and fails (`out_of_memory`, "Mem longest free") if the
  array outgrows that. On a boot-clean pool this lands at ~20.1-20.9 KB of library bytes.
  Measured: 17.9 KB image boots; 20.1 KB boots; 20.9 KB and 21.1 KB fail at row 1.
- **A failed parse leaks its scratch array.** `:reset` does not reclaim it ("Allocated
  arrays: 1" persists) and the next boot fails again - only an MCU reboot rebuilds the
  pool. The *upload* path does reset the VM, so uploading a tiny stub script clears the
  leak without a reboot.
- **Text encoding sets the flash ceiling.** `c_libs/conv.py` packs `0xNN` tokens: 5
  chars/byte, so the ~131 KB region caps the binary at ~26 KB (a 27.8 KB binary yields a
  140 KB file and is rejected before flashing). Decimal tokens are ~3.6 chars/byte and
  raise the ceiling to ~35 KB; see `VescTail/pack.py` for a drop-in replacement.
- **Extension storage is 319 slots total** (`EXTENSION_STORAGE_SIZE`), shared by all
  libraries and never reclaimed on unload; `:info` shows the count. Loading many libraries
  (or re-loading one across boots) can exhaust it.
- **Binary fat that sneaks in.** The soft-double library costs ~2.4 KB: one `roundf()`
  call or a single `float -> int64` cast is enough to pull `__aeabi_f2ulz -> f2d -> dmul`.
  `%f` in `printf` pulls the double printf machinery (~2 KB) and a big stack frame. Use
  inline rounding, int32 casts, and integer formats.
- **Measure the loop, not just the kernel.** A permanent in-thread gauge
  (`avg/max step us` over a window, exposed as an extension) is cheaper and more honest
  than a bench kernel: it reports the real step including every feature, under real
  scheduling. Measured this way: full control step 122-171 us average, 350-660 us worst
  cycle, at a steady 1002 Hz loop period.
