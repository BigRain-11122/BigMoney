"""E278 -- is a zero-spread tail a systematic hole in the normalised ruler, or one bad group?

E272's ruler divides a gap by the spread a tail offers inside the row's (leg, base-count) group.
cross:200 turned out to publish p05 = 1.0000 on all four windows, so its spread is exactly 0 and two
rows became unmeasurable on that tail. One group can be bad luck. If zero-spread tails cluster by
base count (a thin shuffle across few base counts collapses the percentile onto its floor) then the
ruler needs a published minimum-spread policy instead of per-row notes.

Census every published BAND* face for arm rows carrying (cell, leg:base, interval=[p05,p95]),
classify each (leg, base) group at each tail, and join the result to E272's published per-row
tail budget. No shuffle stream is drawn, no band is rebuilt: every number is a function of the
published faces.

Usage:  python scripts/e278_spread_floor.py run|verify|selftest
"""
import glob
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e262_p95_transfer_across_windows as e262  # noqa: E402  (arms_from / load / OUTDIR / LEGS)

ROOT = e262.ROOT
OUTDIR = e262.OUTDIR
TOL = e262.TOL
LEGS = e262.LEGS
BASE_COUNTS = e262.BASE_COUNTS

STUDY = "E278_spread_floor"
TITLE = "is a zero-spread tail a systematic hole in the normalised ruler, or one bad group?"
CUTOFF = "2026-10-29"
SRC_WIDTH = e262.SRC_WIDTH                      # the interval table (arms)
SRC_BUDGET = "BANDFLIPBUDGET-%s.json" % CUTOFF  # E272's published per-row tail budget
SRC_FLOOR = "BANDFLOOR-%s.json" % CUTOFF        # E277's published floor
FACE = "BANDSPREADFLOOR-%s.json" % CUTOFF
LATEST = "bandspreadfloor_latest.json"
SELF_FACES = (FACE, LATEST)

TAILS = ("tight", "wide")
KEY_OF = {"tight": "p05", "wide": "p95"}

CLASSES = ("single_cell_group", "all_cells_at_the_floor", "identical_percentile", "measurable",
           "conflicting_cell_values")
VERDICT_VOCAB = (
    "the_zero_spread_tail_is_the_band_floor_landing_on_the_thin_shuffle",
    "zero_spread_is_one_bad_group",
    "zero_spread_clusters_by_base_count_without_being_the_floor",
    "the_same_group_degenerates_at_both_tails",
    "no_zero_spread_tails_published",
)

NO_BILL = ("measurement only: E259's published interval arms, E272's published per-row tail budget "
           "and E277's published floor are re-read. No draw stream is drawn, no band rebuilt, no "
           "engine runs. A zero spread here is a statement about the published numbers, not about "
           "the market.")


# ------------------------------------------------------------------ io
def load(name):
    with io.open(os.path.join(OUTDIR, name), encoding="utf-8") as fh:
        return json.load(fh)


def arms_from_face(face):
    """{(cell, leg, base): rec} -- E259's interval table, one source of truth."""
    return e262.arms_from(face)


# ------------------------------------------------------------------ generic arm-row walker
def _walk(o, path=""):
    if isinstance(o, dict):
        yield path, o
        for k in sorted(o):
            for item in _walk(o[k], path + "/" + str(k)):
                yield item
    elif isinstance(o, list):
        for v in o:
            for item in _walk(v, path + "/[]"):
                yield item


def arm_rows(face):
    """Every record carrying an 'arm' label of the form leg:base AND an interval pair, anywhere."""
    out = []
    for path, node in _walk(face):
        arm, iv = node.get("arm"), node.get("interval")
        if not isinstance(arm, str) or ":" not in arm or not isinstance(iv, list) or len(iv) < 2:
            continue
        leg, base = arm.split(":", 1)
        try:
            base = int(base)
        except ValueError:
            continue
        out.append({"path": path, "cell": node.get("cell"), "leg": leg, "base": base,
                    "p05": iv[0], "p95": iv[1], "median": node.get("median")})
    return out


def groups_from_rows(rows):
    """{(leg, base): {cell: {record:..}}} plus the faces each group was seen on."""
    out = {}
    for r in rows:
        key = (r["leg"], r.get("base"))
        cell = r.get("cell")
        g = out.setdefault(key, {"leg": r["leg"], "base": r.get("base"), "cells": {}})
        g["cells"].setdefault(cell, []).append(r)
    return out


