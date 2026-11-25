# Bundled firmware references

These files are copied from a VESC firmware checkout so the skill works without
one. `gen_ref.py` refreshes them; the Markdown copy also gets a provenance
header.

| File | Source in `vedderb/bldc` |
|---|---|
| `vesc-lispbm-extensions.md` | `lispBM/README.md` |
| `lispif_vesc_extensions.c` | `lispBM/lispif_vesc_extensions.c` |
| `lispif.c` | `lispBM/lispif.c` |
| `lispif_c_lib.c` | `lispBM/lispif_c_lib.c` |
| `lbm_dyn_lib.c` | `lispBM/lispBM/src/extensions/lbm_dyn_lib.c` |

The internal links in `vesc-lispbm-extensions.md` assume the original
`lispBM/` layout. The language documents they point at are bundled in
`../doc/`.

All files are GPL-3.0. Copyright remains with their original authors; the
copyright headers in the C sources are intact.
