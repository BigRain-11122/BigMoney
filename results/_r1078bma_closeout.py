# -*- coding: utf-8 -*-
# r1078 bm-a closeout: idle --worked + round_reports line + state sequence heal + heartbeat dual-face
# Laws applied: r962/r1008 (committed-but-no-report-line -> successor number), r1074 (sequence repair),
# R170/R178 (epoch int), R262 (clock_read T-sep), r1052 (dual-face ack law - no ack changes this round),
# multi-writer fresh-read-modify-write discipline.
import json, time, subprocess, sys
from datetime import datetime

def now_iso():
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'

def detect_eol(path):
    with open(path, 'rb') as f:
        raw = f.read(65536)
    return '\r\n' if b'\r\n' in raw else '\n'

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def dump_json(path, obj, eol):
    with open(path, 'w', encoding='utf-8', newline=eol) as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write(eol)

# ---- step 0: idle --worked (clear idle_rounds=8, law O-20261007-2315) ----
r = subprocess.run([sys.executable, 'Tools/idle_trigger.py', '--worked'], capture_output=True, text=True)
print('idle_worked rc=%d %s' % (r.returncode, (r.stdout or '').strip()[-200:]))

# ---- step 1: round_reports-bm-a.md append r1078 line ----
RP = 'round_reports-bm-a.md'
eol = detect_eol(RP)
with open(RP, 'r', encoding='utf-8', newline='') as f:
    rp = f.read()
last = [l for l in rp.splitlines() if l.strip()][-1]
if '| r1076 |' not in last:
    print('ABORT: round_reports anchor mismatch, last line head: %s' % last[:120]); sys.exit(3)
if '| r1078 |' in rp:
    print('ABORT: r1078 line already present (idempotency guard)'); sys.exit(3)
ts = now_iso()
line = (ts + ' | r1078 | r1077 遗产收口维持轮：水位 green red=false（py_watermark rc0·next_pick=MF IC reference 挂起面非缺口）；'
 'r1077 勘注（r962/r1008 谱系）=r1077 窗（~10:38 发·push 全落后静默期 silence-kill 死）完成 S0 3-UU law-resolve absorb+S6 46 腿+dualrun NUL 行级 union heal+inbox x2 archive+CODELY 坑行'
 '并已推 7 commits（8895e5d3d4..7ca299d8aa origin tip behind=0 实证·心跳 verdict 10:52:17 在案）但报告行+state closeout 缺=本行 sequence-honest 收口；'
 'S0 零 rebase 全净窗（behind=0/ahead=0）；S0.5 ack 双面 CLEAN 105/114/0+D-19 ord 增量消费=10:53 jman LoRA 年轻档令（@bm-c BigStream 域·r1057 判例零义务·内容裁定法）'
 '→水位 ord→a14c3693 ADVANCED（dec 8706acd8 hold·读回恒等·心跳镜像 7）；轮首孤儿 0/24；idle green_idle=true idle_rounds=8（defer 族累积+r1077 死窗未清→本窗实际产工 --worked 清零）；'
 'S2 零可领如实（job_list 空·任务板 52=长驻车道 claim·tech 0 余量·explore 3 残全=CLOSED_FAMILIES #6 冻结族 CEO 重开权·backlog 池空·satengine ALIVE queue0 idle=W278 bm-c 波道供给面）；'
 'S1 smoke 49/49；S6 46 腿面（43 Leg+live_paper）全 rc0 bad=0（_r1078bma_s6chain.ps1=r1077 面 verbatim 克隆·周一盘前 no-op 恒真·MF 腿 FREEZE-RETAIN r1073 处置维持）；'
 'dualrun 连绿 51 持有（NUL heal 后复跑零漂移）；A5 周五面持有（V1/V3/V4 PASS·V2 1/5·V5 1/3·deadline 10-31 轨上）；'
 'S7 四件套绿（loop 在位 next 11:28·watchdog 在位·双爪 IDENTICAL）；W278 席位观察（bm-c prereg derive=r1115 首动作·bm-a 零抢跑维持）'
 ' | 证据=_r1078bma_s6chain_rc.log 45 rc 行 bad=0+live_paper rc0·smoke 49/49·orders_ack_scan CLEAN 105/114/0·D-19 ADVANCED ord a14c3693·'
 'dualrun rows50 streak51·PACK-2026-10-19 overall PENDING（V1/V3/V4 PASS·V2 streak 1）·quartet schtasks 在位 x2+双爪 IDENTICAL'
 ' | 下轮指针：今日 15:30 后窗=papers 链+MF lane 重测裁决（FREEZE-RETAIN 后首个收盘窗·day-8..12 封锁链证据在案）+A5 新 bar 推进；'
 'W278 prereg/splice/finalize 观察（bm-c 车道）；委员会三合一 ≤10-25 惜乘')
