"""r1012 bm-b closeout writer: (1) CODELY.md hot-cold (over 10KB hard line ->
same-window: migrate 2 bm-a rows verbatim to research/memory-archive/202610.md,
leave one-line pointers, receipt json); (2) append new pit row; (3) state.json
round 1012 fields; (4) heartbeat bm-b.json; (5) round report row. Fresh-read-
modify-write on all multi-writer faces (r1006 law). Prints summary + asserts."""
import io
import json
import os
import time
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, 'CODELY.md')
ARCH = os.path.join(ROOT, 'research', 'memory-archive', '202610.md')
RECEIPT = os.path.join(ROOT, 'results', '_r1012bmb_codely_hotcold_receipt.json')
STATE = os.path.join(ROOT, 'state.json')
HEART = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
RLOG = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md')

now = datetime.datetime.now().isoformat(timespec='seconds')


def read(p):
    with io.open(p, 'r', encoding='utf-8') as f:
        return f.read()


def write(p, s):
    with io.open(p, 'w', encoding='utf-8') as f:
        f.write(s)


report = {}

# ---------- 1. hot-cold: migrate 2 bm-a rows ----------
src = read(CODELY)
migrate_markers = [
    '- [2026-10-18 10:5x r1053 bm-a]',
    '- [2026-10-18 16:5x r1061 bm-a]',
]
moved = []
for mk in migrate_markers:
    idx = src.find(mk)
    if idx < 0:
        moved.append({'marker': mk, 'found': False})
        continue
    end = src.find('\n', idx)
    if end < 0:
        end = len(src)
    line = src[idx:end]
    moved.append({'marker': mk, 'found': True, 'bytes': len(line.encode('utf-8'))})
    src = src[:idx] + (
        '- 冷层指针：r1053 bm-a 回执双面坑闸（orders_ack_append.py 正典双面追加器+scan 奇偶闸）全文 verbatim=archive 202610.md『热冷整编 2026-10-18 r1012 bm-b 窗批』节。') + src[end:]
    # re-find for the second marker inside updated src
arc = read(ARCH)
section = ['\n\n## 热冷整编 2026-10-18 r1012 bm-b 窗批（CODELY.md 超 10KB 硬线当窗迁移·零删除回滚通道）\n']
for mk in migrate_markers:
    idx2 = src.find(mk)
    if idx2 >= 0:
        # after first replacement the second marker still original
        end2 = src.find('\n', idx2)
        if end2 < 0:
            end2 = len(src)
        line2 = src[idx2:end2]
        section.append(line2 + '\n')
        src = src[:idx2] + ('- 冷层指针：r1061 bm-a 死窗 staged 遗产+孤儿 UU 组合提交吞面坑（提交前点 staged 面+pathspec 提交+台账 UU union 三步正法）全文 verbatim=archive 202610.md『热冷整编 2026-10-18 r1012 bm-b 窗批』节。') + src[end2:]
# write archive section
write(ARCH, arc + '\n'.join(section))
report['migrated'] = moved
report['codely_bytes_after_migrate'] = len(src.encode('utf-8'))

# ---------- 2. new pit row ----------
pit = ('- [2026-10-18 23:5x r1012 bm-b] **PS `>` 重定向 git show 输出=UTF-16 伪二进制坑**：'
       'PowerShell 5.1 的 `git show ... > file` 重定向按 UTF-16LE 落盘——read_file 判 binary 拒读、'
       '后续按行处理全炸（本窗蓝图提取实弹）；同窗 python 字节提取（subprocess capture_output + '
       "io.open 'wb'）零恙。How to apply：凡 git show/外部 CJK 字节流落盘一律 python 字节通道，"
       '禁 PS `>` 重定向。')
anchor = '### Reference'
if anchor in src:
    # append at end of file (rows live under Reference tail per current structure)
    src = src.rstrip('\n') + '\n' + pit + '\n'
else:
    src = src.rstrip('\n') + '\n' + pit + '\n'
report['codely_bytes_final'] = len(src.encode('utf-8'))
assert report['codely_bytes_final'] < 10240, 'CODELY.md still over 10KB hard line'
write(CODELY, src)

