# r1011 bm-b closeout (r1010 face clone, no 5x HANDOVER this round).
# Faces: D-19 advance (r1069 canonical tool) -> state -> heartbeat -> round report row -> CODELY pit row -> receipt.
import json, os, subprocess, sys, time
from datetime import datetime, timezone, timedelta

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)
CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")

def rf(p):
    with open(p, "r", encoding="utf-8") as f:
        return f.read()

def wf(p, s):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)

receipt = {"round": 1011, "ts": ts, "steps": {}}

# -- 1. D-19 advance (canonical tool, r1069 law) --
adv = subprocess.run([sys.executable, "scripts\\d19_watermark.py", "update", "--advance"],
                     capture_output=True, text=True, encoding="utf-8", errors="replace")
receipt["steps"]["d19_advance_rc"] = adv.returncode
receipt["steps"]["d19_advance_out"] = (adv.stdout or "").strip()[-500:]
if adv.returncode != 0:
    print("D19-ADVANCE-FAIL", adv.returncode, (adv.stdout or "")[-300:], (adv.stderr or "")[-300:])
    sys.exit(2)

state = json.loads(rf("state.json"))
receipt["steps"]["wm_after_advance"] = {"dec": state.get("last_decisions_sha", "")[:16],
                                        "ord": state.get("last_orders_sha", "")[:16]}

# -- 2. state.json update --
did = ("r1011: (a) FIRST ACTION per r1010 postscript: deferred r1010 payload DELIVERED via own-face surgery on fresh tip e326344c93 "
       "(delivery commit 466312108f on origin/main; two local commits 632a256486+d8bc4f4891 superseded, reflog recoverable): "
       "23 shared regen faces resolved origin-newer-wins (bm-c 21:22 / bm-a 20:39 vs mine 20:26), token_usage union honest-skip "
       "(both faces lack -bm-b key; keys = -bm-a/-bm-c/bm-a/bm-c/default), 18 own faces content-asserted 18/18 (r982 law), zero deletions, "
       "delivery four-way verified (fetch+rev-parse+ls-tree spot+behind/ahead 0/0), claw zero blocks; base raced once "
       "(f10ecc00e8->e326344c93 mid-flight, currency guard fired correctly, re-based); push clean first-try 21:5x. "
       "(b) S0.5: new CEO order O-20261018-2144-bm-c (idle-recurrence all-hands, CEO 21:3x) read + processed same-round: "
       "@bm-b sec2 P0 = CONTENT-LOOP v0.1 + voice lane OPENED (blueprint cph4/fleet/CONTENT-OS-LOOP-BLUEPRINT-v1.md full text loaded 21:5x, "
       "r1012 first code + QUEUE.md) + idle flip (idle_trigger --worked idle_rounds->0, agenda_starved=false, 22:02); "
       "receipt appended to order file sec4; group orders delta consumed (193095774d: 20:48 fleet automation expansion -- BigMoney seat "
       "W-wave loop formalization + backtest gates in-loop, construction plan <=10-25 mirror-registered; 20:54 nine-company inventory; "
       "21:11 nine-company plan order GROUP-AUTOMATION-PLAN-v1.md; 00:2x memory-governance four-piece verified live in L0) "
       "-- advance via canonical tool; DEC 4cfdd17c hold. "
       "(c) S3 checks: saturation engine alive (idle verdict), watermark red=false, smoke rc0 all-pass, "
       "compute_audit FLAG pool_starvation+supply_floor (honest starvation face, board empty, awaiting W273+ seat / secretary restock "
       "per O-2144 sec1.3). "
       "(d) S6 43 legs rc0 2.1min (driver _r1011bmb_s6chain.ps1, log results/_r1011bmb_s6_log.txt): REPORT-2026-10-18 + LIVE-2026-10-18 + "
       "LIVE-latest regenerated, lane-guard honest skips x6 (strategy_scorecard/market_clock_l3/t35_paper_export/daily_scorecard/build_status: "
       "bm-a origin faces fresh 3-4min, third-signal veto), pool_dualrun ZERO-DRIFT streak 51, orphan 7/0, attrition healed, "
       "token_meter appended, Sunday live.paper family x4 skip. "
       "(e) pits this window: orders_ack_append.py has NO arg validation (--help probe appended bogus ack to BOTH faces 104 -- sanitized "
       "same-window via _r1011bmb_ackfix.py then canonical append real ack, read-back verified 104/104); "
       "git write-tree hung once under python subprocess (120s timeout) while manual Start-Process retry was instant 0s "
       "(transient odb/file-lock face, honest record).")

