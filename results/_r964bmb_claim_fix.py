# r964 bm-b correction: breaker-tripped claim fix (r949 claims-at-write law).
# Closeout prose (state did/note/verdict/next + round report row + heartbeat
# verdict) said "breaker not tripped / fails scattered" while the SAME-window
# evidence (driver log tail breaker line + receipt fails 10->30, done 726->746,
# rate 2.0/min) shows the 10-consecutive-double-fail breaker DID trip in the
# 06:30-06:40 night-dead window -> designed 300s probe cadence (r960 law).
# Monitor evidence file was already honest (breaker_in_log_tail=true), no fix
# needed there. Pushed commit body unfixable on origin (no force) -> correction
# rides C-r965 via corrected state.did + r965 round report row.
# round_reports.md edited on the BINARY face, own fresh r964 row only
# (r962 law: bytes.count==1 assert, zero other bytes touched).
import json

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
RPT = BM + r'\logs\iteration-loop\round_reports.md'
V5LOG = BM + r'\results\_r960bmb_restore_driver.log'

print('---- v5 driver log tail (evidence) ----')
with open(V5LOG, 'rb') as f:
    tail = f.read().decode('utf-8', 'replace').splitlines()[-8:]
for l in tail:
    print(l[:170])

# ---- round_reports.md: binary replace, own fresh r964 row only ----
with open(RPT, 'rb') as f:
    b = f.read()
old1 = 'fails=30（累计散布双败·连续断路器未触发·pass2 重试面）'.encode('utf-8')
new1 = 'fails=30（06:30-06:40 夜窗死面·10 连续双败断路器已触发→300s 探针节律·断路窗累计·pass2 重试面）'.encode('utf-8')
old2 = '当前活：v5 恢复驱动 pass1 在飞（746/1804·散布双败归 pass2）'.encode('utf-8')
new2 = '当前活：v5 恢复驱动 pass1 在飞（746/1804·断路器 300s 探针节律在跑·夜窗死面自愈设计中）'.encode('utf-8')
c1, c2 = b.count(old1), b.count(old2)
assert c1 == 1, 'old1 count=%d (must be 1)' % c1
assert c2 == 1, 'old2 count=%d (must be 1)' % c2
b = b.replace(old1, new1).replace(old2, new2)
with open(RPT, 'wb') as f:
    f.write(b)
print('round report row fixed: breaker-claim clause x1 + activity clause x1 (binary, own r964 row only)')

# ---- state.json ----
SP = BM + r'\state.json'
st = json.load(open(SP, encoding='utf-8'))
fixes = [
 ('did', 'breaker=consecutive-only not tripped, pass-2 owns fail set',
  'breaker TRIPPED 06:30-06:40 night-dead window (10 consecutive double-fails -> designed 300s probe cadence per r960; receipt fails 10->30, done 726->746, rate 2.0/min, ETA ~15:45 within <=24h commitment), pass-2 owns fail set'),
 ('note', 'r960 (retry-once + consecutive-only breaker, fails_in_pass=cumulative reading)',
  'r960 (retry-once + consecutive-only breaker, fails_in_pass=cumulative reading; r964 correction: breaker TRIPPED in 06:30-06:40 dead window, 300s probe cadence = designed response, no hand intervention)'),
 ('verdict', 'fails=30 scattered, pass-2 face',
  'fails=30 (breaker tripped night window, 300s probe, pass-2 face)'),
 ('next', 'retried_ok climbing = healthy; fails set = pass-2 face',
  'breaker-tripped dead windows = designed 300s probe cadence (r960); judge health by receipt done-climb + breaker cycle exit, not retried_ok; fails set = pass-2 face'),
]
for k, old, new in fixes:
    v = st.get(k, '')
    assert old in v, 'state.%s missing clause: %s' % (k, old[:50])
    st[k] = v.replace(old, new)
st['r964_correction'] = ('breaker-claim fixed in-window per r949 (closeout prose said not-tripped '
                         'while same-window evidence showed tripped; round report row + state + '
                         'heartbeat fixed on binary/verbatim faces; C-r964 commit body on origin '
                         'carries the stale clause, correction reaches origin via C-r965 state.did')
json.dump(st, open(SP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state.json fixed: did/note/verdict/next clauses replaced + r964_correction field')

# ---- heartbeat ----
HB = BM + r'\fleet\machines\bm-b.json'
hb = json.load(open(HB, encoding='utf-8'))
oldv = 'fails=30(scattered,pass-2 face)'
newv = 'fails=30(breaker tripped 06:30-06:40 night window,300s probe,pass-2 face)'
assert oldv in hb.get('verdict', ''), 'heartbeat verdict clause missing'
hb['verdict'] = hb['verdict'].replace(oldv, newv)
assert 'breaker_seen=True' in hb.get('did', ''), 'heartbeat did breaker_seen=True face expected (keep)'
json.dump(hb, open(HB, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
e2 = json.load(open(HB, encoding='utf-8'))
assert isinstance(e2.get('heartbeat_epoch_utc'), int), 'epoch must stay JSON int'
print('heartbeat fixed: verdict clause replaced; did breaker_seen=True kept; epoch int re-verified')
print('CORRECTION DONE')
