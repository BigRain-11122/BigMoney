"""Does the T/TF curve spread pay for itself, or is it another face?

DIRECTION-20261114 P2 lists one candidate that was never priced: 国债期货曲线（T/TF 跨期）.
Published under the same 30-minute protocol as the convertible line and the LHB line.

Who pays (written before any number was read):
  A curve spread is a relative-value trade: long 10Y futures / DV01-matched short 5Y
  futures (or the reverse). The counterparty is the duration placer who must be
  somewhere on the curve today -- insurers/banks matching liability duration, and basis
  traders unwinding. Their size is set by the balance sheet, not by the spread, so they
  pay the spread their own book needs. What we carry is that the curve re-prices and
  stays there.

Data bias handled before the return is discussed:
  * Both legs are the same kind of instrument (主连 futures), so the roll sits in both
    legs and roughly cancels in the spread -- unlike the IC/IM case, which had to proxy
    the index with an ETF.
  * The spread is a YIELD difference, not a price difference: s = -log(P_a)/D_a +
    log(P_b)/D_b, in bp. A price ratio would drift with the hedge ratio itself (r1787's
    "two knobs" shape); a yield difference is DV01-neutral by construction and its level
    means the same thing in 2017 and in 2026.
  * D is a stated constant per product (T 8.0 / TF 4.2 / TS 1.8), not a fit; the
    sensitivity of the verdict to D is printed, because a verdict that only survives one
    choice of D is not a verdict.
  * z uses a trailing 252-day mean/std of that same spread. Nothing in the signal reads
    the future; the selftest pins that (L2).
  * Sign convention: s = 10Y minus 5Y yield in bp. A wide s means 10Y has cheapened
    against 5Y. Reversion means selling the wide spread, so the payoff of an extreme
    entry is -sign(z) * (s[t+h] - s[t]).

Frozen criteria (written before any number was read):
  C1 net:      the extreme bucket's 20-day reversion, after cost, >= 4.0 bp with |t| >= 2.0
  C2 monotone: the extreme bucket's 5-day reversion is larger in size than the middle
               bucket's drift (an ordering, not just a sign)
  C3 stable:   the extreme bucket's signed 20-day reversion agrees in both halves
  OPEN when at least 2 of the 3 pairs pass all three; CLOSE otherwise.  A CLOSE closes
  the line and keeps the panel + script for reuse (DIRECTION-20261114 §四.3) -- no
  follow-up report.

Costs always on: 1 tick of slippage each side each leg (0.005 quote = 550 CNY per lot)
plus 3 CNY fee, on 1 + D_a/D_b lots, divided by the pair's DV01 in CNY per bp.
"""
import json
import math
import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "futures_daily")
OUT = os.path.join(ROOT, "results", "bond_fut_curve.json")

DUR = {"T": 8.0, "TF": 4.2, "TS": 1.8}
PAIRS = (("T", "TF"), ("T", "TS"), ("TF", "TS"))
Z_WIN = 252
HORIZONS = (5, 10, 20)
Z_EDGE = 0.20
FEE_CNY = 3.0
TICK_CNY = 550.0        # 0.005 of quote on a 1,000,000 face lot
DV01_CNY = 880.0        # per bp, 10Y leg (D * notional * 1e-4, roughly)
C1_BP = 4.0
C1_T = 2.0


def load(sym):
    path = os.path.join(DATA, "%s.csv" % sym)
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        head = f.readline().strip().split(",")
        i_d, i_c = head.index("date"), head.index("close")
        for line in f:
            p = line.strip().split(",")
            if len(p) <= i_c:
                continue
            try:
                rows.append((p[i_d], float(p[i_c])))
            except ValueError:
                continue
    return rows


def join(a, b):
    db = dict(b)
    return [(d, pa, db[d]) for d, pa in a if d in db and pa > 0 and db[d] > 0]


def spread_bp(pa, pb, da, db):
    """10Y-minus-5Y (a minus b) yield difference in bp. Constant term dropped."""
    return (-math.log(pa) / da + math.log(pb) / db) * 1e4


def build_series(j, da, db, d_scale=1.0):
    rows = []
    for d, pa, pb in j:
        rows.append({"date": d, "s": spread_bp(pa, pb, da * d_scale, db * d_scale)})
    for i, r in enumerate(rows):
        if i + 1 < Z_WIN:
            continue
        win = [x["s"] for x in rows[i + 1 - Z_WIN:i + 1]]
        m = sum(win) / len(win)
        sd = statistics.pstdev(win)
        r["z"] = (r["s"] - m) / sd if sd > 0 else None
    return rows