verdict = ("GREEN: delivery+maintenance round r1011 -- r1010 deferred payload DELIVERED (466312108f on origin/main, four-way verified, "
           "behind=0/ahead=0) + O-20261018-2144 CEO idle-recurrence order processed same-round (receipt + blueprint loaded + idle flip) "
           "+ D-19 orders advance (193095774d; BigMoney seat plan <=10-25 mirror-registered) + smoke rc0 + S6 43 rc0 2.1min + "
           "lane-guard honest skips x6 + orphan 7/0 + ack dual-face canonical 104/104; "
           "leftovers = pool starvation honest face (board empty, W273+ seat=bm-c chain, secretary restock per O-2144 sec1.3) + "
           "CONTENT-LOOP v0.1 first code due r1012 (2-round window, P1 <=10-20) + voice lane first batch <=10-22")

nextp = ("r1012: 1) CONTENT-LOOP v0.1 first code on bm-b (O-2144 sec2.1; blueprint loaded; drama QUEUE.md + loop driver skeleton + S4U task; "
         "P1 <=10-20) 2) voice archetype lane bm-b first step (GPT-SoVITS/OpenVoice sourcing per W6; P1 <=10-22) "
         "3) BigMoney automation construction plan mirror-authoring contribution <=10-25 (20:48/21:11 group rows, @quant seat, bm-b=BM-repo mirror) "
         "4) O-0948 window close judgment 10-19 ~10:2x 5) D-19 fresh delta 6) W273+ seat watch")

state["clock_read"] = ts
state["ts"] = ts
state["updated"] = ts
state["updated_at"] = ts
state["last_seen"] = ts
state["last_round_at"] = ts
state["last_round_ts"] = ts
state["last_action_at"] = ts
state["last_decisions_read_at"] = ts
state["last_orders_read_at"] = ts
state["last_decisions_probe_at"] = ts
state["last_orders_probe_at"] = ts
state["round_no"] = 1011
state["round"] = 1011
state["round_no_label"] = "r1011"
state["now_active"] = "r1011 closing"
state["current_task"] = "r1011: closeout (r1010 delivery surgery + O-2144 processing + D-19 advance + S6 43 + state/heartbeat/round-report/push)"
state["task"] = state["current_task"]
state["current"] = verdict
state["did"] = did
state["last_action"] = ("r1011: r1010 deferred payload surgery-delivered (466312108f) + O-2144 CEO order processed (receipt+blueprint+idle flip) "
                        "+ D-19 orders advance + S6 43 rc0 + ack canonical append (+--help probe pollution sanitized same-window)")
state["next"] = nextp
state["next_milestone"] = ("CONTENT-LOOP v0.1 first code r1012 (P1 <=10-20, O-2144 2-round window) + O-0948 window close judgment 10-19 ~10:2x")
state["verdict"] = verdict
state["latest_artifact"] = ("delivery commit 466312108f (r1010 full payload on origin/main 21:5x) + S6 products 22:03: "
                            "docs/daily_report/REPORT-2026-10-18.md + docs/live_usage/LIVE-2026-10-18.md")
state["last_artifact"] = state["latest_artifact"]
state["note"] = ("r1011: O-2144 receipt landed in order file sec4; CONTENT-LOOP v0.1 + voice lane OPENED per CEO idle-recurrence order "
                 "(r1012 first code, 2-round window); BigMoney seat plan <=10-25 mirror-registered; "
                 "orders_ack_append.py no-validation pit (--help probe pollution) sanitized same-window, CODELY row appended")