# ------------------------------------------------------------------ classification
def spread_pct(lo_m, hi_m):
    if lo_m is None or hi_m is None or not lo_m:
        return None
    return (float(hi_m) / float(lo_m) - 1.0) * 100.0


def tail_view(group, tail):
    """One (leg, base) group read at one tail: published values, spread and a named class."""
    key = KEY_OF[tail]
    per_cell, conflicts, n_pub, floor_hits = {}, [], 0, 0
    for cell, recs in sorted(group["cells"].items(), key=lambda kv: str(kv[0])):
        vals = [r.get(key) for r in recs if isinstance(r.get(key), (int, float))
                and not isinstance(r.get(key), bool)]
        distinct = sorted({round(float(v), 12) for v in vals})
        if len(distinct) > 1:
            # the same cell published twice with different numbers: the group is unusable as a
            # ruler rather than quietly taking one of them
            conflicts.append({"cell": cell, "values": distinct})
            continue
        if not distinct:
            continue
        per_cell[cell] = distinct[0]
        n_pub += 1
        if tail == "tight" and abs(distinct[0] - 1.0) <= TOL:
            floor_hits += 1
    vals = list(per_cell.values())
    lo_m = min(vals) if vals else None
    hi_m = max(vals) if vals else None
    spread = spread_pct(lo_m, hi_m)
    # a single published cell has min == max by construction: that is "nothing to compare", not a
    # zero spread, so it must not inherit the zero flag (the frozen spec says so)
    zero = bool(n_pub > 1 and spread is not None and abs(spread) <= TOL * 100.0)
    if conflicts:
        cls = "conflicting_cell_values"
    elif n_pub <= 1:
        cls = "single_cell_group"
    elif not zero:
        cls = "measurable"
    elif tail == "tight" and n_pub and floor_hits == n_pub:
        cls = "all_cells_at_the_floor"
    else:
        cls = "identical_percentile"
    return {"tail": tail, "leg": group["leg"], "base": group.get("base"),
            "n_cells": len(group["cells"]), "n_published": n_pub,
            "values": per_cell, "min": lo_m, "max": hi_m, "spread_pct": spread,
            "zero_spread": bool(zero), "floor_hits": floor_hits,
            "all_at_the_floor": bool(tail == "tight" and n_pub and floor_hits == n_pub),
            "conflicts": conflicts, "class": cls}


def census_groups(groups):
    """Every group at every tail, with the two-tail reading attached."""
    out = []
    for key in sorted(groups, key=lambda k: (str(k[0]), str(k[1]))):
        g = groups[key]
        rec = {"leg": g["leg"], "base": g.get("base"), "n_cells": len(g["cells"])}
        for tail in TAILS:
            rec[tail] = tail_view(g, tail)
        rec["zero_both_tails"] = bool(rec["tight"]["zero_spread"] and rec["wide"]["zero_spread"])
        rec["group_id"] = "%s:%s" % (g["leg"], g.get("base"))
        out.append(rec)
    return out


def by_base(census):
    """Does the zero spread cluster by base count, or is it uniformly distributed?"""
    out = {}
    for rec in census:
        b = rec.get("base")
        slot = out.setdefault(str(b), {"base": b, "n_groups": 0, "zero_tight": 0,
                                       "zero_wide": 0, "floor_hits_tight": 0,
                                       "n_cells": 0, "groups": []})
        slot["n_groups"] += 1
        slot["n_cells"] += rec["n_cells"]
        slot["floor_hits_tight"] += rec["tight"]["floor_hits"]
        if rec["tight"]["zero_spread"]:
            slot["zero_tight"] += 1
            slot["groups"].append(rec["group_id"])
        if rec["wide"]["zero_spread"]:
            slot["zero_wide"] += 1
    return out


def affected_rows(census, budget):
    """Which published E272 rows the zero-spread groups actually strand, on which tail."""
    zero = {}
    for rec in census:
        for tail in TAILS:
            if rec[tail]["zero_spread"]:
                zero.setdefault((rec["leg"], rec.get("base")), []).append(tail)
    out = []
    for blk in (budget.get("tail_budget") or {}).values():
        for row in (blk.get("rows") or []):
            key = (row.get("leg"), row.get("base"))
            if key not in zero:
                continue
            for tail in zero[key]:
                t = row.get(tail) or {}
                out.append({"cell": row.get("cell"), "row": row.get("row"),
                            "index": row.get("index"), "leg": key[0], "base": key[1],
                            "tail": tail, "spread_pct": t.get("spread_pct"),
                            "normalised_gap": t.get("normalised_gap"),
                            "unmeasurable_here": t.get("normalised_gap") is None})
    return out


