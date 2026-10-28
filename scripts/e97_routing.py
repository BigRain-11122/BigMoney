"""E97 — screened-consumer routing table.

E94 (`results/e79/triage-20261026.json`) named the 25 census modes whose published
numbers still come off a repaired print.  E109 then fixed the repair factor on the 14
legs that join a screened arm *themselves*.  What was never published is the routing
question: for each charged mode, is there a screened twin face on disk at all, and if
not, how big is the untouched number it publishes?

This leg answers that from three machine-readable sources and nothing else:

  A. the E94 triage face    -> which modes are charged (and which face each one publishes)
  B. the census source      -> which twin leg CALLS which base leg (`run_screenX -> run_Y`)
  C. the twin faces on disk -> the newest screened face per twin leg

Coverage is therefore a code-graph fact, not a column-name guess.  The column-overlap
signal is also measured, but it is published as an explicitly NON-DECISIVE annotation:
generic metric names (`ann_return_pct`, `sharpe`, `max_drawdown_pct`) make four
unrelated twins match a face at ratio 1.00, so a column test alone would route work to
the wrong leg.  That collision is reported, not hidden.

Usage:
    python scripts/e97_routing.py run [--publish]
    python scripts/e97_routing.py selftest
"""
from __future__ import annotations

import glob
import io
import json
import os
import re
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRIAGE = "results/e79/triage-20261026.json"
CENSUS = "scripts/e39_panel_census.py"
OUT_DIR = "results/e79"

# Twin legs: the function in the census source that rebuilds a base face on screened
# arms, plus the face glob it writes.  Declared from the faces themselves: every glob
# below selects a face whose study name starts with the digest family that built it.
TWIN_FUNCS = {
    "run_screenspread": ("screenspread", "results/e42_spread_size_neutral/NEUTRAL-*-screened.json"),
    "run_screentilt": ("screentilt", "results/e42_tilt_era/TILT-ERA-*-screened.json"),
    "run_calcost_screenreg": ("screencalc", "results/e42_calendar_cost/COST-*-screened.json"),
    "run_screenrob": ("screenrob", "results/e43_neutral_robust/ROBUST-*-screened.json"),
    "run_screenweek": ("screenweek", "results/e44_midmonth/WEEKCLASH-*-screened.json"),
    "run_midscreen": ("midscreen", "results/e44_midmonth/MIDSCREEN-*.json"),
    "run_screenwide": ("screenwide", "results/e44_midmonth/SCREENWIDE-*.json"),
    "run_screengapera": ("screengapera", "results/e44_midmonth/SCREENGAPERA-*.json"),
    "run_screenreg": ("screenreg", "results/e44_midmonth/SCREENREG-*.json"),
    # E112-E115 twins. They were built before they were registered, so the first
    # three routing faces called their runners uncovered while a screened twin
    # for each sat on disk: the coverage question only sees what is declared
    # here, and a twin that is not declared is not a twin as far as this table
    # is concerned.
    "run_burninscreen": ("burninscreen", "results/e44_burnin/BURNINSCREEN-*.json"),
    "run_cutcurvescreen": ("cutcurvescreen", "results/e44_burnin/CUTCURVESCREEN-*.json"),
    "run_livespanscreen": ("livespanscreen", "results/e44_burnin/LIVESPANSCREEN-*.json"),
    "run_chasescreen": ("chasescreen", "results/e44_midmonth/CHASESCREEN-*.json"),
    "run_earlydelayscreen": ("earlydelayscreen",
                             "results/e44_midmonth/EARLYDELAYSCREEN-*.json"),
    # E117: the one twin whose subject IS the repair -- run_panelsplit censuses
    # the prints panel_screen edits, so here a moved count is the repair working.
    "run_panelsplitscreen": ("panelsplitscreen",
                             "results/e44_midmonth/PANELSPLITSCREEN-*.json"),
    # E118: the last of the mid-month E7x family. Its published numbers already
    # exclude >30% single-session jumps, so this twin tests the GUARD rather
    # than the panel: a repair that only moves the unguarded columns means the
    # two screens agree on which prints are impossible.
    "run_staletailscreen": ("staletailscreen",
                            "results/e44_midmonth/STALETAILSCREEN-*.json"),
    # E119/E120: the registry-as-range pit recurred a third time. r1190 burned
    # run_entrydelayscreen and did not declare it, so the routing face still
    # called run_entrydelay uncovered while its twin sat on disk. L15 was red at
    # the open of r1191 -- the leg did its job; both twins are declared here.
    "run_entrydelayscreen": ("entrydelayscreen",
                             "results/e44_midmonth/ENTRYDELAYSCREEN-*.json"),
    "run_neighborhoodscreen": ("neighborhoodscreen",
                               "results/e44_midmonth/NEIGHBORHOODSCREEN-*.json"),
    "run_rebaldayscreen": ("rebaldayscreen",
                           "results/e44_midmonth/REBALDAYSCREEN-*.json"),
    # E122 (r1194): the warm-spread ordering twin. Declared in the same window it
    # was built -- r1190/r1191 burned two twins before registering them and turned
    # L15 red, so the registration is part of the leg's definition now.
    "run_warmspreadscreened": ("warmspreadscreened",
                               "results/e45_warm_spread/WARMSPREADSCREEN-*.json"),
    # E123 (r1196): the ladder-vs-wide drawdown-shape twin.
    "run_pairscreened": ("pairscreened",
                         "results/e40_pair_drawdown/PAIRSCREEN-*.json"),
    # E124 (r1197): the per-era four-member tilt attribution twin.
    "run_tilt4screened": ("tilt4screened",
                          "results/e43_tilt_4member/TILT4SCREEN-*.json"),
    # E125 (r1198): the cash-leg drag twin -- the last uncovered runner. Its
    # subject is the un-invested weight, so the join carries the mechanism
    # (first invested bar) beside the earned numbers.
    "run_cashdragscreened": ("cashdragscreened",
                             "results/e40_cashleg_drag/CASHLegSCREEN-*.json"),
    # E171 (r1206): validated-twin family, declared in the window it was built.
    # Its subject is a FACE split by column (tilt_* invariant by E170, engine_*
    # not), so the twin's value is the per-column attribution, not a move count.
    "run_tilt3screensign": ("tilt3screensign",
                            "results/e43_tilt_4member/TILT3SCREENSIGN-*.json"),
    # E170 (r1205) was burned with its twin function undeclared, so L15 was red
    # at the open of this round and the routing table called run_tilt3reach
    # uncovered while TILT3SCREEN-20261027.json sat on disk -- the fourth
    # recurrence of the registry-as-range pit this leg exists to catch.
    "run_tilt3screened": ("tilt3screened",
                          "results/e43_tilt_4member/TILT3SCREEN-*.json"),
    # E174 (r1208): name-level carrier of E171's engine-column move. Declared
    # with the leg, not after L15 goes red -- the E170 lesson re-applied.
    "run_tilt3signnames": ("tilt3signnames",
                           "results/e43_tilt_4member/TILT3SIGNNAMES-*.json"),
    # E175 (r1209): the drop ladder E174's two points were sampled from.
    "run_tilt3signdropsweep": ("tilt3signdropsweep",
                               "results/e43_tilt_4member/TILT3SIGNDROPSWEEP-*.json"),
}

COLUMN_KEYS = ("column", "metric", "name", "label")


def _abs(rel: str) -> str:
    return rel if os.path.isabs(rel) else os.path.join(ROOT, rel)


def load_json(path: str):
    with io.open(_abs(path), encoding="utf-8") as fh:
        return json.load(fh)


def numeric_leaves(obj, out=None, path=""):
    """Collect (leaf-name, value) for every numeric leaf of a JSON tree."""
    if out is None:
        out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            numeric_leaves(v, out, path + "/" + str(k))
    elif isinstance(obj, list):
        for v in obj:
            numeric_leaves(v, out, path)
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        out.append((path.split("/")[-1], obj))
    return out


def call_graph(source: str):
    """name -> set of run_* functions called in its body (one level, source order)."""
    starts = [(m.group(1), m.start()) for m in re.finditer(r"^def (\w+)\(", source, re.M)]
    graph = {}
    for i, (name, start) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else len(source)
        body = source[start:end]
        graph[name] = set(re.findall(r"\b(run_\w+)\b", body)) - {name}
    return graph


def twin_columns(face: dict):
    """Column names a twin face publishes in its delta tables."""
    cols = set()
    for key in ("delta", "arms", "faces", "delta_table", "delta_rows"):
        rows = face.get(key)
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, dict):
                    for ck in COLUMN_KEYS:
                        if isinstance(row.get(ck), str):
                            cols.add(row[ck])
    return cols


def newest_face(pattern: str):
    files = sorted(glob.glob(_abs(pattern)))
    if not files:
        return None
    return os.path.relpath(files[-1], ROOT).replace("\\", "/")


def _stem(path: str) -> str:
    base = os.path.basename(path or "")
    return re.split(r"[-.]", base)[0].upper()


def _common_root(a: str, b: str, minimum: int = 4) -> str:
    """Longest common filename root, e.g. WEEKLYCLASH / WEEKCLASH -> 'WEEK'."""
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    root = a[:n]
    return root if len(root) >= minimum else ""


def build(root=None, triage=None, census=None):
    """Classify each charged mode.  Root/inputs are injectable for the selftest."""
    global ROOT
    root = root or ROOT
    ROOT = root
    triage = triage if triage is not None else TRIAGE
    census = census if census is not None else CENSUS

    with io.open(_abs(census), encoding="utf-8") as fh:
        source = fh.read()
    graph = call_graph(source)

    twins = []
    for func, (leg, pattern) in TWIN_FUNCS.items():
        face_rel = newest_face(pattern)
        body = ""
        starts = [(m.group(1), m.start()) for m in re.finditer(r"^def (\w+)\(", source, re.M)]
        for i, (nm, st) in enumerate(starts):
            if nm == func:
                body = source[st:starts[i + 1][1] if i + 1 < len(starts) else len(source)]
                break
        twins.append({
            "leg": leg,
            "func": func,
            "face": face_rel,
            "stem": _stem(face_rel),
            "calls": sorted(graph.get(func, set())),
            "body": body.lower(),
            "columns": twin_columns(load_json(face_rel)) if face_rel else [],
        })
    twin_by_func = {t["func"]: t for t in twins}

    tri = load_json(triage)
    charged = [r for r in tri["rows"] if r.get("charged_by_repair")]

    rows = []
    for r in charged:
        face_rel = (r.get("evidence") or {}).get("face_on_disk")
        cells = 0
        leaf_names = set()
        if face_rel and os.path.exists(_abs(face_rel)):
            leaves = numeric_leaves(load_json(face_rel))
            cells = len(leaves)
            leaf_names = set(n for n, _ in leaves)
        runner = r["runner"]

        # (1) code-graph coverage: a twin leg that calls this mode's runner
        code_links = sorted(t["leg"] for t in twins if runner in t["calls"] and t["face"])
        # (1b) weaker code channel: the twin rebuilds the face itself (shared filename
        # root of >=4 chars, and that root appears >=3 times in the twin's own body).
        # Catches run_screenweek, which builds the weekly faces from its own code and
        # only borrows run_midsweep for decision sets.
        name_links = []
        for t in twins:
            if not t["face"] or not face_rel:
                continue
            root = _common_root(_stem(face_rel), t["stem"])
            if root and t["body"].count(root.lower()) >= 3 and t["leg"] not in code_links:
                name_links.append({"leg": t["leg"], "root": root,
                                   "body_mentions": t["body"].count(root.lower())})
        # (2) non-decisive column overlap (generic metric names collide)
        overlaps = []
        for t in twins:
            if not t["columns"] or not leaf_names:
                continue
            inter = leaf_names & set(t["columns"])
            ratio = len(inter) / float(len(t["columns"]))
            if ratio >= 0.8 and len(inter) >= 3:
                overlaps.append({"leg": t["leg"], "ratio": round(ratio, 3),
                                 "shared": len(inter), "columns": sorted(inter)[:4]})
        overlaps.sort(key=lambda x: (-x["ratio"], -x["shared"]))

        if code_links:
            state = "covered_twin"
        elif name_links:
            state = "covered_twin_by_name"
        elif overlaps:
            state = "uncovered_column_only"
        else:
            state = "uncovered"

        rows.append({
            "mode": r["mode"],
            "runner": runner,
            "face": face_rel,
            "published_cells": cells,
            "coverage": state,
            "twin_legs": code_links,
            "twin_by_name": name_links,
            "column_overlap_only": overlaps[:2],
            "read_set": r.get("read_set"),
        })

    uncovered = [x for x in rows if not x["coverage"].startswith("covered_twin")]
    uncovered.sort(key=lambda x: (-x["published_cells"], x["mode"]))

    # group uncovered rows by runner: modes sharing a runner share one burn
    groups = {}
    for x in uncovered:
        groups.setdefault(x["runner"], {"runner": x["runner"], "modes": [],
                                        "published_cells_dedup": 0, "faces": []})
        g = groups[x["runner"]]
        g["modes"].append(x["mode"])
        if x["face"] and x["face"] not in g["faces"]:
            g["faces"].append(x["face"])
            g["published_cells_dedup"] += x["published_cells"]
    group_rows = sorted(groups.values(), key=lambda g: -g["published_cells_dedup"])

    totals = {
        "charged_modes": len(rows),
        "covered_by_twin": sum(1 for x in rows if x["coverage"] == "covered_twin"),
        "covered_twin_by_name": sum(1 for x in rows if x["coverage"] == "covered_twin_by_name"),
        "uncovered": len(uncovered),
        "uncovered_column_only": sum(1 for x in rows if x["coverage"] == "uncovered_column_only"),
        "uncovered_distinct_runners": len(groups),
        "cells_unchanged_by_any_twin": sum(
            x["published_cells"] for x in uncovered
            if x["mode"] == next(m for m in groups[x["runner"]]["modes"])),
    }

    return {
        "study": "e97_screened_consumer_routing",
        "evidence_cutoff": tri.get("evidence_cutoff"),
        "spec": {
            "inputs": [triage, census],
            "twin_legs": [{k: t[k] for k in ("leg", "func", "face", "calls")} for t in twins],
            "coverage_rule": (
                "covered_twin = a twin leg's body calls this mode's runner AND that twin's "
                "screened face exists on disk; coverage is a code-graph fact, not a column match"
            ),
            "coverage_rule_weak": (
                "covered_twin_by_name = the twin rebuilds the face in its own code: mode face "
                "stem and twin face stem share a >=4-char root and that root appears >=3 times "
                "in the twin function body"
            ),
            "uncovered_column_only": (
                "row has no code link but >=80% of some twin's delta columns (>=3 shared) "
                "appear in its face; the column test is NON-DECISIVE and is never counted as coverage"
            ),
            "published_cells": "numeric leaves of the mode's own published face",
        },
        "rows": rows,
        "ranking_uncovered_by_runner": group_rows,
        "ranking_uncovered_by_mode": [
            {"mode": x["mode"], "runner": x["runner"], "published_cells": x["published_cells"],
             "coverage": x["coverage"], "twin_legs": x["twin_legs"]} for x in uncovered
        ],
        "totals": totals,
        "honest": [
            "covered_twin means a screened twin face exists for the mode's runner; it does NOT "
            "mean the mode's own published face was re-derived, so the numbers a reader opens "
            "are still the unscreened ones until the face itself is re-burned",
            "covered_twin_by_name is the weaker of the two code channels: the twin builds the "
            "face in its own body instead of calling the base runner (run_screenweek borrows "
            "run_midsweep for decision sets only), so read it as 'the twin exists' and not as "
            "'the same function burned it'",
            "the column-overlap channel is published because it was measured, not because it "
            "routes work: generic metric names (ann_return_pct/sharpe/max_drawdown_pct) make "
            "unrelated twins match a face at ratio 1.00",
            "published_cells counts numeric leaves in the mode's face; it measures how much "
            "number surface a re-burn would touch, not how much of it the repair would move "
            "(E94/E109 carry the move counts)",
            "modes sharing a runner share one burn, so the runner-level ranking is the "
            "actionable one; the mode-level ranking double-counts shared faces",
        ],
        "law_ref": "O-20261002-2100 capture law (new method -> methodology card)",
    }


# ------------------------------------------------------- E127 screen reach

# The five names every ladder row is built from.  They are a constant here because the
# ledger's whole point is the INTERSECTION of a face's neutralised names with them, and a
# constant that drifted with a face would make two rows answer different questions.
LADDER_NAMES = ("sh510050", "sh510300", "sh510500", "sh512100", "sh588000")
LEDGER_OUT_DIR = "results/e79"
# Ordering bands.  They are conventions, so they are published beside the numbers: a
# reader who disagrees with 1.25 can re-band the table from the ratio column.
REPAIR_DOMINATES_AT = 1.25
REFRESH_DOMINATES_AT = 0.8


def _screen_block(doc):
    """(primary screen report of a face, where it was found).  (None, None) when absent."""
    single = doc.get("screen_report")
    if isinstance(single, dict):
        return single, "screen_report"
    plural = doc.get("screen_reports")
    if isinstance(plural, dict) and plural:
        spec = doc.get("spec") if isinstance(doc.get("spec"), dict) else {}
        mode = spec.get("screen_mode") or "neutralise_int"
        if isinstance(plural.get(mode), dict):
            return plural[mode], "screen_reports[%s]" % mode
        key = next(k for k, v in plural.items() if isinstance(v, dict))
        return plural[key], "screen_reports[%s]" % key
    return None, None


def _nonzero_delta_rows(rows):
    """Rows whose repair delta is non-zero -- the third repair channel, used only when a
    face publishes neither a pair block nor a non_zero_delta_cells count."""
    if not isinstance(rows, list):
        return None
    moved = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        for k, v in row.items():
            if k.startswith("delta") and isinstance(v, (int, float)) and not isinstance(v, bool) \
                    and v != 0:
                moved += 1
                break
    return moved


def _ordering(repair, refresh):
    """Classify repair vs refresh.  Both numbers are published beside this label."""
    if refresh is None:
        return "no_cutoff_control"
    if repair is None:
        return "no_repair_count"
    if refresh == 0:
        return "refresh_zero"
    ratio = float(repair) / float(refresh)
    if ratio >= REPAIR_DOMINATES_AT:
        return "repair_dominates"
    if ratio <= REFRESH_DOMINATES_AT:
        return "refresh_dominates"
    return "tied"


def _repair_count(doc):
    """(cells the repair moved, cells compared, channel).  Three declared channels."""
    pair = doc.get("pair") if isinstance(doc.get("pair"), dict) else {}
    psum = pair.get("summary") if isinstance(pair.get("summary"), dict) else {}
    if psum.get("cells_moved") is not None:
        return psum.get("cells_moved"), psum.get("cells_compared"), "pair.summary"
    ans = doc.get("answers") if isinstance(doc.get("answers"), dict) else {}
    if ans.get("non_zero_delta_cells") is not None:
        return (ans.get("non_zero_delta_cells"), ans.get("delta_cells"),
                "answers.non_zero_delta_cells")
    for key in ("delta", "delta_table"):
        rows = doc.get(key)
        moved = _nonzero_delta_rows(rows)
        if moved is not None and isinstance(rows, list) and rows:
            return moved, len(rows), "%s[non-zero delta rows]" % key
    return None, None, None


