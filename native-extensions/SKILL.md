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

### A const-heap image still needs one contiguous pool block at load

Loading happens in two steps: the reader builds the byte array in the array
pool, then the `@const-start` block moves it to the const region in flash.
Runtime cost is therefore zero, but the **boot** still needs a contiguous
block as large as the image. Measured on a VESC 6 MK6 (28,672 B pool): a
20,388 B and a 20,614 B image boot; 20,746 B fails with `out_of_memory`,
`Mem longest free: 510`, `Starting at row: 1` (the message names the row, not
the size, so it looks like a parse bug). Budget ~20.3 KB of binary, count the
diagnostic strings against it, and remember the image must still have no
writable statics.

### Two hard limits that decide the extension's shape

**1. Extension names are the scarcest resource.** The loader's table is
`EXTENSION_STORAGE_SIZE` = 311 entries (`lispif.c:40`) and the firmware's own
registrations leave room for roughly **fifteen** more. Overrunning it fails
*silently* at registration, and then any *read* of an unregistered `ext-`
symbol raises `fatal_error` from the reader — it tries to auto-register a stub,
fails, and gives up (`eval_cps.c:4473`), so the failure looks like a crash
rather than an unbound symbol. Symptom: some `ext-` names work, later ones
report `fatal_error` with `Current: ~CHANNEL~` and `Starting at row: 1`, and
even a never-seen name like `(ext-zzz)` does the same. Keep the surface small;
put REPL diagnostics behind one selector argument instead of one name each.

**2. A flash-resident image (const heap) cannot have writable statics.** If the
image is loaded inside `@const-start`, it runs from flash read-only: a C store
gives `fatal_error` and lisp refuses the array (`type_error`). The one
writable cell such an image can reach is the loader's per-image `arg` slot:

```c
/* vesc_c_if.h:699 - *VESC_IF->get_arg(PROG_ADDR) */
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
(def my-lib [0x01 0x02 ...])  ; byte array from conv.py output
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

`native-extensions/vesc-pkg-conventions.md` surveys `~/dev/vesc_pkg` (build and
packaging, the `INIT_FUN`/`info->arg`/`stop_fun` contract, config pages via
`conf_custom_add_config`, `plot_*` and `send_app_data` telemetry, CAN EID
layout and `can-send-sid`/`event-can-eid`, and the measured extension-name
budget: shipped libs register 1-5 names). Read it before designing a new
extension's surface, and before inventing a convention this platform already
has.
