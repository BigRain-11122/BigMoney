# -*- coding: utf-8 -*-
"""r515 bm-c round close: state-bm-c.json round_no++ + heartbeat write +
round report main line append. Laws: R170/R178 heartbeat epoch JSON-int;
R262 clock_read T-separator; EOL host-probe for append (r485).
Bloodline: Tools/_r514bmc_close.py."""
import json
import os
import subprocess
import time

import psutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
ROUND = 515


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

CUR = ("当前活: r515 看护收口+5x HANDOVER 核对（S6 38 腿 CEO 面再生+四件套自愈+orders/D-19 双扫零新令；"
       "双判决链席位他机=N2-W15 judge-finalize=bm-a F-04 席·fund-trio finalize=bm-b canonical；bm-a 心跳"
       "回新鲜=lane 守卫正让位·stale-takeover derive 收束） | 最近实物: 5x HANDOVER r511-515 窗行"
       "（research/HANDOVER.md·395→396 行字节手术自证）+S6 38/38 rc0（REPORT-2026-10-05+LIVE-2026-10-05 "
       "再生·ZERO-DRIFT streak 15 @403 entries） @ " + ts + " | 下个里程碑: N2 judge-finalize（bm-a 席·"
       "≤10-12·r482 id-dup probe 先行）；fund-trio finalize（bm-b·10-05..09）；D-20261002-05 selftest "
       "席位窗 10-06 00:00；D-20261002-06 拆件收口窗 10-07 12:00；W3 下一波方向 CEO 裁定（呈报已交）；"
       "复市 10-09 数据链重挂（G3）；月界首考 10-31；下个 5x=r520")

DID = ("r515 bm-c: watch/maintenance + 5x HANDOVER round (boards open=0, judgment-chain seats all on "
       "other machines, holiday no bar). (1) S0: fetch behind=0 ahead=0 at open -> zero integration "
       "needed (no surgery); dirty=2 daemon-live faces +1 r514 mmsg leftover (self artifact, folded "
       "into commit); dual watermark hash MATCH (decisions 755428F8 / orders 3BF0F16E) zero action. "
       "(2) S0.5 dual scan both rounds: orders 154/154 acked strict rc0 zero new order; inbox 0 "
       "unread. (3) S1 smoke 48/48 (05:07). (4) S2 boards empty (job_list 0; fleet 0 open). (5) S3: "
       "watermark red=false green lane healthy (probe 05:11 py_low_board_clear = legal idle "
       "whitelist: board open=0, bandit 0, pool 3 ready all bm-b keepalive lane r487 manual-burn "
       "ban); next_pick=claimed (moneyflow IC reference batch); satengine rc0 alive (Tools face "
       "r467 law); post_review 5,697 rows verdicts YES=4807/WAIT=852/NO=38 unresolved-NO=0 (38 NO "
       "all superseded by later same-id YES re-derive); pool census 403 = 399 done + 3 ready (FUND "
       "trio NULLS = bm-b RAM-gated keepalive lane, r487 manual-burn ban holds) + 1 waiting "
       "(W14-GENERATE governance-parked); trial-labor standing line zero drafting (judgment chains "
       "in flight on other seats + W3 direction awaits CEO); core deliverable = 5x HANDOVER check "
       "r511-515 window line (395->396 lines, +2967B, EOL-preserved byte surgery with assertions, "
       "ledger head 648,730 flat-hold verified live-read). (6) S6 38/38 legs rc0 NON-ZERO=none "
       "(canon driver r515; reconcile ZERO-DRIFT streak 15 @403 entries; CEO faces "
       "REPORT-2026-10-05 + LIVE-2026-10-05 regenerated idempotent; regime ORANGE days_in_state=2; "
       "bm-a heartbeat back FRESH 8min -> lane_io single-writer guards correctly re-yield to bm-a "
       "(stale-takeover derives end); golden-week no-bar legs honest no-op; token_meter delta "
       "recorded). (7) S7: attrition CLEAN rc0 (4 ledgers, 3 healed history rows noted); quartet "
       "4/4 (loop pin=5 no-op first-fire 05:15 + watchdog in-place next-fire 05:13 + both claws "
       "content-match in-place).")

LAST = ("r515 bm-c: watch/maintenance + 5x HANDOVER -- orders/D-19 dual-scan zero unacked, smoke "
        "48/48, S6 38/38 rc0 (CEO faces regen, ZERO-DRIFT streak 15), HANDOVER r511-515 window line, "
        "judgment seats all on other machines (N2 finalize=bm-a, fund-trio=bm-b), bm-a heartbeat "
        "back fresh (lane guards re-yield), quartet 4/4, attrition CLEAN.")

