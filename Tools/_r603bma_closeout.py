"""r603 bm-a bookkeeping four: state/heartbeat/round-report/CODELY + inbox
move. Bytes-safe (r530), int epoch (R170/R178), T-format clock (R262)."""
import json, os, shutil, time
from datetime import datetime, timezone, timedelta

NOW = datetime.now()
TS = NOW.strftime('%Y-%m-%d %H:%M')
CST = timezone(timedelta(hours=8))
ISO = NOW.astimezone(CST).strftime('%Y-%m-%dT%H:%M:%S+08:00')
EPOCH = int(time.time())

# --- 1. state ---
sp = 'state-bm-a.json'
raw = open(sp, 'rb').read()
s = json.loads(raw.decode('utf-8'))
assert s['round_no'] == 602, s['round_no']
s['round_no'] = 603
s['did'] = ('FUND-VALUE-P1 fleet unblock per MSG-0230 + wedge root-fix + '
            'VALUEPE-X2 burn delivered (401 cells, claim closed ok)')
s['verify'] = ('smoke 47/47; S6 34 legs rc0; dualrun ZERO-DRIFT 51/3; '
               'attrition CLEAN; x2 contract closed_at 02:58:28 exit 0')
s['next'] = ('engine drains VALUEPB-X1/X2 + NULLS shards (host-gated, '
             'sequential per-machine); then batch finalize; N4-B1 '
             'deliverable (5) adapter next window')
s['last_round_at'] = TS
s['updated'] = TS
s['last_round'] = 602
s['last_round_ts'] = TS
open(sp, 'wb').write((json.dumps(s, ensure_ascii=False, indent=1)
                     .replace('\n', '\r\n')).encode('utf-8'))
chk = json.loads(open(sp, 'rb').read().decode('utf-8'))
assert chk['round_no'] == 603
print('[state] round 603 written (CRLF preserved)')

# --- 2. heartbeat ---
hp = 'fleet/machines/bm-a.json'
h = json.loads(open(hp, 'rb').read().decode('utf-8'))
h['last_seen'] = ISO
h['heartbeat_epoch_utc'] = EPOCH
h['clock_read'] = ISO
h['current_task'] = ('FUND-VALUE-P1 re-ignition on bm-a: X2 delivered '
                     '(401 cells closed ok 02:58), PB-X1/PB-X2/NULLS '
                     'queued via engine ticks (host-gated)')
import psutil
h['cpu_pct'] = round(psutil.cpu_percent(interval=1), 1)
h['free_ram_gb'] = round(psutil.virtual_memory().available / (1 << 30), 1)
h['verdict'] = ('r603: FUND-VALUE-P1 fleet unblock (MSG-0230 response: 5 '
                'fuse sigs data_fixed-cleared, phantom bm-c claims '
                'stripped from shared+bm-b lane, host_gates x5) + X2 burn '
                'delivered on bm-a; 3 shards engine-draining; next = '
                'batch finalize + N4-B1 deliverable (5)')
open(hp, 'wb').write((json.dumps(h, ensure_ascii=False, indent=1)
                     .replace('\n', '\r\n')).encode('utf-8'))
