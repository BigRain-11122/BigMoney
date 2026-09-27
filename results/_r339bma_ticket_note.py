# _r339bma_ticket_note.py -- append r339 preflight note to T-91 ticket.
# v2 FIX: r338 law says probe the BLOB (not worktree) first -- blob is pure LF no-trailing-NL;
# v1 spliced off the CRLF worktree tail with b[:-2] leaving a bare CR + whole-file churn.
# v2 rebuilds from blob bytes: blob_tail + ',' + LF + new key line + LF + '}' (byte-exact).
import json
import subprocess

p = r'fleet\tasks\T-2026-09-27-91-P1.json'
blob = subprocess.run(['git', 'show', 'HEAD:' + p.replace('\\', '/')],
                      capture_output=True).stdout
assert blob.endswith(b'standing."\n}'), 'blob anchor mismatch'
assert b'\r' not in blob, 'blob expected pure LF'
note = ('r339 bm-a LAUNCH-EVE PREFLIGHT all green (s1/s2/s4 armed-verified, zero changes needed): '
        '(1) anchor artifacts confirmed on-disk: results/rev_osc_live/SIG-2026-09-24.json + BARS-2026-09-24.json '
        '(bm-b exported 09:52 today per r308 MSG chain); (2) harness selftest 12/12 legs PASS on post-rebase tree; '
        '(3) prod run rc=0 idempotent (marks at lane cutoff 09-24 no-op); (4) both accounts armed 1M CNY, '
        'entries=0 CORRECT (entry-day bars arrive with BARS-2026-09-28 Monday evening via bm-b export; '
        'first cohort = SIG-2026-09-24 Top10 entries at 09-28 open, T+1 causality), daily_scorecard '
        'system_v1_face discloses pending_cohorts=1 armed-pending honesty; (5) report faces (daily_scorecard '
        '+ town GM-office + 10-31 bench rows) re-verified rendering this round; (6) Monday sequence locked: '
        'bm-b S6 panel update -> BARS-2026-09-28 git push -> bm-a S6 sysv1 leg consumes -> first marks '
        'auto-flow to all three report faces; s3 stays auto-fire zero manual action. NEXT: Monday evening '
        'first marks + J1 observation face activation; 10-01 month trio standing.')
new = blob[:-2] + b',\n "progress_r339_bma": ' + json.dumps(note, ensure_ascii=False).encode('utf-8') + b'\n}'
json.loads(new.decode('utf-8'))  # validity gate before write
open(p, 'wb').write(new)
print('written from blob, json valid, size', len(new))