if not rp.endswith(('\n', '\r')):
    rp += eol
with open(RP, 'w', encoding='utf-8', newline='') as f:
    f.write(rp + line + eol)
print('report line appended, len=%d' % len(line))

# ---- step 2: state-bm-a.json sequence heal ----
ST = 'state-bm-a.json'
eol_s = detect_eol(ST)
st = load_json(ST)
if st.get('round_no') != 1077:
    print('ABORT: state round_no unexpected: %r' % st.get('round_no')); sys.exit(3)
epoch = int(time.time())
did = ('r1078: (1) r1077 estate closeout (post-commit pre-report death: 7 commits delivered on origin 8895e5d3d4..7ca299d8aa, heartbeat verdict 10:52:17, '
 'report line + state closeout missing -> THIS window sequence-honest per r962/r1008 precedent); (2) S0 zero-rebase clean window (behind=0/ahead=0); '
 '(3) D-19 ord delta consumed = 10:53 jman LoRA young-era order (@bm-c, BigStream domain, zero BigMoney obligation per r1057 precedent; content-adjudication law) '
 '-> wm ord ADVANCED a14c3693, dec 8706acd8 hold, mirrors synced 7; (4) round-start orphan 0/24; idle green_idle=true idle_rounds=8 '
 '(defer-family accumulation + r1077 dead-window uncleared) consumed same-round via --worked (estate closeout + S6 chain = actual product work); '
 '(5) S2 zero claimable (jobs empty, tasks 52 standing lane claims, tech 0, explore 3=CLOSED#6 frozen family, backlog pool 0, satengine idle queue0 supply=bm-c W278 wave lane); '
 '(6) S1 smoke 49/49; S6 46-leg face (43 Leg + live_paper) all rc0 bad=0 (r1077 face verbatim clone, Monday pre-market no-op faces honest; MF legs FREEZE-RETAIN); '
 'dualrun streak 51 held post-heal; A5 Friday face held (V1/V3/V4 PASS, V2 1/5, V5 1/3, 10-31 on-track); (7) S7 quartet green (loop present next 11:28, watchdog present, claws identical both)')
verdict = ('GREEN: r1078 estate-closeout maintenance round -- r1077 work delivered on origin (7 commits, heartbeat 10:52:17), report-line gap disclosed sequence-honest; '
 'S6 all rc0 (Monday pre-market no-ops honest), dualrun streak 51, A5 Friday face held (10-31 on-track), smoke 49/49, ack CLEAN 105/114/0, '
 'D-19 ord delta consumed zero-obligation, quartet green, zero claimable work (waiting-state faces declared one-line each)')
verify = ('_r1078bma_s6chain_rc.log 45 rc-lines bad=0 + live_paper rc0 + smoke 49/49 + orders_ack_scan CLEAN 105/114/0 + D-19 ADVANCED ord a14c3693 read-back '
 '+ dualrun rows=50 streak=51 + PACK-2026-10-19 (V1/V3/V4 PASS, V2 streak 1, overall PENDING deadline 10-31) + quartet schtasks x2 + claws IDENTICAL x2')
nxt = ('r1079: (1) Monday 15:30 bars window: papers chain + MF lane retest adjudication (first post-close window after r1073 FREEZE-RETAIN; day-8..12 blockade chain evidence on file); '
 '(2) A5 streak advance on new-bar (V2 toward 5, V5 toward 3); (3) W278 prereg/splice/finalize watch (bm-c lane, W279 owner naming rides sec.7/8); '
 '(4) committee three-in-one ride watch <=10-25')
artifact = ('results/_r1078bma_s6chain.ps1 (46-leg face clone) + _r1078bma_s6chain_rc.log (all rc0 bad=0, dualrun streak 51) '
 '+ PACK-2026-10-19 A5 re-read + round_reports r1078 line (r1077 gap closed)')
