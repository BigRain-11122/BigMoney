# -*- coding: utf-8 -*-
"""T-2026-10-03-154 dividend events face export (div_events -> dividend_events.parquet).

Lane: bm-c machine-local data/fund_history (R31/R65 data lane).
Precedent: T-149 value_faces (5c3939640) + T-152 quality_faces (r399, PASS 7/7).
Consumer: FUND-DIVLOWVOL-P1 prereg seat (T-145 leg(c) third family, O-20261002-2115
sec.1-1 item-3: dividend-low-vol = A-share classic defensive per CEO
research-orientation law). TTM yield derive happens consumer-side with the
price-holding machine's raw prices (MONEY02 bars + factor.json sidecar per
T-145 next_slice); this face ships the PIT-safe event stream.

PIT anchoring (disclosure, mandatory per fund_pit_audit financial_face_rule
family): corporate-action CASH events anchor at the EX-DIVIDEND DATE
(除权除息日) -- the date the market price adjusts and the distribution is
executed. This is NOT a report-period face; the statutory Q1->04-30/H1->08-31
/Q3->10-31/FY->next-04-30 gate does not apply. A trailing-12M window keyed by
ex_date is lookahead-free by construction: only events already gone ex at
decision time t (ex_date <= t) enter the window; announced-but-future-ex rows
(progress=实施 with ex_date > t) are automatically excluded.

Export rules (fail-closed, bm-c side -- parquet written ONLY on all-pass):
  (1) INCLUDED rows = progress==实施 AND valid ex_date. EXCLUDED + DISCLOSED:
      rows with null ex_date (不分配 no-distribution declarations + 预案
      proposals without ex-date) and rows with ex-date but progress!=实施
      (announced pending -- never anchored). Zero silent drops.
  (2) n_symbols_exported >= 5100;
  (3) multi-component distributions sharing one ex-date (e.g. 600519
      2006-05-19 "10转10派3" recorded as two component rows) AGGREGATED by
      (code, ex_date): cash/send/transfer summed, announce_date = earliest.
      Sum-preservation asserted exact (see gates) -- zero information loss;
  (4) n_rows_exported >= 54000; events with ex_date in 2026 >= 3000;
  (5) ex_date coverage min <= 1991-12-31 and max >= 2026-09-01;
  (6) zero duplicate (code, ex_date) in output (machine re-check);
  (7) per_share_cash band [0, 50] CNY/share; out-of-band = fail-closed;
  (8) announce_date sentinel (year < 1900) -> null, count disclosed;
  (9) known-answer aggregation legs: the 3 measured multi-component events.

Columns EXACT: [code, ex_date, announce_date, per_share_cash, send_per_10,
               transfer_per_10, progress]
  code/ex_date/announce_date: string (ISO YYYY-MM-DD; announce_date null-able)
  per_share_cash: float64  == sum(派息)/10  (sina field is per-10-shares CNY)
  send_per_10 / transfer_per_10: float64 (per-10-share ratios, metadata)
  progress: string (constant 实施 in this face; kept for schema stability)
"""
import json
import os
import sys
import time

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
SRC = os.path.join(REPO, 'data', 'fund_history')
OUT = os.path.join(REPO, 'data', 'fund_history_export', 'dividend_events.parquet')
RECEIPT = os.path.join(REPO, 'results', 't154_dividend_events_export.json')
LOG = os.path.join(REPO, 'results', '_r403bmc_t154_log.txt')

K_ANN = u'\u516c\u544a\u65e5\u671f'          # 公告日期
K_SEND = u'\u9001\u80a1'                      # 送股
K_CONV = u'\u8f6c\u589e'                      # 转增
K_CASH = u'\u6d3e\u606f'                      # 派息 (per 10 shares, CNY)
K_PROG = u'\u8fdb\u5ea6'                      # 进度
K_EX = u'\u9664\u6743\u9664\u606f\u65e5'      # 除权除息日
IMPL = u'\u5b9e\u65bd'                        # 实施

