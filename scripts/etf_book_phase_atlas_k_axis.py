"""The phase atlas read on five buffer rungs: is the verdict a property of the book, or of k?

Every rung of the buffer family is burned on the SAME 280 phase calendars and publishes the
same frozen comparison -- between-cell spread against the median cell band. Each rung is
therefore an independent measurement of one sentence: "config ordering exceeds phase noise".

This face does not burn anything and does not re-judge any cell. It puts the rungs side by
side at one evidence cutoff and asks three questions the single-rung faces cannot answer:

  * does the rung verdict survive the knob (does "ordering exceeds noise" hold at k=0.02 and
    at k=0.40, on the same closes)?
  * how far does the money move with k (the two authoritative cells: the production card and
    the executable ticket)?
  * is the cell ranking the same on every rung, or does the winner change with the knob?

The rule is frozen here, before the first read, and echoed into the payload so a later
"small adjustment" cannot pass for the same rule.

Usage:
  python scripts/etf_book_phase_atlas_k_axis.py run
  python scripts/etf_book_phase_atlas_k_axis.py check
  python scripts/etf_book_phase_atlas_k_axis.py --selftest
"""

from __future__ import annotations

import hashlib
import json
import os
import statistics
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
OUT = os.path.join(RES, "etf_book_phase_atlas_k_axis.json")

# The family the pool named (r2125 registered the k10/k20 rungs; k30 is an older generation
# and is excluded by cutoff rather than by hand -- see RULE R1).
RUNGS = [
    (0.02, "etf_book_phase_atlas_buffer_k02.json"),
    (0.05, "etf_book_phase_atlas_buffer_k05.json"),
    (0.10, "etf_book_phase_atlas_buffer_k10.json"),
    (0.20, "etf_book_phase_atlas_buffer_k20.json"),
    (0.30, "etf_book_phase_atlas_buffer_k30.json"),
    (0.40, "etf_book_phase_atlas_buffer_k40.json"),
]

AUTHORITATIVE = ("production_card", "executable_ticket")
TOP_N = 3

SCHEMA = "etf-book-phase-atlas-k-axis/v1"


def _sha1(path):
    with open(path, "rb") as fh:
        return hashlib.sha1(fh.read()).hexdigest()


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def classify(spread, band):
    """R2: the panels' own rule, re-derived from the two published numbers."""
    if spread is None or band is None:
        return "UNPRICED"
    return "EXCEEDS" if float(spread) >= float(band) else "WITHIN"


def _panel_verdict_word(face):
    word = (face.get("verdict") or "").strip()
    if word.endswith("EXCEEDS_PHASE_NOISE") and "WITHIN" not in word:
        return "EXCEEDS"
    if "WITHIN_PHASE_NOISE" in word:
        return "WITHIN"
    return "UNKNOWN:" + (word or "empty")


def read_rungs(result_dir):
    """Read every rung that exists. Panels are never edited; a missing file is named."""
    rows, missing = [], []
    for k, name in RUNGS:
        path = os.path.join(result_dir, name)
        if not os.path.exists(path):
            missing.append({"buffer_k": k, "path": name, "why": "panel absent"})
            continue
        face = _load(path)
        grid = face.get("grid") or {}
        audit = face.get("audit") or {}
        spread = grid.get("between_cell_spread_pp")
        band = grid.get("median_cell_band_pp")
        rows.append({
            "buffer_k": k,
            "panel": name,
            "sha1": _sha1(path),
            "evidence_cutoff": face.get("evidence_cutoff"),
            "phases_total": grid.get("phases_total"),
            "cells": grid.get("cells"),
            "spread_pp": spread,
            "band_pp": band,
            "excess_pp": (None if spread is None or band is None
                          else round(float(spread) - float(band), 4)),
            "re_derived": classify(spread, band),
            "published": _panel_verdict_word(face),
            "audit_buffer_k": audit.get("buffer_k"),
            "audit_cost": audit.get("cost"),
            "cells_detail": face.get("per_cell") or [],
            "authoritative": face.get("authoritative_cells") or {},
        })
    return rows, missing


