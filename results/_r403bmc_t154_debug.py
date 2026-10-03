# -*- coding: utf-8 -*-
"""r403 debug: actual dtypes/element types in v2 export construction."""
import datetime
import sys

sys.path.insert(0, r'K:\Fluxgroup\FluxGroup\quant\bigmoney\results')
import pandas as pd  # noqa: E402

import _r403bmc_t154_export_v2 as v2  # noqa: E402

# rebuild minimal frame the same way the script does
import json, os  # noqa: E402

SRC = v2.SRC
rows_out = []
for sym in sorted(os.listdir(SRC))[:5]:
    p = os.path.join(SRC, sym, 'div_events.json')
    if not os.path.exists(p):
        continue
    j = json.load(open(p, encoding='utf-8'))
    for row in j.get('rows') or []:
        ex = v2.date_str(row.get(v2.K_EX))
        if ex is None or str(row.get(v2.K_PROG) or '').strip() != v2.IMPL:
            continue
        rows_out.append((sym, ex, row.get(v2.K_CASH), v2.date_str(row.get(v2.K_REC))))

df = pd.DataFrame({'code': [r[0] for r in rows_out],
                   'cash_div_per_10': [float(r[2]) for r in rows_out]})
df['ex_date'] = pd.Series([v2.to_date(r[1]) for r in rows_out], dtype=object)
df['record_date'] = pd.Series([v2.to_date(r[3]) for r in rows_out], dtype=object)
df = df[['code', 'ex_date', 'cash_div_per_10', 'record_date']]
print('pandas', pd.__version__)
print('dtypes:', dict(df.dtypes.astype(str)))
print('code dtype ==', str(df['code'].dtype))
print('ex_date elem type:', type(df['ex_date'].iloc[0]).__name__)
print('ex_date is date:', isinstance(df['ex_date'].iloc[0], datetime.date))
print('cash dtype ==', str(df['cash_div_per_10'].dtype))
