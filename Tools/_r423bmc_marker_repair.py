"""r423 bm-c marker-face repair: 3 files carry leftover merge markers that
escaped the -Last 30 truncation (their CONFLICT lines were cut from view,
my resolve script ran before they were re-listed, a later add -A sealed the
marker version). Both clean sides still recoverable: ours = bcb1330c6 blob,
theirs = origin/main blob. Take-new by embedded ts, rewrite, re-add.

Usage: python Tools/_r423bmc_marker_repair.py
"""
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OURS_COMMIT = "bcb1330c6"
FACES = ["results/daily_scorecard.json",
         "results/paper_export/export-2026-09-30.json",
         "results/paper_export/latest.json"]


def show(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", creationflags=0x08000000)
    return r.stdout if r.returncode == 0 else None


def ts_of(text):
    m = re.findall(r"20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}", text[:4000])
    return max(m) if m else ""


def main():
    receipt = []
    for path in FACES:
        ours = show(OURS_COMMIT, path)
        theirs = show("origin/main", path)
        assert ours is not None and theirs is not None, path
        # origin tip itself carries leftover merge markers (bm-b r626c
        # push residue, 12/21 markers verified) -- only take a CLEAN side;
        # ts comparison applies only when both sides are clean.
        o_clean = not re.search(r"<<<<<<<|^=======$|>>>>>>>", ours, re.M)
        t_clean = not re.search(r"<<<<<<<|^=======$|>>>>>>>", theirs, re.M)
        to, tt = ts_of(ours), ts_of(theirs)
        if o_clean and t_clean:
            text, side = (ours, "ours-newer") if to >= tt else \
                (theirs, "theirs-newer")
        elif o_clean:
            text, side = ours, "ours(clean; theirs carries markers)"
        elif t_clean:
            text, side = theirs, "theirs(clean; ours carries markers)"
        else:
            raise SystemExit(f"MARKER-REPAIR FAIL: both sides dirty {path}")
        assert not re.search(r"<<<<<<<|^=======$|>>>>>>>", text, re.M), path
        with open(os.path.join(ROOT, path), "w", encoding="utf-8",
                  newline="") as f:
            f.write(text)
        subprocess.run(["git", "add", path], cwd=ROOT,
                       creationflags=0x08000000)
        receipt.append({"path": path, "ours_ts": to, "theirs_ts": tt,
                        "winner": side, "markers_after": 0})
        print(f"repaired take-{side}: {path} (ours {to} vs theirs {tt})")
    rp = os.path.join(ROOT, "results", "_r423bmc_marker_repair_receipt.json")
    json.dump(receipt, open(rp, "w", encoding="utf-8"), indent=1,
              ensure_ascii=False)
    print(f"receipt -> {rp}")


if __name__ == "__main__":
    main()
