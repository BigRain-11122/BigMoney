# -*- coding: utf-8 -*-
"""T-2026-10-03-154 div_events faces export v2 -- PER TICKET SPEC (bm-b r609 origin-first ticket, executed by bm-c data holder per T-152 lane precedent).

Supersedes the v1 7-column exploration (results/_r403bmc_t154_export.py +
dividend_events.parquet, kept as working papers only -- NOT the deliverable).
v2 conforms EXACTLY to the origin ticket spec:

  Deliverable: data/fund_history_export/div_events_faces.parquet
  Columns EXACT: [code, ex_date, cash_div_per_10, record_date]
    code=str; ex_date/record_date=date (parquet date32); cash_div_per_10=float64
    ex_date = 除权除息日 normalized ISO date (PIT anchor for TTM windows)
    cash_div_per_10 = 派息 as float (per-10-share cash, NOT divided)
    record_date = 股权登记日 normalized ISO date (missing -> NaT, disclosed)
  Row filter (fail-closed, honest exclusion counts):
    (1) ONLY 进度 == 实施 exported; non-implemented excluded + disclosed;
    (2) missing/unparseable ex_date OR null/missing 派息 excluded + disclosed;
    (3) exact-duplicate (code, ex_date, cash_div_per_10, record_date) rows
        dropped + count disclosed (multi-component same-ex-date rows with
        DIFFERENT cash values are NOT dups -- preserved, consumer TTM-sums);
    (4) 5 quarantined symbols absent per T-131 status -- disclosed.
  Gates: n_symbols_nonempty >= 5100; per-symbol event count median >= 3;
    global ex_date d0/d1 disclosed, d1 >= 2026-01-01; zero null cash;
    zero unsorted (sorted by code then ex_date ascending); dtype contract.
  Receipt: results/t154_div_events_faces_export.json
"""
import json
import os
import sys
import time

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
SRC = os.path.join(REPO, 'data', 'fund_history')
OUT = os.path.join(REPO, 'data', 'fund_history_export', 'div_events_faces.parquet')
RECEIPT = os.path.join(REPO, 'results', 't154_div_events_faces_export.json')
LOG = os.path.join(REPO, 'results', '_r403bmc_t154_log.txt')

K_ANN = u'\u516c\u544a\u65e5\u671f'          # 公告日期 (disclosure only)
K_SEND = u'\u9001\u80a1'
K_CONV = u'\u8f6c\u589e'
K_CASH = u'\u6d3e\u606f'                      # 派息 per 10 shares CNY
K_PROG = u'\u8fdb\u5ea6'
K_EX = u'\u9664\u6743\u9664\u606f\u65e5'      # 除权除息日
K_REC = u'\u80a1\u6743\u767b\u8bb0\u65e5'     # 股权登记日
IMPL = u'\u5b9e\u65bd'

QUARANTINED = ['001235', '001381', '301569', '301660', '301718']


def log(msg):
    with open(LOG, 'a', encoding='utf-8') as fh:
        fh.write(msg + '\n')
        fh.flush()


def date_str(v):
    if v is None:
        return None
    s = str(v).strip()
    if not s or s.lower() in ('none', 'nan'):
        return None
    d = s[:10]
    if len(d) == 10 and d[4] == '-' and d[7] == '-':
        return d
    return None


def to_date(ds):
    import datetime
    if ds is None:
        return None
    y, m, d = ds.split('-')
    return datetime.date(int(y), int(m), int(d))


