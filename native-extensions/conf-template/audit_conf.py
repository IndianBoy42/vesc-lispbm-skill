#!/usr/bin/env python3
"""Static check of a VESC custom-config settings.xml against the recorded
rules from vesc-pkg-conventions.md ("Sanity checks after any edit").

Every check here was learned from a real failure on hardware or in the
tool source; the comments name the failure. Run it over a settings.xml
before regenerating the conf/ files:

    python3 audit_conf.py path/to/settings.xml [more.xml ...]

Exit status is non-zero if any finding was reported.
"""
import re
import sys

TX_NAME = {1: "double", 2: "int", 3: "QString", 4: "enum", 5: "bool",
           6: "bitfield"}
# wire capacity of each vTx type the generator emits for ints
TX_CAP = {1: 255, 2: 127, 3: 65535, 4: 32767, 5: 4294967295,
          6: 2147483647}


def audit(path):
    xml = open(path, encoding="utf-8", errors="replace").read()
    findings = []

    params = [(m.group(1), m.group(2))
              for m in re.finditer(r"<([a-zA-Z0-9_]+)>\s*(<longName>.*?)</\1>",
                                   xml, re.S)]
    by_name = {n: b for n, b in params}

    def missing(name):
        return name not in by_name

    # Tool <=7.00 dereferences getParam("hw_name")->longName unchecked on
    # connect; without the param it segfaults within ~2 s, every connect.
    if missing("hw_name"):
        findings.append("MISSING hw_name: tool <=7.00 segfaults after connect")
    elif not re.search(r"<longName>[^<]+</longName>", by_name["hw_name"]):
        findings.append("hw_name has an empty longName (the page name)")

    # Without config_name the generator names the struct device_config.
    if missing("config_name"):
        findings.append("MISSING config_name: generator emits device_config")

    trans = []
    for n, b in params:
        if re.search(r"<transmittable>1</transmittable>", b):
            t = re.search(r"<type>(\d+)</type>", b)
            trans.append((n, t.group(1) if t else "?", b))

    # getParamsXML (vesc_tool) emits <vTx> only for double and int params.
    # A served bool/enum/bitfield loses its vTx, the tool defaults it to
    # VESC_TX_UNDEFINED, and the page-signature check in deSerialize can
    # never match the generator's hash: "Could not deserialize custom
    # config 0" on every read, on every tool version. The page still
    # *loads*, so a loaded-check never catches it. Int 0/1 with vTx 1
    # keeps the 1-byte wire and hashes identically on both ends.
    for n, t, b in trans:
        if t not in ("1", "2"):
            findings.append(
                f"transmittable {TX_NAME.get(t, t)} '{n}': the served page "
                "loses its <vTx> -> the deserialize signature check fails "
                "forever; make it int 0/1")
        elif not re.search(r"<vTx>\d+</vTx>", b):
            findings.append(
                f"transmittable {TX_NAME[t]} '{n}' has no <vTx> in the "
                "source: the tool defaults it and the hash diverges")

    # The wire is exactly the SerOrder. Entries may be transmittable=0 -
    # that is the read-only info-field pattern (e.g. float's
    # float_version): it rides the wire and renders, but the value only
    # changes in firmware.
    ser = re.findall(r"<ser>([a-zA-Z0-9_]+)</ser>", xml)
    if len(ser) != len(set(ser)):
        findings.append("SerOrder has duplicate entries")
    unknown = {s for s in ser if missing(s)}
    if unknown:
        findings.append(f"SerOrder lists unknown params: {sorted(unknown)}")
    off_wire = {n for n, _, _ in trans} - set(ser)
    if off_wire:
        findings.append(
            f"transmittable params missing from SerOrder (never on the "
            f"wire, never persisted through the page): {sorted(off_wire)}")

    # PageCustomConfig renders only the "General" group's subgroups: one
    # tab per subgroup, one row per param. No Grouping (or no General
    # subgroups) is an empty pane even though the params exist and the
    # data round-trips.
    grp = re.search(r"<Grouping>(.*?)</Grouping>", xml, re.S)
    rendered = set()
    if not grp:
        findings.append(
            "NO Grouping section: the page renders an empty pane")
    else:
        groups = re.findall(r"<groupName>([^<]*)</groupName>", grp.group(1))
        if "General" not in groups:
            findings.append(
                f"no 'General' group ({groups}): only the General group "
                "renders")
        gens = re.search(
            r"<group>\s*<groupName>General</groupName>(.*?)</group>",
            grp.group(1), re.S)
        sub_g = gens.group(1) if gens else ""
        subs = re.findall(r"<subgroupName>([^<]*)</subgroupName>", sub_g)
        rendered = set(re.findall(r"<param>([^<]*)</param>", sub_g))
        if not subs:
            findings.append("General group has no subgroups: empty pane")
    invisible = set(ser) - rendered
    if invisible:
        findings.append(
            f"in SerOrder but not rendered (absent from the General "
            f"subgroups, so invisible on the page): {sorted(invisible)}")

    # The stock buffer codecs wrap silently: buffer_append_uint16 takes a
    # uint16_t (the caller's int truncates), and buffer_append_float16
    # casts to int16_t (values past +-32767 flip sign, they do not
    # saturate). A UI range wider than the wire type lets the user set a
    # value that comes back aliased.
    for n, t, b in trans:
        if t == "1":
            sc = re.search(r"<vTxDoubleScale>([^<]+)</vTxDoubleScale>", b)
            vtx = re.search(r"<vTx>7</vTx>", b)
            if vtx and sc:
                scale = float(sc.group(1))
                lims = []
                for tag in ("maxDouble", "minDouble"):
                    m = re.search(f"<{tag}>([^<]+)</{tag}>", b)
                    if m:
                        lims.append(abs(float(m.group(1))))
                if lims and max(lims) * scale > 32767:
                    findings.append(
                        f"double '{n}': |range| x scale = "
                        f"{max(lims) * scale:.0f} > 32767: the float16 "
                        "cast wraps, so the top of the UI range aliases "
                        "on read-back")
        elif t == "2":
            vtx = re.search(r"<vTx>(\d+)</vTx>", b)
            lims = []
            for tag in ("maxInt", "minInt"):
                m = re.search(f"<{tag}>([^<]+)</{tag}>", b)
                if m:
                    lims.append(abs(int(m.group(1))))
            if vtx and lims:
                v = int(vtx.group(1))
                if TX_CAP.get(v) and max(lims) > TX_CAP[v]:
                    findings.append(
                        f"int '{n}': range {max(lims)} exceeds vTx {v} "
                        f"capacity {TX_CAP[v]}: out-of-range values "
                        "truncate on the wire")

    if not findings:
        print(f"{path}: clean against all recorded rules")
        return True
    print(f"{path}:")
    for f in findings:
        print(f"  - {f}")
    return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    ok = all(audit(p) for p in sys.argv[1:])
    sys.exit(0 if ok else 1)
