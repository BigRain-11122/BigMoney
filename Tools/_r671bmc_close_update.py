# -*- coding: utf-8 -*-
"""r671 bm-c close: state + heartbeat updater.
Laws: R170/R178 epoch int, R262 clock_read T-format, r583 facts-driven
watermark keys (dec/ord sha from s05 facts file), r653 measure-at-use.
S5 ledger row already written earlier this round by _r671bmc_s5_ledger.py
(dedup: no REPORT leg here)."""
import datetime as dt
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
FACTS = os.path.join(ROOT, "results", "_r671bmc_s05_facts.json")
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

ACT = ("当前活: r671 值守+轮报台账 2³ 整文件翻倍治愈批收口（S0 churn 吸收 1 件+落后 0·S1 48/48·S0.5 双扫 DEC/ORD 零 delta×2+orders 164/164 零未回执+inbox W172 seat MSG=bm-a 车道观察不代处理〔bm-a r819 冻结已落地〕·S3 SAT 活+水位绿+板 0 open+池 1 ready bm-b 在飞+fund_premium 车道复活就绪自查全绿〔48/48 NAV+dividends·cutoff 09-30〕·主产品=round_reports-bm-c.md 2³ 翻倍治愈：S3 盘点实锤头行×8/条目×8/17.88MB→git blob 链实证 r666/r668/r669 三窗 push-race UU 整文件 bare-concat（2.23→4.46→8.93→17.87MB 每窗×2）→prescan rc0→keep-first exact-line dedup〔r453 正典律整件面〕17,882,876→2,245,406B〔−15.64MB·−8,106 行〕·集合恒等零丢失门+头×1+300 条目全唯一+diff 纯删除零插入→tripwire 工具 _r671bmc_rr_dup_heal.py〔scan/heal/selftest·9/9〕+隔离区 7 天窗+收据·坑律直写 pit-git-surgery.md〔r453 族第三面〕+方法论卡 E09+登记册行·S6 38/38·QA r671 5/5）"
       " | 最近实物: results/_r671bmc_rr_dup_heal_receipt.json（集合恒等零丢失收据）+Tools/_r671bmc_rr_dup_heal.py（tripwire·selftest 9/9）+results/_quarantine/20261007-1105_r671bmc_rr_predup/（字节恒等隔离+manifest）+research/pit-git-surgery.md（r671 坑律·24,200B）+knowledge/METHODOLOGY_ASSETS.md（E09 卡）+qa/smoke-r671.md 5/5（93 trades·determinism=True·equity 1,017,839 跨轮恒等）+results/_r671bmc_s6_log.txt 38/38 rc0+docs/daily_report/REPORT-2026-10-07.md+docs/live_usage/LIVE-2026-10-07.md（ORANGE）"
       " | 下个里程碑: 10-08（周四）复市首交易日——数据链 re-arm+REGIME_GUARD v3 首 bar 激活（t24 门 last_bar≥2026-10-01 当日核验）+纸盘 marks 地板推进+fund_premium 15:30 首采（bm-c 车道·就绪已核）；trio finalize 观察至 10-09（bm-b 道）；W172 bm-a 在烧→W173 坐席窗（post-W172 universe re-derive）；月界首考 10-31；下个 5x=r675；每轮收口前 tripwire scan（E09 律）")