def pick_cutoff(rows):
    """R1: compare only rungs on one evidence cutoff -- the modal one, ties to the newest."""
    counts = {}
    for row in rows:
        key = row.get("evidence_cutoff") or "?"
        counts[key] = counts.get(key, 0) + 1
    if not counts:
        return None
    best = max(counts.values())
    cands = [k for k, n in counts.items() if n == best]
    return sorted(cands)[-1]


def build_payload(result_dir):
    rows, missing = read_rungs(result_dir)
    cutoff = pick_cutoff(rows)
    on_cutoff = [r for r in rows if (r.get("evidence_cutoff") or "?") == cutoff]
    off_cutoff = [{"buffer_k": r["buffer_k"], "panel": r["panel"],
                   "why": "evidence_cutoff %r is not the rung cutoff %r"
                          % (r.get("evidence_cutoff"), cutoff)}
                  for r in rows if (r.get("evidence_cutoff") or "?") != cutoff]

    # R2b: a panel whose own word contradicts its own two numbers is named, not smoothed.
    contradictions = [{"buffer_k": r["buffer_k"], "published": r["published"],
                       "re_derived": r["re_derived"]}
                      for r in on_cutoff
                      if r["published"] in ("EXCEEDS", "WITHIN")
                      and r["re_derived"] in ("EXCEEDS", "WITHIN")
                      and r["published"] != r["re_derived"]]

    words = sorted({r["re_derived"] for r in on_cutoff})
    if len(on_cutoff) < 2:
        verdict_word = "NOT_COMPARABLE_FEWER_THAN_TWO_RUNGS"
    elif words == ["EXCEEDS"]:
        verdict_word = "VERDICT_IS_K_ROBUST_ORDERING_EXCEEDS"
    elif words == ["WITHIN"]:
        verdict_word = "VERDICT_IS_K_ROBUST_ORDERING_WITHIN_NOISE"
    else:
        verdict_word = "K_AXIS_DECIDES_THE_VERDICT"

    # R4: how far the two authoritative cells move with the knob.
    cell_response = {}
    for name in AUTHORITATIVE:
        series = []
        for r in on_cutoff:
            cell = (r.get("authoritative") or {}).get(name) or {}
            series.append({
                "buffer_k": r["buffer_k"],
                "n_hold": cell.get("n_hold"),
                "rebal": cell.get("rebal"),
                "median_cagr_pp": cell.get("median_cagr_pp"),
                "band_pp": cell.get("band_pp"),
                "min_cagr_pp": cell.get("min_cagr_pp"),
                "max_cagr_pp": cell.get("max_cagr_pp"),
                "phases": cell.get("phases"),
            })
        vals = [s["median_cagr_pp"] for s in series
                if isinstance(s.get("median_cagr_pp"), (int, float))]
        cell_response[name] = {
            "series": series,
            "range_pp": (round(max(vals) - min(vals), 4) if len(vals) >= 2 else None),
            "min_pp": min(vals) if vals else None,
            "max_pp": max(vals) if vals else None,
        }

    # R5: does the winner survive the knob?
    top_sets, per_rung = [], []
    for r in on_cutoff:
        detail = [c for c in r["cells_detail"] if c.get("judged")]
        ranked = sorted(detail, key=lambda c: (-float(c.get("median_cagr_pp") or 0),
                                              int(c.get("rebal") or 0),
                                              int(c.get("n_hold") or 0)))
        top = [(int(c["n_hold"]), int(c["rebal"])) for c in ranked[:TOP_N]]
        top_sets.append(tuple(top))
        per_rung.append({"buffer_k": r["buffer_k"], "top": [list(t) for t in top],
                         "ranked": [[int(c["n_hold"]), int(c["rebal"]),
                                     c.get("median_cagr_pp")] for c in ranked]})
    identical = len(set(top_sets)) == 1 if top_sets else None
    shared = None
    if top_sets:
        sets = [set(t) for t in top_sets]
        common = set.intersection(*sets) if len(sets) > 1 else set(sets[0])
        shared = sorted([list(t) for t in common])

    # R6: the cadence ladder -- does R10 > R20 > R40 hold bucket-against-bucket, and do the
    # bucket ranges overlap? A verdict that flips cannot be trusted; a ladder whose worst cell
    # still beats the next bucket's best cell on every rung can.
    cadence, separating = [], 0
    for r in on_cutoff:
        buckets = {}
        for c in r["cells_detail"]:
            if not c.get("judged"):
                continue
            rebal = int(c.get("rebal") or 0)
            buckets.setdefault(rebal, []).append(float(c.get("median_cagr_pp") or 0.0))
        rung = {"buffer_k": r["buffer_k"], "buckets": {}}
        for rebal in sorted(buckets):
            vals = buckets[rebal]
            rung["buckets"][rebal] = {
                "cells": len(vals),
                "median_pp": round(statistics.median(vals), 4),
                "best_pp": round(max(vals), 4),
                "worst_pp": round(min(vals), 4),
            }
        order = sorted(buckets)
        sep = bool(order)
        for lo, hi in zip(order, order[1:]):
            if not buckets[lo] or not buckets[hi] or min(buckets[lo]) <= max(buckets[hi]):
                sep = False
                break
        rung["ladder_separates"] = sep
        if sep:
            separating += 1
        cadence.append(rung)

    # per-cell spread across rungs, for the record (12 cells, one row each)
    cell_rows = {}
    for r in on_cutoff:
        for c in r["cells_detail"]:
            key = "%dx%d" % (int(c.get("n_hold") or 0), int(c.get("rebal") or 0))
            cell_rows.setdefault(key, {})["k%g" % r["buffer_k"]] = c.get("median_cagr_pp")
    for key, vals in cell_rows.items():
        nums = [v for v in vals.values() if isinstance(v, (int, float))]
        vals["range_pp"] = round(max(nums) - min(nums), 4) if len(nums) >= 2 else None
        vals["median_pp"] = round(statistics.median(nums), 4) if nums else None

    return {
        "schema": SCHEMA,
        "face": "results/etf_book_phase_atlas_k_axis.json",
        "question": ("every rung of the buffer family is burned on the same 280 phase calendars "
                     "and publishes one sentence -- 'config ordering exceeds phase noise'. "
                     "Does that sentence survive the knob, how far does the money move with k, "
                     "and is the winner the same cell on every rung?"),
        "rule": {
            "frozen": "written before the first read (r1350 line)",
            "R1_cutoff": "only rungs whose evidence_cutoff equals the modal cutoff are compared; "
                         "every excluded rung is named with the reason",
            "R2_re_derive": "EXCEEDS iff between_cell_spread_pp >= median_cell_band_pp -- the "
                            "same rule the panels publish, recomputed from their own two numbers",
            "R2b_contradiction": "a panel whose published word contradicts its own numbers is "
                                 "named in contradictions, never smoothed",
            "R4_cell_response": "for the production card and the executable ticket: min / max / "
                                "range of median_cagr_pp across rungs at one cutoff",
            "R5_winner": "rank the judged cells by median_cagr_pp within each rung; keep the "
                         "top-%d; report whether the sets are identical and what they share"
                         % TOP_N,
            "no_number_is_invented": "a missing rung is a named hole, never a zero",
        },
        "rung_cutoff": cutoff,
        "rungs": [r for r in on_cutoff],
        "excluded": off_cutoff + missing,
        "contradictions": contradictions,
        "verdict_by_rung": [{"buffer_k": r["buffer_k"], "spread_pp": r["spread_pp"],
                             "band_pp": r["band_pp"], "excess_pp": r["excess_pp"],
                             "verdict": r["re_derived"]} for r in on_cutoff],
        "verdict_word": verdict_word,
        "rungs_exceeding": sum(1 for r in on_cutoff if r["re_derived"] == "EXCEEDS"),
        "rungs_within": sum(1 for r in on_cutoff if r["re_derived"] == "WITHIN"),
        "rungs_compared": len(on_cutoff),
        "cell_response": cell_response,
        "winner": {"top_n": TOP_N, "identical_across_rungs": identical,
                   "shared_cells": shared, "per_rung": per_rung},
        "cadence_ladder": {
            "rule": "R6: within one rung, bucket A sits above bucket B only if A's worst cell "
                    "beats B's best cell -- a range that overlaps is not a separation",
            "rungs_separating": separating,
            "rungs_compared": len(on_cutoff),
            "verdict": ("CADENCE_LADDER_IS_K_ROBUST" if on_cutoff and separating == len(on_cutoff)
                        else ("CADENCE_LADDER_NOT_ROBUST" if on_cutoff else "NOT_COMPARABLE")),
            "per_rung": cadence,
        },
        "cell_table": cell_rows,
        "evidence_cutoff": cutoff,
        "inputs": {r["panel"]: r["sha1"] for r in on_cutoff},
        "controls": [
            "the rung cutoff is the modal one, so an older generation cannot pass as a rung",
            "a panel's own word is re-derived from its own two numbers (two independent reads)",
            "the winner is ranked per rung, so a cell that wins on one rung only is visible",
        ],
    }