VERIFY = ("r515: receipts results/_r515bmc_s6_log.txt (38 legs rc0 log) + Tools/_r513bmc_s0.py "
          "probe output (dual hash 3BF0F16E/755428F8 MATCH both scans) + smoke 48/48 (05:07) + "
          "attrition CLEAN scan (results/_attrition_guard_scan.json) + orders 154/154 strict rc0 "
          "both scans + post_review unresolved-NO=0 (Tools/_r514bmc_s3.py) + HANDOVER byte-surgery "
          "assertions (395->396 lines +2967B EOL CRLF preserved, Tools/_r515bmc_handover.py) + "
          "quartet 4/4 (pin=5 no-op first-fire 05:15, watchdog in-place 05:13, claws MATCH); "
          "delivery: round commit + push_verify this close.")

NEXT = ("(a) N2-W15 judge-finalize = bm-a F-04 seat (<=10-12, r482 id-dup probe first), watch "
        "only. (b) fund-trio finalize 10-05..10-09 (bm-b canonical, watch only). (c) "
        "D-20261002-05 selftest seat window 10-06 00:00 (first round at/after window runs the pin "
        "selftest seat). (d) D-20261002-06 split closeout window 10-07 12:00. (e) W3 next-wave "
        "direction = CEO ruling face (report delivered). (f) market reopen 10-09 data-chain re-arm "
        "(G3); month-end first exam 10-31. (g) next 5x HANDOVER = bm-c r520.")

NOTE = ("r515: watch/maintenance + 5x HANDOVER round. Zero seats, zero orders, zero drafting "
        "(judgment chains on other machines' seats + W3 direction awaits CEO). bm-a heartbeat "
        "recovered fresh this round (was stale 113-114min two rounds) -- lane_io guards re-yielded, "
        "bm-c stale-takeover derives ended.")

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
st["round_no_label"] = "round 515 (bm-c)"
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# ---- heartbeat fleet/machines/bm-c.json ----------------------------------
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8-sig"))
hb["round_no"] = ROUND
hb["round_no_label"] = "round 515 (bm-c)"
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
hb["activity_now"] = ("r515: watch/maintenance + 5x HANDOVER closeout -- S6 38/38 rc0 (CEO faces "
                      "REPORT/LIVE-2026-10-05 regen + ZERO-DRIFT streak 15) + HANDOVER r511-515 "
                      "window line + smoke 48/48 + quartet 4/4 + attrition CLEAN")
hb["latest_artifact"] = ("research/HANDOVER.md (r511-515 5x window line, 395->396) + "
                         "results/_r515bmc_s6_log.txt (38 legs rc0) + docs/live_usage/"
                         "LIVE-2026-10-05.md + docs/daily_report/REPORT-2026-10-05.md (regen)")
hb["next_milestone"] = ("N2 judge-finalize (bm-a seat <=10-12); fund-trio finalize 10-05..09 "
                        "(bm-b); D-20261002-05 selftest window 10-06 00:00; D-20261002-06 "
                        "closeout 10-07 12:00; market reopen 10-09; month-end 10-31; next 5x "
                        "bm-c r520")
hb["prod_lanes"] = ("N2-W15 JUDGE: pool faces 13/13 done, judge-finalize = bm-a F-04 seat "
                    "(watch); fund-trio NULLS x3 bm-b canonical keepalive (watch only, r487 "
                    "manual-burn ban); W3 next wave = CEO ruling face; boards open=0; watermark "
                    "green")
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
line = (ts + " | r515 | dept:研究/工程（5x HANDOVER 核对轮·orders/D-19 双扫+S6 CEO 面再生+双判决链席位观察） | "
        "watermark verdict=绿（red=false·lane healthy·probe 05:11·py_low_board_clear=板空合法白名单"
        "〔板 open=0·bandit 0·无可跑批=池 3 ready 全 bm-b keepalive 车道 r487 禁手工代烧〕） | " + CUR +
        " | 验证: smoke 48/48（05:07）+S6 日志 38 腿 0 非零（ZERO-DRIFT streak 15 @403 entries）"
        "+attrition CLEAN（4 账本·3 healed 史行照录）+orders 154/154 双扫零未回执+D-19 MATCH（755428F8）"
        "+GORDERS MATCH（3BF0F16E）+post_review 5,697 行 unresolved-NO=0（38 NO 全被同 id 后续 YES "
        "re-derive 压制·_r514bmc_s3.py）+四件套 4/4（loop pin=5 no-op 首发 05:15·watchdog 在位 05:13·双爪 "
        "MATCH 在位）+sat-engine rc0 活+HANDOVER 字节手术自证（395→396 行 +2967B·Tools/_r515bmc_handover.py"
        "·统一链 648,730 实读平持核） | 收口实录: S0=开轮 fetch behind=0 零集成免手术（双水位 MATCH·D-19 "
        "零消费）| 记分:1（HANDOVER 5x 行+S6 regen=实际文件改动·看护轮如实计）| 记账预算:4（state+心跳+轮报"
        "+HANDOVER 5x 法定核对件）| 方法论捕获=无新方法（全链复用正典范式）·宝藏捕获=无（判决 finalize "
        "未落·名单进出零·本批无五类收口面）| 登记册零命中断言=不适用（零清扫零 quarantine）| 本地未达 "
        "origin commit 数: 见 commit 后 push_verify 行 | 部门:研究/工程")
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
