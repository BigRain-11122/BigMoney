# -*- coding: utf-8 -*-
"""r514 bm-c round close: state-bm-c.json round_no++ + heartbeat write +
round report main line append. Laws: R170/R178 heartbeat epoch JSON-int;
R262 clock_read T-separator; EOL host-probe for append (r485).
Bloodline: Tools/_r513bmc_close.py."""
import json
import os
import subprocess
import time

import psutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
ROUND = 514


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

CUR = ("当前活: r514 看护收口（S6 38 腿 CEO 面再生+四件套自愈+orders/D-19 双扫零新令；双判决链席位他机"
       "=N2-W15 judge-finalize=bm-a F-04 席·fund-trio finalize=bm-b canonical·本机零席位动作；W3 方向待 "
       "CEO 裁定〔呈报已交〕） | 最近实物: S6 38/38 rc0 CEO 面再生（REPORT-2026-10-05+LIVE-2026-10-05 "
       "@04:59-05:01·ORANGE/COOL·dualrun ZERO-DRIFT streak 14 @403 entries·bm-a 心跳 stale 113-114min"
       "→bm-c stale-takeover derive O-2100 s2.4〔第 2 连轮〕）+S0 FF-only 合流 bm-b r708 波"
       "（b3a72f3f9→7d581c4aa 零冲突零 UU） @ " + ts + " | 下个里程碑: 5x HANDOVER=r515（下轮）；"
       "D-20261002-05 selftest 席位窗 10-06 00:00；D-20261002-06 拆件收口窗 10-07 12:00；N2 "
       "judge-finalize（bm-a 席·≤10-12·r482 id-dup probe 先行）；fund-trio finalize（bm-b·10-05..09）；"
       "W3 下一波方向 CEO 裁定（呈报已交）；复市 10-09 数据链重挂（G3）；月界首考 10-31")

DID = ("r514 bm-c: watch/maintenance round (boards open=0, judgment-chain seats all on other "
       "machines, holiday no bar). (1) S0: fetch behind=2 ahead=0 at open (bm-b r708 wave: "
       "churn-absorb of bm-a r709/r710 dead-session faces + merge r708 13-commit integration); "
       "dirty-intersect-incoming=0 (my 3 dirty files are bm-c daemon-live faces untouched by "
       "wave) -> FF-only clean closeout b3a72f3f9->7d581c4aa, zero conflict zero UU. (2) S0.5 "
       "dual scan both rounds: orders 154/154 acked strict rc0 zero new order; inbox 0 unread; "
       "D-19 dual hash MATCH-unchanged both scans (decisions 755428F8 / orders 3BF0F16E) zero "
       "action. (3) S1 smoke 48/48. (4) S2 boards empty (job_list 0; fleet 0 open). (5) S3: "
       "watermark red=false green (probe verdict py_low_board_clear = legal idle whitelist: "
       "board open=0, bandit 0, pool 3 ready all bm-b keepalive lane r487 manual-burn ban); "
       "next_pick=claimed (moneyflow IC reference batch); satengine rc0 alive (Tools face r467 "
       "law); post_review 5697 rows verdicts YES=4807/WAIT=852/NO=38 unresolved-NO=0 (all 38 "
       "NO superseded by later same-id YES re-derive, Tools/_r514bmc_s3.py scan); pool census "
       "403 = 399 done + 3 ready (FUND trio NULLS = bm-b RAM-gated keepalive lane, r487 "
       "manual-burn ban holds) + 1 waiting (W14-GENERATE governance-parked); compute_audit "
       "latest sole flag=supply_gap (structural, generator seats on other machines; zero "
       "zombies, zero GPU rogue, zero cap violation); N2-W15 judge-finalize seat = bm-a F-04 "
       "(watch only); fund-trio finalize = bm-b canonical (watch only); W3 next-wave = CEO "
       "ruling face (report delivered docs/trial_labor/CEO-REPORT-MASSW3-20261005.md); "
       "trial-labor standing line zero drafting (judgment chains in flight on other seats + "
       "W3 direction awaits CEO). (6) S6 38/38 legs rc0 NON-ZERO=none (r513 canon driver r514 "
       "copy; reconcile ZERO-DRIFT streak 14 @403 entries; CEO faces REPORT-2026-10-05 + "
       "LIVE-2026-10-05 regenerated ORANGE/COOL, market clock cell ORANGE_COOL, regime ORANGE "
       "days_in_state=2; bm-a hb stale 113-114min second consecutive round -> bm-c "
       "stale-takeover derives per O-2100 s2.4 on t35_open_fill_verify/paper_export/"
       "daily_scorecard/build_status; golden-week no-bar legs honest no-op; update_lhb no-op "
       "<30min guard; token_meter delta=0). (7) S7: attrition CLEAN rc0 (4 ledgers, 3 healed "
       "history rows noted); quartet 4/4 (loop pin=5 no-op first-fire 05:05 + watchdog "
       "re-registered first-fire 05:03 + both claws LF-normalized in-place).")

LAST = ("r514 bm-c: watch/maintenance round -- orders/D-19 dual-scan UNCHANGED zero unacked, "
        "smoke 48/48, S6 38/38 rc0 (CEO faces REPORT/LIVE-2026-10-05 regen, ZERO-DRIFT streak "
        "14), judgment seats all on other machines (N2 finalize=bm-a, fund-trio=bm-b), quartet "
        "4/4, attrition CLEAN, FF-only S0 integration of bm-b r708 wave, bm-a hb stale "
        "113-114min round 2 (stale-takeover derives).")

