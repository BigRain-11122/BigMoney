# r981 closeout prep: state + heartbeat + round report row (pre-surgery facts only)
import json, time, datetime

NOW = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# ---------- state.json ----------
st = json.load(open("state.json", encoding="utf-8"))
st["round_no"] = 981
st["round"] = 981
st["round_no_label"] = "r981"
st["clock_read"] = NOW
st["ts"] = NOW
st["updated"] = NOW
st["updated_at"] = NOW
st["last_seen"] = NOW
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["last_action"] = "r981: S7 LogonType regression captured + root-fixed (both register recipes S4U-via-XML-flip, live tasks verified S4U) + D-19 zero-delta + S6 39 legs green + i2v 51/53"
st["last_action_at"] = NOW
st["current_task"] = "r981: LogonType S4U recipe fix + S6 39 legs + D-19 zero-delta + batch watches"
st["task"] = "r981: LogonType S4U recipe fix + S6 39 legs + D-19 zero-delta + batch watches"
st["current"] = "r981: S7 LogonType regression fix + S6 chain + D-19 probe + i2v/astock watches"
st["now_active"] = "r981: live faces = i2v runner 28900 + ComfyUI 28848 (batch 51/53, KN_KN01 in flight) + backfill worker 8380 (astock rebuild march)"
st["did"] = ("r981: (a) C-r980 receipt consumed: e6ad9982d6 == origin/main tip at round start (merge-base --is-ancestor rc=0, behind=0) "
             "(b) D-19 dual-sha re-probe ZERO genuine delta: decisions full sha256 ab3f0cc9f4cb9bbb...e0ba8fd identical to r980 probe; orders blob sha1 3b1ca198bdd95a57635bab465f0c8bcb9c7d4cf8 "
             "identical to stored watermark (direct hashlib verification over fresh dump); probe changed-flags = short-watermark-vs-full-sha (decisions) + sha256-vs-sha1-method (orders) "
             "comparison artifacts, r980 family same-judgment; watermarks hold (dec ab3f0cc9 / ord 3b1ca198) "
             "(c) S0.5 orders/inbox scan zero-new: no new O-* orders, no new inbound MSGs on origin; O-20261014-0312-bm-c read+verified = bm-c-addressed dispatch already receipted by bm-c "
             "r978-continuation in-file (pulse cadence choice), zero bm-b action; own orders O-20261015-0025/0906/0915/0952 + own MSGs 0104/0825/0952 all standing on origin "
             "(d) S7 LogonType regression CAPTURED + ROOT-FIXED (round main product): Bigmoney-LoopWatchdog live task found at InteractiveToken (zhi-shi-yong-jiao-hu-fang-shi = 10-15 09:16 "
             "sister pit recaptured; both registration recipes register_loop_task.ps1/register_watchdog_task.ps1 still default-principal at r981 - the 09:16 script-side fix never landed in repo, "
             "disk==origin hash-verified both) -> live heal: watchdog re-registered S4U+SWA=false via XML flip (backup %TEMP%\\bmb-s4u-backup-watchdog-r981.xml), loop task verified S4U+SWA=false "
             "intact -> root fix: BOTH recipes rewritten to S4U-via-XML-flip (live-fire discovery: this host Register-ScheduledTask has NO -LogonType parameter, WinPS 5.1 PSScheduledTask module "
             "face; -LogonType attempt failed -> honest fallback fired once -> recipe v2 = default register + export + patch LogonType/SWA + -Xml re-register; flip failure = task left alive + "
             "honest WARN line, no false success per r521; D-20261002-02 honest-fail concern preserved) -> exercise proof: watchdog recipe re-run output 'logon=S4U via XML flip' + schtasks both "
             "tasks = jiao-hu-fang-shi/hou-tai-fang-shi (S4U); loop recipe phase no-op now S4U-enforcing on future drift re-registrations "
             "(e) S6 39 legs CHAIN_DONE nonzero=0 (log _r981bmb_s6chain.log): shell tool 5-min-no-output auto-cancel killed the chain driver at build_status leg after 36 legs -> 3 legs "
             "(build_status/token_meter/attrition_guard) re-run rc=0, no partial damage (build_status rewrote dashboard faces fully); pool_dualrun ZERO-DRIFT streak 36; compute_audit flags "
             "pool_starvation,supply_floor (standing honest face - pool empty, MSG-0825 cpu-pool-restock request standing on origin since r974, RAM<4GB gate blocks new heavy batches); "
             "update_daily 0 new rows pre-close cutoff 10-14; market_regime ORANGE day4 shadow; strategy_scorecard bm-b stale-takeover derive (bm-a hb stale 277min, O-2100 s2.4 STALE_MIN law) "
             "6 traders S=2 A=4 B=0 C=0; minute_feed +105 rows/5 codes; b_layer mask 5222 ok 3517 excluded 1705; attrition CLEAN; docs faces REPORT/LIVE-2026-10-15 written local NOT pushed "
             "(anti-regression vs bm-a fresh-host derive window) "
             "(f) smoke 49/49 green (g) saturation engine live-probed alive (rc=0, queue 0, verdict idle - real probe this round, not chain proxy) "
             "(h) watermark GREEN (red=false, lane=healthy, next_pick=claimed moneyflow IC candidate blocked on parked panel) "
             "(i) i2v batch verdict: 51/53 clips (46->51 in round window, comfy-out-480 33, KN_KN01 in flight, ZERO fails - no fails file), GPU 100% - completion verdict + valve-out "
             "(keepwarm.pause removal + KeepWarm re-pin per r916 law) = next round (ETA ~15:45-16:00) "
             "(j) astock rebuild verdict: worker 8380 alive, per_files_on_disk 2996/5219 (2596->2996 in round window, ~+20/min), ETA ~17:00-17:30 - completion package next rounds "
             "(k) S8 green_idle=false (RAM 7.8% free batch window; claimable_pool_lines=1; idle_rounds=0; no idle sin - two CEO production lines marching) "
             "(l) orphan face=1 (19 py faces, 1 flagged = i2v runner sleeping-orchestrator false-positive family, standing note; probe _orphan_face_probe.bm-b.json) "
             "(m) C-r981 own-face surgery push in closeout segment C (receipt = results/_r981bmb_push_receipt.json, consumed next round)")
