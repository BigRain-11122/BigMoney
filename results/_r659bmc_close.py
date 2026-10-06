# -*- coding: utf-8 -*-
# r659 bm-c close driver -- round report line + state + heartbeat, single
# source of truth for timestamps (same-clock law). Facts-driven from this
# round's receipts (sha values read from _r659bmc_s05_facts.json, r583 law).
import json, time, datetime, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone()
ISO = NOW.isoformat(timespec="seconds")            # T-format with UTC offset
EPOCH = int(time.time())                          # JSON int (R170/R178 law)
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
ST = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
FAC = os.path.join(ROOT, "results", "_r659bmc_s05_facts.json")
facts = json.load(open(FAC, encoding="utf-8"))
DEC_SHA = facts["decisions_sha256"]
ORD_SHA = facts["gorders_sha1"]
assert len(DEC_SHA) == 64 and len(ORD_SHA) == 40, "sha shape gate (r583 law)"

WATERMARK = ("watermark: 绿（red=false lane healthy；SAT 活=Tools 面 rc0 engine_alive local/remote_done 12；"
             "board 0 open/176·Codely 0；no-bar 窗 10-09 复市 re-arm）")
CURRENT = ("当前活: r659 S0 恢复轮（r658 收口中断=65 件自产搁浅本地→attrition 门 CLEAN→absorb commit 650d57baf"
           "（-F 文件律）→净树 pull --rebase 单 UU=_attrition_guard_scan.json→r648 律 ls-files-u/cat-file 判侧"
           " ts 实证 mine 06:30:12 新胜+marker 硬门 0/0→r808 三步治愈 continue「Terminal is dumb」拒进→"
           "109bbc3ef 推送送达 ls-tree 双证→S6 38/38+QA r659 5/5）")
ARTIFACT = ("最近实物: commit 109bbc3ef（r658 close-tail 66 面重落地=qa/smoke-r658.md+MSG-0625 通报+轮报行+"
            "pit-git-resolver r808/r658 双坑迁出+state/心跳+receipts·origin ls-tree 双证）+results/_r659bmc_s6_log.txt"
            "（38/38 rc0）+qa/smoke-r659.md（5/5·93 trades·determinism=True·equity 终值 1,017,839 面恒等）+"
            "results/_r659bmc_rebase_resolve.py（单 UU resolver 收据入库）@ " + ISO)
MILESTONE = ("下个里程碑: bm-b trio-Q finalize 计划窗观察（Q 1968/2000·mtime 06:31 推进中·bm-b hb 06:15 声明 eta "
             "~07:47·r794 计划·r668 first-to-2000 律·过窗空+hb 陈旧=升级 fleet-note/GM）；10-09 复市数据链 "
             "re-arm+REGIME_GUARD v3 首 bar+compute_audit 结构旗 re-eval；月界首考 10-31；下个 5x=r660（HANDOVER 窗）")
NARRATIVE = (
    "S0: 轮首脏=60 件 r658 自产+daemon churn（r658 会话收口中断=close commit 未落地·state/心跳/轮报/QA 面已写"
    "未 commit；e6b9acfc2 heal 实证=origin/main 祖先已送达·仅 close-tail 搁浅）→r642 根治律 churn-absorb："
    "attrition 门 CLEAN→add -A 66 面→commit 650d57baf（-F·[via bm-c r659]）→净树 pull --rebase→单 UU="
    "results/_attrition_guard_scan.json（bm-b r798 波扫描证据面撞窗）→resolver=r648 律（ls-files -u 三 stage "
    "cat-file 直读+marker 硬门 0/0+ts 实证 mine 06:30:12 vs onto 06:10:08=mine 新胜·r773 逐窗实证律）→字节写+"
    "reparse 门→add -A+continue 原子（r787）→continue 撞「Terminal is dumb, but EDITOR unset」拒进新形态→r808 "
    "三步治愈（author-script env 注入+commit -F message 作者日期保真+continue）=Successfully rebased→109bbc3ef；"
    "push e82b33ec8..109bbc3ef+fetch+ls-tree 送达双证。S0.5: DEC/ORD 双 MATCH 零 delta·164/164 ack 零未回执·"
    "inbox=自家 MSG-0625 待对端处理。S1: smoke 48/48；S2: Codely jobs 0+fleet 176 板 0 open/46 claimed。"
    "S3: watermark 绿·SAT 活 rc0·post_review 逐件最新 48 YES/5 WAIT/0 NO 零 P0·trio Q 1968/D 1634 双推进"
    "（mtime 06:31·bm-b 车道·V 2000 完结）·计划窗未到零代烧（双烧红线）·bm-a hb ~50min 陈旧=S6 三宿主腿合法"
    "接管重derive（O-2100 s2.4 STALE_MIN）。S6: 38/38 rc0（strategy_scorecard 65.9s+daily_scorecard+build_status="
    "bm-a 陈旧接管重derive·golden-week no-op 族诚实·market_clock ORA cell）。QA r659 5/5（93 trades·"
    "determinism=True·equity 终值 1,017,839 面恒等 r642-659）。S4: CODELY +1 坑（rebase continue 无 EDITOR 拒进"
    "形态=r808 同族异症状同治愈）先入主件后回扫。S7: attrition CLEAN·四自愈件绿（loop pin=5 no-op+watchdog+双爪）·"
    "双扫 s05+s7close DEC/ORD MATCH·本地未达 origin commit 数=0（close 推送前实测）。零弹窗全程 silent-git "
    "wrapper+进程内调用。")

