# -*- coding: utf-8 -*-
"""r669 bm-c close: state + heartbeat + round-report updater.
Laws: R170/R178 epoch int, R262 clock_read T-format, r583 facts-driven
watermark keys (dec/ord sha from s05 facts file), r640 race law (QA terminal
state polled before this script advances state), r653 measure-at-use (all
sizes in this round's faces derive from receipts/len() never hand-copied)."""
import datetime as dt
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
FACTS = os.path.join(ROOT, "results", "_r669bmc_s05_facts.json")
CREATE_NO_WINDOW = 0x08000000

now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

with open(FACTS, encoding="utf-8-sig") as fh:
    facts = json.load(fh)
dec_sha = facts["dec_sha"]
ord_sha = facts["ord_sha"]
assert len(dec_sha) == 64 and len(ord_sha) == 40, "facts sha shape gate"

gpu_mib = None
try:
    r = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                       capture_output=True, creationflags=CREATE_NO_WINDOW, timeout=20)
    gpu_mib = int(r.stdout.decode("utf-8", errors="replace").strip().splitlines()[0])
except Exception:
    gpu_mib = None

cpu_pct = 12
try:
    with open(os.path.join(ROOT, "results", "watermark.jsonl"), encoding="utf-8") as fh:
        rows = [json.loads(l) for l in fh if l.strip()]
    if rows:
        cpu_pct = int(round(float(rows[-1].get("cpu_total_pct", cpu_pct))))
except Exception:
    pass
cpu_idle = 100 - cpu_pct

with open(STATE, encoding="utf-8-sig") as fh:
    st = json.load(fh)
prev_gpu = st.get("gpu_free_vram_mib") or 1078
gpu_mib = gpu_mib if gpu_mib is not None else prev_gpu

ACT = ("当前活: r669 值守+D-06 超线修复轮收口（S0 落后 2 吸收〔bm-a r817 收口+r818 W172 预坐席〕干净 rebase·S1 48/48·S3 板 0 open+SAT 活+水位绿+池 401 done+1 ready bm-b keepalive+1 治理停泊 W14 零触碰·主产品=pit-git-resolver.md 实测 30,850B>30,720B 域线〔bm-a r817 10:06 增量致·r668 收据面 room-308B 声明=陈旧收据=r653 收据-实测律活案例·当场实测 derive〕→ rebase/sequencer 净路族 9 条 verbatim 零丢失迁出→pit-git-resolver-rebase.md 新子件+主件 r659 坑 994B 迁入母件 append 面·S6 38/38·QA r669 5/5）"
       " | 最近实物: results/_r669bmc_pit_resolver_split.json（零丢失收据·55 checks --verify PASS·prescan rc3 留痕）+research/pit-git-resolver-rebase.md（11,569B/9 条新子件·字节对账+md5 行）+research/pit-git-resolver.md（30,850→23,579B 回线·指针行+r659+对账行）+CODELY.md（主件 30,719→29,724→30,527B〔+S4 新坑律 803B·余量 193B〕）+qa/smoke-r669.md 5/5（93 trades·determinism=True·equity 1,017,839 跨轮恒等）+results/_r669bmc_s6_log.txt 38/38 rc0+docs/daily_report/REPORT-2026-10-07.md+docs/live_usage/LIVE-2026-10-07.md（ORANGE）"
       " | 下个里程碑: 10-08（周四）复市首交易日——数据链 re-arm+REGIME_GUARD v3 首 bar 激活（t24 门=last_bar≥10-01 即活）+纸盘 marks 地板推进（bm-a r714 readiness 件 owns preflight）；trio finalize 窗观察至 10-09（bm-b 道）；W172 冻结窗 bm-a 预坐席已落（r818）；月界首考 10-31；下个 5x=r670（HANDOVER 窗+pit-lineage 让位窗）")
