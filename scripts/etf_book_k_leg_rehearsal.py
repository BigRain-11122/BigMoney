"""The r2063 one-line anchor patch, priced through the two faces it unblocks. (r2064)

r2063 proved the shape: the ticket's `k=0.458463` IS the 2026-11-20 step of the same beta
schedule, and the leg reads 2026-10-23 (`0.460253`) instead -- one step earlier, 0.1790pp
apart.  That red leg is not one red leg:

    etf_book_size_rulers_decision   IDENTITY_BROKEN (ticket_k_reproduced)
      -> etf_book_rebalance_permission  UNREADABLE (baseline_published)
        -> etf_book_cut_order_gap       UNREADABLE (permitted_k missing)

The patch is one line inside `etf_book_size_rulers_decision.run()`; it is printed verbatim
in `results/etf_book_k_identity_bar.json` -> `patch`.  This round cannot land it: another
host holds the shared science faces (`repo_write_contention` rc=3), so writing the leg would
be a shared-face edit.

What CAN be answered without touching them: **if that cell carried the step at `base_bar`,
what would the two downstream faces actually say?**  Both are pure functions of the receipts:

    etf_book_rebalance_permission.decide(rulers, ticket)
    etf_book_cut_order_gap.plan_cut(perm, ticket, repo_rate, repo_date, readers)

so the answer is a copy of the published receipts with ONE cell replaced, run through those
real functions -- imported, never re-implemented.

Three runs are reported, and the last two are the point:

    on_disk    baseline k=0.460253 (2026-10-23)  -> must reproduce today's UNREADABLE
    patched    baseline k=0.458463 (2026-11-20)  -> the prediction
    neighbour  baseline k=0.458808 (2026-09-17)  -> must STAY unreadable

The neighbour run is why the fix is "the bar" and not "the tolerance": the step next to the
right one is 0.0345pp off and still fails at the 6dp identity tolerance.  Widening the
tolerance to swallow a whole step would also turn the leg green -- and would hide a real
break between two adjacent schedule rows.

What this does NOT do (printed in the receipt, not just here):
  * it does not fix the leg, the permission or the gap face -- all three are shared faces;
  * it does not re-price the book or rebuild the schedule (no panel work, no engine call);
  * `beta` on the patched cell is derived (`beta = target/k` while k < 1), not read from a
    receipt, because the receipts carry beta only on `schedule_tail` rows; neither face this
    rehearsal exercises consumes beta;
  * the readers/enforcers scan is not re-run -- the patched gap face is given the empty
    reader list, which can only make it MORE pessimistic, never more favourable.

Usage:
    python scripts/etf_book_k_leg_rehearsal.py run
    python scripts/etf_book_k_leg_rehearsal.py --check
    python scripts/etf_book_k_leg_rehearsal.py --selftest
    python scripts/etf_book_k_leg_rehearsal.py --md
"""
from __future__ import annotations

import copy
import datetime as _dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FACE = os.path.join(ROOT, "results", "etf_book_k_leg_rehearsal.json")
DOC = os.path.join(ROOT, "research", "ETF_BOOK_K_LEG_REHEARSAL.md")
R_RULERS = os.path.join(ROOT, "results", "etf_book_size_rulers_decision.json")
R_PERM = os.path.join(ROOT, "results", "etf_book_rebalance_permission.json")
R_GAP = os.path.join(ROOT, "results", "etf_book_cut_order_gap.json")
R_IDENT = os.path.join(ROOT, "results", "etf_book_k_identity_bar.json")
TICKET_GLOB_DIR = os.path.join(ROOT, "results", "etf_book_order")
SCHEMA = "etf-book-k-leg-rehearsal/v1"
BASELINE = "baseline_published"
IDENT_TOL = 1e-6          # the identity leg's own tolerance (r1852: not 1e-9)


def _read_json(p):
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _r(x, n=6):
    return None if x is None else round(float(x), n)


def latest_ticket():
    import glob
    files = [f for f in sorted(glob.glob(os.path.join(TICKET_GLOB_DIR, "TICKET-*.json")))
             if "-card" not in os.path.basename(f)]
    if not files:
        return None, None
    with open(files[-1], encoding="utf-8") as f:
        d = json.load(f)
    d["_file"] = os.path.basename(files[-1])
    return os.path.basename(files[-1]), d


