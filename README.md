# vesc-lispbm-skill

Agent Skills for writing, testing, and debugging lispBM scripts, device QML, and
native C extensions on VESC motor controllers.

This is the standalone distribution of the skill kept at `lispBM/skill` in the
[VESC firmware tree](https://github.com/vedderb/bldc). That directory is the
source of truth; this repository is synchronized from it with `git subtree`
(see [Syncing](#syncing)).

## Skills

| Directory | Name | Covers |
|---|---|---|
| `.` | `vesc-lispbm` | lispBM language traps, upload and debugging workflow, memory and timing rules, the ESC extension surface |
| `express-logging/` | `vesc-express-logging` | recording lispBM data to a VESC Express SD card |
| `native-extensions/` | `vesc-native-extensions` | writing, compiling, and loading C extensions |
| `qml-ui/` | `vesc-device-qml` | custom QML GUIs, package format, and deployment |
| `vesc-tool-harness/` | `vesc-tool-harness` | driving a VESC Tool window over TCP from a host script (experimental) |

Every skill is a directory with a `SKILL.md` carrying YAML frontmatter, following
the [Agent Skills](https://agentskills.io) layout.

## Install

Clone the repository, then link each skill into your agent's skills directory.
For omp that directory is `~/.omp/agent/skills`; Claude Code uses
`~/.claude/skills`. A project-local `.claude/skills` or `.omp/skills` works too.

```sh
git clone https://github.com/IndianBoy42/vesc-lispbm-skill.git
cd vesc-lispbm-skill
SKILLS=~/.omp/agent/skills
mkdir -p "$SKILLS"
ln -sfn "$PWD" "$SKILLS/vesc-lispbm"
for d in express-logging native-extensions qml-ui vesc-tool-harness; do
    ln -sfn "$PWD/$d" "$SKILLS/$d"
done
```

The root skill references the sub-skills by relative path, so keep them together
or install the whole tree into one directory.

## Using it from a firmware checkout

Parts of the skill assume it sits at `<bldc>/lispBM/skill`. Paths such as
`../lispif.c`, `../c_libs/vesc_c_if.h`, and `../lispBM/` resolve only in a
checkout. Standalone copies carry the generated references, but version-specific
claims are easiest to check against a clone of
[`vedderb/bldc`](https://github.com/vedderb/bldc). Values that change between
firmware releases are listed in `ref/firmware-volatile-values.md`.

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

Each script also prints its defaults with `--help`.

## Syncing

Changes land in `vedderb/bldc` first. From that checkout, split the subtree and
push it here. Pass the commit explicitly: in a colocated jj checkout, git's
`HEAD` does not follow the jj working-copy revision (`jj log -r @ --no-graph -T
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

## Provenance and license

Licensed under the GNU General Public License v3.0; see `LICENSE`.

The skill is derived from the VESC ecosystem and redistributes material from
these GPL-3.0 projects:

- [`vedderb/bldc`](https://github.com/vedderb/bldc) — firmware behavior, C
  interface, and harness examples.
- [`vedderb/lispBM`](https://github.com/vedderb/lispBM) — `ref/doc/` and the
  section files in `ref/` are copied or split from its documentation.
- [`vedderb/vesc_tool`](https://github.com/vedderb/vesc_tool) — `qml-ui/ref/`
  tables are generated from its sources.
- [`vedderb/vesc_express`](https://github.com/vedderb/vesc_express) —
  `ref/vesc-express-extensions.md` is generated from its sources.
- [`vedderb/vesc_pkg`](https://github.com/vedderb/vesc_pkg) — package
  conventions surveyed in `native-extensions/vesc-pkg-conventions.md`.

VESC is a trademark of its respective owner. This project is not affiliated with
or endorsed by the VESC project.
