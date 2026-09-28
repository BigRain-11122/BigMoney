"""r398 bm-b S5/S4 bookkeeping writer: round report line + state.json +
heartbeat + CODELY.md memory line (四问门-gated). Native JSON types only
(R170/R178 epoch-int law)."""

import datetime as dt
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

now = dt.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

# ---- S5: round report line (bm-b uses logs/iteration-loop/round_reports.md)
line = (
    "\n" + ts + " | r398 | dept:数据/工程 (T-111 五员 ETF 日面刷新腿全闭环 + S6 新bar族全绿) "
    "| WM-VERDICT: 绿牌 red=false·py_low_board_clear @20:53 合法空闲(板全闭环+无可跑批); "
    "audit v2.4.1 双旗 supply_gap/supply_floor standing (ready 1<floor 3·streak 252min) "
    "= 候选供给线义务跨轮 standing | did: (1) S0-1 bm-b 锚定; 轮首脏=r397 死会话遗留 "
    "addendum(staged)+p1d_gates churn→进程面实探无本仓并发会话(其余 codely 全他项目车道)"
    "→代收口 e10ced42; S0 pull --rebase up-to-date; (2) S0.5 orders 121/121 零差集; "
    "decisions.md 面: D-20260928-02/-03 均已由机队执行并回执关闭(bm-a r395 verify-in-tree "
    "6a8e2bb2 + bm-c r154 48h 窗内回执 + D-03①② r388/r390 落地)本轮零新动作仅核; "
    "(3) T-111 五员 ETF 日线面板刷新腿 claim+done 同轮全闭环: step-0 四探针(akshare 包装器 "
    "ETF 码 outstanding_share 腿 demjson 崩→直连 klc_kl.js+MiniRacer 配方; as-traded 基定谳: "
    "sina ETF qfq 因子 s=1.0 全事件·四窗 ratio=1.000000·全史干比对 5/5 零失配)→"
    "scripts/update_etf_daily.py(update_repo 家族语义: min-of-lasts 门+取齐验全后统写全或无原子"
    "+15:30 完整性+30min 节流+conn-fuse 3+R31 bm-b 车道守卫; selftest 10/10 双跑稳定)→"
    "实弹首飞 rc=0 五员各 +3 行(09-23/09-24/09-28→面板 cutoff 2026-09-28)→幂等复跑 no-op 零网络→"
    "冻结消费面共存证明 BP1 G-ANCHOR-FACE census 5/5 PASS(D2 lockbox 截断)→smoke 腿接线 25→26/26"
    "+S6 链腿接线 iteration_prompt.txt; (4) S6 全绿且新bar族触发: update_daily +36 行 cutoff 09-28 "
    "(r397「09-28 non-trading day」标签经实弹证伪: 510300 量 986M 收 4.417 −2.17%)→live.paper"
    "(enforce 请求·日期门诚实降级 shadow)+t35 open-fill PASS 0/0+prospect 22/22 pass+promotion "
    "0/22 eligible 合法判读+AGGR 20/20 marked+ALLOC 7/7 written+GRID no-op(面板≤evidence_cutoff)"
    "+system_v1 bm-a 守卫 no-op; bm-a hb stale ~168min→bm-b stale-takeover 合法派生 "
    "paper/scorecard/t35/prospect/export/daily_scorecard/build_status 全共享面(O-2100 s2.4); "
    "astock_daily 分离后台刷新已 spawn(09-24<09-28); (5) S7: loop 任务在位 :X2 针位正·watchdog 就绪"
    "·pre-commit 钳 OK 全零动作 | evidence: results/_r398bmb_etf_daily_probe*.py/.json ×4 组 + "
    "results/_r398bmb_etf_anchor_census.py census 5/5 + results/etf_daily_pull_status.json + "
    "smoke 26/26 + S6 逐腿 rc=0 + fleet/tasks/T-2026-09-28-111-P1.json | next: T-104 s2 宽基网格 "
    "prereg 族(bm-b 认领票下一切片·解锁池 T104-GRID-S3-DUALFACE-P1 门1) > TRIAL_LABOR_LAW 常设线供给"
    "(supply_gap standing: 下一波起草) > CEO 48h 千人试用期报告窗 09-29 22:45 (数据面 r396 起就绪)\n"
)
rep_path = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
with open(rep_path, encoding="utf-8") as f:
    rep = f.read()