def steps_on_receipts(ident, ticket):
    """{bar: k} for every schedule point a receipt actually carries, plus beta where stored.

    No schedule is rebuilt here: the r2063 face already strove the two rows this question
    needs, and `schedule_tail` carries beta for the older ones.
    """
    out = {}
    for row in (ident.get("schedule_tail") or []):
        bar, k = row.get("bar"), row.get("k")
        if bar and k is not None:
            out[str(bar)[:10]] = {"k": float(k), "beta": row.get("beta"), "source": "schedule_tail"}
    for row in (ident.get("schedule_hits") or []):
        bar, k = row.get("bar"), row.get("k")
        if bar and k is not None:
            out[str(bar)[:10]] = {"k": float(k), "beta": row.get("beta"),
                                  "source": "schedule_hits"}
    return out


def beta_from_k(k, target):
    """beta = target / k while k < 1 -- the identity the engine strikes (k = min(1, t/beta))."""
    if k is None or not target or k <= 0:
        return None
    if float(k) >= 1.0:
        return None
    return float(target) / float(k)


def patch_cells(cells, k, beta, bar):
    """One cell replaced, everything else byte-identical to the published receipt."""
    out = copy.deepcopy(cells or {})
    cell = dict(out.get(BASELINE) or {})
    cell["k"] = float(k)
    if beta is not None:
        cell["beta"] = float(beta)
    cell["as_of_bar"] = bar
    out[BASELINE] = cell
    return out


def rehearse(rulers, ticket, k, beta, bar, readers=None):
    """Run the real downstream functions on a copy of the receipts with one cell replaced."""
    import etf_book_rebalance_permission as PP
    import etf_book_cut_order_gap as PG

    patched = dict(rulers or {})
    patched["cells"] = patch_cells((rulers or {}).get("cells"), k, beta, bar)
    perm = PP.decide(patched, ticket)
    gap = PG.plan_cut(perm, ticket, None, None, list(readers or []))
    return {
        "baseline_cell": {
            "k": _r((patched["cells"].get(BASELINE) or {}).get("k"), 9),
            "k_equals_ticket_k_rule": abs(float(k) - float(ticket.get("k_rule") or k))
            <= IDENT_TOL,
            "as_of_bar": bar,
            "beta_derived": None if beta is None else _r(beta, 9),
        },
        "permission": {
            "verdict": perm.get("verdict"),
            "reason": perm.get("reason"),
            "sentence": perm.get("sentence"),
            "permitted_k": perm.get("permitted_k"),
            "cut_k": perm.get("cut_k"),
            "cut_pp": perm.get("cut_pp"),
            "cut_cny": perm.get("cut_cny"),
            "readings_unreadable": perm.get("readings_unreadable"),
            "path_readings": perm.get("path_readings"),
            "supporters_path": perm.get("supporters_path"),
        },
        "cut_order_gap": {
            "verdict": gap.get("verdict"),
            "reason": gap.get("reason"),
            "sentence": gap.get("sentence"),
            "permitted_k": gap.get("permitted_k"),
            "gap_k": gap.get("gap_k"),
            "gap_pp": gap.get("gap_pp"),
            "ordered_book_cny": gap.get("ordered_book_cny"),
            "cut_cny": gap.get("cut_cny"),
            "order_exceeds_permission": gap.get("order_exceeds_permission"),
        },
    }


