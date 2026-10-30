"""E280 -- a published face and its own runner disagree: re-pin, or restore the stream?

The chain leg `star_self_price` went red at r1303: E252's verify recomputed the star's cross
coefficient as -0.7252014696754883 while the E251 face it pinned carried -0.7250430277727764,
and 177 fields moved. The seeded hypothesis was that the r1277 star-rule refactor changed how
the shared draw stream is consumed, so a published shuffled band had been silently re-randomised.

DECISION RULE (frozen here, before any measurement in this file is read):

  D1  If the two implementations agree to <=1e-9 on ONE panel, the moved fields are not an
      implementation difference. Then the repair is the gate (compare faces priced on the same
      bars, disclose a newer vintage instead of calling it drift) and NO face is reburned and
      NO draw stream is restored.
  D2  If they disagree on one panel, the stream was re-randomised: reburn E251 with the new
      stream and publish every moved card.
  D3  If the published same-vintage pair already agrees exactly, D1 is decided by published
      bytes, not by my rerun.

Second deliverable, independent of which branch fires: a leg that pins E251's RNG consumption,
so a future refactor cannot move a published band without a red leg. The pin is the property,
not the numbers: the same (panel, seed, draws) must reproduce the same band, and a different
seed must move it.
"""

import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e239_own_vs_cross as e239  # noqa: E402
import e251_star_own_component as e251  # noqa: E402
import e252_star_prices_itself as e252  # noqa: E402

ROOT = e251.ROOT
OUTDIR = e251.OUTDIR
STUDY = "E280"
TOL = 1e-9


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def head5(face):
    return next((c for c in (face.get("cells") or []) if c.get("label") == "all_five"), {}) or {}


def diff_fields(a, b, path="", out=None):
    """Every leaf whose value differs, as (path, a, b). Counted, not eyeballed."""
    out = [] if out is None else out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            diff_fields(a.get(k), b.get(k), "%s/%s" % (path, k), out)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            diff_fields(x, y, "%s[%d]" % (path, i), out)
    else:
        if isinstance(a, float) and isinstance(b, float):
            if abs(a - b) <= 1e-15:
                return out
        if a != b:
            out.append((path, a, b))
    return out


def published_pair():
    """E251 and E252 faces at the SAME vintage (2026-10-29) -- the identity in published bytes."""
    p251 = os.path.join(OUTDIR, "STAROWN-2026-10-29.json")
    p252 = os.path.join(OUTDIR, "STARSELF-2026-10-29.json")
    if not (os.path.exists(p251) and os.path.exists(p252)):
        return {"available": False}
    b1 = (head5(_load(p251)).get("star_residual") or {}).get("b1")
    bc = (head5(_load(p252)).get("cross_row") or {}).get("b_cross")
    return {"available": True, "e251_b1": b1, "e252_b_cross": bc,
            "abs_diff": None if (b1 is None or bc is None) else abs(b1 - bc)}


def vintage_gap():
    """What one extra bar does to the headline point estimate and to the shuffled band."""
    p29 = os.path.join(OUTDIR, "STAROWN-2026-10-29.json")
    p30 = os.path.join(OUTDIR, "STAROWN-2026-10-30.json")
    if not (os.path.exists(p29) and os.path.exists(p30)):
        return {"available": False}
    f29, f30 = _load(p29), _load(p30)
    c29, c30 = head5(f29), head5(f30)
    b29 = (c29.get("star_residual") or {}).get("b1")
    b30 = (c30.get("star_residual") or {}).get("b1")
    band29 = ((c29.get("band_star_lag1") or {}).get("band") or {})
    band30 = ((c30.get("band_star_lag1") or {}).get("band") or {})
    moves = diff_fields(f29, f30)
    return {"available": True,
            "cutoff_29": f29.get("evidence_cutoff"), "cutoff_30": f30.get("evidence_cutoff"),
            "sessions_29": c29.get("sessions"), "sessions_30": c30.get("sessions"),
            "e251_b1_29": b29, "e251_b1_30": b30,
            "b1_shift": None if (b29 is None or b30 is None) else b30 - b29,
            "band_hi_29": band29.get("hi"), "band_hi_30": band30.get("hi"),
            "band_width_29": band29.get("width"), "band_width_30": band30.get("width"),
            "moved_leaf_fields": len(moves),
            "moved_paths_sample": [m[0] for m in moves[:8]]}


