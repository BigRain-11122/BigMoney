# -*- coding: utf-8 -*-
# r924 bm-a closeout: state heal 920->924 (dead-session chain r921-r923 never
# wrote state/reports; origin commits carry the lineage), C7ORDSHA SHA-1 pin
# execution, heartbeat refresh, E51 methodology card append, round report line.
import json, io, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

NOW = '2026-10-09T19:36:30+08:00'
EPOCH = int(time.time())
ORIGIN_TIP = 'e2187e483'

# 1) state heal
st = json.load(io.open('state-bm-a.json', encoding='utf-8'))
notes = st.get('notes', '')
st['round_no'] = 924
st['round'] = 924
st['loop_round'] = 924
st['last_round'] = 920  # last CLOSED round in state lineage; r921-r923 = dead unclosed sessions (origin commits carry their work)
st['last_round_at'] = '2026-10-09T16:38:09+08:00'
st['last_round_closed'] = NOW
st['last_round_ts'] = NOW
st['now_active'] = 'r924 closing: dead-estate absorb (W201 finalize landed 856,545/K440,120) + W202 seat published (A 459_204..461_203 + B 461_204..461_403 staircase SIXTY-SECOND)'
st['current'] = st['now_active']
st['current_task'] = 'r925: W202 five-face freeze window (seat law <=24h; post-W201 re-derive + own-A reservation W141/E36); sina 10-09 bar late watch self-heal; PARKING-P1 burn due 10-14 12:00 (O-20261009-1105)'
st['task'] = st['current_task']
st['next'] = st['current_task']
st['next_milestone'] = 'r925: W202 five-face freeze + ignition chain; PARKING-P1 burn due 10-14 12:00'
st['did'] = 'r924: S0 dead-estate absorb rebase (87 origin commits, 10 UU take-newer/union zero-loss) + W201 finalize product LANDED (ledger 854,345+2,200=856,545 EXACT, K=440,120, skill 1.1885, push b71610ba4) + W202 seat published (push e2187e483) + C7ORDSHA adjudication executed (ORD sha -> SHA-1 pin 40-hex)'
st['last_action'] = 'r924 closeout: estate closed + W202 seat published; delivery 0/0'
st['last_artifact'] = 'r924 products: results/perpetual_faces/n1_w201_results.json (1,288,095B, ledger 856,545) + results/_r924bma_w202_probe.py + _r924bma_w202_probe_receipt.json (rc0 ADMIT) + fleet/inbox/MSG-2026-10-09-1935-bma-w202-seat.md (published origin e2187e483)'
st['latest_artifact'] = st['last_artifact']
st['verify'] = 'green (r924: W201 finalize product landed 856,545/K440,120 + W202 seat published; smoke 49/49; watermark green; engine ALIVE; attrition CLEAN; push self-verified 0/0; C7ORDSHA SHA-1 pin executed)'
st['verdict'] = st['verify']
# C7ORDSHA adjudication execution: ORD watermark key -> SHA-1 ALGORITHM PIN (r537)
st['last_orders_sha'] = '0a1d9c1d4a77fd02177f49044bd117f6183fa462'
st['ord_sha_method'] = 'python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; C7ORDSHA adjudication MSG-20261009-173x executed r924; prior 64-hex key was SHA-256 base, algorithm fork per science_audit C7 finding)'
st['last_orders_seen'] = 'r924 S0.5 scan: ORD delta consumed (sha256 e6a6fa38 -> pinned sha1 0a1d9c1d) -- 10-09 17:1x-19:0x new rows scanned: all BigMoney-relevant legs previously executed (C-03 bm-a workspace audit PASS / H3 bm-a leg closed 19:0x prior window / FleetLink v1.1-1.2 bm-a live / fleet-memory-sync seeded 64); zero new action'
st['last_orders_at'] = NOW
st['last_orders_ts'] = NOW
st['last_decisions_sha'] = '31e85972112d836e4e70daf55ac9bf2d07f64be9bc74efd516dd8b0961ec1514'
st['last_decisions_seen'] = 'r924 S0.5 scan: DEC delta consumed -- new content = C-20261009-01/02/03 council rows (all landed+executed prior windows; C-03 bm-a face = workspace audit PASS); zero new action'
st['last_decisions_at'] = NOW
st['last_decisions_ts'] = NOW
st['clock_read'] = NOW
st['ts'] = NOW
st['updated'] = NOW
st['last_run'] = NOW
st['last_seen'] = NOW
st['heartbeat_epoch_utc'] = EPOCH
st['last_heartbeat_epoch_utc'] = EPOCH
st['idle_rounds'] = 0
st['agenda_starved'] = False
st['orphan_faces'] = 0
st['push_verified'] = {'ts': NOW, 'origin_tip': ORIGIN_TIP, 'ahead_behind': '0/0',
                       'note': 'r924 seat+estate push self-verified post-push fetch+rev-list'}