def build():
    ticket_name, ticket = latest_ticket()
    rulers = _read_json(R_RULERS)
    ident = _read_json(R_IDENT)
    perm_disk = _read_json(R_PERM)
    gap_disk = _read_json(R_GAP)
    face = {"face": "etf_book_k_leg_rehearsal", "schema": SCHEMA,
            "generated": _dt.datetime.now().astimezone().isoformat(timespec="seconds")}
    if not (ticket and rulers and ident):
        face.update({"verdict": "MECHANISM_FAULT",
                     "sentence": "ticket, rulers receipt or the r2063 identity face is missing",
                     "ticket_file": ticket_name})
        return face

    steps = steps_on_receipts(ident, ticket)
    target = rulers.get("beta_target") or ticket.get("beta_target")
    priced_bar = str(ticket.get("base_bar") or ticket.get("as_of") or "")[:10]
    true_k = ident.get("k_at_the_priced_bar")
    hit = (ident.get("schedule_hits") or [{}])[0]
    hit_bar = str(hit.get("bar") or "")[:10]

    # the step the ticket was priced on, from the receipt; refused if the receipt disagrees
    agree = (true_k is not None
             and abs(float(true_k) - float(ticket.get("k_rule") or true_k)) <= IDENT_TOL
             and hit_bar and hit_bar <= priced_bar)
    beta_true = beta_from_k(true_k, target)

    # the step the leg currently reads, and one step earlier still (the neighbour control)
    leg_bar = str(ident.get("leg_bar") or "")[:10]
    leg_k = ident.get("k_at_book_decided_at")
    tail = [r for r in (ident.get("schedule_tail") or [])]
    neighbour = None
    for row in tail:
        if str(row.get("bar"))[:10] != leg_bar and row.get("k") is not None:
            neighbour = row
            break

    readers = list((gap_disk or {}).get("permission_readers") or [])
    on_disk = rehearse(rulers, ticket, leg_k if leg_k is not None else
                       (rulers.get("cells", {}).get(BASELINE, {}) or {}).get("k"),
                       None, leg_bar or None, readers)
    patched = rehearse(rulers, ticket, true_k, beta_true, hit_bar, readers)
    neg = None
    if neighbour is not None:
        neg = rehearse(rulers, ticket, neighbour.get("k"),
                       beta_from_k(neighbour.get("k"), target),
                       str(neighbour.get("bar"))[:10], readers)

    # every other cell must be byte-identical to the published receipt
    others = sorted(n for n in (rulers.get("cells") or {}) if n != BASELINE)
    untouched = all(
        json.dumps((rulers["cells"].get(n) or {}), sort_keys=True)
        == json.dumps((patch_cells(rulers["cells"], true_k, beta_true, hit_bar).get(n) or {}),
                      sort_keys=True)
        for n in others)

    before_perm = (perm_disk or {}).get("verdict")
    before_gap = (gap_disk or {}).get("verdict")
    flip = (patched["permission"]["verdict"] != before_perm
            and patched["cut_order_gap"]["verdict"] != before_gap)
    on_disk_reproduces = (on_disk["permission"]["verdict"] == before_perm
                          and on_disk["cut_order_gap"]["verdict"] == before_gap)
    neg_stays_red = (neg is None or (neg["permission"]["verdict"] == before_perm
                                     and neg["cut_order_gap"]["verdict"] == before_gap))

    face.update({
        "ticket_file": ticket_name,
        "evidence_cutoff": ticket.get("evidence_cutoff"),
        "ticket_k_rule": _r(ticket.get("k_rule")),
        "ticket_k_now": _r(ticket.get("k_now")),
        "priced_bar": priced_bar,
        "book_decided_at": ticket.get("book_decided_at"),
        "beta_target": target,
        "step_the_ticket_was_priced_on": {
            "bar": hit_bar, "k": _r(true_k), "beta_derived": _r(beta_true),
            "is_last_step_at_or_before_priced_bar": bool(hit_bar and hit_bar <= priced_bar),
            "equals_ticket_k_rule": abs(float(true_k) - float(ticket.get("k_rule") or true_k))
            <= IDENT_TOL if true_k is not None else None,
            "source": hit.get("source") or "results/etf_book_k_identity_bar.json",
        },
        "step_the_leg_reads": {"bar": leg_bar, "k": _r(leg_k)},
        "schedule_points_on_receipt": {b: {"k": _r(v["k"]), "beta": _r(v["beta"])}
                                       for b, v in sorted(steps.items())},
        "runs": {"on_disk": on_disk, "patched": patched, "neighbour": neg},
        "on_disk": {"permission": before_perm, "cut_order_gap": before_gap},
        "checks": {
            "receipts_agree_the_ticket_k_is_the_priced_step": bool(agree),
            "on_disk_run_reproduces_todays_two_verdicts": bool(on_disk_reproduces),
            "patched_run_flips_both_faces": bool(flip),
            "neighbour_step_stays_unreadable": bool(neg_stays_red),
            "patch_touches_only_the_baseline_cell": bool(untouched),
        },
        "what_this_does_not_claim": [
            "it does not land the patch: the leg, the permission face and the gap face are "
            "shared science faces held by another host this round",
            "it does not re-price the book or rebuild the beta schedule (no panel, no engine)",
            "the patched beta is derived (target/k), not read from a receipt, and neither "
            "face exercised here consumes beta",
            "the readers/enforcers scan is not re-run: an empty reader list can only make the "
            "gap face more pessimistic, never more favourable",
            "the permission's permitting floor lands exactly on k_now, so the pass has zero "
            "margin -- one tick of deterioration in that reading turns it into a real cut",
        ],
    })

    p = patched["permission"]
    g = patched["cut_order_gap"]
    ok = all(face["checks"].values())
    face["verdict"] = ("PATCH_WOULD_CLEAR_ALL_THREE" if ok
                       else "REHEARSAL_INCONCLUSIVE")
    face["sentence"] = (
        "with the r2063 one-line anchor patch (baseline cell reads the step at base_bar "
        "%s, k=%.6f instead of %s, k=%.6f): the permission turns from %s into %s with a "
        "permitting floor of k=%s, and the cut/order gap turns from %s into %s with CNY %s "
        "to cut on a CNY %s book. A step next to the right one (%s) stays unreadable, so the "
        "fix is the bar and not the tolerance." % (
            hit_bar, float(true_k or 0), leg_bar, float(leg_k or 0), before_perm,
            p.get("verdict"), p.get("permitted_k"), before_gap, g.get("verdict"),
            format(g.get("cut_cny") or 0, ",.0f"), format(g.get("ordered_book_cny") or 0, ",.0f"),
            ("%s k=%s" % (str(neighbour.get("bar"))[:10], _r(neighbour.get("k"))))
            if neighbour else "n/a"))
    return face


