# -*- coding: utf-8 -*-
"""r1055 S0 bridge restore: checkout keep-local faces from stash@{0}, then union 3 faces.

keep-local = tracked dirty faces MINUS origin-wins-23 (bm-a 20:0x newer regenerables).
Union faces ride keep-local (disk=local ver from stash), then _r1055bmc_s0_bridge.py --apply.
"""
import subprocess, sys, io

ORIGIN_WINS_23 = {
    "results/compute_audit.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/post_review/REPORT-20261016.md",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/watermark_red.json",
    "results/compute_audit.bm-c.json",  # bm-a heal also refreshed per-machine audit faces
}

def main():
    keep = []
    with io.open("results/_r1055bmc_dirty_list.txt", "r", encoding="utf-8-sig") as f:
        for raw in f:
            line = raw.rstrip("\n").rstrip("\r")
            if len(line) < 4:
                continue
            st, path = line[:2], line[3:]
            if st.strip() == "M" and path not in ORIGIN_WINS_23:
                keep.append(path)
    print("keep_local=%d restore_from_stash" % len(keep))
    for i in range(0, len(keep), 20):
        batch = keep[i:i+20]
        r = subprocess.run(["git", "checkout", "stash@{0}", "--"] + batch,
                           capture_output=True)
        if r.returncode != 0:
            print("BATCH FAIL rc=%d: %s" % (r.returncode, r.stderr.decode('utf-8','replace')[:300]))
            sys.exit(2)
    print("restore ok")
    r = subprocess.run([sys.executable, "results/_r1055bmc_s0_bridge.py", "--apply"],
                       capture_output=True)
    sys.stdout.write(r.stdout.decode("utf-8", "replace"))
    if r.returncode != 0:
        sys.stdout.write(r.stderr.decode("utf-8", "replace")[:500])
        sys.exit(3)

if __name__ == "__main__":
    main()
