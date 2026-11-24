# VESC ESC-side scripting API (what a script on the motor controller can call)

The `ref/` language sections and `ref/doc/lbmref.md` describe **lispBM itself**. They do not
describe a single VESC function. Everything a script running on the ESC *with a motor
attached* can call lives in the firmware's lisp interface, and the authoritative reference
for it is:

- `../README.md` (~8000 lines, in this checkout): every ESC/Express extension, with
  signature, platform support and minimum firmware version. **Read the section for a
  function before using it.**
- `../lispif_vesc_extensions.c`: the ground truth. Every name the firmware registers is a
  `lbm_add_extension("name", ...)` line, and the C body defines the exact argument and
  return types. When the README and a script's expectations disagree, this file decides.
- `../lispif.c`: heap sizing and the `image`/`env` handling for stored scripts.
- `../lispBM/lispBM/doc/runtimeref.md`: the runtime extensions that come from lispBM
  itself (buffers, arrays, strings, plotting primitives, `import`, ...).
- `ref/vesc-express-extensions.md`: the **Express side** of the same surface, generated from
  the vesc_express sources. A name there is not automatically available here, and vice
  versa: check both before claiming a function exists.

Verify a name exists before relying on it (the README and the firmware version on the
bench can disagree):

```sh
grep -n 'lbm_add_extension("get-temp' ../lispif_vesc_extensions.c
```

## The API surface, by group

Details and argument order are in `../README.md`; this is the map.

| Group | Functions |
|---|---|
| Motor state | `get-rpm` `get-rpm-fast` `get-rpm-set` `get-duty` `get-duty-abs` (7.00) `get-current` `get-current-in` `get-current-dir` `get-id` `get-iq` `get-id-target` (7.00) `get-iq-target` (7.00) `get-vd` `get-vq` `get-pos` `get-batt` `get-vin` `get-ah` `get-wh` `get-ah-chg` `get-wh-chg` `get-fault` `get-dist` `get-encoder` |
| Thermal | `get-temp-fet` (arg picks sensor 1..3, 0/omitted = hottest) `get-temp-mot` `get-temp-mot-res` (7.00) `override-temp-motor` |
| Encoder (7.00) | `encoder-index-found` `encoder-abi-state` `enc-sample` |
| Timing | `systime` (**100 us ticks**, 10 kHz on ESC) `secs-since` (seconds, wrap-safe) `sleep` (seconds; 100 us granularity + 200 us poll) — units table: `performance-and-memory.md` section 0. Plus the lispBM
loops `loopfor` `loopwhile` `looprange` `loopforeach` and `loopwhile-thd` |
| Config | `conf-get` `conf-set` `conf-store` `conf-get-limits` `conf-restore-mc` `conf-restore-app` `eeprom-store-f` `eeprom-read-f` `eeprom-store-i` `eeprom-read-i` `conf-remap-as504x` `conf-remap-hall` (both 7.00) |
| CAN | `can-send-sid` `can-send-eid` `can-recv-sid` `can-recv-eid` `can-msg-age` `can-list-devs` `canset-*` `canget-*` `canset-current` ... `canget-temp-motor` |
| IO / board | `gpio-configure` `gpio-write` `gpio-read` `pwm-start` `pwm-stop` `pwm-set-duty` `icu-start` `icu-width` `icu-period` `uart-start` `uart-write` `uart-read` `i2c-start` `i2c-tx-rx` `i2c-restore` `get-adc` `get-adc-decoded` `ioboard-*` `override-led` `shutdown` `shutdown-btn-read` (last three 7.00) |
| IMU | `get-imu-rpy` `get-imu-quat` `get-imu-acc` `get-imu-gyro` `get-imu-mag` `get-imu-acc-derot` `get-imu-gyro-derot` — the ESC reads the IMU the firmware was configured with; it does **not** expose `imu-start-lsm6` / `imu-stop` (those are Express-only) |
| Instrumentation | `print` `puts` `stats` `sysinfo` `send-data` `recv-data` `plot-init` `plot-add-graph` `plot-set-graph` `plot-send-points` `log-config-field` `log-start` `log-send-f32` `log-send-f64` `prof-trig` `prof-result` (both 7.00) |
| Script/firmware | `lbm-write` `lbm-run` `lbm-erase` `image-save` `import` `load-native-lib` `unload-native-lib` `lbm-set-gc-stack-size` `free` |
| Math | `sin` `cos` `atan2` `sqrt` `pow` `log` (base e) `log10` `floor` `ceil` `round` `abs` `deg2rad` `rad2deg` `rand` |
| Strings/buffers | `str-from-n` `str-merge` `str-join` `str-to-i` `str-to-f` `str-split` `bufcreate` `buflen` `bufclear` `bufget-i8/u8/i16/u16/i32/u32/f32` `bufset-*` `bufcpy` |

`get-temp-mot` (local) vs `canget-temp-motor` (over CAN) is not a typo on either side; the
names really are inconsistent, and the same asymmetry exists for `canget-temp-fet`.

`conf-set` on **app** settings is clamped in 7.00: `ext_conf_set` now runs
`commands_apply_appconf_hw_limits` (as it already did for motor conf) before
`app_set_configuration`, so a value the hardware cannot take is silently adjusted
rather than applied raw. 6.06 applied the clamp to motor conf only.

Some names are not C extensions at all but short functions defined in a Lisp prelude that
the runtime loads on demand (`../lispBM/src/extensions/lbm_dyn_lib.c`): `abs`, `filter`,
`foldl`, `foldr`, `iota`, `zip`, `zipwith`, `list-to-array`, `array-to-list`, `second`,
`third`, `create-struct` and its accessors, `str-merge`, `str-cmp-asc`, `str-cmp-dsc`. They
behave like the rest; that file is where to look when one of them surprises you.

## Which platform

Most entries in `../README.md` carry a platform table. `ESC` means the motor controller
(this firmware), `Express` means the esp32 companion. Calling an Express-only name from an
ESC script is an `undefined symbol` or an eval error, and many names are per-firmware
version gated (6.00 / 6.05 / 6.06 / 7.00 — the 7.00 additions are marked above; `vesc_c_if.h` gained
`foc_set_fw_override` but no lisp extension registers it). Check the table for the firmware actually on the bench.

## What a script costs

From `../lispif.c`:

- cons cells (lisp values, closures, lists, boxed floats): `HEAP_SIZE` = 2750 cells
  (~22 KB) on the stock 7.00 build (2761 in 6.06 — it trades 8 B of heap per
  `EXTENSION_STORAGE_SIZE` slot).
- arrays and byte buffers (`bufcreate`, `mkarray`): a separate 28 KB pool
  (`LBM_MEMORY_SIZE_28K`).
- A script's ring buffers, tables and images come out of those two pools, so a script
  that keeps large histories must budget for them. `(stats)` in the VESC Tool terminal
  prints heap use, GC counters and the GC stack high water mark.
- `lbm-set-gc-stack-size` and `lbm-set-quota` exist because a script that allocates per
  iteration can outrun the collector; the usual fix is to not allocate (mutate buffers and
  lists with `bufset-*` / `setix` instead of building new lists each pass).

## Native extensions

Timing-critical work (anything that must run inside the control loop, or that needs more
throughput than the lisp interpreter gives) belongs in C, loaded from the script with
`load-native-lib`. See `native-extensions/SKILL.md` and `native-extensions/vesc_c_if_api.md`
in this skill, and `../c_libs/` for the SDK and examples.
