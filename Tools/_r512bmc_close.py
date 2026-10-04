# -*- coding: utf-8 -*-
"""r512 bm-c round close: state-bm-c.json round_no++ + heartbeat write +
round report main line append. Laws: R170/R178 heartbeat epoch JSON-int;
R262 clock_read T-separator; EOL host-probe for append (r485)."""
import json
import os
import subprocess
import time

import psutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
ROUND = 512


def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S+08:00")


# ---- metrics sample ------------------------------------------------------
cpu = round(psutil.cpu_percent(interval=2), 1)
ram_avail = round(psutil.virtual_memory().available / (1024 ** 3), 1)
gpu_free = 0
try:
    p = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free",
         "--format=csv,noheader,nounits"],
        capture_output=True, creationflags=CREATE)
    gpu_free = int(p.stdout.decode("utf-8", "replace").strip().splitlines()[0])
except Exception:
    gpu_free = 0
epoch = int(time.time())
ts = now_iso()

CUR = ("当前活: r512 看护收口（S6 38 腿 CEO 面再生+四件套自愈+orders/D-19 双扫零新令；双判决链席位他机"
       "=N2-W15 judge-finalize=bm-a F-04 席·fund-trio finalize=bm-b canonical·本机零席位动作） | "
       "最近实物: S6 38/38 rc0 CEO 面再生（REPORT-2026-10-05+LIVE-2026-10-05 @04:18-19·ORANGE/50%帽/"
       "COOL/6 员·多 lane 面 bm-a 心跳 stale 72min→bm-c stale-takeover derive O-2100 s2.4）+N2-W15 "
       "JUDGE 池面 13/13 全 done（12 分片+JUDGE-PREP·finalize 席=bm-a）+FF 合流 bm-b r709 波 4 commit "
       "@ " + ts + " | 下个里程碑: D-20261002-05 selftest 席位窗 10-06 00:00；D-20261002-06 拆件收口窗 "
       "10-07 12:00；N2 judge-finalize（bm-a 席·≤10-12·r482 id-dup probe 先行）；fund-trio finalize"
       "（bm-b·10-05..09）；W3 下一波方向 CEO 裁定（呈报已交）；复市 10-09 数据链重挂（G3）；月界首考 "
       "10-31；5x HANDOVER=r515")

DID = ("r512 bm-c: watch/maintenance round (boards open=0, judgment-chain seats all on other "
       "machines, holiday no bar). (1) S0: fetch + FF-merge --ff-only origin/main 4 commits "
       "(bm-b r709 wave: watch round + 20-UU merge closeout + SHARD-2/10 harvest-done "
       "take-theirs + CODELY pit-law) e0731862a->5eeed231a, dirty-intersect-incoming=0, daemon "
       "lane faces preserved; r511 leftover untracked probe results/_r511bmc_final_probe.txt "
       "absorbed into round commit with r494 ownership disclosure. (2) S0.5 dual scan: orders "
       "154/154 acked strict rc0 zero new order; inbox 0 unread; D-19 dual hash MATCH-unchanged "
       "both scans (decisions 755428F8 / orders 3BF0F16E) zero action. (3) S1 smoke 48/48. "
       "(4) S2 boards empty (job_list 0; fleet 0 open, 46 claimed waiting-state). (5) S3: "
       "watermark red=false green; satengine rc0 alive (Tools face r467 law); post_review 5697 "
       "rows zero X; pool census 403 = 399 done + 3 ready (FUND trio NULLS = bm-b RAM-gated "
       "keepalive lane, r487 manual-burn ban holds) + 1 waiting (W14-GENERATE governance-parked); "
       "N2-W15 JUDGE pool faces 13/13 done (12 shards + JUDGE-PREP) -- judge-finalize seat = bm-a "
       "F-04, zero bm-c action per r511 MSG; W3 next-wave = CEO ruling face (report delivered "
       "docs/trial_labor/CEO-REPORT-MASSW3-20261005.md); trial-labor standing line zero "
       "drafting (judgment chains in flight on other seats + W3 direction awaits CEO). "
       "(6) S6 38/38 legs rc0 NON-ZERO=none (r512 canon driver; reconcile ZERO-DRIFT streak 12 "
       "@403 entries; compute_audit verdict CLEAN flags=[] supply_floor breach=false ready 3=3; "
       "py_watermark insufficient_history n=1 sampling window; CEO faces REPORT-2026-10-05 + "
       "LIVE-2026-10-05 regenerated ORANGE cap 50% heat COOL 6 members; lane stale-takeover "
       "derive by bm-c per O-2100 s2.4 bm-a hb stale 72min; golden-week no-bar legs honest "
       "no-op). (7) S7: attrition CLEAN rc0 (4 ledgers, healed history rows noted); quartet 4/4 "
       "(loop pin=5 no-op first-fire 04:25 + watchdog re-registered first-fire 04:23 + both "
       "claws LF-normalized in-place); CODELY.md 39,898B under 50KB watermark no recompile.")

