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
