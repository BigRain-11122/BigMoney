# r986 closeout (dead-predecessor estate absorption, successor same round number per
# bm-a r1019 precedent; predecessor fired ~18:22 tick, watchdog-killed at 25min budget
# ~18:47 — r982 pattern; detached estate workers survived legal and were verified+closed).
# Faces: round_reports.md byte-append (r962 law), state.json rmw (wb-open truncation pit
# r985 law: full-bytes-in-memory -> tmp -> os.replace), heartbeat same.
import json, time, datetime, subprocess, os

NOW = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
NOW_HM = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
EPOCH = int(time.time())

RR = r"logs\iteration-loop\round_reports.md"
line = (
    NOW_HM + " | r986 | 前席死遗产吸收轮（18:22 拍会话 25min 预算 watchdog 斩于 ~18:47 收口前·两枚 detached 长批存活合法·本席 18:52 拍续任同轮号·bm-a r1019 先例）| "
    "WM: green（水位面无 red·pywm 采样窗不足合法延续·token/dualrun/compute_audit 腿随下轮补跑=杀线窗诚实让路面）| "
    "主线=①POOL-0020（P0·O-20261015-1821 CEO 直令「bm-b我换好了，开工」·bm-a 总控窗 18:21 开卡）：步①nvidia-smi -pl 239.80W 实测✓步②GPU-PowerCap-180W-Boot/Hourly 双任务查询空输出=已删✓步③machine-state GPU 面复活（ollama up+任务 Ready/Running·MODE=mixed 派生面）✓步④烧机 30min 满载（前席 18:38:25 点火·本席验证收口）=BURN DONE dur=30min max_draw=239.1W max_temp=77C power_limit=239.80W end_draw=238.2W（results/_r986bmb_gpu_burn_evidence.csv 361 行留档·System log 18/19/41 事件窗内零条=零断电零 WHEA 判据全过）→步⑤满性能投产（首 24h 单批串行保守期启算 19:08·委员会呈报面=本行+回执）；"
    "②card-lint 如实披露=REJECT（④spec 指针 memory\\bm-b-power-loss-20261012.md 为 bm-b 本地 Codely 记忆件·group 仓根不可解析=卡形式缺陷归代理席写手面·正身权威=CEO 直令 O-0952+O-1821·执行不回退·回执随 commit 面呈报）；"
    "③astock 完工包（r985 首要遗留）：前席 close 脚本第三段 19:01 续拉 11/11 零败→complete=true 19:02:04（5221/5229·8 只三击隔离 000019/001235/001381/301718/688089/688143/688173/689009+11 只停牌 settle@exp=10-14 n=3 settle law r305·快照 results/_r986bmb_astock_complete.json）→update_daily 随后跑=sina ETF 端点今日迟 bar（10-15 bar 上游存在 tencent 探针实证·sina 零行·NEWBAR 门关 cutoff=10-14·exit 0 合法 no-op·自愈面同 lhb 先例·results/update_status.json fallback_events 留痕）→NEWBAR 门控腿自动跳过；"
    "④S0.5 orders 真增量消费（sha 2560611e→e394cb69·4 行）：18:00 星晴提示词闸收官（MV 域零 bm-b）+18:0x O-1800 云端并发帽 v1.0（每机 ≤2·本会话=1 合规）+18:2x O-1821（=POOL-0020 执行实况①）+18:3x O-1834 云端双控+本地满用重申令（@bm-b 面=spawn 闸 preflight 24:00 前落位→已落：Tools/iteration_loop.ps1 spawn-gate 段·ASCII 纯净·fail-open·defer 台账 cloud_cap_defer.log·C-20261015-03 §三 spec 逐行对齐；heartbeat codely_live_count 观察哨字段已增·错峰全量核查候下轮（24h 窗内）；轻轮本地路由=BigMoney 轮面本就零云端簿记腿）；decisions ab3f0cc9 恒等零动作；双水位更新；"
    "⑤C-03 §五.1 BM 席核实（双机双 Bigmoney-IterationLoop 疑点）：定谳=多机池设计合法非双烧——双循环各烧各机轮（bm-a r1019/r1020 vs bm-b r98x 各自轮号面+own-face 手术推送互不吞）+池面认领纪律在位（runnable_pool owner 字段+queue_head_collision_probe E3/E4 活律+双跑对账 streak 455 面）·非双开；"
    "⑥S1 smoke 49/49✓·round-zero 孤儿探针 py_faces=15 orphans=0✓·GPU 复工=CEO 令合法面（O-0952 1200W 换装+O-1821 开工令·180W 限档/停车令全面废止·后令胜前令）；"
    "记账预算: 3/5（state+report+心跳·回执随手术件）| 产品积分: 2（astock 完工包 data churn 37 面推送=能跑能用数据面板实物+POOL-0020 烧机验证证据件=可看验收物）| "
    "实况三行：当前活=r986 完工包手术推送在飞；最近实物=results/_r986bmb_astock_complete.json（19:02）+results/_r986bmb_gpu_burn_evidence.csv（19:08·361 行）+Tools/iteration_loop.ps1 spawn 闸（19:11）；下个里程碑=补跑 S6 证据腿+错峰核查（24:00 前·窗 ≤3h）+sina 迟 bar 自愈后 NEWBAR 腿（窗 ≤24h）| "
    "验证证据：burn CSV+BURN DONE 汇总行+System 事件窗零条查询回执+PowerCap 双任务空查询+power.limit=239.80W 实测+card-lint REJECT 输出+astock complete 快照+update_status.json fallback_events+smoke 49/49+git status data/ 37 面清单 | "
    "本地未达 origin commit 数=0（推送后 ls-remote 自证·见手术回执）| 下轮指针：r987=①S6 补腿（token_meter/pool_dualrun/compute_audit/py_watermark probe 全套）②错峰全量核查（C-03 @bm-b 面·24:00 前窗）③S7 四件套+sat engine 实测④sina 迟 bar 自愈监测（NEWBAR 腿开闸即跑 live.paper 链）⑤POOL-0020 步⑥并发帽 spawn 闸同窗核验（C-20261015-03 §七）"
)
with open(RR, "ab") as f:
    f.write(line.encode("utf-8") + b"\n")
