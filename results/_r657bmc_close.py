# -*- coding: utf-8 -*-
# r657 bm-c close driver: (a) zero new pit this round -> zero CODELY.md append
# (law: pits land in main only when real); (b) S5 ledger line to canonical
# per-machine path (r645 epoch law); (c) state-bm-c round_no increment +
# summaries; (d) heartbeat with live metrics + 3-line CEO face; epoch int
# self-assert (smoke F7). Main-file blob size DERIVED LIVE via git cat-file
# (r653 close-size receipt-vs-measure law). ASCII-safe console output.
# Pattern: _r656bmc_close.py (r655 line format, watermark-first).
import json, os, time, datetime, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
TS = NOW.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

# ---------- live metrics ----------
try:
    import psutil
    cpu = round(psutil.cpu_percent(interval=1.0), 1)
    ram_free = round(psutil.virtual_memory().available / (1 << 30), 1)
except Exception:
    cpu, ram_free = 0.0, 0.0
gpu_free = 0
try:
    g = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, creationflags=0x08000000)
    gpu_free = int(g.stdout.decode("ascii", "replace").strip().splitlines()[0])
except Exception:
    gpu_free = 0

# ---------- facts-driven numbers (never hand-typed, r583 S4 law) ----------
trio = json.load(open(os.path.join(ROOT, "results", "_r657bmc_trio_watch.json"), encoding="utf-8-sig"))
qv = trio["trio"]["quality"]["nulls_lines"]
dv = trio["trio"]["divlowvol"]["nulls_lines"]
vv = trio["trio"]["value"]["nulls_lines"]
facts = json.load(open(os.path.join(ROOT, "results", "_r657bmc_s05_facts.json"), encoding="utf-8-sig"))
assert facts["dec_match_prev"] and facts["ord_match_prev"] and facts["unacked_count"] == 0
ack_n = facts["orders_ack_count"]
# main CODELY.md blob size derived LIVE (r653 close-size law)
blob = subprocess.run(["git", "-C", ROOT, "cat-file", "-s", "HEAD:CODELY.md"],
                      capture_output=True)
main_b = int(blob.stdout.decode("ascii", "replace").strip())
headroom = 30720 - main_b
qa_out = open(os.path.join(ROOT, "results", "_r657bmc_qa_runner.out"), encoding="utf-8", errors="replace").read()
assert "REPORT qa\\smoke-r657.md items=5/5" in qa_out and "determinism=True" in qa_out

def load_json(p):
    raw = open(p, "rb").read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    return json.loads(raw.decode("utf-8-sig")), bom

