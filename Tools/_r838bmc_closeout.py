# r838 bm-c closeout: state + heartbeat (load-modify-save per r818 law) + round report line
import json, time, datetime, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def p(rel): return os.path.join(ROOT, rel)

NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")
EPOCH = int(time.time())

ACT = ("当前活: r838 收口——r836 ceremony 债全销（主件指针行+登记册行+回扫 4 条）+S6 43 腿 rc0+T-183 防重复 MSG 出站 | "
"最近实物: CODELY.md r836 指针行+回扫（30,560→28,940B 恒等·receipt _r838bmc_codely_ceremony.json）+TREASURE_REGISTRY 出入行+pit 4 域件迁移落位 "
"@ " + TS + " | 下个里程碑: D-05 写腿（10-11 00:00 常务轮首位）+pit-protocol.md 越帽 sub-split（下窗）+T-182 co-sign（10-16 白话报告窗）")

VERDICT = ("r838 bm-c: r836 ceremony debt discharged in full (main pointer row + registry row + 4-entry re-scan migration, "
"byte identity 30560-2727+1107=28940<=cap, receipt _r838bmc_codely_ceremony.json) + S4 EOL-mixed-surgery law into main (29,734B) + "
"T-183 anti-dup MSG to bma (bmb r838 delivered ce7d437d0, r959 face=verify-only per ticket resolution) + S6 43/43 rc0 + S7 quartet green "
"(pin=5 no-op, watchdog alive, both claws CR-normalized identical) + attrition 4 ledgers CLEAN + d19 NOOP read-back equal + idle --worked; "
"pool zero bm-c-claimable faces (all done / bm-a lane), W17-JUDGE burning on bma; tech T23 + W18 yielded to bmb declared faces; "
"honest disclosure: pit-protocol.md 31433B>30720B since r859 bma 10-08 = protocol-domain sub-split debt next window")

REPORT = ("2026-10-10T20:56:17+08:00 | r838 | dept:工程/舰队（r836 ceremony 债销账轮+S6 43 腿+T-183 防重复协调） | "
"本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） | "
"WM-VERDICT: 绿（red=false·lane=healthy·池无可认领面〔全 done/bm-a-lane〕·W17-JUDGE bm-a 烧收在飞） | "
"孤儿面=1（ComfyUI 8188 影片链服务面·只读探针 killed=[]·r829 判例不触） | "
"r838 bm-c: ①S0.5 双 delta FALSE（DEC 34cf2538/ORD e20de2d6 恒等零动作·unacked=[]·s05 血统件实弹）；"
"②**r836 ceremony 债全销**：根 CODELY.md 主件 r836 域件 sub-split 指针行补入（pit-git-resolver-rebase2 子件披露·1,106B）"
"+TREASURE_REGISTRY 出入记录行 append（956B·r791 三件齐格式·prescan rc3 留痕=D-06 授权通道）"
"+主件回扫批 4 条 verbatim 迁出（r818→pit-protocol-lane 789B/r819→pit-protocol-d19 548B/lhb 首列坑→pit-data 533B/r824→pit-git-staged 853B）"
"·字节恒等 30,560-2,727+1,107=28,940 <=30KB·回执 results/_r838bmc_codely_ceremony.json+S4 新律入主件（EOL 混态手术律·主件 29,734B）；"
"③队列面=T23（N2 U3 alphagen 评估片）bm-b r840 已声明让路+W18 drain-gated（W17-JUDGE 在飞）让路"
"+T-183 三机竞速防重复 MSG 出站（bm-b r838 已交付 ce7d437d0+selftest 43/43·bm-a r959 在飞窗未见·票面 resolution 自洽·r959 face=verify-only）；"
"④L54 观察=W204 12/12 分片烧毕（dedup local/remote 双 12·引擎路径）·bm-a W17-JUDGE autofill 认领=首燃在案·bm-c 无可认领分片待池面；"
"⑤诚实披露=pit-protocol.md 31,433B>30,720B（r859 bm-a 10-08 追加起·协议域下窗 sub-split 债登记）；"
"⑥S6 43/43 rc0（周末数据腿诚实 no-op·驱动 _r838bmc_s6.py）+S7 四件套绿（pin=5 no-op·watchdog 活·双爪 CR 归一恒等）"
"+attrition 4 台账 CLEAN+d19 NOOP 读回恒等+idle --worked 0 | "
"下轮指针: r839 ①D-05 写腿=10-11 00:00 常务轮首位 ②pit-protocol.md 越帽 sub-split ceremony（协议域债）"
"③W17-JUDGE drain 观察+W18 berth 门复核 ④T-182 co-sign 待 bm-a runner（10-16 窗）⑤10-14 政体验证窗 v1.1 re-cut")

NEXT = ("r839 续作: ①D-05 写腿=10-11 00:00 常务轮首位 ②pit-protocol.md 31,433B 越帽 sub-split ceremony（协议域债·r859 起）"
"③W17-JUDGE drain 观察+W18 berth 门复核（drain-gated）④T-182 co-sign 待 bm-a P0 runner 产物（10-16 白话报告窗）⑤10-14 政体验证窗 v1.1 re-cut")

def load(path):
    b = open(path, 'rb').read()
    bom = b.startswith(b'\xef\xbb\xbf')
    return json.loads(b.decode('utf-8-sig')), bom