VERIFY = ("r514: receipts results/_r514bmc_s6_log.txt (38 legs rc0 log) + Tools/_r513bmc_s0.py "
          "probe output (dual hash 3BF0F16E/755428F8, both scans) + smoke 48/48 (04:57) + "
          "attrition CLEAN scan (results/_attrition_guard_scan.json) + orders 154/154 strict "
          "rc0 both scans + pool census 403 + post_review unresolved-NO=0 (Tools/_r514bmc_s3.py) "
          "+ quartet receipts (loop pin=5 no-op 05:05, watchdog first-fire 05:03, claws "
          "LF-normalized); delivery: FF-only S0 pre-merge + round commit + push_verify this "
          "close.")

NEXT = ("(a) 5x HANDOVER core = bm-c r515 (next round, round_no multiple of 5): update "
        "research/HANDOVER.md product list vs r511-515 window. (b) D-20261002-05 selftest "
        "seat window 10-06 00:00 (first round at/after window runs the pin selftest seat). "
        "(c) D-20261002-06 split closeout window 10-07 12:00. (d) N2-W15 judge-finalize = "
        "bm-a F-04 seat (<=10-12, r482 id-dup probe first), watch only. (e) fund-trio finalize "
        "10-05..10-09 (bm-b canonical, watch only). (f) W3 next-wave direction = CEO ruling "
        "face (report delivered). (g) market reopen 10-09 data-chain re-arm (G3); month-end "
        "first exam 10-31.")

NOTE = ("r514: watch/maintenance round. Zero seats, zero orders, zero drafting (judgment chains "
        "on other machines' seats + W3 direction awaits CEO). S6 CEO panels regenerated; bm-b "
        "r708 wave FF-integrated at open. bm-a heartbeat stale 113-114min second consecutive "
        "round (stale-takeover derives covered lane faces; bm-a machine health = bm-a fleet "
        "business, noted for GM visibility).")

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
st["round_no_label"] = "round 514 (bm-c)"
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# ---- heartbeat fleet/machines/bm-c.json ----------------------------------
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8-sig"))
hb["round_no"] = ROUND
hb["round_no_label"] = "round 514 (bm-c)"
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
hb["activity_now"] = ("r514: watch/maintenance closeout -- S6 38/38 rc0 (CEO faces REPORT/LIVE-"
                      "2026-10-05 regen + ZERO-DRIFT streak 14 + stale-takeover derives round "
                      "2) + smoke 48/48 + quartet 4/4 + attrition CLEAN + FF-only S0 "
                      "integration of bm-b r708 wave")
hb["latest_artifact"] = ("results/_r514bmc_s6_log.txt (38 legs rc0 05:01) + docs/live_usage/"
                         "LIVE-2026-10-05.md + docs/daily_report/REPORT-2026-10-05.md "
                         "(04:59-05:01 regen)")
hb["next_milestone"] = ("5x HANDOVER r515 (next round); D-20261002-05 selftest window 10-06 "
                        "00:00; D-20261002-06 closeout 10-07 12:00; N2 judge-finalize (bm-a "
                        "seat <=10-12); fund-trio finalize 10-05..09 (bm-b); market reopen "
                        "10-09; month-end 10-31")
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
line = (ts + " | r514 | dept:研究/工程（看护轮·orders/D-19 双扫+S6 CEO 面再生+双判决链席位观察） | "
        "watermark verdict=绿（red=false·lane healthy·probe 04:59·py_low_board_clear=板空合法白名单"
        "〔板 open=0·bandit 0·无可跑批=池 3 ready 全 bm-b keepalive 车道 r487 禁手工代烧〕） | " + CUR +
        " | 验证: smoke 48/48（04:57）+S6 日志 38 腿 0 非零（ZERO-DRIFT streak 14 @403 entries）"
        "+attrition CLEAN（4 账本·healed 史行照录）+orders 154/154 双扫零未回执+D-19 MATCH（755428F8）"
        "+GORDERS MATCH（3BF0F16E）+post_review 5697 行 unresolved-NO=0（38 NO 全被同 id 后续 YES "
        "re-derive 压制·_r514bmc_s3.py）+四件套 4/4（loop pin=5 no-op 首发保 05:05·watchdog 重注册 "
        "05:03·双爪 LF 归一在位）+sat-engine rc0 活+compute_audit 唯一旗=supply_gap（结构性供给缺口"
        "·发电机席位他机·零僵尸零 GPU 越权零越限） | 收口实录: S0=开轮 fetch behind=2（bm-b r708 波："
        "churn-absorb bm-a r709/710 死会话面+merge r708 13-commit 波合流）→脏∩入站=0→FF-only 正典收口"
        "（b3a72f3f9→7d581c4aa·零冲突零 UU）| 记分:1（S6 CEO 面再生=实际文件改动·看护轮如实计）| "
        "记账预算:3（state+心跳+轮报=法定 3）| 方法论捕获=无新方法（全链复用正典范式）·宝藏捕获=无"
        "（判决 finalize 未落·名单进出零·本批无五类收口面）| 登记册零命中断言=不适用（零清扫零 "
        "quarantine）| 本地未达 origin commit 数: 见 commit 后 push_verify 行 | 部门:研究/工程")
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
