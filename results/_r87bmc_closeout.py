# -*- coding: utf-8 -*-
"""r87 bm-c S5/S7 bookkeeping: round report line + state bump (86->87) + heartbeat refresh.
Live probes: RAM (psutil fallback WMI-free ctypes), GPU free VRAM (nvidia-smi), cpu util.
Writes: utf-8 explicit, EOL mirrored from each file's current bytes. Post-write verification.
"""
import io, json, time, datetime, subprocess, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)

now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# ---- live system probes
free_ram_gb = None
total_ram_gb = None
try:
    import psutil
    vm = psutil.virtual_memory()
    free_ram_gb = round(vm.available / 1024**3, 1)
    total_ram_gb = round(vm.total / 1024**3, 1)
    cpu_util = psutil.cpu_percent(interval=1.0)
except Exception:
    cpu_util = 0.0
gpu_free = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, timeout=10)
    gpu_free = int(r.stdout.decode().strip().splitlines()[0])
except Exception:
    pass

# ---- 1. round report line
rp = "logs/iteration-loop/round_reports-bm-c.md"
raw = open(rp, "rb").read()
nl = b"\r\n" if b"\r\n" in raw else b"\n"
line = (
 iso + "｜R87｜bm-c watermark verdict=绿（red=false·probe 15:23:50 rc0 py_low_board_clear 合法白名单：板 0 open·30 票全 claimed 他人线·job_list 0·W2A=bm-b 数据本地车道在烧·本机无数据分片）"
 "｜S0 继承态死 rebase 救援全闭环：开局=15:10:37 r86 push-reject 恢复窗 pull --rebase 中途亡留 30-UU（onto c3ca1fe9 重放 d1271fbf·无他执行体在飞）→探针实测定性→resolve1 30-UU 正典解=CODELY 条目并集（origin 最重构骨架 6809B+我 2 新行=8079B·我侧 6 条活坑律已在 origin 归档节全量在册=零丢失）+archive 后缀直拼 872203+2507B+autofill 45|45 复合键集恒等 union 45·last_tick 取我 15:00:01+compute_audit union 204+x2 行并 744+coupled paper/export/twins 我侧（14:56>14:54）+take-new 族→union 后 sanity 拦下 regime 1|2→1 假 union（asof 行键被 autofill 复合键折叠=mine 09-24 行丢失级坑·当场拦）→resolve2 逐面键修正（face-key=asof+full-row dedup→09-23/09-24 双行保全）→continue 一次过 b137e5bd→push 拒（origin +3）→pull --rebase 二撞 27-UU 同配方 resolve3（origin 15:00 S6 面更新=HEAD 侧合法取胜·行首锚定标记检查修 prose 假报警）→continue eb2bb3db→push bfc24450..eb2bb3db 落 origin/main 零强推零 abort 双批全解"
 "｜S0.5 orders 96/96 双扫零未回执+决策新行 D-20260927-04（本仓复审锚自纠维持=合理零新动作）+D-20260927-05②（本仓 R13 全扫律既有合规）零动作回执"
 "｜S1 smoke 25/25 绿｜S2 板 0 open·30 票全 claimed 他人线·job_list 0"
 "｜S4 坑律入册（rolling-ledger union dedup 键逐面先探+行首锚定标记检查·r330 模板同病）·CODELY 8079→8994B<10KB"
 "｜S6 32/32 rc=0（周日合法 no-op 族+lane-guard 诚实 no-op·live_paper OK·t35v PASS 零例·prospect 22/22·promotion 0/22·export/scorecard/daily_report/build_status/token_meter 全 rc0）"
 "｜inbox 2 件未读均非本机地址面（bmb→bma W2A 崩修回执·bma→bmb sina 面就绪=留置待收件机轮）"
 "｜证据=results/_r87bmc_probe.py+_r87bmc_resolve.py+_r87bmc_resolve2.py+_r87bmc_resolve3.py+_r87bmc_s6_chain.ps1+push bfc24450..eb2bb3db"
 "｜下轮指针：周一 09-28 开市窗=新 bar 全链接力（update_daily→live.paper REGIME_GUARD v3 enforce→t35v→t24×2→aggr→grid→export→scorecard→daily_report·周一链形参考 results/_r329bmb_s6_chain.ps1）+T-91 s3 自动点火 09:15 SYSTEM-V1+REV-OSC 首队列入场+T-87 astock 首续拉 15:30 后+fund_premium snapshot 腿周一 15:30 自愈验收。 [via bm-c]"
)
with io.open(rp, "ab") as f:
    f.write(line.encode("utf-8") + nl)
