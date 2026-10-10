# -*- coding: utf-8 -*-
# r853 bm-b closeout: state.json + heartbeat + round report line
import json, os, time, ctypes

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_iso = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

# --- machine stats ---
class M(ctypes.Structure):
    _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                ('ullTotalPhys', ctypes.c_uint64), ('ullAvailPhys', ctypes.c_uint64),
                ('ullTotalPageFile', ctypes.c_uint64), ('ullAvailPageFile', ctypes.c_uint64),
                ('ullTotalVirtual', ctypes.c_uint64), ('ullAvailVirtual', ctypes.c_uint64),
                ('ullAvailExtendedVirtual', ctypes.c_uint64)]
m = M(); m.dwLength = ctypes.sizeof(M)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
free_gb = round(m.ullAvailPhys / 1e9, 1)
total_gb = round(m.ullTotalPhys / 1e9, 1)
ram_free_pct = round(100.0 * m.ullAvailPhys / m.ullTotalPhys, 1)

# --- py_cpu from compute audit (O-20261011-0012 sec.3 audit face) ---
try:
    au = json.load(open(os.path.join(REPO, 'results', 'compute_audit.bm-b.json'), encoding='utf-8'))
    py_cpu = au.get('latest', au).get('py_cpu', 'n/a')
except Exception:
    py_cpu = 'n/a'

R854_QUEUE = ("r854 queue: astock completion verify (disk-truth 4805/5217 @01:44, pace ~11/min, ETA ~02:2x) -> "
              "spawn detached T23 census full burn (runner pre-verified selftest 21/21 @r851, panel gate disk-truth law) "
              "-> census_holds readout (window <=10-11 06:00) -> N2 U3(1) prereg window if holds / G2 academic-citation "
              "fallback if negative + S6 chain; O-20261011-0012 条款4 执行点=重建完毕即认领池面+矩阵切片（属主道自助）; "
              "W207 five-face freeze window via M9 watcher (upstream W206 five-face+finalize pending -> run "
              "results/_w207bmb_freeze_edits.py staged @r852, gates live-fired; anchor roll per r590); "
              "W18 stays drain-gated (bm-a owns w17-judge)")

DID = ("r853: S0 冲突窗手术收口（轮首 churn absorb 后 pull --rebase 撞 bm-c r843+bm-a r963 新面=36-UU 双 pick 窗"
       "〔31 主窗+5 absorb 窗〕·resolver=results/_r853bmb_rebase_resolver.py〔ls-files-u sha 通道·ts 双精度深扫"
       "·jsonl line-union·ledger superset 探针·r648 污染面治愈三面=LIVE md×2+dashboard_status.js origin 侧标记入库"
       "取我方干净 blob·fail-closed 五门〕·de511e985+4a6d7e7e6 两 pick 重放成功·delta 标记门 62 面干净"
       "〔全树扫描撞 r505/r506 史迹取证面=假阳性·域律 delta 化已入 rebase2〕·push 4a6d7e7e6 behind=0"
       "·origin 侧三污染面随重放治愈上链） + S0.5 令差集 zero+D19 双水位恒等（dec caca0c6e/ord 4d33cb4f）"
       "+inbox 两件均他机收件零处理 + S1 smoke 49/49 + S2 板空三查（job 0·票 0 open·水位绿 red=false）"
       "+S3 固定序（引擎活 rc0 idle queue 0·T23 slice-2 门=awaiting_panel〔disk-truth 4805/5217=92%·ETA~02:2x〕"
       "·W207 M9 守望 W206 未落诚实等待·O-0012 条款4=重建完毕即认领等待态·意义性律维持零为烧而烧）"
       " + S6 41 腿（40 rc0+alloc rc2 已知 510880·dualrun streak 8） + S4 域律一条直写 rebase2（主件 30,510B 贴帽"
       "·r666 直写例外·1,264B） + S7 四任务 ALIVE（loop no-op pin=2·watchdog 幂等重注册·双爪恒等）"
       "+attrition CLEAN+idle --worked 清零")

VERDICT = ("GREEN: r853 (S0 36-UU rebase surgery closed zero-loss, 3 origin-contaminated faces healed upstream; "
           "T23 census honest awaiting_panel 4805/5217=92%; W207 M9 wait on W206; S6 40/41 rc0 + known alloc rc2; "
           "tasks ALIVE; attrition CLEAN; one domain law appended to rebase2 per r666 direct-write)")

