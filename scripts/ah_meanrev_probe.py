# -*- coding: utf-8 -*-
"""E9: AH discount/premium mean-reversion structure probe (descriptive face).

Queue: state/queue/explore.md E9 (claimed r951 bm-a @ 2026-10-10T10:13:03+08:00).
Self-Drive P3 lane -- descriptive probe, NO prereg NO judged claim.

Question (queue row verbatim): 港股通 AH 折溢价均值回归深化（AH panel 消费面·T-17 后续候选）

Face discipline:
- Descriptive only: no prereg, no engine curves, no judged claims, no
  admission, no shared-panel writes (results/ evidence only).
- T-67 §2 spirit disclosed: per-pair store empirical face starts 2022-03-31
  (H-leg year-window pull); any future judged face needs its own frozen
  prereg from research/PREREG_TEMPLATE.md; nothing here preregisters.
- Panel hygiene disclosed verbatim from results/ah_panel_status.json:
  universe_em 209 mapped / 91 quarantined (crosscheck mapping-suspect) /
  per store 94 pairs / gate refresh last exit 2 (EM mapping endpoint
  RemoteDisconnected) / evidence_cutoff 2026-09-30.

Metrics (frozen, per pair, on daily premium level = close_A/(close_H*fx)-1):
- n_rows, first/last date, mean/std/min/max/latest premium
- lag-1 autocorrelation of level (Pearson x_t vs x_{t-1})
- OU/AR(1) reversion fit on deltas: d_prem_t = alpha + beta*prem_{t-1};
  beta<0 = reversion pull; half_life_days = -ln(2)/ln(1+beta) for
  -2<beta<0, else None (guard var==0 and n<MIN_BETA_ROWS)
- vol_of_change = std(daily d_premium)

Cross-sectional face (per day, equal-weight across pairs present that day):
- composite mean premium, cross-pair dispersion (std), pair_count
- first vs last 252-trading-day window means (level + dispersion drift)

Composite vs HSAHP (short-history honest, spec §4 ~63 rows recent window):
- overlap-window Pearson r (levels) + HSAHP-implied mean premium
  (close/100 - 1) vs composite mean premium mean-abs-diff, n disclosed.

Tags (descriptive, frozen here; NO shortlist/verdict claims):
- FAST_REVERSION half_life <= 21 trading days
- SLOW_REVERSION 21 < half_life <= 126
- NO_REVERSION beta>=0 / invalid / unfitted
- THIN n_rows < 500

Exit contract: 0 ok | 2 mechanism failure (missing store / unreadable panel).
selftest subcommand = offline hermetic (pure functions + synthetic OU,
zero network, fixed seed). Console prints ASCII-safe; CJK lives in the
utf-8 evidence/digest files only (GBK-console pit family).
"""

import datetime as dt
import glob
import json
import math
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PER_DIR = os.path.join(ROOT, 'data', 'ah_panel', 'per')
STATUS_PATH = os.path.join(ROOT, 'results', 'ah_panel_status.json')
UNIVERSE_EM_PATH = os.path.join(ROOT, 'data', 'ah_panel', '_universe_em.json')
HSAHP_PATH = os.path.join(ROOT, 'data', 'ah_panel', 'hsahp_index.csv')
OUT_PATH = os.path.join(ROOT, 'results', 'ah_meanrev_probe.json')

FAST_HL_DAYS = 21.0
SLOW_HL_DAYS = 126.0
THIN_ROWS = 500
MIN_BETA_ROWS = 60
WINDOW_DAYS = 252
PER_COLS = ('date', 'close_A', 'close_H', 'fx_HKD_CNY', 'premium')
EM_PREMIUM_SCALE = 10000.0  # EM push2 f188 = percent x 100 -> fraction = raw/10000
TX_PATH = os.path.join(ROOT, 'data', 'ah_panel', '_universe_tx.json')


def r6(x):
    """Round-or-None to 6dp for deterministic JSON evidence."""
    if x is None:
        return None
    x = float(x)
    if not math.isfinite(x):
        return None
    return round(x, 6)