GATE = {
    'n_symbols_min': 5100,
    'n_rows_min': 54000,
    'events_2026_min': 3000,
    'ex_min_ceiling': '1991-12-31',
    'ex_max_floor': '2026-09-01',
    'cash_per_share_max': 50.0,
}

# known-answer legs: the 3 measured multi-component events (code, ex_date)
# -> (per_share_cash, send_per_10, transfer_per_10)
KNOWN = {
    ('600519', '2006-05-19'): (0.30, 0.0, 10.0),   # 10转10派3 -> cash 3.0/10, conv 10
    ('000402', '2006-04-05'): (0.20, 0.0, 4.0),    # 转增4 + 派息2.0
    ('000501', '1996-08-14'): (0.05, 1.5, 0.0),    # 派息0.5 + 送股1.5
}


def log(msg):
    with open(LOG, 'a', encoding='utf-8') as fh:
        fh.write(msg + '\n')
        fh.flush()


def date_str(v):
    """'2026-09-17T00:00:00.000' / '1996-08-13T...' / None / 'None' -> ISO date or None."""
    if v is None:
        return None
    s = str(v).strip()
    if not s or s.lower() == 'none' or s.lower() == 'nan':
        return None
    d = s[:10]
    if len(d) == 10 and d[4] == '-' and d[7] == '-':
        return d
    return None


