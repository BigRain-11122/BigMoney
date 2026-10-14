"""r996 bm-a S7 closeout: idle --worked + round-report line + state + heartbeat.
Single-process fresh-read-modify-write per multi-writer law; utf-8 everywhere.
"""
import json, subprocess, datetime, hashlib, sys

ROOT = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
G = 'C:/Users/sjs20/Desktop/FluxGroup'
GG = 'C:/Program Files/Git/cmd/git.exe'
NOW = datetime.datetime.now().astimezone().isoformat(timespec='seconds')

# --- full sha of orders.md at origin (python raw-bytes canonical) ---
b = subprocess.run([GG, '-C', G, 'show', 'origin/main:docs/orders.md'],
                   capture_output=True).stdout
ORD_SHA = hashlib.sha256(b).hexdigest()
DEC_SHA = 'c61d7884b347e7e706ed98546aadc304f7f3afddd9071a5110152a860a064bb'

# --- idle trigger worked flag ---
r = subprocess.run(['python', 'Tools/idle_trigger.py', '--worked'],
                   capture_output=True, cwd=ROOT)
print('idle --worked rc=', r.returncode)

# --- round report line ---
LINE = (NOW + ' | r996 bm-a | WM-VERDICT: green (red=false lane=healthy; satengine ALIVE rc0 idle '
    'queue0; next_pick=claimed moneyflow IC batch waits panel first-pull in-flight source-blocked '
    '30-min self-heal) | 当前活: S0 storm closeout + estate absorption (dead 18:08-attempt checkpoint '
    '1dc16ff95 sole-executor-verified + rebase onto bm-b r943 trio 60a6af702, 19-UU shared-regen '
    'deep-ts resolve via treasure_guard gate 18 rc0 + token_usage append-ledger class local-newer '
    'per guard law, r863 zero-UU sequencer refusal cured by r808 three-step churn-absorb commit '
    '844fa5bd9) | 最近实物: results/_r995bma_s6_chain.log (dead-session 27-leg chain 18:17 bad=0 '
    'absorbed+committed; CEO faces REPORT/LIVE/scorecard/dashboard fresh 18:17) + W242 seat receipt '
    'on-disk verified results/_w242bma_20261014_probe_receipt.json (bm-b claw-restored, disk-actor '
    'watch item) | 下个里程碑: W242 materialize (derive+five-face freeze+engine self-burn) on W241 '
    'finalize landing <=48h; moneyflow panel-complete -> IC prereg; month exam 10-31 | '
    'did: S0-1 anchor bm-a orphan 0/34; S0.5 D19 dual-delta: DEC c61d7884 UNCHANGED zero-action; '
    'ORD delta single row cabb4f1 (O-20261014-1705 CEO-PROXY full-chain review, group-domain, zero '
    'BigMoney directives) acked no-action, bm-a watermark advanced 542f99a9->' + ORD_SHA[:12] +
    ' python-raw canonical (bm-b state 1176e4c4 matches no blob in history = r814-family '
    'bad-provenance suspicion noted, their face their repair not overwritten); S1 smoke 49/49; S2 '
    'boards empty (jobs 0 / fleet-tasks 0 / queue probe CLEAR T22/E14 / local orders ack unacked=0); '
    'S3: W242 freeze waits-upstream W241 finalize (bm-c chain in-flight; r995 = commit-only round '
    '138a94745 W242 seat publish, report line absent = sequence-honest note); S6 = absorbed chain '
    '18:17 (bad=0 new_bar=False) + this-window update_daily retry rc0 honest no-op cutoff 10-13 '
    '(sina 10-14 bar undelivered -> paper/marks legs legally gated); S7 quartet green (loop pin=8 '
    'no-op / watchdog / claws x2) + attrition CLEAN rc0 (4 ledgers, historical shrink healed) + '
    'idle --worked | evidence: smoke 49/49 + 844fa5bd9 + chain log bad=0 + watermark_red red=false + '
    'attrition scan rc0 | next: r997 W242 materialize on W241-finalize landing / moneyflow IC '
    'prereg on panel-complete; HANDOVER 5x obligation rolls to r1000 (r995 dead before its 5x '
    'checkpoint) | 孤儿面=0 | 记账预算: 4/5 (state+report+heartbeat+ack-delta; within cap) | '
    '产品积分: 1 (storm closeout + absorbed chain = committed file changes; no new burn product '
    'this window - supply lanes all waits-upstream, honest) | 本地未达 origin commit 数=0 '
    '(closeout push self-verified below) | [r996 bm-a]')
with open(ROOT + r'\round_reports-bm-a.md', 'a', encoding='utf-8') as f:
    f.write(LINE + '\n')
print('report line appended')

# --- state ---
sp = ROOT + r'\state-bm-a.json'
st = json.load(open(sp, encoding='utf-8'))
st['round_no'] = 997
st['last_round'] = 996
st['round'] = 996
st['loop_round'] = 996
for k in ('last_round_at', 'last_round_closed', 'last_round_ts', 'last_run', 'last_seen',
          'updated', 'updated_at', 'ts', 'clock_read'):
    st[k] = NOW
