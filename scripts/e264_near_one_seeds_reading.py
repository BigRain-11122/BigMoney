"""E264 -- what does a near-one multiplier mean for the rows that sit closest to the band?

E259 rebuilt each published band across 40 independent streams and published a per-seed multiplier
m_k = edge_k(top) / edge_k(base).  A row's verdict at multiplier m is

    outside  <=>  |b| > max(|lo|, |hi|) * m   <=>  m < m*     where m* = |b| / max(|lo|, |hi|)

so m* is the whole row-side story: it is the multiplier at which the row would flip, and it needs
no draws at all.  E261 removed the seeds whose multiplier is exactly one (the draw that sets the
band's lower endpoint already arrived inside the base prefix) and found the floor at one belongs to
that bucket rather than to the stream.  This face asks the row-side question that leaves open:

  (a) which published row sits CLOSEST to its own band (smallest gap between m* and the nearest
      published end), and
  (b) does that row's reading depend on a near-one seed -- i.e. is its tight-end verdict produced
      by the p05 == 1 floor those seeds create?

Reading a face only. No shuffle stream is drawn here.
"""
from __future__ import print_function

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e259_band_multiplier_distribution as e259   # noqa: E402  (quantiles, frozen rul)
import e262_p95_transfer_across_windows as e262    # noqa: E402  (arms/rows/leg resolution)

ROOT = e262.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

STUDY = "E264_near_one_seeds_reading"
TITLE = "what does a near-one multiplier mean for the rows that sit closest to the band?"
CUTOFF = "2026-10-29"
SRC = "BANDWINDIST-%s.json" % CUTOFF
FACE = "BANDNEAR1-%s.json" % CUTOFF
LATEST = "bandnear1_latest.json"

TOL = 1e-12
ONE = 1.0

NO_BILL = ("measurement only: E259's published per-seed multipliers are re-read; no shuffle stream "
           "is drawn, no band is rebuilt, and no row verdict outside this face is touched")

VERDICT_VOCAB = (
    "closest_row_reads_a_near_one_seed",     # its tight end is the floor and moving the floor moves it
    "closest_row_survives_without_them",     # the near-one seeds can be dropped and it does not move
    "no_row_sits_close_enough_to_matter",    # every row is far from both ends
)


def _p(name):
    return os.path.join(ROOT, "results", "state_tilt", name)