def save_json(p, obj, bom):
    with open(p, "w", encoding="utf-8-sig" if bom else "utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)

# ---------- three-line CEO face ----------
face3 = ("当前活: r657 值守轮收口（黄金周无 bar：S0 fast-forward bm-a r809 收口批零冲突+S6 38/38+QA 包 r657 显式轮标 5/5·"
         "零新坑零 CODELY append）"
         " | 最近实物: qa/smoke-r657.md（5/5·93 trades·determinism=True·equity 终值 1,017,839 面恒等 r642-656）"
         "+results/_r657bmc_s6_log.txt（38/38 rc0）+results/_r657bmc_trio_watch.json（trio 证据面）"
         " @ {ts} | 下个里程碑: bm-b 07:2x Q finalize 计划窗观察（r794 声明·r668 first-to-2000 律）+D finalize ~10-08；"
         "10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar+compute_audit 金周结构旗 re-eval；月界首考 10-31；下个 5x=r660").format(ts=TS)
latest = ("qa/smoke-r657.md 5/5 (explicit --round 657, pid 24752, 93 trades, determinism=True, equity 800 pts final 1,017,839 "
          "face-identical r642-656) + qa/equity-curve-r657.png + results/_r657bmc_s6_log.txt 38/38 rc0 "
          "+ results/_r657bmc_trio_watch.json (V 2000 complete, Q {q}, D {d}) @ {ts}").format(q=qv, d=dv, ts=TS)
milestone = ("bm-b 07:2x trio-Q finalize plan window watch (r794 declared, r668 first-to-2000 law, G4 r638 fallback armed) + "
             "D finalize ~10-08 (bm-b lane); 10-09 market reopen (data-chain re-arm + regime_guard v3 first bar + "
             "compute_audit structural-flag re-eval); monthly exam 10-31; next 5x = r660 (HANDOVER window)")

did = ("r657 bm-c: golden-week standing-guard round (zero new pits; no P0 tail). (1) S0: round-start dirty = 3 own-lane "
       "daemon faces (autofill + 2 sat-engine live-wins); pull --rebase --autostash fast-forward de2ffd715..21d241406 "
       "(bm-a r809 closeout wave: 51 files, sat-engine ledgers + prospect_promotion faces + r809 closeout scripts; "
       "zero conflict, autostash applied). (2) S0.5 double-sweep (s05 + s7close): DEC 635C3024 / ORD 437E9CDD both "
       "MATCH zero-delta at both sweeps; fleet orders {ack} acked, zero unacked at both sweeps; inbox empty. (3) S1 smoke "
       "48/48. S3: board open=0 (Codely jobs 0, fleet 176 zero open, 46 claimed); watermark green (red=false; "
       "py_watermark py_low_board_clear = golden-week legal idle whitelist); SAT alive (Tools face engine_alive=True, "
       "tick 05:35 fresh, wave_shards_done advancing); post_review per-item-latest 48 YES / 0 NO (00:16 NO rows "
       "json_field-error family already re-derived green by later sweeps -- zero P0). Trio watch r657: V {v}/2000 "
       "COMPLETE, Q {q}/2000, D {d}/2000 zero inter-round growth (nulls mtime 04:35:38 both faces); bm-b hb stale "
       "81.8min @05:4x BUT r794 closeout declared explicit plan: trio Q finalize ~10-07 07:2x (first-to-2000 same-window "
       "per r668, G4 r638 fallback armed) + D finalize late 10-07..10-08 -- plan window not yet due, no forfeiture; "
       "no proxy burn by bm-c (double-burn red line + bm-b same-window finalize design); escalation face = if 07:2x "
       "window passes empty AND hb stale persists -> next-round fleet-note/GM per pool protocol. Pool FUND-QUALITY-P1-NULLS "
       "+ FUND-DIVLOWVOL-P1-NULLS ready owner-face bm-b + TRIAL-LABOR-W14-GENERATE waiting (governance park held); "
       "trial-labor line satisfied by in-flight trio judge batches, no new drafting. bm-a hb fresh 11.8min (r809 "
       "closeout face) -- zero stale-takeover needed this round. (4) S6 chain 38/38 rc0 (dualrun ZERO-DRIFT streak 51 "
       "@403 unchanged face; compute_audit FLAG supply_gap,supply_floor = known golden-week structural face re-eval "
       "10-09+; py_watermark py_low_board_clear legal; CALL-2026-09-30 cell ORA regenerated idempotent; golden-week "
       "no-op family honest; token meter rc0). (5) QA pack r657: ignited detached pid 24752 with EXPLICIT --round 657 "
       "(r758/r640 law), polled terminal before close -- 5/5, 93 trades, determinism=True, equity 800 pts final 1,017,839 "
       "face-identical r642-656, png 66,233B, zero mislabel. Honest note: qa ignite print line carried cosmetic "
       "round=656 remnant (PowerShell quote-escape miss, pit-ps known family) -- fixed in-file same window; ignition "
       "argument was --round 657 throughout, product face zero contamination. (6) S7 self-heal green: loop pin=5 next "
       "fire 05:45 present, watchdog present (schtasks via Invoke-SilentExe named-param face), both claws LF-normalized "
       "MATCH no-op (zero reinstall needed), attrition CLEAN (4 ledgers, zero active loss, historical shrinks "
       "healed-annotated). Zero new pits, zero CODELY.md append (blob face {mb}B derived live at close, headroom "
       "{hr}B).").format(ack=ack_n, v=vv, q=qv, d=dv, mb=main_b, hr=headroom)

verdict = ("alive: r657 standing-guard round complete (zero new pits, zero CODELY append, blob {mb}B headroom {hr}B; QA pack "
           "r657 5/5 explicit --round; S6 38/38 rc0; smoke 48/48; board open=0; satengine alive (face tick fresh, shards "
           "advancing); DEC/ORD double-sweep zero-delta {ack} ack; attrition CLEAN; trio V complete Q{q}/D{d} bm-b "
           "rightful lane (r794 declared 07:2x Q finalize plan window, watch face); golden-week no-bar until 10-09)").format(
               mb=main_b, hr=headroom, ack=ack_n, q=qv, d=dv)

# ---------- (b) S5 ledger line (canonical path, r645 law; watermark first) ----------
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
rb = open(RR, "rb").read()
assert rb.endswith(b"\r\n")
row = ("watermark: 绿（red=false lane healthy·SAT 活=Tools 面 engine_alive True·tick 05:35 新鲜·wave_shards_done 推进·"
       "board 0 open/176·金周 no-bar 至 10-09）"
       " | {ts} | r657 bm-c | dept:工程/舰队 | 当前活: r657 值守轮收口（黄金周无 bar：S0 fast-forward bm-a r809 收口批"
       "零冲突+S6 38/38+QA 包 r657 显式轮标 5/5·零新坑零 CODELY append） | 最近实物: qa/smoke-r657.md 5/5（93 trades·"
       "determinism=True·equity 800 点终值 1,017,839 面恒等 r642-656）+qa/equity-curve-r657.png+results/_r657bmc_s6_log.txt"
       "（38/38 rc0）+results/_r657bmc_trio_watch.json（trio 证据面） | 下个里程碑: bm-b 07:2x Q finalize 计划窗观察"
       "（r794 声明·r668 first-to-2000 律·G4 r638 fallback armed）+D finalize ~10-08；10-09 复市数据链 re-arm+"
       "REGIME_GUARD v3 首 bar+compute_audit 金周结构旗 re-eval；月界首考 10-31；下个 5x=r660 | S0: 轮首树脏=3 本车道 "
       "daemon 面（autofill+2 sat-engine live-wins）→pull --rebase --autostash fast-forward de2ffd715..21d241406（bm-a "
       "r809 收口批 51 文件·sat-engine 台账+prospect_promotion 面+r809 收口脚本·零冲突 autostash 回放）；S0.5 双扫"
       "（s05+s7close 两腿全清洁）：DEC 635C3024/ORD 437E9CDD 双 MATCH 零 delta+fleet orders {ack} ack 零未回执+inbox "
       "空；S1 48/48；S3: 板 open=0（Codely jobs=0·fleet 176 零 open/46 历史 claimed）·watermark 绿（py_watermark "
       "py_low_board_clear=黄金周合法 idle 白名单）·SAT 活（Tools 面 engine_alive True·tick 05:35 新鲜·wave_shards_done "
       "推进）·post_review 按 item 最新行 48 YES/0 NO 零红项（00:16 NO 行=json_field-error 族·后续 derive 已翻绿·零 "
       "P0）·trio watch r657: V {v}/2000 COMPLETE·Q {q}/2000·D {d}/2000 轮间零增长（nulls mtime 04:35:38 双面）——"
       "bm-b hb stale 81.8min@05:4x 但 r794 收口已声明明确计划窗=trio Q finalize ~10-07 07:2x（r668 first-to-2000 "
       "同窗律·G4 r638 fallback armed）+D finalize late 10-07..10-08——未到失约窗不计失约·bm-c 零代烧（双烧红线+bm-b "
       "同窗 finalize 设计）·升级面=若 07:2x 窗空过且 hb stale 持续→下轮 fleet 消息/GM 按 pool 协议处置·池 2 ready"
       "（fund Q/D faces）+TRIAL-LABOR-W14-GENERATE waiting 治理停放维持·试用劳力线=trio 在飞判决批已满足零新起草·"
       "bm-a hb 新鲜 11.8min（r809 收口面）零 stale-takeover 需求；S6 38/38 rc0（dualrun ZERO-DRIFT streak 51 @403 "
       "不变面·compute_audit FLAG supply_gap/supply_floor=金周已知结构面 re-eval 10-09+·CALL-2026-09-30〔cell ORA〕"
       "当日幂等再生·金周 no-bar 族诚实 no-op·token meter rc0）；QA包r657 显式 --round 657 分离点火 pid 24752+轮询"
       "终态零误标（5/5·93 trades·determinism=True·equity 800 点终值 1,017,839·png 66,233B·面恒等 r642-656）；诚实"
       "注记：qa ignite print 行残留 cosmetic round=656（PS 引号转义失手·pit-ps 已知族）——同窗当场修文件·点火实参"
       "全程 --round 657·产物面零污染；S7 自愈面全绿（loop pin=5 下跳 05:45 在册·watchdog 在册〔schtasks via "
       "Invoke-SilentExe 命名参数面〕·precommit/prepush 双爪 LF 归一 MATCH no-op 零重装需求·attrition CLEAN 4 台账"
       "零 active loss·历史 healed 注记照录）；零新坑零 CODELY append（主件 {mb}B close 当场 git cat-file 实测 "
       "derive·余量 {hr}B）；本地未达 origin commit 数=0（push+fetch+ls-tree 自证送达） | 证据=qa/smoke-r657.md 5/5+"
       "qa/equity-curve-r657.png+results/_r657bmc_s6_log.txt 38/38+results/_r657bmc_s05_facts.json（双扫 s05+s7close "
       "两腿）+results/_attrition_guard_scan.json CLEAN+results/_r657bmc_trio_watch.json+results/_r657bmc_qa_runner.out"
       "（terminal 5/5） | 下轮指针：(a) bm-b 07:2x Q finalize 计划窗观察（r794 声明面）——窗空过+hb stale 持续=升级"
       "处置（fleet 消息/GM 按 pool 协议）；(b) 10-09 复市数据链 re-arm+REGIME_GUARD v3 首 bar+compute_audit 金周"
       "结构旗 re-eval；(c) 月界首考 10-31；(d) 下个 5x=r660〔HANDOVER 窗〕"
       "\n").format(ts=TS, ack=ack_n, v=vv, q=qv, d=dv, mb=main_b, hr=headroom)
open(RR, "wb").write(rb + row.encode("utf-8").replace(b"\n", b"\r\n"))

# ---------- (c) state-bm-c.json ----------
SP = os.path.join(ROOT, "state-bm-c.json")
st, bom = load_json(SP)
for k in ("clock_read", "ts", "last_seen", "last_seen_at", "updated", "updated_at", "last_round_at",
          "last_run_at", "last_ts", "last_decisions_read_at", "last_decisions_at", "last_round_ts",
          "current_task_at"):
    st[k] = TS
st["round_no"] = 658
st["round_no_label"] = "round 657 (bm-c)"
st["did"] = did
st["last_round"] = did
st["last_round_summary"] = ("r657: clean standing-guard round, zero new pits (blob {mb}B unchanged, headroom {hr}B); "
                            "QA r657 5/5 explicit --round; S6 38/38; DEC/ORD double-sweep zero-delta {ack} ack; attrition "
                            "CLEAN; trio V complete Q{q}/D{d} bm-b lane (r794 declared 07:2x plan window); smoke 48/48").format(
                                mb=main_b, hr=headroom, ack=ack_n, q=qv, d=dv)
st["last_action"] = did
st["current_task"] = face3
st["activity_now"] = face3
st["next"] = ("(a) bm-b 07:2x trio-Q finalize plan-window watch (r794 declared, r668 first-to-2000 law); if window "
              "passes empty AND bm-b hb stale persists -> escalation (fleet note / GM per pool protocol). "
              "(b) 10-09 market reopen: data-chain re-arm + REGIME_GUARD v3 first bar + compute_audit golden-week "
              "structural flags re-eval. (c) monthly exam 10-31 assembly face. (d) next 5x = r660 (HANDOVER window).")
st["note"] = ("r657: clean standing-guard round, zero new pits (blob {mb}B live-derived, headroom {hr}B); QA r657 5/5 "
              "explicit --round; S6 38/38; DEC/ORD double-sweep MATCH {ack} ack; attrition CLEAN; trio V complete, "
              "Q {q}, D {d} (bm-b lane, r794 declared 07:2x Q finalize plan window -- watch face, no proxy burn).").format(
                  mb=main_b, hr=headroom, ack=ack_n, q=qv, d=dv)
st["verify"] = ("receipts: qa/smoke-r657.md 5/5 (explicit --round 657, pid 24752) + qa/equity-curve-r657.png + "
                "results/_r657bmc_s6_log.txt 38/38 rc0 + results/_r657bmc_s05_facts.json (double-sweep s05+s7close: "
                "DEC 635C3024 + ORD 437E9CDD) + results/_attrition_guard_scan.json CLEAN + results/_r657bmc_trio_watch.json "
                "+ results/_r657bmc_qa_runner.out (terminal 5/5)")
st["dec_sha_method"] = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r657 double-sweep "
                        "s05+s7close both scans = 635C3024 MATCH zero-delta; value facts-driven from "
                        "results/_r657bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))")