st["verdict"] = ("GREEN-production-tail: i2v 51/53 (~2 remaining, completion+valve-out next round); astock rebuild 2996/5219; "
                 "S7 LogonType regression captured+root-fixed (S4U recipes landed, live tasks verified); D-19 zero-delta; S6 39 legs green; worktree bulk normalization still deferred (quiet window)")
st["next"] = ("r982: 1) i2v 53/53 completion verdict -> valve-out (remove C:\\Fluxgroup\\MiniGame\\Tools\\Ollama\\keepwarm.pause + KeepWarm re-pin per r916 law) + completion package 2) C-r981 receipt consume "
              "3) astock refresh completion watch -> data churn completion package push 4) D-19 dual-sha re-probe 5) S7 quad (LogonType spot-check = regression watch face) 6) S8 gate "
              "7) r981 addendum row lands with r982 push face")
st["next_milestone"] = "i2v 53/53 -> valve-out ~15:45-16:00 today (window <=48h); astock completion package ~17:00-17:30 today"
st["last_artifact"] = "results/_r981bmb_push_receipt.json (next-round consume)"
st["latest_artifact"] = "results/_r981bmb_push_receipt.json (next-round consume)"
st["orphan_face"] = 1
st["orphan_faces"] = 1
st["orphan_face_note"] = "r981 probe: 19 py faces, 1 flagged (i2v runner 28900 = sleeping-orchestrator false-positive family; r978/r979/r980 standing note maintained; batch healthy GPU 100%)"
st["note"] = ("r981: docs faces (daily_report/live_usage) written local, NOT pushed (anti-regression: bm-a fresh-host derive cycle owns window); S7 LogonType fix faces "
              "(Tools/register_loop_task.ps1 + Tools/register_watchdog_task.ps1) IN PUSH PAYLOAD (shared cross-machine fix, MSG-20261015-0906 prescription); orphan face=1 "
              "(i2v runner false-positive family); results working files local (fresh views) per r975 precedent")
