"""Did the buy-back that broke the 20 pct ceiling pay?

r1983 measured the *flows*: on 2026-11-09 three accounts cut to 18.4/17.6/9.9 pct and
the very next session bought back 99/125/99 pct of what they sold.  This face asks the
next question, because a rule that costs money to obey is a different problem from one
that costs money to break:

    the lots opened on the re-buy day, marked to the latest export, made or lost what?

Split by asset class, because the breach and the money are not the same legs: the
cash-substitute legs (government-bond ETFs) are what pushed the accounts over the line,
while the equity leg is the risk the rule is written about.

Read-only over the exported faces.  Writes only its own results JSON.
Cross-gate: this face only speaks when the re-buy-day lots it reconstructs reproduce the
operating amounts r1983 already published (within 1 yuan); otherwise STALE, no verdict
(r1934 family: a face that disagrees with its upstream does not get to print a ruling).
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

BACK_DAY = "export-2026-11-10.json"
MARK_DAY = "export-2026-11-20.json"
OUT = os.path.join(ROOT, "results", "regime_cap_breach_pnl.json")

# r1983 published these operating amounts for the 11-10 re-buy legs (CNY).
PUBLISHED_FLOWS = {
    "COMPOSITE-CE-01": 570000.56,
    "COMPOSITE-CE-02": 593500.98,
    "VOLATILITY-CE-01": 299999.11,
}
FLOW_TOL = 1.0

BOND_WORDS = ("债", "短融", "货币", "日利", "快线")


def _exports_dir():
    return os.path.join(ROOT, "results", "paper_export")


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def class_of(symbol, class_map):
    """Keyword class from the single-source classifier, with a bond-word fallback."""
    hit = class_map.get(str(symbol))
    if hit:
        return hit[0] if isinstance(hit, (tuple, list)) else str(hit)
    return "unknown"


def read_class_map():
    try:
        sys.path.insert(0, ROOT)
        from scripts.etf_equity_alpha import load_class_map  # single source, no second table
        return load_class_map(), None
    except Exception as exc:  # noqa: BLE001
        return None, "CANNOT_READ_CLASS_MAP: %s" % exc


def build(exports_dir=None, back_day=BACK_DAY, mark_day=MARK_DAY, class_map=None):
    """Returns (payload, rc).  Never writes the published face."""
    exports_dir = exports_dir or _exports_dir()
    out = {
        "face": "regime_cap_breach_pnl",
        "schema": "regime-cap-breach-pnl/v1",
        "generated": None,
        "evidence_cutoff": None,
        "back_day": back_day.replace("export-", "").replace(".json", ""),
        "mark_day": mark_day.replace("export-", "").replace(".json", ""),
        "class_source": "scripts/etf_equity_alpha.load_class_map",
        "published_flows": dict(PUBLISHED_FLOWS),
        "accounts": {},
        "totals": {},
        "verdict": None,
        "gates": {},
        "not_measured": [],
    }

    if class_map is None:
        class_map, err = read_class_map()
        if err:
            out["verdict"] = err
            out["gates"]["class_map"] = "UNREADABLE"
            return out, 2
    out["gates"]["class_map"] = "ok"

    pb = os.path.join(exports_dir, back_day)
    pm = os.path.join(exports_dir, mark_day)
    for tag, path in (("back", pb), ("mark", pm)):
        if not os.path.exists(path):
            out["verdict"] = "FACE_MISSING: %s" % os.path.basename(path)
            out["gates"][tag] = "missing"
            return out, 2
        try:
            _load(path)
        except Exception as exc:  # noqa: BLE001
            out["verdict"] = "FACE_UNREADABLE: %s (%s)" % (os.path.basename(path), exc)
            out["gates"][tag] = "unreadable"
            return out, 2
        out["gates"][tag] = "ok"

    back = _load(pb)
    mark = _load(pm)
    out["evidence_cutoff"] = mark.get("evidence_cutoff")
    marks = {}
    for trader in mark.get("traders", []):
        marks[trader.get("trader")] = {
            p.get("symbol"): p for p in trader.get("open_positions", [])
        }

    tot_pnl = tot_inv = 0.0
    bond_pnl = bond_inv = 0.0
    eq_pnl = eq_inv = 0.0
    exited_inv = 0.0
    flow_deltas = {}

    for trader in back.get("traders", []):
        name = trader.get("trader")
        lots = [p for p in trader.get("open_positions", [])
                if int(p.get("hold_days", 99)) <= 1]
        if not lots:
            continue
        rec = {"invested": 0.0, "pnl": 0.0, "bond": {"invested": 0.0, "pnl": 0.0, "legs": {}},
               "equity": {"invested": 0.0, "pnl": 0.0, "legs": {}}, "exited": []}
        for lot in lots:
            sym = str(lot.get("symbol"))
            qty = float(lot.get("quantity") or 0.0)
            cost = float(lot.get("cost_price") or 0.0)
            inv = qty * cost
            cls = class_of(sym, class_map)
            bucket = "bond" if any(w in str(cls) or w in str(lot.get("name", ""))
                                   for w in BOND_WORDS) or cls in ("bond", "cash") else "equity"
            now = marks.get(name, {}).get(sym)
            rec["invested"] += inv
            if now is None:
                exited_inv += inv
                rec["exited"].append({"symbol": sym, "invested": round(inv, 2),
                                      "note": "not in mark-day positions; realized P&L not reconstructed"})
                continue
            px = float(now.get("last_close") or 0.0)
            pnl = (px - cost) * qty
            rec["pnl"] += pnl
            rec[bucket]["invested"] += inv
            rec[bucket]["pnl"] += pnl
            rec[bucket]["legs"][sym] = {
                "quantity": round(qty, 2),
                "cost_price": cost,
                "mark_close": px,
                "pnl": round(pnl, 2),
                "ret_pct": round((px / cost - 1.0) * 100.0, 4) if cost else None,
                "class": cls,
            }
            if bucket == "bond":
                bond_pnl += pnl
                bond_inv += inv
            else:
                eq_pnl += pnl
                eq_inv += inv
        tot_pnl += rec["pnl"]
        tot_inv += rec["invested"]
        pub = PUBLISHED_FLOWS.get(name)
        if pub is not None:
            flow_deltas[name] = round(rec["invested"] - pub, 2)
        rec["invested"] = round(rec["invested"], 2)
        rec["pnl"] = round(rec["pnl"], 2)
        for bucket in ("bond", "equity"):
            rec[bucket]["invested"] = round(rec[bucket]["invested"], 2)
            rec[bucket]["pnl"] = round(rec[bucket]["pnl"], 2)
        out["accounts"][name] = rec

    out["totals"] = {
        "invested": round(tot_inv, 2),
        "invested_measured": round(tot_inv - exited_inv, 2),
        "invested_without_measure": round(exited_inv, 2),
        "pnl": round(tot_pnl, 2),
        "bond_invested": round(bond_inv, 2),
        "bond_pnl": round(bond_pnl, 2),
        "bond_ret_pct": round((bond_pnl / bond_inv) * 100.0, 4) if bond_inv else None,
        "equity_invested": round(eq_inv, 2),
        "equity_pnl": round(eq_pnl, 2),
        "equity_ret_pct": round((eq_pnl / eq_inv) * 100.0, 4) if eq_inv else None,
    }

    bad = {k: v for k, v in flow_deltas.items() if abs(v) > FLOW_TOL}
    out["gates"]["cross_gate_flows"] = {"deltas": flow_deltas,
                                        "tolerance": FLOW_TOL,
                                        "state": "STALE" if bad else "ok"}
    if bad:
        out["verdict"] = ("STALE: reconstructed re-buy amounts disagree with the published "
                          "flows %s -- no ruling printed" % json.dumps(bad, ensure_ascii=False))
        return out, 3

    if not out["accounts"]:
        out["verdict"] = "NO_REBUY_LOTS: no lots with hold_days<=1 on the back day"
        return out, 2

    bond_paid = bond_pnl >= 0
    if bond_paid:
        out["verdict"] = "BREACH_LEGS_PAID"
    else:
        out["verdict"] = "BREACH_LEGS_LOST_MONEY"

    for name, rec in out["accounts"].items():
        for leg in rec["exited"]:
            out["not_measured"].append(
                "%s %s: exited between the two days (%s CNY in); realized P&L not "
                "reconstructed from operations (export ops carry no price)" %
                (name, leg["symbol"], leg["invested"]))
    return out, 0


def check(payload, exports_dir=None, class_map=None):
    """Re-derive and compare; a face that cannot re-derive itself must not claim ok."""
    fresh, rc = build(exports_dir=exports_dir, class_map=class_map)
    if rc not in (0, 3):
        return rc, ["upstream cannot be re-derived: %s" % fresh.get("verdict")]
    problems = []
    for key in ("verdict", "totals", "evidence_cutoff"):
        if payload.get(key) != fresh.get(key):
            problems.append("%s: published %r vs re-derived %r" %
                            (key, payload.get(key), fresh.get(key)))
    if payload.get("gates", {}).get("cross_gate_flows", {}).get("state") != \
            fresh.get("gates", {}).get("cross_gate_flows", {}).get("state"):
        problems.append("cross_gate_flows state drifted")
    return (0 if not problems else 3), problems


def _selftest():
    import copy
    import tempfile
    ok = 0
    total = 0

    def leg(cond, msg):
        nonlocal ok, total
        total += 1
        if cond:
            ok += 1
        else:
            print("  FAIL %s" % msg)

    cmap = {"511010": ("bond", "10年国债ETF"), "511090": ("bond", "30年国债ETF"),
            "511260": ("bond", "10年地方债ETF"), "512800": ("equity", "银行ETF")}

    payload, rc = build(class_map=cmap)
    leg(rc == 0, "live build rc=%d (%s)" % (rc, payload.get("verdict")))
    leg(payload["verdict"] in ("BREACH_LEGS_LOST_MONEY", "BREACH_LEGS_PAID"),
        "live verdict is a ruling, got %r" % payload.get("verdict"))
    leg(payload["gates"]["cross_gate_flows"]["state"] == "ok",
        "live cross-gate is ok, got %r" % payload["gates"]["cross_gate_flows"])
    leg(all(abs(v) <= FLOW_TOL for v in payload["gates"]["cross_gate_flows"]["deltas"].values()),
        "live flow deltas within tolerance")
    leg(payload["totals"]["bond_invested"] > 0 and payload["totals"]["equity_invested"] > 0,
        "both buckets populated (bond=%s equity=%s)" %
        (payload["totals"]["bond_invested"], payload["totals"]["equity_invested"]))

    # missing export -> FACE_MISSING, never zeros
    with tempfile.TemporaryDirectory() as td:
        p2, rc2 = build(exports_dir=td, class_map=cmap)
        leg(rc2 == 2 and str(p2["verdict"]).startswith("FACE_MISSING"),
            "missing export must say FACE_MISSING, got %r" % p2.get("verdict"))
        leg(p2["totals"] == {}, "missing export must not print totals")

        # unreadable json -> FACE_UNREADABLE
        bad = os.path.join(td, BACK_DAY)
        with open(bad, "w", encoding="utf-8") as fh:
            fh.write("{not json")
        p3, rc3 = build(exports_dir=td, class_map=cmap)
        leg(rc3 == 2 and str(p3["verdict"]).startswith("FACE_UNREADABLE"),
            "bad json must say FACE_UNREADABLE, got %r" % p3.get("verdict"))

    # synthetic: a bond leg that gained flips the verdict to PAID
    src_back = _load(os.path.join(_exports_dir(), BACK_DAY))
    src_mark = _load(os.path.join(_exports_dir(), MARK_DAY))
    with tempfile.TemporaryDirectory() as td:
        bump = copy.deepcopy(src_mark)
        for trader in bump.get("traders", []):
            for pos in trader.get("open_positions", []):
                if str(pos.get("symbol")) in ("511010", "511090", "511260"):
                    pos["last_close"] = float(pos["last_close"]) * 1.02
        with open(os.path.join(td, BACK_DAY), "w", encoding="utf-8") as fh:
            json.dump(src_back, fh)
        with open(os.path.join(td, MARK_DAY), "w", encoding="utf-8") as fh:
            json.dump(bump, fh)
        p4, rc4 = build(exports_dir=td, class_map=cmap)
        leg(rc4 == 0 and p4["verdict"] == "BREACH_LEGS_PAID",
            "+2%% on the bond legs must flip the ruling to PAID, got %r" % p4.get("verdict"))

        # synthetic: hold_days>1 lots are not re-buy lots, so their losses stay out
        deep = copy.deepcopy(src_back)
        for trader in deep.get("traders", []):
            for pos in trader.get("open_positions", []):
                pos["hold_days"] = int(pos.get("hold_days", 1)) + 5
        with open(os.path.join(td, BACK_DAY), "w", encoding="utf-8") as fh:
            json.dump(deep, fh)
        p5, rc5 = build(exports_dir=td, class_map=cmap)
        leg(rc5 == 2 and str(p5["verdict"]).startswith("NO_REBUY_LOTS"),
            "old lots must not be read as re-buy lots, got %r" % p5.get("verdict"))

        # cross-gate: move one published flow by 5 yuan -> STALE, no ruling
        saved = dict(PUBLISHED_FLOWS)
        try:
            k = sorted(PUBLISHED_FLOWS)[0]
            PUBLISHED_FLOWS[k] = PUBLISHED_FLOWS[k] + 5.0
            with open(os.path.join(td, BACK_DAY), "w", encoding="utf-8") as fh:
                json.dump(src_back, fh)
            p6, rc6 = build(exports_dir=td, class_map=cmap)
            leg(rc6 == 3 and str(p6["verdict"]).startswith("STALE"),
                "cross-gate mismatch must be STALE, got %r" % p6.get("verdict"))
        finally:
            PUBLISHED_FLOWS.clear()
            PUBLISHED_FLOWS.update(saved)

    # selftest must never write the published face
    if os.path.exists(OUT):
        before = os.path.getmtime(OUT)
        _ = build(class_map=cmap)
        leg(os.path.getmtime(OUT) == before, "selftest/build must not touch the published face")

    print("%d/%d PASS" % (ok, total))
    return 0 if ok == total else 1


def run(write=True):
    payload, rc = build()
    if write and rc in (0, 3):
        payload["generated"] = __import__("datetime").datetime.now().astimezone().isoformat(
            timespec="seconds")
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"verdict": payload.get("verdict"), "rc": rc,
                      "totals": payload.get("totals")}, ensure_ascii=False))
    return rc


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "--selftest":
        return _selftest()
    if cmd == "run":
        return run(write=True)
    if cmd == "check":
        if not os.path.exists(OUT):
            print("STALE: face missing at %s" % OUT)
            return 3
        payload = _load(OUT)
        rc, problems = check(payload)
        print(json.dumps({"rc": rc, "problems": problems}, ensure_ascii=False))
        return rc
    if cmd == "show":
        print(json.dumps(build(class_map=None)[0], ensure_ascii=False, indent=1))
        return 0
    print("usage: regime_cap_breach_pnl.py [run|check|--selftest|show]")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