def run(result_dir=RES, out_path=OUT):
    payload = build_payload(result_dir)
    text = json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=False)
    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    os.replace(tmp, out_path)
    return payload


def check(result_dir=RES, out_path=OUT):
    """Two failure kinds, kept apart (r1850/r1934): a moved input is STALE (paid re-run),
    the face disagreeing with its own inputs is CHECK FAILED."""
    if not os.path.exists(out_path):
        print("STALE: face missing at %s" % out_path)
        return 3
    face = _load(out_path)
    moved = []
    for name, sha in (face.get("inputs") or {}).items():
        path = os.path.join(result_dir, name)
        if not os.path.exists(path):
            moved.append("%s missing" % name)
        elif _sha1(path) != sha:
            moved.append("%s moved" % name)
    if moved:
        print("STALE: input faces moved since this face priced them (%s)" % ", ".join(moved))
        return 3
    fresh = build_payload(result_dir)
    for key in ("verdict_word", "verdict_by_rung", "rungs_exceeding", "rungs_within",
                "cell_response", "winner", "rung_cutoff", "contradictions"):
        if json.dumps(face.get(key), sort_keys=True) != json.dumps(fresh.get(key),
                                                                  sort_keys=True):
            print("CHECK FAILED: %s does not re-derive from the same inputs" % key)
            return 1
    print("CHECK OK: %s, %d rungs on cutoff %s, verdict %s"
          % (os.path.basename(out_path), fresh["rungs_compared"],
             fresh["rung_cutoff"], fresh["verdict_word"]))
    return 0