chk = json.loads(open(hp, 'rb').read().decode('utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read']
print('[heartbeat] epoch int verified:', chk['heartbeat_epoch_utc'])

# --- 3. round report ---
rp = 'round_reports-bm-a.md'
line = (
    f"{TS} | dept:工程+研究 | watermark verdict=绿（red=false·probe py 41.9% 采样窗重启 n=1 非故障）| "
    "本轮主产出=FUND-VALUE-P1 舰队解锁+再点火（MSG-0230 响应）："
    "①5 个 fund_value_p1 fuse sigs 按 data_fixed 家族清除（墓碑 cleared_ts 02:44:54>全 lane 尾事件 02:42/02:44·bm-c keep-blocked note 保入 bm_c_note 字段·SENS 墓碑盖 bm-b 02:44:16 同合并结果双档）；"
    "②楔死根治=bm-b 0951ab44a settle 从其 lane 残留把 4 行幽灵 bm-c claim（owner_since 02:06-02:09）重新物化上 origin——接管门 min(活机心跳,claim 龄) 使幽灵行恒 fresh=机队任何 tick 永不可接管（结构楔死）；共享面+复活源 bm-b lane 双剥（raw-text r509·owner_since 唯一锚·池 9+/12- 外科断言过）+bm-b 新鲜 SENS claim 02:44:16 原样保留；"
    "③5 条目加 claim-time host_gates（dir_nonempty Money02/data/cache/p1c_stock *.npy）=bm-c 数据缺件面机械隔离（r316 族根治·本机探针 15 npy PASS）；"
    "④bm-a fuse/pool lane 双轨重镜像（幽灵 owner 预防律）；"
    "**最近实物=results/fund_value_p1/cells_VALUE-PE_x2.jsonl（401/401 cells 全窗判决胞）+cont_VALUE-PE_x2.json——claim 合同 closed ok 02:58:28 exit 0（本机 tick 02:52:12 认领+点火→6min16s 烧毕，32 workers BelowNormal）**；"
    "bm-b 面 SENS 在烧（02:44:16 认领）；余 3 分片（VALUEPB-X1/X2+NULLS）host-gated ready，引擎 tick 串行自排水（no-double-run 同 runner 机内串行设计）；"
    "下个里程碑=3 分片烧完（窗≈03:40 前后）→6/6 收口 finalize 判决判决面（D6+judged 面·窗≤48h→10-05）+N4-B1 deliverable (5) SatEngine FAMILIES 适配器；"
    "验证证据=smoke 47/47+S6 34 腿全 rc0（周末窗数据腿 no-op 合法·reconcile ZERO-DRIFT 51 连绿·moneyflow/ah_panel 分离刷新合法 spawn·车道护栏诚实 no-op）+attrition guard CLEAN+S7 自愈 4/4（loop pin :8 no-op+watchdog 重注册+双爪字节装）+orders 150/150 双扫差集 0；"
    "D-19 集团决策台账=S4U 无 K: 盘验证 skip（r597 律·Test-Path False 实证·last_decisions_sha 937A373D 不动）；"
    "本地未达 origin commit 数=0（push 后 fetch+ls-tree 自证）。—via bm-a r603"
)
with open(rp, 'ab') as fh:
    fh.write((line + '\r\n').encode('utf-8'))
print('[round-report] r603 line appended')

# --- 4. CODELY lesson ---
cl = (
    "\r\n"
    "- [2026-10-03 03:0x r603 bm-a] lane 残留幽灵 claim×活机心跳=永久接管楔死坑"
    "（FUND-VALUE-P1 四分片实弹·bm-c r393-fix 姊妹面）：claim 释放须全 lane 面净——"
    "bm-c 双面释放自家 lane 后，bm-b lane 镜像仍持 02:06-02:09 四行幽灵 bm-c claim，"
    "其 0951ab44a settle（merged view 物化）把幽灵 owner 重新写上 origin；接管门="
    "min(owner 心跳龄, claim 龄)<STALE_MIN=20，活机 bm-c 心跳恒新鲜→幽灵行恒 fresh="
    "机队任何 tick 永不可接管（结构楔死非 10min 暂态）。根治三件=①共享面+复活源 lane"
    "（bm-b）双剥幽灵行对（raw-text r509·owner_since 值唯一锚·外科 numstat 断言）"
    "②fuse 清除墓碑 cleared_ts 必须>全部 lane 面尾 refusal/crash ts 否则合并复活"
    "（本窗 02:44:54>02:42/02:44 实证·lane fuse 镜像同步三面一致）③数据根因批"
    "（r316 族）重认领前加 claim-time host_gates（autofill _host_gate_reason "
    "dir_nonempty·认领时本机复检 fail-closed）=缺件机机械隔离禁烧。How to apply："
    "claim 释放/让路动作必双面（共享+lane）+扫他机 lane 残留同 key 行；fuse 手工清除"
    "取动作时刻勿取注册时刻；数据前置批一律登记 host_gates。正典=本行+"
    "Tools/_r603bma_wedge_rootfix.py。\r\n"
)
with open('CODELY.md', 'ab') as fh:
    fh.write(cl.encode('utf-8'))
print('[CODELY] r603 lesson line appended')

# --- 5. inbox move ---
src = ('fleet/inbox/MSG-2026-10-03-0230-bmc-ALL-'
       'fundvalue-claims-released.md')
dst = 'fleet/inbox/processed/' + os.path.basename(src)
assert os.path.exists(src)
shutil.move(src, dst)
print('[inbox] MSG-0230 -> processed (responded via MSG-0255 + action)')
