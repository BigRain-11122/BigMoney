# -*- coding: utf-8 -*-
"""r2113 probe: can the adopted carry book be split into per-arm daily contributions?"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import idx_fut_carry_ladder_risk as L  # noqa: E402

lat = json.load(open(os.path.join(ROOT, "results", "policy_return_lattice.json"), encoding="utf-8"))
nav = float(lat["nav_cny"])
k = float(lat["inputs"]["k"])
print("nav", nav, "k", k, "cash_rate", lat["inputs"]["cash_rate_pct"])

legs = {p: L.spread_leg(p) for p in ("IC", "IM")}
sleeve = L.equity_sleeve()
print("sleeve", sleeve.get("_refused"), sleeve["span"], len(sleeve["daily"]))

n_lot = L.per_lot_notional(lat)
print("n_lot", n_lot)

eng = [r for r in lat["lattice"] if int(r["ic_lots"]) == 1 and int(r["im_lots"]) == 1][0]
print("engine rung keys sample:", {kk: eng[kk] for kk in ("ic_lots", "im_lots", "notional_cny",
                                                          "cash_cny", "cash_interest_cny",
                                                          "expected_total_cny", "l1_cny",
                                                          "carry_cny", "expected_return_pct")})

d_ic = dict(zip(legs["IC"]["dates"], legs["IC"]["spread"]))
d_im = dict(zip(legs["IM"]["dates"], legs["IM"]["spread"]))
d_eq = dict(zip(sleeve["dates"], sleeve["daily"]))
common = [d for d in sorted(d_eq) if d in d_ic and d in d_im]
print("common days", len(common), common[0], common[-1])

w_ic = 1.0 * n_lot["IC"] / nav
w_im = 1.0 * n_lot["IM"] / nav
print("w_ic %.6f w_im %.6f k %.6f" % (w_ic, w_im, k))

c_eq = [k * d_eq[d] for d in common]
c_ic = [w_ic * d_ic[d] for d in common]
c_im = [w_im * d_im[d] for d in common]
tot = [a + b + c for a, b, c in zip(c_eq, c_ic, c_im)]


def mean(x):
    return sum(x) / len(x)


def ann(x):
    lvl = 1.0
    for r in x:
        lvl *= 1.0 + r
    return (lvl ** (252.0 / len(x)) - 1.0) * 100.0


def vol(x):
    m = mean(x)
    var = sum((v - m) ** 2 for v in x) / (len(x) - 1)
    return (var ** 0.5) * (252 ** 0.5) * 100.0


for name, s in (("equity", c_eq), ("IC", c_ic), ("IM", c_im), ("total", tot)):
    print("%-7s ann_arith %7.3f  ann_comp %7.3f  vol %7.3f  mean_bp %6.3f"
          % (name, mean(s) * 252 * 100, ann(s), vol(s), mean(s) * 1e4))

mt = mean(tot)
cov = {n: sum((a - mean(s)) * (b - mt) for a, b in zip(s, tot)) / (len(tot) - 1)
       for n, s in (("equity", c_eq), ("IC", c_ic), ("IM", c_im))}
vt = sum(cov.values())
print("var_total(ppm^2?)", vt, "sum risk shares", sum(v / vt for v in cov.values()))
print("risk shares", {n: round(v / vt, 4) for n, v in cov.items()})

# cash arm
cash = eng["cash_cny"] / nav * float(lat["inputs"]["cash_rate_pct"]) / 100.0
print("cash arm ann %% of nav: %.4f  (annual cny %.0f)" % (cash * 100, cash * nav))

# carry vs equity arm beta
carry = [b + c for b, c in zip(c_ic, c_im)]
me = mean(c_eq)
mc = mean(carry)
beta = (sum((a - me) * (b - mc) for a, b in zip(c_eq, carry)) / len(c_eq)
        / (sum((a - me) ** 2 for a in c_eq) / len(c_eq)))
print("carry beta to equity arm %.5f ; carry ann_arith %.3f ; corr %.4f"
      % (beta, mc * 252 * 100, (sum((a - me) * (b - mc) for a, b in zip(c_eq, carry)) / len(c_eq))
         / ((sum((a - me) ** 2 for a in c_eq) / len(c_eq)) ** 0.5
            * (sum((b - mc) ** 2 for b in carry) / len(carry)) ** 0.5)))