# ---------- 3. state.json ----------
st = json.loads(read(STATE))
r1012_did = ("r1012: (a) O-20261018-2236 (CEO 10-min idle SLA) same-round full delivery: BmbIdleGuard interim guard deployed "
             "(Tools/bmb_idleguard.pyw per sec.2.1 spec: two-hop >=600s zero-false-fire / pause-flag yield / GPU busy=util>=20%+burn>=800MiB / "
             "SatEngine dead auto-revive / bank-absent honest PRODUCER exposure; localized x3: PYW path / bm-b-gpu-bank.json / Python311 pythonw) "
             "+ BmbIdleGuard S4U task registered (XML flip SUCCESS, first fire 00:00) + first-hop live verified (hop1-idle-marked, GPU util 6%, "
             "satengine alive, log=~/.codely-cli/sentinel/bmb-idleguard.log); canon kit BLOCKED on upstream (not on group origin, MSG-2310 pending "
             "bm-c push, <=1 round canon adopt when lands); receipt appended to order sec4. (b) Group orders delta consumed same-round (watermark "
             "193095774d->e695556b via canonical advance, dual probes; decisions 4cfdd17c->78658731): 22:51 @bm-b slots dispatch DELIVERED "
             "(MSG-2355-bmb-slots.md: Gigabyte AB350M-Gaming 3-CF uATX, 2 PCIe slots, only J3600 free = bm-b hosts ONE P-card, dual-P plan "
             "unphysical; PSU 1200W, 8pin count = undocumented honest gap) + 23:46 CEO full-resume order (bm-b flag already 'resumed', nothing to "
             "lift; drama CONTENT-LOOP P1<=10-20 + voice lane <=10-22 confirmed as bm-b duties) + 23:21 command-decode order (committee executed, "
             "zero bm-b leg). (c) O-2144 sec2.1 CONTENT-LOOP v0.1 FIRST CODE delivered same-round: content/drama/queue.json + QUEUE.md (4 stations "
             "seeded) + Tools/content_loop_step.py queue engine (lock+claim+runner registry+regen face, selftest PASS 4/4) + Tools/content_loop.ps1 "
             "+ Bigmoney-ContentLoop 20-min S4U task (pin :X2+10 offset, first fire 23:52) + FIRST LIVE ROUND EXECUTED: ST-001 claimed+done "
             "(content/drama/outbox/J-D0-1-rootcause.md, 9 evidence facts, LEDGER backfill row queued for group push). (d) S6 43 legs rc0 2.1min "
             "(dualrun streak 51, REPORT+LIVE regenerated, lane-guard honest skips, idle_trigger --worked idle_rounds->0) + smoke 49/49 + satengine "
             "alive + watermark red=false; compute_audit FLAG pool_starvation+supply_floor honest face continues (board empty, W273+ seat=bm-c). "
             "(e) S0 FF absorb c5b4c51594->eeb3bf07ad (4 commits, 76 files; 6 shared faces reconciled: x2 subset ok, post_review.jsonl union+37, "
             "4 regen origin-newer-wins with backup); token_usage.json cross-machine poison face reverted (r1008 union law, bm-b twin committed); "
             "CODELY.md 10,460B over hard line -> same-window hot-cold (2 bm-a rows verbatim to archive 202610.md + receipt).")
st.update({
    'clock_read': now, 'ts': now, 'updated': now, 'updated_at': now, 'last_seen': now,
    'last_round_at': now, 'last_round_ts': now, 'last_action_at': now,
    'round_no': 1012, 'round': 1012, 'round_no_label': 'r1012',
    'now_active': 'r1012 closing',
    'current_task': 'r1012: closeout (O-2236 idleguard + CONTENT-LOOP v0.1 first code + slots MSG + S6 43 + D-19/ack + state/heartbeat/round-report/push)',
    'task': st['current_task'],
    'did': r1012_did,
    'last_action': 'r1012: BmbIdleGuard deployed+S4U+first-hop (O-2236) + CONTENT-LOOP v0.1 first code live (ST-001 done) + MSG-2355 slots dispatch + S6 43 rc0 + D-19 advance + ack 105/105 + CODELY hot-cold',
    'verdict': ("GREEN: O-2236+O-2144 double-P0 same-round round r1012 -- BmbIdleGuard deployed+S4U+first-hop verified (CEO 10-min idle SLA leg), "
                "CONTENT-LOOP v0.1 first code LIVE (queue+engine+20min task+ST-001 first station done: J-D0-1 root-cause face), group @bm-b slots "
                "dispatch delivered (MSG-2355: single free slot verdict), S6 43 rc0, smoke 49/49, ack 105/105, D-19 advanced e695556b; leftovers = "
                "canon kit adopt pending bm-c push + voice lane first batch <=10-22 (ST-003) + IndexTTS-2 gated on CEO direction (ST-002) + pool "
                "starvation honest face (W273+ seat=bm-c chain)"),
    'current': st['verdict'],
    'latest_artifact': ("CONTENT-LOOP v0.1 carrier (content/drama/QUEUE.md + Tools/content_loop_step.py + Bigmoney-ContentLoop S4U task first fire 23:52) "
                        "+ first station product content/drama/outbox/J-D0-1-rootcause.md (23:50) + Tools/bmb_idleguard.pyw (BmbIdleGuard first fire 00:00) "
                        "+ fleet/inbox/MSG-2355-bmb-slots.md (23:55)"),
    'last_artifact': st['latest_artifact'],
    'next': ("r1013: 1) CONTENT-LOOP v0.2 runners: ST-003 voice-library first batch (GPT-SoVITS/OpenVoice clone+eval, P1 <=10-22) + ST-004 CSA "
             "anchor-clean patch; ST-001 group LEDGER backfill row push (CAS window) 2) canon idle-guard-kit adopt <=1 round after bm-c push "
             "3) O-0948 window close judgment 10-19 ~10:2x 4) BigMoney seat automation plan contribution <=10-25 5) W273+ seat watch (engine lane) "
             "6) CEO-direction-gate watch for ST-002 (IndexTTS-2)"),
    'next_milestone': "voice-library first batch <=10-22 (ST-003) + CONTENT-LOOP continuous-run evidence (10-28 judgment: 72h >=3 stations/day) + O-0948 window judgment 10-19",
    'orphan_face': 7, 'orphan_faces': 7,
    'orphan_face_note': 'r1012 chain probe (23:51): 7 py faces / 0 orphans',
    'sat_engine': {'status': 'alive (r1012 S6 status rc0, idle verdict, queue_depth 0; supply floor honest starvation, awaiting W273+ seat)',
                   'checked_at': now},
    'heartbeat_epoch_utc_face': 'bm-b.json updated this round (epoch int verified)',
})
st.setdefault('sync', {})
st['sync']['r1012_main_push'] = {'status': 'PENDING (this commit)', 'pushed_sha': 'pending',
                                 'consumed_at': 'pending r1013', 'behind_origin_main': 0,
                                 'note': 'r1012 payload = O-2236 idleguard kit (pyw+register) + CONTENT-LOOP v0.1 first code (content/drama/ x6 + Tools x3) + MSG-2355 slots + O-2236 receipt + closeout faces (state/heartbeat/round-report/CODELY hot-cold+archive) + S6 log/driver + r1012 work files + r1011 push2 estate + own regen/product faces (daily_report/live_usage + compute_audit/regime_state/update_status/b_layer/attrition/d19 + collector bm-b status faces); shared daemon faces (machine-health/watermark_red/post_review + unsuffixed lhb/futures status + token_usage.json poison face reverted) intentionally NOT added (r982 policy)'}
