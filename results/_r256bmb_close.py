"""_r256bmb_close.py -- R256 round-close bookkeeping (report line + state bump)."""
import io
import json
import time

LINE = (
    "2026-09-26 15:2x | r256 bm-b | dept:portfolio+research+engineering | "
    "WM-VERDICT: GREEN insufficient_history window n=1 (probe 15:08 py "
    "1-2.3%, board 0 open / pool 1 ready = T80 battery lane-pinned bm-a "
    "relaunch-ready post A1 fix; red=false) | did: S0.5 inbox T-80 "
    "anchor-refusal ADJUDICATED as owner -- probe _r256bmb_anchor_probe "
    "reproduced the refusal ON bm-b (0/20, got==bm-a byte-identical -> "
    "canon/dA hypothesis structurally excluded: anchor got{} is "
    "sleeve-domain, grids feed W-GRID after the assert); git archaeology: "
    "T-56 0389dee6 + T-58 47a8f6b4 run lines both EXCLUDE r242 wiring "
    "commit d65f2d4a (C01 tp_ladder / C02+ENGULF ov_full+dd_control / "
    "C01 OOS sharpe 1.6085->1.7479) = live-registry recompute structurally "
    "cannot reproduce frozen anchors; worktree@0389dee6 file-by-file "
    "bisect: engine/live/t28 behavior-zero, registry = sole drift face; "
    "FIX (prereg SS-A1 zero-result amendment): t56_caliber_registry "
    "29-file snapshot (git 0389dee6 byte-faithful + _manifest sha256) + "
    "runner _caliber_init/_caliber_sharpe_map + selftest F11 (11/11) + "
    "probe --t56-caliber 20/20 bit-identical; MSG-20260926-1600-bm-b "
    "relaunch instruction + dA sha256 recipe in pool note + ticket "
    "progress_r256; S7 push-collision replay resolved (autostash rebase, "
    "2x UU pool: CN-DIV=upstream done/bm-a face vs watchdog stale claim "
    "void r239-family, T80=A1 face; resolver _r256bmb_resolve.py; "
    "forensics: no launch/no burn/no ledger double-count) landed d1d68187; "
    "S6 28 legs all exit 0 weekend no-ops (09-25 mid-autumn holiday, "
    "panel cutoff 09-24 complete; marks/paper legs idempotent no-op); "
    "smoke 25/25 pre+post | next: T-80 harvest pending bm-a "
    "relaunch+landed-marker (r244 law); T-81 slice-3 four-must-report "
    "(r255 pointer)\n")

with io.open(r"logs\iteration-loop\round_reports.md", "a",
             encoding="utf-8", newline="\n") as fh:
    fh.write(LINE)

with io.open(r"logs\iteration-loop\state.json", encoding="utf-8") as fh:
    d = json.load(fh)
d["round_no"] = 256
d["did"] = ("r256: T-80 anchor-refusal adjudicated + A1 caliber-pin fix "
            "delivered (sleeve-input basis snapshot git 0389dee6; probe "
            "20/20 bit-identical; selftest 11/11; prereg SS-A1) + S7 "
            "push-collision replay resolved + S6 28 legs green weekend "
            "no-ops + smoke 25/25")
d["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
with io.open(r"logs\iteration-loop\state.json", "w",
             encoding="utf-8", newline="\n") as fh:
    json.dump(d, fh, indent=1, ensure_ascii=False)

print("round report line + state round_no=256 written")
