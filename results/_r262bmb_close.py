# -*- coding: utf-8 -*-
"""R262 bm-b: S5 state + round report + S7 heartbeat write-back.
Byte faces (probed): state.json/bm-b.json = LF, indent 2, TRAILING newline,
no BOM; round_reports.md = append one pipe-separated line."""
import io
import json
import time

import psutil

NOW = time.strftime("%Y-%m-%d %H:%M:%S")
NOW_ISO = time.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
EPOCH = int(time.time())

# ---------- state.json ----------
P = "logs/iteration-loop/state.json"
st = json.load(io.open(P, encoding="utf-8"))
st["round_no"] = 262
st["did"] = (
    "r262: identity re-established mid-round via four-source probe "
    "(machine.json r191 note + 16 cores + state.json r261 + round_reports.md) "
    "-- session had initially misread the PULLED TRACKED state-bm-a.json as "
    "local state and executed bm-a's R257 next-slice pointer; work validated "
    "non-duplicated + all labels corrected. T-73 s2 slice-D FACTOR-HISTORY "
    "three laws census executed cross-lane per lane-affinity (size/lowvol "
    "laws ALIVE BOTH SIDES; dividend style era history; 688 cap unit "
    "double-correction self-caught by cap_sanity leg, 3 size faces "
    "discarded+recomputed N=13 honest) + T-82 deep-bcd SENDER LEG COMPLETED "
    "(branch transfer/t80-deep-bcd-basis 2ef23068 pushed, 6/6 remote blob "
    "byte-verify vs MSG-1556, official sender manifest landed, receipt MSG "
    "to bm-a, MSG-1650 processed)")
st["verdict"] = (
    "GREEN size SIZE/h10 OOS ic -0.0566 (35x thr) IS -0.0470 gates v2 "
    "single-fail + era 2017-2020 INVERSION +0.0075 (core-asset) captured; "
    "lowvol VOL60/h10 OOS -0.0479 all-six-eras negative never flipped; "
    "dividend 2021-2024 +12.39%/yr vs 2025+ reversal -8.63% in case; "
    "supply answer to pool_starvation: slice-D 78.5s in-repo <5min inline "
    "legal, pool 47/47 done zero ready, no fabricated busywork O-1137")
st["next"] = (
    "(1) T-82 deep-bcd receive confirmation watch (bm-a receiver manifest "
    "-Verify + reply to MSG-172x); (2) T-76 faces (a) jisilu/hibor/guorn + "
    "jin-gong post-holiday verify = 09-28 Monday open window; (3) s2 "
    "style-rotation slice = next machine-agnostic research leg (bm-a R258 "
    "likely takes it, anti-dup signal planted in T-73 progress_r262); "
    "(4) zoo #95/#96 paramfreeze deep-read optional; (5) 10-01 month trio + "
    "REGIME_GUARD v3 date gate")
st["last_round_ts"] = NOW_ISO
st["last_result"] = "ok"
st["current_task"] = (
    "T-82 deep-bcd receive watch + T-76 09-28 faces + s2 style-rotation "
    "(machine-agnostic) + 10-01 trio")
st["last_tick"] = time.strftime("%H:%M")
st["updated_at"] = NOW_ISO
st["ts"] = NOW
io.open(P, "w", encoding="utf-8", newline="\n").write(
    json.dumps(st, indent=2, ensure_ascii=False) + "\n")
print("state.json round 262 written, epoch int:", EPOCH,
      "| isinstance int:", isinstance(EPOCH, int))