def ledger_row(rel, doc, declared_leg=None):
    """One face -> one ledger row.  Returns None only when the file is not a screen face."""
    block, block_src = _screen_block(doc)
    repair, compared, repair_src = _repair_count(doc)
    cc = doc.get("cutoff_control") if isinstance(doc.get("cutoff_control"), dict) else None
    refresh, refresh_compared = None, None
    if cc:
        cs = cc.get("summary") if isinstance(cc.get("summary"), dict) else {}
        refresh = cs.get("cells_moved")
        refresh_compared = cs.get("cells_compared")
    if block is None and repair is None and refresh is None:
        return None

    screen = None
    ladder_hits = []
    if isinstance(block, dict):
        names = [n for n in (block.get("names") or []) if isinstance(n, dict)]
        neutralised = sorted(n.get("name") for n in names
                             if n.get("action") == "neutralise" and n.get("name"))
        ladder_hits = [n for n in neutralised if n in LADDER_NAMES]
        screen = {
            "mode": block.get("mode"),
            "source_key": block_src,
            "names_in": block.get("names_in"),
            "names_out": block.get("names_out"),
            "names_touched": block.get("names_touched"),
            "names_neutralised": len(neutralised),
            "ladder_names_neutralised": ladder_hits,
            "ladder_row_is_a_control": not ladder_hits,
        }

    ratio = None
    if isinstance(repair, (int, float)) and isinstance(refresh, (int, float)) and refresh:
        ratio = round(float(repair) / float(refresh), 3)

    exposure = doc.get("ladder_exposure")
    exposure = exposure if isinstance(exposure, dict) else None
    claimed_control = exposure.get("ladder_row_is_a_control") if exposure else None

    flags = []
    if screen is None:
        flags.append("no_screen_census")
    if refresh is None:
        flags.append("no_cutoff_control")
    if repair is None:
        flags.append("no_repair_count")
    if ladder_hits:
        flags.append("ladder_name_neutralised")
    if screen is not None and not exposure:
        flags.append("ladder_control_claim_unpublished")
    if declared_leg is None:
        flags.append("not_a_declared_twin")
    if exposure and claimed_control and ladder_hits:
        flags.append("ladder_claim_contradicted")
    # A moved-count ratio is only an ordering when both counts are over the SAME cells.
    # The neighbourhood twin compares 163 repair cells against 9 shared refresh cells, so
    # 90/3 = 30x is a denominator artefact, not a 30x repair.
    if isinstance(compared, int) and isinstance(refresh_compared, int) \
            and compared != refresh_compared:
        flags.append("denominators_differ")

    return {
        "face": rel,
        "study": doc.get("study"),
        "evidence_cutoff": doc.get("evidence_cutoff"),
        "generation": "twin" if (doc.get("pair") or cc) else "sweep",
        "declared_twin_leg": declared_leg,
        "screen": screen,
        "publishes_ladder_exposure": bool(exposure),
        "ladder_control_claimed": claimed_control,
        "repair": {"cells_moved": repair, "cells_compared": compared, "source": repair_src},
        "refresh": {"cells_moved": refresh,
                    "cells_compared": refresh_compared,
                    "old_face": (cc or {}).get("old_face"),
                    "source": "cutoff_control.summary" if refresh is not None else None},
        "ordering": _ordering(repair, refresh),
        "repair_over_refresh_ratio": ratio,
        "flags": flags,
    }


def screen_reach_ledger(root=None):
    """Every published screened face -> the three facts a reader of ONE face cannot see."""
    global ROOT
    saved = ROOT
    root = root or ROOT
    ROOT = root
    try:
        declared = {}
        for _func, (leg, pattern) in TWIN_FUNCS.items():
            face = newest_face(pattern)
            if face:
                declared[face] = leg
        rows, skipped = [], []
        for path in sorted(glob.glob(os.path.join(root, "results", "**", "*.json"),
                                     recursive=True)):
            rel = os.path.relpath(path, root).replace("\\", "/")
            base = os.path.basename(rel).upper()
            if "SCREEN" not in base and not base.endswith("-SCREENED.JSON"):
                continue
            if any(part in rel for part in ("_quarantine", "sync_backup", "pool_claims")):
                continue
            try:
                doc = load_json(path)
            except Exception:  # noqa: BLE001 - a half-written face must not kill the scan
                skipped.append({"face": rel, "reason": "unreadable"})
                continue
            if not isinstance(doc, dict):
                continue
            row = ledger_row(rel, doc, declared.get(rel))
            if row is None:
                skipped.append({"face": rel, "reason": "not_a_screen_face"})
                continue
            rows.append(row)
        missing_declared = [f for f in declared if f not in {r["face"] for r in rows}]
    finally:
        ROOT = saved

    rows.sort(key=lambda r: (r["generation"], r["face"]))
    cutoffs = sorted(r["evidence_cutoff"] for r in rows if r.get("evidence_cutoff"))

    ord_counts = {}
    matched_counts = {}
    for r in rows:
        ord_counts[r["ordering"]] = ord_counts.get(r["ordering"], 0) + 1
        if r["ordering"] not in ("no_cutoff_control", "no_repair_count") \
                and "denominators_differ" not in r["flags"]:
            matched_counts[r["ordering"]] = matched_counts.get(r["ordering"], 0) + 1

    twins = [r for r in rows if r["generation"] == "twin"]
    both = [r for r in rows if r["repair"]["cells_moved"] is not None
            and r["refresh"]["cells_moved"] is not None]
    census = [r for r in rows if r["screen"] is not None]
    no_cc = [r["face"] for r in rows if "no_cutoff_control" in r["flags"]]
    no_census = [r["face"] for r in rows if r["screen"] is None]
    controls = [r["face"] for r in census if r["screen"]["ladder_row_is_a_control"]]
    ladder_burned = [r["face"] for r in census if r["screen"]["ladder_names_neutralised"]]
    exposure = [r["face"] for r in rows if r["publishes_ladder_exposure"]]
    flagged = [r["face"] for r in rows if "not_a_declared_twin" in r["flags"]]

    totals = {
        "faces_total": len(rows),
        "twins": len(twins),
        "sweeps": len(rows) - len(twins),
        "faces_with_screen_census": len(census),
        "faces_without_screen_census": len(no_census),
        "faces_with_both_numbers": len(both),
        "faces_without_cutoff_control": len(no_cc),
        "faces_without_repair_count": sum(1 for r in rows
                                          if r["repair"]["cells_moved"] is None),
        "faces_with_mismatched_denominators": sum(
            1 for r in rows if "denominators_differ" in r["flags"]),
        "faces_where_ladder_rows_are_controls": len(controls),
        "faces_that_neutralise_a_ladder_name": len(ladder_burned),
        "faces_publishing_ladder_exposure": len(exposure),
        "faces_not_a_declared_twin": len(flagged),
        "declared_twins_missing_from_ledger": len(missing_declared),
        "ordering_counts": ord_counts,
        "orderings_on_matched_denominators": matched_counts,
        "repair_cells_total": sum(r["repair"]["cells_moved"] or 0 for r in rows),
        "refresh_cells_total": sum(r["refresh"]["cells_moved"] or 0 for r in rows),
        "skipped": len(skipped),
    }

    answers = {
        "ladder_rows_are_controls_where_a_census_exists": len(controls) == len(census),
        "faces_publishing_the_ladder_control_fact": exposure,
        "faces_where_ladder_rows_are_controls": controls,
        "faces_neutralising_a_ladder_name": ladder_burned,
        "faces_without_a_screen_census": no_census,
        "ordering_counts": ord_counts,
        "orderings_on_matched_denominators": matched_counts,
        "faces_with_mismatched_denominators": [
            r["face"] for r in rows if "denominators_differ" in r["flags"]],
        "faces_without_cutoff_control": no_cc,
        "faces_not_a_declared_twin": flagged,
        "declared_twins_missing_from_ledger": missing_declared,
        "repair_cells_total": totals["repair_cells_total"],
        "refresh_cells_total": totals["refresh_cells_total"],
        "reading": (
            "%d screened files carry ledger content (%d skipped: not screen faces). %d rows are "
            "declared twin faces, %d are earlier sweeps. %d rows carry BOTH the repair count and "
            "the refresh count (%s); %d of those %d compare DIFFERENT cell sets, so their ratio "
            "is not an ordering, and on matched denominators the labels read %s. %d rows carry no "
            "cutoff control at all, so a repair read off those faces can never be ranked against "
            "data refresh. A screen census exists on %d of %d rows; on every one of those the "
            "ladder rows are controls (%d neutralise a ladder name), yet only %d row publishes "
            "that fact."
            % (len(rows), len(skipped), len(twins), len(rows) - len(twins), len(both),
               ", ".join(k + "=" + str(v) for k, v in sorted(ord_counts.items())),
               sum(1 for r in rows if "denominators_differ" in r["flags"]), len(both),
               ", ".join(k + "=" + str(v) for k, v in sorted(matched_counts.items())),
               len(no_cc), len(census), len(rows), len(ladder_burned), len(exposure))),
    }

    return {
        "study": "e127_screen_reach_ledger",
        "evidence_cutoff": cutoffs[-1] if cutoffs else None,
        "spec": {
            "faces": "every results/**/*SCREEN*.json (or *-screened.json) that carries a screen "
                     "census, a repair count or a cutoff control; declared = the newest face of "
                     "a TWIN_FUNCS glob",
            "ladder_names": list(LADDER_NAMES),
            "names_neutralised": "screen_report.names entries whose action == 'neutralise'",
            "ladder_row_is_a_control": "no ladder name appears in that neutralised set; null "
                                       "when the face publishes no census (unknown, not true)",
            "repair": "pair.summary.cells_moved, else answers.non_zero_delta_cells, else the "
                      "count of non-zero delta rows in delta / delta_table",
            "refresh": "cutoff_control.summary.cells_moved; absent means the face cannot rank "
                       "the two effects at all",
            "ordering_bands": {
                "repair_dominates": "repair / refresh >= %.2f" % REPAIR_DOMINATES_AT,
                "refresh_dominates": "repair / refresh <= %.2f" % REFRESH_DOMINATES_AT,
                "tied": "between the bands; neither number may be quoted alone",
                "refresh_zero": "cutoff_control moved 0 cells, the ratio is undefined",
                "no_cutoff_control": "flag, not a verdict",
            },
        },
        "rows": rows,
        "totals": totals,
        "answers": answers,
        "skipped": skipped,
        "honest": [
            "faces_total counts faces, not burns: a face is a FILE, and two files of one leg "
            "at two cutoffs are two rows",
            "names_in differs between the generations (1271 on the sweeps, 1317 on the twins) "
            "because the panel grew, so a neutralised COUNT is not comparable across "
            "generations -- the ladder intersection is",
            "the sweep generation carries no cutoff control, so its repair column sits beside a "
            "null refresh: that is a defect of the face, not a finding about the repair",
            "the repair channel is declared per row; a row whose count comes from counting "
            "non-zero delta rows is not the same measurement as a twin's pair.summary",
            "ladder_row_is_a_control is derived from the face's own neutralised set, "
            "cross-checked against the face's own claim where one exists, and left null where "
            "no census exists -- a contradiction is flagged, never resolved",
            "not_a_declared_twin is an annotation, not an indictment: the gap-limit and "
            "screen-registration faces census prints without being a twin of any runner",
            "ordering bands are conventions (1.25 / 0.8); the ratio column is published so a "
            "reader can re-band the table without re-burning it",
        ],
        "law_ref": "O-20261002-2100 capture law (new method -> methodology card)",
    }

def run_screenreach(publish=False):
    face = screen_reach_ledger()
    if publish:
        out = os.path.join(_abs(LEDGER_OUT_DIR),
                           "SCREENREACH-%s.json" % (face["evidence_cutoff"] or "unknown"))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(face, ensure_ascii=False, indent=1) + "\n")
        print("wrote", os.path.relpath(out, ROOT).replace("\\", "/"))
    t = face["totals"]
    print("faces=%d twins=%d sweeps=%d both_numbers=%d no_cutoff=%d ladder_controls=%d/%d "
          "exposure_published=%d not_a_twin=%d no_census=%d" % (
              t["faces_total"], t["twins"], t["sweeps"], t["faces_with_both_numbers"],
              t["faces_without_cutoff_control"], t["faces_where_ladder_rows_are_controls"],
              t["faces_total"], t["faces_publishing_ladder_exposure"],
              t["faces_not_a_declared_twin"], t["faces_without_screen_census"]))
    for k in sorted(t["ordering_counts"]):
        print("  ordering %-18s %d" % (k, t["ordering_counts"][k]))
    return 0


# --------------------------------------------------------------------------- E180
# Published-level quote audit.  E177 measured that a decomposition level (a sum of
# daily w*r terms) and a book level (each book compounded on its own) are different
# objects, and that their gap is book-specific.  What nobody audited is which of the
# numbers the family already PUBLISHES are of which kind: a reader quoting
# `engine_mean_ann_bp` is quoting a book level, while a reader quoting
# `decomposition_engine_bp` is quoting an arithmetic sum whose offset sits somewhere
# else (or nowhere).  This leg classifies every level-shaped cell in the two
# directories the pool row names, joins each derived cell to E177's published offset,
# and reports the faces that quote a derived level with no offset beside it.

LEVELQUOTE_DIRS = ("results/e43_tilt_4member", "results/e79")
DECOMOFFSET_GLOB = "results/e43_tilt_4member/TILT3SIGNDECOMOFFSET-*.json"
LEVELQUOTE_OUT_DIR = "results/e79"
# This leg publishes into a directory it scans, so its own face must be excluded or
# the audit would count itself (r1215: 25 -> 26 faces, 1034 -> 3274 cells by
# self-inclusion, and the extra face has no producer so the live leg went red).
LEVELQUOTE_EXCLUDE_STUDIES = ("e180_published_level_quote_audit",
                              "e188_decomposition_label_duty",
                              "e193_decomposition_delta_build_stance",
                              "e196_tilt3_nearzero_sign_census")

# E177's own reading vocabulary, turned into name rules.  Order matters: a gap cell
# named `arithmetic_vs_geometric_gap_bp` carries both vocabularies, and it is a gap.
GAP_TOKENS = ("offset", "gap")
DERIVED_TOKENS = ("decomposition", "arithmetic", "unanchored")
ARITH_OF_LEVELS_TOKENS = ("legs_sum",)
# Offsets that are the SAME construct as E177's published offset, keyed by the field
# name and mapped to the E177 column it may be compared against.  Everything else that
# carries an offset name is inventoried but never differenced: `offset_left_as_cross_
# term_bp` and `arithmetic_vs_geometric_gap_bp` are decompositions OF an offset, so a
# diff against the offset itself would be a comparison between a part and a whole.
COMPARABLE_OFFSETS = {
    "level_offset_bp": "engine_level_offset_bp",
    "engine_level_offset_bp": "engine_level_offset_bp",
    "wide_book_level_offset_bp": "wide_book_level_offset_bp",
    "ladder_book_level_offset_bp": "ladder_book_level_offset_bp",
    "raw_offset_bp": "engine_level_offset_bp",
    "screened_offset_bp": "engine_level_offset_bp",
}
NON_LEVEL_TOKENS = ("delta", "diff", "sd", "tolerance", "share", "pct", "deadband",
                    "sign", "change", "heap", "join", "months", "residual", "count",
                    "beta", "r_squared", "corr", "stability", "abs", "quantum",
                    "band", "cutoff", "yield")
# Two level cells whose names carry a level word but a non-level token.  Declared
# rather than pattern-engineered: `engine_ann_diff_bp` is the engine LEVEL (wide minus
# ladder) and only its name says "difference".
LEVEL_OVERRIDES = {"engine_ann_diff_bp": "anchored"}

ERA_RE = re.compile(r"^(pre2017|2017_2020|2021_2023|2024_now|full)$")
ARM_RE = re.compile(r"(?:^|_)(raw|screened|neutralise_int)(?:$|_)")
ARITH_TOKENS = ("_daily_rets", "_month_daily_rets", "_tilt3decom_blocks")


def level_class(leaf):
    """ANCHORED book level / DERIVED daily-term sum / arithmetic-of-levels / offset."""
    name = (leaf or "").lower()
    if name in LEVEL_OVERRIDES:
        return LEVEL_OVERRIDES[name]
    if any(t in name for t in GAP_TOKENS):
        return "offset"
    if any(t in name for t in DERIVED_TOKENS):
        return "derived_daily"
    if any(t in name for t in ARITH_OF_LEVELS_TOKENS):
        return "arithmetic_of_levels"
    if any(t in name for t in NON_LEVEL_TOKENS):
        return None
    if "bp" in name or "level" in name:
        return "anchored"
    return None


