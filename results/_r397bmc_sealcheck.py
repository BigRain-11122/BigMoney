# -*- coding: utf-8 -*-
# seal-check: high==low on the suspect fill days
import sys
sys.path.insert(0, r'K:\Fluxgroup\FluxGroup\quant\bigmoney\scripts')
import lowamp_deep_p1 as L
prices = L.load_axis('deep')
dates = [('159919', ['2013-12-16', '2013-12-17', '2013-12-18']),
         ('510300', ['2014-01-03', '2014-01-06', '2014-01-07']),
         ('510050', ['2017-05-11', '2017-05-12', '2017-05-15']),
         ('510330', ['2014-06-26', '2014-06-27', '2014-06-30']),
         ('159920', ['2018-09-14', '2018-09-17']),
         ('159934', ['2016-07-08', '2016-07-11'])]
for s, ds in dates:
    for d in ds:
        row = prices[s].loc[d]
        sealed = bool(row['high'] == row['low'])
        print(s, d, 'SEALED(h==l)' if sealed else 'ok',
              {k: round(float(v), 4) for k, v in row.items()})
