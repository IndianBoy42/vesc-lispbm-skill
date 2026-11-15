#!/usr/bin/env python3
"""
Generate the VESC Express LispBM extension reference from a vesc_express checkout.

Every LispBM function the Express firmware exposes is a `lbm_add_extension("name",
handler)` call in C. This script walks those calls, keeps the author's own grouping
(`//` section comments), and pulls each handler's signature comment
(`// (name arg ...)` above the function) where one exists.

Usage:
    python3 gen_express_extensions.py [--express-root /path/to/vesc_express] [--out DIR]

Defaults:
    --express-root  ~/dev/vesc_express
    --out           <this script's directory>/ref

Output:
    ref/vesc-express-extensions.md

Skipped on purpose: `main/lispBM/` (upstream lispBM, covered by gen_ref.py and shared
with the ESC), stubs, tests, examples and benchmarks. Board-specific files under
`main/hwconf/` are kept and marked, because they add real extensions on those boards.
"""

from __future__ import annotations

import argparse
import re
from collections import OrderedDict
from pathlib import Path

DEFAULT_EXPRESS_ROOT = Path.home() / "dev/vesc_express"
DEFAULT_OUT = Path(__file__).resolve().parent / "ref"

# Anything below these directories is not Express firmware surface.
SKIP_DIRS = {
    "main/lispBM",          # upstream lispBM, shared with the ESC skill
    "main/managed_components",
    "main/build",
}

REG_RE = re.compile(r'lbm_add_extension\(\s*"([^"]+)"\s*,\s*&?\s*([A-Za-z_]\w*)')
CATEGORY_RE = re.compile(r'^\s*//\s*(.+?)\s*$')
IF_RE = re.compile(r'^\s*#\s*(if|ifdef|ifndef|else|elif|endif)\b\s*(.*)$')
FUNC_RE = re.compile(r'^\s*static\s+lbm_value\s+([A-Za-z_]\w*)\s*\(')
SIG_RE = re.compile(r'^\s*(?://|\*)?\s*(\(.+)$')
DOXY_SIG_RE = re.compile(r'^\s*\*?\s*signature\s+(\(.+)$')
# A `//` line is only a section header if it reads like prose, not like code.
CODEISH_RE = re.compile(r'[;=]|\(|\)|->')
# Section comments that are about the C file, not about a group of extensions.
GENERIC_HEADINGS = {"private variables", "private", "globals", "static", "statics",
                    "functions", "includes", "defines", "types", "helpers",
                    "internal", "externals", "variables"}

MODULE_ORDER = ["core", "wifi", "ble", "display", "rgbled", "hwconf"]

MODULE_TITLES = {
    "core": "Core (main/)",
    "wifi": "WiFi / TCP",
    "ble": "BLE",
    "display": "Display",
    "rgbled": "RGB LED",
    "hwconf": "Board-specific (hwconf/)",
}


def module_of(rel: Path) -> str:
    parts = rel.parts
    if len(parts) >= 3 and parts[0] == "main" and (rel.parent != Path("main")):
        return parts[1]
    return "core"


def source_of(rel: Path) -> str:
    return str(rel)


def collect(express_root: Path) -> list[dict]:
    """Return registration records in source order."""
    records: list[dict] = []

    for path in sorted(express_root.glob("main/**/*.c")):
        rel = path.relative_to(express_root)
        key = str(rel)
        if any(key == d or key.startswith(d + "/") for d in SKIP_DIRS):
            continue
        if path.name.endswith("_stubs.c"):
            continue
        if any(seg in rel.parts for seg in ("tests", "examples", "benchmarks")):
            continue

        text = path.read_text(errors="replace")
        lines = text.splitlines()

        # Handler -> signature comment from the line(s) directly above the definition.
        sigs: dict[str, str] = {}
        for i, line in enumerate(lines):
            m = FUNC_RE.match(line)
            if not m:
                continue
            handler = m.group(1)
            for j in range(i - 1, max(-1, i - 16), -1):
                prev = lines[j]
                d = DOXY_SIG_RE.match(prev)
                if d:
                    sigs[handler] = d.group(1).strip()
                    break
                s = SIG_RE.match(prev)
                if s:
                    sigs[handler] = s.group(1).strip()
                    break
                # Stop at anything that looks like code above the function.
                if CODEISH_RE.search(prev) and not prev.lstrip().startswith(("*", "//")):
                    break

        category = ""
        cond_stack: list[str] = []
        for i, line in enumerate(lines):
            cm = CATEGORY_RE.match(line)
            if cm:
                text = cm.group(1).strip()
                # Only prose headers: short, starts with a letter, no code punctuation.
                if (text and text[0].isalpha() and len(text) <= 40
                        and not CODEISH_RE.search(text)
                        and text.lower() not in GENERIC_HEADINGS
                        and not text.lower().startswith(("signature", "@"))):
                    category = text
            im = IF_RE.match(line)
            if im:
                kind, expr = im.group(1), im.group(2).strip()
                if kind in ("if", "ifdef", "ifndef"):
                    cond_stack.append((kind, expr))
                elif kind == "endif" and cond_stack:
                    cond_stack.pop()
                continue
            m = REG_RE.search(line)
            if m:
                name, handler = m.group(1), m.group(2)
                records.append({
                    "name": name,
                    "handler": handler,
                    "sig": sigs.get(handler, ""),
                    "file": source_of(rel),
                    "line": i + 1,
                    "module": module_of(rel),
                    "category": category,
                    "cond": " ".join(e for _, e in cond_stack) if cond_stack else "",
                })

    return records


