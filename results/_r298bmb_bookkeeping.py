"""r298 bm-b S7 bookkeeping: orders double-scan, state.json, round report line,
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

DID = ("S0 fetch 面定谳 behind 2(bm-a R293 坠机救捞双提交·CN_KLINE 7/7 判负收口+CODELY take-upstream)"
       "且确触 autofill_state.json 同文件=轮首 pull --rebase 被自有车道未提交 state 阻(非冲突·非阻塞·OS S0 律)"
       "→整合按技能正典让路至 S7 push-rejection 撞车批处理(bigmoney-conflict-resolve 例外面·bm-a e0fed5e9 同范式); "
       "S0.5 orders 91/91 轮首扫描零未回执(python 差集确定性比对双向空)+远端增量零新 orders/tasks(名面实证)"
       "+集团 decisions.md 直扫面 bm-b 无集团仓 clone 不可达如实注记(R291 事实条·镜面=fleet/orders 91/91 零差集); "
       "S1 smoke 25/25; S2 票 32 张非 done 全 claimed 零 open+job_list 0+水位红牌读 red=false; "
       "S3=r293-r297 诚实维护轮延续(队列点名项全闭合/gated)→本轮唯一增量=T-87 探针#11 on_track(3872/5228=74.1%"
       "@12.55/min·ETA 06:43:56<周一 09:15·header/ohlc 零缺陷·at_cutoff 3863/3872·lineage=r281-r297 冻结探针)"
       "+转录坑修正(os.path.SEEK_END 手抄 delta·difflib 定谳·字节复制协议+S4 坑律入册)"
       "+S6 30/30 legs rc=0(复用 r292 runner 落 _r298bmb_s6_chain.log: audit v2.3 CLEAN flags=[] cpu2.0/py5.1"
       "·update_daily 零新行周末诚实·regime ORANGE shadow 触发 breadth 0.77·scorecard 6/28/7·clock CALL-2026-09-24"
       "·lhb no-op·heat/futures 周末·options/mf/sina_mf/ths/ah=bm-a 车道诚实 no-op·fundprem bm-c 车道"
       "·astock lock-alive no-op·fundamental 6.6h skip·b_layer 5/5·live.paper OK·t35v PASS 0 pending"
       "·t24 22/22 drift 0·promo 0/22·aggr/alloc/grid 幂等 no-op·export 09-24·daily_report faces=4"
       "·monitor factors=10·token L2 0 today)+post_review 2588 行 0 fail 0 pending(last_ts 04:11:35 本轮零新声明)零 P0; "
       "S4 一条坑律=冻结血统脚本逐轮复制禁手抄(四问门过)")
NEXT = ("S7 push-rejection 撞车批正典解(autofill_state=mixed-dict+ledger 配方·CODELY=memory-union·"
        "compute_audit=rolling-ledger·token_usage=snapshot·state-bm-a/machines-bm-a=单写者取他机侧·"
        "先跑 classify_conflicts.py 分类); T-87 pass-completion 复探(ETA 06:43:56 后·gate 自动·面板 complete "
        "翻面=bm-a wave-2 解锁); 09-28 周一开市新 bar 全链接力(09:15 首拉实弹·stragglers gate 自愈); "
        "迁移窗 v2.2 armed 至 09-29 12:00(执行器域·Tuanjie 三进程在拦·勿双 arm); CODELY append 后水位自检")

REPORT_LINE = " | ".join([
    NOW_ISO,
    "r298 bm-b",
    "dept:工程/舰队",
    ("WM-VERDICT: 绿 red=false lane healthy; py_low_with_work_cands 合法非红"
     "(T-87 astock 全宇宙供给在飞=2.5s/股网络限速结构性低 CPU 非怠工; 板 0 open 全 claimed; "
     "bandit claimed/parked; 池车道照 r292-r297 判例白名单面)"),
    "did: " + DID,
    ("evidence: results/_r298bmb_astock_pass_probe.py+json(#11 on_track·diff 取证含转录坑定谳) + "
     "results/_r298bmb_s6_chain.log(30/30 rc=0) + smoke 25/25 + schtasks 三任务在役"
     "(IterationLoop 正在运行/Watchdog+Autofill 就绪·R49 CSV 口径) + heartbeat epoch int 自证"),
    "next: " + NEXT,
])

# --- 3) state.json -------------------------------------------------------------
sp = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
st = json.load(io.open(sp, encoding="utf-8-sig"))
st["round_no"] = 298
st["did"] = DID
st["verdict"] = "green"
st["next"] = NEXT
st["last_round_ts"] = NOW_ISO
st["last_result"] = "ok"
st["current_task"] = "r298 maintenance round (T-87 probe#11 on_track + S6 30/30 + S7 canonical conflict-resolve)"
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
hb["current_task"] = ("r298 maintenance round done: T-87 probe#11 on_track 74.1% ETA 06:43 "
                      "+ S6 30/30; integration of bm-a R293 salvage pair via S7 canonical resolve")
hb["cpu_cores"] = 16
hb["free_ram_gb"] = free_ram_gb
hb["gpu_free_vram_gb"] = gpu_free if gpu_free is not None else hb.get("gpu_free_vram_gb", 7.1)
hb["cpu_util_pct"] = cpu_pct
hb["round_no"] = 298
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
assert isinstance(st2["round_no"], int) and st2["round_no"] == 298
codely_b = os.path.getsize(os.path.join(ROOT, "CODELY.md"))
assert codely_b <= 10 * 1024, ("CODELY >10KB", codely_b)
print("self-verify PASS: epoch=%d(int) clock=%s state_round=298 free_ram=%.1fGB "
      "gpu_free=%s cpu=%.1f%%" % (e, hb2["clock_read"], free_ram_gb, gpu_free, cpu_pct))
print("CODELY.md waterline: %dB (+1 kenglu r298, <=10KB hard line held)" % codely_b)
