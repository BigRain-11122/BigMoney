# -*- coding: utf-8 -*-
"""r90 bm-c S5: round report line + state-bm-c.json + heartbeat (bm-c only files).
Fresh clock read at write time (time-honesty law)."""
import io, json, time, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + ("+" if now.utcoffset() >= datetime.timedelta(0) else "-") + now.strftime("%H:%M").lstrip("0") if False else now.isoformat(timespec="seconds")
epoch = int(time.time())

report_line = (
    "2026-09-27T16:57:00+08:00｜R90 bm-c S0-FOLD MISSION COMPLETE (inherited r89 plan) | "
    "keepalive micro-commit 193a8a56 staged-in pre-fold (r332 zero-discard law) -> wave-1 rebase 6-pick onto origin/main+9: "
    "pick-1 14-UU (archive suffix-concat coexist 885817B / CODELY entry-union mine+1 / autofill 46|46 composite / take-new family) "
    "+ pick-3 autofill 1-UU + pick-4 14-UU (paper family coupled-side ours) + pick-5 CODELY swap-union pick "
    "(mid-flight two fixes: mine_new pointer-family guard relax + auto-merged-archive stage-empty -> worktree fallback law; "
    "2 fulls r87/r88-bmc swapped to pointers verbatim-in-archive-asserted, 3 dup pointers dropped keep origin's, 9683B<10KB) "
    "+ pick-6 autofill empty-skip (content absorbed zero-loss) -> push rejected origin+2 (bm-a r337 census burn C8-launch + tick claim) "
    "-> wave-2 rebase 5-pick: pick-1 17-UU (x2 line-union 798+6+6->810 / lhb mine-key overlap carried) + pick-4 11-UU paper family "
    "-> PUSH LANDED 31f87759..bcdd81b8 = FOLD COMPLETE (hash-rewrite receipts x2 chains: 642c3c41->48c762ca->ed656709 / 15af87db->7619982d->7fa3f614 / "
    "eefaa3ce->882d93ee->fe0d1f46 / f62601de->6f8ee757->301a32f2 / 04ff23bb->09c501b4->bcdd81b8) "
    "-> GC executed per r89 plan: machine/bm-c-r{87,88,89} all three deleted post-fold "
    "(content spot-check on origin/main: r89 resolver in-tree / CODELY r89 entry+19th-batch line / F-06 / report R89 / state round_no=89 all present) "
    "+ r72/r84 two stale branches LEFT (cherry-pick patch-id faces polluted by conflict-rewrite false-positives 50/167 unique -- deferred to dedicated verify, not deleted) "
    "+ S0.5 orders 96/96 double-scan zero-unacked (round-start + S7 rescan) + decisions batch D-06..D-10 gate: "
    "D-09 = closed-by-r84 F-03 re-verified (classify_conflicts nested deep-scan in-tree 4-hits) zero-action; "
    "D-08/C-01 seat-3 = already issued via F-20260927-02 (bm-a) + r84 yield receipt F-04, zero-action; "
    "D-06/D-07/D-10 not-our-face zero-action (group repo local tree diverged w/ HQ interactive session in-flight -- read origin blob only, backed off local surgery) "
    "+ smoke 25/25 + watermark green red=false healthy + board 30 all-claimed 0-open job_list empty "
    "+ S6 chain 33/33 rc=0 (r87 chain script + update_repo leg added 32->33; Sunday no-new-bar statutory no-op family + lane guards all honest) "
    "+ CODELY r90 pitlaw appended (auto-merged-face stage-empty fallback law) -> 10309B broke 10KB hard line -> 20th-batch in-window archival "
    "(r332-bmb tick full 1119B verbatim to archive 二十批节 + pointer line; 9425B < 10KB; zero-loss asserts passed) "
    "+ HANDOVER 5x check (r90 = 5-multiple): r86-90 window zero new product rows, receipt line appended, bm-a R331-335 baseline stands "
    "+ schtasks IterationLoop Running(this session)/Watchdog Ready 17:10 + pre-commit claw PRESENT (r89 reinstall holding) "
    "+ inbox zero pending [via bm-c]"
)

