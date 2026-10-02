# -*- coding: utf-8 -*-
# r595 bm-b yield closeout: three-machine T-145 collision resolved per fleet README sec.4
# (commit-time order: bm-a first claimer in 6f53108b7, bm-c delivered slice (a) on the data
# holder in 5d234b3d7, bm-b 21:24:30 local claim = last -> yield). Unpushed local faces only:
# zero external visibility. 1) rewrite ledger line honestly 2) revert ticket to origin + yield
# record 3) delete duplicate probe + moot dispatch 4) heartbeat orders_ack += O-2124.
import io
import json
import os
import subprocess

def run(args):
    return subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')

# 1) ticket: restore origin version then append yield record (pure addition, r483 precedent)
r = run(['git', 'checkout', '--', 'fleet/tasks/T-2026-10-02-145-P1.json'])
assert r.returncode == 0, r.stderr
with io.open('fleet/tasks/T-2026-10-02-145-P1.json', 'r', encoding='utf-8') as f:
    tk = json.load(f)
tk['yield_record_r595_bmb'] = (
    'bm-b claimed locally 21:24:30 (uncommitted); at push the pre-push claw surfaced bm-a\'s '
    'in-flight claim (6f53108b7, committed earlier) + bm-c\'s delivered slice (a) PIT audit '
    '(5d234b3d7, statutory-date rule + structure PASS on the data holder) -> bm-b yields per '
    'sec.4 commit-time order; duplicate probe (scripts/t145_pit_audit.py, unpushed) withdrawn '
    'in favor of bm-c\'s scripts/fund_pit_audit.py avail_date single-source; bm-b lane duty '
    'remains (d) akshare-5228 furnace burns when (b)/(c) land'
)
tmp = 'fleet/tasks/T-2026-10-02-145-P1.json.tmp'
with io.open(tmp, 'w', encoding='utf-8', newline='') as f:
    json.dump(tk, f, ensure_ascii=False, indent=1)
os.replace(tmp, 'fleet/tasks/T-2026-10-02-145-P1.json')
print('ticket: origin version + yield record appended')

# 2) delete unpushed duplicate probe + moot dispatch (untracked, zero visibility)
for p in ('scripts/t145_pit_audit.py',
          'fleet/inbox/MSG-20261002-2145-bmb-t145-pit-audit-dispatch.md'):
    if os.path.exists(p):
        os.remove(p)
        print('deleted unpushed duplicate:', p)

# 3) ledger line rewrite: replace the round-595 line with the honest yield version
NEW = (
    "| 2026-10-02T21:38+08:00 | round 595 (bm-b) | WM verdict: GREEN (red=false; SatEngine alive "
    "queue 0 idle = transition window by design per O-2115 supply-priority; dualrun ZERO-DRIFT "
    "streak 39/3; watermark probe insufficient_history legal) | S0 P0 x2: unpushed r594 commit "
    "carried 9 accidental deletions of bm-a adopted-toolset estate (_r592bma_*/_r593bma_*: reset "
    "--mixed onto newer base whose NEW files never reached disk, add -A swallowed them) -> T-144 "
    "pre-push claw FIRST LIVE SAVE -> r589 unwind-FF-recommit loop #1 (restore 9 + per-face "
    "checkout 19-keep/69-origin-verbatim + execution-time rev-parse FF) -> r594 re-landed at "
    "origin 571f93927 clean; loop #2 at round close (r374 diverged-base artifact: bm-a engine "
    "batch W114 shards + bm-c PIT audit + O-2124 landed mid-round) same loop, zero deletions "
    "re-verified; pit law -> CODELY (66.4KB >50KB disclosed per r504 GM ruling, domain-split "
    "window 10-07) + METHODOLOGY_ASSETS E08 (O-2100 capture-law first bm-b live append) | "
    "PRODUCT-COLLISION-YIELD (honest): T-145 (O-2115, P1 immediate) three-machine collision -- "
    "bm-a first claimer (6f53108b7, in-flight), bm-c DELIVERED slice (a) PIT audit on the data "
    "holder (5d234b3d7: statutory availability rule Q1->04-30/H1->08-31/Q3->10-31/FY->next-04-30 "
    "+ structure PASS 5225 syms + lookahead lags median 46/62/120d + 4 nonperiod-key flags), "
    "bm-b local claim 21:24:30 = last -> YIELDED per sec.4; my parallel probe "
    "(t145_pit_audit.py, selftest 17/17, unpushed) withdrawn as duplicate, bm-c "
    "fund_pit_audit.py avail_date = single-source rule; bm-b lane duty stands: (d) akshare-5228 "
    "furnace burns when (b) unlock eval + (c) family preregs land on bm-a's coordination | S6 "
    "33 legs rc0 (Golden Week no-new-bar paper block honest skip); smoke 47/47; attrition guard "
    "CLEAN; orders 146/146 (O-2100+O-2115+O-2124 acked; O-2124=bm-c->bm-a City3D residents "
    "order, no bm-b duty); W115 seat broadcast processed (no action, N1 deprioritized per "
    "O-2115); D-19 honest skip r481 special | N=0 unreached-origin (571f93927 verified at "
    "origin; this round rides next push) | NEXT: (b)/(c) on bm-a ticket ownership; bm-b = lane "
    "(d) burns + astock panel freshness (dept: strategy/research/data) |"
)
p = 'logs/iteration-loop/round_reports.md'
b = io.open(p, 'rb').read()
old_line = None
lines = b.split(b'\r\n')
for i, ln in enumerate(lines):
    if b'round 595 (bm-b)' in ln:
        old_line = i
        break
assert old_line is not None, 'round-595 ledger line not found'
lines[old_line] = NEW.encode('gbk')
io.open(p, 'wb').write(b'\r\n'.join(lines))
print('ledger line rewritten (yield version)')

# 4) heartbeat: orders_ack += O-20261002-2124-bm-c.md; task/verdict refresh (r583 law)
with io.open('fleet/machines/bm-b.json', 'r', encoding='utf-8') as f:
    hb = json.load(f)
ack = hb.get('orders_ack', [])
new = [o for o in ('O-20261002-2100-bm-c.md', 'O-20261002-2115-bm-c.md', 'O-20261002-2124-bm-c.md')
       if o not in ack]
hb['orders_ack'] = ack + new
hb['current_task'] = ("T-145 yielded to bm-a (first claimer) + bm-c slice (a) delivered; bm-b lane "
                     "duty = (d) akshare-5228 furnace burns when (b)/(c) land; astock panel fresh")
hb['verdict'] = ("round 595 ok: S0 surgery x2 healed r594 deletions (claw first live save) + "
                 "re-landed at origin; T-145 collision yielded honestly; E08 law+card; S6 33 rc0; "
                 "smoke 47/47")
tmp = 'fleet/machines/bm-b.json.tmp'
with io.open(tmp, 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
os.replace(tmp, 'fleet/machines/bm-b.json')
with io.open('fleet/machines/bm-b.json', 'r', encoding='utf-8') as f:
    chk = json.load(f)
print('heartbeat orders_ack=%d epoch_int=%s' % (len(chk['orders_ack']),
                                                isinstance(chk['heartbeat_epoch_utc'], int)))
