#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""do the fleet heartbeats say one thing per quantity, or several?

WHY THIS FILE EXISTS
--------------------
fleet/machines/<machine>.json is a shared face that many writers merge into. Every writer that
wanted "cpu load" invented its own key, so the same machine now publishes
    cpu_load_pct=97 and CPU_load_pct=10.2 and cpu_pct=37
in one object, and the pair that differs only by case makes the file fail a case-insensitive
reader outright (PowerShell ConvertFrom-Json refuses the whole document: "keys with different
casing"). r1909 legislated exactly this for the GPU face ("self-consistency must count every
letter a reader can read"); this tool is the fleet-heartbeat twin of that rule.

WHAT IT DOES
------------
Groups the keys of each heartbeat into frozen quantities (cpu load %, RAM free, RAM total,
VRAM free, VRAM total), converting GB strings to MiB, parsing the prose forms the GPU face
writes ("13.4 GB free / 16 GB"), and reports per quantity:
    spread in canonical units, the disagreeing keys named, and a verdict word
It also flags every case-insensitive duplicate key, because that is a reader-breaking defect no
number can explain.

WHAT IT DOES NOT DO
-------------------
Read-only. It never rewrites a heartbeat, never picks a "true" value, and never invents a zero
for a quantity no writer published (a missing quantity is MISSING, not 0). Deciding which alias
is authoritative is a writer/owner decision, not a measurement.

self  python Tools/heartbeat_alias_audit.py selftest
run   python Tools/heartbeat_alias_audit.py [run]
check python Tools/heartbeat_alias_audit.py check
"""

import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MACHINES_DIR = os.path.join(ROOT, "fleet", "machines")
OUT_PATH = os.path.join(ROOT, "results", "heartbeat_alias_audit.json")
FACE = "results/heartbeat_alias_audit.json"
SCHEMA = "heartbeat-alias-audit/v1"

REL_TOL = 0.02          # 2% of the quantity's median, frozen before the first read
ABS_TOL = {"pct": 2.0, "mib": 64.0}

# quantity -> alias keys with the multiplier that brings them to the canonical unit.
# Only keys whose NAME states the same measurement are grouped; a bare "cpu" or "gpu" is not
# grouped because it may be a process/device figure rather than the machine total.
QUANTITIES = {
    "cpu_load_pct": {
        "unit": "pct",
        "keys": {"cpu_load_pct": 1.0, "cpu_util_pct": 1.0, "cpu_pct": 1.0,
                 "cpu_total_pct": 1.0},
    },
    "ram_free_mb": {
        "unit": "mib",
        "keys": {"ram_free_mb": 1.0, "free_ram_mb": 1.0, "ram_free_gb": 1024.0,
                 "free_ram_gb": 1024.0, "ram_free_gib": 1024.0},
    },
    "ram_total_mb": {
        "unit": "mib",
        "keys": {"ram_total_mb": 1.0, "ram_total_gb": 1024.0, "memory_total_gb": 1024.0},
    },
    "vram_free_mb": {
        "unit": "mib",
        "keys": {"vram_free_mib": 1.0, "vram_free_mb": 1.0, "gpu_free_mib": 1.0,
                 "gpu_free_mb": 1.0, "gpu_free_vram_mb": 1.0, "gpu_free_vram_mib": 1.0,
                 "gpu_vram_free_mb": 1.0, "gpu_vram_free_mib": 1.0, "gpu_idle_mb": 1.0,
                 "gpu_idle_mib": 1.0, "gpu_idle_vram_mb": 1.0, "gpu_idle_vram_mib": 1.0,
                 "free_vram_mb": 1.0, "free_vram_gb": 1024.0, "gpu_free_gb": 1024.0,
                 "gpu_free_vram_gb": 1024.0, "gpu_free_vram_gib": 1024.0},
    },
    "vram_total_mb": {
        "unit": "mib",
        "keys": {"vram_total_mib": 1.0, "gpu_total_mib": 1.0, "gpu_total_mb": 1.0,
                 "gpu_mem_total_mib": 1.0, "gpu_total_vram_mib": 1.0,
                 "gpu_vram_total_mib": 1.0},
    },
}

# prose forms written by Tools/gpu_face.py ("13.4 GB free / 16 GB", "2628 MiB used of 16384 MiB")
PROSE_FREE = re.compile(r"([\d.]+)\s*(GB|GiB|MB|MiB)\s*(?:free|idle)", re.I)
PROSE_USED = re.compile(r"([\d.]+)\s*(GB|GiB|MB|MiB)\s*used", re.I)
UNIT_MULT = {"gb": 1024.0, "gib": 1024.0, "mb": 1.0, "mib": 1.0}


def as_mib(num, unit):
    return float(num) * UNIT_MULT[unit.lower()]


def prose_values(text):
    """pull the numbers a human-form sentence publishes, as (free_mib, used_mib)."""
    free = None
    used = None
    m = PROSE_FREE.search(text)
    if m:
        free = as_mib(m.group(1), m.group(2))
    m = PROSE_USED.search(text)
    if m:
        used = as_mib(m.group(1), m.group(2))
    return free, used


def duplicate_case_keys(pairs):
    """keys that a case-insensitive reader would collapse into one (they break strict readers)."""
    seen, dupes = {}, []
    for k, _v in pairs:
        low = k.lower()
        if low in seen and seen[low] != k:
            dupes.append({"keys": sorted([seen[low], k]), "canonical": low})
        else:
            seen.setdefault(low, k)
    return dupes


def load_heartbeat(path):
    """strict parse that keeps the key pairs, so duplicate-case keys stay visible."""
    with io.open(path, encoding="utf-8") as fh:
        raw = fh.read()
    pairs = json.loads(raw, object_pairs_hook=lambda p: p)
    flat = {}
    for k, v in pairs:
        if isinstance(v, (str, int, float, bool)) or v is None:
            flat[k] = v
    return pairs, flat


def read_quantity(flat, spec, prose_face=None):
    """every alias that carries this quantity, in canonical units."""
    hits, skipped = [], []
    for key, mult in spec["keys"].items():
        if key not in flat:
            continue
        v = flat[key]
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            skipped.append({"key": key, "why": "value is not a number (%r)" % (v,)})
            continue
        hits.append({"key": key, "value": float(v) * mult, "raw": v})
    if prose_face and prose_face.get("free_mib") is not None:
        hits.append({"key": "gpu_face(prose)", "value": prose_face["free_mib"],
                     "raw": prose_face.get("text")})
    return hits, skipped


def unit_mislabels(hits):
    """keys whose NAME says GB/GiB but whose NUMBER is already in MiB.

    Detected without trusting the name: take the median of the keys that are unambiguously MiB
    (name ends in mb/mib), then ask whether this key's RAW number matches that median while its
    converted number does not. That is exactly what a writer does when it puts a MiB figure into
    a GiB key -- and r1311 fixed one such alias while this one survived on two machines.
    """
    plain = [h["value"] for h in hits if h["key"].lower().endswith(("_mb", "_mib"))]
    if len(plain) < 2:
        return []
    base = sorted(plain)[len(plain) // 2]
    tol = max(ABS_TOL.get("mib", 0.0), abs(base) * REL_TOL)
    bad = []
    for h in hits:
        k = h["key"].lower()
        if not k.endswith(("_gb", "_gib")) or h.get("raw") is None:
            continue
        try:
            raw = float(h["raw"])
        except (TypeError, ValueError):
            continue
        if abs(raw - base) <= tol and abs(h["value"] - base) > tol:
            bad.append({"key": h["key"], "raw_written": raw,
                        "reads_as_mib": base, "reads_as_gib_mib": round(h["value"], 1),
                        "why": "the number under a GB/GiB key is already MiB"})
    return bad


def judge(hits, unit):
    if not hits:
        return {"verdict": "MISSING", "spread": None, "named": []}
    vals = [h["value"] for h in hits]
    vals_sorted = sorted(vals)
    mid = vals_sorted[len(vals_sorted) // 2]
    spread = max(vals) - min(vals)
    tol = max(ABS_TOL.get(unit, 0.0), abs(mid) * REL_TOL)
    mislabel = unit_mislabels(hits) if unit == "mib" else []
    word = "AGREE" if spread <= tol else "DISAGREE_ALIASES"
    return {
        "verdict": word,
        "canonical_median": mid,
        "spread": spread,
        "tolerance": tol,
        "unit_mislabels": mislabel,
        "named": [] if word == "AGREE" else [
            {"key": h["key"], "value": round(h["value"], 3),
             "distance_from_median": round(h["value"] - mid, 3)}
            for h in sorted(hits, key=lambda z: -abs(z["value"] - mid))],
    }


def audit_machine(path):
    pairs, flat = load_heartbeat(path)
    name = os.path.basename(path)
    prose_text = None
    for k in ("gpu_face", "gpu_note"):
        if isinstance(flat.get(k), str):
            prose_text = flat[k]
            break
    prose_free, prose_used = prose_values(prose_text) if prose_text else (None, None)
    prose_face = {"free_mib": prose_free, "text": prose_text} if prose_text else None

    blocks = {}
    for qname, spec in QUANTITIES.items():
        hits, skipped = read_quantity(flat, spec,
                                      prose_face if qname == "vram_free_mb" else None)
        block = judge(hits, spec["unit"])
        block["keys_read"] = [h["key"] for h in hits]
        if skipped:
            block["skipped"] = skipped
        blocks[qname] = block

    broken = [b["verdict"] == "DISAGREE_ALIASES" for b in blocks.values()]
    mislabelled = [m for b in blocks.values() for m in (b.get("unit_mislabels") or [])]
    dup = duplicate_case_keys(pairs)
    return {
        "machine_file": name,
        "key_count": len(flat),
        "duplicate_case_keys": dup,
        "unit_mislabels": mislabelled,
        "quantities": blocks,
        "verdict": ("DUPLICATE_CASE_KEYS_AND_DISAGREEING_ALIASES" if dup and any(broken)
                    else "DUPLICATE_CASE_KEYS" if dup
                    else "DISAGREEING_ALIASES" if any(broken)
                    else "AGREE"),
    }


def compute():
    paths = sorted(glob.glob(os.path.join(MACHINES_DIR, "*.json")))
    machines, errors = [], []
    for p in paths:
        try:
            machines.append(audit_machine(p))
        except Exception as exc:                                 # noqa: BLE001
            errors.append({"machine_file": os.path.basename(p), "why": repr(exc)})
    def _count(m, word):
        return sum(1 for q in m["quantities"].values() if q["verdict"] == word)
    return {
        "schema": SCHEMA, "face": FACE,
        "question": "does each heartbeat publish one value per quantity, and can a "
                    "case-insensitive reader open it at all?",
        "rule": {
            "R1_groups": "only keys whose name states the same measurement are grouped; a bare "
                         "'cpu'/'gpu' key is never assumed to be the machine total",
            "R2_units": "GB/GiB are converted at 1024 to MiB before comparing; percentages are "
                        "never mixed with memory",
            "R3_tolerance": "agreement means spread <= max(%s, %.0f%% of the median) -- frozen "
                            "before the first read" % (ABS_TOL, REL_TOL * 100),
            "R4_missing": "a quantity no writer published is MISSING, never zero",
            "R5_dupes": "a case-insensitive duplicate key is reported even when the numbers "
                        "agree, because it breaks strict readers",
            "R6_readonly": "this tool never rewrites a heartbeat and never picks a winner",
            "R7_mislabel": "a key whose name ends in GB/GiB but whose raw number matches the MiB "
                           "median is reported as a unit mislabel -- detected without trusting "
                           "the key name, because the shared GPU writer has this defect",
        },
        "tolerance": {"rel": REL_TOL, "abs": ABS_TOL},
        "machines_read": len(machines),
        "machines": machines,
        "read_errors": errors,
        "summary": {
            "machines_with_duplicate_case_keys": sum(1 for m in machines
                                                     if m["duplicate_case_keys"]),
            "machines_with_disagreeing_aliases": sum(1 for m in machines
                                                     if _count(m, "DISAGREE_ALIASES")),
            "quantity_disagreements": sum(_count(m, "DISAGREE_ALIASES") for m in machines),
            "quantity_missing": sum(_count(m, "MISSING") for m in machines),
            "machines_with_unit_mislabels": sum(1 for m in machines if m["unit_mislabels"]),
            "unit_mislabel_keys": sum(len(m["unit_mislabels"]) for m in machines),
        },
    }


def write_face(doc):
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with io.open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def check():
    if not os.path.exists(OUT_PATH):
        print("STALE face missing: %s" % FACE)
        return 3
    with io.open(OUT_PATH, encoding="utf-8") as fh:
        old = json.load(fh)
    live = compute()
    old_files = {m["machine_file"] for m in old.get("machines") or []}
    new_files = {m["machine_file"] for m in live["machines"]}
    if old_files != new_files or old.get("machines_read") != live["machines_read"]:
        print("STALE machine set changed: %s -> %s"
              % (sorted(old_files), sorted(new_files)))
        return 3
    bad = []
    old_by = {m["machine_file"]: m for m in old.get("machines") or []}
    for m in live["machines"]:
        o = old_by.get(m["machine_file"]) or {}
        if o.get("verdict") != m["verdict"]:
            bad.append("%s verdict %r != %r" % (m["machine_file"], o.get("verdict"), m["verdict"]))
            continue
        for q, blk in m["quantities"].items():
            ob = (o.get("quantities") or {}).get(q) or {}
            if ob.get("verdict") != blk["verdict"]:
                bad.append("%s/%s verdict %r != %r" % (m["machine_file"], q,
                                                       ob.get("verdict"), blk["verdict"]))
    if bad:
        print("STALE heartbeats moved since the face was written: " + "; ".join(bad[:6]))
        return 3
    s = old.get("summary") or {}
    print("CHECK OK %d heartbeats, %d case-duplicate, %d disagreeing-alias machines"
          % (old.get("machines_read") or 0, s.get("machines_with_duplicate_case_keys") or 0,
             s.get("machines_with_disagreeing_aliases") or 0))
    return 0


# --------------------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------------------
def selftest():
    legs, ok = [], 0

    def leg(name, cond):
        nonlocal ok
        legs.append({"leg": name, "pass": bool(cond)})
        if cond:
            ok += 1

    # 1 duplicate-case keys are caught, same-case repeats are not miscounted
    dup = duplicate_case_keys([("cpu_load_pct", 1), ("CPU_load_pct", 2), ("ts", "x")])
    leg("a key pair differing only by case is reported",
        len(dup) == 1 and dup[0]["keys"] == ["CPU_load_pct", "cpu_load_pct"])
    leg("distinct keys are not reported as duplicates",
        duplicate_case_keys([("cpu_load_pct", 1), ("cpu_pct", 2)]) == [])

    # 2 units are converted before comparing
    leg("GB converts at 1024", abs(as_mib(13.4, "GB") - 13721.6) < 1e-9)
    leg("MiB is the canonical unit already", abs(as_mib(2628, "MiB") - 2628.0) < 1e-9)

    # 3 prose forms the GPU face writes
    f, u = prose_values("nvidia-smi 5% / 2628 MiB used of 16384 MiB")
    leg("the used figure is read from prose", abs(u - 2628.0) < 1e-9 and f is None)
    f2, _u2 = prose_values("13.4 GB free / 16 GB")
    leg("the free figure is read from prose and converted", abs(f2 - 13721.6) < 1e-9)

    # 4 agreement and disagreement words
    agree = judge([{"key": "a", "value": 13756.0}, {"key": "b", "value": 13756.0}], "mib")
    leg("identical aliases agree", agree["verdict"] == "AGREE" and agree["named"] == [])
    near = judge([{"key": "a", "value": 13700.0}, {"key": "b", "value": 13756.0}], "mib")
    leg("a small MiB gap is inside the tolerance", near["verdict"] == "AGREE")
    wide = judge([{"key": "a", "value": 16542.0}, {"key": "b", "value": 24064.0}], "mib")
    leg("a 7.5 GB gap is a disagreement", wide["verdict"] == "DISAGREE_ALIASES")
    leg("the disagreement names every key with its distance",
        len(wide["named"]) == 2 and all("distance_from_median" in n for n in wide["named"]))
    pct = judge([{"key": "a", "value": 10.2}, {"key": "b", "value": 97.0}], "pct")
    leg("97% vs 10.2% is a disagreement, not rounding",
        pct["verdict"] == "DISAGREE_ALIASES")
    leg("a missing quantity is MISSING, never zero",
        judge([], "mib")["verdict"] == "MISSING")

    # 5 only named-same-measurement keys are grouped
    flat = {"cpu": 5.0, "cpu_load_pct": 97.0, "CPU_load_pct": 10.2, "gpu_free_mb": 13756,
            "free_ram_mb": 16542, "ram_free_mb": 24064, "ram_free_gb": 29.6}
    hits, _sk = read_quantity(flat, QUANTITIES["cpu_load_pct"])
    leg("a bare 'cpu' key is never assumed to be the machine load",
        "cpu" not in [h["key"] for h in hits])
    ram, _sk2 = read_quantity(flat, QUANTITIES["ram_free_mb"])
    leg("mb and gb aliases of ram free land in one canonical unit",
        sorted(h["key"] for h in ram) == ["free_ram_mb", "ram_free_gb", "ram_free_mb"])
    leg("the gb alias is converted, so 29.6 GB is comparable to 24064 MB",
        any(abs(h["value"] - 30310.4) < 1e-6 for h in ram))

    # 6 a non-numeric alias is skipped with a reason, not silently dropped
    hits3, sk3 = read_quantity({"gpu_free_mb": "13.4 GB free"}, QUANTITIES["vram_free_mb"])
    leg("a string under a numeric alias is named, not parsed as a number",
        hits3 == [] and sk3 and "not a number" in sk3[0]["why"])

    # 7 frozen constants
    leg("tolerances are constants in code",
        REL_TOL == 0.02 and ABS_TOL["mib"] == 64.0 and ABS_TOL["pct"] == 2.0)

    # 8 unit mislabel: a MiB number sitting under a GiB key (the shared GPU writer's defect)
    mis_hits = [{"key": "gpu_free_mib", "value": 13754.0, "raw": 13754},
                {"key": "gpu_free_mb", "value": 13754.0, "raw": 13754},
                {"key": "gpu_free_vram_gib", "value": 13754.0 * 1024.0, "raw": 13754}]
    ml = unit_mislabels(mis_hits)
    leg("a MiB number under a GiB key is named as a unit mislabel",
        len(ml) == 1 and ml[0]["key"] == "gpu_free_vram_gib")
    leg("the mislabel report carries both readings",
        ml and ml[0]["reads_as_mib"] == 13754.0 and ml[0]["reads_as_gib_mib"] > 1e7)
    honest_hits = [{"key": "gpu_free_mib", "value": 13754.0, "raw": 13754},
                   {"key": "gpu_free_mb", "value": 13754.0, "raw": 13754},
                   {"key": "gpu_free_vram_gib", "value": 13.43 * 1024.0, "raw": 13.43}]
    leg("an honest GiB alias is not accused",
        unit_mislabels(honest_hits) == [])
    leg("the mislabel detector stays quiet without at least two MiB keys to anchor on",
        unit_mislabels([{"key": "gpu_free_vram_gib", "value": 13754.0 * 1024.0,
                         "raw": 13754}]) == [])
    leg("the mislabel word is visible in the judge block",
        judge(mis_hits, "mib").get("unit_mislabels") and
        judge(mis_hits, "mib")["verdict"] == "DISAGREE_ALIASES")
    leg("percentages are never run through the MiB mislabel detector",
        judge([{"key": "a_pct", "value": 10.0, "raw": 10},
               {"key": "b_pct", "value": 97.0, "raw": 97}], "pct").get("unit_mislabels") == [])

    print(json.dumps({"legs": len(legs), "passed": ok,
                      "failed": [l["leg"] for l in legs if not l["pass"]]},
                     ensure_ascii=False))
    return 0 if ok == len(legs) else 1


def run():
    doc = compute()
    write_face(doc)
    print(json.dumps({"face": FACE, "machines": doc["machines_read"],
                      "summary": doc["summary"],
                      "errors": doc["read_errors"]}, ensure_ascii=False))
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        return run()
    if cmd == "check":
        return check()
    print("usage: heartbeat_alias_audit.py [run|check|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
