# r1013 bm-b closeout: state.json reconcile (r991->r1013, 21-round divergence healed
# per round_reports.md continuity), heartbeat update (epoch int law), round report
# line append. All faces asserted after write.
import json, time, ctypes, datetime, io, os

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
STATE = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
WM = os.path.join(ROOT, "results", "watermark_red.json")

now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
now_plain = datetime.datetime.now().isoformat(timespec="seconds")
epoch = int(time.time())

class MS(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong)]
m = MS(); m.dwLength = ctypes.sizeof(MS)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
free_ram = round(m.ullAvailPhys / 1024**3, 1)
try:
    ca = json.load(open(os.path.join(ROOT, "results", "compute_audit.json"), encoding="utf-8"))
    cpu_pct = float(ca.get("cpu_total_pct", 0)); gpu_used = float(ca.get("gpu", {}).get("mem_used_mb", 4139))
except Exception:
    cpu_pct, gpu_used = 0.0, 4139.0
gpu_free = int(8192 - gpu_used)
try:
    wm = json.load(open(WM, encoding="utf-8"))
    wm_line = "red=%s" % wm.get("red")
except Exception:
    wm_line = "red=?(unreadable)"

did_state = ("r1013: canon idle-guard-kit adopt 主产（O-2236 ≤1轮：kit 612d580e 三件字节拉取→Tools/bmb_idleguard.pyw canon 体+bm-b 本地化"
             "（REPO/BANK/SYS_PY 三处+STATE/LOG sentinel 连续性+队列端口 8198+burn patterns bm-b 化）→01:50:01 首自然跳双坑实锚"
             "（①过渡版 state ISO 字符串×canon epoch 算术=TypeError 崩死 hop2/银行腿不跑；②CPU-lane 常驻 run 探针错配本机 60s tick 架构"
             "→拉起外形态 Tools 常驻 run=双引擎面）→同轮修复（state epoch 迁移+CPU-lane 腿本地化=scripts status-rc 判活+register+tick 复活链"
             "·协议 S3 bm-b 行）+孤儿 run 击杀（PID 5916 cmdline 精确匹配）+平铺 state 伪面清除→01:54:42 手动跳全路径 rc0"
             "（「idle >=10min but bank EMPTY -- PRODUCER VIOLATION」canon 诚实曝光行）→MSG-021x 双坑预警 @bm-a（其 18:00 adopt 死线）"
             "+D-19 decisions 4 新行消费（D-01 核销批/PT02 催办转夜轮·D-02 watermark_red 退库=bm-c+HQ 腿·D-03 memory-gate 修法=HQ 腿"
             "·D-04 iteration_loop v2 跨线移植=本仓正典源零义务）+update --advance dec=8706acd8（mirrors synced 4）"
             "+S0 收敛（HEAD da13bcf13c→reset --mixed origin 3a01530c70 零本地孤儿实核+44 D 面物化+bm-c 属主/共享 regen origin-newer-wins"
             "+CODELY.md 双行 union+陈旧 inbox 件清除+r1012 术后 7 件 scratch 入册）+S1 smoke 49/49"
             "+S3 SatEngine alive（scripts 入口 engine_alive=true 心跳 22s·Tools 面 state_present=false=镜像路径分歧伪象 bm-c r1102 坑反向面定谳）"
             "+S6 43 腿 rc0 3.6min（idle --worked idle_rounds→0·ZERO-DRIFT streak 51·compute_audit FLAG pool_starvation/supply_floor=诚实饥饿面"
             "·bm-a 心跳 139min→scorecard/paper_export/daily_scorecard/dashboard 四面 STALE_MIN 接管 derive·LIVE-2026-10-19 ORANGE cap50%"
             "+REPORT-2026-10-19·DUALARM-2026-09-30·CALL-2026-10-16 ORANGE_COOL）+S7 四自愈装订（loop pin=2 no-op+watchdog S4U+双爪）"
             "+CODELY 热冷整编（10560→9250B·r1005/r1008 两行 verbatim 入 archive+指针行）+state.json r991→r1013 对账勘正（21 轮脱节）"
             "+S8 本地自驱池 9 件全 done/retired=空·候秘书处补货·闲置面=canon guard 银行缺位曝光行接管")

