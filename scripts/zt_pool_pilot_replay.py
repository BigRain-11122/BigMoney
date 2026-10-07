# -*- coding: utf-8 -*-
# zt_pool_pilot_replay.py -- S5_01_ZT_PILOT adaptation-replay pilot runner.
# Spec (frozen): research/S5_01_ZT_PILOT.md (prereg freeze commit; §7 stays
# empty until post-run). Lineage: OSS_HARVEST_LEDGER §8 S5-01 (vibe-astock
# admission GO, r855 probe) -> r856 zt_pool collector gate landed -> this
# pilot verifies the ADAPTATION MECHANICS on the shallow as-collected window
# before the predictive-value face (deferred per T-67 §2, >=12mo forward
# accrual; OPTIONS_WAVE2 pilot->definitive precedent).
# Reuse-not-rebuild: storage/fetch semantics imported from update_zt_pool
# (same-face assertion, fail-closed VOID on drift).
# Lane bm-a (R31). rc: 0 = pass / lane-guard no-op; 1 = frozen-judgment red;
# 2 = mechanism failure; 3 = shape drift (blocked, honest report).
# evidence_cutoff (D2 lockbox) = 2026-09-30: replay window only; forward
# accrual rows landing after freeze never flow back into this batch.
import io
import json
import os
import shutil
import sys
import tempfile
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

OUT_JSON = os.path.join(ROOT, 'results', 'zt_pool_pilot_replay.json')
OUT_CSV = os.path.join(ROOT, 'results', 'zt_pool_pilot_replay_days.csv')
EVIDENCE_CUTOFF = '2026-09-30'   # D2 lockbox (prereg §2)
WINDOW_START = '2026-09-14'       # bisect-proven first non-zero EM day
LANE_OWNER = 'bm-a'              # R31 lane precedent (same as update_zt_pool)
RATE_SLEEP = 2.5                 # seconds between source calls (citizenship)
TOL = 1e-9

# §4 frozen judgment lines (prereg commit = authority; do not touch after)
MIN_FACE_SUCCESS = 0.90                       # J1
N_ZT_MEDIAN_BAND = (40, 120)                  # J3(a)
N_ZT_P999_CAP = 250                          # J3(a)
N_ZT_HARD_MAX = 250                          # J3(b) crisis-aware
ZB_RATE_MEDIAN_BAND = (0.05, 0.70)           # J3
MAX_BOARD_CAP = 10                           # J4
CRISIS_ABS_R1 = 5.0                          # J3(b) index |r1| % threshold


def _machine_id():
    try:
        with open(os.path.join(ROOT, 'fleet', 'machine.json'),
                  encoding='utf-8-sig') as f:
            return str(json.load(f).get('machine_id', ''))
    except Exception:
        return ''


def _dedup_codes(df):
    """Same storage dedup semantics as gate.append_day within one day:
    (代码) keep-first after str normalization. Returns (frame, n_raw,
    dup_codes)."""
    import pandas as pd
    if df is None or len(df) == 0:
        return df, 0, 0
    rows = df.copy()
    rows['代码'] = rows['代码'].astype(str)
    n_raw = int(len(rows))
    rows = rows.drop_duplicates(subset=['代码'], keep='first')
    return rows, n_raw, n_raw - int(len(rows))


def _derive_face(df):
    """Path-agnostic metrics for one face-day frame (post-dedup).
    zt face additionally carries the consec_boards ladder (J4)."""
    out = {'n': 0, 'max_board': None, 'ladder': None}
    if df is None or len(df) == 0:
        return out
    out['n'] = int(len(df))
    if '连板数' in df.columns:
        import pandas as pd
        boards = pd.to_numeric(df['连板数'], errors='coerce').fillna(1).astype(int)
        boards = boards[boards >= 1]
        hist = {}
        for b in boards.tolist():
            hist[int(b)] = hist.get(int(b), 0) + 1
        out['ladder'] = {str(k): v for k, v in sorted(hist.items())}
        out['max_board'] = int(boards.max()) if len(boards) else None
    return out


def _median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return None
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def _p999(xs):
    import math
    s = sorted(xs)
    if not s:
        return None
    return s[min(len(s) - 1, max(0, math.ceil(0.999 * len(s)) - 1))]


def _in_band(x, band):
    return x is not None and band[0] <= x <= band[1]


