# r276 bm-b rebase conflict resolver (S0 pull --rebase vs bm-a r272 9e66d7b8).
# Skill: bigmoney-conflict-resolve. 3 UU files (classifier: 2 classified + 1
# UNKNOWN hand-adjudicated):
#   post_review.jsonl        = append-log -> line-level union zero loss (r188/r217)
#   autofill_state.json      = mixed-dict+ledger -> launches full-row union,
#                              ts desc cap50, re-sort asc pre-write (r245);
#                              last_tick inner-ts compare whole-dict (r140 tie->ours)
#   REPORT-20260926.md       = UNKNOWN -> hand-adjudicated per r265 same-producer
#                              pairing: daily regenerated report face, take-new by
#                              generated ts (ours 22:20:02 vs theirs 22:30:13);
#                              post-rebase `python Tools/post_review.py run`
#                              re-derives the face from the union ledger anyway.
# Rebase semantics: :1 base, :2 ours = origin/bm-a r272, :3 theirs = my d26817a7.
import json, subprocess

def blob(stage, path):
    return subprocess.check_output(['git', 'show', f':{stage}:{path}'])

def face(raw):
    return {'bom': raw.startswith(b'\xef\xbb\xbf'), 'crlf': b'\r\n' in raw,
            'trailing_nl': raw.endswith(b'\n'),
            'indent': 2 if b'\n  "' in raw[:400] or b'\n  {' in raw[:400] else 1}

def dump_mirror(path, obj, mirror_raw):
    f = face(mirror_raw)
    enc = 'utf-8-sig' if f['bom'] else 'utf-8'
    nl = '\r\n' if f['crlf'] else '\n'
    s = json.dumps(obj, ensure_ascii=False, indent=f['indent'])
    if f['trailing_nl']:
        s += '\n'
    open(path, 'w', encoding=enc, newline='').write(s)

# ---- 1. post_review.jsonl: append-log line-level union ----
p = 'results/post_review.jsonl'
a, b = blob(2, p).decode('utf-8-sig').splitlines(), blob(3, p).decode('utf-8-sig').splitlines()
seen = set(a)
extra = [l for l in b if l not in seen]
merged = a + extra
raw = ('\r\n' if b'\r\n' in blob(1, p) else '\n').join(merged) + ('\n' if blob(1, p).endswith(b'\n') else '')
open(p, 'w', encoding='utf-8', newline='').write(raw)
assert len(merged) == len(set(merged)) == len(set(a) | set(b)), 'jsonl union count mismatch'
print(f'  {p}: union ours {len(a)} + theirs-only {len(extra)} -> {len(merged)} (zero-loss)')

# ---- 2. autofill_state.json: mixed-dict+ledger ----
p = 'results/autofill_state.json'
a, b = blob(2, p), blob(3, p)
ja, jb = json.loads(a.decode('utf-8-sig')), json.loads(b.decode('utf-8-sig'))
out = dict(ja)
la, lb = ja.get('launches', []), jb.get('launches', [])
by_row = {}
for row in la + lb:
    by_row[json.dumps(row, sort_keys=True, ensure_ascii=False)] = row
union_desc = sorted(by_row.values(), key=lambda r: r.get('ts', ''), reverse=True)
out['launches'] = sorted(union_desc[:50], key=lambda r: r.get('ts', ''))  # cap50 keeps newest, write asc (r245)
ta = (ja.get('last_tick') or {}).get('ts')
tb = (jb.get('last_tick') or {}).get('ts')
if tb and (not ta or tb >= ta):
    out['last_tick'] = jb.get('last_tick')
elif ta:
    out['last_tick'] = ja.get('last_tick')
assert isinstance(out.get('last_tick'), dict), 'last_tick not dict'
dump_mirror(p, out, blob(1, p) if b':' in blob(1, p) else a)
print(f"  {p}: launches union {len(la)}+{len(lb)} -> {len(out['launches'])} (cap50 asc); last_tick {ta} vs {tb} -> kept {out['last_tick'].get('ts')}")

# ---- 3. REPORT-20260926.md: take-new by generated ts (r265 format-norm law) ----
p = 'results/post_review/REPORT-20260926.md'
a, b = blob(2, p), blob(3, p)
import re
ga = re.search(rb'\xe7\x94\x9f\xe6\x88\x90 (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', a)
gb = re.search(rb'\xe7\x94\x9f\xe6\x88\x90 (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', b)
ta, tb = ga.group(1).decode(), gb.group(1).decode()
winner = b if tb > ta else a
side = 'theirs(bm-b)' if tb > ta else 'ours(bm-a)'
open(p, 'wb').write(winner)
print(f'  {p}: take-new {side} (ours_gen={ta} theirs_gen={tb}; post-rebase producer re-derive follows)')
print('RESOLVED 3/3')