if " | r398 | dept:" in rep:
    # idempotent rewrite: strip the offset-less ts from the prior partial run
    import re as _re
    rep = _re.sub(r"\n2026-09-28T21:1\d:\d\d \| r398 \|", "\n" + ts + " | r398 |", rep)
    with open(rep_path, "w", encoding="utf-8") as f:
        f.write(rep)
else:
    with open(rep_path, "a", encoding="utf-8") as f:
        f.write(line)

# ---- S5: state.json (bm-b face)
state = {
    "machine_id": "bm-b",
    "round_no": 398,
    "note": ("r398: T-111 five-member ETF daily refresh leg FULL CLOSURE same round "
             "-- 4 probes (akshare wrapper ETF-code outstanding_share leg demjson "
             "crash -> direct klc_kl.js + MiniRacer recipe; as-traded basis proven: "
             "sina ETF qfq factor s=1.0 all events, 4-window ratio=1.000000, "
             "full-history dry-compare 5/5 zero mismatch) -> scripts/update_etf_daily.py "
             "(update_repo family: min-of-lasts gate / all-or-nothing overlap-verified "
             "append / 15:30 completeness / 30min throttle / conn-fuse 3 / R31 bm-b lane "
             "guard; selftest 10/10 double-run stable) -> live first fire rc=0 +3 rows "
             "x5 members (09-23/09-24/09-28 -> panel cutoff 09-28) -> idempotent re-run "
             "no-op -> frozen-consumer proof BP1 anchor census 5/5 PASS (D2 lockbox) -> "
             "smoke leg wired 25->26 PASS + S6 chain leg wired. S6 green with NEW BARS: "
             "update_daily +36 rows cutoff 09-28 (r397 '09-28 non-trading day' label "
             "falsified by live evidence 510300 vol 986M close 4.417); new-bar family "
             "fired all green; bm-a hb stale ~168min -> bm-b stale-takeover all shared "
             "faces lawful. audit supply_gap/supply_floor standing -> next: T-104 s2 "
             "broad-grid prereg family (pool T104-GRID-S3-DUALFACE-P1 gate 1) > "
             "TRIAL_LABOR_LAW standing supply line > CEO 48h report window 09-29 22:45"),
    "last_round_at": ts,
    "last_round_ts": ts,
}
with open(os.path.join(ROOT, "state.json"), "w", encoding="utf-8") as f:
    json.dump(state, f, ensure_ascii=False, indent=1)

# ---- S7: heartbeat (native int epoch law R170/R178)
hb_path = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
with open(hb_path, encoding="utf-8-sig") as f:
    hb = json.load(f)

import psutil

