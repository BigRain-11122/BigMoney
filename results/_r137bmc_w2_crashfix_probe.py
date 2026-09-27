"""r137 bm-c real-data probe: post-fix regression through the crash point.

Verifies _effective_signal_mask + stop_exit_overlay on the REAL core48
panel (short-history member 511090 present) with stop!=none axes -- the
exact face that crashed (IndexError 1083 vs 797, per-symbol raw .values
positional overflow). Hermetic-safe: read-only, no products written.
"""
import json
import sys

sys.path.insert(0, "scripts")
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
assert "511090" in close.columns, "short-history member absent from panel"

mk = sorted(grammar["faces"].keys())[6]
mod, fn = mk.split(".")
cand = {"module": mod, "fn": fn, "sig_params": {}, "axis": [None, "none", None, "none", "p8"]}
mask = tl1._signal_frame(cand, P, grammar["faces"][mk])
mask = mask.reindex(index=close.index, columns=close.columns).fillna(0)
mask = tl1.apply_timing(mask, "none")
on_before = int((mask.values > 0).sum())

for stop in ("p8", "a20"):
    cand["axis"][4] = stop
    S = w2._effective_signal_mask(mask, prices, stop, atr20)
    zapped = on_before - int((S.values > 0).sum())
    print(f"stop={stop}: mirror OK | mask on={on_before} | overlay zeroed {zapped}")

aug, events = w2.stop_exit_overlay(mask, prices, "p8", atr20)
print(f"slice-1 overlay OK | augment cells={int(aug.values.sum())} events={len(events)}")
print("PROBE PASS: both faces clear the crash point on real short-history panel")
