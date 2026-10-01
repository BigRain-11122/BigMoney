import json, sys

PATH = 'results/runnable_pool.json'
raw = open(PATH, encoding='utf-8', newline='').read()
orig = raw

def must(cond, msg):
    if not cond:
        print('FAIL-CLOSED:', msg)
        sys.exit(1)

# --- Edit 1: shard status waiting -> done (W14 shard anchored by its checkpoint path) ---
NL = '\r\n'
i = raw.find('"id": "TRIAL-LABOR-W14-GENERATE"')
must(i >= 0, 'W14 entry not found')
j = raw.find('"checkpoint": "results/trial_labor_w14/w14_candidates.json', i)
must(j >= 0, 'W14 shard checkpoint not found')
# status line immediately precedes the checkpoint line
anchor1 = '"status": "waiting",' + NL + '"checkpoint": "results/trial_labor_w14/w14_candidates.json'
must(raw.count(anchor1) == 1, 'anchor1 not unique: %d' % raw.count(anchor1))
raw = raw.replace(anchor1, '"status": "done",' + NL + '"checkpoint": "results/trial_labor_w14/w14_candidates.json')

# --- Edit 2: shard park_note append + done_at (mirror r138 W2 harvest shape) ---
anchor2 = '(FB-004 fire-declared)"' + NL + '}'
must(raw.count(anchor2) == 1, 'anchor2 not unique: %d' % raw.count(anchor2))
repl2 = ('(FB-004 fire-declared) | r527 bm-a harvest-facts append: burn ran to completion 17:28:17 under r526 ignite '
         '(shard-layer r493 re-arm verdict; entry-layer r494/r504 governance park not re-verified before ignition -- conflict disclosed), '
         'raw 10000 -> dedup 293 (fp 386 + corr 331), ZERO engine cells, trials ledger untouched (N=0 still held); '
         'single-shot product present = refuse-if-exists guard active + same-grammar rerun FORBIDDEN (sec.4) = double no-rerun",'
         + NL + '"done_at": "2026-10-01T17:28:17+08:00"' + NL + '}')
raw = raw.replace(anchor2, repl2)

# --- Edit 3: entry park_note append (shared-verdict pattern, attributed segment) ---
anchor3 = 'burn killed at dedup 7750/10000 pre-product, N=0 held"'
must(raw.count(anchor3) == 1, 'anchor3 not unique: %d' % raw.count(anchor3))
repl3 = ('burn killed at dedup 7750/10000 pre-product, N=0 held | r527 bm-a segment (harvest round, post-completion facts): '
         'r526 ignite completed 17:28:17 (595.4s, pre-kill window elapsed) -> w14_candidates.json n=293 + TRIAL_GRAMMAR_LEDGER row a231bf10940e7878 '
         'committed as consumed-grammar inventory (grammar consumed is a fact; deletion would falsify state; zero engine cells = trial-gate N=0 held); '
         'shard flipped done on work-completion facts (W2 r138 harvest precedent); ENTRY PARK HONORED: screen/judge legs NOT started, '
         'no new prereg, supply line stays parked pending sec-4 self-proof OR GM dual-ruling (MSG-20261001-0400 thread); '
         'inter-machine verdict conflict (r526 STALE-ruling vs r494/r504 park) disclosed to bm-b + GM via MSG-20261001-173x"')
raw = raw.replace(anchor3, repl3)

# typo guard: fix the intentional-ish label
raw = raw.replace('ENTRY PARK HONRED', 'ENTRY PARK HONORED')

must(raw != orig, 'no changes applied')
json.loads(raw)  # parse self-proof
open(PATH, 'w', encoding='utf-8', newline='').write(raw)
print('OK: 3 surgical edits applied, json.loads PASS, bytes', len(orig), '->', len(raw))