state["orphan_face"] = 7
state["orphan_faces"] = 7
state["orphan_face_note"] = "r1011 chain probe (22:02): 7 py faces / 0 orphans"
state["sat_engine"] = {"status": "alive (r1011 S6 status rc0, idle verdict, queue_depth 0; supply floor honest starvation, awaiting W273+ seat)", "checked_at": ts}
state["decisions_delta_pending"] = False
state["orders_delta_pending"] = False
state["d19_probe_due"] = False
state["d19_probe_due_note"] = "r1011: orders delta 193095774d consumed + advanced via d19_watermark.py update --advance; DEC 4cfdd17c hold"
sync = state.get("sync", {})
sync["r1010_main_push"] = {
    "status": "PUSHED_VERIFIED (via r1011 surgery replay)",
    "pushed_sha": "466312108f975d2189169d65e6d8e8aba678e9e6",
    "consumed_at": ts,
    "behind_origin_main": 0,
    "note": ("r1010 payload (41 faces + postscript) delivered by r1011 own-face surgery replay on tip e326344c93; "
             "original local commits 632a256486+d8bc4f4891 superseded (reflog recoverable); 23 shared regen faces origin-newer-wins; "
             "delivery four-way verified 21:5x")
}
sync["r1011_main_push"] = {
    "status": "PENDING (this commit)",
    "pushed_sha": "pending",
    "consumed_at": "pending r1012",
    "behind_origin_main": 0,
    "note": ("r1011 payload = closeout faces (state/heartbeat/round-report + CODELY pit row) + O-2144 receipt + ack canonical append "
             "+ r1011 work files (surgery/tokenfix/ackfix/s6chain driver+log + push/wt evidence logs) + own regen/product faces "
             "(daily_report + live_usage docs + regime_state/token_usage/compute_audit/update_status/b_layer/dualrun/orphan/attrition "
             "+ d19 faces + collector bm-b status faces); shared daemon faces (machine-health/watermark_red/post_review family "
             "+ unsuffixed lhb/futures status) intentionally NOT added (r982 anti-regression policy); base = 466312108f origin tip fresh")
}
sync["behind_origin_main"] = 0
state["sync"] = sync
wf("state.json", json.dumps(state, indent=1, ensure_ascii=False) + "\n")
json.loads(rf("state.json"))
receipt["steps"]["state_written"] = True

# -- 3. heartbeat --
hb = json.loads(rf("fleet\\machines\\bm-b.json"))
epoch = int(time.time())
hb["machine_id"] = "bm-b"
hb["last_seen"] = ts
hb["ts"] = ts
hb["clock_read"] = ts
hb["task"] = state["current_task"]
hb["current_task"] = state["current_task"]
hb["did"] = ("r1011: r1010 deferred payload surgery-delivered (466312108f four-way verified) + O-2144 CEO idle-recurrence processed "
             "(receipt + blueprint loaded + idle flip 0) + D-19 orders advance + S6 43 rc0 2.1min + smoke rc0 + orphan 7/0 + ack 104/104")
hb["last_action"] = state["last_action"]
hb["last_action_at"] = ts
hb["next"] = nextp
hb["verdict"] = verdict
hb["latest_artifact"] = state["latest_artifact"]
hb["note"] = ("r1011: CONTENT-LOOP v0.1 + voice lane OPENED per O-2144; r1012 first code; pool famine honest face continues "
              "(board empty, awaiting W273+ seat / secretary restock).")
