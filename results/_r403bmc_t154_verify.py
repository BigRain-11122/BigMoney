# -*- coding: utf-8 -*-
"""r403 verify: parquet schema (date32) + spot rows for the T-154 v2 deliverable."""
import pyarrow.parquet as pq
import pandas as pd

P = r'K:\Fluxgroup\FluxGroup\quant\bigmoney\data\fund_history_export\div_events_faces.parquet'
s = pq.read_schema(P)
print('schema:', [(f.name, str(f.type)) for f in s])
df = pd.read_parquet(P)
print('rows', len(df), 'cols', list(df.columns))
print('null cash:', int(df['cash_div_per_10'].isna().sum()))
m = df[df['code'] == '600519']
r = m[m['ex_date'].astype(str).str.startswith('2006-05-19')]
print('600519 2006-05-19 rows:', len(r), 'cash sum:', float(r['cash_div_per_10'].sum()))
b = df[df['code'] == '000001']
r2 = b[b['ex_date'].astype(str).str.startswith('2026-09')]
print('000001 2026-09 rows:', len(r2), 'cash:', list(r2['cash_div_per_10']))
print('dtypes:', dict(df.dtypes.astype(str)))