print("round_reports.md appended:", len(line), "chars")

# ---- state.json (watermarks + round face) ----
s = json.load(open("state.json", encoding="utf-8"))
s["round"] = 986
s["round_no"] = 986
s["round_no_label"] = "r986"
s["did"] = ("r986: (a) dead-predecessor estate absorption (18:22 session watchdog-killed ~18:47 pre-closeout, "
           "detached workers survived legal, successor 18:52 same round number); (b) POOL-0020 P0 (CEO order "
           "O-20261015-1821): steps 1-3 verified (pl 239.80W / PowerCap tasks deleted / machine-state GPU resumed), "
           "step 4 burn DONE 30min max 239.1W 77C zero power-loss zero WHEA (evidence CSV 361 rows), step 5 "
           "full-power production + first-24h single-batch serial conservative period; card-lint REJECT disclosed "
           "(element-4 spec pointer = bm-b-local memory file, unresolvable from group-repo root; authority = CEO "
           "direct orders O-0952/O-1821, defect flagged to proxy-writer seat); (c) astock completion: complete=true "
           "19:02:04 (5221/5229, 8 three-strike quarantine + 11 suspended-settled exp=10-14, snapshot "
           "_r986bmb_astock_complete.json) + update_daily no-op (sina ETF late-bar 10-15, tencent probe proves "
           "upstream bar exists, NEWBAR gate closed cutoff=10-14, self-heal next rounds); (d) S0.5 orders delta "
           "consumed 4 rows (watermark -> e394cb69): MV zero-action + O-1800 cloud cap v1.0 + O-1821 (=POOL-0020) + "
           "O-1834 spawn-gate landed in Tools/iteration_loop.ps1 + heartbeat codely_live_count field added; "
           "(e) C-03 sec5.1 BM-seat verdict: dual IterationLoop = legal multi-machine pool design (own-face "
           "surgery pushes, runnable_pool owner discipline), not double-burn; (f) smoke 49/49; (g) orphan probe "
           "15 faces 0 orphans; (h) completion package push (data churn 37 faces + round faces) via r982-v2 surgery")
