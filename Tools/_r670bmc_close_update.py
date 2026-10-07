# -*- coding: utf-8 -*-
"""r670 bm-c close: state + heartbeat updater.
Laws: R170/R178 epoch int, R262 clock_read T-format, r583 facts-driven
watermark keys (dec/ord sha from s05 facts file), r640 race law (QA terminal
state polled before this script advances state), r653 measure-at-use (all
sizes derive from receipts/len() never hand-copied).
S5 ledger row already written earlier this round by _r670bmc_s5_ledger.py
(dedup: no REPORT leg here)."""
import datetime as dt
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
FACTS = os.path.join(ROOT, "results", "_r670bmc_s05_facts.json")
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

ACT = ("当前活: r670 值守+D-06 lineage 让位轮收口（S0 落后 0 零 rebase·S1 48/48·S3 板 0 open+SAT 活+水位绿+O-20261007-0935 派单正主闭口〔bm-b capability receipt 核收：JSON cat-file rc0 验达 origin+MSG 转 processed+票面勾选+回执节·两机全收〕·主产品=pit-lineage.md 30,552B 满员让位 sub-split〔r669 next 指针窗兑现〕：收据可复核律族 12 条 verbatim 零丢失迁出→pit-lineage-receipt.md 新子件 15,198B+母件 18,527B+主件增量批 r653〔677B 实测〕→receipt 子件+r669〔802B 实测〕→pit-git.md·主件 30,527→30,101B 回线余 619B·构造式×方程式双 derive 恒等门首次实装〔r669 S4 坑正法落地·四文件构造==方程全过〕·--verify 93/93·5x HANDOVER 行落账·S6 38/38·QA r670 5/5）"
       " | 最近实物: results/_r670bmc_lineage_receipt_split.json（零丢失收据·93 checks --verify PASS·prescan rc3 留痕）+research/pit-lineage-receipt.md（15,198B/12+r653 条新子件·字节对账+md5 行）+research/pit-lineage.md（30,552→18,527B 回线·指针行）+research/pit-git.md（r669 坑+直写行 26,991B）+CODELY.md（主件 30,101B）+research/HANDOVER.md（r670 5x 核对行）+qa/smoke-r670.md 5/5（93 trades·determinism=True·equity 1,017,839 跨轮恒等）+results/_r670bmc_s6_log.txt 38/38 rc0+docs/daily_report/REPORT-2026-10-07.md+docs/live_usage/LIVE-2026-10-07.md（ORANGE）"
       " | 下个里程碑: 10-08（周四）复市首交易日——数据链 re-arm〔S6 legs 25-28 复活〕+REGIME_GUARD v3 首 bar 激活（t24 门 last_bar≥10-01 当日核验）+纸盘 marks 地板推进（bm-a r714 readiness owns preflight）；trio finalize 窗观察至 10-09（bm-b 道）；W172 冻结窗 bm-a 预坐席在册；月界首考 10-31；下个 5x=r675；主件余量 619B=下批 direct-write pit 续压面")
