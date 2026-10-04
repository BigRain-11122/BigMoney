# -*- coding: utf-8 -*-
"""r507 bm-c round close: state-bm-c.json round_no++ + heartbeat write +
round report main line append (pre-commit; S7-close row appended after
delivery verify by _r507bmc_s7close_row.py). Laws: R170/R178 heartbeat
epoch JSON-int; R262 clock_read T-separator; EOL host-probe for append
(r485); smoke F7 self-checks after write."""
import json
import os
import subprocess
import time

import psutil

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
ROUND = 507


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

CUR = ("当前活: W3 judge finalize 烧录末段 IN_FLIGHT（pid 26052·cpu 16634s 前进·r487 三态 3 连"
       " IN_FLIGHT·w2 标定 4h44m vs age 279min）+N2-W15 JUDGE 12 分片池烧录在途（bm-a autofill "
       "全领 @01:56:04·daemon 领域零手工代领） | 最近实物: S6 38/38 rc0 CEO 面再生（REPORT-2026-10-05"
       "+LIVE-2026-10-05 @02:00-02:01·ORANGE/50%帽/COOL/6 员·多 lane 面 bm-a 心跳 stale 21-23min→"
       "bm-c stale-takeover derive O-2100 s2.4）+MSG-0125 消费（bm-a judge step-1 通报）"
       "+churn-absorb r507 零冲突集成 @ " + ts + " | 下个里程碑: W3 w3_judge.json 落地→r487 verify "
       "ADOPT_PASS→宝藏/方法论问+prereg §7/§8 回填+池翻面复检+48h CEO 报告钟（≤10-06 晚）；N2 judge "
       "烧完→judge-finalize 席位（≤10-12）；CEO 双链接点击（bm-b+bm-c）；D-20261002-05 selftest "
       "席位窗 10-06 00:00；D-20261002-06 拆件收口窗 10-07 12:00")

DID = ("r507 bm-c: watch/maintenance round under dual judgment chains (W3 finalize end-phase + "
       "N2 judge pool burn claimed by bm-a autofill; boards open=0; drafting exempt per MSG-0125 + "
       "trial labor law). (1) S0: churn-absorb 3 bm-c daemon faces (r620 law label r507, round_no "
       "read first) + pull --rebase clean (origin 8-commit treadmill integrated, zero conflict, "
       "tree clean after). (2) S0.5 dual scan: orders 154/154 acked zero new file; D-19 dual hash "
       "UNCHANGED both scans (decisions 755428F8 / orders 3BF0F16E) zero action. (3) S1 smoke "
       "48/48 (01:57). (4) S3: watermark green (red=false, next_pick moneyflow IC claimed/parked); "
       "py_low_with_work_cands named legal custody load (W3 judge finalize pid 26052 alive cpu "
       "advancing 14427->16634s + N2-W15 judge 12 shards all claimed by bm-a autofill @01:56:04 = "
       "dual chains in flight; boards open=0, bandit parked, holiday no bar); post_review today "
       "YES=168/WAIT=16 zero red rows; satengine rc0 alive (Tools face r467 law). (5) W3 judge "
       "custody 3 probes IN_FLIGHT healthy (single-thread end phase, cpu advancing; w2 calibration "
       "4h44m vs age 279min) -- adoption chain armed for landing round: r487 verify -> ADOPT_PASS -> "
       "treasure question + methodology question + prereg sec.7/8 backfill + pool flip recheck "
       "(r668) + 48h CEO clock (<=10-06 evening). (6) MSG-2026-10-05-0125-bma-ALL consumed to "
       "processed (info ack; bm-c lane = pool daemon burn already live). (7) S6 38/38 legs rc0 "
       "(CEO faces REPORT-2026-10-05 + LIVE-2026-10-05 regenerated 02:00-02:01, ORANGE cap 50% "
       "heat COOL 6 members; lane stale-takeover derive by bm-c for scorecard/paper/t35/prospect/"
       "daily_scorecard/dashboard faces per O-2100 s2.4, bm-a lane heartbeat stale 21-23min; "
       "dualrun ZERO-DRIFT streak 7 entries 403; holiday no-bar legs honest no-op). (8) S7: "
       "quartet 4/4 (loop pin=5 no-op first-fire 02:15 + watchdog in-place + both claws in-place); "
       "attrition CLEAN rc0 (4 ledgers, healed history rows noted). S6 runner Leg() "
       "Write-Output->Write-Host fix applied in r507 scratch copy (output-stream pollution made "
       "$fails always non-empty; log file stays truth face).")

LAST = ("r507 bm-c: watch/maintenance closeout -- churn-absorb r507 + clean rebase (8 commits), "
        "orders/D-19 dual-scan UNCHANGED, smoke 48/48, S6 38/38 rc0 (CEO faces REPORT/LIVE-"
        "2026-10-05 regen + stale-takeover derives), W3 custody 3x IN_FLIGHT healthy (adoption "
        "chain armed), N2 judge 12 shards bm-a autofill burn, MSG-0125 consumed, quartet 4/4, "
        "attrition CLEAN.")

VERIFY = ("r507: receipts results/_r507bmc_s6_log.txt (38 legs rc0, 60-line log verified 0 "
          "non-zero legs) + results/_r507bmc_s3probe.json (boards open=0/watermark green/pool "
          "seats/post_review zero red) + results/_r487bmc_w3_judge_verify.json (IN_FLIGHT custody "
          "liveness cpu advancing) + smoke 48/48 (01:57) + attrition CLEAN scan + orders 154/154 "
          "dual-scan + D-19 dual hash UNCHANGED; delivery: round commit + push_verify this close.")