# --- state.json ---
sp = os.path.join(REPO, 'state.json')
d = json.load(open(sp, encoding='utf-8'))
d['round_no'] = 853
d['round_no_label'] = 'r854'
d['note'] = DID
d['did'] = DID
d['last_action'] = DID
d['verdict'] = VERDICT
d['task'] = R854_QUEUE
d['next'] = R854_QUEUE
d['current_task'] = R854_QUEUE
d['now_active'] = 'r853 closeout: S0 rebase surgery closed (36-UU, 62-face delta marker gate clean); T23 awaiting_panel 92%'
d['latest_artifact'] = ('r853: results/_r853bmb_rebase_resolver.py (36-UU dual-pick rebase resolver, five fail-closed gates, '
                        'receipt _r853bmb_rebase_resolver.json) + results/_r853bmb_s6chain.log (41 legs) + '
                        'research/pit-git-resolver-rebase2.md r853 domain law (delta-scope marker gate + dual-precision ts probe)')
d['next_milestone'] = ('astock panel complete (~02:2x) -> detached T23 census full burn -> holds verdict (window <=10-11 06:00) '
                       '-> N2 U3(1) prereg window / G2 fallback; O-20261011-0012 条款4 pool+matrix claim at rebuild completion; '
                       'W207 five-face freeze via staged _w207bmb_freeze_edits.py once W206 five-face+finalize land (M9)')
for k in ('last_round_at', 'last_seen', 'updated', 'ts', 'clock_read', 'last_round_ts', 'updated_at'):
    d[k] = now_iso
d['last_orders_at'] = now_iso
d['d19_watermark_guard']['round_ref'] = 853
d['d19_watermark_guard']['ts'] = now_iso
d['round'] = 853
d['heartbeat_epoch_utc_face'] = 'kept in fleet/machines/bm-b.json'
open(sp, 'w', encoding='utf-8', newline='').write(json.dumps(d, indent=1, ensure_ascii=False))
print('state.json -> round 853')

# --- heartbeat ---
hp = os.path.join(REPO, 'fleet', 'machines', 'bm-b.json')
h = json.load(open(hp, encoding='utf-8'))
h['round'] = 853
h['round_no'] = 853
h['now_active'] = 'r853 closeout: S0 rebase surgery closed (36-UU dual-pick); T23 census awaiting_panel 4805/5217=92%'
h['current_task'] = R854_QUEUE
h['task'] = R854_QUEUE
h['next'] = R854_QUEUE
h['latest_artifact'] = d['latest_artifact']
h['next_milestone'] = d['next_milestone']
h['verdict'] = VERDICT
h['last_action'] = DID
h['did'] = DID
for k in ('last_round_at', 'last_seen', 'updated', 'ts', 'clock_read', 'updated_at'):
    h[k] = now_iso
h['heartbeat_epoch_utc'] = epoch
h['cpu_cores'] = 16
h['free_ram_gb'] = free_gb
h['ram_free_gb'] = free_gb
h['ram_free_pct'] = ram_free_pct
h['gpu_free_vram_mb'] = 3573
h['gpu_free_vram_gb'] = 3.57
h['vram_free_gb'] = 3.57
h['idle_rounds'] = 0
h['agenda_starved'] = False
h['orphan_faces'] = 0
h['orphan_face_note'] = 'round-zero probe 01:22 py_faces=12 orphans=0 (read-only)'
h['sync'] = {"last_push_ts": now_iso, "note": "r853 closeout push; post-push behind=0 self-proof below"}
open(hp, 'w', encoding='utf-8', newline='').write(json.dumps(h, indent=1, ensure_ascii=False))
chk = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178 law)'
assert 'T' in chk['clock_read'], 'clock_read must be T-separated (R262 law)'
print('heartbeat -> round 853; epoch int OK; free RAM', free_gb, 'GB /', total_gb, 'GB; audit py_cpu', py_cpu)

# --- round report line ---
rp = os.path.join(REPO, 'logs', 'iteration-loop', 'round_reports.md')
raw = open(rp, 'rb').read()
t = raw.decode('utf-8')
crlf = t.count('\r\n'); lf = t.count('\n') - crlf
EOL = '\r\n' if crlf >= lf else '\n'
if not t.endswith(EOL):
    t += EOL