def identity_check(census, budget):
    """Each group's re-derived spread must equal the spread E272 published for rows in that group."""
    published = {}
    for blk in (budget.get("tail_budget") or {}).values():
        for row in (blk.get("rows") or []):
            for tail in TAILS:
                t = row.get(tail) or {}
                if t.get("spread_pct") is not None:
                    published.setdefault((row.get("leg"), row.get("base"), tail), set()).add(
                        round(float(t["spread_pct"]), 9))
    out = {"checked": 0, "mismatched": [], "notes": []}
    for rec in census:
        for tail in TAILS:
            key = (rec["leg"], rec.get("base"), tail)
            if key not in published:
                continue
            mine = rec[tail]["spread_pct"]
            if mine is None:
                out["notes"].append("%s/%s: E272 publishes a spread but the census has none" %
                                    (rec["group_id"], tail))
                continue
            out["checked"] += 1
            vals = published[key]
            if len(vals) > 1:
                out["notes"].append("%s/%s: E272 publishes more than one spread for one group" %
                                    (rec["group_id"], tail))
            if not any(abs(float(round(mine, 9)) - v) <= 1e-6 for v in vals):
                out["mismatched"].append({"group": rec["group_id"], "tail": tail,
                                          "census": mine, "published": sorted(vals)})
    return out


# ------------------------------------------------------------------ verdict
def verdict_of(summary, census):
    if not summary["n_groups"]:
        return "no_zero_spread_tails_published"
    zero_tight = [r for r in census if r["tight"]["zero_spread"]]
    zero_wide = [r for r in census if r["wide"]["zero_spread"]]
    if not zero_tight and not zero_wide:
        return "no_zero_spread_tails_published"
    both = [r for r in census if r["zero_both_tails"]]
    if both:
        return "the_same_group_degenerates_at_both_tails"
    floor_driven = all(r["tight"]["class"] == "all_cells_at_the_floor" for r in zero_tight)
    if zero_tight and not zero_wide and floor_driven:
        return "the_zero_spread_tail_is_the_band_floor_landing_on_the_thin_shuffle"
    bases_hit = {str(r.get("base")) for r in zero_tight + zero_wide}
    base_cluster = any((summary["by_base"].get(b, {}).get("floor_hits_tight") or 0) >
                       (summary["by_base"].get(o, {}).get("floor_hits_tight") or 0)
                       for b in bases_hit for o in summary["by_base"] if o not in bases_hit)
    if base_cluster:
        return "zero_spread_clusters_by_base_count_without_being_the_floor"
    return "zero_spread_is_one_bad_group"


def summary_of(census, base_groups, affected):
    zero = {"tight": [r["group_id"] for r in census if r["tight"]["zero_spread"]],
            "wide": [r["group_id"] for r in census if r["wide"]["zero_spread"]],
            "both": [r["group_id"] for r in census if r["zero_both_tails"]]}
    floor_hits = sum(r["tight"]["floor_hits"] for r in census)
    published_tight = sum(r["tight"]["n_published"] for r in census)
    spreads = [r[t]["spread_pct"] for r in census for t in TAILS
               if r[t]["spread_pct"] is not None and not r[t]["zero_spread"]]
    s = {
        "n_groups": len(census),
        "n_groups_measurable_both_tails": sum(1 for r in census
                                              if not r["tight"]["zero_spread"]
                                              and not r["wide"]["zero_spread"]),
        "zero_tight": zero["tight"],
        "zero_wide": zero["wide"],
        "zero_both": zero["both"],
        "n_zero_tight": len(zero["tight"]),
        "n_zero_wide": len(zero["wide"]),
        "classes_tight": {c: sum(1 for r in census if r["tight"]["class"] == c) for c in CLASSES},
        "classes_wide": {c: sum(1 for r in census if r["wide"]["class"] == c) for c in CLASSES},
        "floor_hits_tight": floor_hits,
        "published_tight_values": published_tight,
        "floor_hit_share": (float(floor_hits) / published_tight) if published_tight else None,
        "by_base": base_groups,
        "min_nonzero_spread_pct": min(spreads) if spreads else None,
        "max_nonzero_spread_pct": max(spreads) if spreads else None,
        "rows_stranded": sum(1 for a in affected if a["unmeasurable_here"]),
        "row_tail_readings_in_zero_groups": len(affected),
    }
    s["verdict"] = verdict_of(s, census)
    return s