LAST = ("r512 bm-c: watch/maintenance round -- FF-merge bm-b r709 wave (4 commits), orders/D-19 "
        "dual-scan UNCHANGED zero unacked, smoke 48/48, S6 38/38 rc0 (CEO faces REPORT/LIVE-"
        "2026-10-05 regen, ZERO-DRIFT streak 12), N2-W15 judge pool faces 13/13 done (finalize = "
        "bm-a F-04 seat), quartet 4/4, attrition CLEAN.")

VERIFY = ("r512: receipts results/_r512bmc_s6_log.txt (38 legs rc0 log) + Tools/_r512bmc_s0.py "
          "probe output (FF 5eeed231a behind=0; dual hash 3BF0F16E/755428F8) + smoke 48/48 + "
          "attrition CLEAN scan + orders 154/154 strict rc0 + pool census 403; delivery: round "
          "commit + push_verify this close.")

NEXT = ("(a) D-20261002-05 selftest seat window 10-06 00:00 (first round at/after window runs "
        "the pin selftest seat). (b) D-20261002-06 split closeout window 10-07 12:00. "
        "(c) N2-W15 judge-finalize = bm-a F-04 seat (<=10-12, r482 id-dup probe first), watch "
        "only. (d) fund-trio finalize 10-05..10-09 (bm-b canonical, watch only). (e) W3 "
        "next-wave direction = CEO ruling face (report delivered). (f) market reopen 10-09 "
        "data-chain re-arm (G3); month-end first exam 10-31. Next 5x HANDOVER = bm-c r515.")

NOTE = ("r512: watch/maintenance round. Zero seats, zero orders, zero drafting (judgment chains "
        "on other machines' seats + W3 direction awaits CEO). S6 CEO panels regenerated.")

# ---- state-bm-c.json -----------------------------------------------------
sp = os.path.join(REPO, "state-bm-c.json")
st = json.load(open(sp, encoding="utf-8-sig"))
st["round_no"] = ROUND
st["clock_read"] = ts
st["last_seen"] = ts
st["last_seen_at"] = ts
st["last_ts"] = ts
st["last_round"] = LAST
st["last_round_at"] = ts
st["last_round_ts"] = ts
st["updated"] = ts
st["updated_at"] = ts
st["ts"] = ts
st["cpu_pct"] = cpu
st["cpu_util_pct"] = cpu
st["current_task"] = CUR
st["current_task_at"] = ts
st["did"] = DID
st["verify"] = VERIFY
st["next"] = NEXT
st["note"] = NOTE
st["gpu_free_vram_mib"] = gpu_free
st["idle_ram_gb"] = ram_avail
st["ram_free_gb"] = ram_avail
st["free_ram_gb"] = ram_avail
st["heartbeat_epoch_utc"] = epoch
st["last_decisions_read_at"] = ts
st["round_no_label"] = "round 512 (bm-c)"
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# ---- heartbeat fleet/machines/bm-c.json ----------------------------------
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8-sig"))
hb["round_no"] = ROUND
hb["round_no_label"] = "round 512 (bm-c)"
hb["clock_read"] = ts
hb["last_seen"] = ts
hb["last_seen_at"] = ts
hb["updated"] = ts
hb["updated_at"] = ts
hb["ts"] = ts
hb["cpu_pct"] = cpu
hb["cpu_util_pct"] = cpu
hb["cpu_idle_pct"] = round(100 - cpu, 1)
hb["current_task"] = CUR
hb["current_task_at"] = ts
hb["activity_now"] = ("r512: watch/maintenance closeout -- S6 38/38 rc0 (CEO faces REPORT/LIVE-"
                      "2026-10-05 regen + stale-takeover derives) + smoke 48/48 + quartet 4/4 + "
                      "attrition CLEAN + FF-merge bm-b r709 wave + N2-W15 judge pool faces "
                      "13/13 done (finalize = bm-a F-04 seat)")