NEXT = ("(a) W3 judge product landing watch next rounds: results/_r487bmc_w3_judge_verify.py -> "
        "ADOPT_PASS -> treasure question + prereg sec.7/8 backfill + pool flip recheck (r668) + "
        "48h CEO clock (<=10-06 evening). (b) N2-W15 JUDGE 12 shards: bm-a autofill burn watch "
        "(all claimed @01:56:04; burn <=10-12 then judge-finalize seat, r482 id-dup probe first). "
        "(c) CEO dual tailscale links click (bm-b a/14a391ef01dbc6 + bm-c a/13ac0ce1015dd3). "
        "(d) D-20261002-05 selftest seat window 10-06 00:00; D-20261002-06 split closeout window "
        "10-07 12:00. (e) fund-trio finalize 10-05..10-09 (bm-b canonical, watch only). "
        "(f) market reopen 10-09 data-chain re-arm (G3); month-end first exam 10-31. Next 5x "
        "HANDOVER = bm-c r510.")

NOTE = ("r507: watch/maintenance round under dual judgment chains (W3 finalize end-phase + N2 "
        "judge pool burn by bm-a autofill). Zero new drafting (trial labor law exemption holds per "
        "MSG-0125). Zero orders (154/154 dual scan). D-19 dual hash unchanged. S6 CEO panels "
        "regenerated. W3 adoption chain armed for the landing round.")

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
st["round_no_label"] = "round 507 (bm-c)"
with open(sp, "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# ---- heartbeat fleet/machines/bm-c.json ----------------------------------
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8-sig"))
hb["round_no"] = ROUND
hb["round_no_label"] = "round 507 (bm-c)"
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
hb["activity_now"] = ("r507: watch/maintenance closeout -- S6 38/38 rc0 (CEO faces REPORT/LIVE-"
                      "2026-10-05 regen + stale-takeover derives) + smoke 48/48 + quartet 4/4 + "
                      "attrition CLEAN + W3 custody IN_FLIGHT healthy + N2 judge 12 shards bm-a "
                      "autofill burn + MSG-0125 consumed")
hb["latest_artifact"] = ("results/_r507bmc_s6_log.txt (38 legs rc0 02:01) + docs/live_usage/"
                         "LIVE-2026-10-05.md + docs/daily_report/REPORT-2026-10-05.md (02:00-02:01 "
                         "regen) + results/_r507bmc_s3probe.json")
hb["next_milestone"] = ("W3 w3_judge.json landing -> ADOPT_PASS -> 48h CEO clock (<=10-06 "
                        "evening); N2 judge 12 shards burn <=10-12 -> judge-finalize; CEO "
                        "dual-link click; D-20261002-05 window 10-06; D-20261002-06 closeout "
                        "10-07; fund-trio finalize 10-05..09")
hb["prod_lanes"] = ("W3-JUDGE: finalize wave-3 IN_FLIGHT on bm-c (pid 26052, end-phase, custody "
                    "_r487bmc tri-state, adoption chain armed); N2-W15 JUDGE: 12 shards all "
                    "claimed by bm-a autofill @01:56:04 (daemon territory, burn <=10-12); "
                    "fund-trio NULLS x3 bm-b canonical keepalive (watch only); boards open=0; "
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
line = (ts + " | r507 | dept:研究（W3/N2 双判决链看护轮·S6 CEO 面再生·舰队维护） | "
        "watermark verdict=绿（red=false·next_pick moneyflow IC claimed/parked 自愈面照旧·S6probe "
        "01:59）·py_low_with_work_cands 点名=合法托管载（W3 judge finalize pid 26052 活 cpu 16634s "
        "前进〔r487 三态 3 连 IN_FLIGHT·w2 标定 4h44m vs age 279min 末段〕+N2-W15 JUDGE 12 分片 bm-a "
        "autofill 全领烧录 @01:56:04=双判决链在飞；板 open=0·bandit parked·金周无 bar） | "
        + CUR + " | 验证: smoke 48/48（01:57）+S6 日志 60 行 0 非零腿+attrition CLEAN+orders/D-19 "
        "双扫 UNCHANGED+四件套 4/4（loop pin=5 no-op）+S6 runner Leg() Write-Host 修正注记（"
        "fails 数组显示瑕疵·日志为真面）| 部门:研究")
with open(rp, "ab") as f:
    f.write(line.encode("utf-8") + eol)

# ---- self-checks (smoke F7 laws) -----------------------------------------
chk = json.loads(open(sp, encoding="utf-8-sig").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"] and "+08:00" in chk["clock_read"], "clock_read format"
chk2 = json.loads(open(hp, encoding="utf-8-sig").read())
assert isinstance(chk2["heartbeat_epoch_utc"], int), "hb epoch not int"
assert chk2["round_no"] == ROUND and chk["round_no"] == ROUND
assert "orders_ack" in chk2 and len(chk2["orders_ack"]) >= 150
print("CLOSE_OK", ts, "cpu=", cpu, "ram_avail=", ram_avail, "gpu_free=", gpu_free,
      "epoch=", epoch, "eol=", repr(eol))