# D-19 probe faces
st["last_decisions_at"] = NOW
st["last_decisions_read_at"] = NOW
st["last_orders_at"] = NOW
st["last_orders_read_at"] = NOW
st["last_decisions_probe_at"] = NOW
st["last_orders_probe_at"] = NOW
st["decisions_delta_pending"] = False
st["orders_delta_pending"] = False
st["d19_probe_due"] = False
st["d19_probe_due_note"] = "r981 round-start probe consumed (zero genuine delta; dec ab3f0cc9 / ord 3b1ca198 hold; probe changed-flags = comparison artifacts, sha1 method verified directly); next probe = r982 round-start cadence"
st["last_decisions_sha"] = "ab3f0cc9"
st["last_orders_sha"] = "3b1ca198"
st["last_decisions_sha_probe"] = "ab3f0cc9f4cb9bbb1f23c5e5a98bd5bed540a272b0b111bb481120ea7e0ba8fd"
st["last_orders_sha_probe"] = "3b1ca198bdd95a57635bab465f0c8bcb9c7d4cf8"
st["last_orders_sha_probe_note"] = "r981: probe reported orders_changed=true via sha256-vs-short-sha1-watermark comparison artifact; direct hashlib.sha1 over fresh dump = 3b1ca198bdd95a57635bab465f0c8bcb9c7d4cf8, identical to watermark = zero genuine delta"
st["last_decisions_sha_method"] = "r981: origin blob sha256 via git show (group fetch in-probe); unchanged vs r980 probe"
st["last_orders_sha_note"] = "r981: zero genuine delta - orders blob sha1 identical to stored watermark (direct verification over results/_r686bmb_orders_fresh.md dump)"
# sat engine
st["sat_engine"] = {"status": "alive (live-probed rc=0 this round: queue 0, verdict idle)", "checked_at": NOW}
# sync block
st["sync"]["r980_main_push"]["consumed_at"] = NOW
st["sync"]["behind_origin_main"] = 0
st["sync"]["r981_main_push"] = {
    "status": "PENDING_AT_HASH_TIME",
    "consumed_at": "pending r982",
    "behind_origin_main": 0,
    "note": "C-r981 payload = own faces (state/heartbeat/round report + S7 LogonType recipe fix 2 faces + s6chain work files + d19 probe + orphan probe + astock status + attrition scan + market_clock/thermo/dualarm/minute_feed diff faces); base = origin tip fresh at surgery; docs faces intentionally excluded (anti-regression); receipt = results/_r981bmb_push_receipt.json",
}
with open("state.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state.json updated")

# ---------- heartbeat ----------
h = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8"))
h["last_seen"] = NOW
h["task"] = "r981: S7 LogonType regression captured+root-fixed (S4U recipes) + D-19 zero-delta + S6 39 legs + i2v 51/53 watch"
h["did"] = ("r981: (a) C-r980 receipt consumed (e6ad9982d6 = origin tip, merge-base rc=0, behind=0) (b) D-19 zero genuine delta (decisions full-sha identical to r980 probe; orders sha1 "
            "3b1ca198...9c7d4cf8 identical to watermark via direct hashlib verification; probe changed-flags = comparison artifacts) (c) S0.5 scan zero-new orders/MSGs; O-20261014-0312-bm-c "
            "verified bm-c-receipted zero bm-b action (d) S7 LogonType regression CAPTURED+ROOT-FIXED: watchdog live task was InteractiveToken (09:16 sister pit; both recipes still "
            "default-principal at r981, disk==origin hash-verified) -> live heal S4U+SWA=false via XML flip (backup %TEMP%\\bmb-s4u-backup-watchdog-r981.xml), loop verified S4U+SWA=false intact "
            "-> both recipes rewritten S4U-via-XML-flip (host Register-ScheduledTask has no -LogonType param = WinPS5.1 module face; flip failure = task left alive + honest WARN) -> "
            "recipe re-run proof 'logon=S4U via XML flip' + schtasks both S4U (e) S6 39 legs CHAIN_DONE nonzero=0 (driver killed by shell auto-cancel at build_status leg after 36; 3 legs "
            "re-run rc=0; pool_dualrun streak 36; compute_audit pool_starvation/supply_floor standing; minute_feed +105 rows; scorecard stale-takeover derive per O-2100 s2.4) (f) smoke 49/49 "
            "(g) sat engine live-probe alive (h) watermark GREEN (i) i2v 51/53 zero fails ETA ~15:45-16:00 valve-out next round (j) astock 2996/5219 ETA ~17:00-17:30 (k) S8 green_idle=false "
            "no idle sin (l) orphan face=1 standing (m) C-r981 own-face surgery in segment C")