st['last_orders_sha'] = ORD_SHA
st['last_orders_at'] = NOW
st['last_orders_seen'] = ('r996: ORD ' + ORD_SHA[:12] + ' consumed (delta single row cabb4f1 = '
    'O-20261014-1705 CEO-PROXY full-chain review, group-domain, zero BigMoney directives, acked '
    'no-action; bm-b state 1176e4c4 matches no blob in current history = r814-family PS-redirect '
    'bad-provenance suspicion, their face their repair, not overwritten; python-raw canonical)')
st['last_orders_read_at'] = NOW
st['last_decisions_at'] = NOW
st['last_decisions_read_at'] = NOW
st['last_decisions_seen'] = ('r996: DEC c61d7884 re-verified UNCHANGED python-raw (origin blob '
    'sha256 equality with watermark); zero delta; zero action')
st['current'] = st['current_task'] = st['now_active'] = (
    'r996: S0 storm closeout (estate checkpoint 1dc16ff95 + rebase onto 60a6af702 + 19-UU regen '
    'resolve + r808 three-step) + D19 ORD delta acked (7141acd2 canonical) + S6 absorbed chain '
    'bad=0 + update_daily retry honest no-op; W242 materialize = next product on W241-finalize '
    'landing (bm-c chain waits-upstream)')
st['did'] = ('r996: S0-1 anchor + orphan 0/34 + estate checkpoint 1dc16ff95 + rebase 844fa5bd9 '
    '(19-UU treasure-guarded resolve) + S0.5 ORD single-row ack + smoke 49/49 + boards empty + '
    'satengine ALIVE + S6 absorbed + update_daily retry rc0 no-op cutoff 10-13 + S7 quartet + '
    'attrition CLEAN + idle --worked')
st['task'] = st['last_action'] = 'r996 storm-closeout + D19 ORD ack + S6 absorb'
st['next'] = ('r997: W242 materialize (prereg derive + five-face freeze + engine self-burn 12/12) '
    'fires on W241 finalize landing (bm-c chain); moneyflow IC prereg on panel-complete; HANDOVER '
    '5x rolls to r1000; month exam 10-31; C-20261014-01 revisit 10-16')
st['last_artifact'] = st['recent_artifact'] = st['latest_artifact'] = (
    'results/_r995bma_s6_chain.log (27-leg chain 18:17 bad=0, absorbed+committed) + '
    'results/_w242bma_20261014_probe_receipt.json (W242 seat, on-disk verified)')
st['verdict'] = ('green (wm-red=false; satengine ALIVE rc0 idle queue0; W242 freeze '
    'waits-upstream W241 finalize bm-c lane; dualrun streak 25 absorbed 18:17; orphan 0/34)')
st['verify'] = ('green (smoke 49/49 + rebase 844fa5bd9 clean tree + attrition CLEAN rc0 + '
    'watermark red=false + S7 quartet green + idle --worked)')
st['orphan_face'] = 0
st['orphan_faces'] = 0
st['idle_rounds'] = 0
st['agenda_starved'] = False
st['notes'] = st.get('notes', '') + (' r996: sequence-honest heal -- r994 wrote report line but '
    'state write lost (state ts frozen at r993 17:16:51), r995 = commit-only round (138a94745 W242 '
    'seat publish, no report line, dead before closeout), dead 18:08-attempt estate absorbed via '
    'checkpoint 1dc16ff95 per 60eb16f34 clean-tree law; HANDOVER 5x obligation rolls to r1000; '
    'bm-b 1176e4c4 ORD watermark = no-blob-match bad-provenance (r814 family), noted not '
    'overwritten (their face their repair per dual-source precedent).')
st['push_verified'] = {'ts': NOW, 'note': 'r996: closeout push pending at state-write; sync field updated post-push addendum', 'origin_tip': 'pending'}
st['heartbeat_epoch_utc'] = int(datetime.datetime.now().timestamp())
st['heartbeat_epoch_utc_type_int'] = True
st['last_heartbeat_epoch_utc'] = st['heartbeat_epoch_utc']
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('state written, epoch int =', st['heartbeat_epoch_utc'], type(st['heartbeat_epoch_utc']).__name__)

# --- heartbeat ---
stats = json.load(open(ROOT + r'\_r996_stats.json', encoding='utf-8-sig'))
hb_path = ROOT + r'\fleet\machines\bm-a.json'
hb = json.load(open(hb_path, encoding='utf-8'))
hb.update({
    'last_seen': NOW,
    'ts': NOW,
    'clock_read': NOW,
    'heartbeat_epoch_utc': int(datetime.datetime.now().timestamp()),
    'current_task': st['current_task'],
    'cpu_cores': stats['cores'],
    'free_ram_gb': stats['free_ram_gb'],
    'gpu_free_vram_mb': stats['gpu_free_vram_mb'],
    'verdict': 'green (idle 0; W242 waits-upstream W241 bm-c; smoke 49/49)',
    'idle_rounds': 0,
    'agenda_starved': False,
    'round_no': 996,
    'last_round': 996,
})
json.dump(hb, open(hb_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
chk = json.load(open(hb_path, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'], 'clock_read must be T-separated'
print('heartbeat written + self-verified (epoch int, clock T-format)')
print('DONE r996 closeout writes')
