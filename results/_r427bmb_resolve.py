# -*- coding: utf-8 -*-
# r427 bm-b rebase conflict resolver (canon: bigmoney-conflict-resolve skill)
# stages: :1: base, :2: ours = upstream origin/main (bm-c r219 series), :3: theirs = replayed bm-b r427 commit
# recipes: compute_audit.json = rolling-ledger union + latest take-new (r188/R208, deep-scan nested ts);
#          runnable_pool.json = pool-entry-done-union (r312: done absorbs, one-side-only keep) + W7 shard done-flip convention
import json, subprocess, io, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def blob(stage, path):
    out = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    assert out.returncode == 0, (stage, path, out.stderr[:200])
    return json.loads(out.stdout.decode('utf-8'))

# ---------- 1) compute_audit.json ----------
P_AUDIT = 'results/compute_audit.json'
a_c = blob(2, P_AUDIT)   # bm-c side
a_b = blob(3, P_AUDIT)   # bm-b r427 side
h_c, h_b = a_c['history'], a_b['history']
key = lambda r: json.dumps(r, sort_keys=True, ensure_ascii=False)
union = {key(r): r for r in h_c}
for r in h_b:
    union[key(r)] = r
rows = sorted(union.values(), key=lambda r: r['ts'])
n_union = len(rows)
trim = rows[-201:]  # producer semantics: read[-200:] + 1 append = 201 steady-state cap
# latest: take-new by nested ts (deep-scan; both are top-level dicts with .ts)
lt_c, lt_b = a_c['latest'], a_b['latest']
latest = lt_b if str(lt_b.get('ts', '')) >= str(lt_c.get('ts', '')) else lt_c
audit_out = {'latest': latest, 'history': trim}
json.loads(json.dumps(audit_out, ensure_ascii=False))  # parse-verify before write (r185)
io.open(P_AUDIT, 'w', encoding='utf-8', newline='') and None
with io.open(P_AUDIT, 'w', encoding='utf-8', newline='') as f:
    json.dump(audit_out, f, ensure_ascii=False, indent=2)
print(f'[audit] union rows={n_union} (bm-c {len(h_c)} + bm-b {len(h_b)}), trimmed to {len(trim)}, latest.ts={latest["ts"]} ({"bm-b" if latest is lt_b else "bm-c"} side)')

# ---------- 2) runnable_pool.json ----------
P_POOL = 'results/runnable_pool.json'
p_c = blob(2, P_POOL)
p_b = blob(3, P_POOL)
e_c = {e['id']: e for e in p_c['entries']}
e_b = {e['id']: e for e in p_b['entries']}
all_ids = list(dict.fromkeys([e['id'] for e in p_c['entries']] + [e['id'] for e in p_b['entries']]))

merged_entries = []
absorbed = 0
for eid in all_ids:
    c, b = e_c.get(eid), e_b.get(eid)
    if c is None:                    # one-side-only (my SCREEN) -> keep
        merged_entries.append(b); continue
    if b is None:                    # one-side-only bm-c -> keep
        merged_entries.append(c); continue
    if key(c) == key(b):
        merged_entries.append(b); continue
    # diverged: done absorbs (either side done -> done, completing machine's record)
    if b.get('status') == 'done' and c.get('status') != 'done':
        m = dict(b)
        # zero-loss: carry bm-c-only documentation keys on the entry and shard yield_note
        for k, v in c.items():
            if k not in m and k not in ('status', 'shards'):
                m[k] = v
        msh, csh = m.get('shards', []), c.get('shards', [])
        for si, s in enumerate(msh):
            cs = next((x for x in csh if x.get('key') == s.get('key')), None)
            if cs:
                for k, v in cs.items():
                    if k not in s and k not in ('status', 'owner', 'owner_since', 'done_at', 'note'):
                        s[k] = v   # carry e.g. yield_note (non-authoritative doc field)
        merged_entries.append(m); absorbed += 1
    elif c.get('status') == 'done' and b.get('status') != 'done':
        m = dict(c)
        for k, v in b.items():
            if k not in m and k not in ('status', 'shards'):
                m[k] = v
        merged_entries.append(m); absorbed += 1
    else:
        # both same status (ready/ready or done/done with diverged content): shard-level union, done absorbs at shard level
        m = dict(b if str(b.get('updated_at', '')) >= str(c.get('updated_at', '')) else c)
        raise SystemExit(f'UNEXPECTED same-status divergence for {eid}: manual adjudication required')

# W7-convention shard done-flip for GENERATE (my harvest missed it; complete it in the merge)
gen = next(e for e in merged_entries if e['id'] == 'TRIAL-LABOR-W8-GENERATE')
assert gen['status'] == 'done', gen['status']
for s in gen.get('shards', []):
    if s.get('status') != 'done':
        s['status'] = 'done'
        s['done_at'] = gen['done_at']
        s['note'] = (s.get('note', '') + ' | harvest r427 bm-b done-flip').lstrip(' |')

scr = next(e for e in merged_entries if e['id'] == 'TRIAL-LABOR-W8-SCREEN')
assert scr['status'] == 'ready' and scr.get('lane_owner') == 'bm-b'  # pit-103 lane_owner present

pool_out = dict(p_b)  # version/law_ref/schema from my side (schema verified same both sides)
pool_out['entries'] = merged_entries
pool_out['updated_at'] = max(str(p_b.get('updated_at', '')), str(p_c.get('updated_at', '')))
pool_out['_stamp_note'] = ('r427 bm-b conflict-union with bm-c r219 (rebase replay 5b1bab03e onto 7f564efb1): '
                           'pool-entry-done-union r312 [W8-GENERATE done absorbs bm-b harvest record; bm-c yield_note '
                           'carried zero-loss; W8-SCREEN one-side keep] + audit rolling-ledger union; '
                           f'entries={len(merged_entries)}')
json.loads(json.dumps(pool_out, ensure_ascii=False))  # parse-verify (r185)
tmp = P_POOL + '.tmp_r427bmb'
with io.open(tmp, 'w', encoding='utf-8', newline='') as f:
    json.dump(pool_out, f, ensure_ascii=False, indent=2)
    f.write('\n')
data = open(tmp, 'rb').read().replace(b'\n', b'\r\n')
open(tmp, 'wb').write(data)
os.replace(tmp, P_POOL)

print(f'[pool] entries merged={len(merged_entries)} (bm-c {len(p_c["entries"])} + bm-b {len(p_b["entries"])}), '
      f'done-absorbed={absorbed}, GENERATE shard done-flip applied, SCREEN kept ready lane_owner=bm-b')
# zero-loss assertions
assert len(merged_entries) == 115, len(merged_entries)
ids_c = set(e_c); ids_b = set(e_b)
assert set(all_ids) == ids_c | ids_b
print('[pool] zero-loss check: union ids == |A u B| :', set(e['id'] for e in merged_entries) == ids_c | ids_b)