# 1) round report line append
rp = io.open(ROOT + r"\logs\iteration-loop\round_reports-bm-c.md", encoding="utf-8", newline="").read()
nl = "\r\n" if "\r\n" in rp[:2000] else "\n"
if not rp.endswith((nl, "\n")):
    rp += nl
rp += report_line + nl
io.open(ROOT + r"\logs\iteration-loop\round_reports-bm-c.md", "w", encoding="utf-8", newline="").write(rp)

# 2) state-bm-c.json
state = {
    "machine_id": "bm-c",
    "round_no": 90,
    "updated": now.strftime("%Y-%m-%dT%H:%M"),
    "note": (
        "r90: S0-FOLD MISSION COMPLETE (inherited r89 plan): 6-pick wave-1 + 5-pick wave-2 rebase all canon-resolved "
        "(_r90bmc_probe/_r90bmc_resolve.py; mid-flight fixes: pointer-family guard + auto-merged-archive stage-empty worktree-fallback law) "
        "-> push LANDED 31f87759..bcdd81b8 fold complete -> GC machine/bm-c-r{87,88,89} x3 deleted post-fold (content spot-check pass) "
        "+ r72/r84 left (patch-id polluted, deferred) + orders 96/96 double-scan + decisions D-06..10: D-09 closed-by-r84 verified / "
        "D-08 C-01 seat-3 issued-F02+yield-F04 zero-action / D-06/07/10 not-our-face + smoke 25/25 + S6 33/33 rc=0 (update_repo leg 32->33) "
        "+ CODELY r90 pitlaw + 20th-batch in-window archival 10309->9425B (r332-bmb full 1119B verbatim to archive) + HANDOVER 5x r90 receipt "
        "+ next: (1) Mon 09-28 09:15 T-91 s3 first-marks auto-fire watch; (2) C-01 council window 09-29 12:00; (3) r72/r84 branch dedicated verify+GC; "
        "(4) 10-01 month trio standing (science_audit/monthly_briefing/self_review)"
    ),
    "last_round_ts": iso,
}
io.open(ROOT + r"\state-bm-c.json", "w", encoding="utf-8", newline="\n").write(json.dumps(state, ensure_ascii=False, indent=1) + "\n")

# 3) heartbeat fleet/machines/bm-c.json (own file only; preserve all fields)
hb = json.load(open(ROOT + r"\fleet\machines\bm-c.json", encoding="utf-8"))
hb["last_seen"] = iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = iso
hb["current_task"] = "R90 done: S0 fold complete (5-commit chain landed bcdd81b8) + GC x3 fallback branches + 20th-batch archival; next=Monday T-91 s3 watch + C-01 window 09-29"
hb["cpu_util_pct"] = 73.0
hb["cpu_pct"] = 0.0
hb["free_ram_gb"] = 5.9
hb["total_ram_gb"] = 23.9
hb["gpu_free_vram_mb"] = 9258
hb["verdict"] = "legal idle: fold mission round (board 30 all-claimed 0 open, wm red=false healthy, pool lanes owned bm-a/bm-b); r90=S0-fold+GC+S6 33/33 all green"
io.open(ROOT + r"\fleet\machines\bm-c.json", "w", encoding="utf-8", newline="\n").write(json.dumps(hb, ensure_ascii=False, indent=1) + "\n")

# verify (smoke F7 contract: epoch int, clock_read ISO T-format)
back = json.load(open(ROOT + r"\fleet\machines\bm-c.json", encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int"
assert "T" in back["clock_read"] and "+" in back["clock_read"], "clock_read must be ISO with T and offset"
st = json.load(open(ROOT + r"\state-bm-c.json", encoding="utf-8"))
assert st["round_no"] == 90
print("S5 landed: report line +", len(report_line), "chars; state round 90; heartbeat epoch", epoch, "iso", iso)
