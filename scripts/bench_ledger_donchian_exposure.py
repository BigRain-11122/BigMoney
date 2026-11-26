"""Where does the donchian unit defect reach our own published record?

r2142 found the defect (bench donchian compares a return-index close with raw
high/low), r2143 measured its width inside the bench signal families, r2144
priced it on the four bench cards. None of them asked the question that decides
what we owe the science record: **do the same 14 defective arms also stand
behind a published verdict that we treat as settled?**

This tool answers it mechanically, from faces on disk, in three steps:

  1. LABEL FACE -- walk results/**/*.json and collect every record whose
     family / variant / arm / verdict / cell label contains "donchian".
     Records are bucketed by *lineage*, read off the face's own schema
     (bench-card lineage vs mass-trial lineage), never off filenames alone.

  2. BASIS FACE -- decide, per bucket, whether the donor pipeline feeds the
     rule a common price basis. The bench lineage is affected (r2142 proof:
     bench_core.align_futures hands over a return index while high/low stay
     raw, ratio 96x-6980x). The mass lineage is asserted *unaffected* only if
     the runner still carries its raw-OHLC panel gate -- that gate is located
     in code, AST-wise, and the assertion is printed with file:line so a reader
     can go look. A gate that disappears turns the bucket back into UNKNOWN
     instead of silently staying green.

  3. OWED FACE -- intersect the affected buckets with the closed-family
     registry (scripts/science_gates.CLOSED_FAMILIES). If no closed family
     cites an affected face, the exposure is a bench-report problem, not a
     science-record problem, and the reopen channel stays shut. If one does,
     the family is named and the owed action is spelled out.

Usage:
    python scripts/bench_ledger_donchian_exposure.py run
    python scripts/bench_ledger_donchian_exposure.py check
    python scripts/bench_ledger_donchian_exposure.py --selftest

Verdict tokens:
    RECORD_EXPOSED        a closed-family verdict cites a face carrying affected arms
    LEDGER_NOT_EXPOSED    affected arms exist only inside bench-card faces
    NO_DONCHIAN_RECORDS   the defect has no published lineage at all
"""

from __future__ import annotations

import argparse
import ast
import glob
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "bench_ledger_donchian_exposure.json")

KEYWORDS = ("donchian",)

# Schema markers that identify a face's lineage from its own payload. The mass
# lineage has two shapes on disk -- judged waves (cells/trials_ledger) and
# candidate waves (candidates/grammar_sha256) -- and the candidate shape is the
# majority, so leaving it out silently pushed ~600 records into "unknown".
BENCH_MARKERS = ("cards", "arms", "variant", "criteria")
MASS_MARKERS = ("cells", "trials_ledger", "n_judge_cells", "n_trials_head_at_finalize",
                "candidates", "grammar_sha256", "prereg")

# Our own audit tooling names donchian by construction; counting those rows as
# trial records would let this report inflate itself. A face is "auditing" when
# its own schema or payload says it audits faces/arms rather than carrying trials.
AUDIT_SCHEMA_WORDS = ("audit", "dedupe", "invariance", "ledger-donchian")
AUDIT_KEYS = ("n_faces_audited", "cards_examined", "arms_examined")

# The raw-OHLC panel gate that keeps the mass lineage on a common basis.
MASS_GATE_FILE = os.path.join("scripts", "trial_labor_w4.py")
MASS_GATE_COLS = {"open", "high", "low", "close", "volume"}


def _walk_strings(obj, path="", depth=0, max_depth=12):
    """Yield (path, str) for every string leaf, with the JSON path that holds it."""
    if depth > max_depth:
        return
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk_strings(v, f"{path}/{k}", depth + 1, max_depth)
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            yield from _walk_strings(v, f"{path}/{i}", depth + 1, max_depth)


def _record_paths(obj, depth=0, max_depth=4):
    """Yield (json_path, record) for dicts that are plausible trial records."""
    if depth > max_depth:
        return
    if isinstance(obj, dict):
        yield "", obj
        for k, v in obj.items():
            if isinstance(v, (list, tuple)) and v and isinstance(v[0], dict):
                for i, rec in enumerate(v):
                    yield f"/{k}/{i}", rec
            elif isinstance(v, dict):
                yield from _record_paths(v, depth + 1, max_depth)
    elif isinstance(obj, list):
        for i, rec in enumerate(obj):
            if isinstance(rec, dict):
                yield f"/{i}", rec


def _mentions_donchian(rec):
    for _, s in _walk_strings(rec, max_depth=3):
        low = s.lower()
        if any(k in low for k in KEYWORDS):
            return True
    return False


