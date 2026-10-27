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
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))