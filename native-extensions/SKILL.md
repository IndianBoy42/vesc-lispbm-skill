---
name: vesc-native-extensions
description: "Write, compile, and include native C extensions for lispBM on VESC. Use when building high-performance C functions callable from lisp scripts."
---

# VESC Native C Extensions

Write, compile, and load native C extensions that add high-performance functions callable from lispBM scripts on VESC.

## Overview

Native extensions are C functions compiled to ARM thumb binaries. They run on the VESC's STM32 MCU and can access the full VESC C interface (motor control, CAN, GPIO, IMU, etc.). Extensions are compiled to `.bin`, converted to a lisp byte array by `conv.py`, uploaded to VESC, and loaded with `load-native-lib`.

## Project Structure

```
my_extension/
├── Makefile          # Build configuration
├── code.c            # Extension source code
└── conf/             # (optional) Config XML/datatypes for custom VESC-Tool configs
```

### Minimal Makefile
```makefile
TARGET = my_extension

SOURCES = code.c

VESC_C_LIB_PATH = /path/to/lispBM/c_libs
include $(VESC_C_LIB_PATH)rules.mk
```

### Minimal code.c
```c
#include "vesc_c_if.h"

HEADER

static lbm_value ext_double(lbm_value *args, lbm_uint argn) {
    if (argn != 1 || !VESC_IF->lbm_is_number(args[0])) {
        return VESC_IF->lbm_enc_sym_eerror;
    }
    return VESC_IF->lbm_enc_i(VESC_IF->lbm_dec_as_i32(args[0]) * 2);
}

INIT_FUN(lib_info *info) {
    INIT_START
    (void)info;
    VESC_IF->lbm_add_extension("ext-double", ext_double);
    return true;
}
```

## Required Boilerplate

Every extension file must have:

1. **`#include "vesc_c_if.h"`** — The interface header
2. **`HEADER`** — Macro that declares the program pointer (must be at file scope)
3. **`INIT_FUN(lib_info *info)`** — Init function called when library is loaded
4. **`INIT_START`** — Macro at the start of init function

### Load the image with `(import ...)`, not an array literal

The image file goes into the script's **import table**, not into a lisp array:

```lisp
(import "tail.bin" 'tail)   ; uploaded file is packed beside the script
(load-native-lib tail)
```

How it works: `CodeLoader::lispPackImports` (`vesc_tool/codeloader.cpp`)
appends the file bytes and a name/offset/length table to the script; at boot
`lispif.c`'s import-walking loop (grep `lbm_share_array_const` in `lispif.c`) calls
`lbm_share_array_const(&val, code_data + offset, len)`
(`lispBM/src/lbm_c_interop.c`), which writes only an 8-byte array header into
the const heap and points its data at the **script-flash** bytes. The array is
then a normal const array for `load-native-lib`, and the extension executes
from flash in place. The LBM pool sees no image bytes at all, so the load
ceiling becomes the 128 KiB script region instead of ~20.7 KB.

Shipped packages already do this: `vesc_pkg/balance/balance.lisp` and
`vesc_pkg/tnt/tnt.lisp` open with exactly these two lines.

Two conditions:

- **The upload must pack imports.** `vesc_tool --uploadLisp`, the
  vesc-tool-harness `:upload` (both call `lispUploadFromPath`) and package
  installs do; streaming the text with `lispWriteCode` does not, and the tag
  stays unbound.
