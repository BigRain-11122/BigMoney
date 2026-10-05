# r747 bm-b round bookkeeping: state.json round_no+1, heartbeat, round report line
# (r741 two-step read/write; r743 binary-tail verify for GBK-contaminated ledger)
import json, io, time, datetime

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:]
epoch = int(time.time())

# --- state.json (two-step: read fully, mutate, write fully) ---
sp = io.open(ROOT + r"\state.json", encoding="utf-8")
st = json.load(sp)
sp.close()
assert st["round_no"] == 746, "round_no continuity breach: %r" % st["round_no"]
st["round_no"] = 747
st["round_no_label"] = "r747"
st["round_no_gap_note"] = "none; r744 dead-tail (complete bookkeeping, missing close commit) absorbed at r745 S0 via churn ec6e03faf; r745/r746/r747 = clean sequential +1"
st["clock_read"] = iso
st["ts"] = iso
st["updated"] = iso
st["last_seen"] = iso
st["last_round_at"] = iso
st["last_round_ts"] = iso
st["next"] = ("(a) per-family nulls finalize as trio hits 2000/2000: V 1561 now "
              "(recent ~0.35/min -> ETA ~10-06 evening, fluctuates), Q 1273 (~10-07), "
              "D 1037 (~10-08) -- leg39 probe every round")
st["note"] = ("r747: steady-state golden-week round -- S0 churn-absorb 0116d77d3 + clean "
              "auto-merge origin/main (7 behind, zero UU) single-push 0/0; orders 154/154 "
              "zero diff; D-19 decisions sha MATCH D14DCC74872A599 (canonical Tools/d19_check.py; "
              "ad-hoc r677 orders face false ORDERS_MATCH=False = SHA-1-vs-SHA-256 algorithm "
              "mismatch, dual-hash verified content-unchanged E79E15F9, r537 law applied, zero "
              "consumption error); S1 smoke 48/48")
sp = io.open(ROOT + r"\state.json", "w", encoding="utf-8")
json.dump(st, sp, ensure_ascii=False, indent=1)
sp.close()
# reparse + assert
rp = json.load(io.open(ROOT + r"\state.json", encoding="utf-8"))
assert rp["round_no"] == 747

# --- heartbeat fleet/machines/bm-b.json ---
hp = io.open(ROOT + r"\fleet\machines\bm-b.json", encoding="utf-8")
hb = json.load(hp)
hp.close()
hb["last_seen"] = iso
hb["clock_read"] = iso
hb["heartbeat_epoch_utc"] = epoch  # JSON int type per R170/R178 law
hb["current_task"] = ("steady-state golden-week round r747: FUND trio NULLS burns supervision "
                      "(V1561/Q1273/D1037 of 2000) + S6 39-leg product chain all rc0")
hb["cpu_cores"] = 16
hb["free_ram_gb"] = 3.7
hb["gpu_free_vram_gb"] = 3.3
hb["verdict"] = "healthy: trio burns in flight (autofill+workers), board empty, RAM <4GB heavy gate = zero new burn drafting"
sp = io.open(ROOT + r"\fleet\machines\bm-b.json", "w", encoding="utf-8")
json.dump(hb, sp, ensure_ascii=False, indent=1)
sp.close()
rp = json.load(io.open(ROOT + r"\fleet\machines\bm-b.json", encoding="utf-8"))
assert isinstance(rp["heartbeat_epoch_utc"], int), "epoch must be int (R170/R178 law)"

# --- round report line (append; GBK-contaminated 1.4MB ledger -> binary append + tail verify) ---
line = (
    "2026-10-05T21:58:00+08:00 | round 747 (bm-b, dept:engineering, golden-week steady-state round) | "
    "[watermark verdict: GREEN (red=false lane healthy; satengine alive rc0 idle 0; board 0 open-unclaimed; "
    "trio in-flight = trial-labor line satisfied; RAM 3.7GB < 4GB heavy gate = zero new burn drafting per fleet discipline)] | "
    "CEO three-line: current-work = FUND trio NULLS burns V1561/Q1273/D1037 of 2000 (+19/+17/+15 vs r746, autofill+workers alive, ~30 py procs) | "
    "latest-artifact = results/_r747bmb_s6_chain.log (39 legs ALL rc0 21:48-21:55, lineage r746 verbatim legdiff 3 label lines only) "
    "+ docs REPORT/LIVE-2026-10-05 regen 21:52 | "
    "next-milestone = trio V finalize ~10-06 evening @~0.35/min (fluctuates), Q ~10-07, D ~10-08; "
    "D-06 group closeout 10-07 12:00; market reopen 10-08 (REGIME_GUARD v3 first new bar) | "
    "S0: churn-absorb 0116d77d3 (8 daemon faces: autofill/satengine/fund-nulls) -> merge origin/main behind-7 clean auto-merge 28dba9152 "
    "ZERO-UU (bm-a W138 n1 results + 12 shard pool churn + bm-c close chains absorbed) -> single-push LANDED 31bfdd5f5..28dba9152 "
    "post-push fetch+rev-list 0/0 self-verified | "
    "S0.5: orders 154/154 head-scan zero unacked (README.md non-order excluded); D-19 decisions sha MATCH D14DCC74872A599 "
    "(canonical Tools/d19_check.py rc0; ad-hoc r677 script ORDERS face false-alarm = SHA-1-vs-SHA-256 mismatch, "
    "dual-algorithm verified content-unchanged E79E15F9, r537 law applied in-round, zero consumption error) | inbox 0 | "
    "S1 smoke 48/48 | S3: engine alive queue_depth=0; watermark next_pick claimed-advisory; "
    "RAM 3.7GB < 4GB heavy gate = zero new burn drafting (fleet discipline); W14-GENERATE waiting RAM-gate legitimate | "
    "S6: dualrun ZERO-DRIFT streak 40 (403 entries); compute_audit CLEAN (burning-healthy py 62-100%, pool_ready 3/3, "
    "parallel_eff 12.99 eff cores, zero flags); py_watermark insufficient_history n=1 (local_batch_running=true = legal burn face); "
    "leg39 VERDICT mechanical_ready=False (G1 burn F, G2 T, G3 T, G4 PENDING r638 armed; window 10-05..10-09) | "
    "S7 quartet 4/4 (IterationLoop pin=2 no-op first-fire 22:02; watchdog idempotent -Force re-register 21:58 harmless; "
    "precommit+prepush claws LF-normalized install match) + attrition guard CLEAN (4 ledgers, healed rows historical) | "
    "product score 2 (S6 product chain 39 rc0 + trio burn advance + CEO faces regen)\n"
)
marker = "round 747 (bm-b"
raw = io.open(ROOT + r"\logs\iteration-loop\round_reports.md", "rb").read()
assert marker.encode("utf-8") not in raw, "round 747 line already present (double-append guard)"
assert raw.endswith(b"\n") or raw.endswith(b"\r\n"), "ledger tail not newline-terminated"
with io.open(ROOT + r"\logs\iteration-loop\round_reports.md", "ab") as f:
    f.write(line.encode("utf-8"))
# binary-tail verify (r743 law: no full-file decode on GBK-contaminated ledger)
raw2 = io.open(ROOT + r"\logs\iteration-loop\round_reports.md", "rb").read()
assert raw2.count(marker.encode("utf-8")) == 1, "append count != 1"
assert raw2 == raw + line.encode("utf-8"), "append not byte-exact"
print("bookkeeping OK: state 747, heartbeat epoch int %d, report line appended+verified" % epoch)
