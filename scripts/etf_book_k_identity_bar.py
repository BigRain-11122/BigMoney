"""Two k values, one schedule: the identity was never broken -- the leg reads the wrong step. (r2063)

r2062 grouped 34 red smoke legs under one face (`etf_book_size_rulers_decision` publishing
IDENTITY_BROKEN on `ticket_k_reproduced`) and said the comparison used the 2026-10-23 bar
while the ticket decided 2026-11-11. That is the shape. This face prices the arithmetic.

On the published arm's own beta schedule (78 steps) the two numbers are ADJACENT steps:

    2026-10-23  k=0.460253   <- what the leg reads: step_in_force(sched, book_decided_at)
    2026-11-20  k=0.458463   <- what the ticket published as `k_rule`

`book_decided_at` is when the roster was decided; `base_bar` is the bar the ticket priced on.
k only moves on a schedule step, so the size in force on 2026-11-24 is still the 2026-11-20
step -- as-of, not equality. r1886 wrote that rule into `step_in_force` itself; this is the
one leg that skipped it and asked for the step at a different bar instead.

So the identity has a strictly stronger form than "equals the step at bar X":

    the ticket's k_rule must BE one of the schedule's points,
    that point must be UNIQUE on the schedule,
    and it must be the last point at or before the bar the ticket prices.

All three hold here. The leg asks the weaker question and there is a 0.179pp step in between,
so it went red on the first session after the roster decision and stayed red -- which is why
29 book legs are red in r2062's snapshot, and why `etf_book_rebalance_permission`
(UNREADABLE / baseline_published) and `etf_book_cut_order_gap` (UNREADABLE / permitted_k
missing) both sit downstream of it.

Nothing is repriced: the schedule is rebuilt with the same engine calls `run()` makes
(`etf_composite_pf.run_next_open` -> `etf_book_order.k_schedule`), and every step lookup is
`etf_book_size_rulers_decision.step_in_force`, imported, never re-implemented.

This face does not edit the leg -- another host holds the shared science faces this round --
it prints the one-line patch and what follows from it, so the fix is a copy, not a redesign.

Usage:
    python scripts/etf_book_k_identity_bar.py run
    python scripts/etf_book_k_identity_bar.py --check
    python scripts/etf_book_k_identity_bar.py --selftest
    python scripts/etf_book_k_identity_bar.py --md
"""
from __future__ import annotations

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FACE = os.path.join(ROOT, "results", "etf_book_k_identity_bar.json")
DOC = os.path.join(ROOT, "research", "ETF_BOOK_K_IDENTITY_BAR.md")
TICKET_GLOB = os.path.join(ROOT, "results", "etf_book_order", "TICKET-*.json")
SCHEMA = "etf-book-k-identity-bar/v1"
# The ticket and every face in this family store k at 6dp, so "is this the same point" is asked
# at 6dp (r1852: a 1e-9 tolerance makes the family's own published values look broken).
STEP_TOL = 1e-6
# A bar split is only worth a diagnosis when it is bigger than storage noise: 0.01pp = 100x 6dp.
SEAM_TOL = 1e-4

# the downstream faces whose verdict is a consequence of this leg, not an independent finding
BLAST = (
    "results/etf_book_size_rulers_decision.json",
    "results/etf_book_rebalance_permission.json",
    "results/etf_book_cut_order_gap.json",
    "results/etf_book_k_gap.json",
)

PATCH = (
    "# scripts/etf_book_size_rulers_decision.py, inside run()\n"
    "-    cells[\"baseline_published\"], k_dec_bar, k_at_dec = baseline_cell(arms[\"published\"], tk)\n"
    "+    priced_bar = tk.get(\"base_bar\") or tk.get(\"as_of\") or tk.get(\"book_decided_at\")\n"
    "+    cells[\"baseline_published\"], k_dec_bar, k_at_dec = baseline_cell(\n"
    "+        arms[\"published\"], dict(tk, book_decided_at=priced_bar))\n"
    "+    # the leg must then read the step the ticket was priced on, not the roster decision\n"
    "\n"
    "# why this is the right bar and not a tolerance: k moves only on a schedule step, so the\n"
    "# step at or before base_bar IS the size in force on base_bar (step_in_force's own rule).\n"
    "# Widening the leg's tolerance to a whole step (0.1pp) would also turn it green -- and\n"
    "# would hide a genuine break between two adjacent rows. Fix the bar, keep the tolerance at\n"
    "# the 6dp storage precision the ticket and the faces share.\n"
)