def walk_numeric(obj, path=""):
    """(json-path, value) for every numeric leaf, in document order."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            for item in walk_numeric(v, path + "/" + str(k)):
                yield item
    elif isinstance(obj, list):
        for v in obj:
            for item in walk_numeric(v, path):
                yield item
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        yield path, obj


def _base_name(leaf):
    """Leaf name with its arm token stripped: `decomposition_engine_bp_raw` and
    `decomposition_engine_bp` are the same label to a reader."""
    name = (leaf or "").lower()
    name = re.sub(r"^(raw|screened|neutralise_int)_", "", name)
    name = re.sub(r"_(raw|screened|neutralise_int)$", "", name)
    return name


def era_arm_of(path):
    """(era, arm) inferred from a cell path; both are None when the path carries none."""
    parts = [p for p in (path or "").split("/") if p]
    era = None
    arm = None
    for part in parts[:-1]:
        if ERA_RE.match(part):
            era = part
        elif "|" in part:
            left, _, right = part.partition("|")
            if ERA_RE.match(right):
                era, arm = right, left
    m = ARM_RE.search(parts[-1] if parts else "")
    if m and arm is None:
        arm = m.group(1)
    return era, arm


def _def_table(source):
    starts = [(m.group(1), m.start()) for m in re.finditer(r"^def (\w+)\(", source, re.M)]
    out = []
    for i, (name, start) in enumerate(starts):
        end = starts[i + 1][1] if i + 1 < len(starts) else len(source)
        out.append((name, start, end))
    return out


def producer_index(source):
    """study literal -> the def(s) whose body contains it."""
    table = _def_table(source)
    index = {}
    for m in re.finditer(r'"(e\d{2,3}_[a-z0-9_]+)"', source):
        owner = None
        for name, start, end in table:
            if start <= m.start() < end:
                owner = name
        if owner:
            index.setdefault(m.group(1), set()).add(owner)
    return {k: sorted(v) for k, v in index.items()}


def producer_reach(source, funcs, tokens=ARITH_TOKENS):
    """Which arithmetic tokens a producer reaches, following the module's own calls."""
    bodies = {name: source[start:end] for name, start, end in _def_table(source)}
    seen, stack = set(), [f for f in funcs if f in bodies]
    while stack:
        fn = stack.pop()
        if fn in seen:
            continue
        seen.add(fn)
        for callee in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\(", bodies[fn]):
            if callee in bodies and callee not in seen:
                stack.append(callee)
    return sorted({t for fn in seen for t in tokens if t in bodies[fn]})


def decomoffset_index(root=None):
    """(arm, era) -> the offsets E177 published for that cell, plus its book levels."""
    root = root or ROOT
    pattern = os.path.join(root, DECOMOFFSET_GLOB)
    files = sorted(glob.glob(pattern))
    if not files:
        return {}, None
    rel = os.path.relpath(files[-1], root).replace("\\", "/")
    try:
        with io.open(files[-1], encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return {}, rel
    index = {}
    for key, row in (doc.get("eras") or {}).items():
        arm, _, era = key.partition("|")
        index[(arm, era)] = {
            "engine_level_offset_bp": row.get("level_offset_bp"),
            "wide_book_level_offset_bp": row.get("wide_book_level_offset_bp"),
            "ladder_book_level_offset_bp": row.get("ladder_book_level_offset_bp"),
            "published_engine_bp": row.get("published_engine_bp"),
            "decomposition_engine_bp": row.get("decomposition_engine_bp"),
        }
    return index, rel


def level_quotes(root=None):
    """Audit every level cell the family publishes: anchored, derived, or offset."""
    global ROOT
    saved = ROOT
    root = root or ROOT
    ROOT = root
    try:
        census_path = os.path.join(root, CENSUS)
        census_src = ""
        if os.path.isfile(census_path):
            with io.open(census_path, encoding="utf-8", errors="replace") as fh:
                census_src = fh.read()
        studies = producer_index(census_src) if census_src else {}
        offsets, offset_face = decomoffset_index(root)

        rows, skipped, cutoffs = [], [], []
        for rel_dir in LEVELQUOTE_DIRS:
            for path in sorted(glob.glob(os.path.join(root, rel_dir, "*.json"))):
                rel = os.path.relpath(path, root).replace("\\", "/")
                try:
                    with io.open(path, encoding="utf-8") as fh:
                        doc = json.load(fh)
                except (OSError, ValueError):
                    skipped.append({"face": rel, "reason": "unreadable"})
                    continue
                if not isinstance(doc, dict):
                    skipped.append({"face": rel, "reason": "not_a_face"})
                    continue
                study = doc.get("study")
                if study in LEVELQUOTE_EXCLUDE_STUDIES:
                    skipped.append({"face": rel, "reason": "this_leg_publishes_here"})
                    continue
                producer = studies.get(study, [])
                reach = producer_reach(census_src, producer) if producer else []
                cells = []
                for cell_path, value in walk_numeric(doc):
                    parts = [p for p in cell_path.split("/") if p]
                    if parts and parts[0] == "spec":
                        continue
                    cls = level_class(parts[-1] if parts else "")
                    if not cls:
                        continue
                    era, arm = era_arm_of(cell_path)
                    cells.append({"path": cell_path, "value": value, "class": cls,
                                  "era": era, "arm": arm})
                counts = {}
                for cell in cells:
                    counts[cell["class"]] = counts.get(cell["class"], 0) + 1
                derived = [c for c in cells
                           if c["class"] in ("derived_daily", "arithmetic_of_levels")]
                own_offsets = [c for c in cells if c["class"] == "offset"]
                if derived and not own_offsets:
                    verdict = "quotes_derived_without_offset"
                elif derived:
                    verdict = "quotes_derived_with_offset"
                elif own_offsets:
                    verdict = "offset_only"
                elif counts.get("anchored"):
                    verdict = "anchored_only"
                else:
                    verdict = "no_level_cells"

                # E177 join: the offset that sits behind each derived cell, plus the
                # face's own offset where it publishes one under a comparable name.
                arith = "daily_terms" if reach else "monthly_terms"
                for cell in derived:
                    cell["arith"] = arith
                joins = []
                for cell in derived:
                    if not cell["era"]:
                        continue
                    key = (cell["arm"] or "raw", cell["era"])
                    ref = offsets.get(key)
                    own = None
                    for cand in own_offsets:
                        if cand["era"] != cell["era"]:
                            continue
                        leaf = cand["path"].split("/")[-1].lower()
                        if "wide_book" in leaf or "ladder_book" in leaf:
                            continue
                        if cand["arm"] and cell["arm"] and cand["arm"] != cell["arm"]:
                            continue
                        own = cand
                        break
                    joins.append({
                        "era": cell["era"],
                        "arm": key[0],
                        "field": cell["path"],
                        "value_bp": cell["value"],
                        "own_offset_bp": own["value"] if own else None,
                        "own_offset_field": own["path"] if own else None,
                        "e177_engine_offset_bp": (ref or {}).get("engine_level_offset_bp"),
                        "diff_own_minus_e177_bp": (
                            round(own["value"] - ref["engine_level_offset_bp"], 4)
                            if own and ref and ref.get("engine_level_offset_bp") is not None
                            else None),
                    })
                # Every offset cell is inventoried; only the ones that are the SAME
                # construct as an E177 column are differenced against it.
                comparisons, uncompared = [], []
                for cand in own_offsets:
                    leaf = cand["path"].split("/")[-1].lower()
                    e177_key = COMPARABLE_OFFSETS.get(leaf)
                    if not e177_key or not cand["era"]:
                        uncompared.append({"field": cand["path"], "value_bp": cand["value"],
                                           "era": cand["era"],
                                           "reason": "not_the_same_construct"})
                        continue
                    ref = offsets.get((cand["arm"] or "raw", cand["era"])) or {}
                    theirs = ref.get(e177_key)
                    comparisons.append({
                        "era": cand["era"],
                        "arm": cand["arm"] or "raw",
                        "field": cand["path"],
                        "value_bp": cand["value"],
                        "e177_field": e177_key,
                        "e177_bp": theirs,
                        "diff_bp": (round(cand["value"] - theirs, 4)
                                    if theirs is not None else None),
                    })
                if doc.get("evidence_cutoff"):
                    cutoffs.append(doc["evidence_cutoff"])
                rows.append({
                    "face": rel,
                    "study": study,
                    "producer": producer,
                    "producer_arith_tokens": reach,
                    "producer_uses_daily_terms": bool(reach),
                    "derived_arith": arith,
                    "cells": counts,
                    "level_cells": len(cells) - len(own_offsets),
                    "derived_cells": derived,
                    "offset_cells": own_offsets,
                    "offset_joins": joins,
                    "offset_comparisons": comparisons,
                    "uncompared_offsets": uncompared,
                    "verdict": verdict,
                })
    finally:
        ROOT = saved

    rows.sort(key=lambda r: r["face"])
    with_cells = [r for r in rows if r["level_cells"] or r["offset_cells"]]
    derived_faces = [r for r in rows if r["derived_cells"]]
    leak = [r["face"] for r in rows if r["verdict"] == "quotes_derived_without_offset"]
    unindexed = [r["face"] for r in with_cells if not r["producer"]]

    # One field NAME, two arithmetics: group every derived-class leaf name by whether
    # its producer reaches the daily terms.  A name published from both sides is a
    # quote a reader cannot resolve -- same label, different object.
    by_name = {}
    for row in derived_faces:
        for cell in row["derived_cells"]:
            leaf = _base_name(cell["path"].split("/")[-1])
            slot = by_name.setdefault(leaf, {"daily_faces": [], "monthly_faces": [],
                                             "classes": set(), "leaf_names": set(),
                                             "values_bp": []})
            side = "daily_faces" if row["producer_uses_daily_terms"] else "monthly_faces"
            if row["face"] not in slot[side]:
                slot[side].append(row["face"])
            slot["classes"].add(cell["class"])
            slot["leaf_names"].add(cell["path"].split("/")[-1])
            slot["values_bp"].append({"face": row["face"], "era": cell["era"],
                                      "arm": cell["arm"], "value_bp": cell["value"],
                                      "arith": cell["arith"]})
    sum_named = {}
    for leaf in sorted(by_name):
        slot = by_name[leaf]
        sum_named[leaf] = {
            "daily_faces": slot["daily_faces"],
            "monthly_faces": slot["monthly_faces"],
            "classes": sorted(slot["classes"]),
            "leaf_names": sorted(slot["leaf_names"]),
            "collision": bool(slot["daily_faces"]) and bool(slot["monthly_faces"]),
            "values_bp": slot["values_bp"],
        }
    collisions = sorted(k for k, v in sum_named.items() if v["collision"])
    # What the collision COSTS: for a name published from both arithmetics, the two
    # values on the same (era, arm) are two different answers to the same question.
    collision_gaps = []
    for leaf in collisions:
        daily, monthly = {}, {}
        for v in sum_named[leaf]["values_bp"]:
            if not v["era"]:
                continue
            (daily if v["arith"] == "daily_terms" else monthly)[(v["era"], v["arm"])] = v
        for key in sorted(set(daily) & set(monthly), key=lambda k: (str(k[0]), str(k[1]))):
            collision_gaps.append({
                "field": leaf,
                "era": key[0],
                "arm": key[1],
                "daily_bp": daily[key]["value_bp"],
                "monthly_bp": monthly[key]["value_bp"],
                "diff_daily_minus_monthly_bp": round(
                    daily[key]["value_bp"] - monthly[key]["value_bp"], 4),
                "daily_face": daily[key]["face"],
                "monthly_face": monthly[key]["face"],
            })

    by_class = {}
    for row in rows:
        for cls, n in row["cells"].items():
            by_class[cls] = by_class.get(cls, 0) + n

    diffs = [c["diff_bp"] for r in rows for c in r["offset_comparisons"]
             if c["diff_bp"] is not None]
    joined = [j for r in rows for j in r["offset_joins"] if j["e177_engine_offset_bp"] is not None]

    totals = {
        "faces_scanned": len(rows),
        "faces_with_level_or_offset_cells": len(with_cells),
        "faces_quoting_a_derived_level": len(derived_faces),
        "faces_publishing_an_offset": sum(1 for r in rows if r["offset_cells"]),
        "faces_quoting_derived_without_offset": len(leak),
        "faces_with_unindexed_producer": len(unindexed),
        "level_cells_total": sum(r["level_cells"] for r in rows),
        "offset_cells_total": sum(len(r["offset_cells"]) for r in rows),
        "cells_by_class": by_class,
        "derived_cells_from_daily_producers": sum(
            len(r["derived_cells"]) for r in rows if r["producer_uses_daily_terms"]),
        "derived_cells_from_monthly_producers": sum(
            len(r["derived_cells"]) for r in rows if not r["producer_uses_daily_terms"]),
        "sum_named_level_collisions": collisions,
        "collision_pairs": len(collision_gaps),
        "max_abs_collision_gap_bp": (
            round(max(abs(g["diff_daily_minus_monthly_bp"]) for g in collision_gaps), 4)
            if collision_gaps else None),
        "collision_gap_spread_bp": (
            round(max(g["diff_daily_minus_monthly_bp"] for g in collision_gaps)
                  - min(g["diff_daily_minus_monthly_bp"] for g in collision_gaps), 4)
            if len(collision_gaps) > 1 else None),
        "collision_gap_verdict": (
            "decomposition-not-a-difference" if not collision_gaps else
            ("definitional_wedge"
             if (max(g["diff_daily_minus_monthly_bp"] for g in collision_gaps)
                 - min(g["diff_daily_minus_monthly_bp"] for g in collision_gaps)) <= 1.0
             else "varies_with_the_data")),
        "derived_cells_joined_to_e177": len(joined),
        "offsets_compared_to_e177": len(diffs),
        "max_abs_offset_diff_bp": round(max(abs(d) for d in diffs), 4) if diffs else None,
        "skipped": len(skipped),
    }

    answers = {
        "faces_quoting_a_derived_level": [r["face"] for r in derived_faces],
        "faces_quoting_derived_without_an_offset_beside_it": leak,
        "field_names_published_from_two_arithmetics": collisions,
        "collision_gap_verdict": totals["collision_gap_verdict"],
        "collision_gap_spread_bp": totals["collision_gap_spread_bp"],
        "every_derived_cell_has_a_published_offset_to_join": bool(joined)
        and len(joined) == sum(len(r["derived_cells"]) for r in rows
                               if any(c["era"] for c in r["derived_cells"])),
        "offsets_disagree_across_faces": len(diffs) > 0 and max(abs(d) for d in diffs) > 0.0,
        "reading": (
            "%d faces carry %d level cells: %s. %d face(s) quote a DERIVED (sum of terms) "
            "level, %d from a producer that reaches the daily returns (%d cells) and %d from a "
            "monthly producer (%d cells); %d of those faces publish an offset beside the sum "
            "and %d do not. %d field name(s) are published from BOTH arithmetics (%s), and on %d "
            "comparable cells the two answers differ by up to %s bp -- the label alone does "
            "not identify the object. %d offset cells are published across "
            "the family; where one is the same construct as an E177 column (%d compared) the "
            "two disagree by up to %s bp -- an offset is a book-specific number, so 'the "
            "compounding gap' as one headline is a category error."
            % (len(with_cells), totals["level_cells_total"],
               ", ".join("%s=%d" % (k, v) for k, v in sorted(by_class.items())),
               len(derived_faces),
               sum(1 for r in derived_faces if r["producer_uses_daily_terms"]),
               totals["derived_cells_from_daily_producers"],
               sum(1 for r in derived_faces if not r["producer_uses_daily_terms"]),
               totals["derived_cells_from_monthly_producers"],
               len(derived_faces) - len(leak), len(leak),
               len(collisions), ", ".join(collisions) or "none",
               totals["collision_pairs"],
               ("%.2f" % totals["max_abs_collision_gap_bp"])
               if totals["max_abs_collision_gap_bp"] is not None else "n/a",
               totals["offset_cells_total"], len(diffs),
               ("%.2f" % totals["max_abs_offset_diff_bp"])
               if totals["max_abs_offset_diff_bp"] is not None else "n/a")),
    }

    return {
        "study": "e180_published_level_quote_audit",
        "evidence_cutoff": max(cutoffs) if cutoffs else None,
        "spec": {
            "dirs": list(LEVELQUOTE_DIRS),
            "producer_source": CENSUS,
            "producer_rule": "the def whose body contains the face's study literal; "
                             "arithmetic class is read from the tokens that def reaches "
                             "through the module's own call graph (%s)" % ", ".join(ARITH_TOKENS),
            "class_rules": {
                "offset": "leaf name contains one of %s" % (GAP_TOKENS,),
                "derived_daily": "contains one of %s -- E177 reading (a), a sum of daily w*r"
                                 % (DERIVED_TOKENS,),
                "arithmetic_of_levels": "contains one of %s -- a sum of LEVELS"
                                        % (ARITH_OF_LEVELS_TOKENS,),
                "anchored": "level-shaped (bp/level in the name) and none of the above",
                "not_a_level": "contains one of the descriptive tokens %s" % (NON_LEVEL_TOKENS,),
            },
            "declared_overrides": dict(LEVEL_OVERRIDES),
            "offset_join": "%s: (arm, era) -> engine/wide/ladder level offsets"
                           % (offset_face or "absent"),
            "spec_subtree_excluded": "cells under /spec/ are declarations, not quotes",
            "units": "bp as published by the producing face",
        },
        "faces": rows,
        "totals": totals,
        "skipped": skipped,
        "answers": answers,
        "cross_check": {
            "sum_named_levels": sum_named,
            "sum_named_level_collisions": collisions,
            "collision_gaps": collision_gaps,
            "faces_without_a_producer_in_the_census_source": unindexed,
            "note": "sum_named_levels groups every derived-class leaf NAME by whether its "
                    "producer reaches the daily-return helpers. A name published from both "
                    "sides is a collision: the same label on two different objects. The second "
                    "list is coverage, not a defect -- those faces were burned by a leg the "
                    "census source does not declare",
        },
        "honest": [
            "the classification is NAME-based, not value-based: a cell is derived because of "
            "how its producer builds it, and the name rules encode E177's vocabulary. A cell "
            "renamed without re-burning this leg would be misread, which is why every cell is "
            "published with its path",
            "derived_arith is per FACE, not per cell: a producer that reaches the daily helpers "
            "may still mix both arithmetics inside one face, so a collision on a shared name is "
            "evidence that two faces disagree, not that one face is internally inconsistent",
            "offset cells are published by their own faces, so 'publishes an offset' says the "
            "number is on the page -- it does not say the offset was subtracted from the quote "
            "the reader sees",
            "only offsets in COMPARABLE_OFFSETS are differenced against E177; the rest are "
            "inventoried with reason 'not_the_same_construct' (a decomposition of an offset is "
            "not the offset)",
            "offsets are BOOK-specific (E177: engine 28.41 / wide -29.33 / ladder -57.74 bp on "
            "pre2017), so the wide/ladder rows are compared to their own E177 columns, never to "
            "the engine column",
            "cells under /spec/ are excluded: a declared tolerance is not a published quote",
            "the E177 join only covers (arm, era) keys that face publishes; a derived cell "
            "without an era is joined to nothing rather than to a guess",
        ],
        "law_ref": "O-20261002-2100 capture law (new method -> methodology card)",
    }


def run_levelquotes(publish=False):
    face = level_quotes()
    if publish:
        out = os.path.join(_abs(LEVELQUOTE_OUT_DIR),
                           "DECOMLEVELQUOTES-%s.json" % (face["evidence_cutoff"] or "unknown"))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(face, ensure_ascii=False, indent=1) + "\n")
        print("wrote", os.path.relpath(out, ROOT).replace("\\", "/"))
    t = face["totals"]
    print("faces=%d with_cells=%d derived_faces=%d offsets=%d leak=%d level_cells=%d "
          "classes=%s" % (t["faces_scanned"], t["faces_with_level_or_offset_cells"],
                          t["faces_quoting_a_derived_level"],
                          t["faces_publishing_an_offset"],
                          t["faces_quoting_derived_without_offset"],
                          t["level_cells_total"],
                          ",".join("%s=%d" % (k, v)
                                   for k, v in sorted(t["cells_by_class"].items()))))
    if t["max_abs_offset_diff_bp"] is not None:
        print("offsets joined to E177: %d compared, max abs diff %.4f bp"
              % (t["offsets_compared_to_e177"], t["max_abs_offset_diff_bp"]))
    for f in face["answers"]["faces_quoting_derived_without_an_offset_beside_it"]:
        print("  LEAK", f)
    for name in face["answers"]["field_names_published_from_two_arithmetics"]:
        print("  COLLISION", name)
    return 0


# --- E188 label duty ---------------------------------------------------------------
# E185 located the E180 wedge as the rebalance fee: the same field NAME
# (`decomposition_engine_bp`) is published from a contrib/sink reading (GROSS of the
# fee) by one face and from a daily/curve reading (NET of it) by another.  A number
# that moves by 1.1-10.9% depending on which face a reader copies it from is only
# quotable if the page says which one.  This leg sweeps the family for those cells,
# classifies each face's OWN label state, and re-states the published offsets under
# the other stance so "the label changes nothing" is measured, not assumed.

LABELDUTY_OUT_DIR = "results/e79"
LABELDUTY_EXCLUDE_STUDIES = ("e180_published_level_quote_audit",
                             "e188_decomposition_label_duty",
                             "e193_decomposition_delta_build_stance")
GROSS_FACE_GLOB = "results/e43_tilt_4member/TILT3SIGNBOOKSPLIT-*.json"
NET_FACE_GLOB = "results/e43_tilt_4member/TILT3SIGNDECOMOFFSET-*.json"
FEE_FACE_GLOB = "results/e79/LEVELWEDGE-*.json"
STANCE_GROSS_TOKENS = ("gross of", "gross_of", "gross")
STANCE_NET_TOKENS = ("net of the fee", "net of", "net_of", "after the fee", "after_fee")
FEE_TEXT_TOKENS = ("fee", "turnover", "rebalance cost")


def _is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _newest_under(base, pattern):
    files = sorted(glob.glob(os.path.join(base, pattern.replace("/", os.sep))))
    return files[-1] if files else None


def _rel(base, path):
    return os.path.relpath(path, base).replace("\\", "/")


def fee_ladder(fee_face):
    """(arm, era) -> rebalance cost term in bp, from the E185 wedge face."""
    out = {}
    for cell in (fee_face.get("eras") or {}).values():
        if not isinstance(cell, dict):
            continue
        era, arm = cell.get("era"), cell.get("arm") or "raw"
        fee = cell.get("rebalance_cost_term_bp")
        if era and _is_num(fee):
            out[(arm, era)] = float(fee)
    return out


def gross_ladder(gross_face):
    """(arm, era) -> the sink/contrib reading (E176 shape: one cell per era)."""
    out = {}
    for era, cell in (gross_face.get("eras") or {}).items():
        if not isinstance(cell, dict):
            continue
        for arm in ("raw", "screened"):
            v = cell.get("decomposition_engine_bp_%s" % arm)
            if _is_num(v):
                out[(arm, era)] = float(v)
    return out


def net_ladder(net_face):
    """(arm, era) -> the daily/curve reading (E177 shape: keyed '<arm>|<era>')."""
    out = {}
    for cell in (net_face.get("eras") or {}).values():
        if not isinstance(cell, dict):
            continue
        era, arm = cell.get("era"), cell.get("arm") or "raw"
        v = cell.get("decomposition_engine_bp")
        if era and _is_num(v):
            out[(arm, era)] = float(v)
    return out


def published_ladder(gross_face):
    out = {}
    for era, cell in (gross_face.get("eras") or {}).items():
        if not isinstance(cell, dict):
            continue
        for arm in ("raw", "screened"):
            v = cell.get("published_engine_bp_%s" % arm)
            if _is_num(v):
                out[(arm, era)] = float(v)
    return out


def stance_of(text):
    """Which fee stance a face's own text declares. Four states, no guessing."""
    low = (text or "").lower()
    gross = any(t in low for t in STANCE_GROSS_TOKENS)
    net = any(t in low for t in STANCE_NET_TOKENS)
    if gross and net:
        return "both"
    if gross:
        return "gross_only"
    if net:
        return "net_only"
    return "unlabelled"


def wedge_rows(fee, gross, net, published):
    """Per (arm, era): one number in two stances, the fee between them, and the
    offset each stance publishes (published level minus that reading)."""
    rows = []
    for key in sorted(set(gross) & set(net) & set(fee),
                      key=lambda k: (str(k[1]), str(k[0]))):
        arm, era = key
        g, n, f = gross[key], net[key], fee[key]
        pub = published.get(key)
        off_g = round(pub - g, 4) if pub is not None else None
        off_n = round(pub - n, 4) if pub is not None else None
        rows.append({
            "arm": arm,
            "era": era,
            "gross_bp": g,
            "net_bp": n,
            "fee_bp": f,
            "stance_gap_bp": round(g - n, 4),
            "residual_after_fee_bp": round(g - n - f, 4),
            "rel_shift_pct": (round(100.0 * (g - n) / abs(n), 3) if n else None),
            "offset_gross_stance_bp": off_g,
            "offset_net_stance_bp": off_n,
            "offset_stance_gap_bp": (round(off_n - off_g, 4)
                                     if off_g is not None and off_n is not None else None),
            "offset_margin_in_fees": (round(abs(off_n) / f, 3)
                                      if off_n is not None and f else None),
            "inside_the_wedge": bool(off_n is not None and f
                                     and min(abs(off_n), abs(off_g or 0.0)) <= f),
            "inside_stances": ([s for s, v in (("gross", off_g), ("net", off_n))
                                if v is not None and f and abs(v) <= f]),
            "sign_flips_with_stance": (off_g is not None and off_n is not None
                                       and (off_g > 0) != (off_n > 0)),
        })
    return rows


def _numeric_paths(obj, path="", out=None):
    """Every numeric leaf WITH its key path -- the era/arm context this leg needs
    lives in the enclosing keys, not in the leaf name."""
    if out is None:
        out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            _numeric_paths(v, path + "/" + str(k), out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _numeric_paths(v, path + "/" + str(i), out)
    elif _is_num(obj):
        out.append((path, obj))
    return out


def label_sweep(base, dirs, gross, net, tol=0.01):
    """Classify every face in the quoting dirs by the stance it PUBLISHES cells in
    versus the stance its own text DECLARES."""
    eras = sorted({k[1] for k in list(gross) + list(net)})
    gvals, nvals = {}, {}
    for (arm, era), v in gross.items():
        gvals.setdefault(era, []).append(v)
    for (arm, era), v in net.items():
        nvals.setdefault(era, []).append(v)
    rows, skipped = [], []
    for d in dirs:
        for path in sorted(glob.glob(os.path.join(base, d.replace("/", os.sep), "*.json"))):
            try:
                with io.open(path, encoding="utf-8") as fh:
                    doc = json.load(fh)
            except Exception:
                continue
            study = doc.get("study") if isinstance(doc, dict) else None
            if study in LABELDUTY_EXCLUDE_STUDIES:
                skipped.append({"face": _rel(base, path), "study": study,
                                "reason": "this_leg_or_its_label_source"})
                continue
            # The study slug is an identifier, not a claim: a face called
            # ..._gross_something declares nothing about the cell it publishes.
            text = json.dumps({k: v for k, v in doc.items() if k != "study"}
                              if isinstance(doc, dict) else doc, ensure_ascii=False)
            stance = stance_of(text)
            g_n = n_n = 0
            for leaf, val in _numeric_paths(doc):
                era = next((e for e in eras if e and e in leaf), None)
                if not era:
                    continue
                if any(abs(val - g) <= tol for g in gvals.get(era, [])):
                    g_n += 1
                if any(abs(val - n) <= tol for n in nvals.get(era, [])):
                    n_n += 1
            if g_n and n_n:
                side = "both"
            elif g_n:
                side = "gross"
            elif n_n:
                side = "net"
            else:
                side = "neither"
            if side == "both":
                cls = "labelled" if stance == "both" else "mixed"
            elif side == "neither":
                cls = "no_stance_cells"
            elif stance == "unlabelled":
                cls = "unlabelled"
            elif stance == "both":
                cls = "labelled"
            elif stance[:-5] == side:
                cls = "labelled"
            else:
                cls = "mislabeled"
            rows.append({
                "face": _rel(base, path),
                "study": study,
                "declared_stance": stance,
                "publishes_stance_cells": side,
                "gross_cells": g_n,
                "net_cells": n_n,
                "label_class": cls,
                "mentions_fee": any(t in text.lower() for t in FEE_TEXT_TOKENS),
            })
    rows.sort(key=lambda r: r["face"])
    return rows, skipped


def label_duty(base=None):
    base = base or ROOT
    gp = _newest_under(base, GROSS_FACE_GLOB)
    npth = _newest_under(base, NET_FACE_GLOB)
    fp = _newest_under(base, FEE_FACE_GLOB)
    if not (gp and npth and fp):
        return {"study": "e188_decomposition_label_duty",
                "status": "awaiting_upstream",
                "missing": {"gross_face": bool(gp), "net_face": bool(npth),
                            "fee_face": bool(fp)}}

    def _load(p):
        with io.open(p, encoding="utf-8") as fh:
            return json.load(fh)

    gross_face, net_face, fee_face = _load(gp), _load(npth), _load(fp)
    fee = fee_ladder(fee_face)
    gross = gross_ladder(gross_face)
    net = net_ladder(net_face)
    published = published_ladder(gross_face)
    rows = wedge_rows(fee, gross, net, published)
    sweep, skipped = label_sweep(base, LEVELQUOTE_DIRS, gross, net)

    rel_shifts = [r["rel_shift_pct"] for r in rows if r["rel_shift_pct"] is not None]
    residuals = [abs(r["residual_after_fee_bp"]) for r in rows]
    inside = [r for r in rows if r["inside_the_wedge"]]
    flips = [r for r in rows if r["sign_flips_with_stance"]]

    # The offsets each face PUBLISHES for itself: E176 stores (reading - published),
    # E177 stores (published - reading).  Same construct, opposite sign convention, and
    # the two differ by exactly the fee -- measured here rather than argued.
    published_offsets = []
    for era, cell in (gross_face.get("eras") or {}).items():
        if not isinstance(cell, dict):
            continue
        own = cell.get("decomposition_level_offset_bp")
        if not isinstance(own, dict):
            continue
        for arm in ("raw", "screened"):
            theirs = (net_face.get("eras") or {}).get("%s|%s" % (arm, era), {})
            o_g = own.get(arm)
            o_n = theirs.get("level_offset_bp") if isinstance(theirs, dict) else None
            if not _is_num(o_g) or not _is_num(o_n):
                continue
            published_offsets.append({
                "arm": arm,
                "era": era,
                "gross_face_offset_bp": float(o_g),
                "net_face_offset_bp": float(o_n),
                "gap_bp": round(float(o_n) + float(o_g), 4),
                "fee_bp": fee.get((arm, era)),
                "gap_is_the_fee": (fee.get((arm, era)) is not None
                                   and abs(abs(float(o_n) + float(o_g))
                                           - fee[(arm, era)]) <= 0.10),
            })

    # A delta built from the two readings keeps the fee only insofar as the two arms
    # carry different fees: pre2017/2017_2020 are identical arms, the rest are not.
    delta_shifts = []
    for era in sorted({k[1] for k in fee}):
        fr, fs = fee.get(("raw", era)), fee.get(("screened", era))
        if fr is None or fs is None:
            continue
        delta_shifts.append({"era": era, "fee_raw_bp": fr, "fee_screened_bp": fs,
                             "delta_restatement_shift_bp": round(fr - fs, 4),
                             "delta_is_fee_neutral": abs(fr - fs) == 0.0})

    classes = {}
    for r in sweep:
        classes[r["label_class"]] = classes.get(r["label_class"], 0) + 1
    cutoffs = [d.get("evidence_cutoff") for d in (gross_face, net_face, fee_face)
               if d.get("evidence_cutoff")]
    return {
        "study": "e188_decomposition_label_duty",
        "evidence_cutoff": max(cutoffs) if cutoffs else None,
        "spec": {
            "gross_face": _rel(base, gp),
            "net_face": _rel(base, npth),
            "fee_face": _rel(base, fp),
            "stance_tokens": {"gross": list(STANCE_GROSS_TOKENS),
                              "net": list(STANCE_NET_TOKENS)},
            "class_rules": {
                "labelled": "publishes one stance and its text declares that stance",
                "unlabelled": "publishes a stance and its text declares none",
                "mixed": "publishes BOTH stances under one label (the E180 collision)",
                "mislabeled": "declares one stance and publishes the other",
                "no_stance_cells": "publishes neither reading (not a consumer of this cell)",
            },
            "value_match_tolerance_bp": 0.01,
            "units": "bp as published by the producing face; rel_shift_pct is a percent",
        },
        "wedge": rows,
        "published_offsets": published_offsets,
        "delta_restatement": delta_shifts,
        "family": sweep,
        "skipped": skipped,
        "totals": {
            "cells": len(rows),
            "max_abs_residual_after_fee_bp": round(max(residuals), 4) if residuals else None,
            "rel_shift_range_pct": ([min(rel_shifts), max(rel_shifts)]
                                    if rel_shifts else None),
            "cells_inside_the_wedge": len(inside),
            "cells_quoting_sign_flip_with_stance": len(flips),
            "published_offsets_differ_by_the_fee": sum(
                1 for o in published_offsets if o["gap_is_the_fee"]),
            "published_offsets_checked": len(published_offsets),
            "label_classes": classes,
            "faces_in_family": len(sweep),
            "faces_publishing_a_stance": sum(
                1 for r in sweep if r["publishes_stance_cells"] != "neither"),
        },
        "answers": {
            "the_two_readings_are_one_number_plus_the_fee_measured": (
                bool(residuals) and max(residuals) <= 0.01),
            "the_label_moves_the_level_by_pct": ([min(rel_shifts), max(rel_shifts)]
                                                 if rel_shifts else None),
            "sign_flips_when_the_stance_changes": [r["era"] + "|" + r["arm"]
                                                   for r in flips],
            "verdicts_inside_the_wedge": [
                {"era": r["era"], "arm": r["arm"],
                 "offset_gross_stance_bp": r["offset_gross_stance_bp"],
                 "offset_net_stance_bp": r["offset_net_stance_bp"],
                 "inside_stances": r["inside_stances"],
                 "fee_bp": r["fee_bp"],
                 "offset_margin_in_fees": r["offset_margin_in_fees"]}
                for r in inside],
            "faces_that_say_which_stance_they_publish": [
                {"face": r["face"], "label_class": r["label_class"]}
                for r in sweep if r["label_class"] in ("labelled", "mislabeled")],
            "faces_publishing_a_reading_without_saying_which": [
                {"face": r["face"], "side": r["publishes_stance_cells"],
                 "gross_cells": r["gross_cells"], "net_cells": r["net_cells"]}
                for r in sweep if r["label_class"] == "unlabelled"],
            "reading": (
                "%d cells publish one number in two fee stances; gross minus net equals "
                "the rebalance fee to %s bp, so the label alone moves the level by "
                "%s-%s%%. %d cell(s) quote an offset no wider than its own fee "
                "(inside the wedge) and %d quote a sign that flips with the stance. "
                "%d/%d published offsets are the same construct with the fee between "
                "them. In the family, %d face(s) publish a stance: %s."
                % (len(rows),
                   ("%.4f" % max(residuals)) if residuals else "n/a",
                   ("%s" % min(rel_shifts)) if rel_shifts else "n/a",
                   ("%s" % max(rel_shifts)) if rel_shifts else "n/a",
                   len(inside), len(flips),
                   sum(1 for o in published_offsets if o["gap_is_the_fee"]),
                   len(published_offsets),
                   sum(1 for r in sweep if r["publishes_stance_cells"] != "neither"),
                   ", ".join("%s=%d" % (k, v) for k, v in sorted(classes.items()))
                   or "none")),
        },
        "honest": [
            "the stance is read from the face's OWN text tokens, so a face that labels "
            "the number only in a prose digest (not in the JSON it publishes) counts as "
            "unlabelled -- that is the point: a reader copying the JSON never sees it",
            "gross minus net is the fee only because E185 already located it; this leg "
            "does not re-derive the fee, it joins the published term",
            "a delta that carries the same fee on both arms is fee-neutral by "
            "construction; the restatement shift published here is the difference "
            "between the two arms' fees, not a property of the signal",
            "inside_the_wedge compares the published offset to that cell's own fee, so "
            "the threshold moves with the era rather than sitting at one constant",
        ],
        "law_ref": "O-20261002-2100 capture law (new method -> methodology card)",
    }


def run_labelduty(publish=False, base=None):
    face = label_duty(base=base)
    if face.get("status") == "awaiting_upstream":
        print("awaiting upstream: %s" % face["missing"])
        return 0
    if publish:
        out = os.path.join(_abs(LABELDUTY_OUT_DIR),
                           "LABELDUTY-%s.json" % (face["evidence_cutoff"] or "unknown"))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(face, ensure_ascii=False, indent=1) + "\n")
        print("wrote", os.path.relpath(out, ROOT).replace("\\", "/"))
    t = face["totals"]
    print("cells=%d residual_after_fee=%s rel_shift=%s inside_wedge=%d sign_flips=%d "
          "offsets_differ_by_fee=%d/%d classes=%s"
          % (t["cells"], t["max_abs_residual_after_fee_bp"], t["rel_shift_range_pct"],
             t["cells_inside_the_wedge"], t["cells_quoting_sign_flip_with_stance"],
             t["published_offsets_differ_by_the_fee"], t["published_offsets_checked"],
             ",".join("%s=%d" % (k, v) for k, v in sorted(t["label_classes"].items()))))
    for row in face["answers"]["verdicts_inside_the_wedge"]:
        print("  INSIDE_WEDGE", row["era"], row["arm"],
              "gross", row["offset_gross_stance_bp"],
              "net", row["offset_net_stance_bp"],
              "fee", row["fee_bp"], "stances", row["inside_stances"])
    for row in face["answers"]["faces_publishing_a_reading_without_saying_which"]:
        print("  UNLABELLED", row["face"], row["side"])
    return 0


# ---------------------------------------------------- E193 delta build stance


DELTASTANCE_OUT_DIR = "results/e79"
DELTASTANCE_EXCLUDE_STUDIES = ("e180_published_level_quote_audit",
                               "e188_decomposition_label_duty",
                               "e193_decomposition_delta_build_stance")
DELTA_LEAF_TOKENS = ("delta", "diff", "difference")
DELTA_UNIT_SUFFIX = "_bp"
DELTA_ARMS = ("raw", "screened")

# Build family -> (fee content, what the family means).  The fee content is what the
# delta silently carries: a reader who restates the cell on a single stance moves the
# printed number by exactly that much.
DELTA_FAMILIES = {
    "from_two_published_levels": (
        "fee_free",
        "both operands are published levels; the difference inherits nothing"),
    "book_pair": ("fee_free", "two anchored book levels"),
    "same_stance_arm_delta": (
        "arm_fee_diff",
        "two readings of ONE stance across arms: carries fee_raw minus fee_screened"),
    "cross_stance": (
        "full_fee",
        "one operand gross, the other net: the whole fee sits inside the delta"),
    "abs_sum_of_name_deltas": (
        "arm_fee_diff_per_name",
        "a SUM of absolute per-name arm deltas (turnover of the level), not a "
        "difference of two levels"),
    "arm_delta_of_screen_output": (
        "not_a_curve_reading",
        "screening outputs (tilt / spread / neutral) carry no fee term"),
    "cross_measure_pair": (
        "fee_free", "two different measures of one era, neither a curve reading"),
    "unnamed_operand": (
        "unknown",
        "the label names the arithmetic but not the object it differences"),
    "external_operands": ("unknown", "operands live on a sibling face"),
    "residual": ("not_a_build", "a difference between two deltas"),
    "unbound": ("unknown", "no build rule fired"),
}

# Ordered (regex on the arm-stripped leaf name, build family).  First match wins, so
# the order is part of the classification: the narrower names come first.
DELTA_BUILD_RULES = (
    (re.compile(r"^(?:published_)?engine_bp_delta$"), "from_two_published_levels"),
    (re.compile(r"^engine_delta_from_books_bp$"), "book_pair"),
    (re.compile(r"^(?:rotating_wide_book|wide_book|ladder_book)_delta_bp$"), "book_pair"),
    (re.compile(r"^(?:e182_|max_)?gross_abs_delta_bp$"), "abs_sum_of_name_deltas"),
    (re.compile(r"^(?:e182_)?net_delta_bp$"), "unnamed_operand"),
    (re.compile(r"^(?:tilt|spread_raw|neutral)_bp_delta$"), "arm_delta_of_screen_output"),
    (re.compile(r"^engine_diff_bp_(?:raw|screened)$"), "arm_delta_of_screen_output"),
    (re.compile(r"^(?:max_abs_)?engine_ann_diff_bp$"), "cross_measure_pair"),
    (re.compile(r"^delta_[45]member_minus_3member_bp$"), "external_operands"),
    (re.compile(r"^(?:max_abs_)?engine_delta_residual_bp$"), "residual"),
)

# Families whose label does not name its operand get the whole construct table
# searched; the match is what identifies the object, and it is published as such.
DELTA_SEARCH_ALL = ("unnamed_operand", "abs_sum_of_name_deltas", "unbound")


def delta_build_family(leaf):
    """Which build path a published delta cell's own name declares.

    The raw leaf is tried first: arm-suffixed names (`engine_diff_bp_raw`) carry the
    arm in the name, so stripping it before matching would lose the rule.
    """
    for name in ((leaf or "").lower(), _base_name(leaf)):
        for rx, family in DELTA_BUILD_RULES:
            if rx.match(name):
                return family
    return "unbound"


def _delta_books(gross_face):
    """(book, arm, era) -> the anchored book level the E176 face publishes."""
    out = {}
    for era, cell in (gross_face.get("eras") or {}).items():
        if not isinstance(cell, dict):
            continue
        for arm in DELTA_ARMS:
            for book in ("wide_book", "ladder_book"):
                v = cell.get("%s_bp_%s" % (book, arm))
                if _is_num(v):
                    out[(book, arm, era)] = float(v)
    return out


def delta_constructs(fee, gross, net, published, books):
    """(era, family) -> every number that build path produces from published cells.

    Enumerated a priori from the family's own declared readings, so a cell that
    matches one of them is reproduced rather than guessed at.
    """
    eras = sorted({k[1] for k in list(fee) + list(gross) + list(net) + list(published)})
    out = {}
    for era in eras:
        g = {a: gross.get((a, era)) for a in DELTA_ARMS}
        n = {a: net.get((a, era)) for a in DELTA_ARMS}
        p = {a: published.get((a, era)) for a in DELTA_ARMS}
        cands = {}

        def add(family, label, value):
            if _is_num(value):
                cands.setdefault(family, []).append(
                    {"label": label, "value_bp": round(float(value), 4)})

        def diff(a, b):
            return None if a is None or b is None else float(a) - float(b)

        w = lambda arm: books.get(("wide_book", arm, era))
        lad = lambda arm: books.get(("ladder_book", arm, era))
        add("from_two_published_levels", "published_raw_minus_screened",
            diff(p["raw"], p["screened"]))
        add("book_pair", "wide_book_raw_minus_screened", diff(w("raw"), w("screened")))
        add("book_pair", "ladder_book_raw_minus_screened", diff(lad("raw"), lad("screened")))
        add("book_pair", "wide_minus_ladder_raw", diff(w("raw"), lad("raw")))
        add("book_pair", "wide_minus_ladder_screened", diff(w("screened"), lad("screened")))
        add("same_stance_arm_delta", "gross_raw_minus_screened", diff(g["raw"], g["screened"]))
        add("same_stance_arm_delta", "net_raw_minus_screened", diff(n["raw"], n["screened"]))
        add("cross_stance", "gross_minus_net_raw", diff(g["raw"], n["raw"]))
        add("cross_stance", "gross_minus_net_screened", diff(g["screened"], n["screened"]))
        out[era] = cands
    return out


def delta_fee_content(family, era, arm, fee, matched_family=None):
    """(shift_bp, basis): what a fee-free restatement of this cell would move it by."""
    eff = family
    if family == "unnamed_operand" and matched_family:
        eff = matched_family
    if eff in ("from_two_published_levels", "book_pair", "cross_measure_pair"):
        return 0.0, "fee_free"
    if eff in ("same_stance_arm_delta", "abs_sum_of_name_deltas"):
        fr, fs = fee.get(("raw", era)), fee.get(("screened", era))
        if fr is None or fs is None:
            return None, "unknown"
        return round(fr - fs, 4), "arm_fee_diff"
    if eff == "cross_stance":
        f = fee.get((arm or "raw", era))
        return (round(f, 4), "full_fee") if f is not None else (None, "unknown")
    return None, DELTA_FAMILIES.get(eff, ("unknown", ""))[0]


def _delta_match(cands, value, tol):
    """Collect the constructs a cell reproduces, keeping the sign convention."""
    hits = []
    for c in cands:
        if abs(c["value_bp"] - value) <= tol:
            hits.append((c, "same"))
        elif abs(c["value_bp"] + value) <= tol and abs(value) > tol:
            hits.append((c, "flipped"))
    return hits


def _delta_sibling_map(doc):
    """(era, arm) -> {leaf: value} for the fields a face publishes inside one era cell.

    The cross-measure and residual deltas differ two cells of the SAME era, so the
    operands are siblings; nothing outside this face can rebuild them.
    """
    out = {}
    eras = doc.get("eras")
    if not isinstance(eras, dict):
        return out
    for key, cell in eras.items():
        if not isinstance(cell, dict):
            continue
        era, arm = era_arm_of("/eras/" + str(key) + "/_cell")
        if not era:
            continue
        nums = {k: float(v) for k, v in cell.items() if _is_num(v)}
        if nums:
            out[(era, arm)] = nums
    return out


def _delta_in_cell(value, siblings, leaf, tol=0.01):
    """Pairs of sibling fields whose difference (either sign) is this cell."""
    hits = []
    names = sorted(k for k in siblings if k != leaf)
    for a in names:
        for b in names:
            if a == b:
                continue
            if abs(siblings[a] - siblings[b] - value) <= tol:
                hits.append((a, b, "same"))
            elif abs(value) > tol and abs(siblings[a] - siblings[b] + value) <= tol:
                hits.append((a, b, "flipped"))
    return hits


def delta_sweep(base, fee, gross, net, published, books, tol=0.01):
    """Classify every bp delta a face publishes at era level by how it was BUILT."""
    constructs = delta_constructs(fee, gross, net, published, books)
    rows, nested = [], []
    for d in LEVELQUOTE_DIRS:
        for path in sorted(glob.glob(os.path.join(base, d.replace("/", os.sep), "*.json"))):
            try:
                with io.open(path, encoding="utf-8") as fh:
                    doc = json.load(fh)
            except Exception:
                continue
            if not isinstance(doc, dict):
                continue
            if doc.get("study") in DELTASTANCE_EXCLUDE_STUDIES:
                continue
            rel = _rel(base, path)
            sibs = _delta_sibling_map(doc)
            for cell_path, value in _numeric_paths(doc):
                leaf = cell_path.split("/")[-1]
                low = leaf.lower()
                if not any(t in low for t in DELTA_LEAF_TOKENS):
                    continue
                if "_bp" not in low:
                    # counts, shares and percentages are not deltas in bp; the unit
                    # may sit mid-name (`engine_bp_delta`) or at the end (`delta_bp`)
                    continue
                segs = [s for s in cell_path.split("/") if s]
                era, arm = era_arm_of(cell_path)
                parent = segs[-2] if len(segs) > 1 else None
                p_era, p_arm = era_arm_of(parent or "")
                if not era or not (parent == era or p_era == era):
                    nested.append({"face": rel, "path": cell_path, "value_bp": value,
                                   "reason": "internal_arithmetic_not_an_era_cell"})
                    continue
                family = delta_build_family(leaf)
                era_constructs = constructs.get(era, {})
                zero_cell = abs(value) <= tol
                if family in DELTA_SEARCH_ALL:
                    searched = sorted(era_constructs)
                else:
                    searched = [family]
                hits = []
                if not zero_cell:
                    # A zero has no sign and matches any zero construct: reproducing it
                    # says nothing, so it is reported as unchecked rather than as a hit.
                    for fam in searched:
                        for c, convention in _delta_match(era_constructs.get(fam, []),
                                                          value, tol):
                            hits.append((fam, c, convention))
                elsewhere = [h for h in hits if h[0] != family]
                matched_family = hits[0][0] if hits else None
                in_cell = []
                if not zero_cell and not hits and family in DELTA_SEARCH_ALL + (
                        "cross_measure_pair", "residual", "arm_delta_of_screen_output"):
                    # What the ladder cannot rebuild, the face itself can: a
                    # cross-measure delta differs two fields of its own era cell.
                    in_cell = _delta_in_cell(value, sibs.get((era, arm or p_arm), {}),
                                             leaf, tol)
                if zero_cell:
                    verified = "not_checkable_zero"
                elif hits:
                    verified = ("reproduces" if hits[0][2] == "same"
                                else "reproduces_flipped_sign")
                elif family == "abs_sum_of_name_deltas":
                    # a sum of absolute per-name deltas has no era-level rebuilding:
                    # only the top carriers are published, never the full name set.
                    verified = "not_checkable"
                elif in_cell:
                    verified = "reproduces_in_cell"
                elif not any(era_constructs.get(fam) for fam in searched):
                    verified = "not_checkable"
                else:
                    verified = "does_not_reproduce"
                shift, basis = delta_fee_content(family, era, arm or p_arm, fee,
                                                 matched_family)
                rows.append({
                    "face": rel,
                    "field": cell_path,
                    "leaf": leaf,
                    "base_name": _base_name(leaf),
                    "era": era,
                    "arm": arm or p_arm,
                    "value_bp": value,
                    "build_family": family,
                    "matched_family": matched_family,
                    "fee_content": DELTA_FAMILIES[family][0],
                    "reproduced_by": [h[1]["label"] for h in hits],
                    "reproduced_family": [h[0] for h in hits],
                    "sign_convention": [h[2] for h in hits],
                    "reproduced_value_bp": hits[0][1]["value_bp"] if hits else None,
                    "residual_bp": ((round(value - hits[0][1]["value_bp"], 4)
                                     if hits[0][2] == "same"
                                     else round(value + hits[0][1]["value_bp"], 4))
                                    if hits else None),
                    "matched_outside_its_label": bool(elsewhere),
                    "reproduced_in_cell": [{"minus": a, "plus": b, "convention": c}
                                           for a, b, c in in_cell[:4]],
                    "verification": verified,
                    "restatement_shift_bp": shift,
                    "shift_basis": basis,
                    "shift_exceeds_value": bool(shift is not None
                                                and basis in ("arm_fee_diff", "full_fee")
                                                and abs(value) > tol
                                                and abs(shift) > abs(value)),
                })
    rows.sort(key=lambda r: (r["face"], r["field"]))
    return rows, nested, constructs


def deltastance(base=None):
    base = base or ROOT
    gp = _newest_under(base, GROSS_FACE_GLOB)
    npth = _newest_under(base, NET_FACE_GLOB)
    fp = _newest_under(base, FEE_FACE_GLOB)
    if not (gp and npth and fp):
        return {"study": "e193_decomposition_delta_build_stance",
                "status": "awaiting_upstream",
                "missing": {"gross_face": bool(gp), "net_face": bool(npth),
                            "fee_face": bool(fp)}}

    def _load(p):
        with io.open(p, encoding="utf-8") as fh:
            return json.load(fh)

    gross_face, net_face, fee_face = _load(gp), _load(npth), _load(fp)
    fee = fee_ladder(fee_face)
    gross = gross_ladder(gross_face)
    net = net_ladder(net_face)
    published = published_ladder(gross_face)
    books = _delta_books(gross_face)
    rows, nested, constructs = delta_sweep(base, fee, gross, net, published, books)

    by_family, by_verification, by_fee_content = {}, {}, {}
    for r in rows:
        by_family[r["build_family"]] = by_family.get(r["build_family"], 0) + 1
        by_verification[r["verification"]] = by_verification.get(r["verification"], 0) + 1
        by_fee_content[r["fee_content"]] = by_fee_content.get(r["fee_content"], 0) + 1

    shifts = [abs(r["restatement_shift_bp"]) for r in rows
              if r["restatement_shift_bp"] is not None]
    flagged = [r for r in rows if r["shift_exceeds_value"]]
    cross = [r for r in rows if r["build_family"] == "cross_stance"]
    reproduced = [r for r in rows if r["verification"].startswith("reproduces")]
    contradicted = [r for r in rows if r["verification"] == "does_not_reproduce"]
    flipped = [r for r in rows if r["verification"] == "reproduces_flipped_sign"]
    in_cell = [r for r in rows if r["verification"] == "reproduces_in_cell"]
    outside = [r for r in rows if r["matched_outside_its_label"]]
    # The family's own vocabulary says "net of the fee" (E188 measured it). A delta
    # whose name carries a stance word but is fee-free by construction is the exact
    # defect E193 warns about, one level up: the label, not the arithmetic.  An
    # unnamed-operand cell takes the fee content of the build it reproduces.
    def _effective_fee_content(r):
        if r["build_family"] == "unnamed_operand" and r["matched_family"]:
            return DELTA_FAMILIES.get(r["matched_family"], ("unknown", ""))[0]
        return r["fee_content"]

    for r in rows:
        r["effective_fee_content"] = _effective_fee_content(r)
    stance_named = [r for r in rows
                    if ("net" in r["base_name"] or "gross" in r["base_name"])
                    and r["effective_fee_content"] == "fee_free"]
    distinct = {}
    for r in rows:
        distinct[(r["base_name"], r["era"], round(r["value_bp"], 4))] = r
    # One sign convention for the whole family, MEASURED: every delta the ladder can
    # rebuild lands on the negative of the authored construct, i.e. the faces print
    # screened minus raw while the construct is authored raw minus screened.
    conventions = {}
    for r in rows:
        if not r["sign_convention"]:
            continue
        conventions[r["sign_convention"][0]] = conventions.get(
            r["sign_convention"][0], 0) + 1
    uniform = len([k for k, v in conventions.items() if v]) == 1
    cutoffs = [d.get("evidence_cutoff") for d in (gross_face, net_face, fee_face)
               if d.get("evidence_cutoff")]
    return {
        "study": "e193_decomposition_delta_build_stance",
        "evidence_cutoff": max(cutoffs) if cutoffs else None,
        "spec": {
            "gross_face": _rel(base, gp),
            "net_face": _rel(base, npth),
            "fee_face": _rel(base, fp),
            "scope": ("every bp delta a face of the family publishes at ERA level; "
                      "deltas nested inside per-month / per-name lists are internal "
                      "arithmetic and are counted, not classified"),
            "build_families": {k: {"fee_content": v[0], "meaning": v[1]}
                               for k, v in sorted(DELTA_FAMILIES.items())},
            "binding_rules": [[rx.pattern, fam] for rx, fam in DELTA_BUILD_RULES],
            "verification": ("a cell REPRODUCES when a construct this family can build "
                             "from the published ladders lands within tolerance; a cell "
                             "whose value is the NEGATIVE of a construct reproduces_flipped"
                             "_sign and is reported as a sign-convention difference, not "
                             "as a match"),
            "value_match_tolerance_bp": 0.01,
            "units": "bp as published by the producing face",
        },
        "constructs": [{"era": era,
                        "builds": [{"family": fam, "label": c["label"],
                                    "value_bp": c["value_bp"]}
                                   for fam in sorted(cs) for c in cs[fam]]}
                       for era, cs in sorted(constructs.items())],
        "rows": rows,
        "nested": nested,
        "totals": {
            "era_level_delta_cells": len(rows),
            "distinct_delta_constructs": len(distinct),
            "faces": len({r["face"] for r in rows}),
            "build_families": by_family,
            "verification": by_verification,
            "fee_content": by_fee_content,
            "cells_reproduced": len(reproduced),
            "cells_reproduced_in_cell": len(in_cell),
            "cells_contradicted": len(contradicted),
            "cells_reproduced_flipped_sign": len(flipped),
            "cells_matched_outside_their_label": len(outside),
            "cells_not_checkable": sum(1 for r in rows
                                       if r["verification"] == "not_checkable"),
            "cells_not_checkable_zero": sum(1 for r in rows
                                            if r["verification"] == "not_checkable_zero"),
            "cells_named_net_or_gross_but_fee_free": len(stance_named),
            "cross_stance_cells": len(cross),
            "max_restatement_shift_bp": round(max(shifts), 4) if shifts else None,
            "cells_shift_exceeds_value": len(flagged),
            "nested_delta_cells": len(nested),
            "sign_convention": conventions,
            "sign_convention_is_uniform": uniform,
        },
        "answers": {
            "how_each_published_delta_was_built": {k: by_family[k]
                                                   for k in sorted(by_family)},
            "fee_free_cells": sum(1 for r in rows if r["fee_content"] == "fee_free"),
            "cells_that_sit_under_their_own_shift": [
                {"face": r["face"], "field": r["field"], "era": r["era"],
                 "value_bp": r["value_bp"], "restatement_shift_bp": r["restatement_shift_bp"],
                 "basis": r["shift_basis"]}
                for r in flagged],
            "cells_whose_name_and_number_disagree": [
                {"face": r["face"], "field": r["field"], "era": r["era"],
                 "declared_family": r["build_family"], "value_bp": r["value_bp"],
                 "constructs_tried": [c["label"] for c in
                                      constructs.get(r["era"], {}).get(r["build_family"], [])]}
                for r in contradicted],
            "sign_convention_of_reproduced_deltas": {
                "conventions": conventions,
                "uniform": uniform,
                "note": ("`same` means the printed number is the construct the rule "
                         "names; `flipped` means it is that construct negated, so the "
                         "faces print screened-minus-raw where the rule reads "
                         "raw-minus-screened"),
            },
            "labels_that_do_not_name_their_operand": [
                {"face": r["face"], "field": r["field"], "era": r["era"],
                 "value_bp": r["value_bp"], "matched_family": r["matched_family"],
                 "reproduced_by": r["reproduced_by"][:2]}
                for r in outside],
            "fee_words_in_fee_free_names": [
                {"face": r["face"], "field": r["field"], "era": r["era"],
                 "value_bp": r["value_bp"], "build_family": r["build_family"],
                 "fee_content": r["fee_content"]}
                for r in stance_named],
            "reading": (
                "%d bp delta cells published at era level: %d reproduce a build path "
                "inside their own era cell, %d reproduce a ladder construct only with "
                "the opposite sign, %d contradict theirs, %d are zero-valued and %d "
                "cannot be checked from either source. %d are fee-free by construction, "
                "%d take the absolute value of per-name arm deltas and %d differ the two "
                "stances - the only construct that would carry the whole fee is published "
                "nowhere as a delta. Max arm fee difference available to be inherited is "
                "%s bp, and %d cell(s) would print less than a fee they actually carried. "
                "Sign convention is %s: the printed delta is the construct negated. %d "
                "cell(s) carry a stance word in their name while being fee-free."
                % (len(rows), len(in_cell), len(flipped), len(contradicted),
                   sum(1 for r in rows if r["verification"] == "not_checkable_zero"),
                   sum(1 for r in rows if r["verification"] == "not_checkable"),
                   sum(1 for r in rows if r["fee_content"] == "fee_free"),
                   by_family.get("abs_sum_of_name_deltas", 0), len(cross),
                   ("%.4f" % max(shifts)) if shifts else "n/a", len(flagged),
                   ("uniform (screened minus raw)" if uniform else "not uniform"),
                   len(stance_named))),
        },
        "honest": [
            "the build path of a cell is bound by its own NAME and then verified "
            "against a construct computed from the published ladders; a cell whose "
            "label does not name its operand is matched by number and that match is "
            "published as a reading, not as a declaration",
            "a flipped-sign reproduction is a sign convention, not a wrong number: the "
            "two faces are each internally consistent and disagree with each other",
            "era-level only: %d deltas nested inside per-month / per-name lists are "
            "counted and excluded - they are internal arithmetic of a parent cell, not "
            "a quote a reader takes away" % len(nested),
            "a fee-free verdict says the delta inherits nothing from the fee, not that "
            "the delta is right",
        ],
    }


def run_deltastance(publish=False, base=None):
    face = deltastance(base=base)
    if face.get("status") == "awaiting_upstream":
        print("awaiting upstream: %s" % face["missing"])
        return 0
    if publish:
        out = os.path.join(_abs(DELTASTANCE_OUT_DIR),
                           "DELTASTANCE-%s.json" % (face["evidence_cutoff"] or "unknown"))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(face, ensure_ascii=False, indent=1) + "\n")
        print("wrote", os.path.relpath(out, ROOT).replace("\\", "/"))
    t = face["totals"]
    print("era_cells=%d distinct=%d faces=%d reproduced=%d contradicted=%d "
          "not_checkable=%d cross_stance=%d max_shift=%s shift_exceeds_value=%d nested=%d"
          % (t["era_level_delta_cells"], t["distinct_delta_constructs"], t["faces"],
             t["cells_reproduced"], t["cells_contradicted"], t["cells_not_checkable"],
             t["cross_stance_cells"], t["max_restatement_shift_bp"],
             t["cells_shift_exceeds_value"], t["nested_delta_cells"]))
    print("  families:", ", ".join("%s=%d" % (k, v)
                                   for k, v in sorted(t["build_families"].items())))
    for row in face["answers"]["cells_whose_name_and_number_disagree"]:
        print("  NAME_NUMBER_DISAGREE", row["face"], row["field"], row["era"],
              row["value_bp"], "tried", row["constructs_tried"])
    return 0


