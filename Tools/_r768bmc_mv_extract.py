# -*- coding: utf-8 -*-
"""r768 bm-c: binary-safe extraction of mv0001 handover inputs from group
repo origin/main blobs (mp3 audio + scripts). PowerShell > redirect corrupts
binary; python subprocess capture is byte-exact."""
import subprocess
import sys

REPO = "K:/Fluxgroup/FluxGroup"
WORK = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\mv_work"
FILES = [
    ("cph4/fleet/mv0001-handover/audio/mv001_source_320k.mp3", "mv001_source_320k.mp3"),
    ("cph4/fleet/mv0001-handover/scripts/full_mv_v2.py", "full_mv_v2.py"),
    ("cph4/fleet/mv0001-handover/scripts/full_mv.py", "full_mv.py"),
    ("cph4/fleet/mv0001-handover/scripts/gen_storyboard.py", "gen_storyboard.py"),
    ("cph4/fleet/mv0001-handover/canon/PRODUCTION.md", "PRODUCTION.md"),
    ("cph4/fleet/mv0001-handover/canon/SCRIPT-v1.md", "SCRIPT-v1.md"),
    ("cph4/fleet/mv0001-handover/canon/ANALYSIS-v2.md", "ANALYSIS-v2.md"),
]


def main():
    ok = True
    for src, dst in FILES:
        r = subprocess.run(["git", "-C", REPO, "show", "origin/main:" + src],
                           capture_output=True)
        if r.returncode != 0 or not r.stdout:
            sys.stderr.write("FAIL %s rc=%d %s\n" % (src, r.returncode, r.stderr[:120]))
            ok = False
            continue
        out = WORK + "\\" + dst
        with open(out, "wb") as fh:
            fh.write(r.stdout)
        print("OK %s -> %s (%d B)" % (src, dst, len(r.stdout)))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