st['sync'] = st['push_verified']
if 'r924' not in notes:
    st['notes'] = notes + (' r924: state heal 920->924 -- dead-session chain r921/r922/r923 all died pre-closeout '
                           '(r921 landed W200 freeze cd92a8d9c/finalize 5c46e49bb/W201 seat 188ebe647 on origin; '
                           'r922 died pre-commit at W201 freeze receipt 18:41; r923 absorbed r922 estate c1937ac47 '
                           '+ burn products 1496962d6 + generated W201 finalize 19:05:50 but died pre-commit) -- '
                           'successor r924 absorbed unlanded faces + verified + landed (r899/r941 lineage); '
                           'sequence honest per origin commit evidence, report lines jump 920->924 with this disclosure.')
json.dump(st, io.open('state-bm-a.json', 'w', encoding='utf-8', newline=''),
          ensure_ascii=False, indent=1)
v = json.load(io.open('state-bm-a.json', encoding='utf-8'))
assert isinstance(v['heartbeat_epoch_utc'], int), 'epoch not int'
assert len(v['last_orders_sha']) == 40, 'ORD sha not 40-hex SHA-1'
print('state healed 920->924; ORD sha1 pin', v['last_orders_sha'][:16], 'epoch int OK')

# 2) heartbeat
hb = json.load(io.open('fleet/machines/bm-a.json', encoding='utf-8'))
hb['last_seen'] = NOW
hb['ts'] = NOW
hb['clock_read'] = NOW
hb['heartbeat_epoch_utc'] = EPOCH
hb['current_task'] = st['current_task']
hb['cpu_cores'] = 32
hb['free_ram_gb'] = 31.8
hb['free_vram_gb'] = 1.7
hb['verdict'] = st['verify']
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
json.dump(hb, io.open('fleet/machines/bm-a.json', 'w', encoding='utf-8', newline=''),
          ensure_ascii=False, indent=1)
h = json.load(io.open('fleet/machines/bm-a.json', encoding='utf-8'))
assert isinstance(h['heartbeat_epoch_utc'], int), 'hb epoch not int'
print('heartbeat refreshed; orders_ack count', len(h.get('orders_ack', [])), '(diff-set 0 this window)')

# 3) E51 methodology card
card = ('\n- **E51 rebase UU 双向 take-newer 解算法（origin 侧可更新·胜者完整性单边断言）**：proven·工程面（死会话链 r921-r923 场景）：rebase UU 冲突面的 deep-ts take-newer 必须双向比较（r918 正典只断言 mine-newer——死会话链下 origin 侧（他窗/他 session 的更新快照）可更新：本窗实锚=attrition 快照 origin 19:16:55 > mine 18:58:16、dashboard_status origin 18:55:28 > mine 18:33:21）——正法=逐面取 ts 更新一侧，断言只打在胜者完整性上（attrition 胜者必须 rc0+active_loss=False，与哪侧无关）；compute_audit 滚动史照旧 full-json dedupe UNION 零丢失、token_usage 照旧 per-machine sections union newer-wins。证据：results/_r924bma_resolve_rebase.py 10 面 10/10 断言过（attrition/dashboard.js take-THEIRS + 其余 take-MINE/UNION）。\n- 2026-10-09 19:3x·bm-a r924（死会话遗产收口步·O-20261002-2100 捕获律）·单获例 append E51 rebase UU 双向 take-newer 解算法（live 实证：rebase b71610ba4 前身 5d1c6b089 十面全断言过）。\n')
with io.open('knowledge/METHODOLOGY_ASSETS.md', 'a', encoding='utf-8', newline='') as f:
    f.write(card)