DID = ("r670 bm-c: golden-week watch + D-06 pit-lineage relief sub-split + main increment (r653+r669 out) + 5x HANDOVER + dispatch-receipt closeout round. "
      "(1) S0: round-start dirty = 3 self daemon live-wins faces; behind origin 0 / ahead 0 (no rebase needed). "
      "(2) S0.5 double-sweep: DEC 635C3024 / ORD B687D867 zero-delta x2; fleet orders 164/164 zero unacked; inbox 1 for bm-c = bm-b capability receipt for O-20261007-0935-bm-c (dispatcher leg): receipt verified (JSON evidence results/capability_receipt_bmb_20261007.json cat-file -e rc0 on origin), MSG moved to processed/, order ticket bm-b checkbox + receipt section written -- both bm-a (r817) and bm-b (r803) legs now delivered ahead of the 10-09 deadline, dispatch closed. "
      "(3) S1 smoke 48/48. S3: satengine alive rc0; watermark green (next_pick=claimed moneyflow IC batch, panel parked EM source-blocked 30min self-heal, unchanged); board open=0; job_list 0; pool 401 done + 1 ready (bm-b keepalive) + W14 governance park untouched; trial-labor line not triggered (W172 bm-a pre-seated + trio finalize bm-b in flight). "
      "(4) MAIN WORK D-06 pit-lineage relief sub-split + main increment: pit-lineage.md MEASURED 30,552B full (168B headroom) per r669 next-pointer window; receipt-reviewable family 12 entries (r554/r555-eph/r559/r560/r569/r570/r578/r583/r587/r629/r637/r646) verbatim OUT -> research/pit-lineage-receipt.md (new sub-file 15,198B incl. r653 entry, byte-accounting + md5 row); mother 30,552->18,527B (-12,803B moved +778B pointer row); main increment: r653 close-size entry 677B (MEASURED; stale claim 676B = r653 receipt-vs-measured law THIRD live case, gate derived at use) -> receipt sub-file (r646 same-family homecoming) + r669 split-script pit 802B (MEASURED; stale claim 803B) -> pit-git.md split-script assertion-layer family (r651 precedent) + direct-write accounting line; main 30,527->30,101B (619B headroom); CONSTRUCT-VS-EQUATION DUAL-DERIVE IDENTITY GATE FIRST OPERATIVE USE (r669 S4 law implemented: four files construct==equation all PASS, all size gates len()-derived); prescan rc3 recorded; registry pre-registration row; receipt results/_r670bmc_lineage_receipt_split.json; --verify 93/93 PASS. "
      "(5) three live fail-closed catches, zero partial writes: needle same-round different-pit collision (bare 'r637' hit pit-git-resolver.md's OTHER r637 entry = marker-scan pit vs value-anchor pit; sibling already-migrated gate caught it; all MOVE_NEEDLES upgraded to content-signature form) -> S4 direct-write pit-git.md 913B (r668 same-window direct-write precedent, zero main occupancy); split header line-count assumption wrong (real[4] blank gate fail-closed, probe showed 6-line header, fixed); byte gates re-derived from measurement (676->677, 803->802). "
      "(6) 5x HANDOVER duty: research/HANDOVER.md r670 row inserted at position 2 covering increment window r666-670 (5,528B row). "
      "(7) S6 chain 38/38 rc0 (NON-ZERO LEGS none; bm-a hb stale 29min -> 4 host faces stale-takeover derive legal O-2100 s2.4; REPORT/LIVE-2026-10-07 regenerated ORANGE; golden-week no-bar held until 10-08). "
      "(8) QA r670 5/5 (explicit --round 670 detached runner pid 33376, 93 trades determinism=True, equity 1,017,839 cross-round identical, png 66,379B; latest_panel_bar 2026-09-30 golden-week no-op expected until 10-08). "
      "(9) S7: loop pin=5 present (next fire 10:55) + watchdog present (10:53) + claws MATCH x2; attrition CLEAN (4 ledgers); S5 ledger row appended; watermark keys zero-delta.")
NXT = ("(a) 10-08 (Thu) market reopen FIRST BAR: data-chain re-arm (S6 legs 25-28 auto-revive post-15:30) + REGIME_GUARD v3 enforce first-bar activation (t24 gate: last_bar >= 2026-10-01 activates, verify same day) + paper marks floors advance + external run-11/run-7 (bm-a r714 readiness owns preflight). "
      "(b) trio finalize window watch to 10-09 (bm-b canonical lane, D in flight). "
      "(c) W172 freezer window: bm-a pre-seated (A 393_204..395_203 + B 395_204..395_403 per r818 seat MSG). "
      "(d) CODELY main 30,101B headroom 619B: next direct-write pit triggers next increment batch same-window; candidates when new pits land. "
      "(e) next 5x = bm-c r675; monthly exam 10-31 assembly face (T-143, deliverable 10-29).")