def main():
    import datetime
    t0 = time.time()
    log('=== r403 bm-c T-154 v2 div_events_faces export start %s ==='
        % time.strftime('%Y-%m-%d %H:%M:%S'))

    syms = sorted(os.listdir(SRC))
    n_dirs = len(syms)
    excl_nonimpl = 0
    excl_null_ex = 0
    excl_null_cash = 0
    parse_err = 0
    dup_exact = 0
    rec_missing = 0
    seen = set()
    recs = []
    per_sym = {}

    for sym in syms:
        p = os.path.join(SRC, sym, 'div_events.json')
        if not os.path.exists(p):
            continue
        try:
            with open(p, 'r', encoding='utf-8') as fh:
                j = json.load(fh)
        except ValueError:
            parse_err += 1
            continue
        rows = j.get('rows') or []
        for row in rows:
            ex = date_str(row.get(K_EX))
            if ex is None:
                excl_null_ex += 1
                continue
            if str(row.get(K_PROG) or '').strip() != IMPL:
                excl_nonimpl += 1
                continue
            raw_cash = row.get(K_CASH)
            if raw_cash is None or str(raw_cash).strip().lower() in ('none', 'nan', ''):
                excl_null_cash += 1
                continue
            try:
                cash = float(raw_cash)
            except (TypeError, ValueError):
                excl_null_cash += 1
                continue
            rec = date_str(row.get(K_REC))
            if rec is None:
                rec_missing += 1
            key = (sym, ex, cash, rec)
            if key in seen:
                dup_exact += 1
                continue
            seen.add(key)
            recs.append((sym, ex, cash, rec))
            per_sym[sym] = per_sym.get(sym, 0) + 1

    import pandas as pd
    recs.sort(key=lambda r: (r[0], r[1]))
    # force object dtype so datetime.date objects survive to parquet date32
    # (DataFrame constructor would otherwise coerce to datetime64[ns])
    df = pd.DataFrame({
        'code': [r[0] for r in recs],
        'cash_div_per_10': [float(r[2]) for r in recs],
    })
    df['ex_date'] = pd.Series([to_date(r[1]) for r in recs], dtype=object)
    df['record_date'] = pd.Series([to_date(r[3]) for r in recs], dtype=object)
    df = df[['code', 'ex_date', 'cash_div_per_10', 'record_date']]
    n_syms = len(per_sym)
    n_rows = len(df)
    d0 = df['ex_date'].min().isoformat()
    d1 = df['ex_date'].max().isoformat()
    cnts = sorted(per_sym.values())
    import statistics
    med = statistics.median(cnts) if cnts else 0
    log('scanned %d dirs; exported syms=%d rows=%d excl(nonimpl=%d nullex=%d '
        'nullcash=%d parse=%d) exact_dups=%d rec_missing=%d span %s..%s'
        % (n_dirs, n_syms, n_rows, excl_nonimpl, excl_null_ex, excl_null_cash,
           parse_err, dup_exact, rec_missing, d0, d1))

    fails = []

    def gate(name, ok, detail=''):
        log('gate %-24s %s %s' % (name, 'PASS' if ok else 'RED', detail))
        if not ok:
            fails.append(name)

    gate('G1_n_symbols', n_syms >= 5100, 'n=%d' % n_syms)
    gate('G2_median_events', med >= 3, 'median=%s' % med)
    gate('G3_d1_recent', d1 >= '2026-01-01', 'd1=%s' % d1)
    gate('G4_zero_null_cash', int(df['cash_div_per_10'].isna().sum()) == 0)
    gate('G5_sorted',
         all((c1, e1) <= (c2, e2)
             for (c1, e1), (c2, e2) in zip(
                 zip(df['code'], df['ex_date']),
                 list(zip(df['code'], df['ex_date']))[1:])),
         'spec: sorted by code then ex_date ascending (per-code reset)')
    gate('G6_dtype_contract',
         str(df['code'].dtype) in ('object', 'str')  # pandas 3.x str dtype
         and str(df['cash_div_per_10'].dtype) == 'float64'
         and df['ex_date'].map(lambda x: isinstance(x, datetime.date)).all()
         and df['record_date'].map(
             lambda x: x is None or isinstance(x, datetime.date)).all())
    gate('G7_columns', list(df.columns) == ['code', 'ex_date',
                                            'cash_div_per_10', 'record_date'])
    gate('G8_quarantine_absent',
         all(q not in per_sym for q in QUARANTINED))
    # component-preservation known-answer: 600519 2006-05-19 = TWO rows
    # (10转10 cash 0.0 + 派3 cash 3.0) under exact-dup policy
    m = df[(df['code'] == '600519') & (df['ex_date'] == to_date('2006-05-19'))]
    cash_sum = float(m['cash_div_per_10'].sum())
    gate('G9_component_preserved', len(m) == 2 and abs(cash_sum - 3.0) < 1e-9,
         'rows=%d cash_sum=%s (10转10派3 two-component case)' % (len(m), cash_sum))

    receipt = {
        'ticket': 'T-2026-10-03-154',
        'ticket_version': 'origin-first bm-b r609 spec, executed by bm-c r403',
        'face': 'div_events',
        'deliverable': OUT,
        'columns': ['code', 'ex_date', 'cash_div_per_10', 'record_date'],
        'dtype_contract': {'code': 'str', 'ex_date': 'date',
                           'cash_div_per_10': 'float64', 'record_date': 'date'},
        'n_symbols_nonempty': n_syms,
        'n_rows': n_rows,
        'ex_date_span': [d0, d1],
        'per_symbol_event_median': med,
        'excluded': {
            'non_implemented': excl_nonimpl,
            'null_or_unparseable_ex_date': excl_null_ex,
            'null_or_missing_cash': excl_null_cash,
            'source_file_parse_errors': parse_err,
            'exact_duplicates_dropped': dup_exact,
            'record_date_missing_nat': rec_missing,
        },
        'quarantined_absent': QUARANTINED,
        'multi_component_note': 'same-ex-date multi-component events preserved '
            'as separate rows (3 measured: 600519/000402/000501); exact-dup key '
            '(code,ex_date,cash,record_date) never collapses them (cash differs); '
            'TTM consumer sums cash over window',
        'v1_exploration_superseded': 'results/_r403bmc_t154_export.py + '
            'dividend_events.parquet (7-col, per_share baked, aggregated) kept '
            'as working papers only; deliverable = this v2 per ticket spec',
        'elapsed_sec': round(time.time() - t0, 1),
    }
    if fails:
        receipt['verdict'] = 'RED'
        receipt['failed_gates'] = fails
        with open(RECEIPT, 'w', encoding='utf-8') as fh:
            json.dump(receipt, fh, ensure_ascii=True, indent=1)
        log('VERDICT RED fails=%s -- parquet NOT written (fail-closed)' % fails)
        print('VERDICT RED fails=%s' % fails)
        return 2

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    df.to_parquet(OUT, index=False)
    chk = pd.read_parquet(OUT)
    rb_ok = (list(chk.columns) == list(df.columns) and len(chk) == len(df)
             and abs(float(chk['cash_div_per_10'].sum())
                     - float(df['cash_div_per_10'].sum())) < 1e-9)
    if not rb_ok:
        receipt['verdict'] = 'RED'
        receipt['failed_gates'] = ['G10_readback']
        with open(RECEIPT, 'w', encoding='utf-8') as fh:
            json.dump(receipt, fh, ensure_ascii=True, indent=1)
        os.remove(OUT)
        log('VERDICT RED readback mismatch -- parquet removed')
        print('VERDICT RED readback mismatch')
        return 2

    import hashlib
    with open(OUT, 'rb') as fh:
        sha = hashlib.sha256(fh.read()).hexdigest()
    receipt['verdict'] = 'PASS'
    receipt['gates_passed'] = '10/10 (G1-G9 + G10 readback)'
    receipt['parquet_bytes'] = os.path.getsize(OUT)
    receipt['parquet_sha256'] = sha
    with open(RECEIPT, 'w', encoding='utf-8') as fh:
        json.dump(receipt, fh, ensure_ascii=True, indent=1)
    log('VERDICT PASS 10/10 -- %d bytes sha256=%s (%.1fs)'
        % (receipt['parquet_bytes'], sha, time.time() - t0))
    print('VERDICT PASS 10/10 rows=%d syms=%d bytes=%d sha256=%s span=%s..%s'
          % (n_rows, n_syms, receipt['parquet_bytes'], sha, d0, d1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
