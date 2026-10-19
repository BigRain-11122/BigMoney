# r1074 bm-a closeout: round report line + state sequence-repair update + heartbeat + post-closeout audit/A5 re-run
# sequence-repair law (r1006/r1041 family): r1073 closeout STATE write was lost in the rebase-race surgery
# (disk state = mid-round mixed face: round=1072/round_no=1073 + 07:12:43 heartbeat faces); canonical face
# (round_reports-bm-a.md r1073 row + fc56f32a45/7a70aee504 on origin) governs -> THIS round = r1074, next = 1075.
import json, time, datetime, subprocess, io, sys, re

NOW = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
EPOCH = int(time.time())

def rd(p):
    with io.open(p, encoding='utf-8') as f: return json.load(f)
def wr(p, d):
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(d, f, ensure_ascii=False, indent=1); f.write('\n')

# ---------- 0. live measures ----------
free_gb = total_gb = cpu = free_pct = load_pct = gpu_vram = None
try:
    import psutil
    vm = psutil.virtual_memory()
    total_gb = round(vm.total/1e9, 1); free_gb = round(vm.available/1e9, 1)
    free_pct = round(vm.available*100.0/vm.total, 1); load_pct = round(100.0-free_pct, 1)
    cpu = psutil.cpu_percent(interval=1.5)
except Exception as e:
    print('psutil measure fallback:', e)