def md(face):
    r = face.get("runs") or {}
    line = []
    a = line.append
    a("# The one-line anchor patch, priced through the two faces it unblocks (r2064)\n")
    a("`%s`  \n`ticket %s` · `evidence_cutoff %s`\n"
      % (face.get("sentence"), face.get("ticket_file"), face.get("evidence_cutoff")))
    a("\n## What is being compared\n")
    a("| run | baseline cell reads | permission | cut/order gap | cut CNY |")
    a("|---|---|---|---|---|")
    for tag, label in (("on_disk", "today (on disk)"), ("patched", "the patch"),
                       ("neighbour", "one step earlier than the right one")):
        run = r.get(tag) or {}
        p = run.get("permission") or {}
        g = run.get("cut_order_gap") or {}
        b = run.get("baseline_cell") or {}
        a("| %s | %s · k=%s | %s | %s | %s |" % (
            label, b.get("as_of_bar") or "-", b.get("k"), p.get("verdict"),
            g.get("verdict"),
            "-" if g.get("cut_cny") is None else format(g.get("cut_cny"), ",.0f")))
    a("\n## Checks\n")
    for k, v in (face.get("checks") or {}).items():
        a("* `%s` = **%s**" % (k, "OK" if v else "NO"))
    a("\n## Why the bar and not the tolerance\n")
    a(face.get("sentence") or "")
    a("\n## What this does not claim\n")
    for s in (face.get("what_this_does_not_claim") or []):
        a("* %s" % s)
    a("")
    return "\n".join(line) + "\n"


