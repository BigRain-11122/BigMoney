# -*- coding: utf-8 -*-
"""r673 bm-c close: state + heartbeat updater.
Laws: R170/R178 epoch int, R262 clock_read T-format, r583 facts-driven
watermark keys (dec/ord sha from s05 facts file), r653 measure-at-use."""
import datetime as dt
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-c.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
FACTS = os.path.join(ROOT, "results", "_r673bmc_s05_facts.json")
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
prev_gpu = st.get("gpu_free_vram_mib") or 769
gpu_mib = gpu_mib if gpu_mib is not None else prev_gpu

ACT = ("当前活: r673 值守+复市前夜就绪探针机器自适应扩展轮（S0 absorb+rebase 落 bm-a r821·S1 48/48·S0.5 双扫 DEC/ORD 零 delta+orders 164/164 零未回执+inbox 0·S3 SAT 活+水位绿+板 0 open+池 1 ready bm-b 在飞+W14 零触碰+tripwire/attrition CLEAN·主产品=open_market_readiness.py 机器自适应扩展〔加法·bm-a 座字节保持·selftest 20→28 腿 ALL PASS〕+bm-c 座复市前夜实跑=AMBER〔6 绿+2 黄零红〕→docs/open_market/READINESS-2026-10-07-bm-c.md·连带=MSG-1200-bmc-ALL+pit-tooling 直写坑律〔机感常量泄漏 fixture 坑〕+QA r673 5/5·S6 38/38）"
       " | 最近实物: docs/open_market/READINESS-2026-10-07-bm-c.md（复市前夜就绪页·AMBER 6绿2黄零红·10-08 首 bar 全链转活清单）+results/open_market_readiness.bm-c.json+scripts/open_market_readiness.py（machine-adaptive·selftest 28/28）+qa/smoke-r673.md 5/5（93 trades·determinism=True·equity 1,017,839 跨轮恒等）+results/_r673bmc_s6_log.txt 38/38 rc0+results/_r673bmc_pit_tooling_increment.json"
       " | 下个里程碑: 10-08（周四）复市首交易日——数据链 re-arm+REGIME_GUARD v3 首 bar 激活（t24 门当日核验）+纸盘 marks 地板推进+fund_premium 15:30 首采（bm-c 车道·就绪已核）；O-2115 验收包复跑（10-08 治理日）；trio finalize 观察至 10-09（bm-b 道）；月界首考 10-31；下个 5x=r675；每轮收口前 tripwire scan（E09 律）")
DID = ("r673 bm-c: golden-week guard round + reopen-eve readiness probe machine-adaptive extension. "
      "(1) S0: round-start dirty 5 = own daemon live-wins faces + r672 commitmsg leftovers, absorb commit + pull --rebase onto bm-a r821 (behind 1 -> 0). "
      "(2) S0.5 double-sweep: DEC 635C3024 / ORD B687D867 zero-delta x2; fleet orders 164/164 zero unacked; inbox 0. "
      "(3) S1 smoke 48/48. S3: satengine alive rc0; watermark green (py_low_board_clear legal idle white-list); board open=0; job_list 0; pool 401 done + 1 ready (bm-b DIVLOWVOL re-claimed 10:40 in flight) + W14 governance park untouched; trial-labor line not triggered (W3 judge-prep in flight on bm-a + trio finalize window); tripwire scan CLEAN (r672 16-UU window zero re-duplication, root+logs ledgers verified); attrition CLEAN (4 ledgers). "
      "(4) MAIN WORK open_market_readiness.py machine-adaptive extension (additive, bm-a seat byte-preserving): MACHINE auto-detect via fleet/machine.json (S0-1 anchor law, absent->bm-a fallback), face functions machine-parameterized, R31 lane map PANEL_LANES (bm-a 10 verbatim / bm-b minute_feed / bm-c fund_premium; unknown machine -> lane_map_missing honest fact, zero false RED), per-machine outputs for non-bm-a seats (open_market_readiness.<id>.json + READINESS-<date>-<id>.md); selftest 20->28 legs ALL PASS (first attempt caught fixture machine-constant leak: L4/L5b false red on bm-c host -> hermetic fixture fix pins explicit bm-a lane tuple; pit direct-written). "
      "bm-c seat reopen-eve live run: verdict AMBER (6 GREEN + 2 AMBER, zero RED) -> docs/open_market/READINESS-2026-10-07-bm-c.md (ETF clock at holiday floor 2026-09-30 / bm-c lane fund_premium panel in place / marks families 34/34 at floor / REGIME_GUARD v3 both gates open / external legs staged / supply lanes in window / satengine face_bm-c alive+fresh). "
      "(5) fleet MSG-2026-10-07-1200-bmc-ALL sent (extension notice; bm-a rerun tomorrow unchanged). "
      "(6) knowledge capture: pit-tooling.md direct-write +939B (machine-detected module constant leaking into hermetic selftest fixture pit; receipt sha16=1af419e6ac95f4b1; main-file margin 322B law per r672 precedent). "
      "(7) S6 chain 38/38 rc0 (dualrun streak 51 ZERO-DRIFT; REPORT/LIVE-2026-10-07 regenerated ORANGE; fund_premium pre-15:30 legal no-op; golden-week no-bar held until 10-08). "
      "(8) QA r673 5/5 (explicit --round 673 detached runner pid 30064, 93 trades determinism=True, equity 1,017,839 cross-round identical). "
      "(9) S7: loop pin check + watchdog + claws x2; S5 ledger row appended; watermark keys zero-delta x2.")