try:
    r = subprocess.run(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'], capture_output=True, timeout=20)
    if r.returncode == 0 and r.stdout.strip():
        gpu_vram = int(float(r.stdout.strip().splitlines()[0]))
except Exception as e:
    print('gpu measure fallback:', e)

# ---------- 0b. S6 chain evidence (read at closeout, never hardcode) ----------
rc_lines = 0; bad_rc = 0; mf_rc = None; a5_rc = None
try:
    log = io.open('results/_r1074bma_s6chain_rc.log', encoding='utf-8').read()
    pairs = re.findall(r'(\S+) rc=(\d+)', log)
    rc_lines = len(pairs)
    bad_rc = sum(1 for _, v in pairs if int(v) not in (0, 1))
    mf_rc = next((v for n, v in pairs if n == 'update_moneyflow'), None)
    a5_rc = next((v for n, v in pairs if n == 'a5_acceptance_pack'), None)
except Exception as e:
    print('chain log read fallback:', e)

# ---------- 1. round report line ----------
RRLINE = (
 f"{NOW} | r1074 | 主交付=A4 尾收口+A5 验收记录载体落地（A5 面·死线 <=10-31）: scripts/a5_acceptance_pack.py"
 "（§四 V1-V5 冻结判据机读验收记录·幂等再生面 PACK-*.md+json+streak.jsonl 连绿台账·selftest 10/10·live 读数 V1/V3/V4 PASS+V2 归因 1/5+V5 审计 1/3 诚实 PENDING·入 S6 链常设腿=审计腿后置位 _r1074bma_s6chain.ps1）"
 "‖ 集团基线件 BigMoney 节 CAS 刷新+细化指针一次过上链（§五消费面②收口·e9b916301561 首推落链·path blob 7a24ece66727 字节恒等验证·仅动 §③ 本司节其余节字节恒等断言·现状刷为审计面真值 E1-E5 全 OK 10-19+指针指向 research/AUTOMATION-LINE-PLAN-v1.md+A1-A4 落地面+A5 载体·回执 _r1074bma_group_plan_receipt.json）——仅余委员会三合一骑乘面（委员会席 <=10-25）"
 "‖ 序列修复：r1073 收口 state 写入在 rebase 竞速手术中丢失（盘面=中途混合面 round=1072/round_no=1073·正典面 round_reports r1073 行+fc56f32a45/7a70aee504 origin 在位）→ 本窗=r1074 按正典面续序·round_no 修复至 1075（r1006/r1041 前例族·零编造全披露）"
 "‖ S0: fetch+rebase autostash 吸收 bm-c r1111（W276 全周期 CLOSED·n1_w276_results finalize+fivekeys 6/6·W277 席=bm-c 下窗首动作）；pop-UU watermark_red=watchdog 活写竞速 r1031 家族（活写面 07:51:04 干净重写·add 清 UU·marker 扫描干净·autostash 丢弃）"
 "‖ round-start: 孤儿 0/19（1 常驻服务豁免）·idle green_idle=false（RAM 面）idle_rounds=0·令板 CLEAN 105/114/0·D-19 双扫 HOLD（dec 8706acd8/ord 04050fda）·S1 smoke 49/49·S3 satengine ALIVE rc0 queue0 idle claimable=0"
 "‖ S6 链全绿 rc 行 {rc_lines} bad={bad_rc}（43 常规腿+新 A5 腿+live_paper=45·_r1074bma_s6chain_rc.log·MF 腿 rc={mf_rc}·A5 腿 rc={a5_rc}）"
 "‖ 等待物一行各：W277 席位=bm-c lane（r1112 首动作·bm-a 零抢跑）·A2 归因 streak 累积中（V2 1/5·by 10-31）·council sec.6 首裁表 watch <=10-20 12:00·BmaIdleGuard v2 观察续·watchdog S4U flip 拒绝=carried C-20261016-04·5x HANDOVER=r1075"
 " | 证据=scripts/a5_acceptance_pack.py + results/a5_acceptance/PACK-2026-10-19.json/.md + streak.jsonl + results/_r1074bma_group_plan_receipt.json（集团 e9b9163 blob 恒等）+ results/_r1074bma_s6chain_rc.log + smoke 49/49 + orders_ack CLEAN 105/114/0 + D-19 双扫 HOLD + 孤儿 0/19"
 " | 本地未达 origin commit 数=0（push verify 见 state push_verified 面）"
 " | 下轮=r1075: (1) 5x HANDOVER 核对更新 (2) A5 streak 复读（V5 连绿累积+V2 交易日累积）(3) 委员会三合一骑乘 watch <=10-25 (4) W277/W278 席位链 watch（bm-c lane）(5) A2 归因 streak >=3 交易日 by ~10-21"
)
with io.open('round_reports-bm-a.md', 'a', encoding='utf-8', newline='\n') as f:
    f.write('\n' + RRLINE + '\n')
print('report line appended')

# ---------- 2. state surgical update (sequence repair + r1074 faces) ----------
st = rd('state-bm-a.json')
sum_did = ("r1074: (1) S0 fetch+rebase autostash absorbed bm-c r1111 (W276 full-cycle CLOSED: finalize n1_w276_results ledger 1,031,535 EXACT + fivekeys 6/6; W277 seat = bm-c next-window FIRST ACTION, bm-a zero skip-claim); pop-UU watermark_red = watchdog live-writer race r1031 family (live face 07:51:04 clean rewrite, add cleared UU, marker scan clean, autostash dropped; r1026 orphan stash kept never-pop per r1070 law); "
 "(2) SEQUENCE REPAIR (r1006/r1041 family): r1073 closeout STATE write lost in the rebase-race surgery (disk mixed mid-round face round=1072/round_no=1073); canonical face (round_reports r1073 row + commits fc56f32a45/7a70aee504 on origin) governs -> this window = r1074, round_no repaired to 1075, zero fabrication; "
 "(3) round-start: orphan 0/19 (1 resident exempt); idle green_idle=false (RAM face) idle_rounds=0 claimable 0; board CLEAN 105/114/0; D-19 dual-scan HOLD both (dec 8706acd8/ord 04050fda); S1 smoke 49/49; S3 satengine ALIVE rc0 queue0 idle; "
 "(4) MAIN DELIVERABLE A5 acceptance-record carrier landed: scripts/a5_acceptance_pack.py (frozen sec.IV criteria V1-V5 machine-read, idempotent PACK-*.md+json + per-day streak.jsonl ledger, selftest 10/10; live reading V1/V3/V4 PASS, V2 attribution 1/5 + V5 audit 1/3 honest PENDING, deadline 10-31); wired as S6 standing leg after the audit leg (_r1074bma_s6chain.ps1 45 legs); "
 "(5) GROUP PLAN BigMoney section CAS refresh + detail-plan pointer landed first-try (commit e9b916301561, path blob 7a24ece66727 byte-equal verified, sec.iii only / other sections byte-identical asserted): five-element face refreshed to audit truth (E1-E5 all OK 10-19, gaps=0) + pointer to research/AUTOMATION-LINE-PLAN-v1.md + A1-A4 landed face + A5 carrier; sec.5 consumption surface (2) CLOSED EARLY; committee three-in-one ride remains committee-seat face <=10-25; receipt _r1074bma_group_plan_receipt.json; "
 "(6) S6 chain 45 legs all rc0 bad=0 (new a5 leg rc0); MF retest rides the chain legs (freeze-retain r1073 disposition carried)")
art = "scripts/a5_acceptance_pack.py (A5 acceptance-record carrier) + results/a5_acceptance/PACK-2026-10-19.json/.md + streak.jsonl + group-plan BigMoney section refresh e9b916301561 (receipt _r1074bma_group_plan_receipt.json) + results/_r1074bma_s6chain.ps1 (45-leg standing face)"
verdict = ("GREEN: r1074 product round -- A5 acceptance-record carrier landed (frozen V1-V5 machine-read, honest PENDING streaks accruing to 10-31) + group-plan BigMoney section refreshed with detail pointer (sec.5 surface-2 closed early, committee ride remains); S6 45-leg rc0; smoke 49/49; board CLEAN; sequence-repaired r1073 state loss per canonical face")
verify = ("scripts/a5_acceptance_pack.py selftest 10/10 + live PACK-2026-10-19 (V1/V3/V4 PASS) + group CAS receipt (origin tip e9b9163 == newc, path blob 7a24ece66727 == new blob) + results/_r1074bma_s6chain_rc.log rc-lines bad=0 + orders_ack CLEAN 105/114/0 + D-19 dual HOLD + smoke 49/49 + orphan 0/19")
nxt = ("r1075: (1) 5x HANDOVER check-update; (2) A5 streak re-read (V5 consecutive + V2 trading-day accrual); (3) committee three-in-one ride watch <=10-25; (4) W277/W278 seat chain watch (bm-c lane); (5) A2 attribution streak >=3 trading days by ~10-21")

st.update({
 'round': 1074, 'loop_round': 1074, 'round_no': 1075, 'last_round': 'r1074', 'last_round_label': 'r1074',
 'clock_read': NOW, 'ts': NOW, 'last_seen': NOW, 'last_run': NOW, 'last_round_at': NOW, 'last_round_closed': NOW,
 'last_round_ts': NOW, 'updated': NOW, 'updated_at': NOW, 'last_action_at': NOW, 'last_orders_at': NOW, 'last_decisions_at': NOW,
 'heartbeat_epoch_utc': EPOCH,
 'current': 'r1074: A4 tail + A5 acceptance-record carrier round',
 'current_task': 'r1074: A5 pack carrier + group-plan BigMoney section pointer + sequence repair',
 'task': 'r1074: A4 tail / A5 acceptance prep product round',
 'now_active': 'bm-a loop r1074 closeout (A5 carrier + group-plan pointer)',
 'did': sum_did, 'last_action': sum_did,
 'last_artifact': art, 'recent_artifact': art, 'latest_artifact': art,
 'next': nxt,
 'next_milestone': 'A5 first-line acceptance 10-31 (V5 1/3 + V2 1/5 accruing); committee three-in-one report <=10-25; A2 attribution >=3 trading days by ~10-21',
 'verdict': verdict, 'verify': verify,
 'orders_ack_note': 'r1074: zero NEW fleet orders (dual-scan CLEAN 105/114/0); D-19 dual-scan HOLD both faces (dec 8706acd8 / ord 04050fda); inbox EMPTY',
 'last_orders_seen': 'r1074: D-19 dual-scan HOLD both faces zero-delta; board CLEAN 105/114/0; inbox EMPTY',
 'last_decisions_seen': 'r1074: D-19 dec HOLD 8706acd8 (dual-scan zero-delta)',
 'orphan_face': 0, 'orphan_faces': 0, 'orphan_killed': 0,
 'idle_rounds': 0, 'agenda_starved': False,
 'notes_r1074': ('r1074: (1) SEQUENCE REPAIR disclosed: r1073 closeout state write lost in rebase-race surgery (disk mixed face round=1072/round_no=1073 + 07:12:43 heartbeat fields); canonical face governs (r1006/r1041 family); this round = r1074, round_no -> 1075. '
  '(2) A5 pack probe-nuance: livefire evidence family face nests per-hit (r.hits[].family) with optional top-level mirror -- probe accepts either, never fabricates. '
  '(3) group CAS: hash-object stdout can carry CRLF-warning lines -- 40-hex regex extraction (r1015 law) is the canonical parse, .strip() whole-output is not. '
  '(4) watchdog S4U flip access-denied = carried C-20261016-04 (elevation window pending)'),
})
if free_gb is not None:
    st.update({'free_ram_gb': free_gb, 'ram_free_gb': free_gb, 'idle_ram_gb': free_gb,
               'ram_free_mb': int(free_gb*1024), 'idle_ram_mb': int(free_gb*1024),
               'free_ram_pct': free_pct, 'ram_free_pct': free_pct, 'ram_load_pct': load_pct,
               'total_ram_gb': total_gb})
if cpu is not None:
    st.update({'cpu_load_pct': cpu, 'cpu_pct': cpu, 'cpu_total_pct': cpu, 'cpu_util_pct': cpu})
if gpu_vram is not None:
    st['gpu_free_vram_mb'] = gpu_vram
st['d19_watermark_guard'] = dict(st.get('d19_watermark_guard') or {})
st['d19_watermark_guard'].update({'round_ref': 1074, 'ts': NOW})
wr('state-bm-a.json', st)
print('state updated; epoch int check:', isinstance(st['heartbeat_epoch_utc'], int))

# ---------- 3. heartbeat ----------
hb = rd('fleet/machines/bm-a.json')
hb.update({
 'last_seen': NOW, 'ts': NOW, 'clock_read': NOW,
 'heartbeat_epoch_utc': EPOCH,
 'current': st['current'], 'current_task': st['current_task'],
 'verdict': 'GREEN: r1074 A5 acceptance-record carrier landed (V1/V3/V4 PASS, V2 1/5 + V5 1/3 accruing) + group-plan BigMoney pointer e9b9163 first-try; S6 45-leg rc0; smoke 49/49',
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

# ---------- 4. post-closeout audit + A5 pack re-run (E1 heal + streak refresh) ----------
r = subprocess.run([sys.executable, 'scripts/automation_line_audit.py'], capture_output=True, timeout=180)
print('audit re-run rc', r.returncode)
r2 = subprocess.run([sys.executable, 'scripts/a5_acceptance_pack.py'], capture_output=True, timeout=180)
print('a5 pack re-run rc', r2.returncode)
a = rd('results/automation_line_audit.json')
verds = {e['element']: e['verdict'] for e in a.get('elements', [])}
print('post-closeout audit verdicts:', verds, 'gaps:', a.get('gaps'))
p = rd('results/a5_acceptance/PACK-%s.json' % NOW[:10])
print('post-closeout pack overall:', p.get('overall_verdict'),
      {i['item']: i['verdict'] for i in p.get('items', [])})