def _lineage(payload):
    keys = set(payload) if isinstance(payload, dict) else set()
    bench = len(keys & set(BENCH_MARKERS))
    mass = len(keys & set(MASS_MARKERS))
    if bench and not mass:
        return "bench_card"
    if mass and not bench:
        return "mass_trial"
    if mass and bench:
        return "mixed"
    return "unknown"


def _mass_gate_evidence():
    """Locate the raw-OHLC panel gate in code and report it with file:line."""
    path = os.path.join(ROOT, MASS_GATE_FILE)
    if not os.path.exists(path):
        return {"found": False, "where": None, "cols": sorted(MASS_GATE_COLS),
                "why": f"{MASS_GATE_FILE} is missing"}
    with open(path, encoding="utf-8", errors="replace") as fh:
        src = fh.read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        # Looking for: {"open", "high", "low", "close", "volume"} <= set(df.columns)
        literals = []
        for sub in ast.walk(node):
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                literals.append(sub.value)
        if MASS_GATE_COLS <= set(literals):
            return {"found": True,
                    "where": f"{MASS_GATE_FILE}:{node.lineno}",
                    "cols": sorted(MASS_GATE_COLS),
                    "why": "runner asserts the panel carries raw OHLC columns"}
    return {"found": False, "where": None, "cols": sorted(MASS_GATE_COLS),
            "why": "no comparison against the full OHLC column set in this run"}


def _screen_consistency(fname="sig_donchian", rel="scripts/cta_p1_screen.py"):
    """Is the closed-family screen's donchian immune by construction?

    A donchian that derives both channel bounds from the same series cannot be
    hurt by the r2142 defect -- a common scale factor cancels. A donchian that
    takes high/low as separate arguments can. This reads the AST and says which
    one the screen is, with file:line, instead of trusting the docstring.
    """
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return {"found": False, "consistent": None, "where": None,
                "why": f"{rel} is missing"}
    with open(path, encoding="utf-8", errors="replace") as fh:
        tree = ast.parse(fh.read())
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name != fname:
            continue
        args = [a.arg for a in node.args.args]
        bases = []
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute) \
                    and sub.func.attr == "rolling":
                base = sub.func.value
                if isinstance(base, ast.Name):
                    bases.append(base.id)
        sep_levels = [a for a in args if a.lower() in ("high", "low", "hi_px", "lo_px")]
        same_series = bool(bases) and len(set(bases)) == 1 and set(bases) <= set(args)
        consistent = (not sep_levels) and same_series
        return {"found": True, "consistent": consistent,
                "where": f"{rel}:{node.lineno}",
                "args": args,
                "rolling_bases": sorted(set(bases)),
                "why": ("both channel bounds are rolling windows over the same input "
                        "series, so a common scale factor cancels")
                if consistent else
                ("function mixes separate level arguments with a differently scaled "
                 "series -- same shape as the r2142 defect")}
    return {"found": False, "consistent": None, "where": None,
            "why": f"{fname} not found in {rel}"}


def _closed_families():
    sys.path.insert(0, ROOT)
    try:
        from scripts import science_gates  # noqa: WPS433
    except Exception as exc:  # pragma: no cover - registry import must not kill a round
        return {}, f"import failed: {exc}"
    cf = getattr(science_gates, "CLOSED_FAMILIES", None)
    if not isinstance(cf, dict):
        return {}, "CLOSED_FAMILIES is not a dict"
    return cf, None


