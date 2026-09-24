"""PA1E_PREMIUM_EVENT batch (research/shortline/PA1E_PREMIUM_EVENT.md pre-reg,
frozen 2026-09-24 r64; T-16 deliverable-8 / claim MSG-20260924-1907;
order O-20260924-1155; pointer = PA1_PREMIUM_IC SS8 event-window caliber).

Event-window (episode-conditioned) study of sustained structural ETF
premium episodes on the core48 panel (r53). Zero engine runs -> strategy
engine ledger N untouched; registers no traders. PASS only shelves the
episode-conditioned reversion signal as a conversion candidate; strategy
conversion needs its own prereg + G1' v2 chain.

Frozen aligned-premium decontamination (prereg SS2):
  prem_al(t) = (1+premium_adj(t)) / (1+ret_close(t)) - 1
             = close(t-1)/NAV_asof(t) - 1
clean rows only (ex_div_flag=0, cons_flag=0, ret finite != -1). Both
inputs publish by end of day t-1 -> signal known at t-1 close; entry at
close(t) = one full day after signal availability (zero future data).

Frozen trigger (prereg SS2/SS3): H1 premium episodes -- rolling
3-consecutive-clean-day condition prem_al >= +3% (candidate day t has
3-day prefix sustention), cooldown 10 trading days between kept events
per member. H2 discount mirror (<= -3%) = report-only.

Frozen AR (SS3): AR(t,m) = fwd_ret_h(t,m) - benchmark(t), benchmark =
mean fwd over same-day members with NO primary trigger (H1 or H2), valid
cells only, floor 5 eligible; report columns reuse the same frozen
primary benchmark; nulls re-apply the full rule on shifted series
(matched design). fwd = dividend-inclusive, cons windows excluded (PA1
formula verbatim). h10 = sole gating horizon; h5/h20 report-only if the
primary passes V1.

Frozen null (SS3): K=50 circular shifts of each member's prem_al series
(offset in [60, T-60], seed 20260926+i, SEED_REGISTRY["pa1e_premium_event"]),
same trigger rule on the shifted series, AR re-scored on real returns.
V1 threshold = max(0.5% floor, p95 |null IS mean AR|).

Gates (SS4, frozen before the run, primary only):
  n-gate  IS events >= 60
  V1      IS pooled mean AR_h10 <= -max(0.005, null p95 |mean AR|)
  V2      IS t-stat <= -2.0
  V3      OOS mean AR < 0 AND |OOS| >= 0.5 x |IS|
  PASS    = n-gate AND V1 AND V2 AND V3

Outputs: research/shortline/pa1e_premium_event_results.csv
         results/shortline/pa1e_premium_event.json (+ gate_attrition row)
Usage:  python scripts/pa1e_premium_event.py selftest   (selftest only)
        python scripts/pa1e_premium_event.py           (selftest then batch)
"""
import json
import os
import subprocess
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from composite_ic import IS_END  # established methodology (company caliber)
import science_gates as sg  # cutoff_meta / append_ledger / SEED_REGISTRY

PANEL_CSV = os.path.join(ROOT, "data", "fund_premium", "panel", "panel.csv")
PANEL_SUMMARY = os.path.join(ROOT, "results", "shortline",
                             "fund_premium_panel.json")
RES_CSV = os.path.join(ROOT, "research", "shortline",
                       "pa1e_premium_event_results.csv")
OUT_JSON = os.path.join(ROOT, "results", "shortline",
                        "pa1e_premium_event.json")
ATTRITION_JSON = os.path.join(ROOT, "results", "gate_attrition.json")

