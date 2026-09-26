"""r308 bm-b wrap: round report line + state.json + heartbeat (r302 law: astimezone ISO
clock faces + epoch int self-assert gates before any commit)."""
import json, datetime, subprocess, os

NOW = datetime.datetime.now().astimezone()
NOW_ISO = NOW.isoformat(timespec="seconds")
RR = "logs/iteration-loop/round_reports.md"
STATE = "logs/iteration-loop/state.json"
HB = "fleet/machines/bm-b.json"
EV = "results/_r308bmb_wrap.json"

LINE = NOW_ISO + " | r308 bm-b | dept:舰队/工程 | WM-VERDICT: 绿 red=false lane healthy(watermark_red 07:30:13 red=false; probe 07:43:29 py_low_board_clear=板全闭环合法 idle 白名单·0 open 票·bandit 0·autofill pool 无可领分片·零本地批·零锁面) | did: S0 pull fast-forward 1a9dda99..d5d6be51 收编 bm-a r302 wrap/trail(CN-SECTOR-LEADER-P1 判决负收口面·零撞车); S0.5 orders 91/91 轮首+收尾双扫零未 ack·集团 decisions.md 直扫不可达 R291 如实注记=镜像零差集; S1 smoke 25/25; S2 板 0 open+job_list 0+post_review 复扫 0 开放负判定+水位红牌 red=false(next_pick=moneyflow IC=claimed·advisory only); S3 主活=07:30:03 tick ABORT「corrupt autofill_state」定谳+修复探针 _r308bmb_autofill_state_repair(盘面复检 json.loads=VALID→瞬态读撕裂已自愈·07:41:58 下 tick 干净 no-op·r201 refuse-wipe 正确面·NO_OP_DISK_VALID 零手术·06:50/07:10 keepalive fault=旧码面已随 r301 修复收编·disk delta=last_tick 2 行面随本轮 commit); S6 30/30 legs rc=0(_r308bmb_s6_chain.ps1 冻结血统 Copy-Item·difflib delta=2 header-only r298 坑律: audit v2.3 CLEAN flags=[] cpu1.0/py0.5·update_daily 周末零新行·regime ORANGE shadow breadth 0.77·scorecard 6/28/7·clock CALL-2026-09-24 幂等·lhb min-interval·heat 周末·futures/astock panel-fresh cutoff 09-24 零网络·options/mf/sina_mf/ths/ah=bm-a 车道诚实 no-op·fundprem=bm-c 车道·fundamental 9.4h skip·b_layer 再 derive·live.paper OK·t35v PASS 零 pending·t24 22/22 drift 0·promo 0/22·aggr/alloc/grid 幂等 no-op·export 09-24 再生·daily_report faces=4 token=1·token L2 0 today); S4 CODELY +1 坑律(瞬态读撕裂)+三批热冷整编 10030→9884B ≤10KB 硬线(2 流水面行级零丢失外迁 memory-archive/202609.md·常设律全保热); S7 schtasks 三任务在役(Autofill 07:50·Watchdog 08:00·IterationLoop 本轮·R49 CSV 路径)·迁移 v2.2 journal armed editor-gated 窗至 09-29 12:00 勿双 arm | evidence: _r308bmb_autofill_state_repair.py+json(NO_OP_DISK_VALID)+_r308bmb_s6_chain.ps1+results/_r308bmb_s6_chain.log(30/30 rc=0)+_r308bmb_codely_repack.py+json(9884B 全门 PASS)+smoke 25/25+orders 91/91 双扫+_r305bmb_postreview_pool 复扫 0 开放 | next: 09-28 周一首新 bar 全链(update_daily→live.paper(有新 bar 面设 env enforce)→t35v→t24x2→aggr→grid 5 账户首拍唤醒→export→scorecard→daily_report)+T-87 周一 15:30 后首日续拉实弹(全宇宙分离 fetch by-design·settled 重载自愈)+供给队列 #5 market-neutral(bm-a 车道)+10-01 月度三件套+REGIME_GUARD v3 日期门(10-01 起自动激活)+R310 下次 5x 核对"