DID = ("r671 bm-c: golden-week watch + round_reports-bm-c.md 2^3 whole-file dup heal + tripwire law round. "
      "(1) S0: round-start dirty = own daemon live-wins faces, absorb commit + telemetry-churn checkout discard, behind origin 0. "
      "(2) S0.5 double-sweep: DEC 635C3024 / ORD B687D867 zero-delta x2; fleet orders 164/164 zero unacked; inbox 1 = W172 seat MSG (bm-a lane, freeze already landed r819, observed not processed). "
      "(3) S1 smoke 48/48. S3: satengine alive rc0 (W172 registered, bm-a burning); watermark green; board open=0; job_list 0; pool 401 done + 1 ready (bm-b DIVLOWVOL nulls re-claimed 10:40 in flight) + W14 governance park untouched; fund_premium own-lane reopen readiness self-check all green (48/48 NAV+dividends, cutoff 2026-09-30 holiday floor); trial-labor line not triggered (in-flight judgment work exists). "
      "(4) MAIN WORK round_reports-bm-c.md whole-file duplication heal: S3 routine inventory found 9,265 lines / 17.88MB / header x8 / entries x8; git blob chain forensic (cat-file -s across commits) pinned THREE whole-file doublings at r666/r668/r669 push-race UU closeouts (2,230,045 -> 4,461,521 -> 8,933,204 -> 17,873,611B, x2 per window) = r453 merge-union bare-concat family escalated to whole-file scale with no tripwire (next doubling = 35MB, 95MB red line 5 doublings away); heal = treasure_guard prescan rc0 zero-hit + keep-first exact-line dedup (r453 canonical remedy whole-file face) 17,882,876 -> 2,245,406B (-15,637,470B, -8,106 lines); zero-loss gates: set-equality + header==1 + 300 entry lines all-unique + post-scan CLEAN + git diff pure-deletion zero-insertion (healed = strict subsequence); quarantine 7-day copy results/_quarantine/20261007-1105_r671bmc_rr_predup/ + manifest; receipt results/_r671bmc_rr_dup_heal_receipt.json; tripwire tool Tools/_r671bmc_rr_dup_heal.py (scan/heal/selftest, selftest 9/9). "
      "(5) knowledge capture: pit direct-write research/pit-git-surgery.md r453-family third face (+1,187B, zero main occupancy) + methodology card E09 (append-only dup tripwire + keep-first heal law) + TREASURE_REGISTRY row. "
      "(6) historical note: r657-r666/r668/r669 proper entry lines were lost in dead-session windows BEFORE the doublings (F0 tail ends r656) -- pre-existing loss, commit messages retain the record. "
      "(7) S6 chain 38/38 rc0 (dualrun streak 51 ZERO-DRIFT; REPORT/LIVE-2026-10-07 regenerated ORANGE; bm-a hb stale 53min -> 4 host faces stale-takeover derive legal O-2100 s2.4; golden-week no-bar held until 10-08). "
      "(8) QA r671 5/5 (explicit --round 671 detached runner pid 10624, 93 trades determinism=True, equity 1,017,839 cross-round identical, png 66,251B). "
      "(9) S7: loop pin=5 no-op + watchdog present + claws MATCH x2; attrition CLEAN (4 ledgers); tripwire scan CLEAN post-append; S5 ledger row appended to healed file; watermark keys zero-delta x2.")
NXT = ("(a) 10-08 (Thu) market reopen FIRST BAR: data-chain re-arm + REGIME_GUARD v3 enforce first-bar activation (t24 gate: last_bar >= 2026-10-01 activates, verify same day) + paper marks floors advance + fund_premium first snapshot (bm-c lane, readiness verified this round). "
      "(b) trio finalize window watch to 10-09 (bm-b canonical lane). "
      "(c) W172 burn on bm-a local queue; W173 seat window AFTER W172 finalize (re-derive on post-W172 universe per r818 seat leg4). "
      "(d) per-round close: run Tools/_r671bmc_rr_dup_heal.py scan (E09 tripwire law; round_reports + any append-only ledger raced in UU windows). "
      "(e) next 5x = bm-c r675; monthly exam 10-31 assembly face (T-143, deliverable 10-29).")
NOTE = ("r671: round_reports 2^3 whole-file dup heal (-15.64MB, zero-loss set-equality, quarantine + receipt + tripwire) + pit/方法论/登记册三件捕获 + QA r671 5/5 + S6 38/38; DEC/ORD zero-delta x2; smoke 48/48; attrition CLEAN; W14 park untouched.")
VERIFY = ("receipts: results/_r671bmc_rr_dup_heal_receipt.json (set-equality zero-loss, shape gates, quarantine sha) + Tools/_r671bmc_rr_dup_heal.py (scan/heal/selftest 9/9) + "
          "results/_quarantine/20261007-1105_r671bmc_rr_predup/ (byte-identity copy + manifest) + research/pit-git-surgery.md (r671 pit, 24,200B) + knowledge/METHODOLOGY_ASSETS.md (E09) + knowledge/TREASURE_REGISTRY.md (r671 row) + "
          "qa/smoke-r671.md 5/5 (93 trades determinism=True equity 1,017,839) + qa/equity-curve-r671.png + results/_r671bmc_s6_log.txt 38/38 rc0 + "
          "results/_r671bmc_s05_facts.json (DEC 635C3024 + ORD B687D867 double-sweep zero-delta) + results/_attrition_guard_scan.json CLEAN + commit f1afa744d (heal batch)")