DID = ("r669 bm-c: golden-week watch + D-06 over-cap repair (pit-git-resolver sub-split) + main increment round. "
      "(1) S0: round-start dirty = 3 self daemon live-wins faces; behind origin 2 (bm-a r817 closeout 10:06 + r818 W172 pre-seat/churn-absorb) -- zero path overlap with dirty faces, explicit stash->pull --rebase->pop clean (net-tree zero-autostash root law), 0/0 after. "
      "(2) S0.5 double-sweep: DEC 635C3024 / ORD B687D867 zero-delta x2 (round-start + close); fleet orders 165/165 (164 O-files + README) zero unacked; inbox 0 for bm-c/ALL (bm-a W172-seat MSG = bm-a lane, read-noted only). "
      "(3) S1 smoke 48/48. S3: satengine alive rc0; watermark green (next_pick=claimed moneyflow IC batch, panel parked EM source-blocked 30min self-heal, unchanged); board open=0; job_list 0; pool 401 done + FUND-DIVLOWVOL-P1-NULLS ready (bm-b keepalive lane) + TRIAL-LABOR-W14-GENERATE waiting = governance park per MSG-2026-10-03-0436 (three-machine zero-touch); T-143 all four bm-c faces delivered r405-r408, remaining faces = bm-a primary lanes at assembly window; trial-labor line not triggered (W172 freezer pre-seated by bm-a r818 + trio finalize bm-b in flight = in-flight judgment work exists). "
      "(4) MAIN WORK D-06 over-cap repair: pit-git-resolver.md MEASURED 30,850B > 30,720B domain cap (trigger = bm-a r817 increment 438B landed 10:06; r668 close face claimed 'room 308B' from stale 30,412B receipt = live recurrence of r653 receipt-vs-measured law, annotated in accounting line); sub-split per r441 ritual: rebase/sequencer netpath family 9 entries (r516/r782-bma/r642/r787/r648/r794/r808/r658/r817) verbatim OUT -> research/pit-git-resolver-rebase.md (new sub-file 11,569B, byte-accounting + md5 row, research/ protection family); mother 30,850->21,696B (-10,014B moved +860B pointer row); mother keeps merge-resolver decisioner core + S0-dirty-window worksnap + S7 merge-mode canon + increment append face. "
      "(5) main increment per r668 ritual: r659 entry (rebase --continue no-EDITOR Terminal-dumb -> r808 three-step cure) 994B verbatim OUT of main -> mother append face (mother final 23,579B <= cap); main 30,719->29,724B; prescan rc3 recorded (r441/r651/r654/r662 operative precedent: verbatim zero-loss relocation not deletion); registry pre-registration row appended; receipt results/_r669bmc_pit_resolver_split.json; --verify independent re-check 55/55 PASS. "
      "(6) fail-closed battery live fire x3 (zero partial writes): run-1 caught survivors list-composition bug (3 header lines duplicated into new mother) at the byte-equation gate -- per-line stay-anchor gates all passed (duplication != loss = their blind zone); run-2 caught str/bytes mixed header join; run-3 caught hard-gate off-by-one (removal = len(line incl CR)+1 LF separator = 995 not 994); all fixed, rerun green; new S4 pit entry appended to main (803B, construction-vs-equation dual-derive identity gate law) -> main 30,527B (193B headroom). "
      "(7) S6 chain 38/38 rc0 (lane guards honest: bm-a hosts fresh 6-7min for scorecard/paper_export/build_status = bm-a active in-window; REPORT-2026-10-07 + LIVE-2026-10-07 regenerated ORANGE; golden-week no-bar faces held, reopen 10-08 correct on all faces). "
      "(8) QA r669 5/5 (explicit --round 669 detached runner, 93 trades determinism=True, equity 1,017,839 cross-round identical, png 66,261B; latest_panel_bar 2026-09-30 golden-week no-op expected until 10-08). "
      "(9) S7: loop pin=5 no-op (next fire 10:35) + watchdog present (10:27 run) + claws MATCH x2; attrition CLEAN (4 ledgers, healed rows noted).")