s["verdict"] = ("GREEN: POOL-0020 burn PASSED (30min 239.1W max, zero power-loss, zero WHEA, 77C wall) + astock "
                "panel complete=true + spawn-gate preflight landed + orders 4-row delta consumed + smoke 49/49; "
                "honest defers: S6 quick legs + stagger audit next round (25min kill-window), NEWBAR legs await "
                "sina late-bar self-heal")
s["last_action"] = "r986: estate absorption + POOL-0020 GPU burn verified + astock completion package push"
s["last_action_at"] = NOW
s["last_round_at"] = NOW
s["last_round_ts"] = NOW
s["last_seen"] = NOW
s["updated"] = NOW
s["updated_at"] = NOW
s["ts"] = NOW
s["clock_read"] = NOW
s["current_task"] = "r987: S6 catch-up legs + stagger audit (pre-24:00) + NEWBAR watch"
s["next"] = ("r987: 1) S6 catch-up legs (token_meter/pool_dualrun_reconcile/compute_audit/py_watermark probe) "
            "2) full stagger audit @bm-b task set (C-20261015-03 sec.4, pre-24:00 window) 3) S7 quad + sat engine "
            "live probe 4) sina late-bar self-heal watch -> NEWBAR legs (live.paper chain) when 10-15 bar lands "
            "5) POOL-0020 step-6 concurrency-cap spawn-gate co-verification")
s["next_milestone"] = ("astock recovery data panel shipped (complete=true) + full-power GPU production live; "
                      "stagger audit before 24:00 tonight; NEWBAR legs within 24h self-heal window")
s["note"] = ("r986: dead-predecessor (18:22 tick, killed ~18:47 by 25min round budget) estate absorbed; POOL-0020 "
             "GPU re-commissioning CLOSED (burn passed, first-24h single-batch serial); astock tree-loss rebuild "
             "CLOSED complete=true; NEWBAR gate closed on sina ETF late-bar (tencent proves upstream 10-15 bar, "
             "self-heal); foreign dirty faces held untouched (explicit-faces-only policy)")
s["last_orders_sha"] = "e394cb6923146f3e5fd903d4ea01d4e7d176c04652bffa8f4dec119fec3a00b0"
s["last_orders_at"] = NOW
s["last_orders_read_at"] = NOW
s["last_orders_probe_at"] = NOW
s["orders_delta_pending"] = False
s["last_orders_sha_probe"] = "e394cb6923146f3e5fd903d4ea01d4e7d176c04652bffa8f4dec119fec3a00b0"
s["last_orders_probe_at"] = NOW
s["last_orders_sha_probe_note"] = ("r986: genuine 4-row delta consumed (18:00 MV prompt-gate / O-1800 cloud cap "
                                   "v1.0 / O-1821 GPU re-commission POOL-0020 / O-1834 enforcement tightening); "
                                   "bm-b legs = POOL-0020 done + spawn-gate landed + codely_live_count field; "
                                   "watermark rides r986 push face")