# ---------------------------------------------------------------- selftest

def _fixture(directory, k, cutoff, spread, band, top_cells, whose=None):
    detail = []
    for n_hold, rebal, cagr in top_cells:
        detail.append({"n_hold": n_hold, "rebal": rebal, "judged": True,
                       "phases": 20, "median_cagr_pp": cagr})
    face = {
        "evidence_cutoff": cutoff,
        "verdict": "CONFIG_ORDER_EXCEEDS_PHASE_NOISE" if spread >= band
                   else "CONFIG_ORDER_WITHIN_PHASE_NOISE",
        "grid": {"cells": len(detail), "judged_cells": len(detail), "phases_total": 280,
                 "between_cell_spread_pp": spread, "median_cell_band_pp": band},
        "per_cell": detail,
        "audit": {"buffer_k": k, "cost": 0.001},
        "authoritative_cells": {
            "production_card": {"n_hold": 12, "rebal": 20, "judged": True,
                                "median_cagr_pp": 9.0 + 10 * k, "band_pp": 7.0,
                                "min_cagr_pp": 4.0, "max_cagr_pp": 12.0, "phases": 20},
            "executable_ticket": {"n_hold": 5, "rebal": 20, "judged": True,
                                  "median_cagr_pp": 8.0 + 10 * k, "band_pp": 6.0,
                                  "min_cagr_pp": 3.0, "max_cagr_pp": 11.0, "phases": 20},
        },
    }
    if whose:
        face["verdict"] = whose
    name = "etf_book_phase_atlas_buffer_k%02d.json" % round(k * 100)
    with open(os.path.join(directory, name), "w", encoding="utf-8") as fh:
        json.dump(face, fh)
    return name


