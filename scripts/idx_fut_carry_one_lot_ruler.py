"""One lot costs how much? -- one number, or two that a reader can't both hold.

r2097 shipped the decision face (IC 1132145.38 / IM 1161161.25 per lot). r2098 moved the
same numbers into capacity_lots. Meanwhile three faces written on 2026-11-23 still print
1124479.00 / 1152596.00 -- the previous generation of the very same measurement. A reader
who opens the portfolio-capital page sees "IC is 124,479 CNY short of its first lot" and
a reader who opens the decision page sees "129,566". Both are in the repo, both are said
with the same confidence, and nothing on either page says which generation it is.

This face does not recompute anybody. It lines the consumers up against the authority and
answers one question per consumer: is the number you print the number that is true today,
and if not, are you simply one generation early (rebuild me) or do we have two live rulers
(a real defect)? The attribution is by generation time, not by taste: a consumer older than
the authority and printing a different number is STALE (it read the old inputs); a consumer
at or after the authority and still printing a different number is a disagreement that
needs a human, because the inputs were already on disk when it ran.

Rules the code keeps:
  * authority = sizing_spec / open_capital / always_on_price. They must agree with each
    other to the cent (they are one measurement three ways); if they do not, that is
    AUTHORITY_DISAGREE and nothing downstream is worth judging.
  * money tolerance is 0.01 CNY -- these faces store cents; 1e-9 would redden on rounding.
  * one index tick (multiplier x 0.0001 = 0.02 CNY for IC/IM) is PRECISION_ONLY: two faces
    that agree to a tick print the same money, so neither a rebuild nor a defect is bought.
    Anything above a tick is still DISAGREE -- the third state names a size, it does not
    widen the door.
  * a missing face or field is DATA_BLOCKED, never a default of 0 (r98 family).
  * only the STALE branch says "STALE". The word is a contract: run_leg pays to rebuild
    only when it reads it (r1850/r1934), and a real defect must not buy a rebuild.
  * the arithmetic projection (what the floor would be after a rebuild) is labelled
    arithmetic_only -- it is a delta, not a re-derived face.

Usage:
  python scripts/idx_fut_carry_one_lot_ruler.py run [--write]
  python scripts/idx_fut_carry_one_lot_ruler.py check
  python scripts/idx_fut_carry_one_lot_ruler.py --selftest
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "results", "idx_fut_carry_one_lot_ruler.json")
DOC_PATH = os.path.join(ROOT, "research", "IDX_FUT_CARRY_ONE_LOT_RULER.md")
SCHEMA = "idx-fut-carry-one-lot-ruler/v1"
MONEY_TOL = 0.01
PRODUCTS = ("IC", "IM")

# The smallest amount of money this measurement can express. Index quotes are stored at four
# decimals, so one contract carries a quantum of multiplier x 0.0001 CNY: 0.02 for IC and IM
# (200 CNY a point). Two faces that both say "1132145.xx" and differ by one quantum are not
# printing two answers -- they accumulated the same sigma in a different order.
PRICE_QUANTUM = 0.0001
MULTIPLIER = {"IC": 200, "IM": 200}
DEFAULT_TICK_CNY = 0.02

# The three faces that each carry "what one legal lot costs". They are written by the same
# chain legs in the same pass; if they ever disagree the ruler itself is broken.
AUTHORITY = (
    ("sizing_spec", "results/idx_fut_carry_sizing_spec.json",
     ("accounts", "{p}", "first_executable_capital_cny")),
    ("open_capital", "results/idx_fut_carry_open_capital.json",
     ("accounts", "{p}", "funding", "first_rung_cny")),
    ("always_on_price", "results/idx_fut_carry_always_on_price.json",
     ("products", "{p}", "first_rung_cny")),
)

# Everything that prints one of those numbers on a page a reader can open. Two of these are
# same-generation as the authority (decision_face, capacity_lots) -- keeping them in the
# list is the control: the judge has to separate fresh from stale, not just shout.
CONSUMERS = (
    ("forward_clock", "results/idx_fut_carry_forward_clock.json",
     ("accounts", "{p}", "first_rung_cny")),
    ("portfolio_capital", "results/idx_fut_carry_portfolio_capital.json",
     ("measured_arms", "{p}", "first_rung_cny")),
    ("tradeable_hedge_capital", "results/idx_fut_carry_tradeable_hedge_capital.json",
     ("accounts", "{p}", "reference", "capital_cny")),
    ("decision_face", "results/idx_fut_carry_decision_face.json",
     ("products", "{p}", "capital", "first_rung_cny")),
    ("capacity_lots", "results/idx_fut_carry_capacity_lots.json",
     ("products", "{p}", "desk", "capital_per_lot_cny")),
)

NOT_RECOMPUTED = (
    "the per-lot capital itself (results/idx_fut_carry_sizing_spec.json and its two peers)",
    "any downstream income, Sharpe or floor: this face only prices the gap",
)


# ---------------------------------------------------------------- io helpers

def _read_json(rel):
    p = rel if os.path.isabs(rel) else os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return None
    with io.open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _sha(rel):
    p = rel if os.path.isabs(rel) else os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return None
    h = hashlib.sha256()
    with io.open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _dig(obj, path):
    cur = obj
    for seg in path:
        if not isinstance(cur, dict) or seg not in cur:
            return None
        cur = cur[seg]
    return cur


def _gen_epoch(stamp):
    """Parse the several timestamps this repo already uses (+08:00, +0800, naive)."""
    if not isinstance(stamp, str) or not stamp.strip():
        return None
    s = stamp.strip()
    if len(s) > 5 and (s[-5] in "+-" and s[-3] != ":"):
        s = s[:-2] + ":" + s[-2:]
    try:
        d = _dt.datetime.fromisoformat(s)
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=_dt.timezone(_dt.timedelta(hours=8)))
    return d.timestamp()


def _money(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


# ---------------------------------------------------------------- derive

def _authority_block():
    out = {}
    for label, face, path in AUTHORITY:
        doc = _read_json(face)
        if doc is None:
            out[label] = {"face": face, "missing": True}
            continue
        out[label] = {
            "face": face,
            "generated": doc.get("generated"),
            "gen_epoch": _gen_epoch(doc.get("generated")),
            "cutoff": doc.get("evidence_cutoff"),
            "values": {p: _dig(doc, [s.replace("{p}", p) for s in path]) for p in PRODUCTS},
        }
    return out


def _authority_agrees(auth):
    """One measurement three ways: they must match to the cent, per product."""
    problems = []
    for prod in PRODUCTS:
        seen = {}
        for label, _face, _path in AUTHORITY:
            blk = auth.get(label) or {}
            if blk.get("missing"):
                problems.append("%s.%s face missing" % (label, prod))
                continue
            v = (blk.get("values") or {}).get(prod)
            if not _money(v):
                problems.append("%s.%s value unreadable (%r)" % (label, prod, v))
                continue
            seen[label] = float(v)
        if len(seen) >= 2:
            lo, hi = min(seen.values()), max(seen.values())
            if hi - lo > MONEY_TOL:
                problems.append("%s authority disagrees: %s" % (
                    prod, ", ".join("%s=%.2f" % (k, v) for k, v in sorted(seen.items()))))
    return problems


def _authority_number(auth, prod):
    """The number to judge against: the newest authority reading for this product."""
    best = None
    for label, _face, _path in AUTHORITY:
        blk = auth.get(label) or {}
        v = (blk.get("values") or {}).get(prod)
        if not _money(v):
            continue
        ep = blk.get("gen_epoch")
        cand = (ep if ep is not None else -1.0, label, float(v))
        if best is None or cand[0] > best[0]:
            best = cand
    if best is None:
        return None
    return {"label": best[1], "value": best[2], "gen_epoch": best[0] if best[0] >= 0 else None}


def _tick_cny(prod):
    return round(MULTIPLIER.get(prod, 200) * PRICE_QUANTUM, 4)


def _judge(value, gen_epoch, auth_value, auth_epoch, prod=None):
    """Fresh / precision-only / stale-by-generation / disagree / unreadable.

    The word choice is the contract. PRECISION_ONLY sits between FRESH and STALE: the two
    faces print the same money up to one index tick, so there is nothing to rebuild and
    nothing to escalate -- but it is also not an equality, and a reader should see it.
    """
    if not _money(value):
        return "DATA_BLOCKED", None, "no readable number on this face (not defaulted to 0)"
    delta = round(float(value) - float(auth_value), 2)
    if abs(delta) <= MONEY_TOL:
        return "FRESH", 0.0, "prints the current ruler"
    tick = _tick_cny(prod)
    if abs(delta) <= tick + MONEY_TOL:
        extra = "" if abs(delta) <= tick else " plus a cent of display rounding"
        return "PRECISION_ONLY", delta, (
            "one index tick%s: %.2f CNY at %dx multiplier -- the same measurement accumulated "
            "in a different order, not a second ruler"
            % (extra, tick, MULTIPLIER.get(prod, 200)))
    if gen_epoch is None or auth_epoch is None:
        return "UNATTRIBUTED", delta, ("cannot tell which generation this came from "
                                       "(missing timestamp) -- treat as a defect, not as drift")
    if gen_epoch < auth_epoch - 1.0:
        return "STALE_BY_GENERATION", delta, (
            "written before the ruler moved; it read the previous inputs -- rebuild this face")
    return "DISAGREE", delta, (
        "written at or after the ruler moved and still prints another number -- "
        "same inputs, two answers, needs a human")


def derive():
    auth = _authority_block()
    auth_problems = _authority_agrees(auth)

    consumers = []
    for label, face, path in CONSUMERS:
        doc = _read_json(face)
        if doc is None:
            for prod in PRODUCTS:
                consumers.append({
                    "label": label, "face": face, "product": prod,
                    "field": "/".join(path).replace("{p}", prod),
                    "value": None, "generated": None, "status": "DATA_BLOCKED",
                    "delta_cny": None, "note": "face missing",
                })
            continue
        gen = doc.get("generated")
        gen_ep = _gen_epoch(gen)
        for prod in PRODUCTS:
            value = _dig(doc, [s.replace("{p}", prod) for s in path])
            ruler = _authority_number(auth, prod)
            if ruler is None:
                status, delta, note = "DATA_BLOCKED", None, "authority unreadable"
            else:
                status, delta, note = _judge(value, gen_ep, ruler["value"],
                                             ruler["gen_epoch"], prod)
            consumers.append({
                "label": label, "face": face, "product": prod,
                "field": "/".join(path).replace("{p}", prod),
                "value": value, "generated": gen, "cutoff": doc.get("evidence_cutoff"),
                "status": status, "delta_cny": delta,
                "authority_label": (ruler or {}).get("label"),
                "authority_value": (ruler or {}).get("value"),
                "note": note,
            })

    statuses = {c["status"] for c in consumers}
    if auth_problems:
        verdict = "AUTHORITY_DISAGREE"
    elif "DISAGREE" in statuses or "UNATTRIBUTED" in statuses:
        verdict = "CONSUMERS_DISAGREE_WITH_AUTHORITY"
    elif "STALE_BY_GENERATION" in statuses:
        verdict = "CONSUMERS_ONE_GENERATION_BEHIND"
    elif "DATA_BLOCKED" in statuses:
        verdict = "DATA_BLOCKED"
    elif "PRECISION_ONLY" in statuses:
        verdict = "ONE_RULER_UP_TO_ONE_TICK"
    else:
        verdict = "ONE_RULER"

    rebuild = []
    for c in consumers:
        if c["status"] in ("STALE_BY_GENERATION", "DATA_BLOCKED"):
            if c["face"] not in [r["face"] for r in rebuild]:
                rebuild.append({
                    "face": c["face"], "label": c["label"],
                    "status": c["status"], "generated": c["generated"],
                    "products": [x["product"] for x in consumers
                                 if x["face"] == c["face"]
                                 and x["status"] in ("STALE_BY_GENERATION", "DATA_BLOCKED")],
                })

    # Arithmetic only: what the two published floors would read on the new ruler. These are
    # sums of deltas, not re-derived faces -- a rebuild still has to run.
    deltas = {}
    for c in consumers:
        if _money(c.get("delta_cny")):
            deltas.setdefault(c["label"], {})[c["product"]] = c["delta_cny"]
    projection = {}
    if "portfolio_capital" in deltas:
        d = deltas["portfolio_capital"]
        old_floor = 2277075.0
        if all(p in d for p in PRODUCTS):
            projection["portfolio_capital_floor"] = {
                "old_cny": old_floor,
                "new_cny": round(old_floor + sum(d.values()), 2),
                "delta_cny": round(sum(d.values()), 2),
                "basis": "arithmetic_only: sum of the two per-lot deltas added to the "
                         "published floor; the face itself must still be rebuilt",
            }
    if "forward_clock" in deltas:
        doc = _read_json("results/idx_fut_carry_forward_clock.json") or {}
        rows = []
        for prod in PRODUCTS:
            acct = (doc.get("accounts") or {}).get(prod) or {}
            money_per_lot = acct.get("one_lot_money_cny")
            old_rung = acct.get("first_rung_cny")
            ruler = _authority_number(auth, prod)
            if _money(money_per_lot) and _money(old_rung) and ruler and ruler["value"]:
                rows.append({
                    "product": prod,
                    "pnl_pct_on_first_rung_published": acct.get("one_lot_pnl_pct_on_first_rung"),
                    "pnl_pct_on_first_rung_on_current_ruler": round(
                        100.0 * money_per_lot / ruler["value"], 4),
                    "shift_pp": round(100.0 * money_per_lot / ruler["value"]
                                      - float(acct.get("one_lot_pnl_pct_on_first_rung") or 0.0), 4),
                })
        if rows:
            projection["forward_clock_one_lot_pct"] = {
                "rows": rows,
                "basis": "arithmetic_only: same P&L per lot, denominator moved to today's ruler",
            }

    inputs = {}
    for _label, face, _path in tuple(AUTHORITY) + tuple(CONSUMERS):
        inputs[face] = _sha(face)

    cutoffs = sorted({str((auth.get(l) or {}).get("cutoff")) for l, _f, _p in AUTHORITY
                      if (auth.get(l) or {}).get("cutoff")})
    return {
        "schema": SCHEMA,
        "kind": "one_lot_ruler_cross_face_check",
        "generated": _dt.datetime.now().astimezone().replace(microsecond=0).isoformat(),
        "evidence_cutoff": cutoffs[-1] if cutoffs else None,
        "question": "does every face that prints the cost of one legal lot print today's number?",
        "rule": {
            "authority": [l for l, _f, _p in AUTHORITY],
            "money_tol_cny": MONEY_TOL,
            "precision_tick_cny": {p: _tick_cny(p) for p in PRODUCTS},
            "precision_tick_basis": "multiplier x price quantum: 200 x 0.0001 = 0.02 CNY; "
                                    "a sub-tick difference is the same measurement summed "
                                    "in another order, so it is PRECISION_ONLY and neither "
                                    "a rebuild nor a defect",
            "attribution": "a consumer older than the authority and printing another number "
                           "is STALE (rebuild); one at or after the authority is DISAGREE",
            "only_stale_says_stale": "the word STALE is reserved for rebuildable drift",
        },
        "authority": auth,
        "authority_problems": auth_problems,
        "consumers": consumers,
        "rebuild_list": rebuild,
        "arithmetic_only": projection,
        "verdict": verdict,
        "inputs": inputs,
        "not_recomputed": list(NOT_RECOMPUTED),
    }


# ---------------------------------------------------------------- render

BEGIN = "<!-- one-lot-ruler:begin -->"
END = "<!-- one-lot-ruler:end -->"


def _fmt(v):
    return "{:,.2f}".format(v) if _money(v) else "--"


def render_block(d):
    L = [BEGIN]
    L.append("")
    L.append("generated %s | verdict **%s** | evidence cutoff %s"
             % (d.get("generated"), d.get("verdict"), d.get("evidence_cutoff")))
    L.append("")
    L.append("## What one legal lot costs today")
    L.append("")
    L.append("| product | sizing_spec | open_capital | always_on_price |")
    L.append("|---|---|---|---|")
    for prod in PRODUCTS:
        row = [prod]
        for label, _f, _p in AUTHORITY:
            v = ((d.get("authority") or {}).get(label) or {}).get("values", {}).get(prod)
            row.append(_fmt(v))
        L.append("| " + " | ".join(row) + " |")
    L.append("")
    L.append("## Every face that prints it")
    L.append("")
    L.append("| face | product | prints | today | delta | written | status |")
    L.append("|---|---|---|---|---|---|---|")
    for c in d.get("consumers") or []:
        L.append("| %s | %s | %s | %s | %s | %s | **%s** |" % (
            c.get("label"), c.get("product"), _fmt(c.get("value")),
            _fmt(c.get("authority_value")), _fmt(c.get("delta_cny")),
            (c.get("generated") or "")[:10], c.get("status")))
    L.append("")
    proj = (d.get("arithmetic_only") or {})
    if proj:
        L.append("## If the stale faces are rebuilt (arithmetic only)")
        L.append("")
        for key in ("portfolio_capital_floor",):
            blk = proj.get(key)
            if blk:
                L.append("- opening one lot of every measured arm: %s -> %s (delta %s)"
                         % (_fmt(blk.get("old_cny")), _fmt(blk.get("new_cny")),
                            _fmt(blk.get("delta_cny"))))
                L.append("  - %s" % blk.get("basis"))
        fc = proj.get("forward_clock_one_lot_pct")
        if fc:
            for r in fc.get("rows") or []:
                L.append("- %s one lot P&L on its first rung: %s%% -> %s%% (shift %s pp)"
                         % (r.get("product"), r.get("pnl_pct_on_first_rung_published"),
                            r.get("pnl_pct_on_first_rung_on_current_ruler"),
                            r.get("shift_pp")))
            L.append("  - %s" % fc.get("basis"))
    L.append("")
    if d.get("rebuild_list"):
        L.append("## Rebuild these, in this order")
        L.append("")
        for r in d.get("rebuild_list") or []:
            L.append("- `%s` (%s, written %s) -- %s"
                     % (r.get("face"), r.get("label"), (r.get("generated") or "")[:10],
                        r.get("status")))
        L.append("")
    L.append("`--check` re-reads every one of these faces and re-derives the table; a face "
             "that moved says STALE, a number that moved with the same inputs says "
             "CHECK FAILED.")
    L.append("")
    L.append(END)
    return "\n".join(L)


def render_doc(d):
    L = []
    L.append("# 一手到底要多少钱：一个数，还是两个读者都拿不住数")
    L.append("")
    L.append("同一件事在桌面上有两条腿在印：11-25 那一代（sizing_spec / open_capital / "
             "always_on_price / decision_face / capacity_lots）说 IC 一手 1,132,145.38 元、"
             "IM 一手 1,161,161.25 元；11-23 那一代（forward_clock / portfolio_capital / "
             "tradeable_hedge_capital）仍印 1,124,479.00 / 1,152,596.00。差 7,666.38 与 "
             "8,565.25 元/手，两边都用同样的语气说话，任何一页都不说自己属于哪一代。")
    L.append("")
    L.append("这一页不重算任何人的数，只问一句话：**你印的这个数，是不是今天真的那个**；"
             "如果不是，你是早了一代（重生即可），还是我们有两把同时在用的尺子（真缺陷）。"
             "归因按生成时刻，不按口味：比权威面早、数不同=STALE；不早于权威面还不同=DISAGREE。")
    L.append("")
    L.append(render_block(d))
    L.append("")
    L.append("## 为什么这页值得存在")
    L.append("")
    L.append("那三张 11-23 的面没有任何链腿会自动重生它们——它们的上游在一小时前刚被链推过，"
             "于是「差多少钱才够开一手」这个 CEO 会读的数字在两张页面上差 16,231.63 元。"
             "把这个问题变成一条 check-only 的腿，比记住「记得重生那三张」可靠。")
    L.append("")
    L.append("## 这页没有回答的")
    L.append("")
    for s in NOT_RECOMPUTED:
        L.append("- " + s)
    L.append("")
    return "\n".join(L)


def write_all(d):
    with io.open(OUT_PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1, sort_keys=False)
        fh.write("\n")
    with io.open(DOC_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_doc(d))
    return OUT_PATH, DOC_PATH


# ---------------------------------------------------------------- check

def check(quiet=False, override_results=None, override_doc=None):
    """Re-derive and compare. Moved input bytes -> STALE; moved numbers with the same inputs
    -> CHECK FAILED (without the word STALE), per r1850/r1934/r1935."""
    path = override_results or OUT_PATH
    published = _read_json(path)
    if published is None:
        print("STALE face missing: results/idx_fut_carry_one_lot_ruler.json")
        return 3
    fresh = derive()

    moved = sorted(k for k, v in (published.get("inputs") or {}).items()
                   if (fresh.get("inputs") or {}).get(k) != v)
    if moved:
        if not quiet:
            print("STALE: input face(s) moved: %s -- rebuild this face" % ", ".join(moved))
        return 3

    problems = []
    if published.get("verdict") != fresh.get("verdict"):
        problems.append("verdict %r -> %r" % (published.get("verdict"), fresh.get("verdict")))
    if bool(published.get("authority_problems")) != bool(fresh.get("authority_problems")):
        problems.append("authority_problems %r -> %r"
                        % (published.get("authority_problems"), fresh.get("authority_problems")))

    pub = {(c.get("label"), c.get("product")): c for c in published.get("consumers") or []}
    new = {(c.get("label"), c.get("product")): c for c in fresh.get("consumers") or []}
    for key in sorted(set(pub) | set(new)):
        a, b = pub.get(key), new.get(key)
        if a is None or b is None:
            problems.append("%s only on one side" % (key,))
            continue
        if a.get("status") != b.get("status"):
            problems.append("%s status %r -> %r" % (key, a.get("status"), b.get("status")))
            continue
        for f in ("delta_cny", "value"):
            va, vb = a.get(f), b.get(f)
            if _money(va) and _money(vb):
                if abs(float(va) - float(vb)) > MONEY_TOL:
                    problems.append("%s %s %r -> %r" % (key, f, va, vb))
            elif va != vb:
                problems.append("%s %s %r -> %r" % (key, f, va, vb))

    ra = sorted(r.get("face") for r in published.get("rebuild_list") or [])
    rb = sorted(r.get("face") for r in fresh.get("rebuild_list") or [])
    if ra != rb:
        problems.append("rebuild_list %r -> %r" % (ra, rb))

    # The doc has to say the same thing as the JSON; a hand-edited table is a lie we can catch.
    dp = override_doc or DOC_PATH
    if not os.path.exists(dp):
        problems.append("doc missing: %s" % dp)
    else:
        with io.open(dp, "r", encoding="utf-8") as fh:
            body = fh.read()
        block = render_block(published)
        if block.strip() not in body.replace("\r\n", "\n"):
            problems.append("doc block does not match the published numbers (rendered block "
                            "is not a verbatim substring of the page)")

    if problems:
        if not quiet:
            for p in problems:
                print("CHECK FAILED: " + p)
        return 3
    if not quiet:
        print("CHECK_OK %s (%d consumers, verdict %s)"
              % (os.path.basename(path), len(fresh.get("consumers") or []), fresh.get("verdict")))
    return 0


# ---------------------------------------------------------------- selftest

def _leg(name, ok):
    print(("PASS " if ok else "FAIL ") + name)
    return bool(ok)


def selftest():
    results = []
    auth_v, auth_e = 1132145.38, 1_795_000_000.0

    s, d, _ = _judge(auth_v, auth_e + 100, auth_v, auth_e)
    results.append(_leg("equal value is FRESH whatever the generation", s == "FRESH"))

    s, d, note = _judge(1124479.00, auth_e - 100, auth_v, auth_e)
    results.append(_leg("older face with another number is STALE_BY_GENERATION "
                        "(%s, delta %.2f)" % (s, d or 0),
                        s == "STALE_BY_GENERATION" and note.startswith("written before")))

    s, d, note = _judge(1124479.00, auth_e + 100, auth_v, auth_e)
    results.append(_leg("same-or-later face with another number is DISAGREE, not drift",
                        s == "DISAGREE" and "STALE" not in note.upper()))

    s, d, note = _judge(None, auth_e, auth_v, auth_e)
    results.append(_leg("missing number is DATA_BLOCKED and never defaulted to 0",
                        s == "DATA_BLOCKED" and d is None))

    s, d, _ = _judge(auth_v + 0.005, auth_e, auth_v, auth_e)
    results.append(_leg("half-cent rounding stays FRESH (money tolerance is a cent)",
                        s == "FRESH"))

    s, d, note = _judge(1124479.00, None, auth_v, auth_e)
    results.append(_leg("undated consumer is UNATTRIBUTED and treated as a defect",
                        s == "UNATTRIBUTED" and "STALE" not in note.upper()))

    # The third state: one index tick is the same money, two ticks are two numbers.
    s, d, note = _judge(auth_v - 0.02, auth_e, auth_v, auth_e, "IC")
    results.append(_leg("one tick (0.02 on IC) is PRECISION_ONLY, not drift and not a defect "
                        "(%s, delta %.2f)" % (s, d or 0),
                        s == "PRECISION_ONLY" and "tick" in note and "STALE" not in note.upper()))
    s, d, note = _judge(auth_v - 0.02, auth_e - 100, auth_v, auth_e, "IC")
    results.append(_leg("one tick on an older face is still PRECISION_ONLY -- nothing to rebuild",
                        s == "PRECISION_ONLY"))
    s, d, note = _judge(auth_v - 0.05, auth_e, auth_v, auth_e, "IC")
    results.append(_leg("two and a half ticks is DISAGREE -- the third state names a size, "
                        "it does not widen the door",
                        s == "DISAGREE" and "STALE" not in note.upper()))

    # The whole-derivation legs, on the live repo (read-only): the judge must actually
    # separate fresh from stale here, not just in the toy cases above.
    live = derive()
    statuses = {(c["label"], c["product"]): c["status"] for c in live["consumers"]}
    fresh_side = [k for k, v in statuses.items()
                  if k[0] in ("decision_face", "capacity_lots") and v == "FRESH"]
    results.append(_leg("live: same-generation consumers (decision_face/capacity_lots) read FRESH",
                        len(fresh_side) >= 2))
    stale_side = [k for k, v in statuses.items()
                  if k[0] in ("forward_clock", "portfolio_capital", "tradeable_hedge_capital")
                  and v in ("STALE_BY_GENERATION", "FRESH")]
    results.append(_leg("live: the three 11-23 faces are classified (stale or already rebuilt)",
                        len(stale_side) >= 3))
    results.append(_leg("live: verdict is one of the declared words",
                        live["verdict"] in ("ONE_RULER", "ONE_RULER_UP_TO_ONE_TICK",
                                            "CONSUMERS_ONE_GENERATION_BEHIND",
                                            "CONSUMERS_DISAGREE_WITH_AUTHORITY",
                                            "AUTHORITY_DISAGREE", "DATA_BLOCKED")))
    tick_rows = [c for c in live["consumers"] if c["status"] == "PRECISION_ONLY"]
    results.append(_leg("live: a PRECISION_ONLY row never also reads as STALE "
                        "(the two states are exclusive)",
                        all("STALE" not in (c.get("note") or "").upper() for c in tick_rows)))
    proj = live.get("arithmetic_only") or {}
    pf = proj.get("portfolio_capital_floor")
    results.append(_leg("live: the floor projection is a sum of the two per-lot deltas",
                        pf is None or abs(pf["new_cny"] - pf["old_cny"] - pf["delta_cny"]) < 0.01))

    # Behaviour leg: poison a copy of the published face and prove check() tells "drift"
    # from "defect" -- STALE when an input moved, CHECK FAILED when only a number moved.
    import shutil
    import tempfile
    tmpdir = tempfile.mkdtemp(prefix="onelot_")
    try:
        if os.path.exists(OUT_PATH):
            src = _read_json(OUT_PATH)
            pub_in = dict(src.get("inputs") or {})
            # (a) pretend an input face moved: check must say STALE and rebuild
            bad_in = dict(src)
            bad_in["inputs"] = dict(pub_in)
            k0 = next(iter(bad_in["inputs"]))
            bad_in["inputs"][k0] = "0" * 64
            p1 = os.path.join(tmpdir, "a.json")
            with io.open(p1, "w", encoding="utf-8") as fh:
                json.dump(bad_in, fh)
            import contextlib
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc1 = check(quiet=False, override_results=p1)
            out1 = buf.getvalue()
            results.append(_leg("poisoned input digest -> rc3 and the word STALE",
                                rc1 == 3 and "STALE" in out1))
            # (b) change one consumer's delta only: inputs unchanged -> CHECK FAILED without STALE
            bad_num = json.loads(json.dumps(src))
            if bad_num.get("consumers"):
                bad_num["consumers"][0]["delta_cny"] = (
                    float(bad_num["consumers"][0].get("delta_cny") or 0.0) + 12345.0)
            p2 = os.path.join(tmpdir, "b.json")
            with io.open(p2, "w", encoding="utf-8") as fh:
                json.dump(bad_num, fh)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc2 = check(quiet=False, override_results=p2)
            out2 = buf.getvalue()
            results.append(_leg("poisoned number with the same inputs -> rc3, CHECK FAILED, "
                                "and no STALE word",
                                rc2 == 3 and "CHECK FAILED" in out2 and "STALE" not in out2))
        else:
            results.append(_leg("(skipped behaviour legs: run `run` once to publish)", True))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    print("%d/%d PASS" % (sum(1 for r in results if r), len(results)))
    return 0 if all(results) else 1


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description="cross-face one-lot ruler check")
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=("run", "check", "selftest"))
    ap.add_argument("--write", action="store_true", help="write the research page too")
    ap.add_argument("--selftest", action="store_true", help="alias for cmd=selftest")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "check":
        return check(quiet=a.quiet)
    d = derive()
    rp, dp = write_all(d)
    if not a.quiet:
        print("verdict %s | %d consumers | rebuilt list %d | -> %s"
              % (d["verdict"], len(d["consumers"]), len(d["rebuild_list"]),
                 os.path.relpath(rp, ROOT)))
        for c in d["consumers"]:
            print("  %-24s %s %14s vs %14s  %-22s %s"
                  % (c["label"], c["product"], _fmt(c.get("value")),
                     _fmt(c.get("authority_value")), c["status"], _fmt(c.get("delta_cny"))))
    if d["verdict"] in ("AUTHORITY_DISAGREE", "CONSUMERS_DISAGREE_WITH_AUTHORITY"):
        return 3
    if d["verdict"] == "DATA_BLOCKED":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