# ------------------------------------------------------------------ publish
def minimum_spread_policy(summary, census):
    """Published, not enforced: what a reader should do when a tail's spread is exactly 0."""
    flagged = []
    for r in census:
        for tail in TAILS:
            if r[tail]["zero_spread"]:
                flagged.append({"group": r["group_id"], "tail": tail,
                                "class": r[tail]["class"],
                                "n_cells": r[tail]["n_cells"]})
    return {
        "rule": ("a normalised gap needs spread_pct > 0; a group whose tail spread is exactly 0 "
                 "must publish the tail as unmeasurable and never a normalised gap"),
        "why": ("the same floor that makes the tight lower end freeze (E277) also freezes the "
                "percentile across cells, so the ruler has nothing to divide by"),
        "flagged": flagged,
        "substitution": ("read the other tail; a group flagged on both tails has no usable ruler "
                         "and the row must stay unmeasured rather than be given a default"),
        "enforced_here": False,
    }


def build(outdir=None):
    outdir = outdir or OUTDIR
    width = load(SRC_WIDTH)
    budget = load(SRC_BUDGET)

    rows, faces = [], []
    for f in sorted(glob.glob(os.path.join(outdir, "BAND*.json"))):
        name = os.path.basename(f)
        if name in SELF_FACES or name.endswith("_latest.json"):
            continue
        try:
            with io.open(f, encoding="utf-8") as fh:
                face = json.load(fh)
        except (ValueError, IOError):
            continue
        got = arm_rows(face)
        if got:
            faces.append({"face": name, "arm_rows": len(got)})
            for r in got:
                r["face"] = name
                rows.append(r)

    # the interval table is the canonical source for the (leg, base) groups; other faces may add
    # groups, so both are folded in and the union is censused
    primary = arms_from_face(width)
    groups = groups_from_rows(rows)
    for (cell, leg, base), rec in primary.items():
        g = groups.setdefault((leg, base), {"leg": leg, "base": base, "cells": {}})
        g["cells"].setdefault(cell, []).append({"cell": cell, "leg": leg, "base": base,
                                                "p05": rec.get("p05"), "p95": rec.get("p95"),
                                                "median": rec.get("median"),
                                                "face": SRC_WIDTH, "source": "interval_table"})

    census = census_groups(groups)
    base_groups = by_base(census)
    affected = affected_rows(census, budget)
    summary = summary_of(census, base_groups, affected)
    return {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": CUTOFF,
        "generated": _stamp(),
        "source_faces": [SRC_WIDTH, SRC_BUDGET, SRC_FLOOR],
        "faces_with_arm_rows": faces,
        "frozen_spec": {
            "unit": "one (leg, base count) group; a group's tail is the range of that key across "
                    "the cells it publishes",
            "spread_rule": "spread_pct = (max/min - 1) * 100 over published values, same formula "
                           "as E272's tail_range",
            "zero_rule": "zero spread = |spread_pct| <= 1e-10; a single published cell is NOT a "
                         "zero spread, it is a group with nothing to compare",
            "floor_rule": "a tight value counts as at-the-floor when it equals 1.0 to 1e-12 "
                          "(E277's published floor)",
            "conflict_rule": "one cell publishing two different values makes the group unusable "
                             "rather than silently taking one of them",
            "join_rule": "rows are joined to groups by (leg, base count) against E272's published "
                         "tail_budget blocks",
            "no_new_draws": "no shuffle stream is drawn; every number is a function of the faces",
            "tolerance": TOL,
        },
        "census": census,
        "identity_check": identity_check(census, budget),
        "affected_rows": affected,
        "minimum_spread_policy": minimum_spread_policy(summary, census),
        "summary": summary,
        "verdict": summary["verdict"],
        "verdict_reason": _reason(summary),
        "no_bill": NO_BILL,
    }


def _reason(s):
    if s["verdict"] == "the_zero_spread_tail_is_the_band_floor_landing_on_the_thin_shuffle":
        return ("%d of %d groups publish a zero spread, all of them at the tight tail and all of "
                "them with every cell sitting on the 1.0 floor (E277). The floor hits cluster by "
                "base count (%s), so this is the same build property showing up wherever the "
                "percentile has the least support -- not one unlucky group. %d published row-tail "
                "readings are stranded and must stay unmeasured, not given a default."
                % (s["n_zero_tight"], s["n_groups"],
                   ", ".join("%s: %d" % (k, v["floor_hits_tight"])
                             for k, v in sorted(s["by_base"].items())),
                   s["rows_stranded"]))
    if s["verdict"] == "no_zero_spread_tails_published":
        return "every censused group publishes a positive spread at both tails; the ruler has no hole."
    return "zero spread is present but not explained by the floor; see the census."


