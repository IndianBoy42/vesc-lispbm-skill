# Custom config page template (correct by construction)

Copy this directory's `conf/` into your extension (typically `<pkg>/conf/`),
rename the template symbols, regenerate, and wire the callbacks. The
generated files are committed so a build never needs vesc_tool.

## Rename checklist

1. `conf/settings.xml`: `<valString>` (becomes the struct name and every
   generated symbol), `hw_name`'s `<longName>` (the page name VESC Tool
   shows), param names, `<cDefine>` prefixes.
2. `conf/datatypes.h`: the typedef and its fields — field names and order
   must equal `<SerOrder>`; field types follow the wire mapping documented
   in the file header.
3. `conf/conf_general.h`: `PACKAGE_NAME`, `PACKAGE_VERSION` (bump the
   version when the parameter set or wire layout changes: it folds into the
   generated signature and rejects stale EEPROM blobs).
4. `wiring.c`: the EEPROM callbacks, the cfg callbacks and the registration
   call; rename `template_*`/`TEMPLATECONFIG_*`/`data_templateconfig_` and
   provide `my_apply_params` (clamp-and-adopt) plus `my_state()`.

## Generate and build

```sh
make conf   # vesc_tool --xmlConfToCode conf/settings.xml + const patch
```

with these Makefile pieces:

```make
SOURCES += conf/confparser.c conf/confxml.c conf/buffer.c
USE_OPT += -Iconf -fvisibility=hidden
conf:
	vesc_tool --xmlConfToCode conf/settings.xml
	# The XML blob is read-only data in a flash-resident image: without
	# const it lands in .data, which this image must not have.
	sed -i 's|^__attribute__((used)) uint8_t data_|__attribute__((used)) const uint8_t data_|' conf/confxml.c
	sed -i 's|^extern uint8_t data_|extern const uint8_t data_|' conf/confxml.h
```

This template was verified by generating from its own XML, compiling the
generated parser with `conf/buffer.c` on the host, and round-tripping:
defaults, every UI-range extreme, and a corrupted-signature reject
(2026-11-18, vesc_tool 7.00 generator).

Commit the generated files. `make clean` must not delete them.

## Sanity checks after any XML edit

1. `hw_name` exists (VESC Tool ≤7.00 segfaults without it — see
   `../vesc-pkg-conventions.md`).
2. The XML blob grew or shrank: re-check the image size against the
   `0.9 x longest-free` load cap in `../SKILL.md`.
3. The wire layout changed (any `<SerOrder>`, type or scale edit): bump
   `PACKAGE_VERSION` and clear the tool's cache once,
   `~/.local/share/VESC/VESC Tool/hw_cache/<hwConfCrc>/conf_custom_N.bin`,
   or the tool keeps serving the old page.
4. A host test compares XML defaults against C defaults and round-trips
   serialize/deserialize; the generator prints 6 significant digits, so
   compare with ~2e-5 relative tolerance.