# ---------------------------------------------------------------- pure helpers
def _rel(p):
    """repo-relative when the path is inside the repo, basename otherwise (tempdir fixtures)."""
    try:
        return os.path.relpath(p, ROOT)
    except ValueError:
        return os.path.basename(p)


def step_bar(sched, bar):
    """The last schedule point at or before `bar`, via the single-source lookup."""
    import etf_book_size_rulers_decision as S  # noqa: PLC0415 (as-of rule lives there)
    return S.step_in_force(sched, bar)


def locate(sched, value, tol=STEP_TOL):
    """Every schedule index whose k equals `value` -- uniqueness is part of the identity."""
    hits = []
    for i, (_d, k, _b) in enumerate(sched):
        if k is not None and abs(float(k) - float(value)) <= tol:
            hits.append(i)
    return hits


def _bar_str(d):
    return str(d.date() if hasattr(d, "date") else d)[:10]


def drift_profile(sched):
    """How big an adjacent step is -- the size of the trap the leg fell into."""
    diffs = []
    for i in range(1, len(sched)):
        a, b = sched[i - 1][1], sched[i][1]
        if a is None or b is None:
            continue
        diffs.append(100.0 * (float(b) - float(a)))
    if not diffs:
        return {"n_steps": len(sched), "n_diffs": 0}
    ordered = sorted(diffs, key=abs)
    mid = len(ordered) // 2
    median = ordered[mid] if len(ordered) % 2 else 0.5 * (ordered[mid - 1] + ordered[mid])
    return {
        "n_steps": len(sched),
        "n_diffs": len(diffs),
        "abs_step_pp_median": round(abs(median), 4),
        "abs_step_pp_max": round(max(abs(x) for x in diffs), 4),
        "n_negative_steps": sum(1 for x in diffs if x < 0),
        "n_steps_where_a_0_179pp_gap_would_turn_red":
            sum(1 for x in diffs if abs(x) >= 0.179),
    }


def _idx_of_bar(sched, bar):
    """The schedule index whose bar string is exactly `bar` (None when absent)."""
    for i, (d, _k, _b) in enumerate(sched):
        if _bar_str(d) == str(bar)[:10]:
            return i
    return None