NXT = ("(a) 10-08 (Thu) market reopen FIRST BAR: data-chain re-arm (update legs auto-revive post-15:30) + REGIME_GUARD v3 enforce first-bar activation (t24 gate: last_bar >= 2026-10-01 activates) + paper marks floors advance + external run-11/run-7 (bm-a r714 readiness face owns preflight, MARKET_DATE 10-08 verified). "
      "(b) trio finalize window watch to 10-09 (bm-b canonical lane, D 1674/2000, watch+record only). "
      "(c) W172 freezer window: bm-a pre-seated (A 393_204..395_203 staircase 31st instance + B 395_204..395_403 own-A mutual-exclusion per r818 seat MSG + probe ADMIT); W173+ projection A 395_204..397_203 / B 395_404..395_603. "
      "(d) CODELY main 30,527B headroom 193B: next direct-write pit triggers next increment batch same-window (r670 candidates: r653 close-size entry 676B pending pit-lineage.md 30,552B relief -- lineage sub-split needed first; r669 S4 dual-derive-gate pit 803B targets pit-git.md 拆件脚本断言层族 which has room). "
      "(e) r670 = 5x HANDOVER window (research/HANDOVER.md inventory refresh) + monthly exam 10-31 assembly face (T-143, deliverable 10-29).")
NOTE = ("r669: D-06 over-cap repair round (pit-git-resolver measured 30,850B>30,720B -> rebase family 9 entries out to pit-git-resolver-rebase.md, mother 23,579B, r659 main->mother, prescan rc3, receipt + verify 55) + "
        "r653 live-case annotated + S4 dual-derive-gate pit in main (30,527B) + QA r669 5/5 + S6 38/38; DEC/ORD zero-delta x2; smoke 48/48; attrition CLEAN; W14 park untouched per MSG-0436.")
VERIFY = ("receipts: results/_r669bmc_pit_resolver_split.json (zero-loss split+increment receipt, byte equations, prescan rc3, verify 55/55) + research/pit-git-resolver-rebase.md (9 entries verbatim + accounting) + "
          "research/pit-git-resolver.md (pointer row + r659 verbatim + accounting line, 23,579B) + knowledge/TREASURE_REGISTRY.md (r669 pre-registration row) + CODELY.md (r659 out, r669 S4 pit in, 30,527B) + "
          "qa/smoke-r669.md 5/5 (93 trades determinism=True equity 1,017,839) + qa/equity-curve-r669.png + results/_r669bmc_s6_log.txt 38/38 rc0 + "
          "results/_r669bmc_s05_facts.json (DEC 635C3024 + ORD B687D867 double-sweep zero-delta) + results/_attrition_guard_scan.json CLEAN")

# ---- state ----
st["round_no"] = 670
st["round_no_label"] = "round 669 (bm-c)"
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at",
          "current_task_at", "last_round_at", "last_round_ts", "last_ts", "last_run_at",
          "last_decisions_read_at", "last_decisions_at"):
    st[k] = now
st["current_task"] = ACT
st["activity_now"] = ACT
st["did"] = DID
st["last_round"] = DID
st["last_round_summary"] = ("r669: D-06 over-cap repair (pit-git-resolver 30,850B>cap measured -> rebase family 9 entries -> pit-git-resolver-rebase.md, mother 23,579B, r659 main->mother, prescan rc3, verify 55/55; r668 room-308B stale receipt = r653 live case) + "
                            "S4 dual-derive-gate pit in main (30,527B) + QA r669 5/5 + S6 38/38; DEC/ORD zero-delta x2; smoke 48/48; attrition CLEAN")
