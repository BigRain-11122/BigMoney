# -*- coding: utf-8 -*-
"""r990 ordinal-face fix: dead-session retention assertion wrongly required the
98th ENGLISH ordinal inside the W237 prereg; family face law = current wave A
face carries its own English ordinal (NINETY-SEVENTH), next-wave projection
carries only the Chinese ordinal (第九十八例). W237 carries no NINETY-EIGHTH."""
import io

P = 'results/_w237bmc_prereg_derive.py'
src = io.open(P, encoding='utf-8').read()

old = "assert 'NINETY-EIGHTH' in out and '\\u7b2c\\u4e5d\\u5341\\u516b\\u4f8b' in out"
new = ("assert '\\u7b2c\\u4e5d\\u5341\\u516b\\u4f8b' in out  "
       "# r990 ordinal-face fix: 98th ENGLISH face belongs to W238 prereg (family law)")
assert src.count(old) == 1, src.count(old)
assert 'NINETY-SEVENTH' in src  # retention assertion for current face stays intact
io.open(P, 'w', encoding='utf-8', newline='').write(src.replace(old, new))
print('ordinal-face fix OK')