line = EOL.join([
 f"{now_iso} | r853 bm-b | dept:工程（S0 冲突窗手术+stewardship 等待窗守护+S6 链） | WM-VERDICT: green（red=false @01:27 probe·next_pick=moneyflow IC claimed advisory·py 低位=astock 全宇宙重建网络限速拉取型合法·audit py_cpu={py_cpu}） | 孤儿面=0（round-zero probe 01:22 py_faces=12 orphans=0） | CEO three-line: 当前活=S0 rebase 冲突窗手术收口+T23 census 等待窗守护+S6 41 腿；最近实物=results/_r853bmb_rebase_resolver.py（36-UU 双 pick 手术·receipt _r853bmb_rebase_resolver.json·01:3x）+results/_r853bmb_s6chain.log（41 腿 40 rc0）+research/pit-git-resolver-rebase2.md 域律一条（01:5x）；下个里程碑=astock 面板完备（~02:2x±）→detached T23 census 全量烧录→census_holds 判读（窗≤10-11 06:00）→N2 U3(1) prereg 窗/G2 学术引用回退；O-20261011-0012 条款4=重建完毕即认领池面+矩阵切片；W207 M9 窗（上游 W206 五面+finalize 未落→跑 _w207bmb_freeze_edits.py staged @r852）",
 "did: S0 轮首 churn absorb（f0a7c8bd9）后 pull --rebase 撞 bm-c r843+bm-a r963 新面=36-UU 双 pick 窗（31 主窗=两机 S6 同日再生成面对撞+5 absorb 窗=daemon churn 面）——resolver results/_r853bmb_rebase_resolver.py 按 r782/r917/r794/r516/r642 配方：ls-files-u sha 通道逐面·ts 双精度深扫（秒级+分钟级·p1d_gates 分钟精度假闭已治）·payload-equal-newer-ts·jsonl line-union（x2_watch+satengine history）·ledger superset 探针·r648 污染面治愈三面（LIVE-2026-10-11.md×2+dashboard_status.js=origin 侧提交面自带冲突标记入库→取我方 r852 干净 blob·随重放治愈上链）·fail-closed 五门全过 31+5；de511e985+4a6d7e7e6 两 pick 重放成功→delta 标记门 62 面干净（全树扫描撞 r505/r506 史迹取证面=假阳性·delta 化域律已入 rebase2）→push 4a6d7e7e6 behind=0 自证",
 "S0.5: 令差集 zero（67 件全 ack）+D19 双水位恒等（dec caca0c6e/ord 4d33cb4f·r779 三步法 r852 已证）+inbox 两件（bm-c→bm-a MSG+本机 r852 出件）均非本机收件零处理；S1 smoke 49/49；S2 板空三查（job_list 0·fleet/tasks 0 open·水位绿）+引擎活 rc0 idle queue 0；S3: T23 slice-2 status 门=awaiting_panel 诚实（disk-truth 4805/5217=92%·pace ~11/min·ETA~02:2x·census 零烧零写）·W207=M9 守望 W206 未落（r852 已实弹两门不重扫）·条款4=重建完毕即认领等待态·意义性律维持（O-20260930-1901 零为烧而烧）；S6 41 腿=40 rc0+alloc rc2 已知 510880（P5 slot TRANSFER 待办）·dualrun streak 8；S4=域律一条直写 rebase2（rebase 收口 tip 标记门 delta 化+resolver ts 探针双精度化+r648 续证·1,264B·主件 30,510B 贴帽走 r666 直写例外·rebase2 4,139B 远离帽）；S7 四任务 ALIVE rc0（loop no-op pin=2·watchdog 幂等重注册·双爪恒等重装）+attrition CLEAN（4 ledger·历史缩行 healed）+idle --worked 清零",
 "本地未达 origin commit 数=0（收口 push 后 fetch+ls-remote 自证）；下轮指针 r854：astock 完结核验→分离 T23 census 全量烧录（runner 预验证 21/21·panel 门 disk-truth law）→holds 判读（窗≤06:00）→N2 U3(1) prereg 窗/G2 回退；条款4 池面+矩阵切片认领；W207 M9 窗",
]) + EOL
t += line
open(rp, 'wb').write(t.encode('utf-8'))
print('round report line appended; report EOL =', repr(EOL))
print('CLOSEOUT WRITE OK @', now_iso)
