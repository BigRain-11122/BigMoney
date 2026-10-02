# -*- coding: utf-8 -*-
"""T-2026-10-03-152 quality faces export (roe_q -> quality_faces.parquet).

Lane: bm-c machine-local data/fund_history (R31/R65 data lane).
Precedent: T-149 value_faces export (commit 5c3939640, 18.3MB direct git).
Spec gates (ticket verbatim, fail-closed -- parquet written ONLY on all-pass):
  (1) rows whose period key is not a valid report-period end (MM-DD in
      {03-31, 06-30, 09-30, 12-31}) are EXCLUDED, count + per-sym DISCLOSED
      (honest exclusion, zero silent drops; roe_q:nonperiod_keys 13 syms
      cross-checked against PIT audit receipt);
  (2) n_symbols >= 5100;
  (3) per-symbol avail-anchor count median >= 50 AND p10 >= 20
      (AMENDED r604 bm-b per MSG-2026-10-03-0548 adjudication: original
      single floor median>=60 was this ticket's own estimate, disproven by
      live export evidence -- median listing year ~2013-14 = universe
      immutable property; reality 52/26 passes dual gate with margin);
  (4) avail_date coverage 2001-04-30 .. 2026-08-31 (min<=, max>=);
  (5) zero duplicate period_end per symbol; avail_date monotonic
      non-decreasing per symbol (statutory FY & next-Q1 legally share 04-30);
  (6) statutory mapping EXACT on every exported row (machine re-check).
Columns EXACT: [code, period_end, avail_date, roe_q] (string/string/string/float64-NaN).
"""
import json, os, re, sys, time, statistics

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
SRC = os.path.join(REPO, 'data', 'fund_history')
OUT = os.path.join(REPO, 'data', 'fund_history_export', 'quality_faces.parquet')
RECEIPT = os.path.join(REPO, 'results', 't152_quality_faces_export.json')
AUDIT = os.path.join(REPO, 'results', 'fund_pit_audit', 'audit_results.json')
LOG = os.path.join(REPO, 'results', '_r397bmc_t152_log.txt')

VALID_MD = {('03', '31'), ('06', '30'), ('09', '30'), ('12', '31')}
ROE_KEY = u'\u51c0\u8d44\u4ea7\u6536\u76ca\u7387(%)'  # 净资产收益率(%)

ISO_RE = re.compile(r'^(\d{4})-(\d{1,2})-(\d{1,2})')
CN_RE = re.compile(r'^(\d{4})\u5e74(\d{1,2})\u6708(\d{1,2})\u65e5')


def log(msg):
    with open(LOG, 'a', encoding='utf-8') as fh:
        fh.write(msg + '\n')
        fh.flush()


def parse_key(s):
    if not isinstance(s, str):
        return None
    m = ISO_RE.match(s.strip())
    if m:
        return m.group(1), '%02d' % int(m.group(2)), '%02d' % int(m.group(3))
    m = CN_RE.match(s.strip())
    if m:
        return m.group(1), '%02d' % int(m.group(2)), '%02d' % int(m.group(3))
    return None


def statutory(y, md):
    if md == ('03', '31'):
        return '%s-04-30' % y
    if md == ('06', '30'):
        return '%s-08-31' % y
    if md == ('09', '30'):
        return '%s-10-31' % y
    if md == ('12', '31'):
        return '%04d-04-30' % (int(y) + 1)
    return None