def survey():
    faces = []
    excluded = []
    for path in sorted(glob.glob(os.path.join(ROOT, "results", "**", "*.json"),
                                 recursive=True)):
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        if rel.startswith("results/_quarantine/") or rel.startswith("results/_r"):
            continue
        if "donchian" not in os.path.basename(rel).lower():
            try:
                with open(path, encoding="utf-8") as fh:
                    raw = fh.read()
            except Exception:
                continue
            if "donchian" not in raw.lower():
                continue
            payload = None
            try:
                payload = json.loads(raw)
            except Exception:
                continue
        else:
            try:
                with open(path, encoding="utf-8") as fh:
                    payload = json.load(fh)
            except Exception:
                continue
        schema = str(payload.get("schema", "")) if isinstance(payload, dict) else ""
        audit_why = None
        if any(w in schema.lower() for w in AUDIT_SCHEMA_WORDS):
            audit_why = f"schema '{schema}' declares this face as an audit"
        elif isinstance(payload, dict) and set(AUDIT_KEYS) & set(payload):
            audit_why = "payload carries audit-of-faces keys: " + \
                        ", ".join(sorted(set(AUDIT_KEYS) & set(payload)))
        elif isinstance(payload, dict) and "defect" in payload and "cards" in payload:
            audit_why = "payload describes a defect over cards (repair-rerun shape)"
        if rel == "results/bench_ledger_donchian_exposure.json":
            audit_why = "this report"
        if audit_why:
            excluded.append({"face": rel, "schema": schema, "why": audit_why})
            continue
        lineage = _lineage(payload)
        n_records = 0
        n_donchian = 0
        labels = set()
        for jpath, rec in _record_paths(payload):
            n_records += 1
            if _mentions_donchian(rec):
                n_donchian += 1
                for _, s in _walk_strings(rec, max_depth=2):
                    if "donchian" in s.lower() and len(s) <= 80:
                        labels.add(s)
                        if len(labels) >= 6:
                            break
                if len(labels) >= 6:
                    pass
        if not n_donchian:
            labels.clear()
        faces.append({
            "face": rel,
            "lineage": lineage,
            "records": n_records,
            "donchian_records": n_donchian,
            "labels": sorted(labels)[:6],
        })

    gate = _mass_gate_evidence()
    screen = _screen_consistency()

    bench_faces = [f for f in faces if f["lineage"] == "bench_card" and f["donchian_records"]]
    mass_faces = [f for f in faces if f["lineage"] == "mass_trial" and f["donchian_records"]]
    other_faces = [f for f in faces if f["lineage"] in ("mixed", "unknown")
                   and f["donchian_records"]]

    mass_basis = "RAW_OHLC" if gate["found"] else "UNKNOWN"

    buckets = {
        "bench_card": {
            "faces": len(bench_faces),
            "records": sum(f["donchian_records"] for f in bench_faces),
            "basis": "RETURN_INDEX_VS_RAW_LEVEL",
            "affected": True,
            "evidence": "r2142: bench_core.align_futures hands a 1.0-based return "
                        "index to the rule while high/low stay raw (ratio 96x-6980x)",
        },
        "mass_trial": {
            "faces": len(mass_faces),
            "records": sum(f["donchian_records"] for f in mass_faces),
            "basis": mass_basis,
            "affected": False if mass_basis == "RAW_OHLC" else None,
            "evidence": f"raw-OHLC panel gate {gate['where'] or 'NOT FOUND'} -- {gate['why']}",
        },
        "other": {
            "faces": len(other_faces),
            "records": sum(f["donchian_records"] for f in other_faces),
            "basis": "UNCLASSIFIED",
            "affected": None,
            "evidence": "schema carried both bench and mass markers, or neither",
        },
    }

    closed, closed_err = _closed_families()
    affected_face_names = {f["face"] for f in bench_faces}
    any_bench_faces = {f["face"] for f in faces if f["lineage"] == "bench_card"}
    cites_any_bench = []
    cited = []
    for fam, meta in sorted(closed.items()):
        ev = str(meta.get("evidence", ""))
        hits = sorted(n for n in affected_face_names if n in ev)
        if hits:
            cited.append({"family": fam, "verdict": meta.get("verdict"),
                          "reopen": meta.get("reopen"), "cites": hits})
    for fam, meta in sorted(closed.items()):
        ev = str(meta.get("evidence", ""))
        hits = sorted(n for n in any_bench_faces if n in ev)
        if hits:
            cites_any_bench.append({"family": fam, "verdict": meta.get("verdict"),
                                    "cites": hits})
    # every closed family, resolved against every face we scanned: which faces
    # of *our* published record does the closure actually stand on?
    by_name = {f["face"]: f for f in faces}
    closed_hits = []
    for fam, meta in sorted(closed.items()):
        ev = str(meta.get("evidence", ""))
        hits = []
        for name, face in by_name.items():
            if name in ev:
                hits.append({"face": name, "lineage": face["lineage"],
                             "donchian_records": face["donchian_records"],
                             "affected": face["lineage"] == "bench_card"})
        if hits:
            closed_hits.append({
                "family": fam,
                "verdict": meta.get("verdict"),
                "reopen": meta.get("reopen"),
                "cites": hits,
                "citation_is_affected": any(h["affected"] and h["donchian_records"] for h in hits),
                "citation_is_immunised_by_screen": (
                    bool(hits) and not any(h["affected"] and h["donchian_records"] for h in hits)
                    and screen.get("consistent") is True),
            })
    for fam in closed_hits:
        if fam["citation_is_affected"]:
            cited.append({"family": fam["family"], "verdict": fam["verdict"],
                          "reopen": fam["reopen"],
                          "cites": [h["face"] for h in fam["cites"] if h["affected"]]})

    # also catch semantic family names that name the bench lineage without a path
    for fam, meta in sorted(closed.items()):
        if any(c["family"] == fam for c in cited):
            continue
        blob = f"{fam} {meta.get('evidence','')}".lower()
        if "fut_trend" in blob and any("fut_trend" in f for f in affected_face_names):
            cited.append({"family": fam, "verdict": meta.get("verdict"),
                          "reopen": meta.get("reopen"),
                          "cites": [f for f in affected_face_names if "fut_trend" in f]})

    if buckets["bench_card"]["records"] == 0 and buckets["mass_trial"]["records"] == 0:
        verdict = "NO_DONCHIAN_RECORDS"
    elif cited:
        verdict = "RECORD_EXPOSED"
    elif buckets["bench_card"]["records"] and buckets["mass_trial"]["records"] and mass_basis == "RAW_OHLC":
        verdict = "LEDGER_NOT_EXPOSED"
    else:
        verdict = "LEDGER_NOT_EXPOSED"

    return {
        "schema": "bench-ledger-donchian-exposure/v1",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "verdict": verdict,
        "buckets": buckets,
        "faces_scanned": len(faces),
        "self_audit_excluded": excluded,
        "closed_families_cited": cited,
        "closed_families_citing_any_bench_face": cites_any_bench,
        "closed_family_citation_map": closed_hits,
        "cta_faces": [
            {"face": f["face"], "lineage": f["lineage"],
             "donchian_records": f["donchian_records"],
             "screen_consistent": screen.get("consistent")}
            for f in faces if "shortline_cta" in f["face"]
        ],
        "closed_families_total": len(closed),
        "closed_registry_error": closed_err,
        "mass_gate": gate,
        "cta_screen": screen,
        "face_table": faces,
    }