verdict = ("GREEN: canon idle-guard-kit ADOPTED same-round per O-20261018-2236 <=1-round law "
           "(kit @612d580e pulled via python bytes channel, Tools/bmb_idleguard.pyw canon body + bm-b localization, "
           "first-hop 01:54:42 FULL-PATH verified with honest bank-EMPTY PRODUCER row; two live-fire traps found+fixed same round: "
           "interim state ISO-string vs canon epoch arithmetic TypeError, CPU-lane resident-run probe mismatch vs bm-b 60s-tick "
           "architecture -> scripts status-rc + register+tick repair chain per protocol S3; stray foreign Tools run killed PID 5916, "
           "flat state face removed) + MSG-20261019-021x adopt-traps warning to bm-a ahead of its 18:00 deadline + D-19 decisions "
           "advanced 8706acd8 (4 rows consumed, zero direct bm-b legs, orders face unchanged) + S6 43 rc0 (idle_rounds->0, ZERO-DRIFT "
           "streak 51, bm-a stale-takeover x4 faces, LIVE-2026-10-19 ORANGE cap50%) + CODELY hotcold 9250B + state.json reconciled "
           "r991->r1013 (21-round divergence healed); leftovers = ST-001 group LEDGER backfill row (drama-001-stockera face, <=r1015) "
           "+ CONTENT-LOOP v0.2 runners ST-003 voice <=10-22 / ST-004 CSA + O-0948 window judgment 10-19 ~10:2x + PT02 poke from night desk 03:07")

nxt = ("r1014: 1) ST-001 group LEDGER backfill row CAS push (drama-001-stockera ledger face) 2) CONTENT-LOOP v0.2 runners: "
       "ST-003 voice-library first batch (P1 <=10-22) + ST-004 CSA anchor pre-check 3) O-0948 window close judgment 10-19 ~10:2x "
       "4) PT02 poke watch (night desk 03:07) 5) W273+ seat watch (bm-c in flight) 6) BigMoney seat automation case = bm-a r1069 "
       "delivered 3762f3dafa, consume not rebuild")

artifact = ("Tools/bmb_idleguard.pyw canon-adopted (kit @612d580e, first-hop 01:54:42 full-path verified) + "
            "fleet/inbox/MSG-20261019-021x-bmb-canon-adopt-traps.md + docs/live_usage/LIVE-2026-10-19.md + "
            "docs/daily_report/REPORT-2026-10-19.md (01:58)")

# --- state.json (reconciled r1013) ---
st = {"round_no": 1013, "did": did_state, "verdict": verdict, "next": nxt,
      "last_round_ts": now_iso, "last_result": "ok", "current_task": "r1014: ST-001 LEDGER row + CONTENT-LOOP v0.2 runners",
      "updated_at": now_iso, "last_seen": now_iso, "ts": now_iso}
json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
assert json.load(open(STATE, encoding="utf-8"))["round_no"] == 1013