h["verdict"] = ("GREEN-production-tail: i2v 51/53 (valve-out next round); astock 2996/5219; LogonType S4U regression captured+root-fixed; "
                "D-19 zero-delta; S6 39 legs green; worktree normalization deferred")
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["heartbeat_epoch_utc"] = EPOCH
h["clock_read"] = NOW
h["ts"] = NOW
h["orders_ack"] = ("r981: d19 round-start probe consumed - ZERO genuine delta (decisions ab3f0cc9 full-sha identical to r980 probe; orders sha1 3b1ca198bdd95a57635bab465f0c8bcb9c7d4cf8 "
                  "identical to watermark by direct hashlib verification over fresh dump; probe changed-flags = short-wm-vs-full-sha + sha256-vs-sha1-method comparison artifacts); S0.5 "
                  "scan zero-new orders/zero-new inbound MSGs (O-20261014-0312-bm-c read+verified = bm-c-addressed pulse-cadence dispatch, already receipted by bm-c r978-continuation, zero "
                  "bm-b action); own orders O-20261015-0025/0906/0915/0952 + own MSGs 0104/0825/0952 all on origin standing | " + h.get("orders_ack", ""))
h["note"] = ("r981: docs faces written local NOT pushed (anti-regression bm-a derive window); S7 LogonType recipe fix 2 faces IN PUSH PAYLOAD (shared cross-machine fix, MSG-20261015-0906 "
             "prescription); orphan face=1 (i2v runner false-positive family); results working files local per r975 precedent")