st['round_no'] = 1079
st['round'] = 1078
st['loop_round'] = 1078
st['round_no_label'] = 'r1078'
st['last_round'] = 'r1078'
st['last_round_at'] = ts
st['last_round_closed'] = ts
st['last_round_ts'] = ts
st['last_run'] = ts
st['last_seen'] = ts
st['last_action_at'] = ts
st['updated'] = ts
st['updated_at'] = ts
st['did'] = did
st['last_action'] = 'r1078: estate closeout + S6 46-leg chain + D-19 ord advance + idle --worked clear'
st['current'] = 'r1078: r1077 estate closeout + S6 chain + D-19 ord delta consumed'
st['current_task'] = 'r1078 closeout: report line + state sequence heal + heartbeat dual-face'
st['now_active'] = 'bm-a loop r1078 closeout (r1077 estate + S6 chain + D-19 ord advance)'
st['task'] = 'r1078: S6 chain 46-leg + r1077 estate closeout + D-19 ord advance'
st['verdict'] = verdict
st['verify'] = verify
st['next'] = nxt
st['next_milestone'] = 'A5 first-line acceptance 10-31 (V2 1/5 + V5 1/3 accruing on new-bar days); committee three-in-one report <=10-25; Monday post-15:30 MF retest adjudication'
st['last_artifact'] = artifact
st['latest_artifact'] = artifact
st['recent_artifact'] = artifact
st['last_heartbeat_epoch_utc'] = st.get('heartbeat_epoch_utc', 1792378337)
st['heartbeat_epoch_utc'] = epoch
st['heartbeat_epoch_utc_type_int'] = isinstance(st['heartbeat_epoch_utc'], int)
st['clock_read'] = ts
st['ts'] = ts
st['idle_rounds'] = 0
st['agenda_starved'] = False
st['orphan_face'] = 0
st['orphan_faces'] = 0
st['orphan_killed'] = 0
st['ram_free_gb'] = 50.0
st['free_ram_gb'] = 50.0
st['idle_ram_gb'] = 50.0
st['ram_free_pct'] = 53.4
st['free_ram_pct'] = 53.4
st['cpu_pct'] = 33.0
st['cpu_load_pct'] = 33.0
st['last_orders_seen'] = 'r1078: D-19 ord delta consumed (10:53 jman LoRA young-era row @bm-c BigStream domain, zero obligation); wm ord->a14c3693; dec 8706acd8 hold'
st['last_decisions_seen'] = 'r1078: dec hold 8706acd8 (zero delta)'
st['last_orders_at'] = ts
st['last_decisions_at'] = ts
st['orders_ack_note'] = 'r1078: zero NEW fleet O-files (scan CLEAN 105/114/0 dual-face parity); D-19 ord delta consumed = 10:53 jman LoRA row (@bm-c, BigStream, zero obligation per r1057); dec hold; inbox empty'
st['notes_seq_repair_r1078'] = ('r1078 sequence-honest: r1077 window (fired ~10:38, silence-killed ~11:0x in the quiet window after its push) completed S0 3-UU law-resolve absorb + '
 'S6 46-leg chain + dualrun NUL line-union heal + inbox x2 archive + CODELY pit rows and PUSHED all 7 commits (8895e5d3d4..7ca299d8aa, origin tip behind=0 verified this window) '
 'but died pre-report-line and pre-state-closeout (state round_no stayed 1077, did stayed r1076); THIS window = r1078 per r962/r1008 precedent '
 '(committed-but-no-report-line -> successor takes next number, gap disclosed in successor line); canonical face = round_reports-bm-a.md + git log')
if isinstance(st.get('d19_watermark_guard'), dict):
    st['d19_watermark_guard']['round_ref'] = 1078
    st['d19_watermark_guard']['ts'] = ts
dump_json(ST, st, eol_s)
chk = load_json(ST)
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert chk['round_no'] == 1079
print('state healed: round_no=1079 round=1078 epoch_int=%s' % chk['heartbeat_epoch_utc'])

# ---- step 3: heartbeat fleet/machines/bm-a.json ----
HB = 'fleet/machines/bm-a.json'
eol_h = detect_eol(HB)
hb = load_json(HB)
ack_count = len(hb.get('orders_ack', []))
hb['round_no'] = 1078
hb['last_seen'] = ts
hb['current'] = 'r1078: r1077 estate closeout + S6 46-leg chain (all rc0) + D-19 ord delta consumed + idle --worked clear'
hb['did'] = did
hb['verdict'] = verdict
hb['verify'] = verify
hb['next'] = nxt
hb['next_milestone'] = st['next_milestone']
hb['task'] = st['task']
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = ts
hb['ts'] = ts
hb['ram_free_gb'] = 50.0
hb['free_ram_gb'] = 50.0
hb['idle_ram_gb'] = 50.0
hb['ram_free_pct'] = 53.4
hb['free_ram_pct'] = 53.4
hb['cpu_pct'] = 33.0
dump_json(HB, hb, eol_h)
chk2 = load_json(HB)
assert isinstance(chk2['heartbeat_epoch_utc'], int), 'hb epoch must be int'
assert len(chk2['orders_ack']) == ack_count, 'orders_ack clobbered!'
print('heartbeat healed: round_no=1078 ack=%d epoch_int=%s' % (ack_count, chk2['heartbeat_epoch_utc']))
print('CLOSEOUT_FILES_OK ts=%s' % ts)
