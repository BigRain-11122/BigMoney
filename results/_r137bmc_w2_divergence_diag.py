"""r137 bm-c divergence diagnostic: slice-1 4 augment cells vs mirror zeroed=0.

For each slice-1 augment cell (sym, date), reconstruct the mirror's episode
(a, o, e, t) and classify WHY the mirror no-ops (one-day / exit-fill at or
after signal-off / no low-touch / entry NaN) -- disclosed observation for
owner adjudication, or a bug in the r137 fix.
"""
import json
import sys

sys.path.insert(0, "scripts")
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import trial_labor_w1 as tl1  # noqa: E402
import trial_labor_w2 as w2  # noqa: E402

grammar = json.load(open("results/trial_labor_w2/w2_grammar.json", encoding="utf-8"))
tl1.GRAMMAR = grammar
prices = tl1.load_core()
cut = pd.Timestamp("2026-09-22")
prices = {s: df[df.index <= cut] for s, df in prices.items()}
P = tl1.build_panels(prices)
close = P["close"]
atr20 = w2.atr20_series(prices)

mk = sorted(grammar["faces"].keys())[6]
mod, fn = mk.split(".")
cand = {"module": mod, "fn": fn, "sig_params": {}, "axis": [None, "none", None, "none", "p8"]}
mask = tl1._signal_frame(cand, P, grammar["faces"][mk])
mask = mask.reindex(index=close.index, columns=close.columns).fillna(0)
mask = tl1.apply_timing(mask, "none")

aug, events = w2.stop_exit_overlay(mask, prices, "p8", atr20)
cells = [(str(d), s) for s in mask.columns for d in aug.index if aug.at[d, s]]
print("slice-1 augment cells:", cells)

trig = [e for e in events if "trigger_date" in e]
print("slice-1 trigger events:", len(trig))

# mirror-side episode reconstruction for each augmented symbol
for dstr, sym in cells:
    sig = mask[sym].values
    on = (sig > 0).astype(int)
    d = np.diff(on)
    starts = ([0] if on[0] else []) + list(np.nonzero(d == 1)[0] + 1)
    ends = list(np.nonzero(d == -1)[0] + 1)
    if on[-1]:
        ends.append(len(sig))
    op = prices[sym]["open"].reindex(mask.index).values
    lo = prices[sym]["low"].reindex(mask.index).values
    day_pos = {str(mask.index[i]): i for i in range(len(mask.index))}
    tpos = day_pos.get(dstr)
    print(f"cell {sym} @ {dstr} (mirror pos {tpos}):")
    for a, o in zip(starts, ends):
        e = a + 1
        if tpos is None or not (a <= tpos < o):
            continue
        if e >= o:
            print(f"  episode [{a},{o}): one-day signal -> mirror skip (documented)")
            continue
        eo = op[e]
        if not np.isfinite(eo):
            print(f"  episode [{a},{o}): entry open NaN -> no protection (documented)")
            continue
        level = eo * (1.0 - w2.STOP_FORMULA['p8']['stop'])
        hits = np.nonzero(lo[e:o] <= level)[0]
        if len(hits) == 0:
            print(f"  episode [{a},{o}): no low<=level hit in mirror face")
        else:
            t = e + int(hits[0])
            print(f"  episode [{a},{o}): trigger t={t}, exit-fill t+1={t+1}, "
                  f"o={o} -> {'no-op (t+1>=o, documented)' if t + 1 >= o else 'WOULD ZERO'}")