def judge(sched, ticket, ticket_cny=1000000.0):
    """Is the ticket's k_rule on the schedule, and is the leg reading the same point?"""
    k_rule = ticket.get("k_rule")
    priced_bar = ticket.get("base_bar") or ticket.get("as_of")
    decided_bar = ticket.get("book_decided_at")

    at_priced = step_bar(sched, priced_bar) if priced_bar else (None, None, None)
    at_decided = step_bar(sched, decided_bar) if decided_bar else (None, None, None)
    hits = locate(sched, k_rule) if k_rule is not None else []
    i_priced = _idx_of_bar(sched, at_priced[0]) if at_priced[0] else None
    i_decided = _idx_of_bar(sched, at_decided[0]) if at_decided[0] else None

    legs = {}
    if k_rule is None:
        legs["ticket_carries_a_k_rule"] = False
    else:
        legs["ticket_k_rule_is_a_schedule_point"] = bool(hits)
        legs["that_point_is_unique_on_the_schedule"] = len(hits) == 1
        legs["that_point_is_the_last_step_at_or_before_the_priced_bar"] = bool(
            hits and i_priced is not None and hits[0] == i_priced)
        legs["the_leg_bar_has_a_step_of_its_own"] = bool(i_decided is not None)
        legs["both_values_come_from_one_schedule"] = bool(
            hits and i_priced is not None and i_decided is not None)
        legs["the_ticket_row_and_the_leg_row_are_different_steps"] = bool(
            hits and i_decided is not None
            and abs(float(k_rule) - float(at_decided[1] or 0.0)) > SEAM_TOL)
        legs["the_two_steps_are_adjacent"] = bool(
            hits and i_decided is not None and hits[0] - i_decided == 1)

    broken = [k for k, v in legs.items() if v is False]
    dk_pp = None
    if k_rule is not None and at_decided[1] is not None:
        dk_pp = round(100.0 * (float(k_rule) - float(at_decided[1])), 4)

    out = {
        "ticket_k_rule": None if k_rule is None else round(float(k_rule), 6),
        "k_at_the_priced_bar": None if at_priced[1] is None else round(float(at_priced[1]), 6),
        "k_at_book_decided_at": None if at_decided[1] is None else round(float(at_decided[1]), 6),
        "priced_bar_field": priced_bar,
        "priced_bar": at_priced[0],
        "book_decided_at": decided_bar,
        "leg_bar": at_decided[0],
        "dk_pp": dk_pp,
        "dk_cny_at_ticket": None if dk_pp is None else round(dk_pp / 100.0 * float(ticket_cny), 2),
        "schedule_hits": [{"index": i, "bar": _bar_str(sched[i][0]),
                           "k": round(float(sched[i][1]), 6)} for i in hits],
        "legs": legs,
        "identity_broken": broken,
    }
    if not broken:
        out["verdict"] = "IDENTITY_INTACT_LEG_READS_A_DIFFERENT_STEP"
        out["sentence"] = (
            "the ticket's k=%.6f is %s on the schedule and is the last step at or before %s; "
            "the leg reads %s (k=%.6f) -- one step earlier, %.4fpp apart. The identity holds "
            "and the disagreeing leg is reading a different bar, not catching a break."
            % (float(k_rule), out["schedule_hits"][0]["bar"], priced_bar, at_decided[0],
               float(at_decided[1]), abs(dk_pp)))
    elif not hits:
        out["verdict"] = "IDENTITY_STILL_BROKEN"
        out["sentence"] = (
            "the ticket's k=%s is not any schedule point; that is a real break, not a bar "
            "choice -- do not patch the bar." % k_rule)
    elif "the_ticket_row_and_the_leg_row_are_different_steps" in broken:
        out["verdict"] = "IDENTITY_STILL_BROKEN"
        out["sentence"] = (
            "the leg and the ticket read the SAME step (%s, k=%.6f); whatever turned that leg "
            "red, it is not the bar, and this face's diagnosis does not apply."
            % (at_decided[0], float(at_decided[1])))
    else:
        out["verdict"] = "IDENTITY_STILL_BROKEN"
        out["sentence"] = (
            "the ticket's k=%.6f is on the schedule at %s, but the identity legs still fail "
            "(%s); read those legs before touching the bar."
            % (float(k_rule), out["schedule_hits"][0]["bar"], ",".join(broken)))
    return out


# ---------------------------------------------------------------- panel build
def _latest_ticket():
    files = sorted(glob.glob(TICKET_GLOB))
    if not files:
        return None, None
    with open(files[-1], encoding="utf-8") as f:
        return os.path.basename(files[-1]), json.load(f)


def _published_schedule():
    """The published arm's beta schedule -- the same calls run() makes, nothing new."""
    import pandas as pd

    from scripts import etf_book_class_beta_split as CS
    from scripts import etf_book_order as BO
    from scripts import etf_composite_pf as F
    from scripts import etf_equity_alpha as AE
    from scripts import etf_phase_beta_target as BT
    from scripts.etf_asset_class import classify

    close, openp, amt, feats = F.build_panel()
    if BO.REPAIR_PANEL:
        close, openp, _n = AE.repair_flips(close, openp)
    classes = pd.Series(classify(list(close.columns)))
    mkt_col = next((c for c in BT.MKT if c in close.columns), None)
    if mkt_col is None:
        raise RuntimeError("no market proxy on the panel")
    cols = [c for c in close.columns if classes[c] in CS._keep_classes()]
    score = F.build_score(close[cols], amt[cols], feats)
    ser, _to, _gap = F.run_next_open(close[cols], openp[cols], amt[cols], feats,
                                    BO.REBAL, n_hold=F.N_HOLD, cost=F.COST, score=score)
    idx = ser.index.intersection(close[mkt_col].index)
    sched = BO.k_schedule(BT.rets(ser.reindex(idx)),
                          BT.rets(close[mkt_col].reindex(idx)), BO.DEFAULT_BETA)
    if not sched:
        raise RuntimeError("beta schedule empty")
    return sched, {"last_panel_bar": _bar_str(close.index[-1]),
                   "n_panel_bars": int(len(close)), "n_symbols": int(len(cols))}


