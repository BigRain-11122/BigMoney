# -*- coding: utf-8 -*-
"""r570 bm-b: repair pool_core_samples.jsonl (pretty-blob corruption from the
r569 closeout union face) + verify.

Corruption: lines 1..71 = ONE pretty-printed JSON document (attrition-scan
evidence shape, indent=1, ts 2026-10-02T10:17:23) that entered the file at
commit 733fcca4f (r569 closeout conflict-union window, -S provenance).
The blob is preserved in git history at 733fcca4f (recoverable); it does
NOT belong in this append-only jsonl (row schema = per-batch dict rows).

Repair (r294 domain law, byte-exact line-level union):
  base  = all dict rows from the last pre-blob commit 3bc52e65f
  plus  = current-file dict rows not already in base (append-only growth)
  out   = base + plus, original line bytes preserved verbatim.
"""
import json
import subprocess

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
FP = REPO + r'\results\pool_core_samples.jsonl'
PRE_BLOB_SHA = '3bc52e65f'

# --- base: pre-blob committed rows (byte-exact) -----------------------------
raw_old = subprocess.check_output(
    ['git', '-C', REPO, 'show', PRE_BLOB_SHA + ':results/pool_core_samples.jsonl']
).decode('utf-8')
old_lines = [l for l in raw_old.splitlines() if l.strip()]
base, bad_old = [], 0
for l in old_lines:
    try:
        r = json.loads(l)
    except Exception:
        bad_old += 1
        continue
    if isinstance(r, dict):
        base.append(l)
assert bad_old == 0, f'pre-blob version had {bad_old} junk lines (unexpected)'

# --- current file: keep dict rows, drop the pretty blob fragments ------------
raw_new = open(FP, 'rb').read()
eol = '\r\n' if raw_new.count(b'\r\n') * 2 > raw_new.count(b'\n') else '\n'
cur_lines = [l for l in raw_new.decode('utf-8').splitlines() if l.strip()]
good_cur, junk_cur = [], 0
for l in cur_lines:
    try:
        r = json.loads(l)
    except Exception:
        junk_cur += 1
        continue
    if isinstance(r, dict):
        good_cur.append(l)
    else:
        junk_cur += 1

base_set = set(base)
plus = [l for l in good_cur if l not in base_set]
out = base + plus
assert len(out) == len(base) + len(plus)
# every out line must be a dict row
for l in out:
    assert isinstance(json.loads(l), dict)

data = eol.join(out) + eol
open(FP, 'wb').write(data.encode('utf-8'))
print(f'repaired: base={len(base)} (pre-blob {PRE_BLOB_SHA}) '
      f'+ new-appended={len(plus)} = {len(out)} dict rows; '
      f'dropped junk/blob lines={junk_cur} (blob preserved in git history '
      f'at 733fcca4f); eol={"CRLF" if eol == chr(13) + chr(10) else "LF"}')