def selftest():
    legs = []

    def leg(name, ok, why=""):
        legs.append((name, bool(ok), why))

    def group(fn):
        with tempfile.TemporaryDirectory() as tmp:
            fn(tmp)

    def case_mixed(tmp):
        _fixture(tmp, 0.02, "2026-11-25", 5.0, 6.0, [(3, 10, 11.0), (5, 20, 9.0), (12, 20, 8.0)])
        _fixture(tmp, 0.05, "2026-11-25", 7.0, 6.0, [(3, 10, 11.1), (5, 20, 9.1), (12, 20, 8.1)])
        pay = build_payload(tmp)
        leg("two rungs that disagree produce K_AXIS_DECIDES_THE_VERDICT",
            pay["verdict_word"] == "K_AXIS_DECIDES_THE_VERDICT", pay["verdict_word"])
        leg("the disagreeing rungs are counted on both sides",
            pay["rungs_exceeding"] == 1 and pay["rungs_within"] == 1,
            "%s/%s" % (pay["rungs_exceeding"], pay["rungs_within"]))
        leg("the cell response reports a range, not a single number",
            pay["cell_response"]["production_card"]["range_pp"] is not None
            and pay["cell_response"]["production_card"]["range_pp"] > 0,
            repr(pay["cell_response"]["production_card"]["range_pp"]))
        leg("a cadence ladder whose worst cell beats the next bucket's best is called robust",
            pay["cadence_ladder"]["verdict"] == "CADENCE_LADDER_IS_K_ROBUST"
            and pay["cadence_ladder"]["rungs_separating"] == 2,
            json.dumps(pay["cadence_ladder"]["verdict"]))
        leg("a shared winner across rungs is reported as the shared set",
            pay["winner"]["identical_across_rungs"] is True
            and len(pay["winner"]["shared_cells"] or []) == 3,
            json.dumps(pay["winner"]["shared_cells"]))

    def case_all_within(tmp):
        _fixture(tmp, 0.02, "2026-11-25", 4.0, 6.0, [(12, 20, 9.1), (5, 20, 8.1), (3, 10, 7.1)])
        _fixture(tmp, 0.05, "2026-11-25", 4.1, 6.0, [(12, 20, 9.2), (5, 20, 8.2), (3, 10, 7.2)])
        _fixture(tmp, 0.40, "2026-11-25", 4.4, 6.0, [(5, 20, 9.4), (12, 20, 8.4), (3, 10, 7.4)])
        pay = build_payload(tmp)
        leg("three rungs that all say WITHIN produce ROBUST_ORDERING_WITHIN",
            pay["verdict_word"] == "VERDICT_IS_K_ROBUST_ORDERING_WITHIN_NOISE",
            pay["verdict_word"])
        leg("a winner that moves with the knob is not reported as identical",
            pay["winner"]["identical_across_rungs"] is False,
            json.dumps(pay["winner"]["per_rung"][-1]["top"]))

    def case_old_generation(tmp):
        _fixture(tmp, 0.02, "2026-11-25", 5.0, 6.0, [(12, 20, 9.0), (5, 20, 8.0), (3, 10, 7.0)])
        _fixture(tmp, 0.05, "2026-11-25", 7.0, 6.0, [(12, 20, 9.1), (5, 20, 8.1), (3, 10, 7.1)])
        _fixture(tmp, 0.30, "2026-10-29", 9.0, 6.0, [(12, 20, 9.9), (5, 20, 8.9), (3, 10, 7.9)])
        pay = build_payload(tmp)
        leg("the older-generation rung is excluded with its own cutoff in the reason",
            any(e.get("buffer_k") == 0.30 and "2026-10-29" in (e.get("why") or "")
                for e in pay["excluded"]),
            json.dumps([e.get("why") for e in pay["excluded"]], ensure_ascii=False)[:120])
        leg("the rung cutoff follows the modal generation, not the newest panel",
            pay["rung_cutoff"] == "2026-11-25", pay["rung_cutoff"])
        leg("the excluded rung does not move the counts",
            pay["rungs_compared"] == 2, pay["rungs_compared"])

    def case_contradiction(tmp):
        _fixture(tmp, 0.02, "2026-11-25", 3.0, 6.0,
                 [(12, 20, 9.0), (5, 20, 8.0), (3, 10, 7.0)],
                 whose="CONFIG_ORDER_EXCEEDS_PHASE_NOISE")
        _fixture(tmp, 0.05, "2026-11-25", 3.1, 6.0,
                 [(12, 20, 9.1), (5, 20, 8.1), (3, 10, 7.1)])
        pay = build_payload(tmp)
        leg("a published word that contradicts the panel's two numbers is named",
            any(c.get("buffer_k") == 0.02 for c in pay["contradictions"]),
            json.dumps(pay["contradictions"]))
        leg("the contradicted rung still counts by its own numbers, not its word",
            pay["verdict_word"] == "VERDICT_IS_K_ROBUST_ORDERING_WITHIN_NOISE",
            pay["verdict_word"])

    def case_overlap(tmp):
        _fixture(tmp, 0.02, "2026-11-25", 5.0, 6.0, [(12, 20, 9.0), (5, 20, 8.0), (3, 10, 7.0)])
        _fixture(tmp, 0.05, "2026-11-25", 5.1, 6.0, [(12, 20, 9.1), (5, 20, 8.1), (3, 10, 7.1)])
        pay = build_payload(tmp)
        leg("a bucket whose best cell beats the next bucket's worst is not a separation",
            pay["cadence_ladder"]["verdict"] == "CADENCE_LADDER_NOT_ROBUST"
            and pay["cadence_ladder"]["rungs_separating"] == 0,
            json.dumps(pay["cadence_ladder"]["verdict"]))

    def case_solo(tmp):
        _fixture(tmp, 0.05, "2026-11-25", 7.0, 6.0,
                 [(12, 20, 9.0), (5, 20, 8.0), (3, 10, 7.0)])
        pay = build_payload(tmp)
        leg("a single rung is refused as not comparable",
            pay["verdict_word"] == "NOT_COMPARABLE_FEWER_THAN_TWO_RUNGS",
            pay["verdict_word"])
        leg("a missing rung is a named hole, never a zero",
            len(pay["excluded"]) >= 5 and all("why" in e for e in pay["excluded"]),
            len(pay["excluded"]))

        out = os.path.join(tmp, "face.json")
        run(tmp, out)
        rc = check(tmp, out)
        leg("run then check on untouched inputs returns 0", rc == 0, rc)
        first = open(out, encoding="utf-8").read()
        run(tmp, out)
        leg("run is byte-identical on a second pass",
            first == open(out, encoding="utf-8").read(), "")
        _fixture(tmp, 0.05, "2026-11-25", 3.0, 6.0,
                 [(12, 20, 9.0), (5, 20, 8.0), (3, 10, 7.0)])
        rc2 = check(tmp, out)
        leg("a moved input returns 3 (STALE) rather than 1", rc2 == 3, rc2)

    for case in (case_mixed, case_all_within, case_old_generation, case_contradiction,
                 case_overlap, case_solo):
        group(case)

    bad = [l for l in legs if not l[1]]
    for name, ok, why in legs:
        print("%s %s%s" % ("PASS" if ok else "FAIL", name, (" | " + str(why)) if why else ""))
    print("selftest: %d legs, %d failed" % (len(legs), len(bad)))
    return 0 if not bad else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "--selftest" or cmd == "selftest":
        return selftest()
    if cmd == "run":
        payload = run()
        print("wrote %s | rungs %d on %s | %s (%d exceed / %d within)"
              % (payload["face"], payload["rungs_compared"], payload["rung_cutoff"],
                 payload["verdict_word"], payload["rungs_exceeding"], payload["rungs_within"]))
        return 0
    if cmd in ("check", "--check"):
        return check()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