st["ord_sha_method"] = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r657 double-sweep s05+s7close "
                        "both scans = 437E9CDD MATCH zero-delta; fleet orders {ack} ack at BOTH sweeps (double-sweep "
                        "law); value facts-driven from results/_r657bmc_s05_facts.json, 40hex shape-asserted, never "
                        "hand-typed (r583 S4 law))").format(ack=ack_n)
st["cpu_pct"] = st["cpu_util_pct"] = cpu
st["cpu_idle_pct"] = round(100 - cpu, 1)
st["free_ram_gb"] = st["idle_ram_gb"] = st["ram_free_gb"] = ram_free
for k in ("gpu_free_vram_mib", "gpu_free_vram_mb", "gpu_idle_vram_mib", "gpu_idle_vram_mb", "gpu_free_mb",
          "gpu_idle_mb", "gpu_vram_free_mb", "gpu_free_mib"):
    st[k] = gpu_free
save_json(SP, st, bom)

# ---------- (d) heartbeat ----------
HP = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
hb, bom2 = load_json(HP)
for k in ("clock_read", "ts", "last_seen", "last_seen_at", "updated", "updated_at", "current_task_at"):
    hb[k] = TS
hb["heartbeat_epoch_utc"] = EPOCH
hb["round_no"] = 658
hb["round_no_label"] = "round 657 (bm-c)"
hb["current_task"] = face3
hb["activity_now"] = face3
hb["latest_artifact"] = latest
hb["next_milestone"] = milestone
hb["verdict"] = verdict
hb["prod_lanes"] = ("r657 值守轮（黄金周无 bar：S0 fast-forward bm-a r809 收口批零冲突+S6 38/38+QA r657 5/5 显式轮标；"
                    "板 open=0；watermark 绿；SAT 引擎活；bm-b 07:2x Q finalize 计划窗观察面；零新坑零 CODELY append；"
                    "下个 5x=r660〔HANDOVER 窗〕")
