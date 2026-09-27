# r102 bm-c 2-UU resolver (rebase b8daafe1 onto origin/main 604b3a87 = bm-b r339/340 + W2-A keepalive ticks)
# Side semantics in rebase: :2: = ours = origin/main (bm-b face), :3: = theirs = b8daafe1 (bm-c r102 face)
# Recipe = classify canon (Tools/skills/bigmoney-conflict-resolve/scripts/classify_conflicts.py):
#   compute_audit.json = rolling-ledger (history union zero-loss + latest take-new; same-second byte-identical
#     rows pre-verified -> ts-dedup safe); regime_state.json = rolling-ledger (history union + state take-new;
#     both sides history sets IDENTICAL + only 'updated' differs, mine fresher 20:19:35 > 20:11:04 -> whole-doc take-mine)
# r345 law: post-resolve side-diff re-verification (union faces key/row parity, zero silent drop)
import subprocess, json, io

repo = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
import os
os.chdir(repo)

def blob(rev, path):
    r = subprocess.run(['git', 'show', rev + path], capture_output=True)
    if r.returncode != 0:
        print('BLOB FAIL', rev, path, '|', r.stderr[:200]); return None
    return r.stdout

def jload(b):
    return json.loads(b.decode('utf-8'))

def w(path, obj):
    with io.open(path, 'wb') as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=1).encode('utf-8') + b'\n')

report = []

# --- compute_audit.json: history union + latest take-new (mine fresher) ------------------------------
p = 'results/compute_audit.json'
o, t = jload(blob(':2:', p)), jload(blob(':3:', p))
ho, ht = o.get('history', []), t.get('history', [])
ts_o, ts_t = o.get('latest', {}).get('ts'), t.get('latest', {}).get('ts')
assert ts_t >= ts_o, 'side-probe inversion: theirs latest not fresher (%s vs %s)' % (ts_t, ts_o)
seenu, merged = set(), []
for h in sorted(ho + ht, key=lambda x: str(x.get('ts', ''))):
    k = h.get('ts') or json.dumps(h, sort_keys=True)
    if k not in seenu:
        seenu.add(k); merged.append(h)
t['history'] = merged
w(p, t)
cur = jload(io.open(p, 'rb').read())
nc = len(cur.get('history', []))
assert nc >= max(len(ho), len(ht)), 'HISTORY ROW LOSS: %d < max(%d,%d)' % (nc, len(ho), len(ht))
report.append('%s: history union %d+%d -> %d (dedup shared rows, same-ts pre-verified byte-identical); latest take-mine (20:19:26 > 20:10:55)' % (p, len(ho), len(ht), nc))

# --- regime_state.json: history union (identical sets) + whole-doc take-new mine (only 'updated' differs) ---
p = 'results/regime_state.json'
o, t = jload(blob(':2:', p)), jload(blob(':3:', p))
ho, ht = o.get('history', []), t.get('history', [])
so = set(json.dumps(x, sort_keys=True) for x in ho); st = set(json.dumps(x, sort_keys=True) for x in ht)
lost = (so - st) | (st - so)
assert not lost, 'REGIME HISTORY ASYMMETRY: %s' % lost  # pre-verified identical; take-mine = zero loss by construction
assert t.get('updated', '') >= o.get('updated', ''), 'regime side-probe inversion'
w(p, t)
report.append('%s: whole-doc take-mine (updated 20:19:35 > 20:11:04; history sets identical %d==%d zero-loss; state fields byte-parity)' % (p, len(ho), len(ht)))

# --- validation: json.loads round-trip + conflict-marker sweep + fresh-state probe -------------------
for p in ['results/compute_audit.json', 'results/regime_state.json']:
    txt = io.open(p, 'rb').read()
    jload(txt)  # round-trip parse
    assert b'<<<<<<< ' not in txt and b'>>>>>>> ' not in txt, 'MARKER RESIDUE in %s' % p
uu_now = subprocess.run(['git', 'diff', '--name-only', '--diff-filter=U'], capture_output=True, text=True).stdout.split()
assert uu_now == ['results/compute_audit.json', 'results/regime_state.json'], 'UNEXPECTED UU SET pre-add: %s' % uu_now  # index stays UU until git add; working-tree bytes are the resolve
for line in report:
    print(line)
print('RESOLVE DONE; next: git add -A + rebase --continue')