chk = open(rp, "rb").read()
assert chk.endswith(line.encode("utf-8") + nl), "round report append verify failed"
print("round report appended", len(line.encode("utf-8")), "B")

# ---- 2. state bump 86 -> 87
sp = "state-bm-c.json"
raw = open(sp, "rb").read()
eol = b"\r\n" if b"\r\n" in raw else b"\n"
st = json.loads(raw.decode("utf-8"))
assert st["round_no"] == 86, f"round_no != 86: {st['round_no']}"
st["round_no"] = 87
st["updated"] = now.strftime("%Y-%m-%dT%H:%M")
st["note"] = ("r87: inherited dead-rebase rescue landed -- 15:10:37 r86 push-recovery pull --rebase died mid-30-UU "
 "(onto c3ca1fe9 replaying d1271fbf); probe + 3-pass canon resolve (CODELY entry-union origin-skeleton+2 lines, "
 "archive suffix-concat, autofill keyset-identical, regime asof-key false-union data-loss caught in-flight + "
 "full-row-dedup restore, coupled-side/take-new families); batch-2 27-UU same-recipe (origin 15:00 S6 faces newer = "
 "HEAD legit); zero abort zero force-push; r86' landed eb2bb3db push bfc24450..eb2bb3db; orders 96/96 double-scan "
 "zero unacked; decisions D-20260927-04/05 zero-action receipts; smoke 25/25; S6 32/32 rc=0; pitlaw per-face "
 "union-key + line-anchored marker check (CODELY 8994B<10KB).")
st["last_round_ts"] = iso
out = json.dumps(st, ensure_ascii=False, indent=1) + ("\r\n" if eol == b"\r\n" else "\n")
with io.open(sp, "w", encoding="utf-8", newline="") as f:
    f.write(out)
back = json.loads(io.open(sp, encoding="utf-8").read())
assert back["round_no"] == 87
print("state bumped to r87")

# ---- 3. heartbeat refresh
hp = "fleet/machines/bm-c.json"
raw = open(hp, "rb").read()
eol = b"\r\n" if b"\r\n" in raw else b"\n"
h = json.loads(raw.decode("utf-8"))
h["last_seen"] = iso
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = iso
h["current_task"] = ("R87 done: inherited dead-rebase rescue (r86 push-recovery pull --rebase died mid-30-UU) -- "
 "probe + 3-pass canon resolve incl regime asof-key false-union data-loss catch+fix, batch-2 27-UU same-recipe; "
 "r86' landed eb2bb3db push OK; S6 32/32; smoke 25/25; orders 96/96")
h["cpu_util_pct"] = float(cpu_util if cpu_util else 0.0)
if free_ram_gb is not None:
    h["free_ram_gb"] = free_ram_gb
    h["total_ram_gb"] = total_ram_gb
if gpu_free is not None:
    h["gpu_free_vram_mb"] = gpu_free
h["verdict"] = ("legal idle: board 0 open (30 claimed by other lanes), wm red=false probe 15:23:50 py_low_board_clear "
 "legal, r87 rebase-rescue round complete, fund_premium snapshot leg Monday 15:30 self-heal pending")
out = json.dumps(h, ensure_ascii=False, indent=1) + ("\r\n" if eol == b"\r\n" else "\n")
with io.open(hp, "w", encoding="utf-8", newline="") as f:
    f.write(out)
back = json.loads(io.open(hp, encoding="utf-8").read())
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert isinstance(back["orders_ack"], list) and len(back["orders_ack"]) == 96
assert "T" in back["clock_read"] and "+" in back["clock_read"]
print("heartbeat refreshed: epoch=", epoch, "int ok; cpu=", cpu_util, "free_ram=", free_ram_gb, "gpu_free=", gpu_free)

# ---- 4. S7 second orders scan (double-scan receipt)
ack = set(h["orders_ack"])
files = {f for f in os.listdir("fleet/orders") if f.startswith("O-") and f.endswith(".md")}
uno = sorted(files - ack)
assert not uno, f"UNACKED at S7 close: {uno}"
print("S7 second scan: orders 96/96 acked, zero unacked")
print("BOOKKEEP-OK")