hb["health"] = ("alive (r657 standing-guard clean round: S0 fast-forward bm-a r809 closeout wave zero-conflict, claws "
                "LF-normalized MATCH no-op, loop pin=5 next fire 05:45, watchdog present; golden-week no-bar until 10-09)")
hb["cpu_pct"] = hb["cpu_util_pct"] = cpu
hb["cpu_idle_pct"] = round(100 - cpu, 1)
hb["free_ram_gb"] = hb["idle_ram_gb"] = hb["ram_free_gb"] = ram_free
for k in ("gpu_free_vram_mib", "gpu_free_vram_mb", "gpu_idle_vram_mib", "gpu_idle_vram_mb", "gpu_free_mb",
          "gpu_idle_mb", "gpu_vram_free_mb", "gpu_free_mib"):
    hb[k] = gpu_free
save_json(HP, hb, bom2)

# ---------- self-verify (smoke F7 face) ----------
hb2 = json.loads(open(HP, "rb").read().decode("utf-8-sig"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in hb2["clock_read"] and hb2["clock_read"].endswith("+08:00")
st2 = json.loads(open(SP, "rb").read().decode("utf-8-sig"))
assert st2["round_no"] == 658
print("CLOSE_OK ts=%s cpu=%s ram=%s gpu=%d main_blob=%dB headroom=%dB trio_Q=%d trio_D=%d" % (
    TS, cpu, ram_free, gpu_free, main_b, headroom, qv, dv))
