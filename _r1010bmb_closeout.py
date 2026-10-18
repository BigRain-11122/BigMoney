# r1010 bm-b closeout (ASCII-safe identifiers; CJK content strings ok, file utf-8)
# Faces: D-19 advance (r1069 law tool) -> state -> heartbeat -> round report row -> HANDOVER 5x stamp.
import json, subprocess, sys, time
from datetime import datetime, timezone, timedelta

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
CST = timezone(timedelta(hours=8))
now = datetime.now(CST)
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")

def rf(p):
    with open(p, "r", encoding="utf-8") as f:
        return f.read()

def wf(p, s):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)

receipt = {"round": 1010, "ts": ts, "steps": {}}

# -- 1. D-19 advance (canonical tool, r1069 law: never hand-write watermark keys) --
adv = subprocess.run([sys.executable, "scripts\\d19_watermark.py", "update", "--advance"],
                     cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
receipt["steps"]["d19_advance_rc"] = adv.returncode
receipt["steps"]["d19_advance_out"] = (adv.stdout or "").strip()[-600:]
if adv.returncode != 0:
    print("D19-ADVANCE-FAIL", adv.returncode, (adv.stdout or "")[-400:], (adv.stderr or "")[-400:])
    sys.exit(2)

st_probe = json.loads(rf("results\\_r686bmb_d19_check.json"))
state = json.loads(rf("state.json"))
rb_ord = state.get("last_orders_sha", "")
rb_dec = state.get("last_decisions_sha", "")
receipt["steps"]["wm_after_advance"] = {"dec": rb_dec, "ord": rb_ord}

# -- 2. state.json update --
did = ("r1010: (a) S0 sync: HEAD==origin/main b18fc611 at 20:13 (r1009 closeout push verified landed, PENDING marker healed); "
       "round-start dirty 6 faces all daemon/regen known faces (no foreign half-work). "
       "(b) S0.5 D-19: multi-delta consumed tonight (1b6ccf2a->a021c305->1730ad9a->240a4e2d->final advance), "
       "all delta rows = BigStream/bm-d-hardware lane (V5.8-V5.9 MV feedback chain, methodology five-piece suite, daily evolution class, "
       "production-line tech refresh, compliance entry-point, bm-d purchase law, content-line OS loop order, creation high-voltage line, "
       "market-watch standing order, character-face/voice library order) -- ZERO BigMoney dispatch across every delta; "
       "DEC 4cfdd17c hold throughout; all advances via d19_watermark.py update --advance, read-back OK, heartbeat mirrors synced 3. "
       "orders_ack dual-face scan CLEAN 103/103 zero face divergence zero stale. "
       "(c) S3 checks: saturation engine alive (idle verdict, queue_depth 0, honest starvation), watermark red=false "
       "(next_pick=claimed moneyflow IC reference batch awaiting panel completion), smoke 49/49 PASS, "
       "post_review today 225 YES / 25 WAIT / zero X. "
       "(d) S6 43 legs rc0 3.9min (driver results/_r1010bmb_s6chain.ps1, log results/_r1010bmb_s6_log.txt): "
       "4 stale-takeover derives by bm-b (strategy_scorecard + t35_paper_export + daily_scorecard + dashboard_status per O-2100 s2.4 STALE_MIN law), "
       "REPORT-2026-10-18.md/.json + LIVE-2026-10-18.md/.json regenerated, market_clock CALL-2026-10-16 ORANGE_COOL, "
       "regime_gate_dualarm 2026-09-30 BEAR face, pool_dualrun ZERO-DRIFT streak 51, orphan 7/0, attrition healed-clean, "
       "idle --worked (idle_rounds 3->0), token_meter snapshot appended. Sunday: live.paper family x4 honest skip. "
       "(e) New @bm-b dispatches read + registered as machine-level next-window work (both multi-window builds, need budget window, "
       "not 60-min auto-claim items): 20:12 content-line OS loop order (P1 CONTENT-LOOP v0.1 for drama line on bm-b, deadline <=10-20) + "
       "20:17 character-face/voice library order (bm-b = voice archetype lane, P1 first batch <=10-22). "
       "(f) MSG-20261018-191x-bmc-w272-seat processed to inbox/processed (W272 seat owner=bm-c, informational; "
       "bm-b engine lane awaits W273+ seat publish). "
       "(g) 5x HANDOVER stamp: r1010 due -- r995/r1000/r1005 three stamps OVERDUE-DISCLOSED (push-saga windows r1000-r1005 consumed), "
       "this entry covers r991-r1010 window.")

verdict = ("GREEN: maintenance round r1010 -- S0 FF sync (r1009 push verified) + D-19 multi-advance (zero BigMoney dispatch in all deltas) "
           "+ smoke 49/49 + S6 43 rc0 (4 stale-takeover regen faces + REPORT/LIVE 2026-10-18 products + CALL/DUALARM regen) "
           "+ ack scan CLEAN 103/103 + post_review zero X + orphan 7/0 + idle --worked (3->0); "
           "two new @bm-b content-lane dispatches registered (CONTENT-LOOP v0.1 P1 <=10-20 drama line; voice-library lane P1 <=10-22); "
           "5x HANDOVER stamp landed with 3-stamp OVERDUE-DISCLOSED; "
           "leftovers = pool starvation honest face (local registry 9/9 retired|done zero open, board empty, W272 seat=bm-c, "
           "bm-b engine lane awaits W273+ seat / secretary restock) + O-0948 window zero died-pre-closeout (close judgment 10-19 ~10:2x)")

nextp = ("r1011: 1) O-0948 24h observation window close judgment (10-19 ~10:2x morning window, died-pre-closeout holding zero) "
         "2) CONTENT-LOOP v0.1 implementation on bm-b P1 <=10-20 (20:12 CEO content-line OS order; blueprint cph4/fleet/CONTENT-OS-LOOP-BLUEPRINT-v1.md; "
         "drama line <<Yi Lu Chang Hong>> continuation + five-piece suite instantiation; needs dedicated budget window) "
         "3) voice archetype library bm-b lane P1 <=10-22 (20:17 CEO order; sourcing GPT-SoVITS/OpenVoice per W6 coordination) "
         "4) D-19 fresh delta per round 5) W273+ seat watch (bm-b engine lane refill) "
         "6) POOL-0019 allin1 structure anchor batch candidate (module not installed on bm-b; install+run at budget window; consumer=double-axis editing anchor)")

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
state["round_no"] = 1010
state["round"] = 1010
state["round_no_label"] = "r1010"
state["now_active"] = "r1010 closing"
state["current_task"] = "r1010: closeout (D-19 multi-advance + S6 43 + new dispatch registration + 5x HANDOVER + state/heartbeat/round-report/push)"
state["task"] = state["current_task"]
state["current"] = verdict
state["did"] = did
state["last_action"] = ("r1010: S0 FF sync + D-19 multi-advance (zero BigMoney dispatch) + S6 43 rc0 + stale-takeover x4 + "
                        "content-lane dispatches registered + W272 seat MSG processed + 5x HANDOVER stamp")
state["next"] = nextp
state["next_milestone"] = ("O-0948 window close judgment 10-19 ~10:2x + CONTENT-LOOP v0.1 on bm-b <=10-20 (48h milestone = drama content loop v0.1 live)")
state["verdict"] = verdict
state["latest_artifact"] = ("S6 product faces 2026-10-18: docs/daily_report/REPORT-2026-10-18.md + docs/live_usage/LIVE-2026-10-18.md "
                            "+ 4 stale-takeover regen faces (scorecard/paper_export/daily_scorecard/dashboard) 20:2x")
state["last_artifact"] = state["latest_artifact"]
state["note"] = ("r1010: HANDOVER 5x stamp r995/r1000/r1005 OVERDUE-DISCLOSED (push-saga windows consumed); "
                 "content-lane dispatches (CONTENT-LOOP/voice-library) registered to next-window work queue -- multi-window builds, "
                 "not 60-min auto-claim items; local self-drive registry 9/9 retired|done (pool famine honest face, awaiting secretary restock)")
state["orphan_face"] = 7
state["orphan_faces"] = 7
state["orphan_face_note"] = "r1010 chain probe (20:19): 7 py faces / 0 orphans"
state["sat_engine"] = {"status": "alive (r1010 S6 status rc0, idle verdict, queue_depth 0; supply floor honest starvation, W272 seat=bm-c, bm-b lane awaits W273+)", "checked_at": ts}
state["decisions_delta_pending"] = False
state["orders_delta_pending"] = False
state["d19_probe_due"] = False
state["d19_probe_due_note"] = ("r1010: multi-delta consumed + advanced via d19_watermark.py update --advance (read-back OK, mirrors synced 3); next probe per standing cadence")
state["heartbeat_epoch_utc_face"] = "bm-b.json updated this round (epoch int verified)"
sync = state.get("sync", {})
sync["r1010_main_push"] = {
    "status": "PENDING (this commit)",
    "pushed_sha": "pending",
    "consumed_at": "pending r1011",
    "behind_origin_main": 0,
    "note": ("r1010 payload = closeout faces (state/heartbeat/round-report + HANDOVER 5x stamp) + r1010 work files "
             "(s6chain driver + log + closeout script + receipt) + own regen/product faces (daily_report + live_usage docs + "
             "scorecard/paper_export/daily_scorecard/dashboard stale-takeover + market_clock/dualarm regen + token_usage + "
             "d19 probe + orphan probe); shared non-suffixed faces (machine-health/watermark_red/post_review family) intentionally NOT added "
             "(r982 anti-regression policy); base = b18fc611 origin tip fresh at S0 FF")
}
sync["behind_origin_main"] = 0
state["sync"] = sync
wf("state.json", json.dumps(state, indent=1, ensure_ascii=False) + "\n")
json.loads(rf("state.json"))
receipt["steps"]["state_written"] = True

# -- 3. heartbeat fleet/machines/bm-b.json --
hb = json.loads(rf("fleet\\machines\\bm-b.json"))
epoch = int(time.time())
hb["machine_id"] = "bm-b"
hb["last_seen"] = ts
hb["ts"] = ts
hb["clock_read"] = ts
hb["task"] = state["current_task"]
hb["current_task"] = state["current_task"]
hb["did"] = ("r1010: S0 FF sync + D-19 multi-advance (zero BigMoney dispatch) + smoke 49/49 + S6 43 rc0 "
             "(4 stale-takeover derives + REPORT/LIVE 10-18 + CALL/DUALARM regen) + content-lane dispatches registered "
             "+ W272 seat MSG processed + idle --worked (3->0)")
hb["last_action"] = state["last_action"]
hb["last_action_at"] = ts
hb["next"] = nextp
hb["verdict"] = verdict
hb["latest_artifact"] = state["latest_artifact"]
hb["note"] = ("r1010: HANDOVER 5x stamp with 3-stamp OVERDUE-DISCLOSED; CONTENT-LOOP v0.1 P1 <=10-20 + voice lane P1 <=10-22 "
              "registered as next-window work; pool famine honest face (local registry zero open).")
hb["round_no"] = 1010
hb["round"] = 1010
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
row = (f"{ts} | r1010 bm-b | dept:工程+舰队 | WM verdict: GREEN (red=false @20:19 py_watermark probe, next_pick=claimed moneyflow awaiting panel) | "
       "当前活=r1010 收口（D-19 多段推进 + S6 维护链 + 新派工登记 + 5x HANDOVER）；"
       "最近实物=docs/daily_report/REPORT-2026-10-18.md + docs/live_usage/LIVE-2026-10-18.md + 4 stale-takeover regen faces（scorecard/paper_export/daily_scorecard/dashboard 20:2x）；"
       "下个里程碑（≤48h）=CONTENT-LOOP v0.1 漫剧线实装 @bm-b（20:12 CEO 令 P1 ≤10-20）+ O-0948 窗收口判定（10-19 ~10:2x） | "
       "did: " + did[:1200] + " | "
       "孤儿面=0（7 py faces/0 orphans @20:19 probe）；本地未达 origin commit 数=0（S0 FF 后 HEAD==origin 实测；本轮收口推送 r1011 轮首复核）；"
       "O-0948 观察窗=零 died-pre-closeout 保持（20:22 点火零 TIMEOUT 标记·收口判定 10-19 晨）；"
       "记账面=收口三件套+HANDOVER 补截（≤5 内）；"
       "验证: smoke 49/49 rc0 + S6 43 legs rc0（链日志 results/_r1010bmb_s6_log.txt）+ dualun ZERO-DRIFT streak 51 + "
       "d19 multi-advance read-back OK（mirrors synced 3）+ ack scan CLEAN 103/103 + 双爪恒等 + loop pin=:32 错峰正 + watchdog 20:26 在役 | "
       "下轮: r1011 = 1) O-0948 收口判定（10-19 晨） 2) CONTENT-LOOP v0.1 实装开窗（P1 ≤10-20） 3) 声音库车道 sourcing（P1 ≤10-22） "
       "4) D-19 新鲜差集 5) W273+ 席位守望（bm-b 引擎道回填） 6) push 送达核验\n")
if not rtxt.endswith("\n"):
    rtxt += "\n"
wf(rp, rtxt + row)
receipt["steps"]["round_report"] = "row-appended"

# -- 5. HANDOVER 5x stamp (r1010 due; r995/r1000/r1005 OVERDUE-DISCLOSED) --
hp = "research\\HANDOVER.md"
htxt = rf(hp)
hrow = ("> bm-b round 1010 五倍数核对（2026-10-18 20:3x 核对；增量窗口覆盖 r991-r1010 二十轮·**5x 截 r995/r1000/r1005 三截未落=OVERDUE-DISCLOSED**"
        "〔r1000-r1005 push-saga 连窗消耗：morning promisor 挂面+r1002 死于 25min 墙钟 pre-push+r1005 重放窗终达〕·零回改零伪造·"
        "逐轮权威=logs/iteration-loop/round_reports.md 全行在册+state.json sync 族）：增量窗主线=**推送 saga 判例族+W268 席位让渡+词锚批收口+记忆治理本机腿+O-0948 根治窗**——"
        "①推送链（r997-r1005）：r997 estate absorb d452d780→r999 rebase sequencer deadloop 首例 bypass（temp-index 树手术·b15d5e69 落）→"
        "r1000 爪正拦 stale-base revert 后 r1032 律重放（8b93a702）→r1001 非首推拒后清重放（a8568c55）→r1002 死于 v1 25min 墙钟（O-0948 census 首例）→"
        "r1004 锚 423c33ba82+r1005 9877424b4f 终达+remote 改名 BigMoney.git 接线；"
        "②r1006 D-02 bm-b 腿（6 tick faces 出库·stash-bridge 竞态家族根除·HQ-FEEDBACK F-20261018-01 watermark_red 残留候集团）+"
        "r1007 P2 三曲词锚批（斗牛/黑色幽默校准面+lyric_calibration argv 过滤器·LEDGER union heal·b983a3010）+"
        "r1008 push-saga 判例族（GHOST-REFUSAL deadloop+per-machine UNION 律+c80a274bf5 落链·CODELY 坑律入册）+"
        "r1009 O-1810 双面回执+CODELY 热冷整编（9,968→9,628B）+D-19 双推进+S6 43 rc0；"
        "③O-0948 根治窗（r1004 起全员零 died-pre-closeout·收口判定 10-19 晨）；"
        "④r1010 本窗=S0 FF 同步+D-19 多段推进（全段零 BigMoney 派工）+S6 43 rc0（4 stale-takeover regen 面+REPORT/LIVE 10-18 产品）+"
        "新派工登记（20:12 内容线 OS 循环化 CONTENT-LOOP v0.1 P1 ≤10-20 @bm-b·20:17 角色面孔+声音库 bm-b=声音车道 P1 ≤10-22）+"
        "W272 席 MSG 归档（owner=bm-c·本机引擎道候 W273+）。维护面全窗：smoke 49/49 链·S6 43 rc0 链·attrition CLEAN 链·"
        "双爪恒等链·loop pin=:32 链·idle --worked 链·孤儿面 7/0 合法链。"
        "产物清单漂移（增量代表面非全列）：_r99{7,9}bmb_*+_r10{00..10}bmb_* 工件族+docs/daily_report/REPORT-2026-10-1{7,8}.md+"
        "docs/live_usage/LIVE-2026-10-1{7,8}.md+cph4 词锚产物（anchors/ 斗牛/黑色幽默-calibrated 双面+lyric_calibration.py argv 面）+"
        "CODELY.md+research/memory-archive/202610.md 热冷整编对+results/_r1009bmb_codely_hotcold_receipt.json。"
        "指针：**CONTENT-LOOP v0.1 实装 @bm-b P1 ≤10-20（20:12 CEO 内容线循环化令·蓝图 cph4/fleet/CONTENT-OS-LOOP-BLUEPRINT-v1.md）+"
        "声音库 bm-b 车道 P1 ≤10-22（20:17 CEO 令）+O-0948 收口判定 10-19 晨+W273+ 席位守望**；下一 5x=bm-b r1015。[via bm-b r1010]\n")
if not htxt.endswith("\n"):
    htxt += "\n"
wf(hp, htxt + hrow)
receipt["steps"]["handover_5x"] = "stamp-appended"

# -- 6. receipt --
wf("results\\_r1010bmb_closeout_receipt.json", json.dumps(receipt, indent=1, ensure_ascii=False) + "\n")
print("CLOSEOUT-OK", json.dumps(receipt["steps"], ensure_ascii=False))