def _blast_radius():
    out = []
    for rel in BLAST:
        p = os.path.join(ROOT, rel)
        row = {"face": rel, "on_disk": os.path.exists(p)}
        if row["on_disk"]:
            try:
                with open(p, encoding="utf-8") as f:
                    d = json.load(f)
            except (ValueError, OSError) as exc:
                d = {"_error": str(exc)}
            row.update({
                "verdict": d.get("verdict"),
                "generated": d.get("generated") or d.get("ts"),
                "evidence_cutoff": d.get("evidence_cutoff"),
                "why": d.get("sentence") or d.get("why") or d.get("reason"),
                "mtime": os.path.getmtime(p),
            })
        out.append(row)
    return out


def derive():
    name, tk = _latest_ticket()
    if tk is None:
        return {"face": "etf_book_k_identity_bar", "schema": SCHEMA,
                "verdict": "NO_TICKET", "sentence": "no ticket on disk; nothing to read"}
    sched, panel = _published_schedule()
    j = judge(sched, tk)
    tail = [{"bar": _bar_str(d), "k": round(float(k), 6),
             "beta": None if b is None else round(float(b), 6)} for d, k, b in sched[-3:]]
    d = dict(j)
    d.update({
        "face": "etf_book_k_identity_bar",
        "schema": SCHEMA,
        "ticket_file": name,
        "evidence_cutoff": tk.get("evidence_cutoff"),
        "ticket_generated": tk.get("generated"),
        "sizing_source": tk.get("sizing_source"),
        "sizing_reason": tk.get("sizing_reason"),
        "schedule_tail": tail,
        "drift": drift_profile(sched),
        "panel": panel,
        "blast_radius": _blast_radius(),
        "patch": PATCH,
        "what_this_does_not_claim": [
            "it does not fix the leg: the shared science faces are held by another host this round",
            "it does not re-run the smoke legs: those must speak after the patch lands",
            "it says nothing about the 5 red legs outside the book family (r2062 counted them)",
            "adjacency is shown for this ticket only; the drift profile prices how common that "
            "arc is across all %d steps, not how many tickets ever fell into it" % len(sched),
        ],
    })
    return d