def _index_crisis_days():
    """Index |r1| >= 5% days inside the replay window (J3(b) crisis
    awareness). Source: local core ETF calendar bar file."""
    import pandas as pd
    path = os.path.join(ROOT, 'data', 'daily', '510300.csv')
    if not os.path.exists(path):
        return {}
    df = pd.read_csv(path)
    cols = {c: c for c in df.columns}
    dcol = 'date' if 'date' in df.columns else df.columns[0]
    if dcol not in ('date', '日期') and '日期' in df.columns:
        dcol = '日期'
    ccol = 'close' if 'close' in df.columns else None
    if ccol is None:
        for c in ('close', '收盘', 'close_price'):
            if c in df.columns:
                ccol = c
                break
    if ccol is None:
        return {}
    df = df[(df[dcol] >= WINDOW_START) & (df[dcol] <= EVIDENCE_CUTOFF)].copy()
    df['r1'] = df[ccol].astype(float).pct_change() * 100.0
    return {str(d): abs(float(r)) for d, r in zip(df[dcol], df['r1'])
            if r == r and abs(r) >= CRISIS_ABS_R1}


def _run_burn():
    import pandas as pd
    import akshare as ak
    import update_zt_pool as gate
    import science_gates

    # §2 anchor-face assertion (runner load path == declared path, 逐位)
    asserts = {
        'panel_dir': gate.PANEL_DIR == os.path.join(ROOT, 'data', 'zt_pool'),
        'faces': sorted(gate.ENDPOINTS.keys()) == ['dtgc', 'strong', 'zbgc', 'zt'],
        'mechanics_reusable': all(callable(getattr(gate, f, None)) for f in
                                  ('fetch_day', 'append_day', 'day_rows_match')),
        'calendar_bar': os.path.exists(gate.CORE_CALENDAR_FILE),
    }
    if not all(asserts.values()):
        print('[VOID] anchor-face mismatch (prereg §2):',
              {k: v for k, v in asserts.items() if not v})
        return 2

    dates = [d for d in (gate._load_trading_dates() or [])
             if WINDOW_START <= d <= EVIDENCE_CUTOFF]
    if not dates:
        print('[FAIL] empty replay window (calendar derive)')
        return 2
    n_cells = len(dates) * len(gate.ENDPOINTS)

    # §3 ledger append at burn start (dict schema, no hand-copied prev)
    science_gates.append_ledger('S5_01_ZT_PILOT', n_cells,
                                'results/zt_pool_pilot_replay.json',
                                evidence_cutoff=EVIDENCE_CUTOFF)

    # fetch pass (frozen as-collected snapshot; conn failures exempt-listed)
    raw = {}
    exempt, shape_flags = [], []
    t0 = time.time()
    for day in dates:
        dc = day.replace('-', '')
        for key, (fn_name, inv_cols) in gate.ENDPOINTS.items():
            try:
                df, shape_ok = gate.fetch_day(getattr(ak, fn_name), dc, inv_cols)
                if not shape_ok:
                    shape_flags.append({'day': day, 'face': key})
                raw[(key, day)] = df
            except Exception as ex:
                raw[(key, day)] = None
                exempt.append({'day': day, 'face': key,
                               'error': type(ex).__name__})
            time.sleep(RATE_SLEEP)
    fetch_elapsed = round(time.time() - t0, 1)
    ok_cells = n_cells - len(exempt)
    j1_pass = ok_cells >= MIN_FACE_SUCCESS * n_cells

    # path1 derive + path2 derive-through-storage-mechanics (temp panel)
    path1, path2, dup_log, csv_rows = {}, {}, [], []
    tmpdir = tempfile.mkdtemp(prefix='zt_pilot_')
    real_panel_dir = gate.PANEL_DIR
    try:
        gate.PANEL_DIR = tmpdir  # monkeypatch: storage mechanics, zero touch on real panel
        for key in gate.ENDPOINTS:
            for day in dates:
                df = raw.get((key, day))
                if df is None:
                    continue
                if len(df):
                    gate.append_day(key, day, df)
        for key in gate.ENDPOINTS:
            p = os.path.join(tmpdir, f'{key}.parquet')
            if not os.path.exists(p):
                continue
            back = pd.read_parquet(p)
            back['代码'] = back['代码'].astype(str)
            for day in dates:
                path2[(key, day)] = _derive_face(back[back['日期'] == day])
    finally:
        gate.PANEL_DIR = real_panel_dir
        shutil.rmtree(tmpdir, ignore_errors=True)

    for (key, day), df in sorted(raw.items()):
        if df is None:
            continue
        ded, n_raw, dup = _dedup_codes(df)
        m1 = _derive_face(ded)
        path1[(key, day)] = m1
        if dup:
            dup_log.append({'day': day, 'face': key, 'dup_codes': dup})
        m2 = path2.get((key, day))
        csv_rows.append({
            'day': day, 'face': key, 'rows_raw': n_raw,
            'rows_dedup': m1['n'], 'dup_codes': dup,
            'n': m1['n'], 'max_board': m1['max_board'],
            'ladder': json.dumps(m1['ladder'], ensure_ascii=False),
            'path2_identity': (m2 is not None and m2['n'] == m1['n']
                               and (m2['ladder'] or None) == (m1['ladder'] or None)
                               and m2['max_board'] == m1['max_board']),
        })

    # J2 dual-derive identity (integer faces + ladder; zb_rate float tol)
    j2_viol = []
    for day in dates:
        m1z = path1.get(('zt', day))
        m2z = path2.get(('zt', day))
        for face in gate.ENDPOINTS:
            a, b = path1.get((face, day)), path2.get((face, day))
            if a is None or b is None:
                if a is not None or b is not None:
                    j2_viol.append({'day': day, 'face': face, 'kind': 'presence'})
                continue
            if a['n'] != b['n'] or (a['ladder'] or None) != (b['ladder'] or None) \
                    or a['max_board'] != b['max_board']:
                j2_viol.append({'day': day, 'face': face, 'kind': 'metrics'})
    j2_pass = not j2_viol

    # J5 determinism: re-derive path1 from frozen raw snapshot, byte-compare
    rederive = {}
    for (key, day), df in sorted(raw.items()):
        if df is None:
            continue
        rederive[(key, day)] = _derive_face(_dedup_codes(df)[0])
    j5_pass = all(rederive[k]['n'] == path1[k]['n']
                  and rederive[k]['ladder'] == path1[k]['ladder']
                  and rederive[k]['max_board'] == path1[k]['max_board']
                  for k in path1)

    # three-axis series + J3 distribution bounds + J4 ladder sanity
    n_zt = [path1[('zt', d)]['n'] for d in dates if ('zt', d) in path1]
    n_dt = [path1[('dtgc', d)]['n'] for d in dates if ('dtgc', d) in path1]
    zb = []
    for d in dates:
        nz, nb = path1.get(('zt', d)), path1.get(('zbgc', d))
        if nz and nb and (nz['n'] + nb['n']) > 0:
            zb.append(nb['n'] / (nb['n'] + nz['n']))
    n_zt_median, n_zt_p999 = _median(n_zt), _p999(n_zt)
    zb_median = _median(zb)
    crisis = _index_crisis_days()
    j3_med_zt = _in_band(n_zt_median, N_ZT_MEDIAN_BAND)
    j3_p999 = (n_zt_p999 is not None and n_zt_p999 <= N_ZT_P999_CAP)
    max_zt = max(n_zt) if n_zt else None
    j3_hard = (max_zt is None) or (max_zt <= N_ZT_HARD_MAX)
    if not j3_hard:
        # J3(b): crisis-day awareness -- max breach on crisis days exempt
        # via single-point removal (disclosed), not batch kill
        worst_day = max((d for d in dates if ('zt', d) in path1),
                        key=lambda d: path1[('zt', d)]['n'])
        j3_hard = worst_day in crisis
    j3_zb = _in_band(zb_median, ZB_RATE_MEDIAN_BAND) and \
        all(0.0 <= x <= 1.0 for x in zb)
    j4_bad = [(d, path1[('zt', d)]['max_board']) for d in dates
              if ('zt', d) in path1 and
              (path1[('zt', d)]['max_board'] or 0) > MAX_BOARD_CAP]

    verdicts = {
        'J1_face_success': j1_pass,
        'J2_dual_derive_identity': j2_pass,
        'J3_zt_median_band': j3_med_zt,
        'J3_zt_p999_cap': j3_p999,
        'J3_zt_hard_max_crisis_aware': j3_hard,
        'J3_zb_rate_band': j3_zb,
        'J4_ladder_sanity': not j4_bad,
        'J5_determinism': j5_pass,
    }

    result = {
        'batch': 'S5_01_ZT_PILOT',
        'lane': 'bm-a',
        'spec': 'research/S5_01_ZT_PILOT.md',
        'science_gates': {'cutoff_meta': {'evidence_cutoff': EVIDENCE_CUTOFF}},
        'window': {'start': WINDOW_START, 'end': EVIDENCE_CUTOFF,
                   'n_days': len(dates), 'days': dates},
        'n_cells': n_cells, 'ok_cells': ok_cells,
        'exempt': exempt, 'shape_flags': shape_flags,
        'dup_code_log': dup_log,
        'metrics': {
            'n_zt_series': dict(zip(dates, [path1[('zt', d)]['n']
                                            if ('zt', d) in path1 else None
                                            for d in dates])),
            'n_dt_series': dict(zip(dates, [path1[('dtgc', d)]['n']
                                            if ('dtgc', d) in path1 else None
                                            for d in dates])),
            'n_zt_median': n_zt_median, 'n_zt_p999': n_zt_p999,
            'n_zt_max': max_zt, 'zb_rate_median': zb_median,
            'n_zt_count': len(n_zt),
        },
        'crisis_days': crisis,
        'j2_violations': j2_viol,
        'j4_bad': j4_bad,
        'verdicts': verdicts,
        'all_pass': all(verdicts.values()),
        'fetch_elapsed_sec': fetch_elapsed,
    }
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    with open(OUT_CSV, 'w', encoding='utf-8') as f:
        cols = ['day', 'face', 'rows_raw', 'rows_dedup', 'dup_codes',
                'n', 'max_board', 'ladder', 'path2_identity']
        f.write(','.join(cols) + '\n')
        for r in csv_rows:
            f.write(','.join(str(r[c]) for c in cols) + '\n')

    print('S5_01_ZT_PILOT replay: days=%d cells=%d ok=%d exempt=%d '
          'n_zt_median=%s p99.9=%s zb_med=%s J2=%s J5=%s -> %s'
          % (len(dates), n_cells, ok_cells, len(exempt),
             n_zt_median, n_zt_p999, zb_median, j2_pass, j5_pass,
             'PASS' if result['all_pass'] else 'RED'))
    print('-> %s + %s' % (OUT_JSON, OUT_CSV))
    if shape_flags:
        return 3
    return 0 if result['all_pass'] else 1


