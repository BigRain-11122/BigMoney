# r486 bm-b S0: rebuild shared runnable_pool.json surgically = new-HEAD text + r485 leave-behind 12 N1-W2 entries
# law: r289 (probe indent/CRLF, surgical diff assertion), r283/r485 leave-behind close-out
import json, subprocess, os, sys

head_txt_bytes = subprocess.check_output(['git', 'show', 'HEAD:results/runnable_pool.json'])
head_txt = head_txt_bytes.decode('utf-8-sig')
mine_txt = open(os.path.join(os.environ['TEMP'], 'r486_pool_mine.json'), encoding='utf-8-sig').read()

head = json.loads(head_txt)
mine = json.loads(mine_txt)

head_ids = [e['id'] for e in head['entries']]
mine_ids = [e['id'] for e in mine['entries']]
new_entries = [e for e in mine['entries'] if e['id'] not in set(head_ids)]
assert len(new_entries) == 12, f'expected 12 new N1 entries, got {len(new_entries)}: {[e["id"] for e in new_entries]}'

# top-level diff face (excluding entries): only updated_at expected
top_diffs = []
for k in mine:
    if k == 'entries':
        continue
    if k not in head:
        top_diffs.append(('added-key', k))
    elif mine[k] != head[k]:
        top_diffs.append(('changed', k))
print('top-level diffs mine vs new-HEAD:', top_diffs)

out = dict(head)  # preserve new-HEAD key order
out['entries'] = head['entries'] + new_entries  # append at end (positions 164-175, same as r485 intent)
for kind, k in top_diffs:
    if kind in ('added-key', 'changed'):
        out[k] = mine[k]

# ascii check on both faces
head_has_raw_nonascii = any(ord(c) > 127 for c in head_txt)
mine_has_raw_nonascii = any(ord(c) > 127 for c in mine_txt)
head_has_uesc = '\\u' in head_txt
print('HEAD raw-nonascii:', head_has_raw_nonascii, 'HEAD has \\u escapes:', head_has_uesc, '| MINE raw-nonascii:', mine_has_raw_nonascii)

ensure_ascii = bool(head_has_uesc and not head_has_raw_nonascii)
txt = json.dumps(out, ensure_ascii=ensure_ascii, indent=2)
if '\r\n' not in head_txt and '\n' in head_txt:
    pass  # LF file: write as-is
else:
    txt = txt.replace('\n', '\r\n')
with open('results/runnable_pool.json', 'w', newline='', encoding='utf-8') as f:
    f.write(txt)
print('written. ensure_ascii =', ensure_ascii)

# semantic assertion: entries == HEAD 164 + 12
chk = json.loads(open('results/runnable_pool.json', encoding='utf-8-sig').read())
assert len(chk['entries']) == 176
assert chk['entries'][:164] == head['entries']
assert chk['entries'][164:] == new_entries
print('semantic assertions OK: 164 HEAD + 12 N1 = 176')