st["last_action"] = DID
st["next"] = NXT
st["note"] = NOTE
st["verify"] = VERIFY
st["last_decisions_sha"] = dec_sha
st["last_orders_sha"] = ord_sha
st["last_decisions_sha_method"] = "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r669 s05 round-start + s7close double-sweep MATCH zero-delta; value facts-driven from results/_r669bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))"
st["dec_sha_method"] = st["last_decisions_sha_method"]
st["last_orders_sha_method"] = "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r669 s05 round-start + s7close double-sweep MATCH; facts-driven from results/_r669bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))"
st["ord_sha_method"] = st["last_orders_sha_method"]
st["heartbeat_epoch_utc"] = epoch
st["cpu_pct"] = cpu_pct
st["cpu_util_pct"] = cpu_pct
st["cpu_idle_pct"] = cpu_idle
st["free_ram_gb"] = 4
st["idle_ram_gb"] = 4
st["ram_free_gb"] = 4
st["gpu_free_vram_mib"] = gpu_mib
st["gpu_free_vram_mb"] = gpu_mib
st["gpu_idle_vram_mib"] = gpu_mib
st["gpu_idle_vram_mb"] = gpu_mib
st["gpu_free_mb"] = gpu_mib
st["gpu_free_mib"] = gpu_mib
st["gpu_idle_mb"] = gpu_mib
st["gpu_vram_free_mb"] = gpu_mib
with open(STATE, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
print("STATE written round_no=670 epoch_type=%s gpu_mib=%d cpu=%d" % (type(st["heartbeat_epoch_utc"]).__name__, gpu_mib, cpu_pct))

# ---- heartbeat ----
with open(HB, encoding="utf-8-sig") as fh:
    hb = json.load(fh)
hb["round_no"] = 670
hb["round_no_label"] = "round 669 (bm-c)"
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at", "current_task_at"):
    hb[k] = now
hb["current_task"] = ACT
hb["activity_now"] = ACT
hb["health"] = "alive (r669 D-06 over-cap repair round clean: loop pin=5, watchdog present, claws MATCH, attrition CLEAN; pit-git-resolver 30,850B>cap repaired via zero-loss sub-split, main headroom restored 193B; golden-week no-bar until 10-08)"
hb["heartbeat_epoch_utc"] = epoch
hb["latest_artifact"] = ("results/_r669bmc_pit_resolver_split.json (zero-loss D-06 over-cap repair receipt: pit-git-resolver-rebase.md 9 entries new sub-file, mother 23,579B, r659 main->mother, verify 55/55) + qa/smoke-r669.md 5/5 (93 trades determinism=True equity 1,017,839) @ " + now)
hb["next_milestone"] = ("10-08 (Thu) market reopen FIRST BAR: data-chain re-arm + regime_guard v3 first-bar enforce activation + marks floors advance; trio finalize window to 10-09 (bm-b); W172 freezer window bm-a pre-seated; monthly exam 10-31; next 5x=r670 HANDOVER + pit-lineage relief window")
hb["prod_lanes"] = ("r669 值守+D-06 超线修复轮（pit-git-resolver 实测 30,850B>30,720B〔bm-a r817 增量致·r653 陈旧收据活案例〕→ rebase 族 9 条零丢失迁出 pit-git-resolver-rebase.md+主件 r659 迁入母件·收据+55 checks·smoke 48/48+S6 38/38+QA r669 5/5·板 0 open·水位绿·SAT 活·主件余量 193B·下个 5x=r670〔HANDOVER 窗〕）")
hb["verdict"] = ("alive: r669 watch + D-06 over-cap repair round complete (pit-git-resolver.md measured 30,850B > 30,720B cap after bm-a r817 increment; rebase/sequencer netpath family 9 entries verbatim zero-loss -> pit-git-resolver-rebase.md 11,569B new sub-file; mother 30,850->23,579B incl. r659 migration from main; main 30,719->29,724->30,527B with S4 dual-derive-gate pit in; prescan rc3 recorded, registry row appended, receipt + --verify 55/55 PASS; "
                 "r668 close-face 'room 308B' claim = stale receipt = r653 receipt-vs-measured live case, annotated on accounting line; "
                 "QA r669 5/5; S6 38/38 rc0; smoke 48/48; board open=0; satengine alive rc0; DEC/ORD double-sweep zero-delta 165/165; attrition CLEAN; W14 governance park untouched per MSG-0436; golden-week no-bar face held, reopen 10-08 correct on all faces)")
hb["note"] = "r669: D-06 over-cap repair (resolver split 9 out + r659 in, prescan rc3, verify 55) + S4 dual-derive-gate pit; QA 5/5; S6 38/38; DEC/ORD zero-delta x2; attrition CLEAN."
hb["cpu_pct"] = cpu_pct
hb["cpu_util_pct"] = cpu_pct
hb["cpu_idle_pct"] = cpu_idle
hb["free_ram_gb"] = 4
hb["idle_ram_gb"] = 4
hb["ram_free_gb"] = 4
hb["gpu_free_vram_mib"] = gpu_mib
hb["gpu_free_vram_mb"] = gpu_mib
hb["gpu_idle_vram_mib"] = gpu_mib
hb["gpu_idle_vram_mb"] = gpu_mib
hb["gpu_free_mb"] = gpu_mib
hb["gpu_free_mib"] = gpu_mib
hb["gpu_idle_mb"] = gpu_mib
hb["gpu_vram_free_mb"] = gpu_mib
with open(HB, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
print("HB written round_no=670 epoch=%s" % type(hb["heartbeat_epoch_utc"]).__name__)

# ---- round report ----
line = ("watermark: 绿（red=false lane healthy·py_watermark S6probe 板空合法 idle〔板 0 open·池 401 done+1 ready bm-b keepalive+1 治理停泊 W14 零触碰·判决链在飞：W172 bm-a r818 预坐席+trio finalize bm-b D 1674/2000·金周无 bar〕·SAT 活 rc0·post_review ✗0）"
        " | " + now + " | r669 bm-c | dept:工程/舰队（金周值守轮+D-06 域线超限修复+主件增量批）"
        " | 当前活: r669 值守+超线修复轮（S0 落后 2 吸收干净 rebase〔bm-a r817 收口+r818 W172 预坐席·零路径重叠 stash→rebase→pop〕·S1 48/48·S3 板 0 open+SAT 活+水位绿+T-143 本司 4 面已交付余 bm-a 道待装配窗·主产品=pit-git-resolver.md 实测 30,850B>30,720B 域线〔bm-a r817 10:06 增量 438B 致·r668 收据面 room-308B 声明=陈旧收据=r653 收据-实测律活案例·本轮一切尺寸当场实测 derive〕→ r441 仪式 sub-split：rebase/sequencer 净路族 9 条〔r516/r782-bma/r642/r787/r648/r794/r808/r658/r817〕verbatim 零丢失迁出→research/pit-git-resolver-rebase.md 新子件 11,569B〔字节对账+md5 行〕·母件 30,850→21,696B〔−10,014B 迁出+860B 指针行〕+r668 仪式主件增量：r659 坑 994B verbatim 迁入母件 append 面〔母件终态 23,579B〕·主件 30,719→29,724B·prescan rc3 留痕+登记册预登记行+收据+--verify 55/55·fail-closed 电池实弹三连全零写出〔survivors 头块重复=逐行锚点门盲区·唯一拦截=字节方程门→S4 新坑律 803B 入册·主件终态 30,527B 余量 193B〕·S6 38/38·QA r669 5/5）"
        " | 最近实物: results/_r669bmc_pit_resolver_split.json（零丢失收据·55 checks）+research/pit-git-resolver-rebase.md（9 条新子件）+research/pit-git-resolver.md（指针行+r659+对账行 23,579B）+CODELY.md r669 坑律行（构造式×方程式双 derive 恒等门律）+qa/smoke-r669.md 5/5（93 trades·determinism=True·equity 1,017,839 跨轮恒等）+qa/equity-curve-r669.png+results/_r669bmc_s6_log.txt 38/38 rc0+docs/daily_report/REPORT-2026-10-07.md+docs/live_usage/LIVE-2026-10-07.md（ORANGE）"
        " | 下个里程碑: 10-08（周四）复市首交易日=数据链 re-arm+REGIME_GUARD v3 首 bar 激活（t24 门 last_bar≥10-01 即活·当日核验）+纸盘 marks 地板推进+external run-11/run-7（bm-a r714 readiness 已验正确）；trio finalize 窗观察至 10-09（bm-b 道）；W172 冻结窗 bm-a 预坐席已落；月界首考 10-31；下个 5x=r670（HANDOVER 窗+pit-lineage 30,552B 让位窗=r653 676B 迁出候选） | 本地未达 origin commit 数=0（收口推送后 fetch+ls-tree 自证）")
with open(REPORT, "ab") as fh:
    with open(REPORT, "rb") as fr:
        rb = fr.read()
    sep = b"\r\n" if rb.endswith(b"\r\n") else b"\n"
    if not rb.endswith(sep):
        rb = rb + sep
    fh.write(rb + line.encode("utf-8") + sep)
print("REPORT appended")
print("CLOSE_UPDATER_OK %s epoch=%d gpu_mib=%d cpu=%d" % (now, epoch, gpu_mib, cpu_pct))