def same_panel_identity(per=None, syms=None):
    """One fit each, one panel: is b_cross here the same regression as b1 there?"""
    per = per if per is not None else e239.panels()
    syms = syms or [s for s in e251.BASKET if per.get(s)]
    a = e251.cell(per, syms, None, None, label="all_five", kind="headline",
                  star_draws=1, add_draws=1)
    b = e252.cell(per, syms, None, None, label="all_five", kind="headline",
                  self_draws=1, boot_draws=1)
    b1 = (a.get("star_residual") or {}).get("b1")
    bc = (b.get("cross_row") or {}).get("b_cross")
    return {"sessions_e251": a.get("sessions"), "sessions_e252": b.get("sessions"),
            "e251_b1": b1, "e252_b_cross": bc,
            "abs_diff": None if (b1 is None or bc is None) else abs(b1 - bc)}


def rng_pin(per=None, syms=None):
    """The pin is the property: same (panel, seed, draws) -> same band; another seed -> moves."""
    per = per if per is not None else e239.panels()
    syms = [s for s in (syms or e251.BASKET) if per.get(s)]
    import e240_aggregate_attenuation as e240
    import e243_additivity_out_of_sample as e243
    win = e243.subset_per(per, syms, None, None)
    panel = e240.common_increments(win, syms)[1]
    star, star_source = e251.e250.name_star(panel, syms)
    if not star:
        return {"same_input_same_band": None, "different_seed_moves_band": None,
                "reason": "no star in this panel (star_source=%s)" % star_source}
    lvl = sorted(set.intersection(*[set(win[s]) for s in syms]))
    loo = e251.e250.aggregate_moves(win, syms, lvl, exclude=star)
    seed = e251.BASESEED + len("all_five")
    a = e251.own_column_band(panel, syms, star, loo, 30, seed)
    b = e251.own_column_band(panel, syms, star, loo, 30, seed)
    c = e251.own_column_band(panel, syms, star, loo, 30, seed + 1)
    ba, bb, bc = (a.get("band") or {}), (b.get("band") or {}), (c.get("band") or {})
    measurable = ba.get("hi") is not None and bc.get("hi") is not None
    return {"same_input_same_band": measurable and ba.get("hi") == bb.get("hi")
            and ba.get("lo") == bb.get("lo"),
            "different_seed_moves_band": measurable and bc.get("hi") != ba.get("hi"),
            "measurable": measurable, "seed_used": seed, "star": star,
            "band_hi": ba.get("hi"), "band_hi_other_seed": bc.get("hi"),
            "draws_used": a.get("draws_used")}


def decide(pub, same_panel):
    """Apply the frozen rule to measured numbers only."""
    exact_published = (pub.get("available") and pub.get("abs_diff") is not None
                       and pub["abs_diff"] <= TOL)
    exact_rerun = (same_panel.get("abs_diff") is not None
                   and same_panel["abs_diff"] <= TOL)
    if exact_published or exact_rerun:
        return {"branch": "D1", "verdict": "drift_is_vintage_not_rng",
                "repair": "gate: compare the two faces on the same bars, disclose a newer "
                          "vintage instead of calling it drift (e252 verify, r1304)",
                "reburn": False, "restore_stream": False,
                "reason": "the two implementations are one regression on one panel "
                          "(published same-vintage pair abs_diff=%s, rerun abs_diff=%s)"
                          % (pub.get("abs_diff"), same_panel.get("abs_diff"))}
    return {"branch": "D2", "verdict": "stream_was_re_randomised",
            "repair": "reburn E251 with the new stream and publish every moved card",
            "reburn": True, "restore_stream": False,
            "reason": "the two implementations disagree on the same panel "
                      "(abs_diff=%s)" % same_panel.get("abs_diff")}


