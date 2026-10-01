# r509: STOCK_FACE_FURNACE_P1 real ledger append (MSG-20261001-1432 fulfillment)
# Truth: r506's "ledger 380,320" was a PHANTOM -- stock_face_furnace.py
# cmd_finalize called sg.append_ledger (dict-returning, no disk write), printed
# the block, and wrote only the .ledger_appended guard. The 281 trials never
# entered the chain (discovered r509 via full-tree scans: no block exists in any
# results JSON on local or origin). bm-c's MSG-1432 asked for a data-driven
# re-derive at the new chain head; the honest execution of that request is this
# FIRST-TIME real append at the current head (bm-a's LOWAMP-P2 = 386,267),
# persisting the block into mom_summary.json (the family whose finalize
# triggered the single-shot append), exactly as the r509 runner fix will do
# for any future furnace batch.
import sys, json, subprocess
sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import science_gates as sg

SP = 'results/stock_face_furnace/mom_summary.json'
raw = open(SP, 'rb').read()
head_before = int(sg.ledger_head()['total'])
assert head_before == 386267, f"unexpected head {head_before}"

block = sg.append_ledger(
    "STOCK_FACE_FURNACE_P1", 281, "stock_face_furnace/mom_summary.json",
    note="T-139 akshare-face exploration furnace (281 cells; supply=trial "
         "stock grammar). r509 real append: r506 block was phantom "
         "(guard-marker-only, never persisted); appended here at data-driven "
         "head per MSG-20261001-1432 re-derive request.",
    evidence_cutoff="2026-09-30")
print("block:", json.dumps(block, ensure_ascii=False)[:220])

d = json.loads(raw.decode('utf-8-sig'))
assert 'trials_ledger' not in d, "block already present -- refuse double-append (pit-95)"
assert d['n_cells'] == 16 and d['family'] == 'mom', "unexpected summary shape"
d['trials_ledger'] = block

# format probe: mirror the runner's _dump shape (indent=1 + trailing newline
# convention used by this family's products; verified against raw bytes)
probe_indent = 1
open(SP, 'wb').write((json.dumps(d, ensure_ascii=False, indent=probe_indent) + '\n')
                     .encode('utf-8'))

# gates: parse-verify + head advanced + surgical diff
json.load(open(SP, encoding='utf-8-sig'))
after = sg.ledger_head()
print("ledger head after:", after.get('total'), after.get('file'))
assert int(after['total']) == 386267 + 281 == 386548, "chain must advance by exactly 281"
r = subprocess.run(['git', 'diff', '--stat', '--', SP], capture_output=True)
print("diff:", r.stdout.decode().strip().splitlines()[-1])
lines = r.stdout.decode().strip()
import re
m = re.search(r'(\d+) insertion', lines)
assert m and int(m.group(1)) <= 15, "non-surgical diff on mom_summary.json"
print("REAL APPEND OK: 386,267 -> 386,548 (STOCK_FACE_FURNACE_P1 +281)")
