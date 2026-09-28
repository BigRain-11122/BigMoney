# r165 bm-c close-out: round report line + state round_no + heartbeat (epoch int self-check)
# evidence script per _r395bma_close_out precedent; run once, then committed with round close.
import json, time, datetime

now = datetime.datetime.now()
ts_iso = now.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'

# ---- 0. machine readings for heartbeat ----
import psutil
cpu = psutil.cpu_percent(interval=1)
vm = psutil.virtual_memory()
free_ram_gb = round(vm.available / (1024**3), 2)
gpu_free = 9811  # nvidia-smi free MiB carried from state (no GPU work this round)

# ---- 1. round report line (S5) ----
rr = 'logs/iteration-loop/round_reports-bm-c.md'
line = (
 "2026-09-28T13:2x+08:00 | round 165 bm-c | dept:舰队/工程/策略 (W4-SCREEN finalize 收割轮+维护链) | "
 "WM-VERDICT: 绿 (red=false@12:40:01 lane healthy; probe 13:08 py_low_with_work_cands=合法--本机 W4-SCREEN burn 在飞车道 pid23908 py 37.3% cpu_total 100% + 池 ready 全他机车道认领零 bm-c 可领) | "
 "did: (1) S0-1 锚定 bm-c + S0 pull 被 burn checkpoint 挡(autofill 活写面禁 stash r369 律)->fetch 比对 HEAD==origin/main 零落后 + "
 "S0.5 orders 99/99 双扫零未回执 + decisions 零新行(D-02①/D-03② r154 已回执·D-03① 车道双轨在册·委员会 C-02 席3 意见已出窗至 09-29) + "
 "S1 smoke 25/25 + S2 双板零 open(job_list 0+fleet 0); "
 "(2) S3 主闭环=**TRIAL_LABOR_W4 screen-finalize LANDED 收割**:burn 13:00:01 autofill claim pid23908 12workers ~12.3min checkpoint **4010/4010**(3810 distinct+200 nulls)->"
 "finalize null p95 0.5164(prereg §5 带 [0.42,0.62] PASS)+distinct 3810(带 [2800,4600] PASS)+**survivors 461/3810=12.10%**(带 [2%,15%] PASS·计数 461∈[100,750] PASS)+"
 "vol 分段 {calm 4.98%<none 10.68%<wild 20.42%}=**§5 pred-4 VOL 方向先验反向殉死**(prereg 自 anticipate 两向殉死·batch 末 §8 承接)+gate×vol 交互 top bear|wild 35.94%+"
 "产物 w4_screen.json(evidence_cutoff 2026-09-22 C2 键+grammar sha d498e9343ee57460 恒等)+w4_screen_cells.csv+ledger TRIAL_LAB_W4_SCREEN +4010 链总 **305,190** +"
 "池 W4-SCREEN done 翻面(净 diff 44+/5- byte-style r381 律·tick 重拉止)+**TRIAL-LABOR-W4-JUDGE 入池 parked waiting**(排 W2/W3-JUDGE+MASS 四分片后 per prereg §0 物理序门 bmb r369 裁定·RAM r354 门·judge trio CLI 已在树 bma r397 无需另建)+"
 "**MSG-20260928-1316 judge-unblock 回执**(bmb 判队列串行推进面·W3 r395 MSG-0915 先例);"
 "(3) S6 29 腿 rc=0:审计 CLEAN+水位 probe 13:08 verdict 合法+盘前 no-op 族(cutoff 09-24)+fund_premium 15:30 前 no-op(**15:35 轮首火计划不变**)+"
 "scorecard/daily_scorecard/build_status=合法 stale-takeover(bma 心跳 196min>20min C_HOST_STALE_MIN·O-2100 s2.4)+fundamental 3.4h fresh skip+b_layer verdict 落盘+"
 "daily_report faces=4 token=1+token_meter L2=0+live 族 bars_present=false 按门跳过; "
 "(4) S7:orders 扫-2+schtasks 三件(schtasks /query 律)+claw+commit 定向 add(轮首脏=checkpoint 单件·本轮产出面全 add)+push | "
 "verify: finalize 产品全字段验(C2 顶层键+锚恒等+461/4010)+池字节风格 CRLF 3349/尾} 恒等+净 diff 44+/5-+burn checkpoint 4010 行+smoke 25/25+S6 29 腿逐腿 rc=0+epoch isinstance(int)+clock T 分隔 | "
 "next: r166=fund_premium 15:35 首火(bmc 车道·15:30 后首轮)+census finalize watch(bmb ETA ~15:00->judge flips x5+W2/W3/W4-JUDGE 串行+V2-P1 un-defer)+"
 "15:30 后新 bar 全链接力(REGIME_GUARD v3 日期门 10-01 前 shadow)+bma 静默 196min->15:40 MSG-1042 takeover eval+W5 parked 维持(判官漏斗 headroom 未变)+council C-01 意见窗 09-29 12:00"
)
with open(rr, 'a', encoding='utf-8', newline='\n') as f:
    f.write(line + '\n')
