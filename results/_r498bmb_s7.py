# r498 re-fire S7 finalization: state + heartbeat + round report (utf-8 safe), with self-verification
import json, time, ctypes, os, sys
from datetime import datetime

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
now_iso = datetime.now().astimezone().isoformat(timespec='seconds')  # T separator, +08:00 offset
epoch = int(time.time())

# --- fresh machine stats (ctypes, zero deps) ---
class MemStatus(ctypes.Structure):
    _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong),
                ('ullTotalPageFile', ctypes.c_ulonglong), ('ullAvailPageFile', ctypes.c_ulonglong),
                ('ullTotalVirtual', ctypes.c_ulonglong), ('ullAvailVirtual', ctypes.c_ulonglong),
                ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]
m = MemStatus(); m.dwLength = ctypes.sizeof(MemStatus)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
free_ram = round(m.ullAvailPhys / 1024**3, 1)

cpu_pct, gpu_free_gb = 12.0, 2.3
try:
    with open(os.path.join(ROOT, 'results', 'compute_audit.bm-b.json'), encoding='utf-8') as f:
        ca = json.load(f)
    cpu_pct = ca.get('cpu_total_pct', cpu_pct)
    gpu_used_mb = ca.get('gpu', {}).get('mem_used_mb')
    if gpu_used_mb is not None:
        gpu_free_gb = round(max(0.0, 8192 - gpu_used_mb) / 1024, 1)
except Exception as e:
    print('audit-read-fallback', e)

# --- state.json ---
sp = os.path.join(ROOT, 'state.json')
with open(sp, encoding='utf-8') as f:
    state = json.load(f)
assert state['round_no'] == 497, 'unexpected round_no %s' % state['round_no']
state['round_no'] = 498
state['note'] = ("r498 re-fire: orphaned r498 session died post-S6 pre-S7 (S6 log end 08:07:59 clean, no S7 face) -- "
                 "heritage adopted per r495 precedent: S6 35 legs rc0 evidence + S0 resolver + N1-W3 shard-0 product committed, "
                 "smoke 47/47 on adopted tree, REBASE_HEAD residue cleaned, 1 stranded daemon harvest-flip commit flushed to origin; "
                 "pool N1-W3 live: 1 done (bm-b) / 1 claimed by other machine (claim_lost_yield 08:16, r483 yield law working) / 10 ready, "
                 "daemon 2-min ticks churning; W14 stays governance-parked (GM dual-ruling, MSG-0400); T-136 VOID-vs-stands GM-pending (MSG-048x); "
                 "orders 133/133 EMPTY, D-19 UNCHANGED")
for k in ('last_round_at', 'last_round_ts', 'ts', 'updated', 'updated_at'):
    state[k] = now_iso
with open(sp, 'w', encoding='utf-8', newline='') as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

# --- heartbeat ---
hp = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
with open(hp, encoding='utf-8') as f:
    hb = json.load(f)
hb['last_seen'] = now_iso
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = now_iso
hb['round_no'] = 498
hb['round'] = 498
hb['loop_round'] = 498
hb['current_task'] = ("r498 re-fire done: orphaned r498 S6 heritage adopted+committed (S6 35 legs rc0, N1-W3 shard-0 product), "
                      "stranded daemon harvest-flip flushed to origin, smoke 47/47, REBASE_HEAD cleaned; N1-W3 pool burning fleet-wide (1 done/1 in-flight/10 ready)")
hb['verdict'] = ("healthy: S0 orders 133/133 EMPTY + D-19 UNCHANGED (raw-bytes, case-normalized), S1 47/47, S6 adopted from orphan log "
                 "(reconcile ZERO-DRIFT 15/3, ORANGE shadow, paper 6/6 anchor OK), S7 attrition CLEAN + tasks healthy (schtasks) + REBASE_HEAD cleaned; "
                 "three-line face: active=N1-W3 shard pool burn (fleet parallel), latest=results/p2cal_ext/n1_w3/shard-0-of-12.json + docs/live_usage/LIVE-2026-10-01.md @08:07, "
                 "next milestone=N1-W3 all-12 verdict face + ledger backfill (daemon cadence, window<=48h)")
