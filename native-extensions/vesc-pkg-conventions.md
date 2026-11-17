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

### Generating the settings page (`--xmlConfToCode`), learned the hard way

`vesc_tool --xmlConfToCode conf/settings.xml` reads only the XML; it does
**not** read your `datatypes.h`, and it emits
`confparser.{c,h}`, `confxml.{c,h}` and `conf_default.h` next to the XML.
What it needs, and what silently produces an empty config if missing:

1. **A hand-written `conf/datatypes.h`** with `typedef struct {...} TailConfig;`
   next to the XML. The generated parser `#include "datatypes.h"` and uses
   the struct type named by `<config_name>`; it also wants a `buffer.h` with
   `buffer_append_{uint32,int16,float16}` / `buffer_get_*` (big-endian) and a
   `conf_general.h` (the generated `.c` includes both).
2. `<config_name>` with `<type>3</type>` (QSTRING) and
   `<valString>TailConfig</valString>`. Any other type silently falls back to
   a struct called `device_config`.
3. **`<SerOrder>`**, a sibling of `<Params>`, listing every serialized field
   as `<ser>name</ser>`. Without it the parser has an empty field list:
   `SERIALIZED_CONFIG_LENGTH` comes out as 4 (the signature only) and
   nothing is generated for the page. A name in `<SerOrder>` that is absent
   from `<Params>` prints `"name" not found`.
4. Type codes: `1` double, `2` int, `3` QString, `4` enum, `5` bool,
   `6` bitfield (`CFG_T` in the tool's `datatypes.h`). `vTx` codes:
   `1` uint8, `2` int8, `3` uint16, `4` int16, `5` uint32, `6` int32,
   `7` double16, `8` double32, `9` double32_auto. A double without a
   double16/32 `vTx` prints `Serialization type not supported`.
5. **Doubles are 16-bit fixed point**: `(int16_t)(value * vTxDoubleScale)`.
   So `|value| * scale <= 32767` for the whole UI range, and the scale is
   both the precision and the range budget. Pick per parameter; a range
   spanning five decades cannot survive, so narrow the UI range and keep
   the wider C clamp in code. Saturation in your own `buffer_append_float16`
   keeps an out-of-range value from wrapping to the wrong sign.
6. Defaults are printed with 6 significant digits, so the generated
   `confparser_set_defaults_*` can differ from a C literal in the 6th digit.
   A unit test comparing XML defaults against C defaults needs ~2e-5
   relative tolerance, which still catches real drift.
7. `get_cfg_xml` returns the blob as `data_tailconfig_ + PROG_ADDR` — the
   address in the image is link-time (0-relative). Keep the array `const`
   (patch the generated `.c`, or it lands in `.data`, which a flash image
   must not have) and prove the pointer on hardware by checksumming
   `len` bytes at it against the ELF.
8. The callbacks must be in flash or RAM: the firmware validates them with
   `utils_is_func_valid` (0x08000000..+1MB flash, 0x20000000..+128KB RAM,
   0x10000000..+64KB CCM). Registration is silent when it fails, and
   `COMM_GET_CUSTOM_CONFIG` (93) then never answers.

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