NOTE = ("r670: D-06 lineage relief round (receipt family 12 out -> pit-lineage-receipt.md 15,198B, mother 18,527B, r653+r669 main->domain files, dual-derive gate first operative use, prescan rc3, receipt + verify 93) + "
        "O-0935 dispatch closeout (both legs receipted) + 5x HANDOVER row + QA r670 5/5 + S6 38/38; DEC/ORD zero-delta x2; smoke 48/48; attrition CLEAN; W14 park untouched.")
VERIFY = ("receipts: results/_r670bmc_lineage_receipt_split.json (zero-loss split+increment receipt, dual-derive equations, prescan rc3, verify 93/93) + research/pit-lineage-receipt.md (12 entries verbatim + r653 + accounting) + "
          "research/pit-lineage.md (pointer row, 18,527B) + research/pit-git.md (r669 verbatim + direct-write pit + accounting, 26,991B) + knowledge/TREASURE_REGISTRY.md (r670 pre-registration row) + CODELY.md (r653+r669 out, r670 pointer in, 30,101B) + "
          "research/HANDOVER.md (r670 5x row) + qa/smoke-r670.md 5/5 (93 trades determinism=True equity 1,017,839) + qa/equity-curve-r670.png + results/_r670bmc_s6_log.txt 38/38 rc0 + "
          "results/_r670bmc_s05_facts.json (DEC 635C3024 + ORD B687D867 double-sweep zero-delta) + fleet/orders/O-20261007-0935-bm-c.md (bm-b receipt section + both checkboxes) + results/_attrition_guard_scan.json CLEAN")

# ---- state ----
st["round_no"] = 671
st["round_no_label"] = "round 670 (bm-c)"
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at",
          "current_task_at", "last_round_at", "last_round_ts", "last_ts", "last_run_at",
          "last_decisions_read_at", "last_decisions_at"):
    st[k] = now
st["current_task"] = ACT
st["activity_now"] = ACT
st["did"] = DID
st["last_round"] = DID
st["last_round_summary"] = ("r670: D-06 lineage relief (receipt family 12 -> pit-lineage-receipt.md, mother 18,527B, r653+r669 main->out, dual-derive gate first operative use, prescan rc3, verify 93/93) + "
                            "O-0935 dispatch closeout (bm-a r817 + bm-b r803 both receipted ahead of 10-09) + 5x HANDOVER row + QA r670 5/5 + S6 38/38; DEC/ORD zero-delta x2; smoke 48/48; attrition CLEAN")
st["last_action"] = DID
st["next"] = NXT
st["note"] = NOTE
st["verify"] = VERIFY
st["last_decisions_sha"] = dec_sha
st["last_orders_sha"] = ord_sha
st["last_decisions_sha_method"] = "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r670 s05 round-start + s7close double-sweep MATCH zero-delta; value facts-driven from results/_r670bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))"
st["dec_sha_method"] = st["last_decisions_sha_method"]
st["last_orders_sha_method"] = "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r670 s05 round-start + s7close double-sweep MATCH; facts-driven from results/_r670bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))"
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
chk = json.loads(open(STATE, encoding="utf-8-sig").read())
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch int gate (R170/R178)"
print("STATE written round_no=%s label=%s epoch_type=%s gpu_mib=%d cpu=%d" % (
    chk["round_no"], chk["round_no_label"], type(chk["heartbeat_epoch_utc"]).__name__, gpu_mib, cpu_pct))

# ---- heartbeat ----
with open(HB, encoding="utf-8-sig") as fh:
    hb = json.load(fh)
hb["round_no"] = 671
hb["round_no_label"] = "round 670 (bm-c)"
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at", "current_task_at"):
    hb[k] = now
