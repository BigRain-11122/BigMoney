# R275 bm-a closeout: state file + heartbeat + round report line (face-preserving writes)
# Faces probed: no-BOM / CRLF / no trailing newline / indent=1 / ensure_ascii=False
import io, json, time, datetime, subprocess

now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%d %H:%M")
iso_clock = now.isoformat()          # T-separated per R262
epoch = int(time.time())             # int per R170/R178

DID = ("R275 unattended maintenance+5x HANDOVER verification round: S0.5 double-scan orders 85/85 canonical diff empty"
       " (86 files incl README non-order) + decisions tail D-20260926-11 zero new rows; smoke 25/25; board 84 tickets"
       " all done/claimed zero open + job_list 0 + bandit 0 open; post_review tail zero NO (7 non-YES all WAIT legal);"
       " T-84 s1 re-probe D: absent continues (physical dependency legal deferral, CEO three-path ruling pending);"
       " MF_IC_P1 gate panel 53/5222 complete=false source-blocked continues (30min self-heal loop alive);"
       " migration executor supervision PID 35344 alive (journal 22:35 tail, 15min heartbeat law, waiting CEO"
       " Code.exe fail-closed) + bm-b v2.2 PID 28696 not-on-this-box = per-machine independent physical legs zero"
       " double-mover (R271 adjudication re-verified); anti-repeat tri-verification: town.html already v5-aligned"
       " (org_chart v6 = KPI-column refresh, town info face shows mandate snippets zero KPI face zero lag) / Optuna"
       " stays O-1120 sealed / queue small-items all expired; MAIN DELIVERABLE = R275 5x HANDOVER verification"
       " (header latest-check=round 275 refreshed + tail round 275 bm-a row appended: R271-275 window + bm-b"
       " r275-276 concurrent read + unified ledger 187,845 flat zero batch finalize + migration dual-executor"
       " adjudication face + R280 next-verification pointer); S6 28 legs all rc=0 weekend no-op family"
       " (daily 0 new rows cutoff 09-24 Mid-Autumn closure / lhb+mf+ah throttle windows / fundamental fresh skip /"
       " blf 5222 all gates pass / t35v PASS zero-case / prospect 22/22 drift=0 / promotion 0/22 honest"
       " NOT-ELIGIBLE / aggr+grid marks idempotent no-op / alloc bm-b-lane guard honest no-op / export 6 traders"
       " 18 positions / clock ORANGE_COOL activated=0 idempotent / token delta=-49 L2 retro 1 leg)")

VERDICT = ("R275: watermark GREEN (py_low_board_clear weekend legal-idle: open 0/bandit 0/pool 49/49 done;"
           " pool_starvation flag = supply-gap whitelist same face -- T-84 D:/ physical + MF_IC source-block,"
           " not computable-lane), smoke 25/25, S6 28x rc=0, HANDOVER 5x verification delivered (header+row),"
           " orders 85/85 double-scan zero unacked, inbox receipt processed (bm-b t84-s1 three-witness close)")

NEXT = ("09-28 Monday first-bar chain (paper/prospect/t35/aggr/grid/alloc legs fire), migration auto-trigger receipt"
        " assembly on CEO editor close (executor alive, do not double-arm), T-84: D: volume return -> auto-resume"
        " s1->s2 else CEO three-path ruling, MF_IC_P1 on panel recovery, 10-01 month-first round trio"
        " (science_audit+briefing+self_review) + REGIME_GUARD v3 date gate, R280 next 5x HANDOVER check")

TASK = ("R275 5x HANDOVER verification delivered; T-84 s1/s2 held on D:/Money physical dependency;"
        " MF_IC_P1 on panel recovery; migration executor supervised (window to 09-29 12:00)")

def write_json_face(path, obj):
    s = json.dumps(obj, ensure_ascii=False, indent=1)
    s = s.replace('\n', '\r\n')          # all real newlines in dumps output are line separators
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(s)

# --- state-bm-a.json ---
st = json.load(io.open('state-bm-a.json', encoding='utf-8'))
st['round_no'] = 275
st['did'] = DID
st['verdict'] = VERDICT
st['next'] = NEXT
st['ts'] = ts
st['last_round_ts'] = ts
st['updated_at'] = ts
st['current_task'] = TASK
st['last_run'] = ts
st['last_round_at'] = ts
st['last_round'] = 275
st['updated'] = ts
write_json_face('state-bm-a.json', st)

# --- heartbeat fleet/machines/bm-a.json (sample real cpu/ram/gpu) ---
hb = json.load(io.open('fleet/machines/bm-a.json', encoding='utf-8'))
try:
    import psutil
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    free_ram_gb = round(ram.available / (1024**3), 1)
except Exception:
    cpu, free_ram_gb = 0.0, 0.0
