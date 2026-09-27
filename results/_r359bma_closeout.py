# -*- coding: utf-8 -*-
"""r359 bm-a S7 closeout: state round_no +1, heartbeat (fresh epoch/clock at
write per r96 law, epoch as JSON int per R170/R178), round-report ledger
line. Fresh CPU/RAM sample via psutil (compute_audit lineage)."""
import json
import time

now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
now_epoch = int(time.time())
assert isinstance(now_epoch, int)

# fresh machine sample
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1), 1)
    vm = psutil.virtual_memory()
    free_ram_gb = round(vm.available / (1024 ** 3), 1)
except Exception:
    cpu_pct, free_ram_gb = 0.0, 0.0

# ---------- state-bm-a.json ----------
with open("state-bm-a.json", encoding="utf-8") as fh:
    st = json.load(fh)
assert st["round_no"] == 358, f"unexpected round_no {st['round_no']}"
st["round_no"] = 359
st["did"] = ("R359: control-plane defect fix round: S0 fast-forward pull 7a390e1f (bmb r342/343) + "
             "S0.5 orders 96/96 zero-unacked + MSG-2010 resurrected duplicate dedup (identical processed copy; W2-B mirror fix verified on main on_result=_flush L564) "
             "+ decisions D-20260927-04/09 both-executed re-verified in tracked canon (Tools twin deep-scan L28/46/61 + SKILL.md memory-union L35/L43) "
             "+ S3 POOL-ENTRY SILENT LOSS FIXED: CENSUS-FUS-S2-W2B clobbered by bmb r340 network-dead commit 50ea26ef (git -S: add f5822d92 -> remove 50ea26ef, zero intermediate edits; 4 rounds of reports kept saying 'waiting double-dep' describing a row that no longer existed) -> restored VERBATIM from f5822d92, commit 2a687a81 PUSHED, semantic zero-loss verified (79 shared entries byte-identical, only updated_at + W2B row added), MSG-2215 notify sent to bmb "
             "+ local runtime hygiene: .codely-cli classify_conflicts.py twin was stale vs Tools canon (missing bmc r103 catalog+probe-law additions) -> synced, selftest 26/26 "
             "+ S4 pit-law r359 (network-dead whole-file commit swallows shared pool rows; watch-faces must re-verify actual file each round) + CODELY.md 30th-batch hot-cold restructure 14,690B->10,210B <=10KB hard line (10 union-re-materialized rows folded back to pointers verbatim-in-29th-batch + r109bmc/r342bmb/r359bma 3 rows verbatim into 30th-batch section; 27/27 zero-loss audit; double-CR append bug self-caught and fixed in-window, byte-precise archive rebuild) "
             "+ S6 30/30 rc=0 Sunday no-op family zero-masked (+3 new-bar-gated legal skips) + S7 schtasks 4/4 + claw IDENTICAL")
st["verify"] = ("smoke 25/25 + S6 30/30 rc=0 zero-masked + orders 96/96 both scans + post_review 3143 rows 0 unresolved-NO "
                "+ pool restore: 80 entries, W2B deep-equal f5822d92, shared-79 unchanged + CODELY 10,210B<=10,240B "
                "+ archive boundary r355->30th-header clean + classify selftest 26/26 + schtasks 4/4 + claw IDENTICAL")
st["next"] = ("Mon 09-28 09:15 T-91 s3 auto-fire (IntradayMarks 09:25 armed; first bar ~15:30 -> live.paper enforce + t35 verify + exports; sysv1 marks via bm-b BARS evening); "
              "bm-b W2-A finalize re-check + W2-B sequence (D8 receive -> probe once -> run; pool row restored in place); MF/AH EM self-heal watch; council vote-record 09-29 12:00 window close; next 5x=R360 HANDOVER")