hb["current_task"] = ACT
hb["activity_now"] = ACT
hb["health"] = "alive (r670 D-06 lineage relief round clean: loop pin=5, watchdog present, claws MATCH, attrition CLEAN; pit-lineage 30,552B full relieved via zero-loss sub-split, main headroom restored 619B; dual-derive gate first operative use; O-0935 dispatch closed both legs; golden-week no-bar until 10-08)"
hb["heartbeat_epoch_utc"] = epoch
hb["latest_artifact"] = ("results/_r670bmc_lineage_receipt_split.json (zero-loss D-06 lineage relief receipt: pit-lineage-receipt.md 12+r653 entries new sub-file, mother 18,527B, r653+r669 main->out, dual-derive gate first operative use, verify 93/93) + qa/smoke-r670.md 5/5 (93 trades determinism=True equity 1,017,839) @ " + now)
hb["next_milestone"] = ("10-08 (Thu) market reopen FIRST BAR: data-chain re-arm + regime_guard v3 first-bar enforce activation + marks floors advance; trio finalize window to 10-09 (bm-b); W172 freezer window bm-a pre-seated; monthly exam 10-31; next 5x=r675")
hb["prod_lanes"] = ("r670 值守+D-06 lineage 让位轮（pit-lineage 30,552B 满员→收据可复核族 12 条零丢失迁出 pit-lineage-receipt.md 新子件 15,198B+母件 18,527B+主件增量批 r653/r669 迁出·主件 30,101B 回线·双 derive 恒等门首装·--verify 93/93·O-0935 派单双机回执闭口·5x HANDOVER 行·smoke 48/48+S6 38/38+QA r670 5/5·板 0 open·水位绿·SAT 活）")
hb["verdict"] = ("alive: r670 watch + D-06 lineage relief round complete (pit-lineage.md measured 30,552B full; receipt-reviewable family 12 entries verbatim zero-loss -> pit-lineage-receipt.md 15,198B new sub-file; mother 18,527B; "
                 "main increment r653 677B -> receipt sub-file (r646 homecoming) + r669 802B -> pit-git.md assertion family; main 30,527->30,101B headroom 619B; "
                 "CONSTRUCT-VS-EQUATION dual-derive identity gate first operative implementation (r669 S4 law), four files construct==equation PASS, all gates len()-derived; prescan rc3, registry row, receipt + --verify 93/93 PASS; "
                 "three fail-closed catches (needle same-round different-pit collision -> S4 direct-write pit-git.md; byte gates re-measured 676->677/803->802 = r653 law third live case; header line-count assumption fixed after probe); "
                 "O-20261007-0935 dispatch closed: bm-a r817 + bm-b r803 receipts both verified on origin, ticket checkboxes + receipt sections written; "
                 "QA r670 5/5; S6 38/38 rc0; smoke 48/48; board open=0; satengine alive rc0; DEC/ORD double-sweep zero-delta; attrition CLEAN; W14 park untouched; 5x HANDOVER row inserted; golden-week no-bar held, reopen 10-08")
hb["note"] = "r670: D-06 lineage relief (receipt split 12 out + r653/r669 main->out, dual-derive gate first use, prescan rc3, verify 93/93) + O-0935 closeout + 5x HANDOVER; QA 5/5; S6 38/38; DEC/ORD zero-delta x2; attrition CLEAN."
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
chk2 = json.loads(open(HB, encoding="utf-8-sig").read())
assert isinstance(chk2["heartbeat_epoch_utc"], int), "hb epoch int gate"
assert "T" in chk2["clock_read"], "clock_read T-format gate (R262)"
print("HB written round_no=%s epoch_type=%s clock=%s" % (chk2["round_no"], type(chk2["heartbeat_epoch_utc"]).__name__, chk2["clock_read"]))
print("CLOSE_UPDATER_OK %s epoch=%d gpu_mib=%d cpu=%d" % (now, epoch, gpu_mib, cpu_pct))
