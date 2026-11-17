# House conventions, surveyed from `~/dev/vesc_pkg`

What shipped VESC packages do, compared against a from-scratch native
extension. Sources: `c_libs/` (the shared build system), `c_libs/examples/`
(the canonical skeletons), `lib_ws2812`, `lib_nau7802`, `crsf`, `balance`,
`refloat`, `vdisp`, `vbms32`, `fishtail`.

Use this to avoid re-deriving, and to know which departures are deliberate.

## 1. Build and packaging

A package is a directory with a `Makefile` that drives `vesc_tool`:

```make
# <pkg>/Makefile
all: my.vescpkg
my.vescpkg: mylib
	$(VESC_TOOL) --buildPkg "my.vescpkg:my.lisp::0:README.md:My Thing"
mylib:
	$(MAKE) -C $@
# <pkg>/mylib/Makefile
TARGET = my
SOURCES = code.c
USE_STLIB = yes
VESC_C_LIB_PATH = ../../c_libs/
include $(VESC_C_LIB_PATH)rules.mk
```

- `--buildPkg "out:lisp:qml:qmlFullscreen:readme:Name"`, or
  `--buildPkgFromDesc pkgdesc.qml` when the package needs a compatibility
  function (`isCompatible(fwRxParams)` checks `hw`, `fwName`, `hwTypeStr`).
- A directory named `lib_*` is a **library**: VESC Tool lists it without an
  install button, and other scripts import it.
- `rules.mk` produces `.elf`, `.list`, `.bin`, and `.lisp` (the byte array from
  `conv.py`). Flags: `-fpic -Os -std=gnu99 -fsingle-precision-constant
  -mfloat-abi=hard -mfpu=fpv4-sp-d16 -mcpu=cortex-m4 -Wl,--gc-sections
  --undefined=init`. `--undefined=init` is what keeps the entry point alive.
- Version stamping is done by `sed` from a `version` file into the README and
  `ui.qml.in` (refloat, tnt).
- Cross-package import: `(import "pkg@://vesc_packages/lib_x/x.vescpkg" 'x)`.
  A library's own wrapper script contains only
  `(import "x/x.bin" 'x)`, and the consumer adds `(load-native-lib x)`.

## 2. The extension contract

Every shipped lib follows this shape (`c_libs/examples/extension/code.c`,
`crsf/native/code.c`, `refloat/src/main.c`):

```c
#include "vesc_c_if.h"
HEADER                                    // image base marker at offset 0

INIT_FUN(lib_info *info) {                // -> bool __attribute__((section(".init_fun"))) init
  INIT_START
  Data *d = VESC_IF->malloc(sizeof(Data));
  if (!d) return false;                   // init failure is a false return
  data_init(d);
  info->stop_fun = stop;
  info->arg = d;                          // publish the state pointer
  VESC_IF->can_set_eid_cb(cb);            // any global hook is set here
  return true;
}
```

- `info->arg` **is** the per-image argument slot that `ARG` dereferences
  (`vesc_c_if.h`: `#define ARG (*VESC_IF->get_arg(PROG_ADDR))`). Writing
  `info->arg` and writing `ARG` are the same store. Context-less callbacks
  (CAN, IMU, app data) read it back with `ARG`.
- `stop(arg)` receives that pointer. It must undo every global registration
  before it frees: `can_set_eid_cb(0)`, `imu_set_read_callback(NULL)`,
  `set_app_data_handler(NULL)`, `conf_custom_clear_configs()`,
  `request_terminate(thread)`, then `VESC_IF->free`.
- `unload-native-lib` finds the lib by `base_addr == array->data` and calls
  `stop_fun(arg)`. `load-native-lib` refuses a second load of the same array
  ("Library already loaded"). Both work unchanged for a **const-heap array**,
  which is why `@const-start (def img [...]) @const-end` +
  `(load-native-lib img)` is a legitimate flash-resident image: it is still an
  array, and its `data` is stable in flash.
- Lazy-init variant (`lib_ws2812`, `crsf`): `info->arg = 0` in `INIT_FUN`,
  allocate on the first `ext-...-init` call, guard with `if (ARG)`, then
  `ARG = cfg`. Right choice when init needs lisp-side parameters.
- Threads: `VESC_IF->spawn(fn, stack_bytes, "Name", arg)`; the loop condition
  is `!VESC_IF->should_terminate()`; `stop` calls `request_terminate`.
  `thread_set_priority(-5..5)` exists from fw 6.06.
- **One translation unit per lib** is the norm. `HEADER`'s `prog_ptr` is
  `static` (upstream), and `.program_ptr` must stay a single 4-byte slot at
  offset 0 because `PROG_ADDR = &prog_ptr` is compared against `base_addr`.
  refloat is multi-TU but relies on `-flto` merging the copies. Without LTO,
  a second TU shifts `.init_fun` and breaks `PROG_ADDR` for every TU but the
  first.

