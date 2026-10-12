# r955 track-2 frame extraction: pull bm-a regen frames (C03/C04/C09) from
# group-tree origin/main via git cat-file (zero worktree touch, byte-exact).
# Per MSG-20261013-0455-bma: frames at cph4/fleet/mv0001-handover/outbound/
# krea2/kf-demo-20261012/track2-1013/<tag>.png on origin/main (main@94702cd).
import subprocess, os, sys

GT = r"K:\Fluxgroup\FluxGroup"
BASE = "cph4/fleet/mv0001-handover/outbound/krea2/kf-demo-20261012/track2-1013/"
DST = os.path.join(GT, BASE.replace("cph4/fleet/mv0001-handover/outbound/krea2/kf-demo-20261012/", ""), "bmc", "i2v_frames")
DST = r"K:\Fluxgroup\FluxGroup\cph4\fleet\mv0001-handover\outbound\krea2\kf-demo-20261012\bmc\i2v_frames"
TAGS = ["C03_dig_reveal", "C04_words_alive", "C09_oath_weather"]

def main():
    os.makedirs(DST, exist_ok=True)
    for t in TAGS:
        out = os.path.join(DST, t + "_v2.png")
        if os.path.exists(out) and os.path.getsize(out) > 100000:
            print("SKIP", t, os.path.getsize(out)); continue
        blob = BASE + t + ".png"
        # resolve blob sha at origin/main, then cat-file byte-exact
        sha = subprocess.run(["git", "-C", GT, "rev-parse", "origin/main:" + blob],
                             capture_output=True, text=True)
        if sha.returncode != 0 or len(sha.stdout.strip()) != 40:
            print("REV-PARSE FAIL", t, sha.stdout.strip()[:60], sha.stderr[:120]); sys.exit(2)
        data = subprocess.run(["git", "-C", GT, "cat-file", "-p", sha.stdout.strip()],
                              capture_output=True).stdout
        if len(data) < 100000:
            print("BLOB TOO SMALL", t, len(data)); sys.exit(2)
        open(out, "wb").write(data)
        print("EXTRACTED", t, len(data), "->", out)

if __name__ == "__main__":
    main()
