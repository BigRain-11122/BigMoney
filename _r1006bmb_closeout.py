# r1006 bm-b closeout (ASCII-safe identifiers; CJK content strings ok, file utf-8)
# Faces: D-19 advance (r1069 law tool) -> state -> heartbeat -> backlog row14 -> HQ-FEEDBACK row -> round report row.
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

receipt = {"round": 1006, "ts": ts, "steps": {}}

# -- 1. D-19 advance (canonical tool, r1069 law: never hand-write watermark keys) --
adv = subprocess.run([sys.executable, "scripts\\d19_watermark.py", "update", "--advance"],
                     cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
receipt["steps"]["d19_advance_rc"] = adv.returncode
receipt["steps"]["d19_advance_out"] = (adv.stdout or "").strip()[-600:]
if adv.returncode != 0:
    print("D19-ADVANCE-FAIL", adv.returncode, (adv.stdout or "")[-400:], (adv.stderr or "")[-400:])
    sys.exit(2)

# read-back equality assert
st_probe = json.loads(rf("results\\_r686bmb_d19_check.json"))
state = json.loads(rf("state.json"))
dec_now = st_probe.get("decisions_sha", "")
ord_now = st_probe.get("orders_sha", "")
rb_dec = state.get("last_decisions_sha", "")
rb_ord = state.get("last_orders_sha", "")
ok_rb = (dec_now == rb_dec and ord_now == rb_ord)
receipt["steps"]["d19_readback_equal"] = ok_rb
if not ok_rb:
    print("D19-READBACK-MISMATCH", dec_now, rb_dec, ord_now, rb_ord)
    sys.exit(3)

# -- 2. state.json update --
did = ("r1006: (a) D-20261015-02 bm-b leg closed: 6 own daemon live-tick faces OUT of repo "
       "(autofill_state.bm-b / idle_trigger.bm-b / idle_trigger_state.bm-b / satengine face+state+history_bm-b; "
       "git rm --cached, disk live-wins, treasure_guard prescan rc0, gitignore patterns pre-staged by bm-a leg) "
       "-- S0 stash-bridge structural race eliminated for bm-b family (this round's autostash conflict = 7th cross-machine instance, last one for this family); "
       "watermark_red.json residual honestly deferred: origin blob machine=bm-c, no suffix, claw fail-closed blocks bm-b deletion "
       "(no --no-verify normalization) -> HQ-FEEDBACK F-20261018-01 filed for group ruling. "
       "(b) receipts closed: bm-a MSG-1145 confirms MSG-0845/1035/1137 pickup 8/8 byte-identical + CEO channel + O-0948 receipt window closed both machines; "
       "MSG-1145 + MSG-1229 (bm-c W268 seat, informational) processed to inbox/processed. "
       "(c) O-0948 24h observation interim: zero died-pre-closeout since v2 rootfix (firings 10:12 r1004 / 10:57 r1005 closed / 12:42 r1006 in-flight, no TIMEOUT markers in logs). "
       "(d) D-19 dual delta consumed (dec 4cfdd17c: D-20261018-01 revival-watch = night-round domain not bm-b + bigmoney F-20261017-01 self-fix by bm-c r1089 confirmed on-tree via pull; "
       "ord fe7a4d15: drama full pivot to 3D manga-style CEO order read (audio-line assets remain valid per bm-a MSG-1145), MV V5.6 PASS row, memory-gov addendum -- "
       "bm-b gate --report first-fire LEDGER row already in ledger 10:30) + advanced via d19_watermark.py, read-back equality verified. "
       "(e) S6 43 legs rc0 (Sunday light: live.paper family x4 honest skip; collectors no-op; 4 stale-takeover derives by bm-b per O-2100 s2.4 STALE_MIN law; "
       "REPORT-2026-10-18 + LIVE-2026-10-18 written; dualrun ZERO-DRIFT streak 51; orphan 7/0; attrition healed-clean). "
       "(f) pool starvation honest face: local registry 9/9 retired|done (zero open), board empty, W268 seat armed by bm-c 12:29 = supply answer for audit flag; idle --worked declared (12->0). "
       "(g) backlog row14 done-marker backfilled (work substance = r1004/r1005 windows, evidence MSG-1035 + bm-a MSG-1145 dual-machine closure).")

verdict = ("GREEN: D-02 bm-b leg closed (6/7 own tick faces out-of-repo; watermark_red deferred claw-blocked honest) "
           "+ S6 43 rc0 + smoke 49/49 + receipts closed (MSG-0845/1035/1137 pickup 8/8) + O-0948 window interim zero died-pre-closeout "
           "+ orphan 7/0 + dualrun streak 51 + idle --worked (12->0); leftovers = closeout push verify r1007 (N=0 expected) "
           "+ pool starved awaiting restock (W268 prereg derive = bm-c next window FIRST ACTION; bm-b engine lane ready) "
           "+ watermark_red.json group ruling (HQ-FEEDBACK F-20261018-01)")

nextp = ("r1007: 1) closeout push delivery verify (fetch + ls-remote, N=0 expected, per r1005 disposal order law) "
         "2) O-0948 24h window continue (died-pre-closeout must stay zero through 10-19 ~10:2x) "
         "3) pool starved honest face awaiting secretary restock; burn assigned faces when W268 prereg lands (bm-c owner) "
         "4) watermark_red.json residual = HQ-FEEDBACK F-20261018-01 pending group collection "
         "5) D-19 fresh delta per round 6) O-20261017-1751 drama voice lane: audio-line assets valid under 3D pivot, next demand routed by drama-dept")

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
state["round_no"] = 1006
state["round"] = 1006
state["round_no_label"] = "r1006"
state["now_active"] = "r1006 closing"
state["current_task"] = "r1006: closeout (D-02 bm-b leg + receipts + S6 43 + state/heartbeat/round-report/push)"
state["task"] = state["current_task"]
state["current"] = "r1006: D-02 bm-b leg closed + S6 full chain + receipts + D-19 dual advance"
state["did"] = did
state["last_action"] = ("r1006: D-02 bm-b leg closed (6 own tick faces out-of-repo, watermark_red deferred claw-blocked) "
                        "+ 3 MSG pickup receipts closed + S6 43 rc0 + D-19 dual advance + idle --worked + backlog row14 backfill")
state["next"] = nextp
state["next_milestone"] = ("O-0948 window zero through 10-19 ~10:2x + closeout push N=0 + W268 prereg lands -> bm-b burn lane refills (48h window)")
state["verdict"] = verdict
state["latest_artifact"] = ("D-20261015-02 bm-b leg: 6 tick faces out-of-repo (commit this round) + HQ-FEEDBACK F-20261018-01 "
                            "+ backlog row14 done-marker + S6 products REPORT-2026-10-18 / LIVE-2026-10-18")
state["last_artifact"] = state["latest_artifact"]
state["note"] = ("r1006: autostash conflict at S0 = 7th machine instance of the stash-bridge race, root-caused to still-tracked bm-b tick faces; "
                 "leg executed same round = family race eliminated going forward (6/7; watermark_red shared-name residual = group ruling pending)")
state["orphan_face"] = 7
state["orphan_faces"] = 7
state["orphan_face_note"] = "r1006 chain probe (12:51): 7 py faces / 0 orphans"
state["sat_engine"] = {"status": "alive (r1006 S6 status rc0, idle verdict, queue_depth 0)", "checked_at": ts}
state["decisions_delta_pending"] = False
state["orders_delta_pending"] = False
state["d19_probe_due"] = False
state["d19_probe_due_note"] = ("r1006: dual delta consumed + advanced via d19_watermark.py update --advance "
                               "(dec 4cfdd17c / ord fe7a4d15, read-back full-string equality verified); next probe per standing cadence")
state["heartbeat_epoch_utc_face"] = "bm-b.json updated this round (epoch int verified)"
sync = state.get("sync", {})
sync["r1006_main_push"] = {
    "status": "PENDING (this commit)",
    "pushed_sha": "pending",
    "consumed_at": "pending r1007",
    "behind_origin_main": 0,
    "note": ("r1006 payload = D-02 bm-b leg (6-face index removal) + closeout faces (state/heartbeat/round-report + backlog row14 + "
             "HQ-FEEDBACK F-20261018-01 + inbox processed moves x2) + S6 log/driver/closeout work files + own regen/product faces "
             "(daily_report + live_usage + scorecard/dashboard/paper_export stale-takeover + collectors bm-b lanes + token_meter); "
             "fleet/machine-health.json (shared union daemon face) intentionally NOT added; docs faces = S6 products (daily_report/live_usage) included as own products; "
             "base = f3cc9544d origin tip fresh at S0 rebase")
}
sync["behind_origin_main"] = 0
state["sync"] = sync
wf("state.json", json.dumps(state, indent=1, ensure_ascii=False) + "\n")
# json round-trip sanity
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
hb["did"] = ("r1006: D-02 bm-b leg closed (6 own tick faces out-of-repo; watermark_red deferred claw-blocked honest) "
             "+ 3 MSG pickup receipts closed (bm-a MSG-1145 8/8) + O-0948 window interim zero "
             "+ S6 43 rc0 (REPORT/LIVE-10-18 + 4 stale-takeover derives) + D-19 dual advance + idle --worked + backlog row14 backfill")
hb["last_action"] = state["last_action"]
hb["last_action_at"] = ts
hb["next"] = nextp
hb["verdict"] = verdict
hb["latest_artifact"] = state["latest_artifact"]
hb["note"] = ("r1006: D-20261015-02 bm-b leg executed (autofill/idle x2/satengine x3 out-of-repo, disk live-wins, prescan rc0); "
              "watermark_red.json shared-name residual = HQ-FEEDBACK F-20261018-01 (claw fail-closed: origin blob machine=bm-c); "
              "S0 autostash conflict = 7th stash-bridge instance, family race now eliminated for bm-b; "
              "MSG-1229 W268 seat processed (bm-c owner, informational); pool starved honest face awaiting restock.")
hb["round_no"] = 1006
hb["round"] = 1006
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

# -- 4. backlog row 14 done-marker backfill (shared file: fresh read-modify-write) --
bp = "fleet\\backlog.md"
btxt = rf(bp)
marker_key = "O-0948 rootfix"
lines = btxt.split("\n")
hit = -1
for i, ln in enumerate(lines):
    if marker_key in ln and "14." in ln:
        hit = i
        break
if hit < 0:
    print("BACKLOG-ROW14-NOT-FOUND")
    sys.exit(4)
if "done@bm-b" not in lines[hit]:
    lines[hit] = (lines[hit].rstrip() +
                  " claimed@bm-b@2026-10-18T13:05:00+08:00（补录标记·实质 r1004/r1005 窗完成）"
                  " done@bm-b@2026-10-18T13:05:00+08:00+BigMoney MSG-20261018-1035-bmb-rootfix.md"
                  "（O-0948 回执节 r1004 已落·bm-a MSG-20261018-1145 确认回执窗双机全闭·8/8 字节恒等·CEO 看片通道落位）")
    wf(bp, "\n".join(lines))
    receipt["steps"]["backlog_row14"] = "marker-appended"
else:
    receipt["steps"]["backlog_row14"] = "already-marked"

# -- 5. HQ-FEEDBACK row (mechanism residual, group collection) --
hp = "HQ-FEEDBACK.md"
htxt = rf(hp)
row = ("- F-20261018-01 [bm-b r1006 2026-10-18 13:0x·S0 机制面·D-20261015-02 bm-b 腿执行发现] "
       "**results/watermark_red.json 共享名 churn 面=三机无人能退库的结构性死锁（爪属主门 × machine-local 已 gitignore 共享名件）**："
       "D-02 家族件 results/watermark_red.json（O-1626/T-25 C7 machine-local disposal·.gitignore L84 模式 10-15 已在位）仍 tracked 且每轮三机轮写"
       "（last-writer-wins·origin 现 blob machine=bm-c ts 12:40·本 bm-b 窗 S0 autostash 冲突 10 面之一=病灶面在役实证）；"
       "bm-a r1001（627a3e96c）/bm-c r1019（5b174a247）两腿 rm 集均未含此件；bm-b 腿今窗实测删除被爪正拦"
       "（origin blob machine=bm-c≠bm-b·路径无后缀→第四通道不适用→fail-closed·--no-verify 不常态化）"
       "——结构上任何非现 blob 属主机都无法退该件=churn 面永久在库。建议三选一："
       "①现 blob 属主 bm-c 下窗自退（同型 leg·一次提交全机生效）；"
       "②爪增第五通道=「路径∈.gitignore 已裁定的 machine-local 模式集 且 删除机盘面 live face 的 machine 字段==删除机」即放行"
       "（属主证据在盘面 live face 不在 origin blob——machine-local 件的 blob 只是 last-writer 快照非属主面）；"
       "③集团裁 retired-in-place 冻结（同 results/autofill_state.json 先例）并从 D-02 家族摘名。"
       "证据：git show origin/main:results/watermark_red.json（machine=bm-c 实读）+ 本轮 S0 stash 面清单（该件在列·stash 63f7ce38b 已按纯再生面弃置）"
       "+ 两 leg commit stat 均无此件 + bm-b 腿 6 件全过爪（第四通道）对照。状?open（集团周进化轮收取·bm-b 腿=6/7 收口·本件唯一残留如实披露）\n")
if "F-20261018-01" not in htxt:
    if not htxt.endswith("\n"):
        htxt += "\n"
    wf(hp, htxt + row)
    receipt["steps"]["hq_feedback"] = "row-appended"
else:
    receipt["steps"]["hq_feedback"] = "already-present"

# -- 6. round report row --
rp = "logs\\iteration-loop\\round_reports.md"
rtxt = rf(rp)
row6 = (f"{ts} | r1006 bm-b | dept:工程+舰队 | WM verdict: GREEN (red=false @12:51:37 py_watermark probe, lane=healthy, next_pick=claimed moneyflow awaiting panel) | "
        "当前活=r1006 收口（D-02 bm-b leg + 回执闭环 + S6 维护链）；"
        "最近实物=D-20261015-02 bm-b leg 6 tick faces out-of-repo（autofill/idle×2/satengine×3·prescan rc0·盘面 live-wins）+ REPORT-2026-10-18.md + LIVE-2026-10-18.md（S6 产品面）+ HQ-FEEDBACK F-20261018-01；"
        "下个里程碑（≤48h）=O-0948 24h 窗收口（10-19 ~10:2x·died-pre-closeout 保持零）+ closeout push N=0 复核 + W268 prereg 落地后 bm-b 烧录道回填 | "
        "did: " + did[:1200] + " | "
        "孤儿面=0（7 py faces/0 orphans @12:51 probe）；本地未达 origin commit 数=0（S0 rebase 后实测 behind 15→0；本轮收口推送 r1007 轮首复核）；"
        "O-0948 观察窗中期=零 died-pre-closeout（10:12/10:57/12:42 三点火零 TIMEOUT 标记）；"
        "记账面=收口三件套+backlog 行 14 补标+HQ-FEEDBACK 行（≤5 内）；"
        "验证: smoke 49/49 rc0 + S6 43 legs rc0（链日志 results/_r1006bmb_s6_log.txt）+ dualrun ZERO-DRIFT streak 51 + d19 advance read-back equal + claw selftest 34/34 + 爪双件恒等 + loop pin=2 no-op + watchdog S4U 重注册 | "
        "下轮: r1007 = 1) push 送达核验（fetch+ls-remote·N=0 预期） 2) O-0948 窗续盯 3) 池 starved 诚实面候秘书处补货（W268 prereg=bm-c 下窗 FIRST ACTION·落地后本机烧录道就绪） 4) watermark_red 残留候集团收取 5) D-19 新鲜差集\n")
if not rtxt.endswith("\n"):
    rtxt += "\n"
wf(rp, rtxt + row6)
receipt["steps"]["round_report"] = "row-appended"

# -- 7. receipt --
wf("results\\_r1006bmb_closeout_receipt.json", json.dumps(receipt, indent=1, ensure_ascii=False) + "\n")
print("CLOSEOUT-OK", json.dumps(receipt["steps"], ensure_ascii=False))
