# r486 bm-b: claim PERPETUAL-N1-W2 shards 3..11 (O-2210 claim-by-file + pool owner update)
# laws: r239 (fetch before claim), O-20260930-2355 (workers_plan code-backed), r289 (surgical)
import json, os, subprocess, sys, datetime

def sh(*args, **kw):
    return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace', **kw)

# 1. pull (ff only; tree clean)
r = sh('git', 'pull', '--ff-only')
if r.returncode != 0:
    print('PULL FAIL:', r.stdout, r.stderr); sys.exit(2)

# 2. origin pool state
pool_txt = subprocess.check_output(['git', 'show', 'origin/main:results/runnable_pool.json']).decode('utf-8-sig')
pool = json.loads(pool_txt)

MY = 'bm-b'
n1 = [e for e in pool['entries'] if e['id'].startswith('PERPETUAL-N1-W2-SHARD-')]
assert len(n1) == 12, f'expected 12 N1 entries, got {len(n1)}'
free_shards = []
for e in n1:
    for s in e['shards']:
        if s.get('owner') is None:
            free_shards.append((e, s))
print('free shards on origin:', sorted(s['key'] for _, s in free_shards))

# working copy must match origin semantically for N1 faces before edit
work = json.loads(open('results/runnable_pool.json', encoding='utf-8-sig').read())
wn1 = {e['id']: e for e in work['entries'] if e['id'].startswith('PERPETUAL-N1-W2-SHARD-')}
pn1 = {e['id']: e for e in n1}
for eid, pe in pn1.items():
    we = wn1.get(eid)
    if we is None or we['shards'] != pe['shards']:
        print(f'WORK/origin mismatch on {eid}: working {we["shards"] if we else None} vs origin {pe["shards"]}')
        sys.exit(2)

now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
claimed = []
for e, s in free_shards:
    i = int(e['id'].rsplit('-', 1)[1])          # PERPETUAL-N1-W2-SHARD-<i>
    if not (3 <= i <= 11):
        continue
    s['owner'] = MY
    s['owner_since'] = now[:19]
    s['status'] = 'running'
    # mirror into working copy (same object identity via pn1/wn1? no -- separate parses; edit work copy directly)
    ws = wn1[e['id']]['shards'][0]
    ws['owner'] = MY
    ws['owner_since'] = now[:19]
    ws['status'] = 'running'
    # workers_plan: O-2355 code-backed (conversion landed this round) + O-1858 holiday face
    plan = {"workers": 8, "priority": "Normal",
            "note": "O-2355 code-backed (ProcessPoolExecutor in runner; "
                    "BLAS 1/worker); workers=8 RAM-gated on bm-b "
                    "(dual-company discipline, avail ~4.6GB)"}
    for tgt in (e, wn1[e['id']]):
        tgt['workers_plan'] = plan
    # claim file
    d = os.path.join('results', 'pool_claims', e['id'])
    os.makedirs(d, exist_ok=True)
    cf = os.path.join(d, f"{s['key']}.{MY}.json")
    json.dump({"machine_id": MY, "state": "running", "pid": os.getpid(),
               "heartbeat": now, "started": now,
               "result_ref": "burn in progress (O-2355 multiprocess conversion "
                             "verification + wave shard burn)"},
              open(cf, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    claimed.append((e['id'], s['key'], cf))

print('claiming:', len(claimed), 'shards:', [c[1] for c in claimed])
assert len(claimed) == 9, f'expected 9 free shards 3..11, got {len(claimed)}'

# 3. write working pool surgically (indent2 + CRLF, r289)
txt = json.dumps(work, ensure_ascii=False, indent=2)
if '\r\n' in pool_txt:
    txt = txt.replace('\n', '\r\n')
with open('results/runnable_pool.json', 'w', newline='', encoding='utf-8') as f:
    f.write(txt)

# 4. commit + push claims
subprocess.check_call(['git', 'add', 'results/runnable_pool.json'] +
                       [c[2] for c in claimed])
msg = ("pool claims bm-b: PERPETUAL-N1-W2 shards 3..11 (9 of 12; 0-2 already "
       "bm-c) + workers_plan O-2355 code-backed update [claim-by-file O-2210]")
r = sh('git', 'commit', '-m', msg)
print(r.stdout.strip())
r = sh('git', 'push')
if r.returncode != 0:
    print('PUSH REJECTED:', r.stdout, r.stderr)
    sys.exit(2)
print('claims pushed.')
