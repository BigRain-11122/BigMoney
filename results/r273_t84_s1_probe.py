# r273 bm-a: T-84 s1 first slice -- D:\Money reachability probe + physical-dependency disclosure.
# Why: O-20260926-2229 says System A = "D:\Money ... ON THIS BOX 58 py verified present"
# (GM claim commit 6ab2bc79 22:31:52), but this round's probe finds NO D: drive at all.
# Honest face: s1 code audit physically blocked until the volume returns or a TRANSFER
# channel delivers the 58 py into this repo. No numbers invented; probe evidence only.

import json, os, subprocess, datetime, time

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# Three independent reachability witnesses
ps = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "Get-PSDrive -PSProvider FileSystem | Select-Object -ExpandProperty Name"],
    capture_output=True, text=True)
drives = sorted(x.strip() for x in ps.stdout.split() if x.strip())
py_listing = None
try:
    py_listing = os.listdir("D:/Money")
except FileNotFoundError:
    py_listing = None

probe = {
    "ticket": "T-2026-09-26-84-P1",
    "slice": "s1-reachability-probe (first slice, honest-face)",
    "order": "O-20260926-2229-bm-a",
    "ts": now,
    "evidence_cutoff": "2026-09-26",
    "claim_basis_conflict": {
        "ticket_says": "System A = D:\\Money LightGBM, ON THIS BOX 58 py files verified present (GM commit 6ab2bc79 @ 22:31:52)",
        "probe_found": "NO D: drive on this machine at probe time",
        "witnesses": {
            "psdrive_filesystem_roots": drives,
            "python_listdir_d_money": "FileNotFoundError" if py_listing is None else py_listing[:5],
            "c_money_exists": os.path.exists("C:/Money"),
            "k_drive_exists": os.path.exists("K:/"),
        },
        "note": "22:31 GM-verified-present vs 22:3x probe absent = volume disappeared mid-round "
                "(removable unplugged / mapping dropped / subst cleared), or GM verified on another face. "
                "Disclosed as-is; NOT adjudicated here.",
    },
    "physical_dependency_hold": {
        "law": "CEO immediate-ticket sole legal deferral = physical dependency with in-ticket trace",
        "blocked_work": "s1 code audit (58 py lookahead scan + IC/Sharpe recompute) requires D:\\Money readable",
        "resume_paths_for_ceo_gm": [
            "1. re-mount the volume (plug back / remap / re-subst D:) -> next round auto-resumes s1",
            "2. TRANSFER channel per fleet/TRANSFER.md: ship the 58 py into a controlled repo dir -> audit in-repo",
            "3. if System A actually lives on another box -> re-assign s1 lane to that box's executor (lane handover)",
        ],
    },
    "s1_plan_on_resume": [
        "census 58 py (path/lines/imports)",
        "mechanical lookahead scan: shift(-x) / rolling center=True / negative periods / eval-window overlap",
        "IC recompute de-bloat (IC=1.0 red flag adjudication), Sharpe recompute (5.89 vs dd -32.63% inconsistency)",
        "Top3-twin dedup-gate lesson intake into tournament gates (s3 cross-link)",
    ],
}
out = "results/r273_t84_s1_probe.json"
json.dump(probe, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("probe written:", out)
print("drives seen:", drives, "| D:/Money reachable:", py_listing is not None)
