"""r780 bm-b P0 surgery: re-queue FUND-VALUE-P1-NULLS pool entry (done->ready).

Laws applied: pit-pool-edit.md r509/r500 (raw-text anchored, no json
re-serialization), r694 (needle anchored on entry id region), r629
(trailing comma fix on field deletion), r678/r705 (reparse + count
assertions + diff --stat surgical check), treasure_guard restore rc0
(reproducible-artifact class, passed this round).

Forensic basis (this round, _r780bmb_forensic.py): r779 17-UU rebase
resolve window dropped 14 live-appended rows from nulls.jsonl (r630
family) -- commit snapshots monotone 1877->1986 with zero removals,
runner log DONE 2000/2000 exit 0, current tree == c748e61c6 face.
Cure = re-queue so the daemon re-ignites; runner done-key skip burns
only the 14 missing ks deterministically (rng([20500000,k])).
"""
import json, subprocess, sys

POOL = 'results/runnable_pool.json'
ID_N = '"FUND-VALUE-P1-NULLS"'

raw = open(POOL, encoding='utf-8', newline='').read()
n_lines_before = raw.count('\n')

# ---- r694: anchor on the V entry id, then work strictly inside its block
i = raw.find(ID_N)
assert i > 0, "V entry id not found"
j = raw.rfind('{', 0, i)
depth = 0; k = j
while k < len(raw):
    if raw[k] == '{':
        depth += 1
    elif raw[k] == '}':
        depth -= 1
        if depth == 0:
            break
    k += 1
block = raw[j:k+1]
assert '"runner": "scripts/fund_value_p1.py"' in block, "block sanity"

lines = block.split('\r\n')
assert len(lines) > 10, "block too small -- EOL probe mismatch (host is CRLF)"

# ---- pass 1: flip both status fields done -> ready (exactly 2 expected)
status_idx = [n for n, l in enumerate(lines)
              if l.strip() == '"status": "done",']
assert len(status_idx) == 2, f"expected 2 status lines, got {len(status_idx)}"
for n in status_idx:
    lines[n] = lines[n].replace('"done"', '"ready"')

# ---- pass 2: delete harvest/ownership fields (8 lines expected)
DEL_PREFIXES = ('"owner":', '"owner_since":', '"claimed_since":',
                '"done_at":', '"harvested_by":', '"harvest_claim":',
                '"done_by":')
deletes = [n for n, l in enumerate(lines)
           if l.strip().startswith(DEL_PREFIXES)]
assert len(deletes) == 8, f"expected 8 own-field lines, got {len(deletes)}: {deletes}"
for n in deletes:
    lines[n] = None
lines = [l for n, l in enumerate(lines) if n not in set(deletes)]

# ---- pass 3: trailing comma fixes (r629)
# shard: note line is now the last shard field before its closing brace
note_idx = [n for n, l in enumerate(lines)
            if l.strip().startswith('"note":')]
assert len(note_idx) == 1, f"expected 1 note line, got {len(note_idx)}"
nn = note_idx[0]
assert lines[nn].rstrip().endswith('",'), "note line tail unexpected"
assert lines[nn + 1].strip() == '}', "line after note must close the shard"

# append re-queue provenance to the note (before the closing quote+comma)
PROV = (" | rel-bm-b-r780 2026-10-06: re-queue surgery -- r779 17-UU rebase "
        "resolve window dropped 14 live rows (r630 family forensics: commit "
        "snapshots monotone 1877->1986 zero-removal, runner DONE 2000/2000 "
        "exit 0, tree rewound to c748e61c6 face); re-ignition via done-key "
        "skip todo=14 deterministic rng([20500000,k])")
lines[nn] = lines[nn].rstrip()[:-2] + PROV + '",'
# note line is last field -> strip its trailing comma
lines[nn] = lines[nn].rstrip()[:-1]  # drop the ',' -- now ends with '"'

# entry: host_gates close "]," is now the last field before entry close.
# positional law: the LAST '}' line of the block is the entry close; the
# line immediately before it (after done_by/done_at deletion) is the
# host_gates '],' (runner_args also closes with '],' -- never match by
# stripped content alone).
close_idx = max(n for n, l in enumerate(lines) if l.strip() == '}')
prev = close_idx - 1
assert lines[prev].strip() == '],', f"unexpected pre-close: {lines[prev]!r}"
lines[prev] = lines[prev].rstrip()[:-1]  # '],' -> ']'

new_block = '\r\n'.join(lines)

# ---- pass 4: reparse the block, verify shape
parsed = json.loads(new_block)
assert parsed['status'] == 'ready'
assert parsed['shards'][0]['status'] == 'ready'
sh = parsed['shards'][0]
for f in ('owner', 'owner_since', 'claimed_since', 'done_at',
          'harvested_by', 'harvest_claim'):
    assert f not in sh, f"shard still has {f}"
for f in ('done_by', 'done_at'):
    assert f not in parsed, f"entry still has {f}"
assert 'r780' in sh['note']
assert parsed['runner'] == 'scripts/fund_value_p1.py'
assert parsed['workers_plan']['workers'] == 32

# ---- write back
new_raw = raw[:j] + new_block + raw[k+1:]
assert new_raw.count('\n') == n_lines_before - 8, \
    f"line delta {new_raw.count(chr(10)) - n_lines_before} != -8"
pool = json.loads(new_raw)          # whole-file reparse gate
assert len(pool['entries']) == 403  # entry count unchanged
v = [e for e in pool['entries'] if e['id'] == 'FUND-VALUE-P1-NULLS'][0]
assert v['status'] == 'ready' and v['shards'][0]['status'] == 'ready'
# Q/D untouched
q = [e for e in pool['entries'] if e['id'] == 'FUND-QUALITY-P1-NULLS'][0]
d = [e for e in pool['entries'] if e['id'] == 'FUND-DIVLOWVOL-P1-NULLS'][0]
assert q['status'] == 'ready' and d['status'] == 'ready'
assert q['shards'][0].get('owner') == 'bm-b'   # alive-claim face intact

with open(POOL, 'w', encoding='utf-8', newline='') as fh:
    fh.write(new_raw)

print("SURGERY OK: V entry re-queued (shard ready + entry ready, "
      "8 field lines removed, note provenance appended)")
print("reparse entries:", len(pool['entries']))
