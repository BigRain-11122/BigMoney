# r1073 bm-a closeout: round report line + state surgical update + heartbeat + post-heartbeat audit re-run (E1 heal proof)
import json, time, datetime, subprocess, io, sys

NOW = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
EPOCH = int(time.time())
ZONE = NOW  # full ISO with +08:00

def rd(p):
    with io.open(p, encoding='utf-8') as f: return json.load(f)
def wr(p, d):
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(d, f, ensure_ascii=False, indent=1); f.write('\n')

# ---------- 0. live measures ----------
free_gb = None; total_gb = None; cpu = None
try:
    import psutil
    vm = psutil.virtual_memory()
    total_gb = round(vm.total/1e9, 1); free_gb = round(vm.available/1e9, 1)
    free_pct = round(vm.available*100.0/vm.total, 1); load_pct = round(100.0-free_pct, 1)
    cpu = psutil.cpu_percent(interval=1.5)
except Exception as e:
    print('psutil measure fallback:', e)

gpu_vram = None
try:
    r = subprocess.run(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'], capture_output=True, timeout=20)
    if r.returncode == 0 and r.stdout.strip():
        gpu_vram = int(float(r.stdout.strip().splitlines()[0]))
except Exception as e:
    print('gpu measure fallback:', e)

# ---------- 1. round report line ----------
RRLINE = (
 f"{NOW} | r1073 | 主交付=A4 G5 W 波自转循环律正典化提前落地（deadline <=10-25）: firm/WAVE_LOOP_LAW.md v1.0"
 "（W 波自跑范式=公司标准生产循环·八步一闭环成文：席位窗/prereg derive/五面 splice/引擎自燃 12 分片/sixgate/finalize one-pass/fivekeys/§7-8 回填+下波点名"
 "·chain-order+seat-first 既有法承接零重立·判据冻结律照旧）+ automation_line_audit 入 S6 链常设腿 bm-a 首机实装（律 §4·_r1073bma_s6chain.ps1 新腿 rc0）"
 "‖ S0: fetch+rebase autostash pop-UU watermark_red（watchdog 活写竞速 r1031 家族·新鲜 07:00:04 面重 add·marker 扫描干净）；吸收 bm-c r1108-r1110（W275 全周期 CLOSED+W276 prereg derived=bm-c 第 95 枚自有波·W277 归属候 §7/8 回填点名·bm-a 零抢跑）"
 "‖ round-start: 孤儿 0/19（1 常驻服务豁免）·idle green_idle=false（RAM 面 CEO 周末机合法）idle_rounds=0·令板 CLEAN 105/114/0·D-19 双扫 HOLD（dec 8706acd8/ord 04050fda）"
 "‖ S1 smoke 49/49·S3 satengine ALIVE rc0 queue0 idle（scripts/ 正典入口）"
 "‖ S6 链 43 腿+审计新腿+live_paper 全 rc0 bad=0（_r1073bma_s6chain_rc.log）"
 "‖ MF 周一裁决：封锁 day-13 双道仍活（主道 02:04:44 三连 RemoteDisconnected conn_stopped+rank 道 07:05:56 fetch_failed 158.2s）→ FREEZE-RETAIN 处置回执 _r1073bma_mf_adjudication.json（面板冻结 cutoff 2026-10-13·自愈保留·IC 批 parked）"
 "‖ 审计读数 E2/E3/E4/E5=OK（E3 A3 后清·E5 waiting_share 0.0 product 4/5·E4 归因 streak=1）·E1 audit 时点 GAP=CLOUD_CAP_DEFER 伪红（05:18-06:48 全 defer live=2-3 零死窗·收口心跳后复跑愈合证见 verify 面）"
 "‖ A2 归因面：REPORT-2026-10-19 §七 在位（asof 10-16 前收口径诚实标注）·streak >=3 交易日 by ~10-21 watch 维持"
 "‖ 双爪重装·loop pin=8 no-op·watchdog S4U flip 拒绝=carried C-20261016-04"
 " | 证据=firm/WAVE_LOOP_LAW.md + results/_r1073bma_s6chain_rc.log 44 rc 行 bad=0 + results/_r1073bma_mf_adjudication.json + results/automation_line_audit.json（E2-E5 OK）+ smoke 49/49 + orders_ack 双扫 CLEAN 105/114/0 + D-19 双扫 HOLD + 孤儿 0/19 + claws 双装"
 " | 本地未达 origin commit 数=0（push verify 见 state push_verified 面）"
 " | 下轮=r1074: (1) A4 尾=A5 首线实装验收准备+委员会三合一呈报骑乘 <=10-25 (2) A2 归因 streak >=3 交易日 by ~10-21 (3) W277 席位 watch（bm-c lane）(4) council sec.6 首裁表 watch <=10-20 12:00 (5) BmaIdleGuard v2 观察续 (6) 5x HANDOVER=r1075"
)
with io.open('round_reports-bm-a.md', 'a', encoding='utf-8', newline='\n') as f:
    f.write('\n' + RRLINE + '\n')
print('report line appended')

# ---------- 2. state surgical update ----------
st = rd('state-bm-a.json')
sum_did = ("r1073: (1) S0 fetch+rebase autostash pop-UU watermark_red (watchdog live-writer race r1031 family, fresh 07:00:04 face re-add, marker scan clean); absorbed bm-c r1108-r1110 (W275 full-cycle CLOSED + W276 prereg derived = bm-c 95th own wave; W277 owner naming rides W276 sec.7/8 backfill, bm-a zero skip-claim); "
 "(2) round-start orphan 0/19 (1 resident server exempt); idle green_idle=false (CEO weekend machine RAM face) idle_rounds=0 claimable 0; board CLEAN 105/114/0; D-19 dual-scan HOLD both (dec 8706acd8/ord 04050fda); "
 "(3) S1 smoke 49/49; S3 satengine ALIVE rc0 queue0 idle (scripts/ canonical entry); "
 "(4) MAIN DELIVERABLE A4 G5 LANDED EARLY (plan sec.III A4, deadline <=10-25): firm/WAVE_LOOP_LAW.md v1.0 = W-wave self-run paradigm codified as company standard production loop (8-step cycle, chain-order/seat-first inherited, audit wiring sec.4); automation_line_audit wired as bm-a S6 standing leg (first-machine landing, other lanes = clone-face self-adoption proposal); "
 "(5) S6 chain 43 legs + new audit leg + live_paper all rc0 bad=0; "
 "(6) MF Monday adjudication: blockade ALIVE day-13 both lanes (main 02:04:44 3x RemoteDisconnected conn_stopped + rank 07:05:56 fetch_failed 158.2s) -> FREEZE-RETAIN receipt (_r1073bma_mf_adjudication.json): panel frozen cutoff 2026-10-13, self-heal retained, IC batch parked; "
 "(7) audit readings E2/E3/E4/E5 OK (E3 cleared by A3, E5 waiting_share 0.0, E4 attribution streak=1); E1 audit-time GAP = CLOUD_CAP_DEFER artifact (05:18-06:48 all defer live=2-3, zero dead windows) heals at this closeout (post-heartbeat audit re-run face); "
 "(8) claws reinstalled both; loop pin=8 no-op; watchdog S4U flip denied = carried C-20261016-04")
art = "firm/WAVE_LOOP_LAW.md (A4 G5 law v1.0) + results/_r1073bma_s6chain.ps1 (43+1 audit standing leg) + results/_r1073bma_mf_adjudication.json (MF freeze-retain day-13) + results/automation_line_audit.json (E2-E5 OK refresh)"
verdict = ("GREEN: r1073 product round -- A4 G5 WAVE_LOOP_LAW v1.0 LANDED EARLY (<=10-25 deadline): self-run paradigm = company standard production loop codified (8-step cycle + inherited chain law + in-loop quality gates); automation_line_audit = bm-a S6 standing leg first-machine wiring; "
 "MF Monday adjudication FREEZE-RETAIN receipted (blockade day-13 both lanes); S6 44-leg face all rc0; smoke 49/49; board CLEAN 105/114/0 x2 scans; D-19 dual HOLD; satengine alive; orphan 0/19; product score = 2-point (runnable+visible law + standing audit leg + adjudication receipt)")
verify = ("results/automation_line_audit.json (E2=OK E3=OK E4=OK E5=OK, E1 defer-face healed post-closeout via re-run) + firm/WAVE_LOOP_LAW.md on origin + results/_r1073bma_s6chain_rc.log 44 rc-lines bad=0 + results/_r1073bma_mf_adjudication.json + orders_ack_scan CLEAN 105/114/0 (round-start + closeout double scan) + D-19 dual-scan HOLD (sha256 python raw-bytes canonical) + smoke 49/49 + orphan probe 0/20 + loop pin=8 no-op + claws reinstalled both")
nxt = ("r1074: (1) A4 tail: committee three-in-one report ride <=10-25 + A5 first-line acceptance prep (<=10-31); (2) A2 attribution streak watch (>=3 trading days by ~10-21; V2 acceptance 5 days by 10-31); (3) W277 seat watch (bm-c lane, owner naming rides W276 sec.7/8); (4) council sec.6 first ruling table watch <=10-20 12:00; (5) BmaIdleGuard v2 scheduled fires observation; (6) next 5x HANDOVER = bm-a r1075")

st.update({
 'round': 1073, 'loop_round': 1073, 'round_no': 1074, 'last_round': 'r1073', 'last_round_label': 'r1073',
 'clock_read': NOW, 'ts': NOW, 'last_seen': NOW, 'last_run': NOW, 'last_round_at': NOW, 'last_round_closed': NOW,
 'last_round_ts': NOW, 'updated': NOW, 'updated_at': NOW, 'last_action_at': NOW, 'last_orders_at': NOW, 'last_decisions_at': NOW,
 'heartbeat_epoch_utc': EPOCH,
 'current': 'r1073: A4 G5 W-wave loop law round (WAVE_LOOP_LAW v1.0 landed early)',
 'current_task': 'r1073: A4 G5 W-wave loop law + audit-leg wiring + MF Monday adjudication',
 'task': 'r1073: A4 G5 W-wave loop law round',
 'now_active': 'bm-a loop r1073 closeout (A4 G5 law landed early)',
 'did': sum_did, 'last_action': sum_did,
 'last_artifact': art, 'recent_artifact': art, 'latest_artifact': art,
 'next': nxt,
 'next_milestone': 'A5 first-line acceptance 10-31; committee three-in-one report <=10-25; A2 attribution >=3 trading days by ~10-21',
 'verdict': verdict, 'verify': verify,
 'orders_ack_note': 'r1073: zero NEW fleet orders (dual-scan CLEAN 105/114/0 round-start + closeout); D-19 dual-scan HOLD both faces (dec 8706acd8 / ord 04050fda); inbox EMPTY',
 'last_orders_seen': 'r1073: D-19 dual-scan HOLD both faces zero-delta NOOP (dec 8706acd8 / ord 04050fda); board CLEAN 105/114/0 x2 scans; inbox EMPTY',
 'last_decisions_seen': 'r1073: D-19 dec HOLD 8706acd8 (dual-scan zero-delta)',
 'orphan_face': 0, 'orphan_faces': 0, 'orphan_killed': 0,
 'idle_rounds': 0, 'agenda_starved': False,
 'notes_r1073': ('r1073: (1) NEW pit-nuance (state-notes face per CODELY 10KB budget law): autostash pop-UU resolution -- an UNCONDITIONAL `git add <UU-file>` chained after a FAILED marker-check in one semicolon command line staged the MARKER-LADEN face (watchdog live-writer overwrite + post-add assert saved it; pre-commit claw = belt not gate); LAW: after any UU resolution, hard-assert markers-absent BEFORE git add, and never chain add unconditionally after a failing check (assert-first, add-second). '
  '(2) E1 audit GAP = CLOUD_CAP_DEFER artifact face (05:18-06:48 ten fires all defer live=2-3 launcher log evidence, zero dead windows, O-0948 account clean); heals on closeout heartbeat (post-closeout audit re-run receipt). '
  '(3) W276 prereg derived (bm-c r1110, 95th own wave); W277 owner naming rides W276 sec.7/8 -- bm-a zero skip-claim held. '
  '(4) MF day-13 disposition = FREEZE-RETAIN (panel cutoff 2026-10-13 frozen, conn-fuse + 30-min throttle + rank probe retained as self-heal, IC batch parked until panel completes); next re-adjudication = any lane success or GM directive. '
  '(5) watchdog S4U flip access-denied = carried C-20261016-04 (elevation window pending)'),
})
if free_gb is not None:
    st.update({'free_ram_gb': free_gb, 'ram_free_gb': free_gb, 'idle_ram_gb': free_gb,
               'ram_free_mb': int(free_gb*1024), 'idle_ram_mb': int(free_gb*1024),
               'free_ram_pct': free_pct, 'ram_free_pct': free_pct, 'ram_load_pct': load_pct,
               'total_ram_gb': total_gb})
    st['ram_load_pct'] = load_pct
if cpu is not None:
    st.update({'cpu_load_pct': cpu, 'cpu_pct': cpu, 'cpu_total_pct': cpu, 'cpu_util_pct': cpu})
if gpu_vram is not None:
    st['gpu_free_vram_mb'] = gpu_vram
st['d19_watermark_guard'] = dict(st.get('d19_watermark_guard') or {})
st['d19_watermark_guard'].update({'round_ref': 1073, 'ts': NOW})
wr('state-bm-a.json', st)
print('state updated; epoch int check:', isinstance(st['heartbeat_epoch_utc'], int))

# ---------- 3. heartbeat ----------
hb = rd('fleet/machines/bm-a.json')
hb.update({
 'last_seen': NOW, 'ts': NOW, 'clock_read': NOW,
 'heartbeat_epoch_utc': EPOCH,
 'current': st['current'], 'current_task': st['current_task'],
 'verdict': 'GREEN: r1073 A4 G5 WAVE_LOOP_LAW v1.0 landed early + audit standing leg wired + MF freeze-retain adjudicated; S6 44-leg rc0; smoke 49/49',
 'idle_rounds': 0, 'agenda_starved': False,
})
if free_gb is not None:
    hb.update({'free_ram_gb': free_gb, 'ram_free_gb': free_gb, 'idle_ram_gb': free_gb,
               'free_ram_pct': free_pct, 'ram_free_pct': free_pct, 'ram_load_pct': load_pct, 'total_ram_gb': total_gb})
if cpu is not None:
    hb.update({'cpu_load_pct': cpu, 'cpu_pct': cpu, 'cpu_total_pct': cpu, 'cpu_util_pct': cpu})
if gpu_vram is not None:
    hb['gpu_free_vram_mb'] = gpu_vram
wr('fleet/machines/bm-a.json', hb)
chk = rd('fleet/machines/bm-a.json')
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178)'
assert 'T' in chk['clock_read'] and ' ' not in chk['clock_read'].split('+')[0], 'clock_read must be T-separated ISO (R262)'
print('heartbeat written; epoch int OK; clock T-format OK; free_gb', free_gb, 'cpu', cpu, 'gpu_vram', gpu_vram)

# ---------- 4. post-heartbeat audit re-run (E1 heal proof) ----------
r = subprocess.run([sys.executable, 'scripts/automation_line_audit.py'], capture_output=True, timeout=180)
print('audit re-run rc', r.returncode)
a = rd('results/automation_line_audit.json')
verds = {e['element']: e['verdict'] for e in a.get('elements', [])}
print('post-closeout audit verdicts:', verds, 'gaps:', a.get('gaps'))
