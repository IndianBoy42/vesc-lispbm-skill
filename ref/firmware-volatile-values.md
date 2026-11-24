# Firmware-volatile values: recheck on every firmware update

These numbers and surfaces **change between firmware versions**. Everything else in this
skill is structural and survives an update; the items below do not. After pulling a new
firmware tag, walk this table before trusting any doc that quotes them. Update the
quoting doc in the same pass.

Values last verified against **release_7_00** (2026-11; lispBM core 0.36.0).
| value | 6.06 | 7.00 | where to recheck | quoted by |
|---|---|---|---|---|
| `EXTENSION_STORAGE_SIZE` | 311 (heap 22088 B = 2761 cells) | 322 (heap 22000 B = 2750 cells) | `lispBM/lispif.c`, `#define` block next to `HEAP_SIZE` | `native-extensions/SKILL.md` (hard limits), `ref/performance-and-memory.md` §1, `ref/vesc-esc-extensions.md` (cost) |
| Registered lisp extension names | 229 | 244 | `grep -c 'lbm_add_extension(' lispBM/lispif_vesc_extensions.c` (subtract commented-out lines) | `native-extensions/SKILL.md` headroom, table of new names below |
| New lisp extensions | — | `get-duty-abs` `get-id-target` `get-iq-target` `get-temp-mot-res` `encoder-index-found` `encoder-abi-state` `enc-sample` `conf-remap-as504x` `conf-remap-hall` `shutdown` `shutdown-btn-read` `override-led` `prof-trig` `prof-result` (paired lisp registration of `foc_set_fw_override` is commented out upstream) | same grep, diff against previous tag | `ref/vesc-esc-extensions.md` group table |
| C interface vtable | ends at `shutdown_disable` | + `foc_set_fw_override` | tail of `vesc_c_if` in `lispBM/c_libs/vesc_c_if.h` | `native-extensions/vesc_c_if_api.md` — **regenerate**: `python3 gen_vesc_c_if_docs.py --header <tree>/lispBM/c_libs/vesc_c_if.h --out native-extensions` |
| lispBM core version | 0.33.1 | 0.36.0 | `lispBM/lispBM/include/lbm_version.h` | image-format caveat in `native-extensions/SKILL.md`; image compatibility follows the core changelog (`CHANGELOG` in the lispBM subtree) |
| `HEAP_SIZE` cells | 2761 stock (2753 on the local build the measurements used) | 2750 | `lispBM/lispif.c`, `HEAP_SIZE` | `ref/performance-and-memory.md` §1 table, GC-cliff section, `ref/vesc-esc-extensions.md` |
| Measured pool ceilings (20,707 B array literal; 23,008 B longest free) | measured | same figures — but they follow `memory_reserve_level` and pool state, re-measure if `LISP_MEM_SIZE` changes | `:info` on the bench | `native-extensions/SKILL.md` pool-block section |
| New conf symbols in `conf-get`/`conf-set` | — | many new symbol names (e.g. the `vr-*` CANDADLE block, `foc-fw-*`, `adc-v*`, extra `pin-hall*`) | `grep lbm_add_symbol_const lispBM/lispif_vesc_extensions.c`, diff against previous tag | any doc enumerating config field names |
| appconf hw-clamping on lisp `conf-set` | motor conf only | motor + app conf | `ext_conf_set` in `lispBM/lispif_vesc_extensions.c`, look for `commands_apply_appconf_hw_limits` | `ref/vesc-esc-extensions.md` conf-set note |
| Upload erase/ack flow constants | 8 s erase / 4 s chunk | same | `COMM_LISP_ERASE_CODE` handler in `comm/commands.c`, `COMM_LISP_STREAM_CODE` in `lispBM/lispif.c`, `vesc_tool/codeloader.cpp` timeouts | `ref/performance-and-memory.md` upload section, `SKILL.md`, `vesc-tool-harness/SKILL.md` |

How to recheck, in order:

1. `grep -n 'EXTENSION_STORAGE_SIZE\|HEAP_SIZE\|LISP_MEM_SIZE' lispBM/lispif.c`
2. `grep -c 'lbm_add_extension(' lispBM/lispif_vesc_extensions.c`
3. `grep -n 'LBM_MINOR_VERSION\|LBM_PATCH_VERSION' lispBM/lispBM/include/lbm_version.h`
4. `tail -30 lispBM/c_libs/vesc_c_if.h` (new vtable tail entries)
5. Regenerate `native-extensions/vesc_c_if_api.md` (the `gen_vesc_c_if_docs.py` dict holds the curated descriptions; add entries for any new vtable members).
6. Bench-verify the pool ceilings once per hardware/battery of record.

Line anchors in this skill intentionally name files plus a function, macro or message
constant instead of a line number: they survive reformatting. When an anchor text stops
matching, that is a signal the code changed, not just its position.