def _stamp():
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def _write(face, outdir, tag=""):
    outdir = outdir or OUTDIR
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    name = FACE if not tag else FACE.replace(".json", "_%s.json" % tag)
    path = os.path.join(outdir, name)
    with io.open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True))
    latest = os.path.join(outdir, LATEST)
    with io.open(latest, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True))
    return path


def run(save=True, outdir=None, tag=""):
    face = build(outdir)
    if save:
        face["_written"] = os.path.basename(_write(face, outdir, tag))
    return face


def verify(outdir=None, tag=""):
    """Re-derive from the sources and compare to what is on disk -- never trust the summary."""
    problems = []
    disk = load(FACE if not tag else FACE.replace(".json", "_%s.json" % tag))
    fresh = build(outdir)
    for key in ("summary", "census", "affected_rows", "minimum_spread_policy", "identity_check"):
        if fresh.get(key) != disk.get(key):
            problems.append("%s does not re-derive" % key)
    if fresh.get("verdict") != disk.get("verdict"):
        problems.append("verdict does not re-derive")
    if (fresh.get("summary") or {}).get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict is outside the frozen vocabulary")
    if (fresh.get("identity_check") or {}).get("mismatched"):
        problems.append("a group's spread disagrees with E272's published spread")
    return {"ok": not problems, "problems": problems,
            "verdict": (disk.get("summary") or {}).get("verdict")}


# ------------------------------------------------------------------ selftest
def _grp(leg, base, cells):
    """cells = {cell: (p05, p95)}"""
    return {"leg": leg, "base": base,
            "cells": {c: [{"cell": c, "leg": leg, "base": base, "p05": v[0], "p95": v[1]}]
                      for c, v in cells.items()}}