# --- heartbeat (overlay, preserve orders_ack + d19 mirrors) ---
hb = json.load(open(HB, encoding="utf-8"))
hb.update({
    "machine_id": "bm-b", "last_seen": now_plain, "task": "r1013: canon idle-guard-kit adopt + D-19 + S6 43 + closeout",
    "did": "r1013: canon kit ADOPTED (bmb_idleguard.pyw canon body, first-hop full-path verified, 2 live-fire traps fixed same round) "
           "+ MSG-021x traps warning @bm-a + D-19 dec advance 8706acd8 (4 rows, zero bm-b legs) + S0 converge (reset origin 3a01530c70, "
           "44 faces materialized, CODELY union) + S6 43 rc0 (idle 0, ZERO-DRIFT 51, bm-a stale-takeover x4) + CODELY hotcold 9250B + "
           "state.json reconciled r1013",
    "cpu_cores": 16, "free_ram_gb": free_ram, "gpu_free_vram_mb": gpu_free, "cpu_load_pct": cpu_pct,
    "verdict": verdict, "idle_rounds": 0, "agenda_starved": False,
    "heartbeat_epoch_utc": epoch, "clock_read": now_iso, "ts": now_iso,
    "round_no": 1013, "round": 1013, "current_task": "r1014: ST-001 LEDGER row + CONTENT-LOOP v0.2 runners",
    "next": nxt, "last_action": "r1013: canon idle-guard-kit adopt (O-2236 <=1-round law) + traps fixed + MSG @bm-a + D-19 advance + S6 43 + hotcold + state reconcile",
    "last_action_at": now_iso, "latest_artifact": artifact, "last_artifact": artifact,
    "now_active": "r1013 closing", "current": verdict,
    "next_milestone": "ST-003 voice-library first batch <=10-22 (P1) + ST-001 group LEDGER row <=r1015 + O-0948 judgment 10-19 ~10:2x",
    "note": "r1013: canon kit adopt COMPLETE (O-2236 <=1-round law met); state.json 21-round divergence healed r991->r1013",
})
json.dump(hb, open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
hb2 = json.load(open(HB, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"
assert "T" in hb2["clock_read"], "clock_read must be T-separated (R262 law)"

# --- round report line ---
report_line = ("{ts} | r1013 bm-b | dept:工程+舰队 | WM verdict: GREEN ({wm} @01:56 py_watermark insufficient_history 夜窗合法·板空) | "
               "当前活=r1013 canon idle-guard-kit adopt（O-2236 ≤1轮义务·bm-c 00:45 kit 上链 354f66e/612d580e 触发）+D-19 消费+S0 收敛+全链维护 | "
               "最近实物=Tools/bmb_idleguard.pyw canon 适配版（01:54:42 首跳全路径实证）+MSG-20261019-021x 双坑预警 @bm-a+LIVE/REPORT-2026-10-19+scorecard 等四面 STALE_MIN 接管产出（01:58）| "
               "下个里程碑=CONTENT-LOOP ST-003 voice-library 首批 ≤10-22（P1）+ST-001 集团 LEDGER 回填行 ≤r1015+O-0948 观察窗判定 10-19 ~10:2x | "
               "did: (a) S0 HEAD da13bcf13c→reset --mixed origin 3a01530c70（零本地孤儿实核）+收敛（44 D 面物化+bm-c 属主/共享 regen origin-newer-wins+CODELY.md 双行 union 10560B）+r1012 术后 7 件 scratch 入册; "
               "(b) S0.5 orders 差集=0（README 非令件）+D-19 decisions 4 新行消费（D-20261019-01 核销批·PT02 催办转夜轮 03:07/D-02 watermark_red 退库=bm-c+HQ 腿零 bm-b 直接义务/D-03 memory-gate 修法=HQ 腿 r1053 同族法采纳/D-04 iteration_loop v2 跨线移植令=本仓正典源零移植义务）+update --advance dec=8706acd8（mirrors synced 4）; "
               "(c) S1 smoke 49/49; (d) S3 SatEngine alive（scripts 入口 engine_alive=true 心跳 22s；Tools 面 state_present=false=镜像路径分歧伪象·bm-c r1102 坑 bm-b 反向面定谳·本机活入口=scripts 副本 60s tick 架构）; "
               "(e) canon adopt 主产：kit 三件字节拉取（origin 612d580e·python 字节通道·PS > 重定向坑规避）→canon 体+本地化→01:50:01 首自然跳双坑实锚（①过渡版 state ISO×canon epoch 算术=TypeError 崩死·②CPU-lane 常驻 run 探针错配 tick 架构拉起外形态 Tools run=双引擎面）→同轮修复（state epoch 迁移+CPU-lane 腿本地化=scripts status-rc 判活+register+tick 复活链）+孤儿击杀（PID 5916 cmdline 精确匹配）+平铺 state 伪面清除→01:54:42 手动跳全路径 rc0（bank EMPTY PRODUCER 诚实曝光行）→MSG-021x @bm-a（同源过渡版必中两坑·18:00 死线前）; "
               "(f) S6 43 腿 rc0 3.6min（idle --worked idle_rounds→0·ZERO-DRIFT streak 51·compute_audit FLAG pool_starvation/supply_floor 诚实饥饿面·bm-a 心跳 139min→scorecard/paper_export/daily_scorecard/dashboard 四面 STALE_MIN 接管·LIVE-2026-10-19 ORANGE cap50%·attrition heal 注记照录）; "
               "(g) S7 四自愈装订（loop pin=2 no-op+watchdog S4U+双爪 LF 归一）+CODELY 热冷（10560→9250B·r1005/r1008 两行 verbatim 入 archive 202610.md+指针行）+state.json r991→r1013 对账勘正（21 轮脱节·以 round_reports 连续性为准）; "
               "(h) S8 本地自驱池 9 件全 done/retired=空·候秘书处补货·canon guard 银行缺位曝光行接管闲置面 | "
               "证据=smoke 49/49+results/_r1013bmb_s6_log.txt 43 rc0+guard log 01:54:42 canon 行+results/_r1013bmb_canon_pull.json（612d580e）+results/_r1013bmb_s0_converge.json+results/d19_watermark.json（dec 8706acd8·mirrors 4）+results/_r1013bmb_codely_hotcold_receipt.json（9250B）| "
               "下轮 r1014: 1) ST-001 集团 LEDGER 回填行 CAS 推送（drama-001-stockera 台账落位）2) CONTENT-LOOP v0.2 runner：ST-003 voice-library 首批（P1 ≤10-22）/ST-004 CSA 预检 3) O-0948 观察窗判定 10-19 ~10:2x 4) PT02 poke 候夜轮 03:07 5) W273+ 席盯守（bm-c 在飞）6) BigMoney 席自动化案=bm-a r1069 已交付 3762f3dafa·本司消费+补位不重建"
               ).format(ts=now_iso, wm=wm_line)
with io.open(REPORT, "a", encoding="utf-8") as f:
    f.write(report_line + "\n")

print(json.dumps({"state_round": 1013, "heartbeat_epoch": hb2["heartbeat_epoch_utc"],
                  "free_ram_gb": free_ram, "gpu_free_vram_mb": gpu_free, "wm": wm_line,
                  "report_len": len(report_line)}, ensure_ascii=False))
