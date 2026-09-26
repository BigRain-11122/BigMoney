# -*- coding: utf-8 -*-
"""R287 bm-a wrap: S4 memory entries + S5 round-report line + S7 state/heartbeat.
Byte-face probed per R255/R257/R262/R271/R281 laws."""
import json
import time
from datetime import datetime

now = datetime.now()
ts = now.strftime("%Y-%m-%d %H:%M:%S")
ts_iso = now.astimezone().isoformat()
epoch = int(time.time())

# ---- S4: CODELY.md memory entries (probe tail byte, R281 law) ----
p = "CODELY.md"
raw = open(p, "rb").read()
sep = b"" if raw.endswith(b"\n") else b"\n"
entries = (
    "\n- [2026-09-27 02:4x] 坑律（bm-a R287·CENSUS_FUS_S2 runner 建造期·E1 selftest 期自捕零外泄）："
    "**blend/基准 sizing 分母必须随实际 target 集——fixed_all 基准（EW48）沿用 TOP_K 常量分母=每员 1/16 权重、Σw=3.0 收益放大 3 倍（实弹：EW48 ann 0.4876 vs 真 ~0.169，无噪漂移夹具 [3a] 当场红）**；正律=want=NOTIONAL/len(target) 于 target 定后取；"
    "连带=「完美信号」夹具必须截面单调——时序单调列=常数截面被 ic_series 正确跳过=夹具自病非机器病（P-1 S6 无噪漂移范式是正解）。指针=scripts/census_fusion_s2.py blend_top16 want 行+selftest [2][3a] 修正史\n"
    "- [2026-09-27 02:4x] 纪律（bm-a R287·集团令扫描面新维·D-20260927-05② 自评采纳落地）：**集团 docs/orders.md 直令面可承载 @BigMoney dispatched 令而不落本司 fleet/orders/——实弹：L45「CODELY ≤10KB」令经 fleet/orders 差集=空漏接，集团台账全文件扫描面捕获（R287 承接执行 8a00f514）**；正律=每轮 S0.5 decisions.md 同位步加扫集团 orders.md 全文件 @BigMoney/quant 行（dispatched 未回执=落 O 件入册执行），本律入本件=轮读面自动携带。指针=fleet/orders/O-20260927-0230-bm-a.md+集团 orders.md L45\n"
).encode("utf-8")
open(p, "wb").write(raw + sep + entries)
d = open(p, "rb").read()
assert len(d) <= 10240, f"CODELY over 10KB line: {len(d)}"
print("codely_bytes", len(d))

# ---- S5: round report line (CRLF face, tail_nl True) ----
p = "logs/iteration-loop/round_reports-bm-a.md"
raw = open(p, "rb").read()
sep = b"" if raw.endswith(b"\n") else b"\n"
line = (
    f"{ts} | R287 bm-a | WM=GREEN healthy (red=false lane=healthy; batch alive: CN-TREND nulls burning local + CENSUS-FUS-S2-W1 pool entry ready 02:44 = supply fed same round) | "
    "S0.5 double-scan clean + NEW SCAN FACE: group docs/orders.md L45 @BigMoney CODELY<=10KB order caught (fleet/orders diff was EMPTY) -> O-20260927-0230 executed 50.8KB->1.8KB byte-exact, 53 kenglu line-lossless to research/memory-archive/202609.md (8a00f514; bm-b r289 co-receipt, resurrection incident repaired their side) | "
    "T-86 s2: census runner built per frozen prereg e51e55e0 (29 faces, N=4518=4060+58+400, ic_series/alloc_backtest/compute_all anchors, selftest 14/14 incl r286 np-native+glue legs, real-data probe PASS gate 48/48 grid 279 EW48 x1 0.154) + pool entry ready workers_plan 4 BelowNormal | "
    "S6 22 legs rc=0 (audit v2.3 CLEAN flags=[], update_daily 0 new rows cutoff 09-24, clock ORANGE_COOL sleeves 4, weekend no-ops honest, ah_panel detached refresh + moneyflow rank pass spawned) | smoke 25/25 | "
    "push note: census commit 3bcd438c -> machine/bm-a-r287 after 2x rejection (bm-b r289 in-flight window) | "
    "next: autofill tick burns CENSUS-FUS-S2-W1 -> harvest on landing three-piece (prereg s7/s8 + post_review row + attrition r285 law); CN-TREND harvest when product lands; two new laws -> CODELY (EW48 sizing divisor + group-orders scan face)\r\n"
).encode("utf-8")
open(p, "wb").write(raw + sep + line)
print("report appended")