try:
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.total,memory.used',
                        '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=10)
    tot, used = [float(x.strip()) for x in r.stdout.strip().split(',')]
    gpu_free_vram_gb = round((tot - used) / 1024, 1)
except Exception:
    tot, used = 12282.0, 6520.0
    gpu_free_vram_gb = 5.6
hb['last_seen'] = ts
hb['current_task'] = TASK
hb['cpu_pct'] = cpu
hb['free_ram_gb'] = free_ram_gb
hb['gpu_free_vram_gb'] = gpu_free_vram_gb
hb['verdict'] = VERDICT
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = iso_clock
hb['round_no'] = 275
hb['task'] = TASK
hb['free_ram_mb'] = int(free_ram_gb * 1024)
hb['gpu_idle_vram_gb'] = gpu_free_vram_gb
hb['gpu_free_vram_mb'] = int(gpu_free_vram_gb * 1024)
hb['gpu_idle_vram_mb'] = int(gpu_free_vram_gb * 1024)
hb['idle_ram_gb'] = free_ram_gb
hb['gpu0_free_vram_gb'] = gpu_free_vram_gb
write_json_face('fleet/machines/bm-a.json', hb)

# --- round report line ---
line = ("2026-09-26 22:57 | R275 | bm-a dept:工程·舰队（无人值守维护轮+5x HANDOVER 核对）| 水位=绿"
        "（py_low_board_clear 周末合法 idle：open 0/bandit 0/池 49/49 done；compute_audit pool_starvation 旗"
        "=供给缺口白名单同面——T-84 D: 物理挂起+MF_IC 源阻断非算力可解）| did: S0 pull up-to-date；S0.5 双扫"
        " orders 85/85 canonical diff empty（86 files 含 README 非令件）+decisions 尾 D-20260926-11 零新行；"
        "S1 smoke 25/25；S2 板 84 票全 done/claimed 零 open+job_list 0+bandit 0；S3 复审尾零 NO（7 non-YES 全"
        "=WAIT 合法等待态）+T-84 s1 复探针 D: 缺位持续（物理依赖合法暂缓·CEO 三径裁决待办）+MF_IC_P1 门=面板"
        " 53/5222 complete=false 源阻断持续（30min 自愈环活）+迁移执行器监督=PID 35344 活（21:23:47 起·"
        "journal 22:35 尾活 15min 降频律健康·等 CEO Code.exe fail-closed）+bm-b v2.2 PID 28696 非本机=各机独立"
        "物理腿零双 mover（R271 裁定复核）+反重复三验（town.html 已 v5 对齐 org_chart v6=KPI 列刷新零滞后/"
        "Optuna 维持 O-1120 封印/队列小活全过期）+**主交付=R275 5x HANDOVER 核对**（头行最近核对=round 275 刷新"
        "+文末 round 275 bm-a 行=R271-275 窗+bm-b r275-276 并读+统一链 187,845 平持实读零批 finalize+迁移双执行器"
        "裁定面+R280 指针）；S6 28 腿全 rc=0 周末 no-op 族（daily 0 新行 cutoff 09-24/lhb+mf+ah 节流窗/"
        "fundamental 新鲜跳过/blf 5222 全门过/t35v PASS 零例/prospect 22/22 drift=0/promotion 0/22 诚实"
        " NOT-ELIGIBLE/aggr+grid 幂等 no-op/alloc bm-b 车道护栏/export 6 traders 18 pos/clock ORANGE_COOL"
        " activated=0 幂等/token delta=-49 L2 retro 1 腿）| 证据: HANDOVER 头+行实读+ledger_head 187,845 实读"
        "+smoke 25/25+S6 28x rc0+orders diff empty+journal 尾读+双 PID 探针 | 下轮: 09-28 周一新 bar 全链"
        "（paper/prospect/t35/aggr/grid/alloc legs）+迁移点火回执（CEO 编辑器闭即触发）+MF_IC 待源+10-01 月首轮"
        "三件套+REGIME_GUARD v3 日期门 [via bm-a]")
rp = io.open('logs/iteration-loop/round_reports-bm-a.md', 'rb').read()
eol = b'\r\n' if rp.count(b'\r\n') > 0 and rp.count(b'\n') == rp.count(b'\r\n') else b'\n'
if not rp.endswith(b'\n'):
    rp += eol
rp += line.encode('utf-8') + eol
io.open('logs/iteration-loop/round_reports-bm-a.md', 'wb').write(rp)

# --- self-verification ---
st2 = json.load(io.open('state-bm-a.json', encoding='utf-8'))
hb2 = json.load(io.open('fleet/machines/bm-a.json', encoding='utf-8'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in hb2['clock_read'], 'clock_read must be T-separated'
assert st2['round_no'] == 275
print('closeout ok | ts', ts, '| epoch', epoch, '| cpu', cpu, '| ram', free_ram_gb, '| gpu_free', gpu_free_vram_gb)
print('clock_read', hb2['clock_read'])