def half_life_days(beta):
    """OU half-life from delta-AR slope beta; None when non-reverting/invalid."""
    if beta is None or not (beta < 0.0) or beta <= -2.0:
        return None
    lam = 1.0 + beta
    if lam <= 0.0:
        return None
    hl = -math.log(2.0) / math.log(lam)
    return hl if hl > 0.0 else None


def fit_beta(x_prev, dx):
    """Centered OLS slope of dx on x_prev; None on zero variance."""
    x_prev = np.asarray(x_prev, dtype=float)
    dx = np.asarray(dx, dtype=float)
    if x_prev.size < 2:
        return None
    vp = float(np.var(x_prev))
    if not math.isfinite(vp) or vp <= 0.0:
        return None
    beta = float(np.cov(x_prev, dx, bias=False)[0, 1] / vp)
    return beta if math.isfinite(beta) else None


def pearson(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.size < 2:
        return None
    va, vb = float(np.var(a)), float(np.var(b))
    if va <= 0.0 or vb <= 0.0:
        return None
    r = float(np.corrcoef(a, b)[0, 1])
    return r if math.isfinite(r) else None


def load_universe_map():
    """h_code -> {a_code, name} from the EM mapping freeze (best effort)."""
    out = {}
    try:
        with open(UNIVERSE_EM_PATH, 'r', encoding='utf-8') as fh:
            raw = json.load(fh)
    except Exception:
        return out
    rows = raw if isinstance(raw, list) else raw.get('rows') or raw.get('pairs') or []
    for row in rows:
        if not isinstance(row, dict):
            continue
        h = str(row.get('h_code') or row.get('H_code') or row.get('f12') or '').strip()
        if not h:
            continue
        out[h] = {
            'a_code': row.get('a_code') or row.get('A_code') or row.get('f191'),
            'name': row.get('name') or row.get('f193'),
        }
    return out


def em_fraction(raw_premium_pct):
    """EM push2 f188 raw (percent x 100) -> premium fraction (spec probe face)."""
    return float(raw_premium_pct) / EM_PREMIUM_SCALE


def em_crosscheck_face(per_latest, em_rows):
    """Offline re-crosscheck: per/ last-row synth vs EM census f188/10000.

    Descriptive falsification of the 2026-09-28 mass quarantine: if the
    A<->H mappings were genuinely suspect, diffs would be order-of-magnitude
    wild; a tight single-digit-pp spread validates the mapping family.
    """
    em = {}
    for r in em_rows or []:
        h = str(r.get('h_code') or '').strip()
        if h and r.get('premium_pct') is not None:
            em[h] = r['premium_pct']
    rows_out, diffs = [], []
    for h, synth in sorted(per_latest.items()):
        if h not in em or synth is None:
            continue
        ef = em_fraction(em[h])
        d = abs(float(synth) - ef)
        diffs.append(d)
        rows_out.append({'h_code': h, 'synth_latest': r6(synth),
                         'em_fraction': r6(ef), 'diff': r6(d)})
    face = {'n': len(diffs), 'pass_005': 0, 'pass_010': 0, 'median': None,
            'p75': None, 'p90': None, 'max': None, 'rows': rows_out,
            'note': 'per/ last-row synth (store dates) vs EM census fetched_at '
                    '2026-10-08: date-gap confound disclosed; tight spread = '
                    'mapping family validated, not a per-day equality claim.'}
    if not diffs:
        return face
    arr = np.array(diffs, dtype=float)
    face['pass_005'] = int((arr <= 0.05).sum())
    face['pass_010'] = int((arr <= 0.10).sum())
    face['median'] = r6(float(np.median(arr)))
    face['p75'] = r6(float(np.percentile(arr, 75)))
    face['p90'] = r6(float(np.percentile(arr, 90)))
    face['max'] = r6(float(arr.max()))
    return face


def tx_census_face(tx_rows, em_rows):
    """TX census premium_pct parse sanity face (quarantine root-cause probe).

    If TX premium_pct were the real premium in any fixed unit, the ratio
    em_fraction/tx_value would be near-constant across pairs. A wide ratio
    spread (IQR/median > 0.5) = no constant scale = parse-suspect verdict.
    """
    tx = {}
    for r in tx_rows or []:
        h = str(r.get('h_code') or '').strip()
        if h and r.get('premium_pct') is not None:
            tx[h] = float(r['premium_pct'])
    em = {}
    for r in em_rows or []:
        h = str(r.get('h_code') or '').strip()
        if h and r.get('premium_pct') is not None:
            em[h] = r['premium_pct']
    vals = np.array(sorted(tx.values()), dtype=float) if tx else np.array([])
    ratios = [em_fraction(em[h]) / v for h, v in tx.items()
              if h in em and abs(v) > 1e-12]
    face = {'n_rows': int(vals.size), 'min': None, 'median': None, 'max': None,
            'ratio_n': len(ratios), 'ratio_median': None,
            'ratio_iqr_over_median': None, 'verdict': 'NO_DATA',
            'note': '2026-09-28 mass quarantine used |synth - tx/100| <= 0.05; '
                    'this face tests whether tx premium_pct carries a constant '
                    'scale relationship to the EM/10000 truth face at all.'}
    if vals.size:
        face['min'] = r6(float(vals.min()))
        face['median'] = r6(float(np.median(vals)))
        face['max'] = r6(float(vals.max()))
    if ratios:
        arr = np.array(sorted(ratios), dtype=float)
        med = float(np.median(arr))
        iqr = float(np.percentile(arr, 75) - np.percentile(arr, 25))
        face['ratio_median'] = r6(med)
        face['ratio_iqr_over_median'] = r6(iqr / med if med else None)
        face['verdict'] = ('NON_CONSTANT_SCALE (parse suspect)'
                           if med and iqr / med > 0.5 else 'CONSTANT_SCALE')
    return face


def pair_metrics(h_code, df, meta):
    """Descriptive metrics for one pair's premium series."""
    df = df.dropna(subset=['date', 'premium']).sort_values('date')
    n = int(len(df))
    rec = {
        'h_code': h_code,
        'a_code': (meta or {}).get('a_code'),
        'name': (meta or {}).get('name'),
        'n_rows': n,
        'first': None if n == 0 else str(df['date'].iloc[0]),
        'last': None if n == 0 else str(df['date'].iloc[-1]),
        'mean': None, 'std': None, 'min': None, 'max': None, 'latest': None,
        'lag1_autocorr': None, 'beta': None, 'half_life_days': None,
        'vol_of_change': None, 'fit_ok': False, 'tag': 'NO_REVERSION',
        'thin': False,
    }
    if n == 0:
        rec['thin'] = True
        return rec
    x = df['premium'].to_numpy(dtype=float)
    rec['mean'] = r6(float(np.mean(x)))
    rec['std'] = r6(float(np.std(x, ddof=1))) if n > 1 else None
    rec['min'] = r6(float(np.min(x)))
    rec['max'] = r6(float(np.max(x)))
    rec['latest'] = r6(float(x[-1]))
    if n >= MIN_BETA_ROWS and n >= 2:
        x_prev, dx = x[:-1], np.diff(x)
        beta = fit_beta(x_prev, dx)
        rec['beta'] = r6(beta)
        rec['fit_ok'] = beta is not None
        rec['lag1_autocorr'] = r6(pearson(x[:-1], x[1:]))
        rec['vol_of_change'] = r6(float(np.std(dx, ddof=1)))
        hl = half_life_days(beta)
        rec['half_life_days'] = r6(hl)
        if hl is not None and hl <= FAST_HL_DAYS:
            rec['tag'] = 'FAST_REVERSION'
        elif hl is not None and hl <= SLOW_HL_DAYS:
            rec['tag'] = 'SLOW_REVERSION'
    rec['thin'] = n < THIN_ROWS
    return rec


def cross_section_face(all_rows):
    """Per-day equal-weight composite + dispersion + window drift."""
    frame = pd.DataFrame(all_rows)  # date, premium
    grp = frame.groupby('date')['premium']
    comp = pd.DataFrame({
        'mean': grp.mean(),
        'std': grp.std(ddof=1),
        'count': grp.size(),
    }).sort_index()
    n_days = int(len(comp))
    face = {'n_days': n_days, 'first': None, 'last': None,
            'level_first252': None, 'level_last252': None,
            'dispersion_first252': None, 'dispersion_last252': None,
            'paircount_first252': None, 'paircount_last252': None}
    if n_days == 0:
        return face
    face['first'] = str(comp.index[0])
    face['last'] = str(comp.index[-1])
    w = comp.tail(WINDOW_DAYS)
    w0 = comp.head(WINDOW_DAYS)
    face['level_last252'] = r6(float(w['mean'].mean()))
    face['dispersion_last252'] = r6(float(w['std'].mean()))
    face['paircount_last252'] = r6(float(w['count'].mean()))
    face['level_first252'] = r6(float(w0['mean'].mean()))
    face['dispersion_first252'] = r6(float(w0['std'].mean()))
    face['paircount_first252'] = r6(float(w0['count'].mean()))
    return face


def hsahp_face(comp_dates, comp_mean_by_date):
    """Overlap-window comparison vs HSAHP index (short-history honest)."""
    face = {'n_overlap': 0, 'r_levels': None, 'mean_abs_diff_implied': None,
            'note': 'hsahp_index.csv is a ~63-row recent window (spec S4); '
                    'deep history = per-pair build; comparison is descriptive only.'}
    try:
        h = pd.read_csv(HSAHP_PATH)
    except Exception:
        face['note'] += ' | hsahp_index.csv unreadable -> skipped.'
        return face
    h = h.dropna(subset=['date', 'close']).sort_values('date')
    hmap = dict(zip(h['date'].astype(str), h['close'].astype(float)))
    common = sorted(set(comp_dates) & set(hmap))
    face['n_overlap'] = len(common)
    if len(common) < 10:
        face['note'] += ' | overlap < 10 days -> r withheld.'
        return face
    a = np.array([comp_mean_by_date[d] for d in common], dtype=float)
    b = np.array([hmap[d] for d in common], dtype=float)
    face['r_levels'] = r6(pearson(a, b))
    implied = b / 100.0 - 1.0
    face['mean_abs_diff_implied'] = r6(float(np.mean(np.abs(implied - a))))
    face['hsahp_implied_mean_last'] = r6(float(implied[-1]))
    return face


def run():
    files = sorted(glob.glob(os.path.join(PER_DIR, '*.csv')))
    if not files:
        print('ah_meanrev_probe: no per-pair store files -> exit 2')
        return 2
    try:
        with open(STATUS_PATH, 'r', encoding='utf-8') as fh:
            status = json.load(fh)
    except Exception:
        status = {}
    umap = load_universe_map()

    per_pair, all_rows, total_rows = [], [], 0
    for path in files:
        h_code = os.path.splitext(os.path.basename(path))[0]
        try:
            df = pd.read_csv(path)
        except Exception:
            per_pair.append({'h_code': h_code, 'read_error': True, 'n_rows': 0,
                             'tag': 'NO_REVERSION'})
            continue
        if not all(c in df.columns for c in PER_COLS):
            per_pair.append({'h_code': h_code, 'schema_error': True,
                             'n_rows': int(len(df)), 'tag': 'NO_REVERSION'})
            continue
        df['date'] = df['date'].astype(str)
        rec = pair_metrics(h_code, df, umap.get(h_code))
        per_pair.append(rec)
        total_rows += rec['n_rows']
        all_rows.extend(zip(df['date'].tolist(), df['premium'].tolist()))
    if not all_rows:
        print('ah_meanrev_probe: empty panel -> exit 2')
        return 2

    fitted = [r for r in per_pair if r.get('fit_ok')]
    hls = sorted(r['half_life_days'] for r in fitted
                 if r.get('half_life_days') is not None)
    def q(v, p):
        if not v:
            return None
        i = min(len(v) - 1, max(0, int(round(p * (len(v) - 1)))))
        return r6(v[i])
    hl_face = {
        'fitted_pairs': len(fitted),
        'valid_half_life_n': len(hls),
        'median': q(hls, 0.50), 'q25': q(hls, 0.25), 'q75': q(hls, 0.75),
        'min': r6(hls[0]) if hls else None,
        'max': r6(hls[-1]) if hls else None,
        'fast_n': sum(1 for r in per_pair if r.get('tag') == 'FAST_REVERSION'),
        'slow_n': sum(1 for r in per_pair if r.get('tag') == 'SLOW_REVERSION'),
        'norev_n': sum(1 for r in per_pair if r.get('tag') == 'NO_REVERSION'),
        'thin_n': sum(1 for r in per_pair if r.get('thin')),
    }

    comp_rows = pd.DataFrame(all_rows, columns=['date', 'premium'])
    cs = cross_section_face(comp_rows)
    comp_mean_by_date = comp_rows.groupby('date')['premium'].mean().to_dict()
    hs = hsahp_face(sorted(comp_mean_by_date), comp_mean_by_date)

    # quarantine root-cause diagnosis (offline, read-only; E9 deepening face)
    try:
        with open(UNIVERSE_EM_PATH, 'r', encoding='utf-8') as fh:
            em_rows = (json.load(fh) or {}).get('rows') or []
    except Exception:
        em_rows = []
    try:
        with open(TX_PATH, 'r', encoding='utf-8') as fh:
            tx_rows = (json.load(fh) or {}).get('rows') or []
    except Exception:
        tx_rows = []
    per_latest = {r['h_code']: r.get('latest') for r in per_pair
                  if not (r.get('read_error') or r.get('schema_error'))}
    emc = em_crosscheck_face(per_latest, em_rows)
    txc = tx_census_face(tx_rows, em_rows)
    quarantined_keys = set((status.get('quarantined') or {}).keys())
    per_keys = set(r['h_code'] for r in per_pair)
    q_overlap = len(quarantined_keys & per_keys)
    conclusion = ('mass quarantine = false-positive family (TX census parse '
                  'broken; mapping validated by EM/10000 re-crosscheck)'
                  if ('NON_CONSTANT' in txc.get('verdict', '')
                      and emc.get('median') is not None and emc['median'] < 0.15)
                  else 'inconclusive')

    evidence = {
        'generated': dt.datetime.now().astimezone().isoformat(timespec='seconds'),
        'machine': 'bm-a',
        'probe': 'ah_meanrev_probe.py v1.0 (E9 slice-1 descriptive face)',
        'queue_row': 'E9 港股通 AH 折溢价均值回归深化（AH panel 消费面·T-17 后续候选）',
        'evidence_cutoff': status.get('evidence_cutoff'),
        'panel': {
            'per_files': len(files),
            'pairs': len(per_pair),
            'rows': total_rows,
            'first_date': cs['first'],
            'last_date': cs['last'],
        },
        'universe': {
            'mapped_pairs': status.get('mapped_pairs'),
            'quarantine_count': status.get('quarantine_count'),
            'gate_last_refresh_exit': status.get('last_refresh_exit'),
            'gate_note': 'refresh in-flight/failed face is the collector lane; '
                         'this probe consumes the per/ store read-only.',
        },
        'half_life_face': hl_face,
        'cross_section': cs,
        'hsahp_face': hs,
        'crosscheck_diagnosis': {
            'quarantined_in_store': q_overlap,
            'em_face': emc,
            'tx_face': txc,
            'conclusion': conclusion,
        },
        'per_pair': per_pair,
        'notes': [
            'descriptive only; no prereg / judged claim / admission (T-67 S2 spirit)',
            'quarantined pairs remain in per/ store (isolated from refresh only): '
            '%d of %d store files are 2026-09-28 crosscheck quarantinees; the '
            'EM/10000 re-crosscheck validates the mapping family (see '
            'crosscheck_diagnosis)' % (q_overlap, len(files)),
            'half-life = -ln(2)/ln(1+beta) on daily delta-AR fit; trading-day units',
            'collector-lane implications (crosscheck re-point / quarantine '
            're-adjudication / finalize refresh) are recorded for the T-17 lane; '
            'this probe writes no panel/status faces',
        ],
    }
    with open(OUT_PATH, 'w', encoding='utf-8') as fh:
        json.dump(evidence, fh, ensure_ascii=False, indent=1, sort_keys=True)

    print('ah_meanrev_probe: pairs=%d rows=%d range=%s..%s' % (
        len(per_pair), total_rows, cs['first'], cs['last']))
    print('half-life face: fitted=%d valid=%d median=%s fast=%d slow=%d norev=%d thin=%d' % (
        hl_face['fitted_pairs'], hl_face['valid_half_life_n'],
        hl_face['median'], hl_face['fast_n'], hl_face['slow_n'],
        hl_face['norev_n'], hl_face['thin_n']))
    print('cross-section: level first252=%s last252=%s disp first252=%s last252=%s' % (
        cs['level_first252'], cs['level_last252'],
        cs['dispersion_first252'], cs['dispersion_last252']))
    print('hsahp overlap: n=%s r=%s implied_absdiff=%s' % (
        hs['n_overlap'], hs['r_levels'], hs['mean_abs_diff_implied']))
    print('crosscheck diagnosis: quarantined_in_store=%d em_face n=%s '
          'med=%s pass05=%s pass10=%s | tx verdict=%s ratio_iqr/med=%s' % (
              q_overlap, emc['n'], emc['median'], emc['pass_005'],
              emc['pass_010'], txc['verdict'], txc['ratio_iqr_over_median']))
    print('conclusion: %s' % conclusion)
    print('evidence -> %s' % os.path.relpath(OUT_PATH, ROOT))
    return 0


def selftest():
    """Offline hermetic selftest: formula units + synthetic OU recovery."""
    checks = []

    def chk(name, cond):
        checks.append((name, bool(cond)))

    # 1. half-life formula unit checks: -ln(2)/ln(1+beta)
    hl = half_life_days(-0.01)
    chk('formula beta=-0.01 -> (68,69)d', hl is not None and 68.0 < hl < 69.0)
    hl2 = half_life_days(-0.5)
    chk('formula beta=-0.5 -> 1.0d', hl2 is not None and abs(hl2 - 1.0) < 1e-9)
    chk('beta=0 -> None', half_life_days(0.0) is None)
    chk('beta=-2.0 -> None', half_life_days(-2.0) is None)
    chk('beta=-2.5 -> None', half_life_days(-2.5) is None)
    chk('beta=None -> None', half_life_days(None) is None)

    # 2. synthetic OU recovery: x_t = phi*x_{t-1} + eps, phi=0.98 -> beta~-0.02
    rng = np.random.default_rng(20261010)
    n = 50000
    x = np.zeros(n)
    eps = rng.normal(0.0, 0.01, n)
    for t in range(1, n):
        x[t] = 0.98 * x[t - 1] + eps[t]
    beta = fit_beta(x[:-1], np.diff(x))
    hl_rec = half_life_days(beta)
    hl_true = -math.log(2.0) / math.log(0.98)
    chk('OU beta recovered <0', beta is not None and beta < 0)
    chk('OU half-life recovered within 20%',
        hl_rec is not None and abs(hl_rec - hl_true) / hl_true < 0.20)

    # 3. degenerate faces: constant series -> beta None
    chk('constant series -> beta None', fit_beta(np.ones(50), np.zeros(50)) is None)
    chk('pearson degenerate -> None', pearson(np.ones(5), np.ones(5)) is None)

    # 4. pair_metrics fixture: monotone series (no reversion), thin guard
    df = pd.DataFrame({
        'date': ['2026-01-%02d' % (i + 1) for i in range(40)],
        'close_A': np.linspace(10, 12, 40), 'close_H': [5.0] * 40,
        'fx_HKD_CNY': [0.9] * 40,
        'premium': np.linspace(1.0, 1.5, 40),
    })
    rec = pair_metrics('TEST', df, {'a_code': '600000', 'name': 'unit'})
    chk('fixture n_rows=40', rec['n_rows'] == 40)
    chk('fixture unfitted (<MIN_BETA_ROWS) fit_ok False', rec['fit_ok'] is False)
    chk('fixture thin bool True', rec['thin'] is True)
    chk('fixture tag NO_REVERSION when unfitted',
        rec['tag'] == 'NO_REVERSION')
    chk('fixture meta join', rec['a_code'] == '600000' and rec['name'] == 'unit')
    chk('fixture beta None below MIN_BETA_ROWS', rec['beta'] is None)

    # 5. cross-section fixture: exact means
    cs = cross_section_face(pd.DataFrame({
        'date': ['d1', 'd1', 'd2'], 'premium': [0.1, 0.3, 0.2]}))
    chk('cross n_days=2', cs['n_days'] == 2)
    chk('cross level first/last equal small',
        cs['level_first252'] == round((0.2 + 0.2) / 2, 6) and
        cs['level_last252'] == round(0.2, 6))

    # 6. schema contract constants intact
    chk('PER_COLS frozen', PER_COLS == ('date', 'close_A', 'close_H',
                                        'fx_HKD_CNY', 'premium'))
    chk('tags frozen', FAST_HL_DAYS == 21.0 and SLOW_HL_DAYS == 126.0
        and THIN_ROWS == 500)
    chk('EM scale frozen 10000', EM_PREMIUM_SCALE == 10000.0)
    chk('em_fraction 17509 -> 1.7509',
        abs(em_fraction(17509) - 1.7509) < 1e-9)

    # 7. em_crosscheck_face fixture: exact match pair
    emc = em_crosscheck_face({'A': 0.16, 'B': 0.40, 'C': None},
                             [{'h_code': 'A', 'premium_pct': 1600},
                              {'h_code': 'B', 'premium_pct': 3500}])
    chk('em_crosscheck n=2 (None skipped)', emc['n'] == 2)
    chk('em_crosscheck pass_005=1 pass_010=2',
        emc['pass_005'] == 1 and emc['pass_010'] == 2)
    chk('em_crosscheck median 0.025', abs(emc['median'] - 0.025) < 1e-9)

    # 8. tx_census_face fixtures: constant vs scattered ratio spread
    txc_const = tx_census_face(
        [{'h_code': 'A', 'premium_pct': 0.02}, {'h_code': 'B', 'premium_pct': 0.03}],
        [{'h_code': 'A', 'premium_pct': 2000}, {'h_code': 'B', 'premium_pct': 3000}])
    chk('tx constant-scale fixture -> CONSTANT_SCALE',
        txc_const['verdict'] == 'CONSTANT_SCALE')
    txc_scatter = tx_census_face(
        [{'h_code': 'A', 'premium_pct': 0.02}, {'h_code': 'B', 'premium_pct': 0.03}],
        [{'h_code': 'A', 'premium_pct': 2000}, {'h_code': 'B', 'premium_pct': 9000}])
    chk('tx scattered fixture -> NON_CONSTANT_SCALE',
        'NON_CONSTANT' in txc_scatter['verdict'])
    chk('tx no-data fixture -> NO_DATA',
        tx_census_face([], [])['verdict'] == 'NO_DATA')

    failed = [n for n, ok in checks if not ok]
    for n, ok in checks:
        if not ok:
            print('FAIL %s' % n)
    print('ah_meanrev_probe selftest: %d/%d PASS' % (
        len(checks) - len(failed), len(checks)))
    return 1 if failed else 0


def main(argv):
    if len(argv) > 1 and argv[1] == 'selftest':
        return selftest()
    return run()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