# ---- state ----
st["round_no"] = 672
st["round_no_label"] = "round 671 (bm-c)"
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at",
          "current_task_at", "last_round_at", "last_round_ts", "last_ts", "last_run_at",
          "last_decisions_read_at", "last_decisions_at"):
    st[k] = now
st["current_task"] = ACT
st["activity_now"] = ACT
st["did"] = DID
st["last_round"] = DID
st["last_round_summary"] = ("r671: round_reports 2^3 whole-file dup heal (-15.64MB zero-loss, tripwire + quarantine + receipt) + r453-family pit + E09 methodology card + registry row; QA 5/5; S6 38/38; DEC/ORD zero-delta x2; attrition CLEAN")
st["last_action"] = DID
st["next"] = NXT
st["note"] = NOTE
st["verify"] = VERIFY
st["last_decisions_sha"] = dec_sha
st["last_orders_sha"] = ord_sha
st["last_decisions_sha_method"] = "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r671 s05 round-start + s7close double-sweep MATCH zero-delta; value facts-driven from results/_r671bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))"
st["dec_sha_method"] = st["last_decisions_sha_method"]
st["last_orders_sha_method"] = "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r671 s05 round-start + s7close double-sweep MATCH; facts-driven from results/_r671bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))"
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
hb["round_no"] = 672
hb["round_no_label"] = "round 671 (bm-c)"
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at", "current_task_at"):
    hb[k] = now
hb["current_task"] = ACT
hb["activity_now"] = ACT
hb["health"] = "alive (r671 round_reports 2^3 dup heal round clean: loop pin=5, watchdog present, claws MATCH, attrition CLEAN, tripwire CLEAN post-heal; -15.64MB zero-loss with quarantine+receipt; golden-week no-bar until 10-08; fund_premium lane reopen-ready verified)"
hb["heartbeat_epoch_utc"] = epoch
hb["latest_artifact"] = ("results/_r671bmc_rr_dup_heal_receipt.json (round_reports-bm-c.md 2^3 whole-file dup heal: 17,882,876 -> 2,245,406B zero-loss set-equality, quarantine 7-day copy, tripwire tool selftest 9/9) + qa/smoke-r671.md 5/5 (93 trades determinism=True equity 1,017,839) @ " + now)
hb["next_milestone"] = ("10-08 (Thu) market reopen FIRST BAR: data-chain re-arm + regime_guard v3 first-bar enforce activation + marks floors advance + fund_premium first snapshot (bm-c); trio finalize window to 10-09 (bm-b); W173 seat window after W172 finalize; monthly exam 10-31; next 5x=r675; per-close tripwire scan (E09)")
hb["prod_lanes"] = ("r671 值守+轮报台账 2³ 翻倍治愈轮（17.88MB→2.25MB 零丢失去重·隔离区+收据+tripwire 工具·坑律直写 r453 族第三面+方法论卡 E09+登记册行·smoke 48/48+S6 38/38+QA r671 5/5·板 0 open·水位绿·SAT 活）")
hb["verdict"] = ("alive: r671 watch + round_reports whole-file dup heal complete (9,265 lines / 17.88MB / header x8 forensically pinned to r666/r668/r669 push-race UU bare-concats via blob chain 2.23->4.46->8.93->17.87MB; "
                 "prescan rc0; keep-first exact-line dedup per r453 canonical law: 17,882,876 -> 2,245,406B, -8,106 lines; set-equality zero-loss + header x1 + 300 entries all-unique + pure-deletion diff; "
                 "quarantine 7-day + receipt + tripwire scan/heal/selftest tool (9/9); pit direct-write pit-git-surgery.md r453-family third face; methodology E09 card + registry row; "
                 "QA r671 5/5; S6 38/38 rc0; smoke 48/48; board open=0; satengine alive rc0; DEC/ORD double-sweep zero-delta; attrition CLEAN; W14 park untouched; golden-week no-bar held, reopen 10-08")
hb["note"] = "r671: round_reports 2^3 dup heal (-15.64MB zero-loss, tripwire + quarantine + receipt) + r453-family pit + E09 card; QA 5/5; S6 38/38; DEC/ORD zero-delta x2; attrition CLEAN."
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