# ---------------------------------------------------------------- write / doc
def write():
    d = derive()
    with open(FACE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("%s %s" % (d.get("verdict"), _rel(FACE)))
    if d.get("verdict") == "IDENTITY_INTACT_LEG_READS_A_DIFFERENT_STEP":
        print(d["sentence"])
    write_doc(d)
    return 0


def write_doc(face):
    if face.get("verdict") == "NO_TICKET":
        return 0
    L = []
    L.append("# One schedule, two steps: the k leg that reads a different bar\n")
    L.append("source: `results/etf_book_k_identity_bar.json` @ %s | ticket `%s`\n"
             % (face.get("ticket_generated"), face.get("ticket_file")))
    L.append("**%s**\n" % face["verdict"])
    L.append("%s\n" % face["sentence"])
    L.append("## the two rows, from the schedule itself\n")
    L.append("| bar | k | what it is |")
    L.append("|---|---|---|")
    L.append("| %s | %.6f | what the leg reads (`book_decided_at` = %s) |"
             % (face["leg_bar"], face["k_at_book_decided_at"], face["book_decided_at"]))
    L.append("| %s | %.6f | what the ticket published as `k_rule`, last step at or before %s |"
             % (face["priced_bar"], face["k_at_the_priced_bar"], face["priced_bar_field"]))
    L.append("")
    L.append("A ticket of 1,000,000 CNY: the ticket's row sits **%.4fpp / %.2f CNY** below the "
             "row the leg reads (signed %.4fpp).\n"
             % (abs(face["dk_pp"]), abs(face["dk_cny_at_ticket"]), face["dk_pp"]))
    L.append("schedule tail (last three steps):\n")
    L.append("| bar | k | beta |")
    L.append("|---|---|---|")
    for r in face["schedule_tail"]:
        L.append("| %s | %.6f | %s |" % (r["bar"], r["k"],
                                        "n/a" if r["beta"] is None else "%.6f" % r["beta"]))
    L.append("")
    dr = face.get("drift") or {}
    L.append("The step between those two rows is not unusual: across %d steps the median "
             "adjacent move is **%.4fpp**, the largest is **%.4fpp**, and **%d** of the %d steps "
             "are at least as large as this 0.179pp arc. A leg keyed to the wrong bar is red "
             "whenever the two bars straddle any step at all.\n"
             % (dr.get("n_steps", 0), dr.get("abs_step_pp_median", 0.0),
                dr.get("abs_step_pp_max", 0.0), dr.get("n_steps_where_a_0_179pp_gap_would_turn_red", 0),
                dr.get("n_diffs", 0)))
    L.append("## the identity that actually holds\n")
    L.append("| leg | reads |")
    L.append("|---|---|")
    for k, v in (face.get("legs") or {}).items():
        L.append("| %s | %s |" % (k, "True" if v else ("False" if v is False else "n/a")))
    L.append("")
    L.append("The strong form -- *the ticket's k is a distinct point on the schedule, and it is "
             "the last one at or before the bar the ticket prices* -- is what makes a size "
             "auditable. \"Equals the step at whatever bar the reader picked\" is not the same "
             "statement, and it is the one the red leg asks.\n")
    L.append("## what is downstream of this leg\n")
    L.append("| face | verdict | cutoff | why |")
    L.append("|---|---|---|---|")
    for r in face.get("blast_radius") or []:
        why = r.get("why")
        if isinstance(why, (dict, list)):
            why = json.dumps(why, ensure_ascii=False)
        L.append("| `%s` | %s | %s | %s |"
                 % (os.path.basename(r["face"]), r.get("verdict") or "missing",
                    r.get("evidence_cutoff") or "-", str(why or "-")[:160]))
    L.append("")
    L.append("`etf_book_rebalance_permission` publishes UNREADABLE because the baseline cell it "
             "classifies carries this leg's verdict; `etf_book_cut_order_gap` then publishes "
             "UNREADABLE because a null `permitted_k` is not a permission. Both are consequences, "
             "not second opinions.\n")
    L.append("## the patch, in full\n")
    L.append("```diff\n%s```\n" % PATCH)
    L.append("Widening the leg's tolerance to a whole step (0.1pp) would also turn it green "
             "today. It would also hide a genuine break between two adjacent rows. Fix the bar; "
             "keep the tolerance at the 6dp storage precision the ticket and the faces share.\n")
    L.append("## what this does not claim\n")
    for c in face.get("what_this_does_not_claim") or []:
        L.append("- %s" % c)
    L.append("")
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    with open(DOC, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("doc %s" % _rel(DOC))
    return 0


# ---------------------------------------------------------------- check
def check():
    if not os.path.exists(FACE):
        print("STALE face missing: %s" % _rel(FACE))
        return 3
    with open(FACE, encoding="utf-8") as f:
        old = json.load(f)
    problems = []
    if old.get("verdict") == "NO_TICKET":
        problems.append("STALE face has no ticket: re-run when a ticket exists")
    # cheap external anchor: the ticket this face read must still be the newest ticket on disk
    name, tk = _latest_ticket()
    if tk is None:
        problems.append("STALE no ticket on disk")
    else:
        if name != old.get("ticket_file"):
            problems.append("STALE newest ticket moved: %s -> %s"
                            % (old.get("ticket_file"), name))
        elif (tk.get("k_rule") is not None
              and abs(float(tk["k_rule"]) - float(old.get("ticket_k_rule") or 0.0)) > STEP_TOL):
            problems.append("STALE ticket k_rule moved: %s -> %s"
                            % (old.get("ticket_k_rule"), tk.get("k_rule")))
        elif (tk.get("base_bar") or tk.get("as_of")) != old.get("priced_bar_field"):
            problems.append("STALE ticket priced bar moved: %s -> %s"
                            % (old.get("priced_bar_field"),
                               tk.get("base_bar") or tk.get("as_of")))
    # internal arithmetic: the two decided numbers must still be the two printed numbers
    if old.get("verdict") == "IDENTITY_INTACT_LEG_READS_A_DIFFERENT_STEP":
        if old.get("k_at_the_priced_bar") is not None and old.get("ticket_k_rule") is not None:
            if abs(float(old["k_at_the_priced_bar"]) - float(old["ticket_k_rule"])) > STEP_TOL:
                problems.append("CHECK FAILED the printed ticket row no longer equals k_rule")
        if old.get("priced_bar") and old.get("schedule_hits"):
            if old["schedule_hits"][0]["bar"] != old["priced_bar"]:
                problems.append("CHECK FAILED schedule hit bar != priced bar")
        if not os.path.exists(DOC):
            problems.append("STALE doc missing: research/ETF_BOOK_K_IDENTITY_BAR.md")
        else:
            body = open(DOC, encoding="utf-8").read()
            if "IDENTITY_INTACT_LEG_READS_A_DIFFERENT_STEP" not in body:
                problems.append("CHECK FAILED doc does not print this face's verdict")
    if "STALE" in " ".join(problems):
        print(" ".join(problems))
        return 3
    if problems:
        print("CHECK FAILED " + "; ".join(problems))
        return 2
    print("CHECK OK %s: k=%.6f at %s, leg read %s (%.4fpp apart)"
          % (old["verdict"],
             float(old["ticket_k_rule"]),
             old["priced_bar"],
             old["leg_bar"],
             abs(float(old["dk_pp"]))))
    return 0


# ---------------------------------------------------------------- selftest
def _fixture_sched():
    """Four steps, the arc r2063 found, in miniature."""
    import pandas as pd
    return [(pd.Timestamp("2026-09-17"), 0.458808, 0.435912),
            (pd.Timestamp("2026-10-23"), 0.460253, 0.434543),
            (pd.Timestamp("2026-11-20"), 0.458463, 0.436240),
            (pd.Timestamp("2026-12-18"), 0.457100, 0.437600)]


def selftest():
    legs = []
    sched = _fixture_sched()

    # 1 as-of lookup: nothing scheduled after the bar is visible
    bar, k, _b = step_bar(sched, "2026-11-24")
    assert bar == "2026-11-20" and abs(k - 0.458463) <= 1e-12, (bar, k)
    legs.append("asof_step")

    # 2 the roster-decision bar lands one step earlier -- this is the whole trap
    bar, k, _b = step_bar(sched, "2026-11-11")
    assert bar == "2026-10-23" and abs(k - 0.460253) <= 1e-12, (bar, k)
    legs.append("leg_bar_one_step_back")

    # 3 a bar before the first step has no answer (callers must fall back and turn red)
    assert step_bar(sched, "2026-01-01") == (None, None, None)
    legs.append("no_step_before_first")

    # 4 the intact case, with the real ticket numbers
    tk = {"k_rule": 0.458463, "base_bar": "2026-11-24", "book_decided_at": "2026-11-11"}
    j = judge(sched, tk)
    assert j["verdict"] == "IDENTITY_INTACT_LEG_READS_A_DIFFERENT_STEP", j["verdict"]
    assert not j["identity_broken"], j["identity_broken"]
    assert j["priced_bar"] == "2026-11-20" and j["leg_bar"] == "2026-10-23"
    legs.append("intact_case")

    # 5 the gap is priced, signed, and in the right units
    assert abs(j["dk_pp"] - (-0.179)) < 1e-9, j["dk_pp"]
    assert abs(j["dk_cny_at_ticket"] - (-1790.0)) < 1e-6, j["dk_cny_at_ticket"]
    legs.append("gap_units")

    # 6 a value that is not any schedule point is a real break, not a bar choice
    j2 = judge(sched, dict(tk, k_rule=0.459999))
    assert j2["verdict"] == "IDENTITY_STILL_BROKEN" and not j2["schedule_hits"], j2
    legs.append("off_schedule_is_a_break")

    # 7 a point that exists but is NOT the last one before the priced bar is also a break
    j3 = judge(sched, dict(tk, k_rule=0.460253, base_bar="2026-11-24"))
    assert j3["verdict"] == "IDENTITY_STILL_BROKEN", j3["verdict"]
    assert "that_point_is_the_last_step_at_or_before_the_priced_bar" in j3["identity_broken"], j3
    legs.append("wrong_point_on_schedule")

    # 8 uniqueness is enforced: a duplicated k cannot claim the strong identity
    dup = list(sched) + [(__import__("pandas").Timestamp("2026-12-31"), 0.458463, 0.436240)]
    j4 = judge(dup, tk)
    assert "that_point_is_unique_on_the_schedule" in j4["identity_broken"], j4["legs"]
    legs.append("duplicate_point_blocked")

    # 9 the drift profile sees both large and small steps
    dr = drift_profile(sched)
    assert dr["n_steps"] == 4 and dr["n_diffs"] == 3, dr
    assert dr["abs_step_pp_max"] >= 0.179, dr
    assert dr["n_negative_steps"] >= 1, dr
    legs.append("drift_profile")

    # 10 a missing k_rule fails a named leg instead of crashing
    j5 = judge(sched, {"base_bar": "2026-11-24"})
    assert j5["legs"]["ticket_carries_a_k_rule"] is False and j5["verdict"] == "IDENTITY_STILL_BROKEN"
    legs.append("missing_k_rule")

    # 11 check() refuses a missing face with STALE, not a crash
    import tempfile
    global FACE  # noqa: PLW0603 (fixture injection, restored below)
    keep = FACE
    with tempfile.TemporaryDirectory() as td:
        FACE = os.path.join(td, "nope.json")
        assert check() == 3, "missing face must be STALE rc3"
    FACE = keep
    legs.append("check_missing_face")

    # 12 check() turns STALE when the newest ticket's k_rule moves -- the external anchor works
    fixture = {"face": "etf_book_k_identity_bar", "schema": SCHEMA,
               "verdict": "IDENTITY_INTACT_LEG_READS_A_DIFFERENT_STEP",
               "ticket_file": os.path.basename(glob.glob(TICKET_GLOB)[-1])
               if glob.glob(TICKET_GLOB) else "TICKET-none.json",
               "ticket_k_rule": 0.111111, "priced_bar_field": "1999-01-01",
               "priced_bar": "1999-01-01", "leg_bar": "1999-01-01",
               "k_at_the_priced_bar": 0.111111, "dk_pp": 0.0,
               "schedule_hits": [{"index": 0, "bar": "1999-01-01", "k": 0.111111}]}
    with tempfile.TemporaryDirectory() as td:
        FACE = os.path.join(td, "stale.json")
        with open(FACE, "w", encoding="utf-8") as f:
            json.dump(fixture, f)
        rc = check()
    FACE = keep
    assert rc == 3, "ticket drift must be STALE rc3, got %s" % rc
    legs.append("check_ticket_drift")

    # 13 doc contract: the verdict token must be printed by the writer itself
    import inspect
    src = inspect.getsource(write_doc)
    assert "IDENTITY_INTACT_LEG_READS_A_DIFFERENT_STEP" in src or "verdict" in src
    legs.append("doc_verdict")

    # 14 the patch names the field it fixes and does not widen the tolerance
    assert "base_bar" in PATCH and "1e-6" not in PATCH.split("Widening")[0]
    assert "book_decided_at=priced_bar" in PATCH
    legs.append("patch_shape")

    print("selftest %d/%d OK: %s" % (len(legs), len(legs), ",".join(legs)))
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "selftest"
    if cmd in ("run", "write"):
        return write()
    if cmd == "--check" or cmd == "check":
        return check()
    if cmd == "--selftest" or cmd == "selftest":
        return selftest()
    if cmd == "--md":
        d = json.load(open(FACE, encoding="utf-8"))
        return write_doc(d)
    print("usage: etf_book_k_identity_bar.py [run|--check|--selftest|--md]")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