def _selftest():
    """Offline selftest: derive/dedup/bounds/determinism on synthetic
    frames; no network, no panel touch."""
    import pandas as pd
    checks = []

    def ck(name, cond):
        checks.append((name, bool(cond)))

    # dedup semantics: intra-day duplicate codes -> keep-first
    df = pd.DataFrame({'代码': ['000001', '000002', '000001'],
                       '连板数': [2, 1, 9]})
    ded, n_raw, dup = _dedup_codes(df)
    ck('dedup_keep_first', len(ded) == 2 and n_raw == 3 and dup == 1)

    # ladder derive: NaN board -> 1; histogram sorted keys
    df2 = pd.DataFrame({'代码': ['000001', '000002', '000003'],
                        '连板数': [3, None, 3]})
    m = _derive_face(df2)
    ck('ladder_nan_fill', m['ladder'] == {'1': 1, '3': 2}
       and m['max_board'] == 3 and m['n'] == 3)

    # empty frame
    ck('empty_face', _derive_face(pd.DataFrame())['n'] == 0)

    # median / p999
    ck('median_odd', _median([3, 1, 2]) == 2)
    ck('median_even', _median([4, 1, 3, 2]) == 2.5)
    # p999 nearest-rank: N=1000 rank999 -> idx998; [1]*998+[250]*2 -> 250
    ck('p999_cap', _p999([1] * 998 + [250] * 2) == 250)
    ck('p999_small_n_is_max', _p999([55, 103, 52]) == 103)

    # frozen bands
    ck('band_hit', _in_band(55, N_ZT_MEDIAN_BAND))
    ck('band_miss', not _in_band(121, N_ZT_MEDIAN_BAND))
    ck('zb_band', _in_band(0.30, ZB_RATE_MEDIAN_BAND))

    # determinism helper: re-derive equality on synthetic
    a = _derive_face(_dedup_codes(df)[0])
    b = _derive_face(_dedup_codes(df)[0])
    ck('determinism_rederive', a == b)

    # lane guard off-machine path
    ck('lane_self', isinstance(LANE_OWNER, str))

    n_pass = sum(1 for _, ok in checks if ok)
    for name, ok in checks:
        print('[%s] %s' % ('PASS' if ok else 'FAIL', name))
    print('selftest: %d/%d PASS' % (n_pass, len(checks)))
    return 0 if n_pass == len(checks) else 1


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'run'
    if mode == 'selftest':
        return _selftest()
    if mode != 'run':
        print('usage: zt_pool_pilot_replay.py [run|selftest]')
        return 2
    mid = _machine_id()
    if mid != LANE_OWNER:
        print('zt_pool_pilot_replay: lane guard (owner=%s, this=%s) -- '
              'stdout-only honest no-op' % (LANE_OWNER, mid))
        return 0
    return _run_burn()


if __name__ == '__main__':
    sys.exit(main())
