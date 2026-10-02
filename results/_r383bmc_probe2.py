"""r383 bm-c part-2 probe: guard fn existence + prereg SS7 backfill state
+ chain-head cross-check vs origin (r518 law: consume chain head from origin
truth). UTF-8 stdout per bm-b r593 GBK-capture law."""
import json, os, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CN = 0x08000000
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import science_gates as sgmod
print("finalize_already_landed exists:", hasattr(sgmod, "finalize_already_landed"))

def gshow(pathspec, repo=ROOT):
    r = subprocess.run(["git", "-C", repo, "show", pathspec], capture_output=True,
                       creationflags=CN)
    return r.stdout if r.returncode == 0 else None

# does origin already carry any W113 ledger block? (r381-2: twin check)
blob = gshow("origin/main:results/perpetual_faces/n1_w113_results.json")
print("origin has n1_w113_results.json:", blob is not None)

# prereg SS7/SS8 backfill state
pre = os.path.join(ROOT, "research", "PERPETUAL_N1_W113_PREREG.md")
with open(pre, encoding="utf-8") as f:
    txt = f.read()
for key in ("SS7", "SS8", "PENDING_BACKFILL", "placeholder", "PLACEHOLDER",
            "一次定稿", "613,148", "613148", "246,520", "246520",
            "-0.0928", "0.3105"):
    print(f"prereg contains {key!r}:", key in txt)
# print the SS7-ish lines for eyes
for i, line in enumerate(txt.splitlines()):
    if "SS7" in line or "SS8" in line or "BACKFILL" in line.upper():
        print(f"L{i+1}: {line[:240]}")