vm = psutil.virtual_memory()
hb.update({
    "machine_id": "bm-b",
    "role": hb.get("role", "compute-node"),
    "joined": hb.get("joined", "2026-09-23"),
    "last_seen": ts,
    "heartbeat_epoch_utc": epoch,
    "clock_read": ts,
    "current_task": ("r398 done: T-111 five-member ETF daily refresh leg FULL CLOSURE "
                     "(4 probes: akshare wrapper ETF crash -> direct klc_kl.js+MiniRacer; "
                     "as-traded basis proven qfq-factor s=1.0 all events; runner "
                     "scripts/update_etf_daily.py update_repo-family selftest 10/10 + "
                     "live first fire +3x5 rows -> panel cutoff 09-28 + idempotent no-op "
                     "+ BP1 anchor census 5/5 coexistence) -> next: T-104 s2 broad-grid "
                     "prereg family (unblocks pool T104-GRID-S3-DUALFACE-P1 gate 1) > "
                     "TRIAL_LABOR_LAW supply line (supply_gap standing) > CEO 48h report "
                     "09-29 22:45"),
    "cpu_cores": psutil.cpu_count(logical=True),
    "free_ram_gb": round(vm.available / 1e9, 1),
    "idle_ram_gb": round(vm.available / 1e9, 1),
    "total_ram_gb": round(vm.total / 1e9, 2),
    "cpu_util_pct": psutil.cpu_percent(interval=0.3),
    "round_no": 398,
    "round": 398,
    "loop_round": hb.get("loop_round", 394),
    "verdict": ("healthy: smoke 26/26 (+1 new etf_daily leg); T-111 refresh leg closed "
                "same round (panel 09-22->09-28, frozen anchors coexist 5/5); S6 all "
                "rc=0 with new-bar family fired (update_daily +36 rows cutoff 09-28; "
                "r397 non-trading-day label falsified); bm-a hb stale ~168min -> "
                "stale-takeover lawful; watermark py_low_board_clear legal idle + audit "
                "supply_gap/supply_floor standing -> supply line next; orders ack "
                "121/121 self-receipt closed"),
    "orders_ack": hb.get("orders_ack", []),
    "n_orders_ack": len(hb.get("orders_ack", [])),
    "cores": psutil.cpu_count(logical=True),
    "idle_ram_mb": int(vm.available / 1e6),
    "free_ram_mb": int(vm.available / 1e6),
    "gpu_model": hb.get("gpu_model", ""),
    "prod_lanes": hb.get("prod_lanes", []),
    "prod_lanes_note": hb.get("prod_lanes_note", ""),
})
try:
    import subprocess
    q = subprocess.run(["nvidia-smi", "--query-gpu=memory.total,memory.used",
                        "--format=csv,noheader,nounits"], capture_output=True,
                       text=True, timeout=10)
    tot, used = [int(x.strip()) for x in q.stdout.strip().splitlines()[0].split(",")]
    hb["gpu_free_vram_gb"] = round((tot - used) / 1024, 2)
    hb["gpu_idle_vram_gb"] = round((tot - used) / 1024, 2)
    hb["gpu_idle_vram_mb"] = tot - used
except Exception:
    pass
tmp = hb_path + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
os.replace(tmp, hb_path)

# ---- S4: CODELY.md memory line (四问门 passed: long-term value yes /
# formal artifacts carry detail -> one-line+pointer / positive interface
# knowledge / one item)
mem = (
    "\n- [2026-09-28 21:1x] r398 bm-b 正面接口知识（五员 ETF 日面通道定谳·T-111）："
    "akshare stock_zh_a_daily 包装器对 ETF 码死（outstanding_share/turnover 腿 demjson "
    "「No value to decode」——价格腿 klc_kl.js 本身五员全通）→直连配方="
    "zh_sina_a_stock_hist_url + MiniRacer hk_js_decode（r398 探针实证）；"
    "sina 对 ETF 的 qfq 因子 s=1.0 全事件（份额折算型分红不回溯改价）→五员 "
    "data/daily/sh*.csv=as-traded 基，qfq 标签是拉取 API 用法非数据语义；"
    "冻结面追加安全=D2 lockbox 截 cutoff 后行锚校验不受影响（census 5/5 实证）。"
    "采集器=scripts/update_etf_daily.py（票 T-2026-09-28-111·四探针 "
    "results/_r398bmb_etf_daily_probe*）。How to apply：ETF 线任何日频数据工作直接复用"
    "该通道与 as-traded 基面结论，勿再探针勿走 akshare 包装器。\n"
)
p = os.path.join(ROOT, "CODELY.md")
with open(p, "a", encoding="utf-8") as f:
    f.write(mem)

# ---- self-verification (R170/R178 law: fix value AND type together)
with open(hb_path, encoding="utf-8-sig") as f:
    back = json.load(f)
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in back["clock_read"] and "+" in back["clock_read"], "clock_read format"
sz = os.path.getsize(p)
print("bookkeeping OK: report line + state 398 + heartbeat epoch",
      back["heartbeat_epoch_utc"], "| CODELY.md", sz, "bytes (<=10KB:",
      sz <= 10240, ")")