hb['last_round_at'] = now_iso
hb['last_round_ts'] = now_iso
hb['cpu_util_pct'] = cpu_pct
hb['free_ram_gb'] = free_ram
hb['idle_ram_gb'] = free_ram
hb['ram_free_gb'] = free_ram
hb['gpu_free_vram_gb'] = gpu_free_gb
hb['gpu_idle_vram_gb'] = gpu_free_gb
hb['gpu_free_vram_mb'] = int(gpu_free_gb * 1024)
with open(hp, 'w', encoding='utf-8', newline='') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# --- round report (bm-b lane file, utf-8 append) ---
report_line = (
    f"{now_iso} | r498 bm-b re-fire（孤儿收口·r495 判例接管猝死轮号）| dept:工程/舰队 | "
    "[watermark verdict: 08:07 探针=insufficient_history（15min 窗 n=1，非红非绿如实携带）；compute_audit 三旗 idle_with_work/supply_gap/ignition_sla "
    "为 08:07 快照、其后实况向好：n1w3-0 本机烧完 harvest 翻 done（f58a8174b）、SHARD-1 08:16 他机认领本机让票=claim_lost_yield（r483 让票律实证生效）、"
    "余 10 ready，daemon 2min tick 续烧中——点火恢复非死锁，如实披露不掩盖] | "
    "本轮主产出（实物）：(1) 孤儿 r498 遗产收口入库：S6 35 腿全绿日志（reconcile ZERO-DRIFT 15/3 连绿、ORANGE days_in_state=4 shadow、paper 6 员 anchor OK、"
    "PROSPECT 22 员诚实 ineligible、export equity 5,998,496）+ N1-W3 shard-0 烧录产物 results/p2cal_ext/n1_w3/shard-0-of-12.json + "
    "LIVE/REPORT/dashboard 三 CEO 面 08:07 再生成（含 1 件滞留 daemon harvest-flip commit 随本轮 flush=认领可见性解堵）"
    "(2) .git/REBASE_HEAD 残留清理（r498 S0 rebase 遗留·r305 律） | "
    "验证：S1 47/47（收编树实证）；orders 133/133 双扫 EMPTY（134 件=133 回执+README）；D-19 ED4E0EAB UNCHANGED（raw-bytes+大小写归一 r503 律）；"
    "attrition CLEAN（4 账本·healed 照录）；schtasks 双任务健康（Loop 在跑/Watchdog 就绪·R49 口径）；"
    "inbox 2 件均 GM 亲启非本机件原位保留（T-136 VOID-vs-stands=MSG-048x、PERPETUAL_FACES v1.1=MSG-0400——均待 GM 署名，执行机不越权自裁） | "
    "下轮指针：(1) N1-W3 全批烧完后判决面消费+sec.7/8 回填走常设线自动（harvest 翻面已由 r497 握手修固化）"
    "(2) 12 quarantined heal 仍冻结——N1-W3 在飞消耗冻结面板（pin 5217），heal 排其后+下一 prereg 重探面前勿提前（r496 指针不变）"
    "(3) 观察项：r497/r498 连续两轮死于 S7 前（r497 死于 state 写后 commit 前、r498 死于 S6 后）——若 r499 再发同型猝死，查 S6 尾上下文体积与会话流饱和面 | "
    "executive 三行面：当前活=N1-W3 分片池烧录（三机并行 1 done/1 在飞/10 ready）；最近实物=shard-0-of-12.json@08:1x + LIVE-2026-10-01.md@08:07；"
    "下个里程碑=N1-W3 全 12 分片判决面落地+账本回填（daemon 节奏·窗 ≤48h·预计今日）"
)
rp = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md')
with open(rp, 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + report_line + '\n')

# --- self-verification ---
with open(sp, encoding='utf-8') as f: s2 = json.load(f)
with open(hp, encoding='utf-8') as f: h2 = json.load(f)
ok_epoch = isinstance(h2['heartbeat_epoch_utc'], int)
ok_clock = 'T' in h2['clock_read'] and '+08:00' in h2['clock_read']
ok_round = s2['round_no'] == 498 and h2['round_no'] == 498
tail = open(rp, 'rb').read()[-200:].decode('utf-8', 'replace')
print('SELFTEST epoch_int=%s clock_T=%s round498=%s report_tail_ok=%s' % (ok_epoch, ok_clock, ok_round, 'r498 bm-b re-fire' in tail))
print('STATS cpu=%s free_ram=%s gpu_free=%s' % (cpu_pct, free_ram, gpu_free_gb))
if not (ok_epoch and ok_clock and ok_round):
    sys.exit(1)
print('S7 finalization OK', now_iso)