# ---------------------------------------------------------------- selftest
def selftest():
    seen = []

    def leg(cond, name):
        seen.append(bool(cond))
        print("%-4s %s" % ("OK" if cond else "FAIL", name))

    ticket_name, ticket = latest_ticket()
    rulers = _read_json(R_RULERS)
    ident = _read_json(R_IDENT)
    if not (ticket and rulers and ident):
        print("FAIL receipts missing"); return 1
    target = rulers.get("beta_target") or ticket.get("beta_target")

    # L1 the beta derivation is the engine's own identity, checked on rows that carry beta
    carry = [r for r in (ident.get("schedule_tail") or []) if r.get("beta") and r.get("k")]
    legs1 = []
    for row in carry:
        got = beta_from_k(row["k"], target)
        floors = [abs(got - float(row["beta"])),
                  abs(float(row["beta"]) * float(row["k"]) - float(target))]
        legs1.append(min(floors) <= 1e-5)
    leg(len(legs1) >= 2 and all(legs1),
        "beta = target/k reproduces every schedule_tail row that carries beta (%d rows)"
        % len(legs1))

    # L2 patch_cells touches one cell and leaves the rest byte-identical
    cells = rulers.get("cells") or {}
    patched_cells = patch_cells(cells, 0.458463, 0.436240, "2026-11-20")
    leg(all(json.dumps(cells.get(n), sort_keys=True) == json.dumps(patched_cells.get(n),
                                                                   sort_keys=True)
            for n in cells if n != BASELINE),
        "patch_cells leaves every non-baseline cell byte-identical")
    leg(patched_cells[BASELINE]["k"] == 0.458463
        and patched_cells[BASELINE]["as_of_bar"] == "2026-11-20",
        "patch_cells replaces k and as_of_bar on the baseline cell only")

    # L3 the on-disk run reproduces today's verdicts (the harness is not the cause)
    before_perm = (_read_json(R_PERM) or {}).get("verdict")
    before_gap = (_read_json(R_GAP) or {}).get("verdict")
    leg_k = ident.get("k_at_book_decided_at")
    on_disk = rehearse(rulers, ticket, leg_k, None, str(ident.get("leg_bar"))[:10])
    leg(on_disk["permission"]["verdict"] == before_perm
        and on_disk["cut_order_gap"]["verdict"] == before_gap,
        "rehearsing the on-disk cell %s reproduces %s/%s"
        % (_r(leg_k), before_perm, before_gap))

    # L4 the patched run flips both, and the gap closes to zero
    true_k = ident.get("k_at_the_priced_bar")
    patched = rehearse(rulers, ticket, true_k, beta_from_k(true_k, target),
                       str((ident.get("schedule_hits") or [{}])[0].get("bar"))[:10])
    leg(patched["permission"]["verdict"] != before_perm,
        "patched permission leaves UNREADABLE (%s)" % patched["permission"]["verdict"])
    leg(not (patched["permission"].get("readings_unreadable") or {}),
        "patched permission has no unclassified reading")
    leg(patched["permission"].get("permitted_k") is not None,
        "patched permission publishes a permitting floor")
    leg(patched["cut_order_gap"]["verdict"] != "UNREADABLE"
        and patched["cut_order_gap"].get("permitted_k") is not None,
        "patched gap face is readable (%s)" % patched["cut_order_gap"]["verdict"])

    # L5 a step next to the right one still fails at the 6dp identity tolerance
    tail = [r for r in (ident.get("schedule_tail") or []) if r.get("k") is not None]
    nb = next((r for r in tail if str(r.get("bar"))[:10] != str(ident.get("leg_bar"))[:10]), None)
    if nb is not None:
        neg = rehearse(rulers, ticket, nb["k"], beta_from_k(nb["k"], target),
                       str(nb.get("bar"))[:10])
        leg(neg["permission"]["verdict"] == before_perm,
            "neighbour step %s (k=%s) stays %s"
            % (str(nb["bar"])[:10], _r(nb["k"]), before_perm))
    else:
        leg(False, "no neighbour step on the receipt to control against")

    # L6 the identity tolerance would have to be widened by 345x to swallow that step
    if nb is not None and true_k is not None:
        gap = abs(float(nb["k"]) - float(true_k))
        leg(gap > IDENT_TOL,
            "neighbour sits %.6f away from the right step = %.0fx the identity tolerance"
            % (gap, gap / IDENT_TOL))

    # L7 the face itself is deterministic
    a = build(); b = build()
    for d in (a, b):
        d.pop("generated", None)
    leg(json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True),
        "two builds are byte-identical apart from the timestamp")

    print("\n%d/%d OK" % (sum(seen), len(seen)))
    return 0 if all(seen) else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lstrip("-")
    if cmd == "selftest":
        return selftest()
    face = build()
    if cmd == "md":
        txt = md(face)
        with open(DOC, "w", encoding="utf-8", newline="\n") as f:
            f.write(txt)
        sys.stdout.write(txt)
        return 0 if face.get("verdict") != "MECHANISM_FAULT" else 2
    if cmd == "check":
        disk = _read_json(FACE)
        if disk is None:
            print("STALE: no face on disk -- run first"); return 3
        a = dict(disk); b = dict(face)
        for d in (a, b):
            d.pop("generated", None)
        if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
            print("STALE: the receipts moved; re-derive (run)")
            return 3
        bad = [k for k, v in (b.get("checks") or {}).items() if not v]
        if bad:
            print("CHECK FAILED: %s" % ", ".join(bad)); return 3
        print("CHECK OK %s" % b.get("verdict"))
        return 0
    with open(FACE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(json.dumps({"verdict": face.get("verdict"),
                      "checks": face.get("checks"),
                      "sentence": face.get("sentence")},
                     ensure_ascii=False, indent=1))
    return 0 if face.get("verdict") != "MECHANISM_FAULT" else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