- **The file must exist next to the script at pack time** (`import "tail.bin"`
  resolves relative to the script's directory).

The rest of this section is the array-literal path, kept because it explains
where the old ~20.7 KB number came from and why a literal must never be used
for an image.

Image format caveat: firmware 7.00 ships lispBM **0.36.0** (6.06 shipped 0.33.1).
0.35.0 changed how const-heap indices are computed and 0.34.0 fixed
`next_symbol_id` recreation on image load, so an image saved by a 6.06 device
(`image-save` output) is **not** guaranteed to load on 7.00. Rebuild/re-save
images on the 7.00 device; treat the image format as volatile per lispBM
version (`ref/firmware-volatile-values.md`).

### A const-heap image still needs one contiguous pool block at load

Not a pool fraction, and not arbitrary: it is `0.9 x longest_free`, and
`longest_free` already excludes the 10 % reserve. The chain, measured on a
VESC 6 MK6 (`memory_array` = `LBM_MEMORY_SIZE_64BYTES_TIMES_X(448)` = 7,168
words = 28,672 B):

| step | source | bytes |
|---|---|---|
| pool | `memory_array[]` sized by `LISP_MEM_SIZE` in `lispif.c` | 28,672 |
| VM's own state after an upload, before the script runs (`:info` during a `(sleep 8)` at the top: 0 arrays, 4 cons cells) | measured | −2,800 |
| 10 % reserve, `memory_reserve_level = 0.1 x words` (`lbm_memory.c`, `lbm_memory_set_reserve_percent`) | computed | −2,864 |
| **longest free run** (`:info` prints 23,008; `lbm_memory_longest_free()` subtracts the reserve) | measured | 23,008 |
| reader's scratch, `initial_size = 0.9 x longest_free`, words x `sizeof(lbm_uint)` (`eval_cps.c`, `cont_read_start_bytearray`) | computed | **20,707** |

So the largest image that can be written as a `[...]` literal is 20,707 B
(one byte less by the `ix >= size - 1` check). Measured: 20,700 boots, 21,000
fails. Three consequences worth knowing:

- **The cap moves with the pool state.** `cont_read_start_bytearray` sizes the
  array once, up front, and *never grows it*; `cont_read_append_bytearray`
  raises `ENC_SYM_MERROR` when the literal outgrows that guess, which surfaces
  as `out_of_memory` + `Mem longest free: N` + `Starting at row: 1` - it looks
  like a parser bug, not a size limit. With the runtime running, longest free
  falls to 18,588, so the same image cannot be reloaded by re-running the
  script (`:reset`); only an upload boots it.
- **A failed parse leaks the scratch.** The error longjmps past the free, so
  the next attempt in the same session sees ~500 B of longest free and nothing
  boots. Recover with another upload, never with a reset.
- **The move to flash does not free the RAM copy.** Right after
  `(load-native-lib img)` the pool still holds the array (`Allocated arrays: 1`,
  free 6,644 with a 20,424 B image; the const heap also holds it). The next GC
  reclaims it - with the runtime running, free returns to 21,456. So the image
  costs nothing at steady state but needs the full contiguous block at boot.

### Two hard limits that decide the extension's shape

**1. Extension names are the scarcest resource.** The loader's table is
`EXTENSION_STORAGE_SIZE` = **322** entries in 7.00 (`lispif.c`, the `#define`
block next to `HEAP_SIZE`) and the firmware registers **244** names in 7.00
(229 in 6.06). Count them with
`grep -c 'lbm_add_extension(' ../lispif_vesc_extensions.c`. The ~78 free
slots look roomy, but every native lib and every re-load across boots spends
them, and both numbers are **volatile** — re-check them on every firmware
update (`ref/firmware-volatile-values.md`). Overrunning it fails *silently*
at registration, and then any *read* of an unregistered `ext-` symbol raises
`fatal_error` from the reader — it tries to auto-register a stub via
`lbm_add_extension(ext_name, lbm_extensions_default)` in `eval_cps.c`'s
extension-symbol path and gives up when the lookup fails, so the failure
looks like a crash rather than an unbound symbol. Symptom: some `ext-` names
work, later ones report `fatal_error` with `Current: ~CHANNEL~` and
`Starting at row: 1`, and even a never-seen name like `(ext-zzz)` does the
same. Keep the surface small; put REPL diagnostics behind one selector
argument instead of one name each.

**2. A flash-resident image (const heap) cannot have writable statics.** If the
image is loaded inside `@const-start`, it runs from flash read-only: a C store
gives `fatal_error` and lisp refuses the array (`type_error`). The one
writable cell such an image can reach is the loader's per-image `arg` slot:

```c
/* vesc_c_if.h, the ARG macro near the end: *VESC_IF->get_arg(PROG_ADDR) */
#define ARG  (*VESC_IF->get_arg(PROG_ADDR))
```

It is a `void *` in firmware RAM (`lispif_c_lib.c:lib_get_arg`, keyed by the
image base the loader stored in `base_addr`), readable *and writable* from
flash code, and it is what `stop_fun(arg)` receives. Use it to publish a
heap-allocated state pointer so context-less callbacks can find it:

```c
/* Do NOT use HEADER for this: its prog_ptr is non-static, so under -fpic
   &prog_ptr comes from the GOT, and this static link has no relocations -
   the GOT entry is the link-time address 0, which never matches base_addr. */
static volatile int prog_ptr __attribute__((__section__(".program_ptr")));

static state_t *state(void) {
  void **slot = VESC_IF->get_arg((uint32_t)&prog_ptr);
  return (slot && *slot) ? (state_t *)*slot : NULL;
}
```

Allocate the state in an `(ext-...-open)` call with `VESC_IF->malloc`, publish
it in the slot, and free it from `info->stop_fun`. Verify a flash build with
`arm-none-eabi-size`: **bss must be 0**; `data` may be only the 4-byte
`.program_ptr` and constants.

## Extension Function Signature

```c
static lbm_value my_ext(lbm_value *args, lbm_uint argn)
```

- `args` — Array of lisp values (encoded)
- `argn` — Number of arguments
- Returns an encoded lisp value or `VESC_IF->lbm_enc_sym_eerror` on error

## Naming Convention

All extensions **must** start with `ext-` prefix. The `lbm_add_extension` function enforces this and will reject names that don't start with `ext-`.

## Accessing the Interface

All VESC functions are accessed through the `VESC_IF` macro, which is a pointer to the `vesc_c_if` struct at a fixed memory address (`0x1000F800`). See `native-extensions/vesc_c_if_*.md` for detailed documentation of each function category.

## Lifecycle

### Loading
```lisp
(import "my-lib.bin" 'my-lib)  ; packed into the script's import table
(load-native-lib my-lib)       ; calls INIT_FUN, returns t on success
```

### Unloading
```lisp
(unload-native-lib my-lib)     ; calls stop_fun if registered, frees resources
```

### Stop Function (optional)
```c
static void stop(void *arg) {
    my_data *d = (my_data*)arg;
    // cleanup: free threads, memory, etc.
    VESC_IF->free(d);
}

INIT_FUN(lib_info *info) {
    INIT_START
    my_data *d = VESC_IF->malloc(sizeof(my_data));
    info->stop_fun = stop;
    info->arg = d;
    return true;
}
```

## State Management

Use `ARG` macro to store/retrieve persistent state:
```c
INIT_FUN(lib_info *info) {
    INIT_START
    my_data *d = VESC_IF->malloc(sizeof(my_data));
    info->arg = d;    // Store
    // ...
}

static lbm_value ext_something(lbm_value *args, lbm_uint argn) {
    my_data *d = (my_data*)ARG;  // Retrieve
    // ...
}
```

## Threading

```c
static void my_thread(void *arg) {
    while (!VESC_IF->should_terminate()) {
        // do work
        VESC_IF->sleep_ms(100);
    }
}

INIT_FUN(lib_info *info) {
    INIT_START
    lib_thread t = VESC_IF->spawn(my_thread, 1024, "MyThd", NULL);
    // ...
}
```

## Build Process

```bash
cd my_extension
make
# Produces: my_extension.bin and my_extension.lisp
# Upload my_extension.lisp content to VESC via VESC-Tool
```

The build chain: `code.c` → `.so` (ARM object) → `.elf` → `.bin` → `conv.py` → `.lisp` (byte array)

### Compiler Flags (from rules.mk)
- `-fpic -Os -Wall -Wextra -std=gnu99`
- `-DIS_VESC_LIB` — Defines the VESC library context
- `-mcpu=cortex-m4 -mthumb -mfloat-abi=hard -mfpu=fpv4-sp-d16`

### Linker Script
Uses `link.ld` which places `.program_ptr` and `.init_fun` sections at the start of the binary.

## Error Handling

Return `VESC_IF->lbm_enc_sym_eerror` for errors. Optionally set error reason:
```c
VESC_IF->lbm_set_error_reason("Invalid argument");
return VESC_IF->lbm_enc_sym_eerror;
```

## Available Symbol Constants

- `VESC_IF->lbm_enc_sym_nil` — nil
- `VESC_IF->lbm_enc_sym_true` — t
- `VESC_IF->lbm_enc_sym_terror` — type error
- `VESC_IF->lbm_enc_sym_eerror` — eval error
- `VESC_IF->lbm_enc_sym_merror` — memory error

## Examples

See `c_libs/examples/` in the lispBM repo:
- `extension/` — Minimal extension (multiply by 3)
- `thread/` — Extension with background thread
- `speed_test/` — C vs lisp performance comparison
- `ssd1306/` — SSD1306 OLED display driver
- `ws2812/` — WS2812 LED strip driver with DMA
- `config/` — Custom VESC-Tool config panel
- `custom_data_comm/` — Custom data communication with VESC-Tool

## Utility Libraries

Available in `c_libs/utils/`:
- `utils.h/c` — Math utilities, angle normalization, low-pass filters, CRC, FFT
- `rb.h/c` — Thread-safe ring buffer implementation

## House Conventions from Shipped Packages

`native-extensions/vesc-pkg-conventions.md` surveys a `vesc_pkg` checkout (build and
packaging, the `INIT_FUN`/`info->arg`/`stop_fun` contract, config pages via
`conf_custom_add_config`, `plot_*` and `send_app_data` telemetry, CAN EID
layout and `can-send-sid`/`event-can-eid`, and the measured extension-name
budget: shipped libs register 1-5 names). Read it before designing a new
extension's surface, and before inventing a convention this platform already
has.

If you are generating a settings page, start from `conf-template/` and its
rename checklist instead of assembling the scaffolding by hand; its
README's sanity list covers the three ways this goes wrong silently
(`hw_name` missing segfaults VESC Tool ≤7.00 on connect, the tool caches
the served XML by hardware CRC, and the blob must stay `const` for a
flash-resident image). VescTail shipped without `hw_name` once and crashed
the user's tool on every connect.