def selftest():
    legs = []

    def leg(ok, name, detail=""):
        legs.append({"ok": bool(ok), "name": name, "detail": detail})

    # L1: a group whose every tight cell sits on the floor
    g = _grp("cross", 200, {"a": (1.0, 1.5), "b": (1.0, 1.6), "c": (1.0, 1.7), "d": (1.0, 1.8)})
    t = tail_view(g, "tight")
    leg(t["zero_spread"] and t["class"] == "all_cells_at_the_floor", "L1 floor group",
        "%s spread=%r hits=%d" % (t["class"], t["spread_pct"], t["floor_hits"]))

    # L2: a group whose every tight cell is identical but NOT on the floor
    g = _grp("self", 60, {"a": (1.5, 2.0), "b": (1.5, 2.1)})
    t = tail_view(g, "tight")
    leg(t["zero_spread"] and t["class"] == "identical_percentile", "L2 identical not at floor",
        t["class"])

    # L3: a single published cell is not a zero spread
    g = _grp("self", 200, {"a": (1.2, 1.9)})
    t = tail_view(g, "tight")
    leg((not t["zero_spread"]) and t["class"] == "single_cell_group", "L3 single cell",
        "%s zero=%r" % (t["class"], t["zero_spread"]))

    # L4: spread arithmetic is the published formula
    g = _grp("cross", 60, {"a": (1.0, 2.0), "b": (1.1008218707620367, 2.1)})
    t = tail_view(g, "tight")
    leg(abs(t["spread_pct"] - 10.08218707620367) < 1e-9, "L4 spread formula",
        repr(t["spread_pct"]))

    # L5: a healthy group is measurable and carries no zero flag
    g = _grp("self", 60, {"a": (1.0095, 2.18), "b": (1.0932, 2.13)})
    t = tail_view(g, "tight")
    w = tail_view(g, "wide")
    leg(t["class"] == "measurable" and w["class"] == "measurable" and not w["zero_spread"],
        "L5 healthy group", "%s/%s" % (t["class"], w["class"]))

    # L6: one cell publishing two different values poisons the group instead of picking one
    g = {"leg": "self", "base": 60, "cells": {"a": [
        {"cell": "a", "leg": "self", "base": 60, "p05": 1.0, "p95": 2.0},
        {"cell": "a", "leg": "self", "base": 60, "p05": 1.2, "p95": 2.0}]}}
    t = tail_view(g, "tight")
    leg(t["class"] == "conflicting_cell_values" and not t["zero_spread"], "L6 conflict rule",
        "%s conflicts=%d" % (t["class"], len(t["conflicts"])))

    # L7: by-base aggregation counts groups and floor hits
    cen = census_groups({
        ("cross", 200): _grp("cross", 200, {"a": (1.0, 1.5), "b": (1.0, 1.8)}),
        ("self", 60): _grp("self", 60, {"a": (1.1, 1.5), "b": (1.2, 1.8)}),
    })
    bb = by_base(cen)
    leg(bb["200"]["zero_tight"] == 1 and bb["60"]["zero_tight"] == 0
        and bb["200"]["floor_hits_tight"] == 2, "L7 by-base aggregation", json.dumps(bb, sort_keys=True)[:120])

    # L8: the both-tails flag needs BOTH tails zero
    g = _grp("x", 60, {"a": (1.0, 2.0), "b": (1.0, 2.0)})
    cen = census_groups({("x", 60): g})
    leg(cen[0]["zero_both_tails"] is True, "L8 both tails", str(cen[0]["zero_both_tails"]))
    g = _grp("x", 60, {"a": (1.0, 2.0), "b": (1.0, 2.1)})
    cen = census_groups({("x", 60): g})
    leg(cen[0]["zero_both_tails"] is False, "L8b one tail only", str(cen[0]["zero_both_tails"]))

    # L9: the census over the real interval table covers every (leg, base) group, 4 cells each
    face = load(SRC_WIDTH)
    prim = arms_from_face(face)
    gr = groups_from_rows([{"cell": c, "leg": l, "base": b, "p05": r.get("p05"),
                            "p95": r.get("p95")} for (c, l, b), r in prim.items()])
    cen = census_groups(gr)
    leg(len(cen) == len(LEGS) * len(BASE_COUNTS) and all(r["n_cells"] == 4 for r in cen),
        "L9 real census shape", "%d groups / cells %s" % (len(cen), [r["n_cells"] for r in cen]))

    # L10: identity -- the re-derived spread equals the spread E272 published for those groups
    face_disk = load(FACE) if os.path.exists(os.path.join(OUTDIR, FACE)) else None
    if face_disk:
        idc = face_disk.get("identity_check") or {}
        leg(idc.get("checked", 0) > 0 and not idc.get("mismatched"), "L10 identity to E272",
            "checked=%s mismatched=%s" % (idc.get("checked"), len(idc.get("mismatched") or [])))
    else:
        leg(False, "L10 identity to E272", "face missing")

    # L11: every zero-spread group in the published face is flagged in the policy block
    if face_disk:
        flagged = {(f["group"], f["tail"]) for f in
                   (face_disk.get("minimum_spread_policy") or {}).get("flagged") or []}
        zeros = {(r["group_id"], t) for r in face_disk.get("census") or []
                 for t in TAILS if r[t]["zero_spread"]}
        leg(flagged == zeros, "L11 policy covers every zero spread",
            "%d flagged / %d zero" % (len(flagged), len(zeros)))
    else:
        leg(False, "L11 policy covers every zero spread", "face missing")

    # L12: every stranded row is genuinely unmeasurable on that tail
    if face_disk:
        aff = face_disk.get("affected_rows") or []
        bad = [a for a in aff if not a["unmeasurable_here"]]
        leg(bool(aff) and not bad, "L12 stranded rows are unmeasurable",
            "%d rows, %d measurable" % (len(aff), len(bad)))
    else:
        leg(False, "L12 stranded rows are unmeasurable", "face missing")

    ok = sum(1 for l in legs if l["ok"])
    return {"legs": legs, "passed": ok, "total": len(legs), "ok": ok == len(legs)}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "run":
        face = run()
        s = face["summary"]
        print("verdict=%s groups=%d zero_tight=%s zero_wide=%s floor_hits=%s stranded=%s"
              % (s["verdict"], s["n_groups"], s["zero_tight"], s["zero_wide"],
                 s["floor_hits_tight"], s["rows_stranded"]))
        print("written results/state_tilt/%s" % (FACE))
        return 0
    if cmd == "verify":
        r = verify()
        print(json.dumps(r, ensure_ascii=False))
        return 0 if r["ok"] else 1
    if cmd == "selftest":
        r = selftest()
        for l in r["legs"]:
            print("%s %s  %s" % ("PASS" if l["ok"] else "FAIL", l["name"], l["detail"]))
        print("%d/%d" % (r["passed"], r["total"]))
        return 0 if r["ok"] else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())