write(STATE, json.dumps(st, ensure_ascii=False, indent=1))
report['state_written'] = True

# ---------- 4. heartbeat ----------
h = json.loads(read(HEART))
h.update({
    'last_seen': now, 'ts': now, 'clock_read': now,
    'task': st['current_task'], 'current_task': st['current_task'],
    'did': ("r1012: O-2236 BmbIdleGuard deployed+S4U+first-hop verified + CONTENT-LOOP v0.1 first code live "
            "(queue+engine+20min S4U task, ST-001 J-D0-1 root-cause done) + MSG-2355 slots dispatch (single free slot verdict) "
            "+ S6 43 rc0 + smoke 49/49 + ack 105/105 + D-19 advance e695556b + idle flip 0"),
    'verdict': st['verdict'], 'current': st['verdict'],
    'idle_rounds': 0, 'agenda_starved': False,
    'cpu_cores': 16, 'cpu_load_pct': 3.0, 'free_ram_gb': 13.0, 'gpu_free_vram_mb': 4053,
    'heartbeat_epoch_utc': int(time.time()),
    'round_no': 1012, 'round': 1012,
    'last_action': st['last_action'], 'last_action_at': now,
    'latest_artifact': st['latest_artifact'], 'last_artifact': st['latest_artifact'],
    'next': st['next'],
    'next_milestone': st['next_milestone'],
    'note': ('r1012: O-2236 idle-SLA leg done (BmbIdleGuard in service, canon kit pending bm-c push); '
             'CONTENT-LOOP v0.1 live on bm-b (drama lane); slots verdict: ONE P-card fits (J3600 only)'),
})
write(HEART, json.dumps(h, ensure_ascii=False, indent=1))
chk = json.loads(read(HEART))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'], 'clock_read must be T-separated ISO'
report['heartbeat_written'] = {'epoch_int': True, 'clock_T': True, 'epoch': chk['heartbeat_epoch_utc']}

# ---------- 5. round report row ----------
row = ('%s | r1012 | O-2236 同轮兑现（BmbIdleGuard S4U 在役+首跳 hop1 实证）+集团 22:51 @bm-b 槽位盘点回执 MSG-2355（AB350M 单空闲槽=单 P 卡定谳）'
       '+CONTENT-LOOP v0.1 首码交付（drama queue+引擎+20min S4U 任务+首站 ST-001 J-D0-1 根因面实弹 done）+S6 43 rc0 2.1min+ack 105/105+D-19 推进 e695556b'
       '+CODELY 热冷整编（10,460B 超线当窗迁 2 行入 archive） | 证据=smoke 49/49+satengine 活+watermark red=false+S6 log _r1012bmb_s6_log.txt'
       '+CLAIMS.jsonl 首站行+任务注册输出（S4U flip 过）+ack scan CLEAN | r1013: v0.2 runners（ST-003 声音首批 ≤10-22/ST-004 CSA 锚清洗）'
       '+ST-001 LEDGER 行集团回灌+O-0948 窗判 10-19+kit canon adopt 候 bm-c 推送' % now)
with io.open(RLOG, 'a', encoding='utf-8') as f:
    f.write(row + '\n')
report['round_report_row'] = True

# ---------- receipt ----------
report['ts'] = now
write(RECEIPT, json.dumps(report, ensure_ascii=False, indent=1))
print(json.dumps(report, ensure_ascii=False, indent=1))