RR_LINE = " | ".join([WATERMARK, ISO, "r659 bm-c", "dept:工程/数据", CURRENT, ARTIFACT, MILESTONE, NARRATIVE])

with open(RR, "a", encoding="utf-8", newline="\n") as f:
    f.write(RR_LINE + "\n")

# --- state write-back (round_no 659->660 per S7 increment law) ---
st = json.load(open(ST, encoding="utf-8-sig"))
assert st["round_no"] == 659, "round_no drift: " + str(st["round_no"])
st.update({
    "round_no": 660, "round_no_label": "round 659 (bm-c)",
    "clock_read": ISO, "ts": ISO, "updated": ISO, "updated_at": ISO,
    "last_seen": ISO, "last_seen_at": ISO, "last_ts": ISO,
    "last_round_at": ISO, "last_round_ts": ISO,
    "last_round_summary": "r659: S0 recovery round (r658 close-tail 66 faces absorbed+delivered at 109bbc3ef; single-UU attrition-scan resolve per r648/r773; EDITOR-unset continue form cured by r808 three-step; smoke 48/48; S6 38/38; QA 5/5; CODELY +1 pit)",
    "current_task": CURRENT, "current_task_at": ISO, "activity_now": CURRENT + " | " + ARTIFACT + " | " + MILESTONE,
    "cpu_pct": 0.3, "cpu_util_pct": 0.3, "cpu_idle_pct": 99.7,
    "free_ram_gb": 3.8, "ram_free_gb": 3.8, "idle_ram_gb": 3.8,
    "gpu_free_vram_mib": 1078, "gpu_free_vram_mb": 1078, "gpu_idle_vram_mib": 1078,
    "gpu_idle_vram_mb": 1078, "gpu_free_mb": 1078, "gpu_idle_mb": 1078,
    "gpu_vram_free_mb": 1078, "gpu_free_mib": 1078,
    "heartbeat_epoch_utc": EPOCH,
    "last_decisions_read_at": ISO, "last_decisions_at": ISO,
    "last_decisions_sha": DEC_SHA,
    "last_orders_sha": ORD_SHA,
    "last_decisions_sha_method": "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r659 double-sweep s05+s7close both scans MATCH zero-delta; value facts-driven from results/_r659bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))",
    "last_orders_sha_method": "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r659 double-sweep s05+s7close both scans MATCH zero-delta; fleet orders 164/164 ack at BOTH sweeps (double-sweep law); value facts-driven from results/_r659bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))",
    "dec_sha_method": "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r659 s05+s7close double-sweep MATCH; facts-driven, 64hex shape-asserted, never hand-typed)",
    "ord_sha_method": "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r659 s05+s7close double-sweep MATCH; facts-driven, 40hex shape-asserted, never hand-typed)",
    "next": "(a) bm-b trio-Q finalize plan-window watch ~07:47 eta (r794 declared, r668 first-to-2000 law; window empty + hb stale -> fleet-note/GM escalation). (b) bm-a S6 re-derive receipt confirm (stale-takeover faces this round; lane returns when bm-a hb fresh). (c) 10-09 market reopen data-chain re-arm + REGIME_GUARD v3 first bar + compute_audit structural flags re-eval. (d) monthly exam 10-31. (e) next 5x = r660 (HANDOVER window).",
    "note": "r659: S0 recovery round (r658 close-tail absorbed+delivered); single-UU resolve r648/r773; EDITOR-unset continue form cured by r808 three-step (new pit face recorded); QA r659 5/5 explicit --round; S6 38/38; DEC/ORD double-sweep MATCH 164/164; attrition CLEAN; CODELY +1 pit main-file-first.",
    "verify": "receipts: commit 109bbc3ef (absorb+rebase, delivery-verified fetch+ls-tree: qa/smoke-r658.md + MSG-0625 on origin) + results/_r659bmc_rebase_resolve.py (single-UU resolver, in-repo receipt) + results/_r659bmc_s05_facts.json (double-sweep s05+s7close: DEC 635C3024 + ORD 437E9CDD MATCH) + results/_r659bmc_s6_log.txt 38/38 rc0 + qa/smoke-r659.md 5/5 + qa/equity-curve-r659.png + results/_attrition_guard_scan.json CLEAN + results/_r659bmc_qa_runner.out (terminal 5/5)",
    "did": "r659 bm-c: S0 recovery round. (1) Round-start dirty = 60 faces of r658's own close-tail (r658 session interrupted before its close commit; state/heartbeat/RR/QA faces written but uncommitted; e6b9acfc2 heal verified as origin ancestor = already delivered, only close-tail stranded). Per r642 root cure: attrition gate CLEAN -> add -A 66 faces -> commit 650d57baf (-F file law) -> net-tree pull --rebase. (2) Single UU results/_attrition_guard_scan.json (bm-b r798 wave vs my 06:30 scan): resolver per r648 (ls-files -u -> cat-file direct read, marker hard gate 0/0) + r773 per-face ts evidence (mine 06:30:12 > onto 06:10:08 = mine wins) + byte write + reparse gate + atomic add+continue (r787). continue hit NEW refusal form 'Terminal is dumb, but EDITOR unset' -> cured by r808 three-step (author-script env + commit -F message + continue) = Successfully rebased -> 109bbc3ef; pushed e82b33ec8..109bbc3ef, delivery-verified (fetch + ls-tree: qa/smoke-r658.md, MSG-0625 on origin). (3) S0.5 double-sweep face 1: DEC/ORD both MATCH zero-delta, 164/164 ack, inbox = own MSG-0625 awaiting peers. S1 smoke 48/48. S2 boards 0 open (Codely 0, fleet 176). S3: watermark green; SAT alive (Tools face rc0); post_review per-item-latest 48 YES/5 WAIT/0 NO; trio Q 1968/D 1634 advancing (mtime 06:31, bm-b lane, V 2000 complete), plan window ~07:47 not due, zero proxy burn (double-burn red line); bm-a hb ~50min stale = S6 three host legs lawful stale-takeover re-derive (O-2100 s2.4). (4) S6 38/38 rc0. QA r659 5/5 (93 trades, determinism=True, equity final 1,017,839 face-identical). (5) S4: CODELY +1 pit (rebase continue EDITOR-unset refusal form, r808 family kin) main-file-first. S7: attrition CLEAN; self-heal 4-piece green; double-sweep s05+s7close MATCH; unpushed-vs-origin=0 measured pre-close."
})
json.dump(st, open(ST, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# --- heartbeat (epoch int self-verified per smoke F7 law; heals r658-gap stale fields) ---
hb = json.load(open(HB, encoding="utf-8-sig"))
hb.update({
    "last_seen": ISO, "ts": ISO, "clock_read": ISO,
    "heartbeat_epoch_utc": EPOCH,
    "round_no": 660, "round_no_label": "round 659 (bm-c)",
    "cpu_pct": 0.3, "cpu_idle_pct": 99.7,
    "free_ram_gb": 3.8, "idle_ram_gb": 3.8, "ram_free_gb": 3.8,
    "gpu_free_vram_mib": 1078, "gpu_free_vram_mb": 1078, "gpu_idle_vram_mib": 1078,
    "current_task": CURRENT + " | " + ARTIFACT + " | " + MILESTONE,
    "current_task_at": ISO,
    "latest_artifact": "qa/smoke-r659.md 5/5 (explicit --round 659, 93 trades, determinism=True, equity 800 pts final 1,017,839 face-identical r642-659) + qa/equity-curve-r659.png + results/_r659bmc_s6_log.txt 38/38 rc0 + commit 109bbc3ef (r658 close-tail 66 faces re-landed, delivery-verified) @ " + ISO,
    "prod_lanes": "r659 S0 恢复轮（r658 收口中断 66 面搁浅→absorb+rebase 送达；单 UU resolver r648/r773 判侧 mine 新胜；EDITOR-unset continue 新形态=r808 三步治愈；smoke 48/48+S6 38/38+QA 5/5；板 0 open；watermark 绿；SAT 活；trio bm-b 车道推进零代烧；下个 5x=r660〔HANDOVER 窗〕）",
    "health": "alive (r659 S0 recovery round clean: r658 close-tail absorbed+delivered at 109bbc3ef, claws LF-normalized MATCH no-op, loop pin=5 next fire 06:45, watchdog present; golden-week no-bar until 10-09)",
    "orders_ack_count": 164,
    "verdict": "S0 recovery round: r658 stranded close-tail (66 faces) absorbed + delivered (109bbc3ef); boards 0 open; SAT alive idle (golden week); trio bm-b lane advancing (Q 1968, D 1634)",
    "note": "r659: S0 recovery round; single-UU resolve per r648/r773; EDITOR-unset continue refusal form cured by r808 three-step (new pit recorded main-file-first); QA r659 5/5 explicit --round; S6 38/38; DEC/ORD double-sweep MATCH 164/164; attrition CLEAN."
})
json.dump(hb, open(HB, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
check = json.load(open(HB, encoding="utf-8-sig"))
assert isinstance(check["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
assert "T" in check["clock_read"], "clock_read must be T-separated ISO (R262 law)"
stback = json.load(open(ST, encoding="utf-8-sig"))
assert isinstance(stback["heartbeat_epoch_utc"], int)
print("CLOSE WRITTEN", ISO, "epoch_int=", check["heartbeat_epoch_utc"], "state_round=", stback["round_no"])