def num(v):
    if v is None:
        return 0.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main():
    t0 = time.time()
    log('=== r403 bm-c T-154 dividend events face export start %s ==='
        % time.strftime('%Y-%m-%d %H:%M:%S'))

    syms = sorted(os.listdir(SRC))
    n_dirs = len(syms)
    excl_null_ex = 0
    excl_nonimpl_ex = 0
    parse_errors = 0
    ann_sentinel = 0
    agg_events = 0            # multi-component (code, ex_date) aggregates
    ann_missing = 0
    cash_total_in = 0.0
    send_total_in = 0.0
    conv_total_in = 0.0
    events_2026 = 0
    per_sym_counts = {}
    rows = {}                 # (code, ex_date) -> dict

    for sym in syms:
        p = os.path.join(SRC, sym, 'div_events.json')
        if not os.path.exists(p):
            continue
        with open(p, 'r', encoding='utf-8') as fh:
            try:
                j = json.load(fh)
            except ValueError:
                parse_errors += 1
                continue
        src_rows = j.get('rows') or []
        if not src_rows:
            continue
        sym_n = 0
        for row in src_rows:
            ex = date_str(row.get(K_EX))
            prog = str(row.get(K_PROG) or '').strip()
            if ex is None:
                excl_null_ex += 1
                continue
            if prog != IMPL:
                excl_nonimpl_ex += 1
                continue
            c = num(row.get(K_CASH))
            s = num(row.get(K_SEND))
            v = num(row.get(K_CONV))
            if c is None or s is None or v is None:
                parse_errors += 1
                continue
            ann = date_str(row.get(K_ANN))
            if ann is not None and ann[:4] < '1900':
                ann_sentinel += 1
                ann = None
            if ann is None:
                ann_missing += 1
            key = (sym, ex)
            cur = rows.get(key)
            if cur is None:
                rows[key] = {'cash': c, 'send': s, 'conv': v, 'ann': ann}
            else:
                agg_events += 1
                cur['cash'] += c
                cur['send'] += s
                cur['conv'] += v
                if ann is not None and (cur['ann'] is None or ann < cur['ann']):
                    cur['ann'] = ann
            cash_total_in += c
            send_total_in += s
            conv_total_in += v
            sym_n += 1
            if ex[:4] == '2026':
                events_2026 += 1
        if sym_n:
            per_sym_counts[sym] = sym_n

    n_syms = len(per_sym_counts)
    n_rows = len(rows)
    log('scanned %d symbol dirs; exported syms=%d rows(aggregated)=%d '
        'agg_events=%d excl_null_ex=%d excl_nonimpl_ex=%d parse_errors=%d '
        'ann_sentinel=%d ann_missing=%d'
        % (n_dirs, n_syms, n_rows, agg_events, excl_null_ex, excl_nonimpl_ex,
           parse_errors, ann_sentinel, ann_missing))

    # ---- build dataframe
    import pandas as pd
    keys = sorted(rows.keys())
    ex_dates = [k[1] for k in keys]
    recs = [(k[0], k[1], rows[k]['ann'], rows[k]['cash'] / 10.0,
             rows[k]['send'], rows[k]['conv'], IMPL) for k in keys]
    df = pd.DataFrame(recs, columns=['code', 'ex_date', 'announce_date',
                                     'per_share_cash', 'send_per_10',
                                     'transfer_per_10', 'progress'])
    cash_total_out = float(df['per_share_cash'].sum()) * 10.0
    send_total_out = float(df['send_per_10'].sum())
    conv_total_out = float(df['transfer_per_10'].sum())

    # ---- gates (fail-closed)
    fails = []

    def gate(name, ok, detail=''):
        log('gate %-28s %s %s' % (name, 'PASS' if ok else 'RED', detail))
        if not ok:
            fails.append(name)

    gate('G1_n_symbols', n_syms >= GATE['n_symbols_min'],
         'n=%d floor=%d' % (n_syms, GATE['n_symbols_min']))
    gate('G2_n_rows', n_rows >= GATE['n_rows_min'],
         'n=%d floor=%d' % (n_rows, GATE['n_rows_min']))
    gate('G3_events_2026', events_2026 >= GATE['events_2026_min'],
         'n=%d floor=%d' % (events_2026, GATE['events_2026_min']))
    gate('G4_coverage', (min(ex_dates) <= GATE['ex_min_ceiling']
                         and max(ex_dates) >= GATE['ex_max_floor']),
         'min=%s max=%s' % (min(ex_dates), max(ex_dates)))
    gate('G5_no_dup_keys', len(set(keys)) == len(keys),
         'unique=%d rows=%d' % (len(set(keys)), len(keys)))
    gate('G6_sum_preserve_cash',
         abs(cash_total_in - cash_total_out) < 1e-6,
         'in=%.6f out=%.6f' % (cash_total_in, cash_total_out))
    gate('G6b_sum_preserve_send',
         abs(send_total_in - send_total_out) < 1e-6,
         'in=%.6f out=%.6f' % (send_total_in, send_total_out))
    gate('G6c_sum_preserve_conv',
         abs(conv_total_in - conv_total_out) < 1e-6,
         'in=%.6f out=%.6f' % (conv_total_in, conv_total_out))
    bad_band = df[(df['per_share_cash'] < 0)
                  | (df['per_share_cash'] > GATE['cash_per_share_max'])]
    gate('G7_cash_band', len(bad_band) == 0,
         'violations=%d band=[0, %.1f]' % (len(bad_band), GATE['cash_per_share_max']))
    mono_ok = True
    last_code, last_ex = None, None
    for code, ex in keys:
        if code == last_code and ex <= last_ex:
            mono_ok = False
            break
        last_code, last_ex = code, ex
    gate('G8_ex_mono_ascending', mono_ok)
    # known-answer aggregation legs
    ka_fail = 0
    for (code, ex), (cash, send, conv) in KNOWN.items():
        m = df[(df['code'] == code) & (df['ex_date'] == ex)]
        if len(m) != 1:
            ka_fail += 1
            log('known-answer %s %s: row-count=%d RED' % (code, ex, len(m)))
            continue
        r = m.iloc[0]
        ok = (abs(float(r['per_share_cash']) - cash) < 1e-9
              and abs(float(r['send_per_10']) - send) < 1e-9
              and abs(float(r['transfer_per_10']) - conv) < 1e-9)
        log('known-answer %s %s: cash=%s send=%s conv=%s %s'
            % (code, ex, r['per_share_cash'], r['send_per_10'],
               r['transfer_per_10'], 'PASS' if ok else 'RED'))
        if not ok:
            ka_fail += 1
    gate('G9_known_answers', ka_fail == 0, 'legs=%d fail=%d' % (len(KNOWN), ka_fail))

    import statistics
    cnts = sorted(per_sym_counts.values())
    stats = {
        'per_sym_events_median': statistics.median(cnts) if cnts else 0,
        'per_sym_events_p10': cnts[max(0, len(cnts) // 10)] if cnts else 0,
        'per_sym_events_max': cnts[-1] if cnts else 0,
    }
    receipt = {
        'ticket': 'T-2026-10-03-154',
        'face': 'dividend_events',
        'direction': 'bm-c -> fleet (git 方案 A, direct self-delivering parquet)',
        'consumer': 'FUND-DIVLOWVOL-P1 prereg seat (T-145 leg(c) third family, seat OPEN)',
        'data_cutoff': 'T-131 fetch 2026-10-02 15:40 (div_events face, sina source)',
        'pit_anchor': 'ex_date (除权除息日); TTM window by ex_date is lookahead-free; '
                      'financial-face statutory gate N/A for corporate actions (disclosed)',
        'n_symbol_dirs_scanned': n_dirs,
        'n_symbols_exported': n_syms,
        'n_rows_exported': n_rows,
        'aggregated_multicomponent_events': agg_events,
        'excluded_null_ex_date': excl_null_ex,
        'excluded_nonimpl_with_ex': excl_nonimpl_ex,
        'parse_errors': parse_errors,
        'announce_sentinel_1900_to_null': ann_sentinel,
        'announce_missing_null': ann_missing,
        'events_ex_2026': events_2026,
        'ex_date_min': min(ex_dates),
        'ex_date_max': max(ex_dates),
        'per_symbol_stats': stats,
        'gates': GATE,
        'known_answers': ['600519 2006-05-19', '000402 2006-04-05',
                          '000501 1996-08-14'],
        'elapsed_sec': round(time.time() - t0, 1),
    }
    log('gates: %d/%d PASS, fails=%s'
        % (9 - len(fails), 9, fails or 'none'))

    if fails:
        receipt['verdict'] = 'RED'
        receipt['failed_gates'] = fails
        with open(RECEIPT, 'w', encoding='utf-8') as fh:
            json.dump(receipt, fh, ensure_ascii=True, indent=1)
        log('VERDICT RED -- parquet NOT written (fail-closed). receipt=%s'
            % RECEIPT)
        print('VERDICT RED fails=%s -- parquet NOT written' % fails)
        return 2

    # ---- write parquet (all-pass only)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    df.to_parquet(OUT, index=False)
    # read-back verification
    chk = pd.read_parquet(OUT)
    rb_ok = (list(chk.columns) == list(df.columns)
             and len(chk) == len(df)
             and str(chk['per_share_cash'].dtype) == 'float64'
             and abs(float(chk['per_share_cash'].sum())
                     - float(df['per_share_cash'].sum())) < 1e-9)
    if not rb_ok:
        receipt['verdict'] = 'RED'
        receipt['failed_gates'] = ['G10_readback']
        with open(RECEIPT, 'w', encoding='utf-8') as fh:
            json.dump(receipt, fh, ensure_ascii=True, indent=1)
        log('VERDICT RED readback mismatch -- parquet REMOVED')
        os.remove(OUT)
        print('VERDICT RED readback mismatch')
        return 2

    import hashlib
    with open(OUT, 'rb') as fh:
        sha = hashlib.sha256(fh.read()).hexdigest()
    receipt['verdict'] = 'PASS'
    receipt['parquet'] = OUT
    receipt['parquet_bytes'] = os.path.getsize(OUT)
    receipt['parquet_sha256'] = sha
    receipt['gates_passed'] = '10/10 (G1-G9 + G10 readback)'
    with open(RECEIPT, 'w', encoding='utf-8') as fh:
        json.dump(receipt, fh, ensure_ascii=True, indent=1)
    log('VERDICT PASS 10/10 -- parquet %d bytes sha256=%s (%.1fs)'
        % (receipt['parquet_bytes'], sha, time.time() - t0))
    print('VERDICT PASS 10/10 rows=%d syms=%d bytes=%d sha256=%s'
          % (n_rows, n_syms, receipt['parquet_bytes'], sha))
    return 0


if __name__ == '__main__':
    sys.exit(main())
