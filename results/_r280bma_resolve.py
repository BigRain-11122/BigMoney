# -*- coding: utf-8 -*-
"""R280 bm-a S0 rebase resolver: results/autofill_state.json (mixed-dict+ledger).

Collision: bm-a tick commit c41ef933 (revosc claim 00:10:01) vs bm-b 69014e67
maintenance commit (fusion-nav-0of1 bm-b claim 00:00:01 landed via origin).
Recipe per skill bigmoney-conflict-resolve / r203/R208/r215/r220/r245:
- launches: union both blobs by (entry,ts,machine,shard); shared-key field
  diffs resolved to the side with richer/newer field state (crash_counted=True
  is the counted-newer state); sort ts desc -> cap 50 -> re-sort ts asc
  (producer append order, r245 law: write-back must be ascending).
- last_tick: inner ts compare, WHOLE dict assign (mine 00:10:01 > 00:00:01);
  no str() comparison; assert isinstance(last_tick, dict).
- Format mirror: indent=1, CRLF (newline translation mode), no trailing
  newline (both blobs end without \n), per r223/r234.
"""
import subprocess, json, io, sys

def load(rev):
    raw = subprocess.run(['git','show',rev+':results/autofill_state.json'],
                         capture_output=True, check=True).stdout
    return raw, json.loads(raw.decode('utf-8-sig'))

raw_m, m = load('REBASE_HEAD')   # bm-a tick commit (being replayed)
raw_o, o = load('HEAD')          # origin/main tip (bm-b maintenance landed)

def key(l): return (l['entry'], l['ts'], l.get('machine'), l.get('shard'))

merged = {}
for l in o['launches']: merged[key(l)] = dict(l)
for l in m['launches']:
    k = key(l)
    if k in merged:
        # field-level: keep the side carrying more state (crash_counted etc.)
        if len(l) >= len(merged[k]): merged[k] = dict(l)
    else:
        merged[k] = dict(l)

# union -> newest-50 rolling window (ts desc), then producer append order (asc)
desc = sorted(merged.values(), key=lambda l: l['ts'], reverse=True)
if len(desc) > 50:
    dropped = [ (l['entry'], l['ts']) for l in desc[50:] ]
    print('cap50 dropped (oldest):', dropped)
kept = sorted(desc[:50], key=lambda l: l['ts'])  # ascending = append order

lt_m, lt_o = m['last_tick'], o['last_tick']
last_tick = lt_m if lt_m.get('ts','') >= lt_o.get('ts','') else lt_o
assert isinstance(last_tick, dict), 'last_tick must be dict'

out = {'launches': kept, 'last_tick': last_tick}
for extra in m:  # mirror any top-level extras from mine
    if extra not in out: out[extra] = m[extra]
for extra in o:
    if extra not in out: out[extra] = o[extra]

# zero-loss check: every unique launch key from both sides survives or is the
# explicitly-dropped oldest beyond cap
surv = {key(l) for l in kept}
allk = {key(l) for l in m['launches']} | {key(l) for l in o['launches']}
assert allk - surv <= set(desc[50:] and [key(l) for l in desc[50:]] or []) or allk <= surv | set(), 'zero-loss'

s = json.dumps(out, indent=1, ensure_ascii=False)
with io.open('results/autofill_state.json','w',encoding='utf-8',newline='\r\n') as f:
    f.write(s)  # no trailing newline (both base blobs end without \n)

# parse-verify round-trip (r185 law)
chk = json.loads(io.open('results/autofill_state.json',encoding='utf-8-sig').read())
assert len(chk['launches']) == len(kept) and isinstance(chk['last_tick'], dict)
ts_list = [l['ts'] for l in chk['launches']]
assert ts_list == sorted(ts_list), 'launches must be ts-ascending (r245)'
raw_disk = open('results/autofill_state.json','rb').read()
assert raw_disk.endswith(b'\r\n}') and not raw_disk.endswith(b'\n\r\n'), 'format mirror'
print('resolved: launches', len(chk['launches']), '| last_tick', chk['last_tick'].get('ts'),
      '| revosc-in', any(key(l)[0]=='REV-OSC-STOCK-P1' for l in chk['launches']),
      '| fusionnav-bmb-in', any(key(l)[1]=='2026-09-27 00:00:01' for l in chk['launches']),
      '| bytes', len(raw_disk))