hb["latest_artifact"] = ("results/_r512bmc_s6_log.txt (38 legs rc0 04:19) + docs/live_usage/"
                         "LIVE-2026-10-05.md + docs/daily_report/REPORT-2026-10-05.md (04:18-19 "
                         "regen)")
hb["next_milestone"] = ("D-20261002-05 selftest window 10-06 00:00; D-20261002-06 closeout "
                        "10-07 12:00; N2 judge-finalize (bm-a seat <=10-12); fund-trio "
                        "finalize 10-05..09 (bm-b); market reopen 10-09")
hb["prod_lanes"] = ("N2-W15 JUDGE: pool faces 13/13 done, judge-finalize = bm-a F-04 seat "
                    "(watch); fund-trio NULLS x3 bm-b canonical keepalive (watch only, r487 "
                    "manual-burn ban); W3 next wave = CEO ruling face; boards open=0; "
                    "watermark green")
hb["verdict"] = DID
hb["idle_ram_gb"] = ram_avail
hb["ram_free_gb"] = ram_avail
hb["free_ram_gb"] = ram_avail
for k in ("gpu_free_mb", "gpu_free_vram_mb", "gpu_free_vram_mib", "gpu_idle_vram_mb",
          "gpu_idle_vram_mib", "gpu_idle_mb", "gpu_vram_free_mb"):
    if k in hb:
        hb[k] = gpu_free
hb["heartbeat_epoch_utc"] = epoch
with open(hp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# ---- round report main line ----------------------------------------------
rp = os.path.join(REPO, "round_reports-bm-c.md")
raw = open(rp, "rb").read()
eol = b"\r\n" if raw.endswith(b"\r\n") else b"\n"
line = (ts + " | r512 | dept:研究/工程（看护轮·orders/D-19 双扫+S6 CEO 面再生+双判决链席位观察） | "
        "watermark verdict=绿（red=false·py_low_board_clear=板空合法白名单〔板 open=0·bandit 0·无可跑"
        "批=池 3 ready 全 bm-b keepalive 车道 r487 禁手工代烧〕·probe insufficient_history n=1 采样窗）"
        " | " + CUR + " | 验证: smoke 48/48（04:1x）+S6 日志 38 腿 0 非零（ZERO-DRIFT streak 12 @403 "
        "entries）+attrition CLEAN（4 账本·healed 史行照录）+orders 154/154 双扫零未回执+D-19 MATCH"
        "（755428F8）+GORDERS MATCH（3BF0F16E）+post_review 零 ✗+四件套 4/4（loop pin=5 no-op 首发保 "
        "04:25·watchdog 重注册 04:23·双爪 LF 归一在位）+sat-engine rc0 活 | 收口实录: S0=fetch 后 behind "
        "4 脏∩入站=0→FF-merge --ff-only 5eeed231a 零冲突（bm-b r709 波·daemon lane 面全程保留）+r511 "
        "遗留 untracked 探针件随轮吸收（r494 载运披露=本机 r511 自产探针·归属一致）| 记分:1（S6 38 面 "
        "CEO 再生=实际文件改动·看护轮如实计）| 记账预算:3（state+心跳+轮报=法定 3）| 方法论捕获=无新方法"
        "（全链复用正典范式）·宝藏捕获=无（判决 finalize 未落·名单进出零·本批无五类收口面）| 登记册零"
        "命中断言=不适用（零清扫零 quarantine）| 本地未达 origin commit 数: 见 commit 后 push_verify 行 "
        "| 部门:研究/工程")
with open(rp, "ab") as f:
    f.write(line.encode("utf-8") + eol)

# ---- self-checks (smoke F7 laws) ------------------------------------------
chk = json.loads(open(sp, encoding="utf-8-sig").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"] and "+08:00" in chk["clock_read"], "clock_read format"
chk2 = json.loads(open(hp, encoding="utf-8-sig").read())
assert isinstance(chk2["heartbeat_epoch_utc"], int), "hb epoch not int"
assert chk2["round_no"] == ROUND and chk["round_no"] == ROUND
assert "orders_ack" in chk2 and len(chk2["orders_ack"]) >= 150
print("CLOSE_OK", ts, "cpu=", cpu, "ram_avail=", ram_avail, "gpu_free=", gpu_free,
      "epoch=", epoch, "eol=", repr(eol))
