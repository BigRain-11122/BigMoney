# r280bm-b T-87 ticket progress write-back: five-face byte probe first
# (R255 indent + R257 trailing-newline + BOM/EOL/ascii family laws), then
# add progress_r280_bmb field only -- zero touch on bm-a's whole-ticket faces.
import json, subprocess, sys, io

PATH = 'fleet/tasks/T-2026-09-26-87-P1.json'
raw_disk = open(PATH, 'rb').read()
blob = subprocess.run(['git', 'show', 'HEAD:' + PATH], capture_output=True).stdout
probe = {
    'disk_bytes': len(raw_disk), 'blob_bytes': len(blob),
    'disk_bom': raw_disk.startswith(b'\xef\xbb\xbf'),
    'blob_bom': blob.startswith(b'\xef\xbb\xbf'),
    'disk_crlf': b'\r\n' in raw_disk, 'blob_crlf': b'\r\n' in blob,
    'blob_tail_nl': blob.endswith(b'\n'), 'disk_tail_nl': raw_disk.endswith(b'\n'),
}
# indent depth: count leading spaces of the second line
second = blob.decode('utf-8-sig').splitlines()[1]
probe['blob_indent'] = len(second) - len(second.lstrip(' '))
src = blob.decode('utf-8-sig')
probe['ensure_ascii_face'] = ('\\u' in src)
d = json.loads(src)
probe['keys'] = sorted(d.keys())
print(json.dumps(probe, ensure_ascii=False))

NEW = ("r280 bm-b supply-lane BUILD DELIVERED (step-0 + collector + wiring): "
       "(1) step-0 endpoint probe results/_r280bmb_probe_akshare_daily.json -- "
       "ak.stock_zh_a_daily (sina, qfq) ALIVE 4/4 incl bj face, schema = "
       "date,open,high,low,close,volume,amount,outstanding_share,turnover; "
       "ak.stock_zh_a_hist (EM) 0/4 ConnectionError from bm-b = channel "
       "decision sina-only, EM face honest-disclosed dead. (2) collector "
       "scripts/update_astock_daily.py (family conventions mirror: 2.5s "
       "throttle, per-symbol checkpoint resume, conn-fuse 3, quarantine>=3, "
       "detached full-universe pass, 30-min spawn throttle, lock, atomic "
       "writes, selftest subcommand -- all guard cases PASS; deviation "
       "disclosed: qfq corporate-action rewrite = full re-pull + atomic "
       "replace counted readjusted, NOT family not-touched freeze -- qfq "
       "panel must track source adjusted truth). Universe = eligibility.csv "
       "6-digit codes 0/3->sz, 6->sh = 5,228 pullable; B-shares (2/9) + "
       "bj-nt (4/8/920) honestly skipped per-bucket (update_sina_mf "
       "precedent; bj probe-alive evidence recorded, extension = future "
       "signed decision). (3) live smoke 6 symbols 49,043 rows full-history "
       "1991->2026-09-24 zero failures, vwap unit anchor max 0.037 "
       "(r262 law diagnostic). (4) full-universe detached pass SPAWNED "
       "r280 23:47 (pid evidence in data lock; ~3.6h; status=results/"
       "astock_daily_update_status.json tracked). (5) S6 chain wired "
       "(Tools/iteration_prompt.txt update_astock_daily leg, lane=bm-b R31 "
       "guard). NEXT (r281+): pass completion check + Monday 09-28 daily "
       "continuation first live fire + consumption face (REV_OSC_STOCK_P1 "
       "paper forward leg reads panel; cross-machine data locality = "
       "fleet/TRANSFER.md mechanism decision when bm-a consumption opens).")

assert 'progress_r280_bmb' not in d, 'progress_r280_bmb already present'
d['progress_r280_bmb'] = NEW
out = json.dumps(d, ensure_ascii=probe['ensure_ascii_face'], indent=probe['blob_indent'])
if probe['blob_bom']:
    out_bytes = b'\xef\xbb\xbf' + out.encode('utf-8')
else:
    out_bytes = out.encode('utf-8')
if probe['blob_crlf']:
    out_bytes = out_bytes.replace(b'\n', b'\r\n')
if probe['blob_tail_nl'] and not out_bytes.endswith(b'\n'):
    out_bytes += b'\n'
with open(PATH, 'wb') as f:
    f.write(out_bytes)
# verify: json parses + only the one new field added vs HEAD
d2 = json.loads(open(PATH, 'rb').read().decode('utf-8-sig'))
assert d2['progress_r280_bmb'] == NEW
r = subprocess.run(['git', 'diff', '--stat', PATH], capture_output=True, text=True, encoding='utf-8')
print('diff --stat:', r.stdout.strip())
print('OK ticket write-back (field-level increment only expected)')