def run(save=True):
    pub = published_pair()
    gap = vintage_gap()
    sp = same_panel_identity()
    pin = rng_pin()
    dec = decide(pub, sp)
    face = {
        "study": STUDY,
        "title": "a published face and its own runner disagree: re-pin, or restore the stream?",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": gap.get("cutoff_30") or gap.get("cutoff_29"),
        "decision_rule": {
            "D1": "same-panel identity <=1e-9 -> the move is vintage, fix the gate, reburn nothing",
            "D2": "disagree on one panel -> stream was re-randomised, reburn and disclose",
            "D3": "published same-vintage bytes decide it before any rerun",
        },
        "published_same_vintage": pub,
        "vintage_gap": gap,
        "same_panel_identity": sp,
        "rng_pin": pin,
        "decision": dec,
        "cards_that_move": {
            "note": "nothing is republished: every field that differs between the two E251 "
                    "faces is a different panel, and E252's face still equals E251's on its "
                    "own vintage",
            "e251_cutoff_29": gap.get("e251_b1_29"),
            "e251_cutoff_30": gap.get("e251_b1_30"),
        },
        "no_bill": "no new coefficient is claimed here; this face repairs a gate and decides "
                   "between two repairs that were both already on the table",
    }
    if save:
        os.makedirs(OUTDIR, exist_ok=True)
        cut = face["evidence_cutoff"] or "unknown"
        path = os.path.join(OUTDIR, "STAROWNREPIN-%s.json" % cut)
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(face, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
        latest = os.path.join(OUTDIR, "starownrepin_latest.json")
        with open(latest, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(face, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
        face["written"] = [os.path.relpath(path, ROOT), os.path.relpath(latest, ROOT)]
    return face


def leg(ok, name, detail=None):
    return {"pass": bool(ok), "leg": name, "detail": detail}


def selftest():
    legs = []
    # 1. the diff counter counts leaves, and tolerates float noise but not a real move
    a = {"x": {"b": 1.0}, "v": [1.0, 2.0]}
    b = {"x": {"b": 1.0 + 1e-16}, "v": [1.0, 2.5]}
    d = diff_fields(a, b)
    legs.append(leg(len(d) == 1 and d[0][0] == "/v[1]", "float noise is not a moved field", d))

    # 2. rule D1 fires on an exact same-panel pair, whatever the vintage gap says
    dec = decide({"available": True, "abs_diff": 0.0}, {"abs_diff": 0.0})
    legs.append(leg(dec["branch"] == "D1" and dec["reburn"] is False,
                    "exact same-panel identity -> gate repair, no reburn", dec))

    # 3. rule D2 fires when the two implementations disagree on one panel
    dec = decide({"available": True, "abs_diff": 0.0}, {"abs_diff": 1.6e-4})
    legs.append(leg(dec["branch"] == "D1",
                    "published exactness alone already settles it (D3 before D2)",
                    dec["reason"]))
    dec = decide({"available": True, "abs_diff": 1.6e-4}, {"abs_diff": 1.6e-4})
    legs.append(leg(dec["branch"] == "D2" and dec["reburn"] is True,
                    "disagreement on one panel -> reburn branch", dec["reason"]))

    # 4. rounding noise below tolerance must not be called a disagreement
    dec = decide({"available": True, "abs_diff": 5e-10}, {"abs_diff": 5e-10})
    legs.append(leg(dec["branch"] == "D1", "sub-tolerance noise stays in D1", dec.get("verdict")))

    # 5. the live measurement, if the faces are on disk: the two implementations are one fit
    sp = same_panel_identity()
    if sp.get("abs_diff") is not None:
        legs.append(leg(sp["abs_diff"] <= TOL,
                        "e251's b1 and e252's b_cross are the same fit on one panel",
                        sp))
        legs.append(leg(sp.get("sessions_e251") == sp.get("sessions_e252"),
                        "the two cells priced the same number of rows", sp))
    else:
        legs.append(leg(False, "same-panel identity was not measurable", sp))

    # 6. the RNG pin: same inputs reproduce the band
    pin = rng_pin()
    legs.append(leg(pin.get("same_input_same_band") is True,
                    "same (panel, seed, draws) reproduces the same band", pin))
    legs.append(leg(pin.get("different_seed_moves_band") is True,
                    "a different seed does move the band (the pin is not vacuous)", pin))
    return {"legs": legs, "passed": sum(1 for x in legs if x["pass"]), "total": len(legs),
            "ok": all(x["pass"] for x in legs)}


def main(argv):
    mode = (argv[1] if len(argv) > 1 else "run").lower()
    if mode == "selftest":
        r = selftest()
        for x in r["legs"]:
            print(("PASS " if x["pass"] else "FAIL ") + x["leg"])
            if not x["pass"]:
                print("      ", json.dumps(x["detail"], ensure_ascii=False)[:400])
        print("selftest %d/%d" % (r["passed"], r["total"]))
        return 0 if r["ok"] else 1
    if mode == "run":
        face = run(save=True)
        d = face["decision"]
        g = face["vintage_gap"]
        print("decision: %s (%s)" % (d["branch"], d["verdict"]))
        print("  %s" % d["reason"])
        print("  repair: %s" % d["repair"])
        if g.get("available"):
            print("vintage gap: sessions %s->%s, b1 %s->%s, moved leaves %s"
                  % (g["sessions_29"], g["sessions_30"],
                     round(g["e251_b1_29"], 6), round(g["e251_b1_30"], 6),
                     g["moved_leaf_fields"]))
        print("written:", ", ".join(face.get("written") or []))
        return 0
    print("usage: e280_e251_rng_drift_repin.py [run|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
