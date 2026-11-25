# Maintaining this repository

The skill is edited in `lispBM/skill` inside a VESC firmware checkout and
exported to this repository with `git subtree`.

## Export

Changes land in `vedderb/bldc` first. From that checkout, split the subtree and
push it. Pass the commit explicitly: in a colocated jj checkout, git's `HEAD`
does not follow the jj working-copy revision (`jj log -r @ --no-graph -T
commit_id`).

```sh
git subtree split --prefix=lispBM/skill <commit> > /tmp/split-sha
git push https://github.com/IndianBoy42/vesc-lispbm-skill.git \
    "$(tail -1 /tmp/split-sha)":refs/heads/main
```

Pull changes made directly in this repository back with:

```sh
git subtree pull --prefix=lispBM/skill \
    https://github.com/IndianBoy42/vesc-lispbm-skill.git main --squash
```

## Regenerating the references

The checked-in `ref/`, `qml-ui/ref/`, and `native-extensions/vesc_c_if_api.md`
files are generated from the firmware, VESC Tool, and VESC Express sources. Point
the scripts at local checkouts:

```sh
VESC_FW=/path/to/bldc
VESC_EXPRESS=/path/to/vesc_express
VESC_TOOL=/path/to/vesc_tool

python3 gen_ref.py --lispbm-root "$VESC_FW/lispBM/lispBM"
python3 gen_vesc_c_if_docs.py --header "$VESC_FW/lispBM/c_libs/vesc_c_if.h"
python3 gen_express_extensions.py --express-root "$VESC_EXPRESS"
python3 qml-ui/gen_qml_refs.py --vesc-tool-root "$VESC_TOOL"
```

`gen_ref.py` also refreshes the bundled copies in `ref/upstream/`. Each script
prints its defaults with `--help`.

After regenerating, re-check the volatile values listed in
`ref/firmware-volatile-values.md`.