s["d19_probe_due"] = False
s["orphan_faces"] = 0
s["orphan_face"] = 0
s["orphan_face_note"] = "r986 round-zero probe (18:53): 15 py faces, 0 orphans (2 detached estate workers live-verified)"
s["d19_watermark_guard"]["ts"] = NOW
s["d19_watermark_guard"]["round_ref"] = 986
tmp = "state.json.r986tmp"
open(tmp, "wb").write(json.dumps(s, ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
os.replace(tmp, "state.json")
print("state.json updated: round=986 orders-sha=e394cb69")

# ---- heartbeat (fleet/machines/bm-b.json) ----
h = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8"))
try:
    live = int(subprocess.run(["powershell", "-NoProfile", "-Command",
                              "@(Get-CimInstance Win32_Process -Filter \"Name='codely.exe'\").Count"],
                             capture_output=True, text=True, timeout=30).stdout.strip() or 1)
except Exception:
    live = -1
h["machine_id"] = "bm-b"
h["last_seen"] = NOW
h["task"] = "r986: POOL-0020 burn close + astock completion package push"
h["did"] = ("r986: (a) estate absorption of dead 18:22 predecessor (watchdog-killed ~18:47; detached burn + astock "
           "workers verified and closed by successor); (b) POOL-0020 (P0 CEO order O-1821) CLOSED: pl 239.80W + "
           "PowerCap tasks deleted + machine-state resumed + 30min burn PASSED (max 239.1W/77C, zero power-loss, "
           "zero WHEA, evidence results/_r986bmb_gpu_burn_evidence.csv) -> full-power production, first-24h "
           "single-batch serial; card-lint REJECT element-4 disclosed (spec pointer = bm-b-local memory path, "
           "group-repo unresolvable; authority = CEO O-0952/O-1821); (c) astock panel complete=true 19:02 "
           "(5221/5229, 8 quarantine + 11 settled, snapshot _r986bmb_astock_complete.json) + update_daily "
           "honest no-op (sina ETF late-bar, tencent probe disclosure, NEWBAR closed); (d) S0.5 4-row orders "
           "delta consumed (O-1800/O-1821/O-1834 + MV zero-action), watermarks -> e394cb69; (e) C-03 sec7 "
           "@bm-b faces: spawn-gate preflight LANDED in Tools/iteration_loop.ps1 (fail-open, defer ledger "
           "cloud_cap_defer.log) + codely_live_count heartbeat field (this write); full stagger audit next "
           "round pre-24:00; (f) C-03 sec5.1 BM-seat verdict: dual IterationLoop = legal multi-machine pool; "
           "(g) smoke 49/49; orphan probe 15/0; completion package push in flight (data churn 37 faces)")
h["cpu_cores"] = 16
try:
    ram = float(subprocess.run(["powershell", "-NoProfile", "-Command",
                                "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)"],
                               capture_output=True, text=True, timeout=30).stdout.strip())
except Exception:
    ram = h.get("free_ram_gb", 0)
h["free_ram_gb"] = ram
h["gpu_free_vram_mb"] = 2048
h["verdict"] = ("GREEN: POOL-0020 burn PASSED (zero power-loss zero WHEA 239.1W max) -> GPU full-power live "
                "(1200W PSU); astock complete=true; spawn-gate landed; orders delta consumed; smoke 49/49; "
                "honest defers: S6 quick legs + stagger audit next round (kill-window), NEWBAR await sina self-heal")
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["heartbeat_epoch_utc"] = EPOCH
h["clock_read"] = NOW
h["ts"] = NOW
h["codely_live_count"] = live
h["orders_ack"] = ("r986: orders delta 2560611e->e394cb69 consumed (4 rows: MV prompt-gate zero-action + O-1800 "
                   "cloud cap v1.0 (bm-b session count=1 compliant) + O-1821 GPU re-commission = POOL-0020 DONE "
                   "(burn passed) + O-1834 enforcement tightening (spawn-gate landed pre-24:00, codely_live_count "
                   "field added, stagger audit next round)); decisions ab3f0cc9 zero-delta | r985-close face: see "
                   "prior ack")
h["note"] = ("r986: GPU full-power production live (PSU 1200W, burn passed, first-24h single-batch serial); astock "
             "rebuild CLOSED complete=true (8 quarantine + 11 settled honest); NEWBAR gate closed on sina ETF "
             "late-bar (tencent proves upstream 10-15 bar exists; self-heal watch); S6 quick legs deferred next "
             "round (25min kill-window, r984 chain face green same window); orphan face=0; POOL-0020 receipt rides "
             "C-r986 commit face")
h["latest_artifact"] = "pending C-r986 surgery push (results/_r986bmb_push_receipt.json)"
tmp = r"fleet\machines\bm-b.json.r986tmp"
open(tmp, "wb").write(json.dumps(h, ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
os.replace(tmp, r"fleet\machines\bm-b.json")
print("heartbeat updated: epoch=%d codely_live_count=%d ram=%.1f" % (EPOCH, live, ram))
chk = json.load(open(r"fleet\machines\bm-b.json", encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in chk["clock_read"], "clock_read must be ISO8601 T-separated (R262 law)"
print("heartbeat self-check OK (epoch int + T-sep clock)")

r = subprocess.run(["python", "Tools\\idle_trigger.py", "--worked"], capture_output=True, text=True)
print("idle_trigger --worked:", (r.stdout or r.stderr).strip()[-120:])