H_GATE = 10
H_REPORT = [5, 20]
N_NULLS = 50
SEED0 = 20260926       # SEED_REGISTRY["pa1e_premium_event"] (prereg SS3)
TH = 0.03              # episode threshold (H1 +, H2 -)
MINLEN = 3             # consecutive clean signal days
COOLDOWN = 10          # trading days between kept events per member
SHIFT_MIN = 60         # circular-shift null offset band
V1_FLOOR = 0.005
V2_T = 2.0
V3_RETAIN = 0.5
MIN_EVENTS_IS = 60
BENCH_MIN = 5
IS_END_TS = pd.Timestamp(IS_END)
CUTOFF = "2026-09-23"  # panel evidence_cutoff (r53 build, lockbox D2)
NAV_COV_MIN = 0.95
N_EFF_BASE = 56        # 1 primary + 5 report columns + 50 nulls (SS0)
N_EFF_REPORT = 2       # +h5/h20 report columns if primary passes V1 (58)
# cross-border high-premium family (prereg SS3: members with >=10 H1
# starts in the full-sample probe; frozen pre-run, not post-hoc)
FAMILY = ["513100", "513500", "513050", "513520", "159985"]
# report-column specs: (threshold, minlen, side, label)
REPORT_SPECS = [(0.05, 3, "hi", "th5"), (0.02, 3, "hi", "th2"),
                (0.03, 5, "hi", "ml5"), (0.03, 3, "lo", "lo3")]


# ---------------------------------------------------------------- helpers
def fwd_ret_div(close, div, h):
    """Dividend-inclusive forward return (PA1 SS3 formula verbatim):
    (close[t+h] + sum_{t<d<=t+h} div_per_unit[d]) / close[t] - 1."""
    cs = np.cumsum(div, axis=0)
    out = np.full_like(close, np.nan)
    out[:-h] = (close[h:] + (cs[h:] - cs[:-h])) / close[:-h] - 1.0
    return out


def cons_in_window(cons, h):
    """True where any cons_flag=1 day falls in (t, t+h] for that member."""
    cs = np.cumsum(cons, axis=0)
    out = np.zeros(cons.shape, dtype=bool)
    out[:-h] = (cs[h:] - cs[:-h]) > 0
    return out


def prefix_runlen(hit):
    """Prefix length of consecutive True ending at each cell (0 if False).
    hit: 2D bool (T x N). Vectorized: prefix = i - last_false_index."""
    T = hit.shape[0]
    idx = np.arange(T)[:, None]
    last_false = np.maximum.accumulate(np.where(~hit, idx, -1), axis=0)
    return np.where(hit, idx - last_false, 0)


def candidates(prem_al, th, minlen, side):
    """Rolling minlen-day sustention candidates (prereg SS2): day t has
    `minlen` consecutive clean signal days ending at t. NaN breaks runs."""
    hit = (prem_al >= th) if side == "hi" else (prem_al <= -th)
    hit = np.where(np.isnan(prem_al), False, hit)
    return hit & (prefix_runlen(hit) >= minlen)


def apply_cooldown(cand, cooldown):
    """Greedy ascending keep: >=cooldown trading-day gap from the last kept
    event per member (prereg SS2)."""
    out = np.zeros_like(cand)
    for j in range(cand.shape[1]):
        last = -(10 ** 9)
        for i in np.nonzero(cand[:, j])[0]:
            if i - last >= cooldown:
                out[i, j] = True
                last = i
    return out


def aligned_premium(pan):
    """Long panel -> wide aligned premium (prereg SS2 decontamination).
    Clean rows only. Returns (prem_al, codes, cal, wide close, div, cons)."""
    pan = pan.sort_values(["code", "date"]).copy()
    pan["ret"] = pan.groupby("code")["close"].pct_change()
    clean = ((pan["ex_div_flag"] == 0) & (pan["cons_flag"] == 0)
             & pan["premium_adj"].notna() & pan["ret"].notna()
             & (pan["ret"] != -1))
    pan["prem_al"] = np.where(
        clean, (1 + pan["premium_adj"]) / (1 + pan["ret"]) - 1, np.nan)
    pan["code"] = pan["code"].astype(str)
    codes = sorted(pan["code"].unique())
    cal = pd.DatetimeIndex(np.sort(pan["date"].unique()))

    def wide(col):
        return (pan.pivot(index="date", columns="code", values=col)
                .reindex(index=cal, columns=codes).values)

    return (np.asarray(wide("prem_al"), dtype=np.float64), codes, cal,
            np.asarray(wide("close"), dtype=np.float64),
            np.nan_to_num(np.asarray(wide("div_per_unit"), dtype=np.float64)),
            np.nan_to_num(np.asarray(wide("cons_flag"), dtype=np.float64)))