with open(r"fleet\machines\bm-b.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)

# self-check: epoch must be int (R170/R178 law)
h2 = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in h2["clock_read"] and " " not in h2["clock_read"], "clock_read must be T-separated ISO"
print("heartbeat updated; epoch int verified:", h2["heartbeat_epoch_utc"])

# ---------- round report row (append-only, binary) ----------
row = ("%s | r981 | C-r980 回执消费（e6ad9982d6=origin tip·merge-base rc=0·behind=0）+D-19 双 sha 复探零真实增量（decisions 全 sha 与 r980 探针恒等 ab3f0cc9·"
       "orders sha1 3b1ca198bdd9…9c7d4cf8 与水位恒等=对 fresh dump 直接 hashlib 复核·probe changed 旗=短水位对全长 sha+sha256-vs-sha1 法比较工件假阳·r980 族同判）+S0.5 令扫零新令零新 MSG"
       "（O-20261014-0312-bm-c 实读=bm-c 属主 pulse 节律派单·bm-c r978-continuation 已回执·零 bm-b 腿）+smoke 49/49+**S7 LogonType 回归抓获+根治（本轮主产出）**："
       "Bigmoney-LoopWatchdog 实况=只使用交互方式（InteractiveToken 回归=10-15 09:16 姊妹坑复发·两配方脚本 r981 时点仍默认 principal=09:16 脚本侧修法从未落仓·disk==origin 双 hash 实证）→"
       "活体修复=watchdog XML flip S4U+SWA=false（备份 %%TEMP%%\\bmb-s4u-backup-watchdog-r981.xml）+loop 任务实证 S4U+SWA=false 无恙→根因修=两配方（register_loop_task.ps1/"
       "register_watchdog_task.ps1）改 S4U-via-XML-flip（本机 Register-ScheduledTask 无 -LogonType 参数=WinPS5.1 模块面首弹实证·-LogonType 版失败诚实回退一次后配方 v2=默认注册→export→"
       "patch LogonType/SWA→-Xml 重注册·flip 败=任务保活+诚实 WARN 不假成功 r521·D-20261002-02 保活关切保留）→配方回跑实证「logon=S4U via XML flip」+schtasks 双任务登录状态=交互方式/后台方式+"
       "S6 39 腿 CHAIN_DONE nonzero=0（log=results/_r981bmb_s6chain.log·shell 工具 5min 无输出自动取消杀驱动于 build_status 腿=36 腿后断·3 腿补跑全 rc=0 无盘污·pool_dualrun ZERO-DRIFT streak36·"
       "compute_audit 旗=pool_starvation,supply_floor 池饿如实常设面·MSG-0825 补货请求在 origin 候fleet·update_daily 盘前 0 新行 cutoff 10-14·market_regime ORANGE 第 4 天 shadow·"
       "scorecard bm-a 心跳 stale 277min→bm-b stale-takeover derive per O-2100 s2.4·minute_feed +105 行/5 码·b_layer mask 5222 ok3517/excl1705·attrition CLEAN·docs 双面 REPORT/LIVE-2026-10-15 "
       "写本地不推=防陈旧回退）+饱和引擎活实测（rc=0 queue0 idle·非链绿代理）+水位 GREEN（red=false·lane healthy·next_pick=claimed moneyflow IC 候 parked 面板）+i2v 判定 51/53"
       "（46→51 本轮窗·comfy-out-480 33·KN_KN01 在烧·fails 台账零=无 fails 件·ETA ~15:45-16:00·完工判定+阀出=下轮首要）+astock 重建判定（8380 活·per_files 2596→2996/5219·~+20/min·"
       "ETA ~17:00-17:30·完工包候后窗）+S8 green_idle=false（RAM 7.8% 批窗·claimable_pool_lines=1·idle_rounds=0·双产线在飞无闲置罪）+孤儿面=1（19 py faces·i2v runner 睡眠编排器假阳性族常设注记） | "
       "实况三行：当前活=i2v 51/53 全功率在烧（ETA ~15:45-16:00 批完阀出）+astock refresh 行军 2996/5219+S7 LogonType 回归已抓已修；最近实物=Tools/register_loop_task.ps1+"
       "Tools/register_watchdog_task.ps1 S4U 配方落地（15:1x·随 C-r981 面）+双任务 S4U schtasks 实证+LIVE-2026-10-15/REPORT-2026-10-15+minute_feed +105 行；下个里程碑=i2v 53/53→"
       "阀出+KeepWarm 复 pin（~15:45-16:00·窗≤48h）+astock 完工包（~17:00-17:30） | 记账预算: 4/5（state+report+心跳+push 回执） | 产品积分: 2（LogonType 根因配方=能跑实物+S6 数据面 39 腿+docs 双面本地） | "
       "验证证据：schtasks 双任务登录状态行+配方回跑输出 logon=S4U via XML flip+smoke 49/49+results/_r981bmb_s6chain.log 尾 CHAIN_DONE nonzero=0+results/_r686bmb_d19_check.json+"
       "orders sha1 恒等命令面回执+results/_orphan_face_probe.bm-b.json+results/idle_trigger.bm-b.json+sat engine status rc=0+watermark_red.json red=false | 下轮指针：r982=i2v 53/53 完工判定→"
       "阀出（C:\\Fluxgroup\\MiniGame\\Tools\\Ollama\\keepwarm.pause 移除+KeepWarm 复 pin per r916 律）+完工包+C-r981 回执消费+astock 完工判定→数据 churn 完工包+D-19 再探+S7/S8（LogonType 点查=回归观察面）\n")
open(r"logs\iteration-loop\round_reports.md", "ab").write(row.encode("utf-8"))
print("round report row appended")
print("NOW =", NOW, "EPOCH =", EPOCH)