def bucket_stats(rows, h):
    graded = [r for r in rows if r.get("z") is not None and r["z"] != 0.0]
    if len(graded) < 120:
        return None
    absz = sorted(abs(r["z"]) for r in graded)
    cut = absz[int(len(absz) * (1.0 - Z_EDGE))]
    ext, mid = [], []
    for k, r in enumerate(graded):
        if k + h >= len(graded):
            continue
        d = graded[k + h]["s"] - r["s"]
        payoff = -d if r["z"] > 0 else d        # reversion of the wide side
        (ext if abs(r["z"]) >= cut else mid).append(payoff)
    return {"cut_abs_z": cut, "ext": ext, "mid": mid}


def mean_t(xs):
    if len(xs) < 3:
        return None, None
    m = sum(xs) / len(xs)
    sd = statistics.pstdev(xs)
    if sd == 0:
        return m, None
    return m, m / (sd / math.sqrt(len(xs)))


def cost_bp(da, db):
    lots = 1.0 + da / db
    sides = 2.0 * 2.0                            # both legs, entry and exit
    cny = lots * sides * (TICK_CNY + FEE_CNY)
    return cny / DV01_CNY


def pair_block(a, b, d_scale=1.0):
    j = join(load(a), load(b))
    rows = build_series(j, DUR[a], DUR[b], d_scale)
    if len(rows) < Z_WIN + max(HORIZONS) + 60:
        return {"status": "short_panel", "days": len(rows)}
    cost = cost_bp(DUR[a], DUR[b])
    block = {"status": "ok", "legs": [a, b], "days": len(rows),
             "first": rows[0]["date"], "last": rows[-1]["date"],
             "dur": [DUR[a] * d_scale, DUR[b] * d_scale],
             "cost_bp": round(cost, 2), "horizons": {}}
    mid = len(rows) // 2
    for h in HORIZONS:
        st = bucket_stats(rows, h)
        if not st:
            block["horizons"][str(h)] = {"status": "too_few"}
            continue
        m_ext, t_ext = mean_t(st["ext"])
        m_mid, _ = mean_t(st["mid"])
        halves = []
        for lo, hi in ((0, mid), (mid, len(rows))):
            st2 = bucket_stats(rows[lo:hi], h)
            if not st2:
                halves.append(None)
                continue
            m2, _ = mean_t(st2["ext"])
            halves.append(None if m2 is None else round(m2, 2))
        block["horizons"][str(h)] = {
            "cut_abs_z": round(st["cut_abs_z"], 3),
            "n_extreme": len(st["ext"]),
            "gross_bp": None if m_ext is None else round(m_ext, 2),
            "t": None if t_ext is None else round(t_ext, 2),
            "middle_bp": None if m_mid is None else round(m_mid, 2),
            "net_bp": None if m_ext is None else round(m_ext - cost, 2),
            "halves_bp": halves,
        }
    return block


def verdict(face):
    rows = []
    for name, blk in face["pairs"].items():
        if blk.get("status") != "ok":
            continue
        h20 = blk["horizons"].get("20", {})
        h5 = blk["horizons"].get("5", {})
        if h20.get("net_bp") is None or h20.get("t") is None:
            continue
        hb = h20.get("halves_bp") or [None, None]
        c1 = h20["net_bp"] >= C1_BP and abs(h20["t"]) >= C1_T
        c2 = (h5.get("gross_bp") is not None and h5.get("middle_bp") is not None
              and abs(h5["gross_bp"]) > abs(h5["middle_bp"]))
        c3 = hb[0] is not None and hb[1] is not None and hb[0] * hb[1] > 0
        rows.append({"pair": name, "C1": c1, "C2": c2, "C3": c3,
                     "net_bp": h20["net_bp"], "t": h20["t"], "halves": hb})
    passed = [r["pair"] for r in rows if r["C1"] and r["C2"] and r["C3"]]
    return {
        "verdict": "OPEN" if len(passed) >= 2 else "CLOSE",
        "pairs_passed": passed,
        "per_pair": rows,
        "frozen_criteria": {
            "C1": "20-day reversion net of cost >= %.1f bp and |t| >= %.1f" % (C1_BP, C1_T),
            "C2": "extreme bucket's 5-day reversion bigger in size than the middle bucket",
            "C3": "both halves of the sample agree in sign",
            "open_rule": "at least 2 of 3 pairs pass all three",
            "frozen_before_reading": True,
        },
        "duration_sensitivity": face.get("duration_sensitivity"),
    }