def event_ar(trig_events, excl, fwd, close, cons_win):
    """Abnormal-return matrix over trigger cells (prereg SS3).
    benchmark(t) = mean fwd over same-day valid members NOT in `excl`;
    <BENCH_MIN eligible -> day dropped. Event cells also require own fwd
    validity (finite fwd, finite close, no cons in window)."""
    mask_fwd = np.isfinite(close) & np.isfinite(fwd) & ~cons_win
    elig = mask_fwd & ~excl
    n_elig = elig.sum(axis=1)
    bench = np.full(fwd.shape[0], np.nan)
    good = n_elig >= BENCH_MIN
    if good.any():
        vals = np.where(elig[good], fwd[good], np.nan)
        with np.errstate(invalid="ignore"):
            bench[good] = np.nanmean(vals, axis=1)
    ar = np.where(trig_events & mask_fwd, fwd - bench[:, None], np.nan)
    return ar, n_elig


def pooled(ar_matrix, rows_mask):
    """Finite-cell stats over selected rows: n/mean/std/t/median."""
    vals = ar_matrix[rows_mask]
    vals = vals[np.isfinite(vals)]
    if len(vals) == 0:
        return {"n": 0}
    mean = float(np.mean(vals))
    if len(vals) > 1:
        std = float(np.std(vals, ddof=1))
        t = mean / (std / np.sqrt(len(vals))) if std > 0 else float("nan")
    else:
        std, t = float("nan"), float("nan")
    return {"n": int(len(vals)), "mean": mean, "std": std, "t": t,
            "median": float(np.median(vals))}


def null_band(prem_al, close, div, cons, is_rows):
    """K=50 circular-shift nulls (prereg SS3): per member, roll the prem_al
    series by a seeded random offset in [SHIFT_MIN, T-SHIFT_MIN]; re-apply
    the full trigger rule (sustention + cooldown, both sides); AR re-scored
    on real returns with the null's own exclusion set (matched design).
    Returns list of IS pooled mean AR per null draw."""
    T, N = prem_al.shape
    means = []
    for k in range(N_NULLS):
        rng = np.random.default_rng(SEED0 + k)
        shifts = rng.integers(SHIFT_MIN, T - SHIFT_MIN, size=N)
        shifted = np.empty_like(prem_al)
        for j in range(N):
            shifted[:, j] = np.roll(prem_al[:, j], int(shifts[j]))
        trig_hi = apply_cooldown(candidates(shifted, TH, MINLEN, "hi"),
                                 COOLDOWN)
        trig_lo = apply_cooldown(candidates(shifted, TH, MINLEN, "lo"),
                                 COOLDOWN)
        fwd = fwd_ret_div(close, div, H_GATE)
        ar, _ = event_ar(trig_hi, trig_hi | trig_lo, fwd, close,
                         cons_in_window(cons, H_GATE))
        st = pooled(ar, is_rows)
        means.append(st.get("mean", float("nan")) if st.get("n") else
                     float("nan"))
        if (k + 1) % 10 == 0:
            print(f"  null {k+1}/{N_NULLS} done", flush=True)
    return means