def render(records: list[dict], express_root: Path) -> str:
    by_module: "OrderedDict[str, list[dict]]" = OrderedDict()
    for mod in MODULE_ORDER:
        recs = [r for r in records if r["module"] == mod]
        if recs:
            by_module[mod] = recs
    for r in records:  # anything unexpected still gets a section
        if r["module"] not in by_module:
            by_module.setdefault(r["module"], []).append(r)

    # A name registered by several files (one per display driver, say) is one
    # function with several providers: merge the rows and list all the sources.
    def merge(recs: list[dict]) -> "OrderedDict[tuple[str, str], dict]":
        merged: "OrderedDict[tuple[str, str], dict]" = OrderedDict()
        for r in recs:
            key = (r["category"], r["name"])
            if key not in merged:
                merged[key] = {"name": r["name"], "sig": r["sig"],
                               "cond": r["cond"], "srcs": []}
            e = merged[key]
            e["srcs"].append(f"{r['file']}:{r['line']}")
            e["sig"] = e["sig"] or r["sig"]
            e["cond"] = e["cond"] or r["cond"]
        return merged

    unique = {r["name"] for r in records}
    with_sig = {r["name"] for r in records if r["sig"]}
    out: list[str] = []
    w = out.append

    w("# VESC Express LispBM extensions (generated)\n")
    w("Every function the **VESC Express** (ESP32) firmware registers for LispBM, extracted by")
    w("`gen_express_extensions.py` from `lbm_add_extension(\"name\", handler)` calls in the")
    w("vesc_express source. Signatures come from the `// (name arg ...)` or `signature (...)`")
    w("comment above each C handler where the firmware author wrote one.\n")
    w(f"Source: `{express_root}`  ")
    w(f"Unique names: **{len(unique)}**, of which **{len(with_sig)}** carry a signature in the")
    w(f"source. {len(records)} registrations across {len(by_module)} modules.\n")
    w("Regenerate after updating the firmware checkout:\n")
    w("```sh")
    w("python3 gen_express_extensions.py --express-root ~/dev/vesc_express")
    w("```\n")
    w("## How to use this file\n")
    w("- This is the **Express-only** surface: display, WiFi/TCP, BLE, NVS, crypto, image and")
    w("  board extensions that do not exist on an ESC. The shared language lives in `ref/`")
    w("  and the ESC-side API in `ref/vesc-esc-extensions.md`; `../README.md` in the bldc")
    w("  checkout is the prose reference for names common to both.")
    w("- A registration here means the name exists **in the firmware version you are reading**,")
    w("  not that it exists on your board: some are behind `#if` guards (shown inline) and")
    w("  some live in one board's `hwconf/` file.")
    w("- An empty Signature column is not an error: that handler has no signature comment in")
    w("  the C source. Read the body for argument order and return values:")
    w("  `grep -n \"<handler>\" <file>`.\n")

    w("## Modules\n")
    w("| Module | Unique names | Registrations | File(s) |")
    w("|---|---|---|---|")
    for mod, recs in by_module.items():
        files = sorted({r["file"] for r in recs})
        title = MODULE_TITLES.get(mod, mod)
        names = len({r["name"] for r in recs})
        w(f"| {title} | {names} | {len(recs)} | {', '.join(f'`{f}`' for f in files)} |")
    w("")

    for mod, recs in by_module.items():
        w(f"## {MODULE_TITLES.get(mod, mod)}\n")
        # Preserve the author's own sections, in source order.
        groups: "OrderedDict[str, list[dict]]" = OrderedDict()
        for r in recs:
            groups.setdefault(r["category"] or "", []).append(r)
        for cat, items in groups.items():
            if cat:
                w(f"### {cat}\n")
            w("| Name | Signature | Source |")
            w("|---|---|---|")
            for e in merge(items).values():
                sig = e["sig"].replace("|", "\\|") if e["sig"] else ""
                srcs = ", ".join(f"`{s}`" for s in e["srcs"])
                name = f"`{e['name']}`"
                if e["cond"]:
                    name += f" *(if {e['cond']})*"
                w(f"| {name} | {sig} | {srcs} |")
            w("")

    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--express-root", type=Path, default=DEFAULT_EXPRESS_ROOT)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    root = args.express_root.expanduser().resolve()
    if not (root / "main").is_dir():
        print(f"not a vesc_express checkout: {root}")
        return 1

    records = collect(root)
    if not records:
        print("no lbm_add_extension() calls found")
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    dest = args.out / "vesc-express-extensions.md"
    dest.write_text(render(records, root))

    names = len({r["name"] for r in records})
    print(f"wrote {dest}: {names} unique names, {len(records)} registrations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