hb["round_no"] = 1011
hb["round"] = 1011
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["heartbeat_epoch_utc"] = epoch
assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be JSON int"
wf("fleet\\machines\\bm-b.json", json.dumps(hb, indent=1, ensure_ascii=False) + "\n")
chk = json.loads(rf("fleet\\machines\\bm-b.json"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch round-trip must be int"
assert "T" in chk["clock_read"], "clock_read must be T-separated"
receipt["steps"]["heartbeat_written"] = True
receipt["steps"]["epoch"] = epoch

# -- 4. round report row --
rp = "logs\\iteration-loop\\round_reports.md"
rtxt = rf(rp)
row = (f"{ts} | r1011 bm-b | dept:工程+舰队 | WM verdict: GREEN (red=false @22:02 py_watermark probe insufficient_history window n=1·合法周末面) | "
       "当前活=r1011 收口（r1010 递延载荷外科送达 + O-2144 CEO 闲置复发令承办 + S6 维护链）；"
       "最近实物=delivery commit 466312108f（r1010 全载荷 21:5x 上链·四验绿）+ docs/daily_report/REPORT-2026-10-18.md + docs/live_usage/LIVE-2026-10-18.md（22:03 再生）；"
       "下个里程碑（≤48h）=CONTENT-LOOP v0.1 漫剧线首码 @bm-b（O-2144 §2.1·P1 ≤10-20·r1012 开窗）+ O-0948 窗收口判定（10-19 ~10:2x） | "
       "did: " + did[:1200] + " | "
       "孤儿面=0（7 py faces/0 orphans @22:02 probe）；本地未达 origin commit 数=0（r1010 载荷 21:5x 四验送达实测；本轮收口推送 r1012 轮首复核）；"
       "O-0948 观察窗=零 died-pre-closeout 保持（收口判定 10-19 晨）；"
       "记账面=收口三件套+O-2144 回执+ack 追加（≤5 内）；"
       "验证: smoke rc0 all-pass + S6 43 legs rc0（链日志 results/_r1011bmb_s6_log.txt）+ dualrun ZERO-DRIFT streak 51 + "
       "d19 advance read-back OK + 送达四验（fetch+rev-parse+ls-tree+behind/ahead）+ ack 双面 104/104 回读断言 | "
       "下轮: r1012 = 1) CONTENT-LOOP v0.1 首码+QUEUE.md（O-2144 §2.1·P1 ≤10-20） 2) voice lane 寻源首步（P1 ≤10-22） "
       "3) BigMoney 建设案镜像贡献（≤10-25） 4) O-0948 收口判定（10-19 晨） 5) D-19 新鲜差集 6) push 送达核验\n")
if not rtxt.endswith("\n"):
    rtxt += "\n"
wf(rp, rtxt + row)
receipt["steps"]["round_report"] = "row-appended"

# -- 5. CODELY.md pit row (project memory, one item, fresh-read-append per r1006 multi-writer law) --
cp = "CODELY.md"
ct = rf(cp)
crow = ("- [2026-10-18 22:1x r1011 bm-b] **orders_ack_append.py 零参数校验坑+write-tree 子进程瞬时挂死坑**：①Tools/orders_ack_append.py 无 argv 校验无 --help——"
        "任何传入字符串（含 `--help` 探针）都会被当 target 真追加进 state+心跳双面 orders_ack（本窗 104 假 ack 实弹）——接口=仅位置 target 一个参数；"
        "探针一律先读脚本头部禁传试探参数；污染修复=python 双面剔除+正典重追加+回读断言（_r1011bmb_ackfix.py 范式）。"
        "②git write-tree 在 python subprocess 下偶发 120s+ 挂死而同窗 Start-Process 手跑 0 秒即成（疑 odb/AV 瞬时文件锁面）——"
        "重活 git 写操作挂死先换 Start-Process 通道重试勿判死锁。How to apply：ack 工具只传真实令文件名；python git 子进程挂死=换壳通道即刻重试。\n")
if not ct.endswith("\n"):
    ct += "\n"
wf(cp, ct + crow)
receipt["steps"]["codely_pit_row"] = "appended"

# -- 6. receipt --
wf("results\\_r1011bmb_closeout_receipt.json", json.dumps(receipt, indent=1, ensure_ascii=False) + "\n")
print("CLOSEOUT-OK", json.dumps(receipt["steps"], ensure_ascii=False))