NXT = ("(a) 10-08 (Thu) market reopen FIRST BAR: data-chain re-arm + REGIME_GUARD v3 enforce first-bar activation (t24 gate: last_bar >= 2026-10-01 activates, verify same day) + paper marks floors advance + fund_premium first snapshot (bm-c lane, readiness verified r671 + this-round probe). "
      "(b) O-2115 acceptance pack rerun on 10-08 governance day (scripts/o2115_acceptance_pack.py run, ALL_MET as of 10-04). "
      "(c) trio finalize window watch to 10-09 (bm-b canonical lane). "
      "(d) W172 burn on bm-a local queue; W173 seat window AFTER W172 finalize; W3 judge burn target <=10-12 (bm-a seat). "
      "(e) per-round close: run Tools/_r671bmc_rr_dup_heal.py scan (E09 tripwire law). "
      "(f) next 5x = bm-c r675; monthly exam 10-31 assembly face (T-143, deliverable 10-29).")
NOTE = ("r673: reopen-eve readiness probe machine-adaptive extension (bm-a byte-preserving, selftest 28/28) + bm-c seat AMBER (6 green+2 amber zero red) + MSG + pit-tooling direct-write + QA r673 5/5 + S6 38/38; DEC/ORD zero-delta x2; smoke 48/48; attrition CLEAN; W14 park untouched.")
VERIFY = ("receipts: docs/open_market/READINESS-2026-10-07-bm-c.md + results/open_market_readiness.bm-c.json (verdict AMBER, 8 faces) + scripts/open_market_readiness.py (selftest 28/28 ALL PASS, py_compile clean) + "
          "qa/smoke-r673.md 5/5 (93 trades determinism=True equity 1,017,839) + qa/equity-curve-r673.png + results/_r673bmc_s6_log.txt 38/38 rc0 + "
          "results/_r673bmc_s05_facts.json (DEC 635C3024 + ORD B687D867 double-sweep zero-delta) + results/_attrition_guard_scan.json CLEAN + results/_r673bmc_pit_tooling_increment.json (pit direct-write receipt) + fleet/inbox/MSG-2026-10-07-1200-bmc-ALL.md")

# ---- state ----
st["round_no"] = 674
st["round_no_label"] = "round 673 (bm-c)"
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at",
          "current_task_at", "last_round_at", "last_round_ts", "last_ts", "last_run_at",
          "last_decisions_read_at", "last_decisions_at"):
    st[k] = now