# ---- S7: state-bm-a.json (round 287) ----
p = "state-bm-a.json"
st = json.load(open(p, encoding="utf-8-sig"))
st["round_no"] = 287
st["did"] = ("R287: group order O-20260927-0230 CODELY<=10KB executed (50.8KB->1.8KB, 53 kenglu "
             "line-lossless to archive/202609.md, group-orders.md scan face law encoded) + T-86 s2 "
             "census runner built per frozen prereg e51e55e0 (selftest 14/14 + real probe PASS) + "
             "pool entry CENSUS-FUS-S2-W1 ready + S6 22 legs rc=0 + smoke 25/25")
st["verdict"] = "ok"
st["next"] = ("autofill burns CENSUS-FUS-S2-W1 (23 blocks est 20-40min) -> harvest three-piece on "
              "landing (prereg s7/s8 single-finalization + post_review row + attrition, r285 law); "
              "CN-TREND harvest when product lands (r288 ruling: bm-a face governs)")
for k in ("ts", "last_round_ts", "updated_at", "current_task", "last_run", "last_round_at", "updated", "last_seen"):
    st[k] = ts if isinstance(st.get(k), str) and "T" not in st.get(k, "") and ":" in st.get(k, "") else st.get(k)
st["ts"] = ts
st["last_round_ts"] = ts
st["updated_at"] = ts
st["last_run"] = ts
st["last_round_at"] = ts
st["updated"] = ts
st["last_round"] = 286
st["current_task"] = "R287 done: census runner + pool entry ready; group order CODELY compact executed; next census burn+harvest"
st["last_seen"] = ts_iso
out = json.dumps(st, ensure_ascii=False, indent=1)
json.loads(out)
open(p, "w", encoding="utf-8", newline="") .write(out)
print("state 287 written")

# ---- S7: heartbeat fleet/machines/bm-a.json ----
import psutil
p = "fleet/machines/bm-a.json"
hb = json.load(open(p, encoding="utf-8-sig"))
hb["last_seen"] = ts_iso
hb["current_task"] = st["current_task"]
hb["task"] = st["current_task"]
vm = psutil.virtual_memory()
hb["cpu_cores"] = vm and (psutil.cpu_count(logical=True))
hb["cores"] = psutil.cpu_count(logical=True)
hb["cpu_pct"] = round(psutil.cpu_percent(interval=1), 1)
hb["free_ram_gb"] = round(vm.available / 1024 ** 3, 1)
hb["free_ram_mb"] = int(vm.available / 1024 ** 2)
hb["idle_ram_gb"] = hb["free_ram_gb"]
try:
    import subprocess
    q = subprocess.run(["nvidia-smi", "--query-gpu=memory.total,memory.used",
                        "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout.strip()
    tot, used = [float(x) for x in q.split(",")]
    hb["gpu_free_vram_gb"] = round((tot - used) / 1024, 1)
    hb["gpu_idle_vram_gb"] = hb["gpu_free_vram_gb"]
    hb["gpu_idle_vram_mb"] = int((tot - used))
    hb["gpu_free_vram_mb"] = int((tot - used))
    hb["gpu_total_vram_mb"] = tot
    hb["gpu"] = {"present": True, "idle_vram_free_gb": hb["gpu_free_vram_gb"],
                 "note": f"nvidia-smi: {tot:.0f} MiB total - {used:.0f} used = {tot-used:.0f} free"}
except Exception as e:  # honest degrade
    hb["gpu"] = {"present": True, "error": repr(e)}
hb["verdict"] = "batch_alive_supply_fed_census_ready"
hb["round_no"] = 287
hb["heartbeat_epoch_utc"] = epoch          # MUST be JSON int (R170/R178 law)
hb["clock_read"] = ts_iso                 # T-separated ISO (R262 law)
ack = hb.get("orders_ack", "")
for tok in ("O-20260927-0230-bm-a", "O-20260927-0230-bm-a.md"):
    if tok not in ack:
        ack += " " + tok
hb["orders_ack"] = ack.strip()
out = json.dumps(hb, ensure_ascii=False, indent=1)
d2 = json.loads(out)
assert isinstance(d2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in d2["clock_read"], "clock_read must be T-separated"
open(p, "w", encoding="utf-8", newline="").write(out)
print("heartbeat written; epoch int ok; ack +O-20260927-0230")