DID = "r308: honest-maintenance + autofill_state 瞬态读撕裂定谳(07:30:03 tick ABORT→盘面复检 VALID·07:41:58 下 tick 干净 no-op 自愈实证·修复探针 NO_OP 零手术·r201 refuse-wipe 正确) + S6 30/30 rc=0 + CODELY 三批整编 9884B + orders 91/91 双扫"
NEXT = "09-28 周一首新 bar 全链+T-87 首续拉实弹+供给 #5 market-neutral(bm-a)+10-01 月度三件套+REGIME_GUARD v3 日期门+迁移窗 v2.2 至 09-29 12:00+R310 5x 核对"

# ---- round report append (utf-8, one line)
with open(RR, "a", encoding="utf-8", newline="\n") as f:
    f.write(LINE + "\n")

# ---- state.json update (canonical keys, legacy keys untouched)
st = json.load(open(STATE, encoding="utf-8"))
st["round_no"] = 308
st["did"] = DID
st["verdict"] = "green"
st["next"] = NEXT
st["last_round_ts"] = NOW_ISO
st["last_result"] = "ok"
st["current_task"] = DID
st["updated_at"] = NOW_ISO
json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- heartbeat update
hb = json.load(open(HB, encoding="utf-8"))
cpu_pct = hb.get("cpu_util_pct", 0)
free_gb = hb.get("free_ram_gb", 0)
gpu_gb = hb.get("gpu_free_vram_gb", 0)
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=0.5), 1)
    vm = psutil.virtual_memory()
    free_gb = round(vm.available / (1024 ** 3), 1)
except Exception:
    pass
try:
    q = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, timeout=10)
    if q.returncode == 0 and q.stdout.strip():
        gpu_gb = round(float(q.stdout.strip().splitlines()[0]) / 1024, 1)
except Exception:
    pass

epoch = int(datetime.datetime.now().astimezone().timestamp())
hb["last_seen"] = NOW_ISO
hb["clock_read"] = NOW_ISO
hb["heartbeat_epoch_utc"] = epoch
hb["round_no"] = 308
hb["current_task"] = DID
hb["cpu_cores"] = hb.get("cpu_cores", 16)
hb["cpu_util_pct"] = cpu_pct
hb["free_ram_gb"] = free_gb
hb["gpu_free_vram_gb"] = gpu_gb
hb["verdict"] = "green"
hb["cores"] = hb.get("cores", 16)
hb["idle_ram_gb"] = free_gb
hb["idle_ram_mb"] = int(free_gb * 1024)
hb["free_ram_mb"] = int(free_gb * 1024)
hb["gpu_free_vram_mb"] = int(gpu_gb * 1024)
hb["gpu_idle_vram_mb"] = int(gpu_gb * 1024)
hb["gpu_idle_vram_gb"] = gpu_gb
hb["cpu_pct"] = cpu_pct
hb["round"] = 308
hb["n_orders_ack"] = len(hb.get("orders_ack", "").split())
json.dump(hb, open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ---- r302-law self-assert gates (heartbeat reload + clock faces + state reload)
hb2 = json.load(open(HB, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int (F7 red face)"
assert "T" in hb2["clock_read"] and "+08:00" in hb2["clock_read"], "clock_read not astimezone ISO (R262/F7)"
st2 = json.load(open(STATE, encoding="utf-8"))
assert st2["round_no"] == 308
rr_tail = open(RR, encoding="utf-8").read().rstrip("\n").splitlines()[-1]
assert rr_tail.startswith(NOW_ISO[:16]) and "r308 bm-b" in rr_tail, "round report tail not r308 line"

ev = {"ts": NOW_ISO, "heartbeat_epoch_utc": epoch, "cpu_pct": cpu_pct, "free_ram_gb": free_gb,
      "gpu_free_vram_gb": gpu_gb, "n_orders_ack": hb2["n_orders_ack"],
      "gates": "epoch int PASS + clock_read astimezone PASS + state 308 PASS + report tail PASS"}
json.dump(ev, open(EV, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(ev, ensure_ascii=False))