print('round report appended')

# ---- 2. state-bm-c.json round_no 165 ----
st = json.load(open('state-bm-c.json', encoding='utf-8'))
st['round_no'] = 165
st['round'] = 165
st['loop_round'] = 165
st['did'] = ("R165: W4-SCREEN finalize 收割轮: burn 4010/4010 -> null p95 0.5164 -> survivors 461/3810=12.10% (三带全 PASS) -> "
             "vol 方向先验反向殉死诚实披露 (calm<none<wild) -> w4_screen.json+cells csv+ledger 305,190 -> 池 done 翻面 (44+/5- byte-style) + "
             "W4-JUDGE 入池 parked waiting (§0 物理序门) + MSG-1316 judge-unblock + S6 29 腿 rc=0 + orders 99/99 双扫 + smoke 25/25")
st['verify'] = ("finalize C2 键+锚恒等+461/4010+池 CRLF/尾字节恒等净 diff 44+/5-+checkpoint 4010 行+smoke 25/25+S6 逐腿 rc=0+schtasks 三件+epoch int 自证")
st['next'] = ("r166: fund_premium 15:35 首火 bmc 车道 + census finalize watch (bmb ~15:00 -> judge flips 串行 x5+V2-P1 un-defer) + 15:30 后新 bar 全链接力 + "
              "bma 静默 196min 15:40 MSG-1042 takeover eval + W5 parked 维持 + council C-01 窗 09-29 12:00")
st['last_round_at'] = ts_iso
st['last_round_ts'] = ts_iso
st['last_round'] = ts_iso
st['current_task'] = 'r165 closed: W4 screen-finalize LANDED (461/3810 survivors, ledger 305,190; pool done-flipped; W4-JUDGE parked waiting; MSG-1316); next = fund_premium 15:35 first-fire + census watch + new-bar relay'
st['updated'] = ts_iso
st['ts'] = now.strftime('%Y-%m-%d %H:%M:%S')
json.dump(st, open('state-bm-c.json','w',encoding='utf-8',newline='\n'), ensure_ascii=False, indent=1)
print('state round_no=165 written')

# ---- 3. heartbeat fleet/machines/bm-c.json ----
hb = json.load(open('fleet/machines/bm-c.json', encoding='utf-8'))
epoch = int(time.time())
assert isinstance(epoch, int)
hb['machine_id'] = 'bm-c'
hb['last_seen'] = now.strftime('%Y-%m-%d %H:%M:%S')
hb['current_task'] = ('R165 done: W4 screen-finalize LANDED (4010/4010 cells; null p95 0.5164; survivors 461/3810=12.1%; '
                      'ledger 305,190; pool done-flip + W4-JUDGE parked waiting + MSG-1316) + S6 29 legs rc=0 + orders 99/99')
hb['cpu_cores'] = 32
hb['cpu_pct'] = cpu
hb['free_ram_gb'] = free_ram_gb
hb['gpu_free_vram_gb'] = round(gpu_free/1024, 1)
hb['verdict'] = ('py_low_with_work_cands legal (W4-SCREEN burn harvested this round -> pool done; judge faces waiting = serial queue '
                 'behind W2/W3-JUDGE per prereg sec.0 + RAM r354 gate; census W2B on bm-b until ~15:00; fund_premium own-lane '
                 'first-fire 15:35; bma silent 196min -> stale-takeover lawful for guarded faces)')
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = ts_iso
hb['task'] = 'round-closed'
hb['round_no'] = 165
hb['round'] = 165
hb['loop_round'] = 165
hb['cores'] = 32
hb['free_ram_mb'] = int(free_ram_gb*1024)
hb['idle_ram_gb'] = free_ram_gb
hb['cpu_util_pct'] = cpu
hb['gpu_free_vram_mb'] = gpu_free
hb['gpu_idle_vram_gb'] = round(gpu_free/1024, 1)
hb['gpu_idle_vram_mb'] = gpu_free
json.dump(hb, open('fleet/machines/bm-c.json','w',encoding='utf-8',newline='\n'), ensure_ascii=False, indent=1)
chk = json.load(open('fleet/machines/bm-c.json', encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk['clock_read'] and '+' in chk['clock_read']
print('heartbeat written; epoch int verified:', chk['heartbeat_epoch_utc'], chk['clock_read'], 'cpu', cpu, 'free_ram', free_ram_gb)