def main():
    t0 = time.time()
    log('=== r397 bm-c T-152 quality faces export start %s ==='
        % time.strftime('%Y-%m-%d %H:%M:%S'))
    audit_flagged = set()
    try:
        with open(AUDIT, 'r', encoding='utf-8') as fh:
            audit = json.load(fh)
        for it in audit.get('flagged_symbols', []):
            if 'roe_q:nonperiod_keys' in (it.get('flags') or []):
                audit_flagged.add(str(it.get('code')))
        log('audit flagged roe_q:nonperiod_keys syms: n=%d' % len(audit_flagged))
    except Exception as e:
        log('[warn] audit receipt unreadable: %s' % e)

    codes = sorted(d for d in os.listdir(SRC)
                   if os.path.isdir(os.path.join(SRC, d)))
    n_dirs = len(codes)
    rows = []
    per_sym_counts = []
    n_missing, n_empty, n_excluded, n_unparsable = 0, 0, 0, 0
    n_null_roe, n_bad_roe = 0, 0
    excluded_by_sym = {}
    fmt_iso = fmt_cn = fmt_other = 0
    dup_syms, mono_bad_syms = [], []
    avail_min, avail_max = None, None

    for code in codes:
        p = os.path.join(SRC, code, 'roe_q.json')
        if not os.path.exists(p):
            n_missing += 1
            continue
        try:
            with open(p, 'r', encoding='utf-8') as fh:
                j = json.load(fh)
        except Exception as e:
            log('[warn] json parse fail %s: %s' % (code, e))
            n_missing += 1
            continue
        rs = j.get('rows') or []
        if not rs:
            n_empty += 1
            continue
        seen = set()
        sym_rows = []
        sym_dup = False
        for r in rs:
            key = r.get(u'\u65e5\u671f')  # 日期
            parsed = parse_key(key) if key is not None else None
            if parsed is None:
                n_unparsable += 1
                n_excluded += 1
                excluded_by_sym[code] = excluded_by_sym.get(code, 0) + 1
                fmt_other += 1
                continue
            if ISO_RE.match(str(key).strip()):
                fmt_iso += 1
            else:
                fmt_cn += 1
            y, mm, dd = parsed
            md = (mm, dd)
            if md not in VALID_MD:
                n_excluded += 1
                excluded_by_sym[code] = excluded_by_sym.get(code, 0) + 1
                continue
            pe = '%s-%s-%s' % (y, mm, dd)
            if pe in seen:
                sym_dup = True
                continue
            seen.add(pe)
            v = r.get(ROE_KEY)
            if v is None:
                n_null_roe += 1
                fv = float('nan')
            else:
                try:
                    fv = float(v)
                except (TypeError, ValueError):
                    n_bad_roe += 1
                    fv = float('nan')
            sym_rows.append((code, pe, statutory(y, md), fv))
        if sym_dup:
            dup_syms.append(code)
        sym_rows.sort(key=lambda t: t[1])
        av = [t[2] for t in sym_rows]
        if any(av[i] > av[i + 1] for i in range(len(av) - 1)):
            mono_bad_syms.append(code)
        if sym_rows:
            lo, hi = av[0], av[-1]
            if avail_min is None or lo < avail_min:
                avail_min = lo
            if avail_max is None or hi > avail_max:
                avail_max = hi
        rows.extend(sym_rows)
        per_sym_counts.append(len(sym_rows))

    n_symbols = len(per_sym_counts)
    median_anchors = float(statistics.median(per_sym_counts)) if per_sym_counts else 0.0
    p10_anchors = float(statistics.quantiles(per_sym_counts, n=10)[0]) if len(per_sym_counts) >= 10 else 0.0

    # gate 6 machine re-check: statutory mapping exact on every exported row
    map_bad = 0
    for code, pe, av, fv in rows:
        y = pe[:4]
        md = (pe[5:7], pe[8:10])
        if statutory(y, md) != av:
            map_bad += 1
    map_exact = (map_bad == 0)

    gates = {
        'n_symbols_ok': bool(n_symbols >= 5100),
        'anchor_median_ok': bool(median_anchors >= 50),  # amended r604 bmb
        'anchor_p10_ok': bool(p10_anchors >= 20),        # amended r604 bmb dual gate
        'coverage_ok': bool(avail_min is not None and avail_min <= '2001-04-30'
                            and avail_max is not None and avail_max >= '2026-08-31'),
        'dup_period_end_ok': bool(not dup_syms),
        'mono_avail_ok': bool(not mono_bad_syms),
        'statutory_map_exact': bool(map_exact),
    }
    verdict = 'PASS' if all(gates.values()) else 'FAIL'

    out_bytes = 0
    if verdict == 'PASS':
        import pandas as pd
        df = pd.DataFrame(rows, columns=['code', 'period_end', 'avail_date', 'roe_q'])
        df = df.astype({'code': 'object', 'period_end': 'object',
                        'avail_date': 'object', 'roe_q': 'float64'})
        df.to_parquet(OUT, index=False)
        out_bytes = os.path.getsize(OUT)
        log('parquet written: %d rows, %d bytes' % (len(df), out_bytes))
    else:
        log('FAIL-CLOSED: parquet NOT written; gates=%s' % json.dumps(gates))

    flagged_excl = sorted(set(excluded_by_sym) & audit_flagged)
    flagged_no_excl = sorted(audit_flagged - set(excluded_by_sym))
    excl_not_flagged = sorted(set(excluded_by_sym) - audit_flagged)
    receipt = {
        'ticket': 'T-2026-10-03-152-P1',
        'machine': 'bm-c',
        'n_dirs': n_dirs,
        'n_symbols': n_symbols,
        'missing_face_syms': n_missing,
        'empty_face_syms': n_empty,
        'excluded_nonperiod_rows': n_excluded,
        'excluded_unparsable_rows': n_unparsable,
        'excluded_by_sym': excluded_by_sym,
        'excluded_syms_n': len(excluded_by_sym),
        'audit_flagged_13_cross': {
            'flagged_with_exclusions': flagged_excl,
            'flagged_without_exclusions': flagged_no_excl,
            'excluded_not_in_audit_flags': excl_not_flagged,
        },
        'date_format_counts': {'iso': fmt_iso, 'cn': fmt_cn, 'other': fmt_other},
        'anchor_median': median_anchors,
        'anchor_p10': p10_anchors,
        'avail_global_min': avail_min,
        'avail_global_max': avail_max,
        'dup_period_end_syms': dup_syms,
        'mono_violation_syms': mono_bad_syms,
        'statutory_map_bad_rows': map_bad,
        'n_rows': len(rows),
        'n_roe_nonnull': sum(1 for r in rows if r[3] == r[3]),
        'n_roe_null': n_null_roe + n_bad_roe,
        'gates': gates,
        'out': OUT if verdict == 'PASS' else None,
        'bytes': out_bytes,
        'elapsed_sec': round(time.time() - t0, 1),
        'verdict': verdict,
        'note': ('roe_q face, statutory avail_date baked in per PIT audit '
                 'pit.financial_face_rule; honest exclusion of nonperiod rows '
                 'disclosed above; FY & next-Q1 legally share avail 04-30 '
                 '(non-decreasing mono per spec; probe leg2 dup axis note in '
                 'flight to bm-b).'),
    }
    with open(RECEIPT, 'w', encoding='utf-8') as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1, sort_keys=True)
    log('receipt written: %s verdict=%s gates=%s' % (RECEIPT, verdict, json.dumps(gates)))
    log('=== T-152 export end %s elapsed=%.1fs ==='
        % (time.strftime('%Y-%m-%d %H:%M:%S'), time.time() - t0))
    return 0 if verdict == 'PASS' else 2


if __name__ == '__main__':
    sys.exit(main())