print('E51 card appended')

# 4) round report line
line = ('2026-10-09T19:36:30+08:00 | r924 | dead-session estate takeover r921/r922/r923 (r899/r941 lineage): '
        'S0 absorb+rebase 87 origin commits (10 UU canon-resolved take-newer/union zero-loss, _r924bma_resolve_rebase.py; '
        'E42 writer-pause window x4 tasks) + W201 FINALIZE PRODUCT LANDED (n1_w201_results.json 1,288,095B: ledger '
        '854,345+2,200=856,545 EXACT, merged pool K=440,120 EXACT, skill_line_v2 1.1885, 12/12 shards, evidence_cutoff '
        '2026-09-22, finalize product generated by dead r923 19:05:50 -- absorbed, verified shape-complete, push b71610ba4) '
        '+ r921/r923 S6 chain receipts absorbed (38/38 rc0 both, r923 18:57:58-19:06:50 bad_legs NONE) | '
        'W202 SEAT CHAIN WINDOW OPENED: pre-seat probe rc0 ADMIT 5 legs (A 459_204..461_203 staircase SIXTY-SECOND hops=1 '
        '+ B 461_204..461_403 same-freeze mutual exclusion hops=1; full universe conflict scan 0; origin vacancy verified; '
        'anchor W201 finalize actuals 856,545/K440,120 per r590 zero roll-forward) + seat MSG published=reserved on origin '
        'e2187e483 (MSG-2026-10-09-1935-bma-w202-seat.md; bm-a 117th own wave 192nd engine wave) | '
        'S0.5: ORD delta consumed zero-action (10-09 17:1x-19:0x rows all prior-executed: C-03 bm-a face PASS / H3 bm-a '
        'leg closed / FleetLink v1.1-1.2 / memory-sync seeded) + C7ORDSHA adjudication EXECUTED (ORD watermark key 64-hex '
        'SHA-256 -> SHA-1 40-hex ALGORITHM PIN r537 = 0a1d9c1d4a77fd02..., ord_sha_method field aligned with bm-c; DEC '
        'delta = C-01/02/03 council rows all prior-consumed) | S1 smoke 49/49 PASS | watermark green (red=false, '
        'next_pick=claimed moneyflow panel self-heal) | engine ALIVE idle (108 shards total, queue 0) | sina 10-09 bar '
        'STILL ABSENT (update_daily retry 19:32 = 0 new rows cutoff 10-08, source-side lag honest no-op; full chain '
        'deferred -- all legs would no-op identically; bar watch next round self-heal) | state heal 920->924 (dead chain '
        'r921/r922/r923 zero state/report writes -- origin commits carry lineage, sequence honest per commit evidence; '
        'report lines jump 920->924 with this disclosure) | E51 card appended (bidirectional take-newer) | '
        'orphan_faces=0; attrition CLEAN (4 files, healed shrink rows noted); idle --worked 0 (substantial work exempt, '
        'VRAM 1.7GB busy face) | artifact: n1_w201_results.json + _r924bma_w202_probe.py/receipt + seat MSG | '
        'next: r925 W202 five-face freeze window (seat law <=24h); PARKING-P1 burn due 10-14 12:00 | [r924 bm-a]\n')
with io.open('round_reports-bm-a.md', 'a', encoding='utf-8', newline='') as f:
    f.write(line)
print('report line appended')

# 5) verify local-vs-origin commit count for the report metric
import subprocess
ahead = subprocess.run(['git', 'rev-list', '--count', 'main', '^origin/main'],
                       capture_output=True).stdout.decode().strip()
print('ahead of origin:', ahead)