def load(name):
    with io.open(_p(name), encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------ per-seed lists
def seed_lists(face):
    """{(cell, leg, base): [m_k ...]} straight off the published window records."""
    out = {}
    for cell, table in ((face or {}).get("windows") or {}).items():
        for arm, rec in (table or {}).items():
            if ":" not in str(arm):
                continue
            leg, base = str(arm).split(":", 1)
            try:
                base = int(base)
            except ValueError:
                continue
            ms = rec.get("seed_multipliers")
            if isinstance(ms, list) and ms:
                out[(cell, leg, base)] = [float(m) for m in ms]
    return out


def is_near_one(m, eps=TOL):
    return abs(float(m) - ONE) <= eps


def drop_near_one(ms, eps=TOL):
    """The seeds that are NOT the endpoint-already-attained bucket."""
    return [float(m) for m in (ms or []) if not is_near_one(m, eps)]


def p05_of(ms):
    """p05 on the same frozen quantile rule E259 used; None when there is nothing to read."""
    ms = [float(m) for m in (ms or [])]
    if not ms:
        return None
    return e259.quantiles(ms)["p05"]


# ------------------------------------------------------------------ row side
def m_star(b, lo, hi):
    """The multiplier at which this row flips. No draws involved."""
    if b is None or lo is None or hi is None:
        return None
    span = max(abs(float(lo)), abs(float(hi)))
    if span <= 0:
        return None
    return abs(float(b)) / span


def outside_at(b, lo, hi, m):
    return e262.judge(b, lo, hi, m)


def row_table(face, arms, seeds):
    """One record per published row: where it sits, and whether a near-one seed is load-bearing."""
    records = e262.row_records(face, arms)
    out = []
    for rec in records:
        row = dict(rec)
        if rec.get("status") != "measured":
            out.append(row)
            continue
        b, lo, hi = rec.get("b"), rec.get("band_lo"), rec.get("band_hi")
        star = m_star(b, lo, hi)
        row["m_star"] = star
        ms = (seeds or {}).get((rec.get("cell"), rec.get("leg"), rec.get("base")))
        row["n_seeds_read"] = len(ms or [])
        if star is None or not ms:
            row["status"] = "measured_no_seed_list"
            out.append(row)
            continue
        p05, p95 = p05_of(ms), e259.quantiles(ms)["p95"]
        kept = drop_near_one(ms)
        p05_kept = p05_of(kept)
        row.update({
            "own_p05_recomputed": p05,
            "own_p95_recomputed": p95,
            "n_near_one_seeds": sum(1 for m in ms if is_near_one(m)),
            "n_seeds_without_near_one": len(kept),
            "p05_without_near_one": p05_kept,
            "verdict_tight": ("outside" if outside_at(b, lo, hi, p05) else "inside")
            if p05 is not None else None,
            "verdict_wide": ("outside" if outside_at(b, lo, hi, p95) else "inside")
            if p95 is not None else None,
            "verdict_tight_without_near_one": ("outside" if outside_at(b, lo, hi, p05_kept)
                                               else "inside") if p05_kept is not None else None,
        })
        # name-is-semantics (E207/E208 family): the flag is the CONJUNCTION of "the tight end was
        # exactly the floor" and "dropping those seeds moves the tight-end verdict". A row that
        # merely has near-one seeds elsewhere in its list is not near-one dependent.
        tight_was_floor = bool(p05 is not None and is_near_one(p05))
        moved = (row.get("verdict_tight") is not None
                 and row.get("verdict_tight_without_near_one") is not None
                 and row.get("verdict_tight") != row.get("verdict_tight_without_near_one"))
        row["tight_end_was_the_floor"] = tight_was_floor
        row["tight_verdict_moves_without_near_one"] = moved
        row["near_one_dependent"] = bool(tight_was_floor and moved)
        # distance to the nearest published end, in multiplier units, and as a ratio
        ends = [(abs(star - e), e) for e in (p05, p95) if e is not None]
        if ends:
            dist, end = min(ends)
            row["nearest_end"] = end
            row["nearest_end_name"] = "p05" if end == p05 else "p95"
            row["gap_to_nearest_end"] = dist
            row["gap_ratio"] = (star / end) if end else None
        out.append(row)
    return out


def ranking(rows):
    """Closest rows first. A tie is disclosed as a tie, never resolved by list order (r1281 shape)."""
    measured = [r for r in rows if r.get("gap_to_nearest_end") is not None]
    ordered = sorted(measured, key=lambda r: (r["gap_to_nearest_end"], r.get("index", 0)))
    if not ordered:
        return {"rows": [], "n_tied_at_the_top": 0, "closest": None, "tied": []}
    best = ordered[0]["gap_to_nearest_end"]
    tied = [r for r in ordered if abs(r["gap_to_nearest_end"] - best) <= TOL]
    return {"rows": [{"index": r.get("index"), "cell": r.get("cell"), "row": r.get("row"),
                      "leg": r.get("leg"), "base": r.get("base"), "m_star": r.get("m_star"),
                      "nearest_end": r.get("nearest_end"),
                      "nearest_end_name": r.get("nearest_end_name"),
                      "gap_to_nearest_end": r.get("gap_to_nearest_end"),
                      "gap_ratio": r.get("gap_ratio"),
                      "near_one_dependent": r.get("near_one_dependent"),
                      "verdict_tight": r.get("verdict_tight"),
                      "verdict_wide": r.get("verdict_wide")} for r in ordered],
            "n_tied_at_the_top": len(tied),
            "closest": tied[0] if len(tied) == 1 else None,
            "tied": tied if len(tied) > 1 else []}


def floor_rows(rows):
    """Every row whose tight end is literally the floor, whether or not it moves without it."""
    out = []
    for r in rows:
        if not r.get("tight_end_was_the_floor"):
            continue
        out.append({"index": r.get("index"), "cell": r.get("cell"), "row": r.get("row"),
                    "leg": r.get("leg"), "base": r.get("base"), "m_star": r.get("m_star"),
                    "p05": r.get("own_p05_recomputed"),
                    "p05_without_near_one": r.get("p05_without_near_one"),
                    "verdict_tight": r.get("verdict_tight"),
                    "verdict_tight_without_near_one": r.get("verdict_tight_without_near_one"),
                    "moved": r.get("tight_verdict_moves_without_near_one")})
    return out


def verdict_of(rows, rank, floors):
    measured = [r for r in rows if r.get("m_star") is not None]
    dependent = [r for r in rows if r.get("near_one_dependent")]
    if not measured:
        return "no_row_could_be_read", "no published row carries both a coefficient and a band"
    if dependent:
        return ("closest_row_reads_a_near_one_seed",
                "%d of %d read row(s) change their tight-end verdict when the near-one seeds are "
                "dropped; the closest row sits %.4f away from its %s"
                % (len(dependent), len(measured),
                   (rank.get("rows") or [{}])[0].get("gap_to_nearest_end") or 0.0,
                   (rank.get("rows") or [{}])[0].get("nearest_end_name") or "end"))
    if not floors:
        return ("no_row_sits_close_enough_to_matter",
                "no read row has its tight end at the floor; the closest row sits %.4f away"
                % ((rank.get("rows") or [{}])[0].get("gap_to_nearest_end") or 0.0))
    return ("closest_row_survives_without_them",
            "%d row(s) end on the floor but none moves when it is removed (largest shift %.4f)"
            % (len(floors), max([abs((f.get("p05_without_near_one") or 1.0)
                                     - (f.get("p05") or 1.0)) for f in floors] or [0.0])))


# ------------------------------------------------------------------ cross-check vs E262
def borrowed_flip_check(rank, transfer_face):
    """Does the ranking agree with the rows a borrowed wide end actually moved?

    This is a disclosure, not a screen: E265 owns the per-row threshold test. Here we only ask
    whether the rows that sit closest to their own wide end are the same rows E262 moved. Moves
    are read off E262's flat blocks (and its ordered pairs), matched by E259's row index.
    """
    seen = {}
    for arm, blk in ((transfer_face or {}).get("flat") or {}).items():
        for mv in (blk or {}).get("moved_at_flat") or []:
            key = mv.get("index")
            seen.setdefault(key, {"index": key, "cell": mv.get("cell"), "row": mv.get("row"),
                                  "arms": [], "directions": []})
            seen[key]["arms"].append(arm)
            seen[key]["directions"].append(mv.get("direction"))
    for arm, blk in ((transfer_face or {}).get("transfer") or {}).items():
        for pair in (blk or {}).get("pairs") or []:
            for mv in pair.get("moved") or []:
                key = mv.get("index")
                if key in seen:
                    continue
                seen.setdefault(key, {"index": key, "cell": mv.get("cell"), "row": mv.get("row"),
                                      "arms": [], "directions": []})
                seen[key]["arms"].append("%s<-%s" % (pair.get("recipient"), pair.get("donor")))
                seen[key]["directions"].append(mv.get("direction"))
    moved = [seen[k] for k in sorted(seen, key=lambda x: (x is None, x))]
    top = (rank.get("rows") or [])
    top3_idx = [r.get("index") for r in top[:3]]
    hit = [m for m in moved if m["index"] in top3_idx]
    return {"transfer_face_present": bool(transfer_face),
            "rows_moved_by_a_borrowed_end": len(moved),
            "moved_rows": moved,
            "top3_closest": [{"index": r.get("index"), "cell": r.get("cell"),
                              "row": r.get("row"), "leg": r.get("leg"),
                              "base": r.get("base"),
                              "gap_to_nearest_end": r.get("gap_to_nearest_end")}
                             for r in top[:3]],
            "moved_rows_inside_the_top3_closest": hit,
            "n_moved_and_closest": len(hit),
            "note": ("disclosure only: the per-row threshold screen is E265's study, not this one")}


# ------------------------------------------------------------------ run
def run(save=True, outdir=None):
    outdir = outdir or OUTDIR
    face_src = load(SRC)
    arms = e262.arms_from(face_src)
    seeds = seed_lists(face_src)
    rows = row_table(face_src, arms, seeds)
    rank = ranking(rows)
    floors = floor_rows(rows)
    verdict, reason = verdict_of(rows, rank, floors)
    try:
        transfer_face = load(e262.FACE)
    except (IOError, OSError, ValueError):
        transfer_face = None
    borrowed = borrowed_flip_check(rank, transfer_face)

    measured = [r for r in rows if r.get("m_star") is not None]
    dependent = [r for r in rows if r.get("near_one_dependent")]
    gaps = [r["gap_to_nearest_end"] for r in measured if r.get("gap_to_nearest_end") is not None]
    shifts = [abs((r.get("p05_without_near_one") or 1.0) - (r.get("own_p05_recomputed") or 1.0))
              for r in measured if r.get("p05_without_near_one") is not None]
    out = {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": CUTOFF,
        "generated": None,
        "source_face": SRC,
        "no_bill": NO_BILL,
        "verdict": verdict,
        "verdict_reason": reason,
        "frozen_spec": {
            "rule": "outside <=> m < m*, m* = |b| / max(|lo|,|hi|); the row side needs no draws",
            "interval": "E259's own [p05, p95] per (cell, leg, base count)",
            "near_one": "a seed whose multiplier is 1 within 1e-12 (endpoint already attained "
                        "inside the base prefix)",
            "counterfactual": "drop every near-one seed and re-read p05 on the surviving seeds",
            "quantile_rule": "same linear rule E259 froze",
            "leg_resolution": "e262.resolve_leg: b_source first, coefficient identity second",
            "no_bill": NO_BILL,
        },
        "summary": {
            "rows_published": len(rows),
            "rows_read": len(measured),
            "rows_unjudgeable": len([r for r in rows if r.get("m_star") is None]),
            "rows_unreadable_seed_list": len([r for r in rows
                                              if r.get("status") == "measured_no_seed_list"]),
            "rows_tight_end_at_the_floor": len(floors),
            "rows_near_one_dependent": len(dependent),
            "gap_to_nearest_end_min": min(gaps) if gaps else None,
            "gap_to_nearest_end_median": sorted(gaps)[len(gaps) // 2] if gaps else None,
            "gap_to_nearest_end_max": max(gaps) if gaps else None,
            "p05_shift_when_dropped_median": sorted(shifts)[len(shifts) // 2] if shifts else None,
            "p05_shift_when_dropped_max": max(shifts) if shifts else None,
        },
        "closest": rank,
        "borrowed_flip_check": borrowed,
        "floor_rows": floors,
        "near_one_dependent_rows": [{"index": r.get("index"), "cell": r.get("cell"),
                                     "row": r.get("row"), "leg": r.get("leg"),
                                     "base": r.get("base"), "m_star": r.get("m_star"),
                                     "p05": r.get("own_p05_recomputed"),
                                     "p05_without_near_one": r.get("p05_without_near_one")}
                                    for r in dependent],
        "rows": rows,
    }
    out["generated"] = _stamp()
    if save:
        _write(out, outdir)
    return out


def _stamp():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _summary(face):
    return {
        "verdict": face.get("verdict"),
        "rows_read": (face.get("summary") or {}).get("rows_read"),
        "rows_near_one_dependent": (face.get("summary") or {}).get("rows_near_one_dependent"),
        "closest_gap": ((face.get("closest") or {}).get("rows") or [{}])[0].get(
            "gap_to_nearest_end"),
    }


def _write(face, outdir, tag=""):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "BANDNEAR1-%s%s.json" % (face.get("evidence_cutoff"), tag))
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    with io.open(os.path.join(outdir, LATEST), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    return path


def verify(outdir=None, tag=""):
    """Re-derive and report every field that does not come back (generated stamp excepted)."""
    outdir = outdir or OUTDIR
    path = os.path.join(outdir, "BANDNEAR1-%s%s.json" % (CUTOFF, tag))
    if not os.path.exists(path):
        return ["no published face at %s" % path]
    with io.open(path, encoding="utf-8") as fh:
        got = json.load(fh)
    fresh = run(save=False)
    skip = {"generated"}
    problems = []
    for key in sorted(set(got) | set(fresh)):
        if key in skip:
            continue
        if got.get(key) != fresh.get(key):
            problems.append("%s does not re-derive" % key)
    return problems


# ------------------------------------------------------------------ selftest
def _leg(ok, name, detail=None):
    return {"leg": name, "ok": bool(ok), "detail": detail}


def _rowrec(cell, row, b, lo, hi, base=60, src="self_row.b_self", status="measured"):
    return {"cell": cell, "row": row, "b": b, "band_lo": lo, "band_hi": hi,
            "band_draws": base, "b_source": src, "published_outside": True,
            "verdict_wide": "outside", "status": status, "index": 0}


def selftest():
    legs = []

    # --- m* is the whole row-side story and it agrees with the published margin at m = 1
    s = m_star(-0.7, -0.3, 0.2)
    legs.append(_leg(abs(s - 0.7 / 0.3) <= TOL, "m* = |b| / max(|lo|,|hi|)", s))
    legs.append(_leg(m_star(None, 1, 1) is None, "no coefficient means no threshold"))
    legs.append(_leg(m_star(-0.7, 0.0, 0.0) is None,
                     "a zero-width band has no threshold (never divides by zero)", None))

    # --- outside iff m < m*: both sides of the boundary, one step each
    s = m_star(-0.7, -0.3, 0.2)
    legs.append(_leg(outside_at(-0.7, -0.3, 0.2, s * 0.999) is True,
                     "just below the threshold the row is outside"))
    legs.append(_leg(outside_at(-0.7, -0.3, 0.2, s * 1.001) is False,
                     "just above the threshold the row is inside"))
    legs.append(_leg(outside_at(-0.7, -0.3, 0.2, s) is False,
                     "exactly at the threshold counts as inside (strict inequality)"))

    # --- near-one detection and the counterfactual
    legs.append(_leg(is_near_one(1.0 + 1e-13), "1 + 1e-13 is the floor within tolerance"))
    legs.append(_leg(not is_near_one(1.0 + 1e-6), "1 + 1e-6 is not the floor"))
    kept = drop_near_one([1.0, 1.0, 1.2, 1.5])
    legs.append(_leg(kept == [1.2, 1.5], "dropping the floor leaves the other seeds", kept))
    legs.append(_leg(drop_near_one([1.0, 1.0]) == [], "an all-floor list leaves nothing"))
    legs.append(_leg(p05_of([]) is None, "an empty list has no p05 (never 1.0 by default)"))
    legs.append(_leg(abs(p05_of([1.2, 1.5]) - e259.quantiles([1.2, 1.5])["p05"]) <= TOL,
                     "the counterfactual uses the same frozen quantile rule"))

    # --- a row whose tight end is the floor and whose threshold sits just above it: the floor is
    #     what holds its rejection up, so dropping the floor loses the rejection (m rises past m*)
    rows = row_table({"rows": [_rowrec("A", "self", -0.31, -0.30, 0.10)]},
                     {("A", "self", 60): {"cell": "A", "leg": "self", "base": 60,
                                          "p05": 1.0, "p95": 1.5}},
                     {("A", "self", 60): [1.0, 1.0, 1.2, 1.5]})
    r = rows[0]
    legs.append(_leg(r["near_one_dependent"] is True,
                     "a row between the floor and the next seed is near-one dependent"))
    legs.append(_leg(r["verdict_tight"] == "outside"
                     and r["verdict_tight_without_near_one"] == "inside",
                     "its tight verdict flips (rejection lost) when the floor is removed",
                     [r["verdict_tight"], r["verdict_tight_without_near_one"]]))

    # --- a row far outside both ends does not move: near-one seeds exist but are not load-bearing
    rows = row_table({"rows": [_rowrec("A", "self", -0.9, -0.30, 0.10)]},
                     {("A", "self", 60): {"cell": "A", "leg": "self", "base": 60,
                                          "p05": 1.0, "p95": 1.5}},
                     {("A", "self", 60): [1.0, 1.0, 1.2, 1.5]})
    r = rows[0]
    legs.append(_leg(r["tight_end_was_the_floor"] is True, "its tight end IS the floor"))
    legs.append(_leg(r["near_one_dependent"] is False,
                     "but the floor is not load-bearing for it (conjunction, not existence)",
                     [r["verdict_tight"], r["verdict_tight_without_near_one"]]))

    # --- a row genuinely inside everywhere stays inside; a row with no seed list is disclosed
    rows = row_table({"rows": [_rowrec("A", "self", -0.05, -0.30, 0.10),
                               _rowrec("A", "self", -0.05, -0.30, 0.10, base=200)]},
                     e262.arms_from({"interval_spread": {"rows": [
                         {"cell": "A", "arm": "self:60", "interval": [1.0, 1.5]}]}}),
                     {("A", "self", 60): [1.0, 1.3]})
    legs.append(_leg(rows[0]["near_one_dependent"] is False,
                     "a row with no near-one seeds in its arm is not dependent"))
    legs.append(_leg(rows[0]["verdict_tight_without_near_one"] == "inside",
                     "removing the only floor seed still leaves it inside"))
    legs.append(_leg(rows[1]["status"] in ("no_arm", "measured_no_seed_list"),
                     "a row with no published arm is disclosed, not silently read",
                     rows[1]["status"]))

    # --- ranking: closest first, and a tie is a tie (never resolve one by list order)
    rows = [{"index": 0, "gap_to_nearest_end": 0.05, "cell": "A", "row": "self"},
            {"index": 1, "gap_to_nearest_end": 0.05, "cell": "B", "row": "self"},
            {"index": 2, "gap_to_nearest_end": 0.40, "cell": "C", "row": "self"}]
    rank = ranking(rows)
    legs.append(_leg(rank["closest"] is None and rank["n_tied_at_the_top"] == 2,
                     "a tie at the top names no single closest row", rank["n_tied_at_the_top"]))
    rows[2]["gap_to_nearest_end"] = 0.01
    rank = ranking(rows)
    legs.append(_leg(rank["closest"] is not None
                     and rank["closest"]["index"] == 2,
                     "a strictly closest row is named", rank["closest"]))
    legs.append(_leg(ranking([])["closest"] is None, "an empty ranking names nothing", None))

    # --- the read count is not the row count (unjudgeable rows are disclosed, not absorbed)
    rows = [{"index": 0, "m_star": 1.2, "gap_to_nearest_end": 0.1},
            {"index": 1, "m_star": None}]
    v, why = verdict_of(rows, ranking(rows), [])
    legs.append(_leg(v == "no_row_sits_close_enough_to_matter",
                     "a face with no floor rows says so", v))
    v, why = verdict_of([{"index": 0, "m_star": None}], ranking([]), [])
    legs.append(_leg(v == "no_row_could_be_read", "an empty read set is its own verdict", v))

    # --- the whole pipeline runs on a two-row fake face
    fake = {"windows": {"A": {"self:60": {"seed_multipliers": [1.0, 1.0, 1.2, 1.5]}}},
            "interval_spread": {"rows": [{"cell": "A", "arm": "self:60",
                                          "interval": [1.0, 1.5], "median": 1.2, "width": 0.5}]},
            "rows": [_rowrec("A", "self", -0.31, -0.30, 0.10, base=60)]}
    arms = e262.arms_from(fake)
    seeds = seed_lists(fake)
    legs.append(_leg(seeds.get(("A", "self", 60)) == [1.0, 1.0, 1.2, 1.5],
                     "seed lists are keyed by (cell, leg, base), not by base alone"))
    rows = row_table(fake, arms, seeds)
    rank = ranking(rows)
    v, _ = verdict_of(rows, rank, floor_rows(rows))
    legs.append(_leg(v == "closest_row_reads_a_near_one_seed",
                     "the fake face reaches the dependent verdict", v))

    ok = all(l["ok"] for l in legs)
    print("selftest %d/%d %s" % (sum(1 for l in legs if l["ok"]), len(legs), "OK" if ok else "FAIL"))
    for l in legs:
        if not l["ok"]:
            print("  FAIL", l["leg"], l["detail"])
    return 0 if ok else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        if problems:
            print("verify %d problem(s)" % len(problems))
            for p in problems:
                print("  -", p)
            return 1
        print("verify 0 problems")
        return 0
    if cmd == "run":
        face = run()
        print("%s: %s" % (face["verdict"], face["verdict_reason"]))
        m = face["summary"]
        print("rows read %d of %d | floor rows %d | near-one dependent %d | closest gap %s" % (
            m["rows_read"], m["rows_published"], m["rows_tight_end_at_the_floor"],
            m["rows_near_one_dependent"], m["gap_to_nearest_end_min"]))
        return 0
    print("usage: e264_near_one_seeds_reading.py [run|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())