NEARZERO_OUT_DIR = "results/e79"
# Pre-declared before the sweep is read (E196): a printed sign whose additive
# magnitude is below this fraction of the compounded gap it is told apart from is a
# rounding-scale fact and must not be quoted as a direction.
NEARZERO_RATIO_FLOOR = 0.05
# Pre-declared: below this gap the two readings are not told apart at all, so the
# cell carries no sign question to answer.
NEARZERO_GAP_FLOOR_BP = 1.0
NEARZERO_LEVEL_KEYS = ("arith_bp", "arithmetic_bp", "arith_leg_bp")
NEARZERO_GAP_KEYS = ("comp_bp", "compounded_bp", "comp_leg_bp")


def _nearzero_cells(obj, path, out):
    """Collect every published cell that prints BOTH an additive level and a compounded gap."""
    if isinstance(obj, dict):
        level = gap = None
        for k in NEARZERO_LEVEL_KEYS:
            v = obj.get(k)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                level = float(v)
                break
        for k in NEARZERO_GAP_KEYS:
            v = obj.get(k)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                gap = float(v)
                break
        if level is not None and gap is not None:
            out.append({"path": path, "level_bp": level, "gap_bp": gap})
        for k, v in obj.items():
            _nearzero_cells(v, path + "/" + str(k), out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _nearzero_cells(v, path + "/" + str(i), out)


def _nearzero_sign(v):
    if v > 0:
        return 1
    if v < 0:
        return -1
    return 0


def _nearzero_class(level, gap):
    """The published classification, with the two declared floors applied in order."""
    if abs(gap) < NEARZERO_GAP_FLOOR_BP:
        return "level_agrees"
    if abs(level) < NEARZERO_RATIO_FLOOR * abs(gap):
        return "sign_is_hair"
    return "sign_quotable"


def _nearzero_cutoff(base, faces=None):
    """The newest evidence_cutoff the contributing faces declare; unknown when none does.

    Only ISO dates count: several status faces carry prose in evidence_cutoff
    ("panel 2026-10-14 (bars 10-15 due 15:30)") and a lexicographic max over that
    text wins over every real date, which is how the first publish got a sentence
    for a filename.
    """
    root = os.path.join(base or ".", "results")
    IsoDate = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    want = set(faces) if faces else None
    best = None
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in sorted(filenames):
            if not fn.endswith(".json"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, base or ".").replace("\\", "/")
            if want is not None and rel not in want:
                continue
            try:
                doc = json.load(io.open(full, encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(doc, dict):
                continue
            c = doc.get("evidence_cutoff")
            if isinstance(c, str) and IsoDate.match(c) and (best is None or c > best):
                best = c
    return best


def _nearzero_hair_side(level, gap, cls):
    """Which of the two published numbers is the rounding artefact?

    The same floor answers both directions: a level far below its gap is a hair, and
    so is a gap far below its level (one live cell prints 27.99bp against -0.52bp).
    """
    if cls == "sign_is_hair":
        return "level"
    if cls == "level_agrees" and abs(gap) < NEARZERO_GAP_FLOOR_BP and abs(level) >= NEARZERO_GAP_FLOOR_BP:
        return "gap"
    return None


def nearzero_sign_sweep(base=None):
    """E196: for every published additive-vs-compounded pair, is the printed sign quotable?

    The family (E183-E190) publishes a level reading and a compounded gap side by side.
    A level of +0.07bp against a -38.20bp gap is not a small direction, it is no
    direction: the sign is decided by rounding scale.  This sweep publishes |level| /
    |gap| for every such cell and classifies it against the two floors declared above.
    """
    root = os.path.join(base or ".", "results")
    rows = []
    faces = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in sorted(filenames):
            if not fn.endswith(".json") or "NEARZEROSIGN" in fn:
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, base or ".").replace("\\", "/")
            cells = []
            try:
                doc = json.load(io.open(full, encoding="utf-8"))
            except Exception:
                continue
            _nearzero_cells(doc, "", cells)
            if not cells:
                continue
            faces.append(rel)
            for c in cells:
                level, gap = c["level_bp"], c["gap_bp"]
                ratio = (abs(level) / abs(gap)) if gap else None
                cls = _nearzero_class(level, gap)
                rows.append({
                    "face": rel,
                    "path": c["path"],
                    "level_bp": round(level, 6),
                    "gap_bp": round(gap, 6),
                    "level_over_gap": (round(ratio, 6) if ratio is not None else None),
                    "class": cls,
                    "hair_side": _nearzero_hair_side(level, gap, cls),
                    "sign_level": _nearzero_sign(level),
                    "sign_gap": _nearzero_sign(gap),
                    "signs_disagree": (_nearzero_sign(level) * _nearzero_sign(gap) < 0),
                    # the gap at which this same level would clear the ratio floor
                    "gap_needed_for_quotable_bp": round(abs(level) / NEARZERO_RATIO_FLOOR, 6),
                })
    classes = {}
    for r in rows:
        classes[r["class"]] = classes.get(r["class"], 0) + 1
    disagreements = [r for r in rows if r["signs_disagree"]]
    hair_disagreements = [r for r in disagreements if r["class"] == "sign_is_hair"]
    ratios = sorted(r["level_over_gap"] for r in rows if r["level_over_gap"] is not None)
    median = None
    if ratios:
        n = len(ratios)
        median = ratios[n // 2] if n % 2 else (ratios[n // 2 - 1] + ratios[n // 2]) / 2.0
    return {
        "study": "e196_tilt3_nearzero_sign_census",
        "evidence_cutoff": _nearzero_cutoff(base, faces),
        "spec": {
            "question": "for every published additive-vs-compounded pair in the "
                        "E183-E190 delta family, is the printed sign a direction or a "
                        "rounding-scale artefact?",
            "method": "walk every results/*.json, take every dict carrying both an "
                      "additive level and a compounded gap, publish |level|/|gap| and "
                      "classify against two floors declared before the sweep was read",
            "ratio_floor": NEARZERO_RATIO_FLOOR,
            "gap_floor_bp": NEARZERO_GAP_FLOOR_BP,
            "classes": {
                "sign_is_hair": "|level| < ratio_floor*|gap| -- the printed sign must not be quoted",
                "level_agrees": "|gap| < gap_floor_bp -- no gap to speak of, no sign question",
                "sign_quotable": "|level| >= ratio_floor*|gap| -- the additive reading is big "
                                 "enough to be told apart from the gap",
            },
            "units": "bp",
            "answer_blind": "the classification uses only the two published numbers; no "
                            "threshold was moved after a cell was seen",
        },
        "rows": rows,
        "faces_scanned": sorted(set(faces)),
        "answers": {
            "cells": len(rows),
            "faces": len(set(faces)),
            "class_counts": classes,
            "cells_where_the_two_readings_disagree": len(disagreements),
            "disagreements_whose_sign_is_a_hair": len(hair_disagreements),
            "cells_where_the_gap_is_the_hair": len([r for r in rows
                                                    if r["hair_side"] == "gap"]),
            "distinct_hair_pairs": len(set((r["face"].split("/")[-1], r["path"])
                                           for r in hair_disagreements)),
            "hair_disagreements": [
                {k: r[k] for k in ("face", "path", "level_bp", "gap_bp",
                                   "level_over_gap", "gap_needed_for_quotable_bp")}
                for r in hair_disagreements
            ],
            "median_level_over_gap": (round(median, 6) if median is not None else None),
            "min_level_over_gap": (round(ratios[0], 6) if ratios else None),
            "max_level_over_gap": (round(ratios[-1], 6) if ratios else None),
            "verdict": ("the_printed_sign_is_a_rounding_fact_wherever_level_over_gap_is_below_"
                        "the_floor" if hair_disagreements else
                        "every_published_sign_is_big_relative_to_the_gap_it_separates"),
        },
        "honest": [
            "the two floors are declared constants, not fitted: 5% of the gap and 1bp of gap",
            "a cell prints both numbers but the face never says which one a reader should quote",
            "gap_needed_for_quotable_bp is what the gap would have to be for this same level to "
            "carry a quotable sign at the declared floor -- a scale statement, not a forecast",
            "cells outside the E183-E190 family are included only if they publish both numbers",
        ],
        "law_ref": "O-20260924-1626 R3 (advisory: reader-facing defect, zero-bp cost)",
    }


def run_nearzerosign(publish=False, base=None):
    face = nearzero_sign_sweep(base=base)
    if publish:
        out = os.path.join(_abs(NEARZERO_OUT_DIR),
                           "NEARZEROSIGN-%s.json" % (face["evidence_cutoff"] or "unknown"))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(face, ensure_ascii=False, indent=1) + "\n")
        print("wrote", os.path.relpath(out, ROOT).replace("\\", "/"))
    a = face["answers"]
    print("cells=%d faces=%d disagree=%d hair_disagreements=%d median_ratio=%s"
          % (a["cells"], a["faces"], a["cells_where_the_two_readings_disagree"],
             a["disagreements_whose_sign_is_a_hair"], a["median_level_over_gap"]))
    print("  classes:", ", ".join("%s=%d" % (k, v) for k, v in sorted(a["class_counts"].items())))
    for r in a["hair_disagreements"]:
        print("  SIGN_IS_HAIR", r["face"], r["path"], r["level_bp"], "vs", r["gap_bp"],
              "ratio", r["level_over_gap"], "gap_needed", r["gap_needed_for_quotable_bp"])
    print("  verdict:", a["verdict"])
    return 0


def render_md(face, path=None):
    """Render the routing table as a markdown page (numbers read from the face)."""
    t = face["totals"]
    lines = []
    lines.append("# E97 - screened-consumer routing table")
    lines.append("")
    lines.append("Date: 2026-10-27 | round r1176 | dept: research+engineering")
    lines.append("Face: `results/e79/ROUTING-20261027.json` | "
                 "Tool: `scripts/e97_routing.py` (selftest 14/14)")
    lines.append("")
    lines.append("## What this answers")
    lines.append("")
    lines.append("E94 named %d census modes whose published numbers still come off a repaired "
                 "print. E109 then fixed the repair factor on the 14 legs that join a screened "
                 "arm themselves. What nobody had published is the routing question: for each "
                 "charged mode, **is there a screened twin face on disk at all**, and if not, "
                 "how much number surface does the untouched face carry?" % t["charged_modes"])
    lines.append("")
    lines.append("Coverage is a **code-graph** fact (does a twin leg call this mode's runner, "
                 "or build that face itself), not a column-name guess. The column test is "
                 "measured and published, but it is explicitly non-decisive.")
    lines.append("")
    lines.append("## Totals")
    lines.append("")
    lines.append("| charged | covered by twin call | covered by twin body | uncovered | distinct runners "
                 "| column-only collisions |")
    lines.append("|---|---|---|---|---|---|")
    lines.append("| %d | %d | %d | %d | %d | %d |" % (
        t["charged_modes"], t["covered_by_twin"], t["covered_twin_by_name"],
        t["uncovered"], t["uncovered_distinct_runners"], t["uncovered_column_only"]))
    lines.append("")
    lines.append("## The table")
    lines.append("")
    lines.append("| mode | runner | screened twin | coverage | numbers carried |")
    lines.append("|---|---|---|---|---|")
    for r in face["rows"]:
        twin = ",".join(r["twin_legs"]) or ",".join(x["leg"] for x in r["twin_by_name"]) or "none"
        lines.append("| %s | %s | %s | %s | %d |" % (
            r["mode"], r["runner"], twin, r["coverage"], r["published_cells"]))
    lines.append("")
    lines.append("## Ranked: uncovered, by runner (one burn per runner)")
    lines.append("")
    lines.append("| # | runner | numbers carried | modes sharing the face |")
    lines.append("|---|---|---|---|")
    for i, g in enumerate(face["ranking_uncovered_by_runner"], 1):
        lines.append("| %d | %s | %d | %s |" % (
            i, g["runner"], g["published_cells_dedup"], ", ".join(g["modes"])))
    lines.append("")
    lines.append("## What the numbers say")
    lines.append("")
    top = face["ranking_uncovered_by_runner"][0]
    dedup_total = sum(g["published_cells_dedup"] for g in face["ranking_uncovered_by_runner"])
    share = 100.0 * top["published_cells_dedup"] / dedup_total if dedup_total else 0.0
    lines.append("1. **The biggest untouched face is not a headline leg.** `%s` carries %d "
                 "numbers across %s - the largest single burn, %.0f%% of the %d numbers the "
                 "%d uncovered runners carry together (one burn each, shared faces counted "
                 "once)." % (top["runner"], top["published_cells_dedup"],
                             ", ".join(top["modes"]), share, dedup_total,
                             len(face["ranking_uncovered_by_runner"])))
    lines.append("2. **Only %d of %d charged modes have a twin that calls their runner**, and "
                 "%s. So E109's fixed-factor sweep did not reach the base faces: the corrected "
                 "numbers live on twin faces, while the faces a reader opens are still the "
                 "unscreened ones." % (t["covered_by_twin"], t["charged_modes"],
                                       "exactly one more is covered by a twin that builds the "
                                       "face in its own body" if t["covered_twin_by_name"] else
                                       "no body-built twin exists"))
    lines.append("3. **A column-name test would have routed work to the wrong leg.** %d rows "
                 "match some twin at >=80%% column overlap without any code link; generic metric "
                 "names (`ann_return_pct`, `sharpe`, `max_drawdown_pct`) are why." %
                 t["uncovered_column_only"])
    lines.append("")
    lines.append("## Honest")
    lines.append("")
    for h in face["honest"]:
        lines.append("- " + h)
    lines.append("")
    lines.append("## Verify")
    lines.append("")
    lines.append("```")
    lines.append("python scripts/e97_routing.py selftest      # 14/14")
    lines.append("python scripts/e97_routing.py run --publish\npython scripts/e97_routing.py run --md")
    lines.append("```")
    lines.append("")
    body = "\n".join(lines)
    if path:
        out = _abs(path)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
        print("wrote", path)
    return body


def run(publish=False, md=None):
    face = build()
    payload = json.dumps(face, ensure_ascii=False, indent=1)
    if publish:
        out = os.path.join(_abs(OUT_DIR), "ROUTING-20261027.json")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with io.open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(payload + "\n")
        print("wrote", os.path.relpath(out, ROOT).replace("\\", "/"))
    if md:
        render_md(face, md)
    t = face["totals"]
    print("charged=%d covered_twin=%d by_name=%d uncovered=%d (runners=%d) col_only=%d" % (
        t["charged_modes"], t["covered_by_twin"], t["covered_twin_by_name"], t["uncovered"],
        t["uncovered_distinct_runners"], t["uncovered_column_only"]))
    print("top uncovered runners:")
    for g in face["ranking_uncovered_by_runner"][:8]:
        print("  %-18s cells=%-5d modes=%s" % (g["runner"], g["published_cells_dedup"],
                                               ",".join(g["modes"])))
    return 0


# ---------------------------------------------------------------- selftest


def _fixture(tmp):
    """Hermetic fixture: 3 modes, one code-linked twin, one column-only collision."""
    census = os.path.join(tmp, "census.py")
    with io.open(census, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(
            "def run_alpha(outdir):\n    return 1\n\n"
            "def run_beta(outdir):\n    return 2\n\n"
            "def run_weeklyclash(outdir):\n    return 3\n\n"
            "def run_screenalpha(outdir):\n    return run_alpha(outdir)\n\n"
            "def run_screenweek(outdir):\n"
            "    # week rows: week faces, week baseline, week near month-end\n"
            "    return 4\n"
        )
    faces = os.path.join(tmp, "results", "e9")
    os.makedirs(faces, exist_ok=True)

    def write(name, obj):
        with io.open(os.path.join(faces, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(obj, fh)

    write("ALPHA-20261027.json", {"cells": {"ann_pct": 1.0, "sharpe": 0.5}})
    write("BETA-20261027.json", {"cells": {"ann_pct": 2.0, "sharpe": 0.7, "turnover": 0.3}})
    write("TINY-20261027.json", {"cells": {"x": 1.0}})
    write("WEEKLYCLASH-20261027.json", {"cells": {"gap_bp": 1.0, "n": 2}})
    write("WEEKCLASH-20261027-screened.json",
          {"delta": [{"column": "gap_bp"}, {"column": "n"}, {"column": "other"}]})
    write("SCREENSOMETHING-20261027.json",
          {"delta": [{"column": "ann_pct"}, {"column": "sharpe"}, {"column": "turnover"}]})
    triage = os.path.join(tmp, "triage.json")
    with io.open(triage, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"evidence_cutoff": "2026-10-27", "rows": [
            {"mode": "alpha", "runner": "run_alpha", "charged_by_repair": True,
             "evidence": {"face_on_disk": "results/e9/ALPHA-20261027.json"}},
            {"mode": "beta", "runner": "run_beta", "charged_by_repair": True,
             "evidence": {"face_on_disk": "results/e9/BETA-20261027.json"}},
            {"mode": "tiny", "runner": "run_tiny", "charged_by_repair": True,
             "evidence": {"face_on_disk": "results/e9/TINY-20261027.json"}},
            {"mode": "weeklyclash", "runner": "run_weeklyclash", "charged_by_repair": True,
             "evidence": {"face_on_disk": "results/e9/WEEKLYCLASH-20261027.json"}},
            {"mode": "immune", "runner": "run_immune", "charged_by_repair": False,
             "evidence": {"face_on_disk": "results/e9/TINY-20261027.json"}},
        ]}, fh)
    return triage, census


def _ledger_fixture(tmp):
    """Hermetic faces for the E127 legs: every shape the ledger must classify."""
    faces = os.path.join(tmp, "results", "e9")
    os.makedirs(faces, exist_ok=True)

    def write(name, obj):
        with io.open(os.path.join(faces, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(obj, fh)

    def screen(names):
        return {"mode": "neutralise_int", "names_in": 1317, "names_out": 1317,
                "names_touched": len(names),
                "names": [{"name": n, "action": a} for n, a in names]}

    def twin(cutoff, repair, refresh, names, exposure=None, pair=True):
        doc = {"study": "fixture", "evidence_cutoff": cutoff,
               "screen_report": screen(names)}
        if pair:
            doc["pair"] = {"summary": {"cells_compared": 68, "cells_moved": repair}}
        if refresh is not None:
            doc["cutoff_control"] = {"old_face": "OLD-20261020.json",
                                     "summary": {"cells_moved": refresh}}
        if exposure is not None:
            doc["ladder_exposure"] = exposure
        return doc

    keep = [("sh510050", "kept-gapped-only")]
    write("TWINBOTHSCREEN-20261027.json",
          twin("2026-10-27", 71, 20, keep + [("sh510020", "neutralise"),
                                             ("sz159915", "neutralise")]))
    write("TWINTIEDSCREEN-20261027.json",
          twin("2026-10-27", 30, 28, keep, {"ladder_row_is_a_control": True}))
    write("TWINREFRESHSCREEN-20261027.json", twin("2026-10-27", 17, 29, keep))
    write("TWINZEROSCREEN-20261027.json", twin("2026-10-27", 5, 0, keep))
    write("TWINLADDERHITSCREEN-20261027.json",
          twin("2026-10-27", 10, 5, keep + [("sh510300", "neutralise")],
               {"ladder_row_is_a_control": True}))
    write("TWINNOREPAIRSCREEN-20261027.json", twin("2026-10-27", None, 4, keep, pair=False))
    write("TWINEMPTYSCREEN-20261027.json", twin("2026-10-27", 0, 0, []))
    write("TWINODDSCREEN-20261027.json", {
        "study": "fixture_odd_denominators", "evidence_cutoff": "2026-10-27",
        "screen_report": screen(keep),
        "pair": {"summary": {"cells_compared": 163, "cells_moved": 90}},
        "cutoff_control": {"old_face": "OLD-20261021.json",
                           "summary": {"cells_compared": 9, "cells_moved": 3}},
    })
    write("SWEEP-20261023-screened.json", {
        "study": "fixture_sweep", "evidence_cutoff": "2026-10-23",
        "spec": {"screen_mode": "neutralise_int"},
        "screen_reports": {"neutralise_int": screen(keep + [("sh510020", "neutralise")]),
                           "drop": screen(keep)},
        "answers": {"delta_cells": 68, "non_zero_delta_cells": 12},
    })
    write("NOSCREEN-20261027.json", {"study": "fixture_no_screen"})
    write("NOCENSUSSCREEN-20261023.json", {
        "study": "fixture_no_census", "evidence_cutoff": "2026-10-23",
        "delta": [{"era": "pre2017", "column": "raw_spread_ann_bp",
                   "delta_neutralise_int": 1.0},
                  {"era": "2017_2020", "column": "raw_spread_ann_bp",
                   "delta_neutralise_int": 0.0}],
    })
    return tmp


def _levelquote_fixture(tmp):
    """A tiny repo: a census source with four producers and four faces on disk."""
    root = tmp
    os.makedirs(os.path.join(root, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(root, "results", "e43_tilt_4member"), exist_ok=True)
    os.makedirs(os.path.join(root, "results", "e79"), exist_ok=True)
    census = (
        "def _daily_helper(curve):\n"
        "    return _daily_rets(curve)\n\n"
        "def run_alpha(outdir):\n"
        '    study = "e901_alpha_levels"\n'
        "    return _monthly_core()\n\n"
        "def run_beta(outdir):\n"
        '    study = "e902_beta_derived"\n'
        "    return _daily_helper(None)\n\n"
        "def run_gamma(outdir):\n"
        '    study = "e903_gamma_leak"\n'
        "    return _daily_helper(None)\n\n"
        "def run_delta(outdir):\n"
        '    study = "e904_delta_unsourced"\n'
        "    return None\n\n"
        "def run_e177(outdir):\n"
        '    study = "e177_tilt3_decomposition_level_offset"\n'
        "    return _daily_helper(None)\n"
    )
    with io.open(os.path.join(root, CENSUS), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(census)

    def face(name, doc):
        path = os.path.join(root, "results", "e43_tilt_4member", name)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")

    face("ALPHA-20261027.json", {
        "study": "e901_alpha_levels", "evidence_cutoff": "2026-10-27",
        "spec": {"moved_tolerance_bp": 0.05},
        "eras": {"pre2017": {"engine_mean_ann_bp": 287.2, "tilt_sd_bp": 687.5,
                             "share_of_ladder_level_pct": 61.9}},
    })
    face("BETA-20261027.json", {
        "study": "e902_beta_derived", "evidence_cutoff": "2026-10-27",
        "eras": {"raw|pre2017": {"published_engine_bp": 287.2,
                                 "decomposition_engine_bp": 258.8,
                                 "level_offset_bp": 28.4,
                                 "offset_left_as_cross_term_bp": 20.1}},
    })
    face("GAMMA-20261027.json", {
        "study": "e903_gamma_leak", "evidence_cutoff": "2026-10-27",
        "eras": {"pre2017": {"decomposition_engine_bp": 100.0}},
    })
    face("DELTA-20261027.json", {
        "study": "e904_delta_unsourced", "evidence_cutoff": "2026-10-27",
        "eras": {"pre2017": {"decomposition_engine_bp": 1.0}},
    })
    face("TILT3SIGNDECOMOFFSET-20261027.json", {
        "study": "e177_tilt3_decomposition_level_offset", "evidence_cutoff": "2026-10-27",
        "eras": {"raw|pre2017": {"published_engine_bp": 287.2,
                                 "decomposition_engine_bp": 258.8,
                                 "level_offset_bp": 28.4,
                                 "ladder_book_level_offset_bp": -57.7}},
    })
    with io.open(os.path.join(root, "results", "e79", "ROUTING-20261027.json"),
                 "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps({"study": "e97_screened_consumer_routing",
                             "evidence_cutoff": "2026-10-27",
                             "rows": [{"mode": "alpha", "published_cells": 3}]},
                            ensure_ascii=False, indent=1) + "\n")
    # The leg publishes into this directory, so a copy of its own output must be
    # skipped rather than counted (self-inclusion is how a leg grows a phantom face).
    with io.open(os.path.join(root, "results", "e79", "DECOMLEVELQUOTES-20261027.json"),
                 "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps({"study": "e180_published_level_quote_audit",
                             "evidence_cutoff": "2026-10-27",
                             "answers": {"collision_gap_spread_bp": 0.7}},
                            ensure_ascii=False, indent=1) + "\n")
    return root


def selftest():
    legs = []

    def chk(name, cond):
        legs.append((name, bool(cond)))

    tmp = tempfile.mkdtemp(prefix="e97_")
    triage, census = _fixture(tmp)

    saved = dict(TWIN_FUNCS)
    TWIN_FUNCS.clear()
    TWIN_FUNCS["run_screenalpha"] = ("screenalpha", "results/e9/SCREENSOMETHING-*.json")
    TWIN_FUNCS["run_screenweek"] = ("screenweek", "results/e9/WEEKCLASH-*-screened.json")
    try:
        face = build(root=tmp, triage=triage, census=census)
    finally:
        TWIN_FUNCS.clear()
        TWIN_FUNCS.update(saved)

    rows = {r["mode"]: r for r in face["rows"]}
    chk("L1 only charged modes are routed", "immune" not in rows and len(rows) == 4)
    chk("L2 code-linked twin covers its base", rows["alpha"]["coverage"] == "covered_twin")
    chk("L3 unlinked mode is not coverage",
        rows["beta"]["coverage"] == "uncovered_column_only")
    chk("L4 tiny face is uncovered and smallest",
        rows["tiny"]["coverage"] == "uncovered" and rows["tiny"]["published_cells"] == 1)
    chk("L5 column collision is labelled non-decisive",
        rows["beta"]["column_overlap_only"] and rows["beta"]["coverage"] != "covered_twin")
    chk("L6 column collision did not become coverage",
        rows["beta"]["twin_legs"] == [])
    chk("L7 ranking is by cells desc",
        [x["published_cells"] for x in face["ranking_uncovered_by_mode"]] ==
        sorted([x["published_cells"] for x in face["ranking_uncovered_by_mode"]], reverse=True))
    chk("L8 runner grouping de-duplicates shared faces",
        face["ranking_uncovered_by_runner"][0]["published_cells_dedup"] ==
        max(g["published_cells_dedup"] for g in face["ranking_uncovered_by_runner"]))
    chk("L9 totals reconcile", face["totals"]["charged_modes"] ==
        face["totals"]["covered_by_twin"] + face["totals"]["covered_twin_by_name"] +
        face["totals"]["uncovered"])
    chk("L10 missing face does not crash the classifier",
        build(root=tmp, triage=triage, census=census)["totals"]["charged_modes"] == 4)
    # L11: a twin whose face glob is absent must not count as coverage
    TWIN_FUNCS.clear()
    TWIN_FUNCS["run_screenalpha"] = ("screenalpha", "results/e9/NOPE-*.json")
    TWIN_FUNCS["run_screenweek"] = ("screenweek", "results/e9/NOPE-*.json")
    try:
        face2 = build(root=tmp, triage=triage, census=census)
    finally:
        TWIN_FUNCS.clear()
        TWIN_FUNCS.update(saved)
    chk("L11 twin without a face on disk is not coverage",
        {r["mode"]: r["coverage"] for r in face2["rows"]}["alpha"] != "covered_twin")
    # L12: call graph finds the link even when the twin is declared later in the file
    graph = call_graph("def run_b(outdir):\n    pass\n\ndef run_screenb(outdir):\n    run_b(1)\n")
    chk("L12 call graph resolves later-defined bases", graph["run_screenb"] == {"run_b"})
    # L13: the name channel covers a twin that builds the face in its own body
    chk("L13 body-built twin covers its base by name",
        rows["weeklyclash"]["coverage"] == "covered_twin_by_name"
        and rows["weeklyclash"]["twin_by_name"][0]["leg"] == "screenweek")
    # L14: the name channel does not leak to unrelated modes
    chk("L14 name channel does not leak", rows["tiny"]["coverage"] == "uncovered"
        and not rows["tiny"]["twin_by_name"])

    # L15: the registry is the only channel this table reads, so a twin function
    # that exists in the census source but is not declared is invisible coverage.
    # E112-E115 were written without being declared and the table reported their
    # runners uncovered while the twin faces sat on disk.
    # the leg reads the REAL census source, not the selftest's temp root (selftest
    # reassigns ROOT, so anchor on this file's own location instead)
    _repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _src = open(os.path.join(_repo, CENSUS), "r", encoding="utf-8", errors="replace").read()
    _twin_named = [n for n in re.findall(r"^def (run_\w+)\(", _src, re.M) if "screen" in n]
    chk("L15 every run_*screen* twin in the census source is declared",
        _twin_named and all(n in TWIN_FUNCS for n in _twin_named))

    # ------------------------------------------------ E127 ledger legs (L16-L27)
    tmp2 = tempfile.mkdtemp(prefix="e127_")
    ledger_root = _ledger_fixture(tmp2)
    TWIN_FUNCS.clear()
    TWIN_FUNCS["run_screenboth"] = ("screenboth", "results/e9/TWINBOTHSCREEN-*.json")
    try:
        led = screen_reach_ledger(root=ledger_root)
    finally:
        TWIN_FUNCS.clear()
        TWIN_FUNCS.update(saved)
    lrow = {r["face"].split("/")[-1]: r for r in led["rows"]}

    both = lrow["TWINBOTHSCREEN-20261027.json"]
    chk("L16 twin publishes both numbers with an ordering label",
        both["repair"]["cells_moved"] == 71 and both["refresh"]["cells_moved"] == 20
        and both["ordering"] == "repair_dominates"
        and both["repair_over_refresh_ratio"] == 3.55)
    chk("L17 equal-sized effects are labelled tied, not a winner",
        lrow["TWINTIEDSCREEN-20261027.json"]["ordering"] == "tied")
    chk("L18 refresh bigger than repair is labelled refresh_dominates",
        lrow["TWINREFRESHSCREEN-20261027.json"]["ordering"] == "refresh_dominates")
    chk("L19 a zero refresh is its own label and no ratio",
        lrow["TWINZEROSCREEN-20261027.json"]["ordering"] == "refresh_zero"
        and lrow["TWINZEROSCREEN-20261027.json"]["repair_over_refresh_ratio"] is None)
    sweep = lrow["SWEEP-20261023-screened.json"]
    chk("L20 sweep generation reads repair from answers and flags the missing control",
        sweep["generation"] == "sweep" and sweep["repair"]["cells_moved"] == 12
        and sweep["refresh"]["cells_moved"] is None
        and "no_cutoff_control" in sweep["flags"]
        and sweep["repair"]["source"] == "answers.non_zero_delta_cells")
    hit = lrow["TWINLADDERHITSCREEN-20261027.json"]
    chk("L21 a neutralised ladder name flips the control flag and is flagged as a contradiction",
        hit["screen"]["ladder_row_is_a_control"] is False
        and hit["screen"]["ladder_names_neutralised"] == ["sh510300"]
        and "ladder_claim_contradicted" in hit["flags"])
    chk("L22 a face no twin declares is annotated, a declared one is not",
        "not_a_declared_twin" in lrow["TWINTIEDSCREEN-20261027.json"]["flags"]
        and lrow["TWINBOTHSCREEN-20261027.json"]["declared_twin_leg"] == "screenboth"
        and "not_a_declared_twin" not in both["flags"])
    chk("L23 a SCREEN-named file that is not a screen face is skipped with a reason",
        any(s["face"].endswith("NOSCREEN-20261027.json")
            and s["reason"] == "not_a_screen_face" for s in led["skipped"]))
    t = led["totals"]
    chk("L24 totals reconcile",
        t["faces_total"] == t["twins"] + t["sweeps"]
        and sum(t["ordering_counts"].values()) == t["faces_total"])
    empty = lrow["TWINEMPTYSCREEN-20261027.json"]
    chk("L25 a face with no neutralised names is a control and does not crash",
        empty["screen"]["names_neutralised"] == 0
        and empty["screen"]["ladder_row_is_a_control"] is True)
    chk("L26 a face with a control but no repair count says so",
        lrow["TWINNOREPAIRSCREEN-20261027.json"]["ordering"] == "no_repair_count")

    # L27: the live leg.  Fixtures prove the plumbing; only the real disk proves the
    # faces still carry the blocks this ledger reads (a fixture-only leg hid reality
    # twice in this repo: r1255 and r1294).
    live = screen_reach_ledger(root=_repo)
    live_by_face = {r["face"]: r for r in live["rows"]}
    # declared_faces comes from the ledger itself: newest_face() resolves patterns against
    # the module ROOT, which build() left pointing at this selftest's temp fixture.
    declared_faces = [r["face"] for r in live["rows"] if r["declared_twin_leg"]]
    missing = [f for f in declared_faces if f not in live_by_face]
    no_repair = sorted(f for f in declared_faces
                       if live_by_face[f]["repair"]["cells_moved"] is None)
    # A declared twin that publishes no repair count is a finding, not a hole: the row must
    # be present and flagged, and the flagged set must be the one the totals count.
    flagged_norepair = sorted(r["face"] for r in live["rows"]
                              if "no_repair_count" in r["flags"])
    chk("L27 every declared twin face on disk is in the ledger; a missing repair count is flagged",
        len(declared_faces) >= 20 and not missing
        and len(declared_faces) - len(no_repair) >= 20
        and flagged_norepair == sorted(set(flagged_norepair))
        and set(no_repair) <= set(flagged_norepair)
        and live["totals"]["faces_without_repair_count"] == len(flagged_norepair))
    # L28: a face with no census is a row with an UNKNOWN ladder verdict, never a control --
    # "no ladder name was neutralised" and "this face never said which names it touched" are
    # different answers, and only the second is what such a face supports.
    odd = lrow["TWINODDSCREEN-20261027.json"]
    chk("L29 a ratio over different cell sets is flagged and kept out of the matched count",
        "denominators_differ" in odd["flags"]
        and odd["repair"]["cells_compared"] == 163
        and odd["refresh"]["cells_compared"] == 9
        and odd["face"] in led["answers"]["faces_with_mismatched_denominators"]
        and sum(led["totals"]["orderings_on_matched_denominators"].values())
        == led["totals"]["faces_with_both_numbers"]
        - led["totals"]["faces_with_mismatched_denominators"])
    nocensus = lrow["NOCENSUSSCREEN-20261023.json"]
    chk("L28 a face without a census is a row with an unknown ladder verdict",
        nocensus["screen"] is None
        and "no_screen_census" in nocensus["flags"]
        and nocensus["repair"]["cells_moved"] == 1
        and nocensus["repair"]["source"] == "delta[non-zero delta rows]"
        and nocensus["face"] in led["answers"]["faces_without_a_screen_census"]
        and led["totals"]["faces_with_screen_census"]
        + led["totals"]["faces_without_screen_census"] == led["totals"]["faces_total"])

    # ----------------------------------------- E180 published-level quote legs
    tmp3 = tempfile.mkdtemp(prefix="e180_")
    lq_root = _levelquote_fixture(tmp3)
    lq = level_quotes(root=lq_root)
    lq_rows = {r["face"].split("/")[-1]: r for r in lq["faces"]}

    chk("L30 the level vocabulary splits anchored / derived / offset / not-a-level",
        level_class("engine_mean_ann_bp") == "anchored"
        and level_class("wide_book_arithmetic_bp") == "derived_daily"
        and level_class("decomposition_engine_bp") == "derived_daily"
        and level_class("arithmetic_vs_geometric_gap_bp") == "offset"
        and level_class("legs_sum_bp") == "arithmetic_of_levels"
        and level_class("engine_ann_diff_bp") == "anchored"
        and level_class("tilt_sd_bp") is None
        and level_class("share_of_ladder_level_pct") is None)
    chk("L31 (era, arm) come off the path, the leaf suffix or nowhere",
        era_arm_of("/eras/raw|pre2017/level_offset_bp") == ("pre2017", "raw")
        and era_arm_of("/eras/pre2017/holdings/raw_level_bp") == ("pre2017", "raw")
        and era_arm_of("/eras/pre2017/holdings/engine_bp_screened") == ("pre2017", "screened")
        and era_arm_of("/answers/total_bp") == (None, None))
    alpha = lq_rows["ALPHA-20261027.json"]
    chk("L32 an anchored face is anchored only and its spec block is not a quote",
        alpha["verdict"] == "anchored_only" and alpha["level_cells"] == 1
        and alpha["cells"].get("anchored") == 1)
    beta = lq_rows["BETA-20261027.json"]
    chk("L33 a derived face that publishes its own offset is joinable, not a leak",
        beta["verdict"] == "quotes_derived_with_offset"
        and beta["offset_joins"][0]["own_offset_bp"] == 28.4
        and beta["offset_joins"][0]["diff_own_minus_e177_bp"] == 0.0
        and beta["producer_uses_daily_terms"])
    chk("L34 a derived face with no offset beside it is the leak this leg exists for",
        lq_rows["GAMMA-20261027.json"]["verdict"] == "quotes_derived_without_offset"
        and "results/e43_tilt_4member/GAMMA-20261027.json"
        in lq["answers"]["faces_quoting_derived_without_an_offset_beside_it"]
        and lq["totals"]["faces_quoting_derived_without_offset"] == 2
        and lq_rows["BETA-20261027.json"]["face"]
        not in lq["answers"]["faces_quoting_derived_without_an_offset_beside_it"])
    chk("L35 an offset that is not the same construct is inventoried, never differenced",
        lq["faces"] and all(c["e177_field"] for r in lq["faces"]
                            for c in r["offset_comparisons"])
        and any(u["reason"] == "not_the_same_construct" for r in lq["faces"]
                for u in r["uncompared_offsets"]))
    chk("L36 totals reconcile with the per-face classes",
        lq["totals"]["level_cells_total"] ==
        sum(r["level_cells"] for r in lq["faces"])
        and lq["totals"]["faces_scanned"] == len(lq["faces"])
        and sum(lq["totals"]["cells_by_class"].values()) ==
        sum(sum(r["cells"].values()) for r in lq["faces"]))
    chk("L36b one field name published from both arithmetics is a collision",
        "decomposition_engine_bp" in lq["answers"]["field_names_published_from_two_arithmetics"]
        and lq["cross_check"]["sum_named_levels"]["decomposition_engine_bp"]["collision"]
        and lq["cross_check"]["sum_named_levels"]["decomposition_engine_bp"]["daily_faces"]
        and lq["cross_check"]["sum_named_levels"]["decomposition_engine_bp"]["monthly_faces"])
    # L36c: a near-constant gap between the two arithmetics is a definitional wedge, not
    # a compounding artifact -- compounding would vary with the era's volatility.
    chk("L36c collision gaps are published per cell and their spread decides the label",
        lq["totals"]["collision_pairs"] == len(lq["cross_check"]["collision_gaps"]) >= 1
        and all(g["daily_face"] != g["monthly_face"]
                for g in lq["cross_check"]["collision_gaps"])
        and (lq["answers"]["collision_gap_spread_bp"] is None
             if len(lq["cross_check"]["collision_gaps"]) < 2 else
             lq["answers"]["collision_gap_spread_bp"] ==
             round(max(g["diff_daily_minus_monthly_bp"]
                       for g in lq["cross_check"]["collision_gaps"])
                   - min(g["diff_daily_minus_monthly_bp"]
                         for g in lq["cross_check"]["collision_gaps"]), 4)))
    chk("L36d this leg does not audit its own published face",
        not any(r["study"] in LEVELQUOTE_EXCLUDE_STUDIES for r in lq["faces"])
        and any(s["reason"] == "this_leg_publishes_here" for s in lq["skipped"]))

    # L37: the live leg.  Fixtures prove the plumbing; only the real disk proves the
    # family still publishes what this audit claims it publishes.  The collision itself
    # is a measurement, not an invariant -- it is reported, not asserted here.
    live_lq = level_quotes(root=_repo)
    live_derived = [r["face"] for r in live_lq["faces"] if r["derived_cells"]]
    live_by_face = {r["face"].split("/")[-1]: r for r in live_lq["faces"]}
    chk("L37 on the real disk every quoting face has a producer and E177 joins resolve",
        len(live_derived) >= 1
        and not live_lq["cross_check"]["faces_without_a_producer_in_the_census_source"]
        and live_by_face["TILT3SIGNDECOMOFFSET-20261027.json"]["verdict"]
        == "quotes_derived_with_offset"
        and live_lq["totals"]["offsets_compared_to_e177"] >= 1
        and live_lq["totals"]["max_abs_offset_diff_bp"] is not None
        and live_lq["totals"]["faces_quoting_derived_without_offset"] == 0)

    # ---- E188 label duty ---------------------------------------------------------
    # Fixture numbers are the REAL published pair on two eras, so the legs pin the
    # identity a reader depends on rather than an invented round number.
    lf = os.path.join(tmp, "labelduty")
    os.makedirs(os.path.join(lf, "results", "e43_tilt_4member"), exist_ok=True)
    os.makedirs(os.path.join(lf, "results", "e79"), exist_ok=True)

    def _lface(sub, name, doc):
        p = os.path.join(lf, "results", sub, name)
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")

    _lface("e43_tilt_4member", "TILT3SIGNBOOKSPLIT-20261027.json", {
        "study": "e176_book_split", "evidence_cutoff": "2026-10-27",
        "eras": {
            "pre2017": {"published_engine_bp_raw": 287.2,
                        "published_engine_bp_screened": 287.2,
                        "decomposition_engine_bp_raw": 261.76,
                        "decomposition_engine_bp_screened": 261.76,
                        "decomposition_level_offset_bp": {"raw": -25.44,
                                                          "screened": -25.44}},
            "2021_2023": {"published_engine_bp_raw": 251.1,
                          "published_engine_bp_screened": 280.4,
                          "decomposition_engine_bp_raw": 255.87,
                          "decomposition_engine_bp_screened": 286.07,
                          "decomposition_level_offset_bp": {"raw": 4.77,
                                                            "screened": 5.67}},
        },
    })
    _lface("e43_tilt_4member", "TILT3SIGNDECOMOFFSET-20261027.json", {
        "study": "e177_decom_offset", "evidence_cutoff": "2026-10-27",
        "eras": {
            "raw|pre2017": {"arm": "raw", "era": "pre2017",
                            "published_engine_bp": 287.2,
                            "decomposition_engine_bp": 258.8365,
                            "level_offset_bp": 28.41},
            "screened|pre2017": {"arm": "screened", "era": "pre2017",
                                 "published_engine_bp": 287.2,
                                 "decomposition_engine_bp": 258.8365,
                                 "level_offset_bp": 28.41},
            "raw|2021_2023": {"arm": "raw", "era": "2021_2023",
                              "published_engine_bp": 251.1,
                              "decomposition_engine_bp": 252.2442,
                              "level_offset_bp": -1.1442},
            "screened|2021_2023": {"arm": "screened", "era": "2021_2023",
                                   "published_engine_bp": 280.4,
                                   "decomposition_engine_bp": 282.4866,
                                   "level_offset_bp": -2.0866},
        },
    })
    _lface("e79", "LEVELWEDGE-20261027.json", {
        "study": "e185_level_wedge", "evidence_cutoff": "2026-10-27",
        "eras": {
            "raw|pre2017": {"arm": "raw", "era": "pre2017",
                            "rebalance_cost_term_bp": 2.9207},
            "screened|pre2017": {"arm": "screened", "era": "pre2017",
                                 "rebalance_cost_term_bp": 2.9207},
            "raw|2021_2023": {"arm": "raw", "era": "2021_2023",
                              "rebalance_cost_term_bp": 3.6208},
            "screened|2021_2023": {"arm": "screened", "era": "2021_2023",
                                   "rebalance_cost_term_bp": 3.5823},
        },
    })
    # An owner claiming nothing, a face claiming gross, and a face claiming net while
    # publishing the gross reading -- the three states a sweep must not conflate.
    _lface("e43_tilt_4member", "SILENT-20261027.json", {
        "study": "e901_silent_gross", "evidence_cutoff": "2026-10-27",
        "eras": {"pre2017": {"decomposition_engine_bp_unlabelled": 261.76}}})
    _lface("e43_tilt_4member", "HELD-20261027.json", {
        "study": "e902_declared_gross", "evidence_cutoff": "2026-10-27",
        "honest": ["this level is GROSS of the rebalance fee"],
        "eras": {"2021_2023": {"decomposition_engine_bp_declared": 255.87}}})
    _lface("e43_tilt_4member", "WRONG-20261027.json", {
        "study": "e903_declared_net", "evidence_cutoff": "2026-10-27",
        "honest": ["this level is net of the fee"],
        "eras": {"pre2017": {"decomposition_engine_bp_wrong": 261.76}}})

    lfx = label_duty(base=lf)
    lf_rows = {(r["era"], r["arm"]): r for r in lfx["wedge"]}
    chk("L38 gross minus net is the fee and the two offsets differ by it",
        len(lf_rows) == 4
        and max(abs(r["residual_after_fee_bp"]) for r in lf_rows.values()) <= 0.01
        and all(abs(r["offset_stance_gap_bp"] - r["fee_bp"]) <= 0.01
                for r in lf_rows.values() if r["offset_stance_gap_bp"] is not None))
    chk("L39 the offsets the two faces publish are one construct plus the fee",
        lfx["totals"]["published_offsets_checked"] == 4
        and lfx["totals"]["published_offsets_differ_by_the_fee"] == 4)
    chk("L40 a delta is fee-neutral only when both arms carry the same fee",
        {d["era"]: d["delta_restatement_shift_bp"] for d in lfx["delta_restatement"]}
        == {"pre2017": 0.0, "2021_2023": 0.0385})
    chk("L41 stance_of has four states and no default",
        [stance_of(x) for x in ("nothing here", "gross of the fee",
                                "net of the fee", "gross but net of the fee")]
        == ["unlabelled", "gross_only", "net_only", "both"])
    chk("L42 the sweep separates silent / declared / mis-declared faces",
        {r["study"]: r["label_class"] for r in lfx["family"]}.get("e901_silent_gross")
        == "unlabelled"
        and {r["study"]: r["label_class"] for r in lfx["family"]}.get(
            "e902_declared_gross") == "labelled"
        and {r["study"]: r["label_class"] for r in lfx["family"]}.get(
            "e903_declared_net") == "mislabeled")
    chk("L43 inside_the_wedge is per stance and inclusive at the boundary",
        lf_rows[("pre2017", "raw")]["inside_the_wedge"] is False
        and lf_rows[("2021_2023", "raw")]["inside_stances"] == ["net"]
        and lf_rows[("2021_2023", "screened")]["inside_stances"] == ["net"]
        and bool(wedge_rows({("raw", "e"): 3.0},
                            {("raw", "e"): 10.0}, {("raw", "e"): 10.0},
                            {("raw", "e"): 13.0})[0]["inside_the_wedge"]
                 or wedge_rows({("raw", "e"): 3.0}, {("raw", "e"): 10.0},
                               {("raw", "e"): 10.0}, {("raw", "e"): 10.0})
                 [0]["inside_the_wedge"]) is True)
    chk("L44 rel_shift_pct is a percent, not a fraction",
        1.0 < lf_rows[("pre2017", "raw")]["rel_shift_pct"] < 1.3)
    live_ld = label_duty(base=_repo)
    live_ld_prod = {r["face"].split("/")[-1]: r for r in live_ld["family"]}
    chk("L45 on the real disk the producers are silent and the audit face is the label",
        live_ld["totals"]["cells"] >= 10
        and (live_ld["totals"]["max_abs_residual_after_fee_bp"] or 0) <= 0.01
        and live_ld["totals"]["cells_quoting_sign_flip_with_stance"] == 0
        and live_ld_prod["TILT3SIGNBOOKSPLIT-20261027.json"]["label_class"] == "unlabelled"
        and live_ld_prod["TILT3SIGNDECOMOFFSET-20261027.json"]["label_class"] == "unlabelled"
        and live_ld_prod["LEVELWEDGE-20261027.json"]["label_class"] == "labelled")

    # ---- E193 delta build stance -------------------------------------------------
    df = os.path.join(tmp, "deltastance")
    os.makedirs(os.path.join(df, "results", "e43_tilt_4member"), exist_ok=True)
    os.makedirs(os.path.join(df, "results", "e79"), exist_ok=True)

    def _dface(sub, name, doc):
        p = os.path.join(df, "results", sub, name)
        with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")

    _dface("e43_tilt_4member", "TILT3SIGNBOOKSPLIT-20261027.json", {
        "study": "e176_book_split", "evidence_cutoff": "2026-10-27",
        "eras": {
            "pre2017": {"published_engine_bp_raw": 287.2,
                        "published_engine_bp_screened": 287.2,
                        "wide_book_bp_raw": 1279.97, "wide_book_bp_screened": 1279.97,
                        "ladder_book_bp_raw": 1018.21, "ladder_book_bp_screened": 1018.21,
                        "decomposition_engine_bp_raw": 261.76,
                        "decomposition_engine_bp_screened": 261.76},
            "2021_2023": {"published_engine_bp_raw": 251.1,
                          "published_engine_bp_screened": 280.4,
                          "wide_book_bp_raw": -667.681, "wide_book_bp_screened": -637.477,
                          "ladder_book_bp_raw": -922.64, "ladder_book_bp_screened": -923.54,
                          "decomposition_engine_bp_raw": 255.87,
                          "decomposition_engine_bp_screened": 286.07},
        },
    })
    _dface("e43_tilt_4member", "TILT3SIGNDECOMOFFSET-20261027.json", {
        "study": "e177_decom_offset", "evidence_cutoff": "2026-10-27",
        "eras": {
            "raw|pre2017": {"arm": "raw", "era": "pre2017",
                            "decomposition_engine_bp": 258.8365},
            "screened|pre2017": {"arm": "screened", "era": "pre2017",
                                 "decomposition_engine_bp": 258.8365},
            "raw|2021_2023": {"arm": "raw", "era": "2021_2023",
                              "decomposition_engine_bp": 252.2442},
            "screened|2021_2023": {"arm": "screened", "era": "2021_2023",
                                   "decomposition_engine_bp": 282.4866},
        },
    })
    _dface("e79", "LEVELWEDGE-20261027.json", {
        "study": "e185_level_wedge", "evidence_cutoff": "2026-10-27",
        "eras": {
            "raw|pre2017": {"arm": "raw", "era": "pre2017",
                            "rebalance_cost_term_bp": 2.9207},
            "screened|pre2017": {"arm": "screened", "era": "pre2017",
                                 "rebalance_cost_term_bp": 2.9207},
            "raw|2021_2023": {"arm": "raw", "era": "2021_2023",
                              "rebalance_cost_term_bp": 3.6208},
            "screened|2021_2023": {"arm": "screened", "era": "2021_2023",
                                   "rebalance_cost_term_bp": 3.5823},
        },
    })
    # One face carrying all four states a delta sweep must separate: a published-level
    # delta printed with the opposite sign, an unnamed-operand delta that is really a
    # fee-free book delta, a zero delta, and a cross-measure delta whose operands are
    # siblings of its own era cell.
    _dface("e43_tilt_4member", "DELTAMIX-20261027.json", {
        "study": "e910_delta_mix", "evidence_cutoff": "2026-10-27",
        "eras": {"2021_2023": {
            "published_engine_bp_delta": 29.3,
            "net_delta_bp": 30.204,
            "engine_delta_residual_bp": 0.0,
            "spread_raw_ann_bp": 500.0,
            "arithmetic_vs_geometric_gap_bp": 81.0,
            "engine_ann_diff_bp": 419.0,
        }}})

    dfx = deltastance(base=df)
    d_rows = {(r["field"].split("/")[-1], r["era"]): r for r in dfx["rows"]}
    chk("L46 delta_build_family binds by name and the rule order matters",
        delta_build_family("published_engine_bp_delta") == "from_two_published_levels"
        and delta_build_family("wide_book_delta_bp") == "book_pair"
        and delta_build_family("net_delta_bp") == "unnamed_operand"
        and delta_build_family("gross_abs_delta_bp") == "abs_sum_of_name_deltas"
        and delta_build_family("something_else_bp") == "unbound")
    chk("L47 a delta printed as the negated construct is a sign convention",
        d_rows[("published_engine_bp_delta", "2021_2023")]["verification"]
        == "reproduces_flipped_sign"
        and d_rows[("published_engine_bp_delta", "2021_2023")]["residual_bp"] == 0.0
        and all(abs(r["residual_bp"]) <= 0.01 for r in dfx["rows"] if r["residual_bp"]))
    chk("L48 a zero delta is never reported as a reproduction",
        d_rows[("engine_delta_residual_bp", "2021_2023")]["verification"]
        == "not_checkable_zero")
    chk("L49 a cross-measure delta reproduces from its own era cell's siblings",
        d_rows[("engine_ann_diff_bp", "2021_2023")]["verification"]
        == "reproduces_in_cell"
        and any(p["minus"] == "spread_raw_ann_bp"
                and p["plus"] == "arithmetic_vs_geometric_gap_bp"
                for p in d_rows[("engine_ann_diff_bp", "2021_2023")]["reproduced_in_cell"]))
    chk("L50 a net-named fee-free delta is flagged and keeps its declared family",
        d_rows[("net_delta_bp", "2021_2023")]["build_family"] == "unnamed_operand"
        and d_rows[("net_delta_bp", "2021_2023")]["matched_family"] == "book_pair"
        and d_rows[("net_delta_bp", "2021_2023")]["effective_fee_content"] == "fee_free"
        and dfx["totals"]["cells_named_net_or_gross_but_fee_free"] == 1
        and dfx["totals"]["nested_delta_cells"] == 0)
    live_ds = deltastance(base=_repo)
    ds_fields = {(r["field"].split("/")[-1], r["era"]): r for r in live_ds["rows"]}
    chk("L51 on the real disk no published delta is built across stances",
        live_ds["totals"]["era_level_delta_cells"] >= 60
        and live_ds["totals"]["cross_stance_cells"] == 0
        and live_ds["totals"]["cells_contradicted"] == 0
        and live_ds["totals"]["sign_convention_is_uniform"] is True
        and live_ds["totals"]["max_restatement_shift_bp"] <= 0.08
        and live_ds["totals"]["nested_delta_cells"] > 100
        and ds_fields[("net_delta_bp", "2024_now")]["effective_fee_content"] == "fee_free")

    # E196 near-zero sign census: fixture first, then the live disk.
    nz = tmpdir = None
    try:
        tmpdir = tempfile.mkdtemp(prefix="nz196-")
        nzfaces = os.path.join(tmpdir, "results", "e9")
        os.makedirs(nzfaces, exist_ok=True)

        def _nzwrite(name, obj):
            with io.open(os.path.join(nzfaces, name), "w", encoding="utf-8", newline="\n") as fh:
                json.dump(obj, fh)

        _nzwrite("MIX-20261029.json", {"evidence_cutoff": "2026-10-29", "eras": {"full": {"base": {
            "arith_bp": 0.074333, "comp_bp": -38.198705}, "hair": {
            "arith_bp": 12.0, "comp_bp": -38.198705}, "quotfloat": {
            "arith_bp": 9.0, "comp_bp": 100.0}, "tinygap": {
            "arith_bp": 3.0, "comp_bp": -0.4}, "zero_gap": {
            "arith_bp": 5.0, "comp_bp": 0.0}}}})
        _nzwrite("WHEN-20261029.json", {"evidence_cutoff": "2026-10-29", "base": {"arith_bp": 5.0,
                                                                        "comp_bp": 100.0}})
        _nzwrite("STATUS-20261014.json", {"evidence_cutoff": "panel 2026-10-14 (bars 10-15 due 15:30)",
                                          "note": "a status face carries prose in the cutoff field"})
        nz = nearzero_sign_sweep(base=tmpdir)
        nzrows = {r["path"]: r for r in nz["rows"]}
        chk("L58 a prose evidence_cutoff never wins the cutoff over a real date",
            nz["evidence_cutoff"] == "2026-10-29")
        chk("L52 a level two orders below its gap is classified a hair, not a direction",
            nzrows["/eras/full/base"]["class"] == "sign_is_hair"
            and nzrows["/eras/full/base"]["signs_disagree"] is True
            and nzrows["/eras/full/base"]["level_over_gap"] < 0.01)
        chk("L53 the same pair clears the floor once the level is large against it",
            nzrows["/eras/full/hair"]["class"] == "sign_quotable"
            and nzrows["/eras/full/hair"]["signs_disagree"] is True)
        chk("L54 a gap under the declared floor answers no sign question at all",
            nzrows["/eras/full/tinygap"]["class"] == "level_agrees"
            and nzrows["/eras/full/zero_gap"]["level_over_gap"] is None
            and nzrows["/eras/full/zero_gap"]["class"] == "level_agrees")
        chk("L55 a 9/100 level is quotable at a 5% floor and would need a 180bp gap at 10%",
            nzrows["/eras/full/quotfloat"]["class"] == "sign_quotable"
            and abs(nzrows["/eras/full/quotfloat"]["gap_needed_for_quotable_bp"] - 180.0) < 1e-6)
        chk("L56 only sign-disagreeing hairs enter the published defect list",
            nz["answers"]["disagreements_whose_sign_is_a_hair"] == 1
            and nz["answers"]["hair_disagreements"][0]["path"] == "/eras/full/base")
    finally:
        if tmpdir and os.path.isdir(tmpdir):
            shutil.rmtree(tmpdir, ignore_errors=True)

    live_nz = nearzero_sign_sweep(base=_repo)
    anchor = [r for r in live_nz["rows"]
              if r["face"].endswith("LADDERDROPRULE-20261027.json")
              and r["path"].endswith("/full/drops/0/base")]
    chk("L57 on the real disk the E195 anchor pair is a printed hair, not a reversal",
        bool(anchor)
        and anchor[0]["class"] == "sign_is_hair"
        and anchor[0]["signs_disagree"] is True
        and abs(anchor[0]["level_bp"] - 0.074333) < 1e-6
        and live_nz["answers"]["cells"] >= 4)

    ok = sum(1 for _, c in legs if c)
    for name, cond in legs:
        print(("PASS " if cond else "FAIL ") + name)
    print("selftest: %d/%d" % (ok, len(legs)))
    return 0 if ok == len(legs) else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        md = None
        if "--md" in argv:
            md = "research/digests/DIGEST-20261027-e97-screened-consumer-routing.md"
        return run(publish="--publish" in argv, md=md)
    if cmd == "screenreach":
        return run_screenreach(publish="--publish" in argv)
    if cmd == "levelquotes":
        return run_levelquotes(publish="--publish" in argv)
    if cmd == "labelduty":
        return run_labelduty(publish="--publish" in argv)
    if cmd == "deltastance":
        return run_deltastance(publish="--publish" in argv)
    if cmd == "nearzerosign":
        return run_nearzerosign(publish="--publish" in argv)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))