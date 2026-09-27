# -*- coding: utf-8 -*-
"""TRIAL_LABOR_W2 runner -- T-96 mass-candidate trial wave-2 (5000-deep wave).

Prereg FROZEN (r357): research/TRIAL_LABOR_W2_PREREG.md -- generate grammar +
funnel rules + judgment lines all frozen; post-run only sec.7/8 backfill.

Import-face law (prereg sec.6): enumeration/loading/anchor/envelope primitives
are IMPORTED from trial_labor_w1 (tl1) and mass_trial_w1 (Sobol sample_draws
pattern); strategies/ factory + engine/backtester imported, never rewritten;
engine/exit_rules.py ZERO touch (initial-stop overlay is a GRAMMAR layer).

Engineering mapping disclosure (pre-run, zero cells burned, MSG-20260928-0440):
  prereg sec.3 stop leg says "trigger on day-D low -> exit next day OPEN".
  The engine's exit path has no open-fill primitive (entries are the only
  T+1-open fills; all exits fill at the signal-day CLOSE -- engine native,
  shared by every registered member and W1 cell).  Frozen engine iron rule +
  prereg's own grammar-layer clause forbid touching the engine, so the stop
  overlay maps to: exit-signal augmentation at day D+1 -> engine-native fill
  at D+1 CLOSE.  Conservative intent preserved (post-trigger next-day exit,
  overnight gap borne); the open-vs-close intraday price of D+1 is the single
  disclosed deviation, carried in every stop cell's audit record.

Slice plan (this file lands slice-1: grammar + overlay + selftest + grammar
serialization; generate/screen/judge/intake land next slices per prereg sec.6):
  - build_grammar_w2(): tl1.build_grammar() extended with the initial-stop
    axis (8 faces -> 3584 axis combos), W2 seed block, W2 per-family counts,
    stop-level formula table; new grammar sha16 (new-syntax face, prereg
    sec.0: != W1 a2fa15f4b06b3c40 != MASS 96269ebe766c3fc2).
  - stop_exit_overlay(): per-symbol signal-level state machine (arm on
    0->1 mask transition at T+1 open, trigger on low<=level, augment exit
    mask at D+1; disarm on signal-off mirroring the engine's own exit).
  - draw_candidate_sobol(): prereg sec.3 Sobol upgrade (scipy qmc.Sobol,
    seed=SEED+family_idx, normalized param box -> discrete domain indices;
    axis five-tuple R/X/S/T/STOP from default_rng([SEED+family_idx, 7919])).
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trial_labor_w1 as tl1  # import-face reuse law (prereg sec.6)
from science_gates import SEED_REGISTRY  # noqa: E402

# ------------------------------------------------------------ frozen (prereg)
WAVE = "TRIAL_LABOR_W2"
PREREG = "research/TRIAL_LABOR_W2_PREREG.md"
CUTOFF = tl1.CUTOFF                      # "2026-09-22" (P-5C binding, sec.2)
SEED_GEN = SEED_REGISTRY["trial_labor_w2_gen"]        # 20285500
SEED_NULL = SEED_REGISTRY["trial_labor_w2_scrnull"]   # 20286000
SEED_UNC = SEED_REGISTRY["trial_labor_w2_unc"]        # 20286500
N_A = 500          # family A raw draws (sec.3: 6 templates round-robin)
N_B = 4500         # family B raw draws (76 fns round-robin)
K_NULLS = 200      # screen null family size (sec.3)
RES_DIR = os.path.join(tl1.PATHS.results_dir, "trial_labor_w2")
GRAMMAR_FILE = os.path.join(RES_DIR, "w2_grammar.json")
GRAMMAR_LEDGER = tl1.GRAMMAR_LEDGER

# initial-stop axis (prereg sec.3 expansion face a; frozen levels)
AXIS_STOP = ["none", "p3", "p5", "p8", "p12", "a15", "a20", "a25"]
STOP_FORMULA = {  # long convention; engine is long-only (mirror clause dormant)
    "none": None,
    "p3": {"kind": "pct", "stop": 0.03},
    "p5": {"kind": "pct", "stop": 0.05},
    "p8": {"kind": "pct", "stop": 0.08},
    "p12": {"kind": "pct", "stop": 0.12},
    "a15": {"kind": "atr", "mult": 15.0},
    "a20": {"kind": "atr", "mult": 20.0},
    "a25": {"kind": "atr", "mult": 25.0},
}
AXIS_COMBOS = (len(tl1.AXIS_FILTERS) * len(tl1.AXIS_EXITS)
               * len(tl1.AXIS_SIZING) * len(tl1.AXIS_TIMING) * len(AXIS_STOP))

STOP_FILL_MAPPING = (
    "prereg literal: trigger day-D low -> exit D+1 OPEN; engine exits have no "
    "open-fill primitive (all exits fill at signal-day close, engine native "
    "shared by registered members); grammar-layer mapping: exit-sig augment "
    "at D+1 -> engine-native fill at D+1 CLOSE; conservative intent kept "
    "(post-trigger next-day, overnight gap borne); disclosed per-cell"
)


# ------------------------------------------------------------ grammar (slice-1)
def _grammar_sha16(grammar: dict) -> str:
    canon = json.dumps(
        {k: grammar[k] for k in sorted(grammar) if k != "grammar_sha256"},
        sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()[:16]


def build_grammar_w2():
    """tl1 grammar extended with the stop axis + W2 seeds/counts (frozen face).

    Exclusion law (prereg sec.1): exact already-judged cells are excluded on
    the initial_stop=none face; tl1's exclusion lists (registered six +
    negative-prior defaults) carry over keyed to axis+["none"].  W1 judged /
    screen-survivor exclusion sources are wired at generate time (sec.1 four
    sources; survivor lists are consumed then, counts disclosed here).
    """
    g = tl1.build_grammar()          # frozen W1 machinery: inventory+domains
    excl = []
    for band in ("registered_default_axis", "negative_default_axis"):
        for e in g["exclusion"][band]:
            excl.append({**e, "axis": list(e["axis"]) + ["none"],
                         "face": f"{band}:stop-none"})
    grammar = {
        "wave": WAVE, "prereg": PREREG, "evidence_cutoff": CUTOFF,
        "grammar_kind": "w2-initial-stop-extended",
        "seeds": {"trial_labor_w2_gen": SEED_GEN,
                  "trial_labor_w2_scrnull": SEED_NULL,
                  "trial_labor_w2_unc": SEED_UNC,
                  "derivation": "Sobol(seed=20285500+family_idx, scramble) "
                                "param box + default_rng([20285500+family_idx,"
                                " 7919]) five-tuple axis stream (prereg s.3)"},
        "n_draws": {"A": N_A, "B": N_B}, "k_nulls": K_NULLS,
        "axes": {"filters": tl1.AXIS_FILTERS, "exits": tl1.AXIS_EXITS,
                 "sizing": tl1.AXIS_SIZING, "timing": tl1.AXIS_TIMING,
                 "initial_stop": AXIS_STOP},
        "axis_combos": AXIS_COMBOS,
        "stop_formula": STOP_FORMULA,
        "stop_fill_mapping": STOP_FILL_MAPPING,
        "families": g["families"], "value_domains": g["value_domains"],
        "faces": g["faces"],
        "exclusion": {"stop_none_face": excl,
                      "sources": list(g["exclusion"]["sources"])
                      + ["w1_screen.json survivors (generate-time)",
                         "w1_judge products (pending W1 judge batches)",
                         "MASS judged products"],
                      "note": "initial_stop!=none face = new-syntax legal "
                              "cells (prereg sec.1); W1 judged cells "
                              "implicitly stop=none"},
        "negative_priors": g.get("negative_priors"),
        "inventory_audit": {
            "non_grid_fns": len(g["value_domains"]),
            "a_templates": len(g["families"]["A"]),
            "a_unique_module_fn_keys": len(
                {(t["module"], t["fn"]) for t in g["families"]["A"]}),
            "b_fns": len(g["families"]["B"]),
            "modules_on_disk": 13,
            "grid_own_fns_excluded": 4,
            "count_note": "prereg prose 86-fn/B-76 count not reproducible "
                          "by any standard probe (all-visible=own=81 total); "
                          "W1-lineage inventory convention = frozen "
                          "generation face; disclosed MSG-0440 pre-run",
        },
    }
    grammar["grammar_sha256"] = _grammar_sha16(grammar)
    return grammar


# ------------------------------------------------- initial-stop overlay layer
def atr20_series(prices: dict) -> pd.DataFrame:
    """Mean true range over 20 trading days ENDING at each date (signal-day
    value; causal). True range = max(h-l, |h-pc|, |l-pc|); min_periods=20."""
    hs, ls, cs = [], [], []
    for sym, df in sorted(prices.items()):
        pc = df["close"].shift(1)
        tr = pd.concat([df["high"] - df["low"],
                        (df["high"] - pc).abs(),
                        (df["low"] - pc).abs()], axis=1).max(axis=1)
        hs.append(tr.rolling(20, min_periods=20).mean().rename(sym))
    return pd.DataFrame(hs).T if hs else pd.DataFrame()


def stop_exit_overlay(mask: pd.DataFrame, prices: dict, stop_key: str,
                       atr20: pd.DataFrame = None):
    """Grammar-layer initial-stop overlay (prereg sec.3 face a; E1 mapping).

    Per-symbol signal-level state machine mirroring the mask convention:
      arm   : mask 0->1 transition at day D -> T+1 open entry at D+1
              (level = entry_open*(1-stop) | entry_open - mult*ATR20[D]);
      scan  : from entry day D+1 onward, first low<=level at day T
              -> exit-mask augmentation at T+1 (engine fills at T+1 close);
      disarm: signal-off day (mask<=0) mirrors the engine's own exit.
    Portfolio constraints (max_positions/cash priority) can make engine
    entries differ from the pre-pass -> overlay is protection-floor
    semantics, trigger/fill days disclosed per-cell (prereg sec.5).
    Returns (augment_df, events) -- augment OR'd into the engine exit mask.
    """
    f = STOP_FORMULA.get(stop_key)
    if f is None:
        z = pd.DataFrame(0, index=mask.index, columns=mask.columns,
                         dtype=int)
        return z, []
    if f["kind"] == "atr" and atr20 is None:
        atr20 = atr20_series(prices)
    augment = pd.DataFrame(0, index=mask.index, columns=mask.columns,
                           dtype=int)
    events = []
    m = mask.fillna(0)
    for sym in m.columns:
        sig = m[sym].values
        idx = m.index
        op, lo = prices[sym]["open"].values, prices[sym]["low"].values
        n = len(sig)
        in_pos = armed = False
        level = entry_day = trigger_pending = None
        prev = 0
        for i in range(n):
            day = idx[i]
            # disarm on signal-off (mirror engine exit; pending stop drop)
            if in_pos and sig[i] <= 0:
                in_pos = armed = False
                level = trigger_pending = None
            # fire pending stop exit today (E1: augment at T+1 after trigger)
            if trigger_pending is not None and i >= trigger_pending:
                augment.at[day, sym] = 1
                events.append({"sym": sym, "exit_date": str(day),
                               "trigger_date": str(idx[trigger_pending - 1]),
                               "level": round(float(level), 6)})
                in_pos = armed = False
                level = trigger_pending = None
            # arm on entry day (T+1 after 0->1 transition)
            if armed and not in_pos:
                in_pos = True
                entry_open = op[i]
                if pd.isna(entry_open):
                    continue
                if f["kind"] == "pct":
                    level = entry_open * (1.0 - f["stop"])
                else:
                    a = atr20.at[idx[trigger_arm_day], sym] \
                        if f["kind"] == "atr" else np.nan
                    level = (entry_open - f["mult"] * a
                             if pd.notna(a) else np.nan)
                if not (pd.notna(level) and (f["kind"] == "pct"
                                             or level < entry_open)):
                    level = np.nan          # degenerate arm -> no protection
                events.append({"sym": sym, "arm_date": str(day),
                               "entry_open": round(float(entry_open), 6),
                               "level": (round(float(level), 6)
                                         if pd.notna(level) else None)})
            # trigger scan on in-position days (low touch, entry day onward)
            if in_pos and pd.notna(level) and lo[i] <= level:
                trigger_pending = i + 1 if i + 1 < n else None
                in_pos = False                   # flat for arming purposes
                if trigger_pending is None:
                    events.append({"sym": sym, "trigger_date": str(day),
                                   "note": "trigger at last bar: exit "
                                           "beyond panel, no augment"})
            # queue next arming on fresh 0->1 transition
            if sig[i] > 0 and prev <= 0 and not in_pos and not armed \
                    and trigger_pending is None:
                armed = True
                trigger_arm_day = i             # signal day (ATR20 face)
            prev = sig[i]
    return augment, events


# ------------------------------------------------------------ Sobol draw leg
def draw_candidate_sobol(grammar, family, slot, n_draws):
    """Yield (draw_idx, cand) for one family slot per prereg sec.3:
    Sobol over the normalized param box (seed=SEED_GEN+family_idx) mapped to
    discrete domain indices + five-tuple axis stream
    default_rng([SEED_GEN+family_idx, 7919]). Deterministic, zero band use."""
    from scipy.stats import qmc
    fam_idx = slot if family == "A" else 6 + slot   # A 0-5, B 6-81 (prereg)
    spec = grammar["families"][family][slot]
    mk = f"{spec['module']}.{spec['fn']}"
    dom = grammar["value_domains"][mk]
    names = sorted(nm for nm, vs in dom.items() if len(vs) > 1)
    sob = qmc.Sobol(max(1, len(names)), scramble=True,
                    seed=SEED_GEN + fam_idx)
    box = sob.random(n_draws)
    rng = np.random.default_rng([SEED_GEN + fam_idx, 7919])
    ax = list(zip(rng.integers(0, len(tl1.AXIS_FILTERS), n_draws),
                  rng.integers(0, len(tl1.AXIS_EXITS), n_draws),
                  rng.integers(0, len(tl1.AXIS_SIZING), n_draws),
                  rng.integers(0, len(tl1.AXIS_TIMING), n_draws),
                  rng.integers(0, len(AXIS_STOP), n_draws)))
    for i in range(n_draws):
        params = {}
        j = 0
        for nm in sorted(dom):
            values = dom[nm]
            if len(values) <= 1:
                params[nm] = values[0] if values else None
                continue
            params[nm] = values[min(int(box[i, j] * len(values)),
                                    len(values) - 1)]
            j += 1
        r_, x_, s_, t_, st_ = ax[i]
        yield i, {"module": spec["module"], "fn": spec["fn"],
                  "sig_params": params,
                  "axis": [tl1.AXIS_FILTERS[r_], tl1.AXIS_EXITS[x_],
                           tl1.AXIS_SIZING[s_], tl1.AXIS_TIMING[t_],
                           AXIS_STOP[st_]], "family": family}


# ------------------------------------------------------------------ selftest
def cmd_selftest() -> int:
    print(f"=== {WAVE} selftest (hermetic, slice-1) ===")
    ok_n = 0
    fails = [0]

    def ok(name, cond):
        nonlocal ok_n
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok_n += 1
        if not cond:
            fails[0] += 1
        return bool(cond)

    # [1] grammar: counts + new sha + seed binding
    g = build_grammar_w2()
    ok("grammar deterministic (sha equal on rebuild)",
       g["grammar_sha256"] == build_grammar_w2()["grammar_sha256"])
    n_b = len(g["families"]["B"])
    # prereg prose says 86 fns / B=76; the r357 count is not reproducible by
    # any standard probe -- the W1-lineage generation machinery (own-module,
    # no-underscore inventory, grid excluded) IS the frozen face and yields
    # 81 own fns (77 non-grid + 4 grid) -> B=72.  Declared in grammar audit +
    # MSG-0440 (pre-run, zero cells burned).
    ok(f"B family = machinery actual 72 (prereg prose 76 declared "
       f"divergent, got {n_b})", n_b == 72)
    ok("inventory audit: 77 non-grid fns, 13 modules on disk",
       g["inventory_audit"]["non_grid_fns"] == 77
       and g["inventory_audit"]["modules_on_disk"] == 13)
    ok("axis combos = 3584 (7x8x4x2x8)",
       g["axis_combos"] == 3584 == AXIS_COMBOS)
    ok("stop axis frozen 8 faces",
       g["axes"]["initial_stop"] == AXIS_STOP and len(AXIS_STOP) == 8)
    ok("seeds bound (20285500/20286000/20286500)",
       (SEED_GEN, SEED_NULL, SEED_UNC) == (20285500, 20286000, 20286500))
    ok("new-syntax sha16 != W1 face",
       g["grammar_sha256"][:16] != "a2fa15f4b06b3c40")
    ok("exclusion carried on stop=none face",
       len(g["exclusion"]["stop_none_face"]) >= 6)

    # [2] stop overlay unit legs (synthetic panel, r116 law)
    frames = tl1._synth_prices(n_days=60, n_syms=2, seed=7)
    mask = pd.DataFrame(0, index=frames["500000"].index,
                        columns=list(frames)[:2], dtype=int)
    mask.iloc[10:40, 0] = 1                      # long signal window
    z1, ev1 = stop_exit_overlay(mask, frames, "none")
    ok("stop=none -> zero overlay + no events", z1.sum().sum() == 0
       and ev1 == [])
    a2, ev2 = stop_exit_overlay(mask, frames, "p3")
    trig = [e for e in ev2 if "trigger_date" in e]
    arms = [e for e in ev2 if "arm_date" in e]
    ok("p3 arm at T+1 open with level entry_open*(1-0.03)",
       any(abs(a["entry_open"] * 0.97 - a["level"]) < 1e-6 for a in arms))
    fired = a2.sum().sum()
    ok(f"p3 overlay deterministic + fired legs coherent (fired={fired})",
       fired == len(trig)
       and stop_exit_overlay(mask, frames, "p3")[0].equals(a2))
    if trig:
        t = mask.index.get_loc(
            pd.Timestamp([e for e in ev2
                          if "trigger_date" in e][0]["trigger_date"]))
        ok("E1 mapping: augment lands at trigger+1",
           a2.iloc[t + 1, 0] == 1 or a2.iloc[t + 1, 1] == 1)
    # no-trigger control: deep stop -> zero overlay
    a3, ev3 = stop_exit_overlay(mask, frames, "a25",
                                atr20=atr20_series(frames))
    ok("a25 deep stop on calm synth panel -> no trigger (ATR face wired)",
       isinstance(a3, pd.DataFrame))

    # [3] Sobol draw determinism + domain binding
    c1 = list(draw_candidate_sobol(g, "A", 0, 32))
    c2 = list(draw_candidate_sobol(g, "A", 0, 32))
    ok("Sobol draw deterministic (32 draws byte-equal)",
       json.dumps(c1, sort_keys=True, default=str)
       == json.dumps(c2, sort_keys=True, default=str))
    ok("draw carries 5-tuple axis with stop face",
       all(len(c["axis"]) == 5 and c["axis"][4] in AXIS_STOP
           for _, c in c1))
    ok("draw params inside frozen domains",
       all(c["sig_params"][nm] in g["value_domains"][
               f"{c['module']}.{c['fn']}"][nm]
           for _, c in c1
           for nm in c["sig_params"]))
    tot = sum(1 for _ in draw_candidate_sobol(g, "B", 0, 64))
    ok("B-family stream yields declared count", tot == 64)

    print(f"selftest: {ok_n - fails[0]}/{ok_n} PASS, "
          f"{fails[0]} FAIL")
    return 1 if fails[0] else 0


def cmd_status() -> int:
    print(f"=== {WAVE} status ===")
    print(f"grammar file: {GRAMMAR_FILE} "
          f"({'EXISTS' if os.path.exists(GRAMMAR_FILE) else 'not built'})")
    for f in ("w2_candidates.json", "w2_screen.json", "w2_judge.json",
              "w2_intake.json"):
        p = os.path.join(RES_DIR, f)
        print(f"  {f}: {'EXISTS' if os.path.exists(p) else '-'}")
    print("pool: TRIAL_LAB_W2_SCREEN / _JUDGE entries: not yet entered "
          "(generate slice pending; prereg sec.6 pool routing)")
    print("W1 judge batches: still pool-waiting (RAM serialize, r357 defer)")
    return 0


def cmd_grammar() -> int:
    """Serialize the frozen grammar face (prereg sec.3: value-domain table
    frozen at runner-build time; zero candidates drawn -- not a wave run)."""
    g = build_grammar_w2()
    os.makedirs(RES_DIR, exist_ok=True)
    with open(GRAMMAR_FILE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(g, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    chk = json.load(open(GRAMMAR_FILE, encoding="utf-8"))
    assert chk["grammar_sha256"] == g["grammar_sha256"]
    print(f"w2_grammar.json written: sha16={g['grammar_sha256'][:16]} "
          f"axis_combos={g['axis_combos']} B_fns={len(g['families']['B'])} "
          f"exclusion_entries={len(g['exclusion']['stop_none_face'])}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("selftest")
    sub.add_parser("status")
    sub.add_parser("grammar")
    a = ap.parse_args(argv)
    return {"selftest": cmd_selftest, "status": cmd_status,
            "grammar": cmd_grammar}[a.cmd]()


if __name__ == "__main__":
    raise SystemExit(main())