# ---------- round report ----------
LINE = (
    "2026-09-26 17:3x | r262 bm-b | watermark: GREEN (17:12 probe py 0.5% "
    "open=0 bandit=0 batch=0 -> py_low_board_clear legal idle face; "
    "compute_audit FLAG pool_starvation span 35.4min honestly answered: "
    "slice-D in-repo batch 78.5s <5min inline legal, pool 47/47 done zero "
    "ready, remaining s2 legs fast research, no fabricated busywork "
    "O-1137) | did: S0 fetch 0 incoming (r261 addendum already local HEAD); "
    "S0.5 orders 82/82 zero unacked under CORRECT identity -- identity "
    "incident honestly disclosed: session started by misreading the PULLED "
    "TRACKED state-bm-a.json as local state, executed bm-a's R257 "
    "next-slice pointer under wrong lens; four-source probe mid-round "
    "(machine.json r191 note + 16 cores + state.json r261 + "
    "round_reports.md) re-established bm-b; work validated NON-DUPLICATED "
    "(slice executed once, prereg frozen pre-run, evidence chain clean) + "
    "all identity labels corrected (ticket progress_r258->progress_r262 "
    "renamed with attribution, digest/CODELY relabeled, helper filenames "
    "kept for reference integrity); S1 smoke 25/25 (pre-incident); S3 "
    "MAIN-A = T-73 s2 slice-D FACTOR-HISTORY three laws one-round census "
    "(cross-lane per ticket lane-affinity note, anti-dup signal planted): "
    "scripts/t73_s2_factor_history.py prereg-frozen header + selftest 10 "
    "legs (NaN equal_nan pit self-caught, fixture mislabel fixed, ETF "
    "sh-prefix crash on run1) + corrected batch 78.5s -> results/t73_s2/"
    "factor_history.json + digest sliceD: SIZE ALIVE BOTH SIDES SIZE/h10 "
    "OOS -0.0566 (35x 1.6bp thr) IS -0.0470, gates v2 single-fail (IS ir "
    "0.246<0.30), size/h20 all-gates variant (face stays h10 frozen), era "
    "2017-2020 INVERSION +0.0075 (core-asset era) vs 2015-2016 peak "
    "-0.1125 vs 2025+ alive -0.0566; LOWVOL ALIVE BOTH SIDES VOL60/h10 "
    "OOS -0.0479 IS -0.0495 (30x/31x), gates v2 fail, ALL-SIX-ERAS "
    "negative never flipped (pre2005 -0.034 .. 2021-2024 -0.088 .. 2025+ "
    "-0.048); DIVIDEND style history 510880vs510300 (price face, bias "
    "against law disclosed): full-window -0.05%/yr, 2017-2020 -11.63%, "
    "2021-2024 +12.39%/yr, cy2024 -3.82% (distributions excluded), 2025+ "
    "REVERSAL -8.63% in case; corr(size,vol60 IC)=-0.158; unit forensics: "
    "run1 /100 board fix = double-correction (operative cache volume "
    "already normalized, amount/volume~close anchors x1.0007/x1.0014, "
    "probe _r258bma_688_probe.py) caught by cap_sanity disclosure leg "
    "(688 median cap 71M implausible) -> 3 size faces discarded + "
    "recomputed, defect-robust (defective OOS -0.0546 vs corrected "
    "-0.0566), N=13 IC computations consumed / 10 in final artifact; S3 "
    "MAIN-B = T-82 deep-bcd SENDER LEG (own-machine pending deliverable, "
    "bm-a window armed since 16:49): official manifest "
    "T-2026-09-26-82-deepbcd-sender.json (6 files 27,210,738B, 6/6 sha "
    "MATCH MSG-1556) + branch transfer/t80-deep-bcd-basis pushed commit "
    "2ef23068 via isolated worktree (first push empty-tree gitignore "
    "block -> same-window -f second commit fast-forward, no force-push, "
    "no consumer pollution) + remote blob byte-verify 6/6 subprocess raw "
    "bytes (R255 law) + receipt MSG-20260926-172x to bm-a + MSG-1650 "
    "processed (both-side add per r257 move law) + T-82 ticket "
    "progress_r262 note; S6 chain all exit 0 weekend no-ops (regime "
    "ORANGE shadow days=2 breadth 0.77, clock ORANGE_COOL idempotent, lhb "
    "quarter refetch 0 new, heat/futures no-op, options/moneyflow/sina_mf/"
    "ths/ah bm-a-lane guards correctly no-op for bm-b, fund_premium bm-c "
    "lane, fundamental 20.1h fresh skip, blf all_pass, scorecard 6 "
    "traders, report 4 faces token=1, build_status 432combos, token "
    "delta=41); no new bar Saturday -> paper conditional legs legally "
    "skipped; monthly trio not month-first round | evidence: results/"
    "t73_s2/factor_history.json + DIGEST-20260926-t73-s2-sliceD-factor-"
    "history.md + probes + git ls-remote transfer/t80-deep-bcd-basis "
    "2ef23068 + fleet/transfers/T-2026-09-26-82-deepbcd-sender.json + S6 "
    "exit codes in transcript | next: (1) T-82 receive confirmation "
    "watch; (2) T-76 faces 09-28 Monday window; (3) s2 style-rotation "
    "slice (machine-agnostic, bm-a likely takes per its pointer); (4) "
    "#95/#96 deep-read optional; (5) 10-01 month trio + v3 date gate\n")
with io.open("logs/iteration-loop/round_reports.md", "a",
             encoding="utf-8", newline="") as fh:
    fh.write(LINE)
print("round report appended, chars:", len(LINE))

# ---------- heartbeat ----------
H = "fleet/machines/bm-b.json"
hb = json.load(io.open(H, encoding="utf-8"))
cpu = psutil.cpu_percent(interval=1)
ram = psutil.virtual_memory()
hb["last_seen"] = NOW
hb["round_no"] = 262
hb["current_task"] = st["current_task"]
hb["cpu_cores"] = psutil.cpu_count(logical=True)
hb["cpu_pct"] = round(cpu, 1)
hb["free_ram_gb"] = round(ram.available / 2**30, 1)
gpu_free = None
try:
    import subprocess as sp
    out = sp.run(["nvidia-smi", "--query-gpu=memory.free",
                  "--format=csv,noheader,nounits"], capture_output=True,
                 text=True).stdout.strip().splitlines()
    gpu_free = round(float(out[0]) / 1024, 1) if out else None
except Exception:
    gpu_free = None
if gpu_free is not None:
    hb["gpu_free_vram_gb"] = gpu_free
hb["verdict"] = st["verdict"]
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW_ISO
io.open(H, "w", encoding="utf-8", newline="\n").write(
    json.dumps(hb, indent=2, ensure_ascii=False) + "\n")
chk = json.load(io.open(H, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print("heartbeat written; epoch:", chk["heartbeat_epoch_utc"],
      "| int-verified:", isinstance(chk["heartbeat_epoch_utc"], int),
      "| gpu_free:", gpu_free, "| cpu:", hb["cpu_pct"],
      "| ram_free:", hb["free_ram_gb"])