st["last_round_at"] = now_iso
st["current_task"] = "r359 closed: W2B pool row restored + CODELY 30th-batch restructure + green S6"
st["updated"] = now_iso
with open("state-bm-a.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)

# ---------- heartbeat ----------
with open("fleet/machines/bm-a.json", encoding="utf-8") as fh:
    hb = json.load(fh)
hb["last_seen"] = now_iso
hb["current_task"] = st["current_task"]
hb["cpu_pct"] = cpu_pct
hb["free_ram_gb"] = free_ram_gb
hb["verdict"] = "loaded_ok_maintenance_green"
hb["heartbeat_epoch_utc"] = now_epoch
hb["clock_read"] = now_iso
hb["round_no"] = 359
hb["round"] = 359
hb["loop_round"] = 359
hb["task"] = "idle-round-done"
with open("fleet/machines/bm-a.json", "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)
# post-write self-proof (smoke F7 face)
with open("fleet/machines/bm-a.json", encoding="utf-8") as fh:
    chk = json.load(fh)
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in chk["clock_read"], "clock_read must be ISO 8601 T-separated"

# ---------- round report ledger line ----------
report = ("2026-09-27" + now_iso[10:] + " | R359 bm-a (dept:总经办·舰队 engineering-governance face) | "
          "WM first-line verdict: GREEN (red=false @21:50 tick; probe 22:02 py 0.3% board-clear legal-idle; audit v2.3 22:02 CLEAN py 0.2% flags=[] load_state pool-supply-gap starvation=false pool_ready=1=W2A-owned-by-bmb) | "
          "did: S0 clean-tree fast-forward pull 7a390e1f (bmb r342/343 W2-A-burn window) + S0.5 orders 96/96 double-scan zero-unacked + inbox MSG-2010 resurrected duplicate dedup (identical processed copy in place; W2-B mirror fix verified on main on_result=_flush L564) + decisions audit: D-20260927-04/09 both-executed re-verified in tracked canon (Tools classify_conflicts.py deep-scan L28/46/61 + SKILL.md memory-union suffix-recipe L35/L43) + S1 smoke 25/25 + S2 board zero-open (job_list empty; tickets all claimed/done; T-91 mine armed) + post_review 3143 rows zero-unresolved-NO + "
          "S3 CLOSED LOOP = control-plane silent-loss defect fixed: CENSUS-FUS-S2-W2B pool entry was DELETED by bmb r340 network-dead local commit 50ea26ef (git log -S evidence: add f5822d92 -> remove 50ea26ef, zero intermediate edits) while bmb-r341/342/343 and my R356-358 reports all kept writing 'W2-B waiting double-dep unchanged' = watch-face describing a row that no longer existed -> restored VERBATIM from f5822d92 (results/_r359bma_pool_restore.py, commit 2a687a81 PUSHED) + semantic zero-loss verify (pool 79->80, shared-79 byte-identical, top-key diff only entries+updated_at) + MSG-20260927-2215-bma-bmb loss+restore+hygiene notify; "
          "+ local runtime hygiene: .codely-cli classify_conflicts.py twin stale vs Tools tracked canon (missing bmc r100-r103 catalog entries+probe laws; SKILL twins already identical) -> synced, selftest 26/26; "
          "+ S4 pit-law r359 appended (network-dead whole-file commit swallows shared control-plane rows; watch-faces must re-verify actual file every round; restore=verbatim from sole authoritative version) + CODELY.md 30th-batch hot-cold restructure (10KB hard line in-window per O-20260927-0230): 14,690B -> 10,210B; 10 union-re-materialized full rows (r96/r345/r100/r350/r101/r340bmb/r351x2/r353/r355, verbatim already in 29th-batch archive, containment re-verified) folded back to pointers + r109bmc/r342bmb/r359bma 3 new rows verbatim into 30th-batch archive section then folded; 27/27 zero-loss audit; pass-1 double-CR append bug (newline=anl translation + explicit anl concat = \\r\\r\\n phantom blanks) self-caught, archive tail rebuilt byte-precise in-window (fixer/fixer2/fixer3 evidence scripts) "
          "+ S6 30/30 rc=0 Sunday no-op family zero-masked (daily 0-new cutoff 09-24 -> live.paper/t35_open_fill/t24_prospect_paper 3 legal gated-skips + regime ORANGE shadow #10 breadth 0.77 + scorecard 6/28/7 + clock CALL-2026-09-24 ORANGE_COOL sleeves=4 activated=0 + lhb <30min-guard no-op + heat weekend + futures/repo/options cutoff-covered zero-network + MF rank 29.3min<30min throttle self-heal + sina_mf covered + lane-guards astock/rev_osc/alloc/fund_premium stdout-no-op + ths same-day idempotent + ah 28min<30min throttle same EM family + fundamental 0.3h fresh-skip + b_layer mask gates pass + t24_promo 0/22 honest NOT-ELIGIBLE legs 0/0/0 + aggr/alloc/grid/sysv1 no-op marks@cutoff T-91 ARMED + t35 export 09-24 regen + daily_scorecard + daily_report REPORT-2026-09-27 faces=4 token=1 + build_status + token_meter L2 1-leg crash-fuse 1) "
          "+ S7 schtasks 4/4 (Loop Running / Watchdog 22:20 / Autofill 22:10 / IntradayMarks Mon 09-28 09:25 Ready = T-91 armed) + claw IDENTICAL "
          "| verify: smoke 25/25 + S6 30/30 rc=0 zero-masked + orders 96/96 both scans + post_review 3143 rows 0-unresolved-NO + pool restore deep-equal+shared-79-unchanged + CODELY 10,210B<=10,240B + archive boundary r355->30th-header clean + classify selftest 26/26 + heartbeat epoch int self-proof "
          "| next: Mon 09-28 09:15 T-91 s3 auto-fire (IntradayMarks 09:25; first bar ~15:30 -> live.paper enforce + t35 open-fill verify + exports; sysv1 marks via bm-b BARS evening); bm-b W2-A finalize re-check + W2-B sequence (D8 receive -> probe once -> run; pool row restored); MF/AH EM self-heal watch; council vote-record 09-29 12:00 window close; next 5x=R360 HANDOVER\n")
with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8", newline="\n") as fh:
    fh.write(report)

print(f"closeout OK: state round 359, heartbeat epoch={now_epoch} int, "
      f"cpu={cpu_pct}% free_ram={free_ram_gb}GB, report line appended")