# ---------------------------------------------------------------- selftest
def selftest():
    """Synthetic fixtures (bm-c r52 pitfall law: selftest BEFORE the batch;
    fixtures in natural serialized shapes, string codes/dates)."""
    ok_n = 0

    def ok(name, cond):
        nonlocal ok_n
        assert cond, f"SELFTEST FAIL: {name}"
        ok_n += 1
        print(f"  [ok] {name}", flush=True)

    # S1: aligned-premium reconstruction from raw serialized semantics.
    # close(t-1)="1.02", NAV(t-1)="1.00" -> true premium 2%; close(t)="1.03"
    # -> premium_adj=3%, ret=1.03/1.02-1; prem_al must equal 2% exactly.
    prem_adj = float("0.03")
    ret = 1.03 / 1.02 - 1
    pa = (1 + prem_adj) / (1 + ret) - 1
    ok("S1 reconstruction exact (= close(t-1)/NAV - 1)",
       abs(pa - (1.02 / 1.00 - 1)) < 1e-12)

    # S2: prefix run-length + rolling 3-day sustention (NaN breaks runs).
    col = np.array([np.nan, 0.01, 0.031, 0.032, 0.033, 0.01, 0.03, 0.03,
                    0.03, 0.03]).reshape(-1, 1)
    cand = candidates(col, TH, MINLEN, "hi")
    ok("S2 rolling 3-day candidates fire on the 3rd sustained day",
       bool(cand[4, 0]) and not cand[2, 0] and not cand[3, 0])
    ok("S2b NaN day breaks the run (restart fires on its 3rd day, rolling "
       "keeps firing in-run; cooldown dedups)",
       bool(cand[8, 0]) and bool(cand[9, 0]) and not cand[6, 0]
       and not cand[7, 0])

    # S3: cooldown 10 td between kept events (greedy ascending).
    c = np.zeros((30, 1), bool)
    c[[4, 9, 14, 28]] = True
    kept = apply_cooldown(c, COOLDOWN)
    ok("S3 cooldown suppresses <10td follow-ups, keeps >=10td",
       bool(kept[4, 0]) and not kept[9, 0] and bool(kept[14, 0])
       and bool(kept[28, 0]))

    # S4: AR = fwd - same-day non-trigger mean; trigger excluded from
    # benchmark; floor BENCH_MIN.
    T, N = 3, 48
    close = np.full((T, N), 10.0)
    fwd = np.full((T, N), 0.01)
    fwd[1, 0] = 0.05                      # event member +4% vs others
    trig = np.zeros((T, N), bool)
    trig[1, 0] = True
    ar, bench_n = event_ar(trig, trig, fwd, close, np.zeros((T, N), bool))
    ok("S4 AR = fwd - non-trigger benchmark mean",
       abs(ar[1, 0] - (0.05 - float(np.mean(np.delete(fwd[1], 0)))))
       < 1e-12 and bench_n[1] == N - 1)
    close2 = close.copy()
    close2[1, 5:] = np.nan               # only 5 valid members incl trigger
    ar2, _ = event_ar(trig, trig, fwd, close2, np.zeros((T, N), bool))
    ok("S4b benchmark floor (<5 eligible -> day dropped)",
       not np.isfinite(ar2[1, 0]))

    # S5: null determinism + shift band + roll preserves the multiset.
    rng = np.random.default_rng(SEED0)
    ser = rng.standard_normal((200, 3))
    rng2 = np.random.default_rng(SEED0)
    sh = rng2.integers(SHIFT_MIN, 200 - SHIFT_MIN, size=3)
    rolled = np.empty_like(ser)
    for j in range(3):
        rolled[:, j] = np.roll(ser[:, j], int(sh[j]))
    ok("S5 seeded shift deterministic & multiset-preserving",
       np.allclose(sorted(rolled[:, 0]), sorted(ser[:, 0]))
       and bool(np.all(sh >= SHIFT_MIN)) and bool(np.all(sh < 200 - SHIFT_MIN)))

    # S6: dividend-inclusive fwd + cons-window exclusion (PA1 formula).
    cl = np.array([[10.0], [11.0], [12.0]])
    dv = np.array([[0.0], [0.0], [0.5]])
    f1 = fwd_ret_div(cl, dv, 1)
    ok("S6 fwd dividend-inclusive",
       abs(f1[1, 0] - ((12.0 + 0.5) / 11.0 - 1)) < 1e-12
       and not np.isfinite(f1[2, 0]))
    cn = np.array([[0.0], [1.0], [0.0]])
    ok("S6b cons in (t, t+h] flags the signal day, not the cons day itself",
       bool(cons_in_window(cn, 1)[0, 0]) and not cons_in_window(cn, 1)[1, 0])

    print(f"selftest: {ok_n} checks PASS", flush=True)
    return ok_n