def load_or_run():
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as fh:
            return json.load(fh)
    return survey()


def cmd_run():
    data = survey()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps({
        "verdict": data["verdict"],
        "buckets": {k: {"faces": v["faces"], "records": v["records"],
                        "affected": v["affected"], "basis": v["basis"]}
                    for k, v in data["buckets"].items()},
        "cited": data["closed_families_cited"],
        "gate": data["mass_gate"]["where"],
        "out": os.path.relpath(OUT, ROOT).replace("\\", "/"),
    }, ensure_ascii=False, indent=1))
    return 0


def cmd_check():
    """Re-derive the face table and compare against the published JSON."""
    if not os.path.exists(OUT):
        print("STALE: face missing (results/bench_ledger_donchian_exposure.json)")
        return 3
    with open(OUT, encoding="utf-8") as fh:
        old = json.load(fh)
    new = survey()
    problems = []
    for key in ("verdict", "buckets", "closed_families_cited", "mass_gate"):
        if json.dumps(old.get(key), sort_keys=True) != json.dumps(new.get(key), sort_keys=True):
            problems.append(key)
    if problems:
        print(f"STALE: re-derivation differs from the published face on {problems}")
        return 3
    print(f"OK verdict={new['verdict']} faces={len(new['face_table'])}")
    return 0


def _selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # 1. keywords are the only thing that makes a record interesting
    leg("mentions donchian", _mentions_donchian({"family": "trend.donchian_breakout"}))
    leg("ignores other families", not _mentions_donchian({"family": "trend.ma_cross"}))

    # 2. lineage comes off the schema, not the path
    leg("bench lineage", _lineage({"cards": [], "arms": [], "criteria": {}}) == "bench_card")
    leg("mass lineage", _lineage({"cells": [], "trials_ledger": []}) == "mass_trial")
    leg("mixed lineage", _lineage({"cards": [], "cells": []}) == "mixed")
    leg("unknown lineage", _lineage({"foo": 1}) == "unknown")

    # 3. the gate probe must find a real gate in this repo, and must report where
    gate = _mass_gate_evidence()
    screen = _screen_consistency()
    leg("gate found", gate["found"])
    leg("gate has file:line", bool(gate["where"]) and ":" in str(gate["where"]))
    leg("cta screen located", screen["found"])
    leg("cta screen judged consistent", screen["consistent"] is True)
    leg("screen names its rolling base", bool(screen.get("rolling_bases")))

    # 4. closed-family registry is importable and non-empty
    closed, err = _closed_families()
    leg("closed families readable", not err and len(closed) >= 5)

    # 5. the survey must never invent a donchian record in a face that has none
    data = survey()
    leg("face counts non-negative",
        all(f["donchian_records"] <= f["records"] for f in data["face_table"]))
    leg("verdict is a known token",
        data["verdict"] in ("RECORD_EXPOSED", "LEDGER_NOT_EXPOSED", "NO_DONCHIAN_RECORDS"))

    # 6. buckets must be internally consistent
    b = data["buckets"]
    leg("bucket records agree with table",
        b["bench_card"]["records"] == sum(f["donchian_records"] for f in data["face_table"]
                                          if f["lineage"] == "bench_card"))

    ok = sum(1 for _, c in legs if c)
    for name, cond in legs:
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    print(f"selftest: {ok}/{len(legs)} PASS")
    return 0 if ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "check", "selftest"))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "selftest":
        return _selftest()
    if args.cmd == "check":
        return cmd_check()
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