def save(path, obj, bom):
    out = json.dumps(obj, ensure_ascii=False, indent=1)
    data = out.encode('utf-8')
    if bom: data = b'\xef\xbb\xbf' + data
    open(path, 'wb').write(data)

# --- state file ---
S = p('state-bm-c.json')
st, bom = load(S)
st['round_no'] = 838
st['round_no_label'] = 'round 838 (bm-c)'
st['loop_round'] = 838
st['last_round'] = 838
st['clock_read'] = TS
st['ts'] = TS
st['updated'] = TS
st['updated_at'] = TS
st['last_round_at'] = TS
st['last_round_closed'] = TS
st['last_seen'] = TS
st['current_task'] = ACT
st['current_task_at'] = TS
st['activity_now'] = ACT
st['did'] = VERDICT
st['last_action'] = VERDICT
st['verdict'] = VERDICT
st['next'] = NEXT
st['next_pointer'] = NEXT
st['next_milestone'] = 'D-05 write leg (10-11 00:00 first) + pit-protocol.md sub-split + T-182 co-sign (10-16 window)'
st['latest_artifact'] = ('CODELY.md r836 pointer row + 4-entry re-scan (receipt _r838bmc_codely_ceremony.json) + '
                         'TREASURE_REGISTRY ceremony row + MSG-2026-10-10-2057 T-183 anti-dup')
st['last_artifact'] = st['latest_artifact']
st['recent_artifact'] = st['latest_artifact']
st['orphan_face'] = 1
st['orphan_faces'] = 1
st['idle_rounds'] = 0
st['agenda_starved'] = False
st['heartbeat_epoch_utc'] = EPOCH
st['last_decisions_at'] = TS
st['last_orders_at'] = TS
st['last_decisions_read_at'] = TS
st['last_orders_read_at'] = TS
st['free_ram_gb'] = 4.1
st['idle_ram_gb'] = 4.1
st['ram_free_gb'] = 4.1
st['gpu_free_vram_mib'] = 14392
st['gpu_free_vram_mb'] = 14392
st['gpu_vram_free_mb'] = 14392
st['gpu_idle_vram_mb'] = 14392
st['gpu_idle_vram_mib'] = 14392
st['cpu_pct'] = 53
st['cpu_util_pct'] = 53
st['cpu_idle_pct'] = 47
if 'd19_watermark_guard' in st:
    st['d19_watermark_guard']['round_ref'] = 838
    st['d19_watermark_guard']['ts'] = TS
save(S, st, bom)

# --- heartbeat (orders_ack list preserved untouched) ---
H = p('fleet/machines/bm-c.json')
hb, bom2 = load(H)
ack_before = len(hb.get('orders_ack', []))
hb['clock_read'] = TS
hb['ts'] = TS
hb['updated'] = TS
hb['updated_at'] = TS
hb['last_seen'] = TS
hb['current_task'] = ACT
hb['current_task_at'] = TS
hb['activity_now'] = ACT
hb['did'] = VERDICT
hb['last_action'] = VERDICT
hb['verdict'] = VERDICT
hb['next'] = NEXT
hb['next_pointer'] = NEXT
hb['next_milestone'] = st['next_milestone']
hb['last_round'] = 838
hb['last_round_at'] = TS
hb['round_no'] = 838
hb['round_no_label'] = 'round 838 (bm-c)'
hb['loop_round'] = 838
hb['heartbeat_epoch_utc'] = EPOCH
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['cores'] = 32
hb['cpu_cores'] = 32
hb['cpu_pct'] = 53
hb['cpu_util_pct'] = 53
hb['cpu_idle_pct'] = 47
hb['free_ram_gb'] = 4.1
hb['idle_ram_gb'] = 4.1
hb['ram_free_gb'] = 4.1
hb['total_ram_gb'] = 25.7
for k in ('gpu_free_mib', 'gpu_free_mb', 'gpu_idle_mib', 'gpu_idle_mb',
          'gpu_idle_vram_mb', 'gpu_idle_vram_mib', 'gpu_free_vram_mb', 'gpu_free_vram_mib', 'gpu_vram_free_mb'):
    hb[k] = 14392
hb['latest_artifact'] = st['latest_artifact']
hb['last_artifact'] = st['latest_artifact']
hb['recent_artifact'] = st['latest_artifact']
hb['last_decisions_at'] = TS
hb['last_orders_at'] = TS
hb['health'] = 'ok'
save(H, hb, bom2)
assert len(hb.get('orders_ack', [])) == ack_before, "orders_ack list mutated!"
assert isinstance(hb['heartbeat_epoch_utc'], int)

# --- round report line (EOL-matched append) ---
R = p('round_reports-bm-c.md')
b = open(R, 'rb').read()
eol = b'\r\n' if b.count(b'\r\n') > b.count(b'\n') - b.count(b'\r\n') else b'\n'
if not b.endswith(eol):
    b = b + eol
b = b + REPORT.encode('utf-8') + eol
open(R, 'wb').write(b)

print("state round_no -> 838 | heartbeat epoch", EPOCH, "int | ack", ack_before, "| report line appended (", len(REPORT), "chars,", eol, ")")
print("now:", TS)