# ---------------------------------------------------------------- main
def main():
    t0 = time.time()
    if "selftest" in sys.argv:
        selftest()
        return
    selftest()  # pitfall law: selftest before every batch run
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)

    # ---- panel load + aligned premium
    pan = pd.read_csv(PANEL_CSV, parse_dates=["date"])
    prem_al, codes, cal, close, div, cons = aligned_premium(pan)
    T, N = len(cal), len(codes)
    is_rows = cal <= IS_END_TS
    oos_rows = ~is_rows
    print(f"panel: T={T} ({cal[0].date()}..{cal[-1].date()}) x N={N} "
          f"({time.time()-t0:.0f}s)", flush=True)

    # ---- data-completeness gates (prereg SS2; fail -> abort, no numbers)
    nav_cov = float(pan["nav"].notna().mean())
    pa_nan = int(pan["premium_adj"].isna().sum())
    summ = json.load(open(PANEL_SUMMARY, encoding="utf-8-sig"))
    summ_gates = summ.get("gates", {})
    g1 = nav_cov >= NAV_COV_MIN
    g2 = (summ_gates.get("verdict") == "PASS"
          and summ.get("evidence_cutoff") == CUTOFF
          and int(summ.get("members", 0)) == N)
    g3 = pa_nan == 0
    print(f"data gates: nav_cov={nav_cov:.4f} ({g1}) | summary verdict="
          f"{summ_gates.get('verdict')} cutoff={summ.get('evidence_cutoff')}"
          f" ({g2}) | premium_adj_nan={pa_nan} ({g3})", flush=True)
    if not (g1 and g2 and g3):
        print("DATA GATE FAIL - aborting batch (no numbers produced)")
        sys.exit(1)

    # ---- primary triggers + frozen benchmark (prereg SS3)
    trig_hi = apply_cooldown(candidates(prem_al, TH, MINLEN, "hi"), COOLDOWN)
    trig_lo = apply_cooldown(candidates(prem_al, TH, MINLEN, "lo"), COOLDOWN)
    primary_excl = trig_hi | trig_lo
    fwd10 = fwd_ret_div(close, div, H_GATE)
    cons10 = cons_in_window(cons, H_GATE)
    ar10, _ = event_ar(trig_hi, primary_excl, fwd10, close, cons10)

    ev_is = int((trig_hi & is_rows[:, None]).sum())
    ev_oos = int((trig_hi & oos_rows[:, None]).sum())
    ev_members = int((trig_hi.sum(axis=0) > 0).sum())
    ev_dates = int((trig_hi.sum(axis=1) > 0).sum())
    lo_is = int((trig_lo & is_rows[:, None]).sum())
    fam_mask = np.isin(np.array(codes), FAMILY)
    fam_is = int(((trig_hi & fam_mask[None, :]) & is_rows[:, None]).sum())
    print(f"events H1: IS={ev_is} OOS={ev_oos} members={ev_members} "
          f"uniq_dates={ev_dates} | H2 lo IS={lo_is} | family IS={fam_is}",
          flush=True)

    # ---- null band (K=50 circular shifts, seed 20260926+i)
    t1 = time.time()
    null_means = null_band(prem_al, close, div, cons, is_rows)
    valid = [m for m in null_means if np.isfinite(m)]
    p95_abs = float(np.quantile(np.abs(valid), 0.95)) if valid else 9.9
    v1_thr = max(V1_FLOOR, p95_abs)
    print(f"nulls: K={len(valid)} p95|meanAR|={p95_abs:.5f} "
          f"v1_thr={v1_thr:.5f} ({time.time()-t1:.0f}s)", flush=True)

    # ---- primary row + gates
    rows = []
    st_is = pooled(ar10, is_rows)
    st_oos = pooled(ar10, oos_rows)
    rec = {"spec": f"hi th={TH} minlen={MINLEN} cooldown={COOLDOWN}",
           "role": "primary", "h": H_GATE, "v1_thr": round(v1_thr, 6),
           "status": "ok"}
    for seg, st in [("is", st_is), ("oos", st_oos)]:
        for k in ("n", "mean", "std", "t", "median"):
            rec[f"{seg}_{k}"] = st.get(k, "")
    if st_is.get("n") and st_oos.get("n"):
        v_n = st_is["n"] >= MIN_EVENTS_IS
        v1 = st_is["mean"] <= -v1_thr
        v2 = (np.isfinite(st_is.get("t", np.nan))
              and st_is["t"] <= -V2_T)
        v3 = (st_oos["mean"] < 0
              and abs(st_oos["mean"]) >= V3_RETAIN * abs(st_is["mean"]))
        rec.update({"n_gate": bool(v_n), "v1": bool(v1), "v2": bool(v2),
                    "v3": bool(v3),
                    "pass": bool(v_n and v1 and v2 and v3)})
    else:
        rec.update({"n_gate": False, "v1": False, "v2": False, "v3": False,
                    "pass": False})
    primary_pass, primary_v1 = rec["pass"], bool(rec["v1"])
    print(f"  primary: IS mean AR={st_is.get('mean')} t={st_is.get('t')} "
          f"n={st_is.get('n')} | OOS mean={st_oos.get('mean')} "
          f"pass={rec['pass']}", flush=True)
    rows.append(rec)

    # ---- report columns (never gate; frozen primary benchmark reused)
    for th, ml, side, label in REPORT_SPECS:
        events = apply_cooldown(candidates(prem_al, th, ml, side), COOLDOWN)
        arx, _ = event_ar(events, primary_excl, fwd10, close, cons10)
        si, so = pooled(arx, is_rows), pooled(arx, oos_rows)
        rr = {"spec": f"{side} th={th} minlen={ml} cooldown={COOLDOWN}",
              "role": f"report:{label}", "h": H_GATE, "v1_thr": "",
              "status": "ok"}
        for seg, st in [("is", si), ("oos", so)]:
            for k in ("n", "mean", "std", "t", "median"):
                rr[f"{seg}_{k}"] = st.get(k, "")
        rr.update({"n_gate": "", "v1": "", "v2": "", "v3": "", "pass": ""})
        rows.append(rr)
        print(f"  report {label}: IS mean={si.get('mean')} n={si.get('n')}",
              flush=True)

    fam_ar = np.where(trig_hi & fam_mask[None, :], ar10, np.nan)
    fsi, fso = pooled(fam_ar, is_rows), pooled(fam_ar, oos_rows)
    rr = {"spec": f"family-only hi th={TH} minlen={MINLEN}",
          "role": "report:family", "h": H_GATE, "v1_thr": "", "status": "ok"}
    for seg, st in [("is", fsi), ("oos", fso)]:
        for k in ("n", "mean", "std", "t", "median"):
            rr[f"{seg}_{k}"] = st.get(k, "")
    rr.update({"n_gate": "", "v1": "", "v2": "", "v3": "", "pass": ""})
    rows.append(rr)
    print(f"  report family: IS mean={fsi.get('mean')} n={fsi.get('n')}",
          flush=True)

    # h5/h20 report horizons (primary V1 passer only, non-gating)
    report_done = False
    if primary_v1:
        for h in H_REPORT:
            fw = fwd_ret_div(close, div, h)
            arh, _ = event_ar(trig_hi, primary_excl, fw, close,
                              cons_in_window(cons, h))
            rows[0][f"h{h}_is_mean"] = pooled(arh, is_rows).get("mean", "")
            rows[0][f"h{h}_oos_mean"] = pooled(arh, oos_rows).get("mean", "")
        report_done = True
        print("  report horizons h5/h20 computed for primary V1 passer",
              flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(RES_CSV, index=False, encoding="utf-8")

    # ---- trials ledger (factor line; zero engine runs)
    n_cells = N_EFF_BASE + (N_EFF_REPORT if report_done else 0)
    prev = max(int(sg.ledger_head(os.path.join(ROOT, "results"))["total"]),
               int(sg.ledger_head(os.path.dirname(OUT_JSON))["total"]))
    ledger = sg.append_ledger(
        "pa1e_premium_event", n_cells,
        "results/shortline/pa1e_premium_event.json",
        evidence_cutoff=CUTOFF, prev_total=prev,
        note=("1 primary H1 episode AR@h10 + 5 report columns (same "
              "prem_al trigger lineage: th5/th2/ml5/lo3-mirror/family; "
              "report-only) + 50 circular-shift nulls (seed 20260926+i); "
              "zero engine runs, event-window statistical batch "
              "(PA1E_PREMIUM_EVENT.md frozen r64, claim MSG-20260924-1907)"))

    # ---- audit segment (in-batch compute_audit, prereg SS0)
    audit_seg = {}
    try:
        subprocess.run([sys.executable,
                        os.path.join("scripts", "compute_audit.py")],
                       cwd=ROOT, capture_output=True, text=True, timeout=120)
    except Exception as exc:  # noqa: BLE001
        print(f"[pa1e] compute_audit in-batch run failed: {exc}", flush=True)
    apath = os.path.join(ROOT, "results", "compute_audit.json")
    if os.path.exists(apath):
        with open(apath, encoding="utf-8") as fh:
            aj = json.load(fh)
        latest = aj.get("history", [{}])[-1] if aj.get("history") else aj
        audit_seg = {"source": "results/compute_audit.json (in-batch run)",
                     "verdict": latest.get("verdict"), "ts": latest.get("ts"),
                     "cpu_pct": latest.get("cpu_pct"),
                     "flags": latest.get("flags")}
    audit_seg.update({"elapsed_sec": round(time.time() - t0, 1),
                      "workers": 1,
                      "cpu_cap_policy": "vectorized single-proc "
                                        "(O-20260923-1738)"})

    out = {
        **sg.cutoff_meta(CUTOFF),
        "meta": {"batch": "PA1E_PREMIUM_EVENT (aligned-premium sustained-"
                          "episode event-window study)",
                 "pre_reg": "research/shortline/PA1E_PREMIUM_EVENT.md",
                 "order": "O-20260924-1155", "claim": "MSG-20260924-1907",
                 "task": "T-16 deliverable-8", "dept": "data+research",
                 "date": time.strftime("%Y-%m-%d %H:%M"),
                 "is_end": IS_END, "gate_horizon": H_GATE,
                 "n_nulls": N_NULLS, "seed0": SEED0,
                 "seed_registry": sg.SEED_REGISTRY.get("pa1e_premium_event"),
                 "trigger_rule": f"prem_al >= +{TH} (H1) / <= -{TH} (H2) "
                                 f"x {MINLEN} consecutive clean signal "
                                 f"days, cooldown {COOLDOWN} td (rolling "
                                 f"rule)",
                 "prem_al": "aligned premium (1+premium_adj)/(1+ret)-1 = "
                            "close(t-1)/NAV_asof(t)-1, clean rows only "
                            "(ex_div=0, cons=0); known at t-1 close "
                            "(zero future data, entry close(t) = one day "
                            "after signal)",
                 "fwd_ret": "dividend-inclusive (PA1 formula), cons "
                            "windows excluded",
                 "ar_benchmark": "fwd minus same-day mean over members "
                                 "with NO primary trigger (frozen primary "
                                 "benchmark reused by report columns; "
                                 "nulls matched-design re-apply the rule; "
                                 "floor 5 eligible)",
                 "null_design": "K=50 per-member circular shifts of "
                                "prem_al, offset [60, T-60], same trigger "
                                "rule, AR re-scored on real returns",
                 "engine_runs": 0,
                 "ledger_note": "event-window statistical batch: engine "
                                "ledger N untouched; PASS -> shelf only, "
                                "no trader registration"},
        "data_gates": {"nav_coverage": round(nav_cov, 4),
                       "nav_cov_min": NAV_COV_MIN, "g1": bool(g1),
                       "panel_summary_verdict": summ_gates.get("verdict"),
                       "panel_summary_cutoff": summ.get("evidence_cutoff"),
                       "g2": bool(g2), "premium_adj_nan": pa_nan,
                       "g3": bool(g3)},
        "event_stats": {"h1_is": ev_is, "h1_oos": ev_oos,
                        "h1_members": ev_members, "h1_uniq_dates": ev_dates,
                        "h2_is": lo_is, "family_is": fam_is,
                        "family": FAMILY},
        "thresholds": {"null_p95_abs_mean_ar": round(p95_abs, 6),
                       "v1_floor": V1_FLOOR, "v1_thr": round(v1_thr, 6),
                       "v2_t_wall": V2_T, "v3_retain": V3_RETAIN,
                       "n_gate": MIN_EVENTS_IS,
                       "null_means": [round(m, 6) if np.isfinite(m) else None
                                      for m in null_means]},
        "counts": {"report_columns": len(REPORT_SPECS) + 1,
                   "report_horizons_computed": report_done,
                   "pass": int(primary_pass)},
        "rows": rows,
        "trials_ledger": ledger,
        "audit": audit_seg,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)

    # ---- gate_attrition entry (measurement batch, s7-T)
    try:
        with open(ATTRITION_JSON, encoding="utf-8-sig") as fh:
            attr = json.load(fh)
        prim = rows[0]
        attr["entries"].append({
            "batch": "PA1E_PREMIUM_EVENT",
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "kind": "measurement",
            "cells_ledger_delta": n_cells,
            "ledger_total_after": ledger.get("total"),
            "gates": {"n_gate": bool(prim.get("n_gate")),
                      "null_is_p95_abs": round(p95_abs, 6),
                      "v1_thr": round(v1_thr, 6),
                      "primary_v1": bool(prim.get("v1")),
                      "primary_v2": bool(prim.get("v2")),
                      "primary_v3": bool(prim.get("v3")),
                      "pass": bool(primary_pass), "void": False},
            "eliminated": None,
            "refs": {"results": "results/shortline/pa1e_premium_event.json",
                     "prereg": "research/shortline/PA1E_PREMIUM_EVENT.md"},
        })
        with open(ATTRITION_JSON, "w", encoding="utf-8") as fh:
            json.dump(attr, fh, ensure_ascii=False, indent=1)
    except Exception as exc:  # noqa: BLE001
        print(f"[pa1e] gate_attrition append failed: {exc}", flush=True)

    print(f"\n=== PA1E_PREMIUM_EVENT: primary_pass={primary_pass} "
          f"cells={n_cells} ledger_total={ledger['total']} "
          f"({time.time()-t0:.0f}s) ===", flush=True)
    if primary_pass:
        print("verdict: episode-conditioned premium-reversion signal "
              "shelved (conversion = separate prereg)", flush=True)
    else:
        print("verdict: premium sub-line both calibers judged negative - "
              "honest close (P-A1 continuous r55 + PA1E event; panel data "
              "asset retained)", flush=True)


if __name__ == "__main__":
    main()