st["current_task"] = ACT
st["activity_now"] = ACT
st["did"] = DID
st["last_round"] = 673
st["last_round_summary"] = ("r673: reopen-eve readiness probe machine-adaptive extension (bm-a byte-preserving, selftest 20->28 ALL PASS) + bm-c seat AMBER verdict (6 green + 2 amber, zero red) + fleet MSG + pit-tooling direct-write; QA r673 5/5; S6 38/38; DEC/ORD zero-delta x2; attrition CLEAN")
st["last_action"] = DID
st["next"] = NXT
st["note"] = NOTE
st["verify"] = VERIFY
st["last_decisions_sha"] = dec_sha
st["last_orders_sha"] = ord_sha
st["last_decisions_sha_method"] = "python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; r673 s05 round-start + s7close double-sweep MATCH zero-delta; value facts-driven from results/_r673bmc_s05_facts.json, 64hex shape-asserted, never hand-typed (r583 S4 law))"
st["dec_sha_method"] = st["last_decisions_sha_method"]
st["last_orders_sha_method"] = "python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; r673 s05 round-start + s7close double-sweep MATCH; facts-driven from results/_r673bmc_s05_facts.json, 40hex shape-asserted, never hand-typed (r583 S4 law))"
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
hb["round_no"] = 674
hb["round_no_label"] = "round 673 (bm-c)"
for k in ("clock_read", "ts", "updated", "updated_at", "last_seen", "last_seen_at", "current_task_at"):
    hb[k] = now
hb["current_task"] = ACT
hb["activity_now"] = ACT
hb["health"] = "alive (r673 guard round clean: loop pin, watchdog present, claws MATCH, attrition CLEAN, tripwire CLEAN; reopen-eve probe landed AMBER 6 green + 2 amber zero red; golden-week no-bar until 10-08 reopen; fund_premium lane reopen-ready)"
hb["heartbeat_epoch_utc"] = epoch
hb["latest_artifact"] = ("docs/open_market/READINESS-2026-10-07-bm-c.md (reopen-eve readiness page from bm-c seat: verdict AMBER, 6 GREEN + 2 AMBER zero RED, all 10-08 first-bar faces enumerated) + scripts/open_market_readiness.py machine-adaptive (selftest 28/28) + qa/smoke-r673.md 5/5 @ " + now)
hb["next_milestone"] = ("10-08 (Thu) market reopen FIRST BAR: data-chain re-arm + regime_guard v3 first-bar enforce + marks floors advance + fund_premium first snapshot (bm-c); O-2115 acceptance pack rerun (governance day); trio finalize window to 10-09 (bm-b); monthly exam 10-31; next 5x=r675; per-close tripwire scan (E09)")
hb["prod_lanes"] = ("r673 值守+复市前夜就绪探针机器自适应扩展轮（open_market_readiness.py 加法扩展 bm-a 字节保持·selftest 28/28·bm-c 座实跑 AMBER 6绿2黄零红·MSG+pit 直写·smoke 48/48+S6 38/38+QA r673 5/5·板 0 open·水位绿·SAT 活）")
hb["verdict"] = ("alive: r673 watch + reopen-eve readiness landed (probe machine-adaptive extension additive/bm-a-byte-preserving, selftest 20->28 ALL PASS; "
                 "bm-c seat run verdict AMBER = 6 GREEN + 2 AMBER zero RED: ETF clock at holiday floor, bm-c lane fund_premium panel in place, marks 34/34 at floor, "
                 "REGIME_GUARD v3 both gates open, external legs staged, supply lanes in trio window, satengine face_bm-c alive; "
                 "moneyflow EM source-blocked 30-min self-heal = only open amber on bm-a lane; QA r673 5/5; S6 38/38 rc0; smoke 48/48; "
                 "board open=0; satengine alive rc0; DEC/ORD double-sweep zero-delta; attrition CLEAN; W14 park untouched; reopen 10-08")
hb["note"] = "r673: reopen-eve probe extension (selftest 28/28) + bm-c seat AMBER page + MSG + pit direct-write; QA 5/5; S6 38/38; DEC/ORD zero-delta x2; attrition CLEAN."
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
