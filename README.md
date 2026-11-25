# vesc-lispbm-skill

Agent Skills for writing, testing, and debugging lispBM scripts, device QML, and
native C extensions on VESC motor controllers.

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

## What the skill needs

The skill is self-contained for reading and writing scripts. `ref/upstream/`
carries a snapshot of the firmware references it cites: the ESC and Express
extension reference, `lispif_vesc_extensions.c`, `lispif.c`, `lispif_c_lib.c`,
and `lbm_dyn_lib.c`. The language chapters are in `ref/doc/`. See
`ref/upstream/PROVENANCE.md` for the source of each file.

Three inputs are not bundled because they are build or test tools. Clone
[`vedderb/bldc`](https://github.com/vedderb/bldc) anywhere and set `VESC_FW` to
that path.

| Input | Used for |
|---|---|
| `$VESC_FW/lispBM/c_libs/` | the native extension SDK: `vesc_c_if.h`, `rules.mk`, `link.ld`, `utils/`, `examples/` |
| `$VESC_FW/lispBM/lispBM/repl/repl` | running lispBM scripts off-target (`ref/testing.md`) |
| `vesc_tool` | previewing or building a QML package, and the TCP harness |

`vesc_express` and `vesc_pkg` checkouts are needed only to regenerate reference
tables, not to use the skill.

## Provenance and license

Licensed under the GNU General Public License v3.0; see `LICENSE`.

The skill is derived from the VESC ecosystem and redistributes material from
these GPL-3.0 projects:

- [`vedderb/bldc`](https://github.com/vedderb/bldc): firmware behavior, the C
  interface, and the bundled sources in `ref/upstream/`.
- [`vedderb/lispBM`](https://github.com/vedderb/lispBM): `ref/doc/` and the
  section files in `ref/` are copied or split from its documentation.
- [`vedderb/vesc_tool`](https://github.com/vedderb/vesc_tool): `qml-ui/ref/`
  tables are generated from its sources.
- [`vedderb/vesc_express`](https://github.com/vedderb/vesc_express):
  `ref/vesc-express-extensions.md` is generated from its sources.
- [`vedderb/vesc_pkg`](https://github.com/vedderb/vesc_pkg): package
  conventions surveyed in `native-extensions/vesc-pkg-conventions.md`.

VESC is a trademark of its respective owner. This project is not affiliated with
or endorsed by the VESC project.