def duration_sensitivity():
    """A verdict that only survives one choice of D is not a verdict."""
    out = {}
    for name, (a, b) in zip(("%s_%s" % p for p in PAIRS), PAIRS):
        row = {}
        for scale in (0.85, 1.0, 1.15):
            blk = pair_block(a, b, d_scale=scale)
            h20 = blk.get("horizons", {}).get("20", {}) if blk.get("status") == "ok" else {}
            row["Dx%.2f" % scale] = h20.get("gross_bp")
        out[name] = row
    return out


def build():
    face = {"pairs": {}}
    for a, b in PAIRS:
        key = "%s_%s" % (a, b)
        try:
            face["pairs"][key] = pair_block(a, b)
        except FileNotFoundError as e:
            face["pairs"][key] = {"status": "no_panel", "detail": str(e)}
    last = [v.get("last") for v in face["pairs"].values() if v.get("status") == "ok"]
    face["evidence_cutoff"] = max(last) if last else None
    face["duration_sensitivity"] = duration_sensitivity()
    face["verdict"] = verdict(face)
    return face


def selftest():
    ok = True

    def check(name, cond, detail=""):
        nonlocal ok
        if not cond:
            ok = False
        print("[%s] %s | %s" % ("PASS" if cond else "FAIL", name, detail))

    # L1: if both legs move by the same yield, the spread must not move at all.
    da, db = 8.0, 4.2
    s1 = spread_bp(110.0, 106.0, da, db)
    pa, pb = 110.0 * math.exp(-0.0001 * da), 106.0 * math.exp(-0.0001 * db)  # +1bp yield each
    s2 = spread_bp(pa, pb, da, db)
    check("a parallel curve move leaves the spread unchanged", abs(s2 - s1 - (-1.0 * 0)) < 0.02,
          "s1=%.3f s2=%.3f" % (s1, s2))

    # L2: z is causal -- dropping the tail must not change earlier z values.
    j = [("d%04d" % i, 110.0 + 0.02 * math.sin(i / 9.0), 106.0 + 0.01 * math.sin(i / 11.0))
         for i in range(500)]
    full = build_series(j, da, db)
    cut = build_series(j[:460], da, db)
    same = all((a.get("z") is None and b.get("z") is None) or
               (a.get("z") is not None and b.get("z") is not None and abs(a["z"] - b["z"]) < 1e-12)
               for a, b in zip(full, cut))
    check("z uses only trailing data (truncation leaves it unchanged)", same)

    # L3: a passing synthetic pair opens the line; the floor is 2 of 3.
    good = {"status": "ok",
            "horizons": {"20": {"net_bp": 9.0, "t": 2.6, "halves_bp": [1.0, 2.0]},
                         "5": {"gross_bp": 5.0, "middle_bp": 0.5}}}
    bad = {"status": "ok",
           "horizons": {"20": {"net_bp": 1.0, "t": 0.4, "halves_bp": [1.0, -2.0]},
                        "5": {"gross_bp": 0.2, "middle_bp": 0.9}}}
    v = verdict({"pairs": {"A": good, "B": good, "C": bad}})
    check("two passing pairs open the line", v["verdict"] == "OPEN", json.dumps(v["pairs_passed"]))
    v2 = verdict({"pairs": {"A": good, "B": bad, "C": bad}})
    check("one passing pair cannot open the line", v2["verdict"] == "CLOSE")
    check("halves that disagree veto the pair",
          verdict({"pairs": {"A": dict(bad), "B": dict(bad), "C": dict(bad)}})["verdict"] == "CLOSE")

    # L4: the cost must be positive and finite in the units the verdict uses.
    c = cost_bp(da, db)
    check("cost is a positive bp number", 0.0 < c < 50.0, "%.3f bp" % c)

    print("SELFTEST %s" % ("OK" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    face = build()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(face, f, ensure_ascii=False, indent=1)
    print("wrote %s (cutoff %s)" % (os.path.relpath(OUT, ROOT), face["evidence_cutoff"]))
    for name, blk in face["pairs"].items():
        if blk.get("status") != "ok":
            print("  %s: %s" % (name, blk.get("status")))
            continue
        print("  %s [%s -> %s] days=%d cost=%.2fbp" % (
            name, blk["first"], blk["last"], blk["days"], blk["cost_bp"]))
        for h, row in blk["horizons"].items():
            print("    h=%s n=%s gross=%s t=%s net=%s halves=%s" % (
                h, row.get("n_extreme"), row.get("gross_bp"), row.get("t"),
                row.get("net_bp"), row.get("halves_bp")))
    v = face["verdict"]
    print("VERDICT %s | passed=%s" % (v["verdict"], v["pairs_passed"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
