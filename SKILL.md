---
name: vesc-lispbm
description: "Write lispBM scripts and native C extensions for VESC motor controllers. Use when coding in lispbm for VESC firmware, interfacing with motors/CAN/GPIO/IMU, or building native C extensions."
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

## Architecture

### How It Works
1. **LispBM** is a lisp/scheme-like scripting language for microcontrollers
2. **VESC firmware** embeds LispBM as its scripting engine
3. **VESC-Tool** provides the IDE for writing/uploading scripts
4. **Native extensions** are C functions compiled to ARM thumb binaries, uploaded as byte arrays, and loaded with `load-native-lib`

### Key Paths (in lispBM repo)
- `lispBM/` — LispBM language implementation
- `lispBM/doc/lbmref.md` — Full language reference (9800+ lines)
- `lispBM/doc/runtimeref.md` — Runtime extensions reference
- `lispBM/doc/gotchas.md` — Gotchas and caveats
- `c_libs/` — Native extension SDK
- `c_libs/vesc_c_if.h` — VESC C interface (all available functions)
- `c_libs/rules.mk` — Build system for native extensions
- `c_libs/examples/` — Example extensions
- `lispif_c_lib.c` — Implementation of the C interface on VESC firmware

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

### VESC-Specific LispBM Functions
These are available when running on VESC firmware (not in standalone LispBM):
- Motor control: `get-rpm`, `get-duty`, `set-duty`, `set-current`, etc.
- CAN bus: `can-send`, `can-recv`, `can-set-cid`
- GPIO: `gpio-configure`, `gpio-write`, `gpio-read`
- ADC: `get-adc`
- IMU: `get-imu-rpy`, `get-imu-accel`, `get-imu-gyro`
- Display: `disp-render`, `disp-clear`
- Config: `get-selected-motor`, `set-selected-motor`

## Reference Files

Regenerate from upstream sources:
```bash
# Language reference sections from lbmref.md
python3 gen_ref.py --lispbm-root ~/dev/vesc/lispBM/lispBM

# VESC C interface API docs from vesc_c_if.h
python3 gen_vesc_c_if_docs.py --header ~/dev/vesc/lispBM/c_libs/vesc_c_if.h
```

- `ref/INDEX.md` — Master index of all language sections
- `ref/NN-*.md` — Individual sections from lbmref.md
- `ref/doc/lbmref.md` — Full language reference
- `ref/doc/runtimeref.md` — Runtime extensions
- `ref/doc/gotchas.md` — Gotchas and caveats
- `ref/doc/displayref.md` — Display library
- `ref/doc/dynref.md` — Dynamic loadable functions
- `native-extensions/SKILL.md` — C extension development guide
- `native-extensions/vesc_c_if_api.md` — Auto-generated VESC C interface API reference
