"""T27 audit (r1093 bm-a): avail_date trustworthiness across the three fundamental statement panels.

Question: the growth-face digest found income_faces.avail_date shifted ~+1 year in the historical
range (median 360 days late vs statutory deadline) while recent periods look normal. T27 asks
whether cashflow_faces and balance_faces carry the same defect, and pins the boundary period.

Output: results/_r1093bma_t27_avail_audit.json  (read-only over panels; zero network; deterministic)
"""
import io, json, os, sys
import pandas as pd

PANELS = {
    'income': 'data/fund_statement_export/income_faces.parquet',
    'cashflow': 'data/fund_statement_export/cashflow_faces.parquet',
    'balance': 'data/fund_statement_export/balance_faces.parquet',
}
OUT = 'results/_r1093bma_t27_avail_audit.json'


def statutory(period_end_series):
    """Conservative statutory disclosure deadline (A-share law) for each period_end."""
    pe = pd.to_datetime(period_end_series, errors='coerce')
    mmdd = pe.dt.strftime('%m-%d')
    year = pe.dt.year
    deadline = pd.Series(pd.NaT, index=pe.index, dtype='datetime64[ns]')
    deadline[mmdd == '03-31'] = pd.to_datetime(year[mmdd == '03-31'].astype(str) + '-04-30')
    deadline[mmdd == '06-30'] = pd.to_datetime(year[mmdd == '06-30'].astype(str) + '-08-31')
    deadline[mmdd == '09-30'] = pd.to_datetime(year[mmdd == '09-30'].astype(str) + '-10-31')
    deadline[mmdd == '12-31'] = pd.to_datetime((year[mmdd == '12-31'] + 1).astype(str) + '-04-30')
    return deadline


def bucket(days):
    if pd.isna(days):
        return 'unparsed'
    if days < 0:
        return 'early_lt_deadline'
    if days <= 20:
        return 'on_time_le20'
    if 300 <= days <= 430:
        return 'year_shifted_300_430'
    if days > 430:
        return 'other_late_gt430'
    return 'late_21_299'


def audit(name, path):
    df = pd.read_parquet(path, columns=['code', 'period_end', 'avail_date'])
    dl = statutory(df['period_end'])
    av = pd.to_datetime(df['avail_date'], errors='coerce')
    days = (av - dl).dt.days
    b = days.map(bucket)
    dist = b.value_counts(normalize=True).round(4).to_dict()
    counts = b.value_counts().to_dict()
    by_year = {}
    py = pd.to_datetime(df['period_end'], errors='coerce').dt.year
    for y in sorted([int(x) for x in py.dropna().unique()])[-22:]:
        m = py == y
        by_year[str(y)] = {
            'rows': int(m.sum()),
            'median_days': None if days[m].dropna().empty else float(days[m].median()),
            'year_shifted_share': round(float((b[m] == 'year_shifted_300_430').mean()), 4),
        }
    # boundary: earliest period year where year_shifted share < 5%
    boundary = None
    for y in sorted([int(x) for x in py.dropna().unique()]):
        m = py == y
        if m.sum() < 50:
            continue
        if float((b[m] == 'year_shifted_300_430').mean()) < 0.05:
            boundary = y
            break
    # period-type breakdown (annual vs quarterly) -- isolates partial-panel defects
    mmdd = pd.to_datetime(df['period_end'], errors='coerce').dt.strftime('%m-%d')
    by_type = {}
    for pt in ('03-31', '06-30', '09-30', '12-31'):
        m = mmdd == pt
        if m.sum() == 0:
            continue
        by_type[pt] = {
            'rows': int(m.sum()),
            'median_days': None if days[m].dropna().empty else float(days[m].median()),
            'year_shifted_share': round(float((b[m] == 'year_shifted_300_430').mean()), 4),
        }
    return {
        'by_period_type': by_type,
        'panel': name,
        'rows': int(len(df)),
        'codes': int(df['code'].nunique()),
        'periods': int(df['period_end'].nunique()),
        'period_range': [str(df['period_end'].min())[:10], str(df['period_end'].max())[:10]],
        'median_days_late': None if days.dropna().empty else float(days.median()),
        'distribution': dist,
        'counts': counts,
        'year_shift_boundary_first_clean_year': boundary,
        'by_period_year_tail': by_year,
    }


def main():
    out = {'ts': None, 'audit': 'T27 growth/statement avail_date trust audit', 'panels': {}}
    import datetime
    out['ts'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
    for name, path in PANELS.items():
        if not os.path.isfile(path):
            out['panels'][name] = {'error': 'missing panel'}
            print(f'{name}: MISSING')
            continue
        r = audit(name, path)
        out['panels'][name] = r
        print(f"{name}: rows={r['rows']} median_late={r['median_days_late']} "
              f"year_shifted={r['distribution'].get('year_shifted_300_430', 0):.2%} "
              f"first_clean_year={r['year_shift_boundary_first_clean_year']}")
    verdict = all(
        (p.get('distribution', {}).get('year_shifted_300_430', 0) > 0.5)
        for p in out['panels'].values() if 'distribution' in p)
    out['verdict'] = {
        'same_defect_all_three_panels': bool(verdict),
        'policy': 'PIT dates MUST come from statutory deadline, never from panel avail_date, for periods before the first clean year',
        'consumer_action': 'no in-repo consumer may read avail_date from these panels',
    }
    io.open(OUT, 'w', encoding='utf-8', newline='\n').write(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    print('VERDICT same_defect_all_three=', verdict, '->', OUT)


if __name__ == '__main__':
    main()