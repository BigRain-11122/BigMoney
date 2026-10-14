"""r1001 bm-a S0 surgery: side-excerpt registry-hit stale face + quarantine untracked stale export,
discard stale pre-bar derived faces, ff-pull origin (bm-c r1008 landed 10-14 bar + full paper chain).

Rationale: r1000 detached S6 chain (legs 40, bad=0, done 21:19) derived faces WITHOUT the 10-14 bar
(klc unpublished at run time). bm-c r1008 landed the 10-14 bar + full paper chain WITH it.
Origin's committed faces are strictly newer derived state; local dirty stale re-derivations get
discarded (regenerable artifacts, treasure_guard rc0 except registry-hit which is excerpted aside
per guard escape hatch "先摘录存旁"). pool_dualrun.bm-a.jsonl (append-only evidence) and all
bm-a-lane runtime faces are NOT touched (bm-c commit does not include them).
"""
import json
import os
import shutil
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QDIR = os.path.join(ROOT, "results", "_quarantine", "20261014-2125_r1001bma_prebar_faces")
MANIFEST = os.path.join(ROOT, "results", "_quarantine", "manifest.json")

STALE_TRACKED = [
    "docs/daily_report/REPORT-2026-10-14.json",
    "docs/daily_report/REPORT-2026-10-14.md",
    "docs/live_usage/LIVE-2026-10-14.json",
    "docs/live_usage/LIVE-2026-10-14.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/compute_audit.json",
    "results/market_clock/call_latest.json",
    "results/prospect_paper/_summary.json",
    "results/regime_state.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
]
UNTRACKED_STALE = "results/paper_export/export-2026-10-14.json"  # collides with origin add


def main():
    os.makedirs(QDIR, exist_ok=True)
    side = []
    # 1) side-excerpt registry-hit file (prospect_paper/_summary.json per TREASURE_REGISTRY row 21)
    p_sum = os.path.join(ROOT, "results", "prospect_paper", "_summary.json")
    dst = os.path.join(QDIR, "prospect_paper_summary.json")
    shutil.copy2(p_sum, dst)
    side.append(("results/prospect_paper/_summary.json", "prospect_paper_summary.json"))
    # 2) quarantine-move untracked stale export (origin adds same path)
    p_exp = os.path.join(ROOT, UNTRACKED_STALE)
    dst2 = os.path.join(QDIR, "paper_export_export-2026-10-14.json")
    shutil.copy2(p_exp, dst2)
    side.append((UNTRACKED_STALE, "paper_export_export-2026-10-14.json"))
    os.remove(p_exp)
    # 3) manifest append (fresh read-modify-write)
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    window_until = "2026-10-21"
    manifest = []
    if os.path.exists(MANIFEST):
        with open(MANIFEST, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    manifest.append({
        "ts": now_iso,
        "round": "r1001 bm-a",
        "dir": "20261014-2125_r1001bma_prebar_faces",
        "files": [s[1] for s in side],
        "reason": ("S0 ff-pull surgery: stale pre-10-14-bar derived faces excerpted aside before "
                   "origin(bm-c r1008, new-bar) versions land; registry-hit prospect_paper/_summary "
                   "excerpt per treasure_guard escape hatch"),
        "window_until": window_until,
    })
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    # 4) discard stale tracked dirty faces -> HEAD (pure working-tree restore, zero HEAD change)
    r = subprocess.run(["git", "checkout", "--"] + STALE_TRACKED, cwd=ROOT,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    # 5) verify: none of STALE_TRACKED remain dirty
    st = subprocess.run(["git", "status", "--porcelain=v1"], cwd=ROOT,
                        capture_output=True, text=True).stdout.splitlines()
    dirty = {ln[3:].strip() for ln in st if ln.startswith(" M") or ln.startswith("M")}
    residual = [p for p in STALE_TRACKED if p in dirty]
    assert not residual, residual
    # 6) assert untracked collision removed
    assert not os.path.exists(p_exp)
    # 7) ff-only pull
    r = subprocess.run(["git", "pull", "--ff-only"], cwd=ROOT, capture_output=True, text=True)
    print("PULL_STDOUT:", r.stdout.strip()[-400:])
    print("PULL_RC:", r.returncode)
    assert r.returncode == 0, r.stderr
    # 8) post-pull: behind must be 0
    subprocess.run(["git", "fetch", "origin"], cwd=ROOT, capture_output=True, text=True)
    cnt = subprocess.run(["git", "rev-list", "--count", "main..origin/main"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    assert cnt == "0", cnt
    tip = subprocess.run(["git", "rev-parse", "--short", "origin/main"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    print(json.dumps({
        "ok": True,
        "quarantine_files": [s[1] for s in side],
        "discarded_stale_tracked": len(STALE_TRACKED),
        "residual_dirty_overlap": 0,
        "behind": 0,
        "origin_tip": tip,
        "manifest_entries": len(manifest),
    }, indent=1))


if __name__ == "__main__":
    main()
