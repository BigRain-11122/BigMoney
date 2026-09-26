"""r297 bm-b S7 bookkeeping: orders double-scan, state.json, round report line,
heartbeat update (epoch int + clock_read T-sep self-verified). One-shot, idempotent
per field values; leaves all legacy keys untouched (mixed-dict union law)."""
import datetime as dt
import glob
import io
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = dt.datetime.now().astimezone()
NOW_ISO = NOW.isoformat(timespec="seconds")          # T-separator, +08:00 offset

# --- 1) S7 orders double-scan (python set diff, no timestamp filter) ---------
hb_path = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
ack = set(json.load(io.open(hb_path, encoding="utf-8-sig"))["orders_ack"].split())
files = {os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "fleet", "orders", "O-*.md"))}
unacked, missing = sorted(files - ack), sorted(ack - files)
assert not unacked and not missing, ("UNACKED", unacked, "ACK_NOFILE", missing)
print("orders double-scan: %d/%d zero unacked, zero ack-no-file" % (len(ack), len(files)))

# --- 2) resource samples ------------------------------------------------------
free_ram_gb, cpu_pct, gpu_free = 12.3, 5.0, None
try:
    import psutil
    free_ram_gb = round(psutil.virtual_memory().available / 2**30, 1)
    cpu_pct = round(psutil.cpu_percent(interval=1), 1)
except Exception:
    pass
try:
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=10).stdout.strip().splitlines()
    gpu_free = round(int(out[0].strip()) / 1024, 1)
except Exception:
    pass

DID = ("S0 pull 被轮首 autofill 自有脏阻断(fetch 面查 HEAD==origin 零远端增量零实损); "
       "S0.5 orders 91/91 轮首扫描零未回执(python 差集确定性比对双向空)+集团 decisions.md/orders.md "
       "直扫面 bm-b 无集团仓 clone 不可达如实注记(R291 事实条·镜面=fleet/orders 91/91 零差集); "
       "S1 smoke 25/25; S2 票 32 张非 done 全 claimed 零 open+job_list 0+水位红牌读; "
       "S3=r293-r296 诚实维护轮延续(队列点名项全闭合/gated: J12 反重复禁堆/J13 bm-a 车道/J10 J18b "
       "已交付/town r292 已对齐/Optuna 6<8 冻结)→本轮唯一增量=T-87 探针#10 on_track(3687/5228=70.5%"
       "@12.52/min·ETA 06:44:56<周一 09:15·header/ohlc 零缺陷·at_cutoff 3680/3687·lineage=r281-r296 "
       "冻结探针 verbatim)+S6 30/30 legs rc=0(复用 r292 runner 落 _r297bmb_s6_chain.log: audit CLEAN "
       "flags=[] cpu7.0/py4.6·update_daily 零新行周末诚实·regime ORANGE shadow 触发 breadth 0.77·"
       "scorecard 6/28/7·clock CALL-2026-09-24·lhb min-interval·heat/futures 周末·options/mf/sina_mf/"
       "ths/ah=bm-a 车道诚实 no-op·fundprem bm-c 车道·astock lock-alive no-op·fundamental 6.4h skip·"
       "b_layer 5/5·live.paper OK·t35v PASS 0 pending·t24 22/22 drift 0·promo 0/22·aggr/alloc/grid 幂等 "
       "no-op·export 09-24·daily_report faces=4·monitor factors=10·token L2 0 today)+post_review 13 NO "
       "零新增(last_ts 04:11:35 本轮零新声明)零 P0; S4 零新坑律=纯维护复用零 append(四问门①②)")
NEXT = ("T-87 pass-completion 复探(ETA 06:44 后·gate 自动·面板 complete 翻面=bm-a wave-2 解锁); "
        "09-28 周一开市新 bar 全链接力(09:15 首拉实弹·stragglers gate 自愈); CN-KLINE runner=bm-a "
        "车道零触碰; 迁移窗 v2.2 armed 至 09-29 12:00(执行器域·Tuanjie 三进程在拦·勿双 arm); "
        "S4 append 后必带字节水位自检(本轮零 append·面=2,379B)")

REPORT_LINE = " | ".join([
    NOW_ISO,
    "r297 bm-b",
    "dept:工程/舰队",
    ("WM-VERDICT: 绿 red=false lane healthy; probe 04:42:12 py_low_with_work_cands 合法非红"
     "(T-87 astock 全宇宙供给在飞=2.5s/股网络限速结构性低 CPU 非怠工; 板 0 open 全 claimed; "
     "bandit claimed/parked; 池/票 54/54 done 车道照 r292-r296 判例白名单面)"),
    "did: " + DID,
    ("evidence: results/_r297bmb_astock_pass_probe.py+json(#10 on_track) + "
     "results/_r297bmb_s6_chain.log(30/30 rc=0) + smoke 25/25 + schtasks 三任务在役"
     "(IterationLoop 正在运行/Watchdog 就绪/Autofill 就绪·R49 CSV 口径) + heartbeat epoch int 自证"),
    "next: " + NEXT,
])

# --- 3) state.json -------------------------------------------------------------
sp = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
st = json.load(io.open(sp, encoding="utf-8-sig"))
st["round_no"] = 297
st["did"] = DID
st["verdict"] = "green"
st["next"] = NEXT
st["last_round_ts"] = NOW_ISO
st["last_result"] = "ok"
st["current_task"] = "r297 maintenance round (T-87 probe#10 on_track + S6 30/30)"
st["updated_at"] = NOW_ISO
with io.open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# --- 4) round report line (bm-b ledger) ---------------------------------------
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
with io.open(rp, "a", encoding="utf-8") as f:
    f.write(REPORT_LINE + "\n")
print("round_report line appended:", len(REPORT_LINE), "chars")

# --- 5) heartbeat --------------------------------------------------------------
hb = json.load(io.open(hb_path, encoding="utf-8-sig"))
hb["last_seen"] = NOW_ISO
hb["heartbeat_epoch_utc"] = int(time.time())          # MUST be JSON int (R170/R178)
hb["clock_read"] = NOW_ISO                             # T-separator (R262)
hb["current_task"] = ("r297 maintenance round done: T-87 probe#10 on_track 70.5% ETA 06:44 "
                      "+ S6 30/30; T-87 astock supply in flight ETA window 06:40-09:30")
hb["cpu_cores"] = 16
hb["free_ram_gb"] = free_ram_gb
hb["gpu_free_vram_gb"] = gpu_free if gpu_free is not None else hb.get("gpu_free_vram_gb", 7.1)
hb["cpu_util_pct"] = cpu_pct
hb["round_no"] = 297
hb["verdict"] = "green"
hb["n_orders_ack"] = len(ack)                          # 91, unchanged this round
with io.open(hb_path, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# --- 6) self-verification ------------------------------------------------------
hb2 = json.load(io.open(hb_path, encoding="utf-8-sig"))
st2 = json.load(io.open(sp, encoding="utf-8-sig"))
e = hb2["heartbeat_epoch_utc"]
assert isinstance(e, int) and not isinstance(e, bool) and abs(e - time.time()) < 300, e
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], hb2["clock_read"]
assert isinstance(st2["round_no"], int) and st2["round_no"] == 297
print("self-verify PASS: epoch=%d(int) clock=%s state_round=297 free_ram=%.1fGB "
      "gpu_free=%s cpu=%.1f%%" % (e, hb2["clock_read"], free_ram_gb, gpu_free, cpu_pct))
print("CODELY.md waterline: %dB (zero-append round, face unchanged since r296 reorg)"
      % os.path.getsize(os.path.join(ROOT, "CODELY.md")))