## 3. Config, telemetry and logging (the parts most extensions forget)

- **Config page for VESC Tool**: `conf_custom_add_config(get_cfg, set_cfg,
  get_cfg_xml)` with a struct generated from `settings.xml` by
  `vesc_tool --xmlConfToCode` (`c_libs/examples/config/code.c`,
  `refloat/src/conf/settings.xml`). Persist with `store_eeprom_var` /
  `read_eeprom_var` behind a signature word, and read it back in `INIT_FUN`.
  The XML blob is addressed as `data_my_config_ + PROG_ADDR`, because the
  image is linked at 0.
- **Any absolute address baked into data needs `+ PROG_ADDR`** in an image
  linked at 0. Pointer tables (`const char *names[]`, function-pointer
  arrays) are therefore traps in this link model; string literals loaded
  PC-relatively are not.
- **Real-time plots**: `plot_init(name_x, name_y)`, `plot_add_graph(name)`,
  `plot_set_graph(n)`, `plot_send_points(x, y)` from C; `(plot-init ...)`,
  `(plot-add-graph ...)`, `(plot-set-graph ...)` from lisp. Cheapest way to see
  internal signals in VESC Tool.
- **Firmware settings from C**: `get_cfg_float/int`, `set_cfg_float/int`,
  `store_cfg` (`CFG_PARAM`), the C counterpart of lisp `(conf-get ...)`.
- **App data channel**: `send_app_data(buf, len)` / `set_app_data_handler(fn)`
  carries custom byte frames over USB/COMM to VESC Tool; the lisp side sees
  `event-data-rx`. Independent of CAN.
- **Logging**: `VESC_IF->printf` with `PACKAGE_NAME`, version and git hash on
  init and on stop (refloat). No `%f` in the evaluator thread; a lib thread
  has a bigger stack, but the printf path is still the firmware's.

## 4. CAN house style

- Receive in lisp: `(event-enable 'event-can-eid)` and a thread doing
  `(loopwhile t (recv (event-can-eid (? id) . (? data)) (proc-eid id data)))`.
  The `data` buffer is malloc'd for the handler and **must be `free`d**.
- Standard EID layout, matching the firmware's own `comm_can.c`:
  node id in bits 0-7, packet id in bits 8-15.
  `(bits-dec-int id 0 8)` / `(bits-dec-int id 8 8)`, transmit
  `(bitwise-or (shl cmd 8) node)` (`fishtail/tail.lisp:20-47`).
- Transmit from lisp: `(can-send-sid id data)` is the common call
  (18 uses across the packages, versus 1 for `can-send-eid`).
- Peer liveness primitives: `can-msg-age`, `can-list-devs`, `can-scan`,
  `can-ping`. A consumer checks age rather than trusting a heartbeat field.
- Safety is the sender's job: a periodic sender means "no traffic" is a fault;
  a receiver that acts on the last command forever is a bug.

## 5. Where this project (VescTail) stands

Matches the house style already: single all-flash image inside
`@const-start` + `(load-native-lib)`, state malloc'd and published in the arg
slot, `stop_fun` teardown, `spawn`/`should_terminate`/`request_terminate`,
C-side CAN RX with node filtering, lisp-side opt-in TX, unit-tested control
math.

Deliberate departures, and why:

| Departure | Why |
|---|---|
| EID: node in bits 16-23, op nibble in bits 4-11, extended ids | Private space for a two-frame protocol with a 4-bit argument; the only peer is our own H7, not VESC Tool. Do not reuse the house layout for a *new* protocol without saying so in the header. |
| No `conf_custom_add_config` | Params are driven by the host controller over CAN. Adding the settings page is the natural next step if a human tunes the tail from VESC Tool. |
| No `plot_*` | Bench telemetry goes over CAN frames the H7 logs. `plot_*` is the cheaper option for solo bench work. |
| Not packaged as `.vescpkg` | Deployment is our own upload script; a package would add an install/update path and a QML page. |
| `ext-...-open`/`-close` instead of only `INIT_FUN` + `unload-native-lib` | Init needs the lisp runtime ready and a handle to pass around; the name cost is two of the ~15 available. |

## 6. Extension-name budget, measured

Measured `lbm_add_extension` counts in shipped libs: `crsf` 5, `lib_ws2812` 3,
`tnt` 2, `refloat` 2 (`ext-dbg`, `ext-set-fw-version`), `balance` 1
(`ext-balance-dbg`). The ecosystem keeps the lisp surface to **1-5 names** and
puts everything else behind a single debug selector, a settings page, or the C
side. A 15-name surface is an outlier; treat it as spending the scarcest
resource the platform has. Firmware 6.06 registers ~229 names itself;
`EXTENSION_STORAGE_SIZE` is 311. Overrunning is silent at registration and
fatal at first read - see the two hard limits in `SKILL.md`.
