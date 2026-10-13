# -*- coding: utf-8 -*-
# r977 S0.5 ground-truth consumption: fetch group tree, verify watermark deltas,
# extract new rows vs watermarks (ord blob cat-file diff / dec post-D-20261013-02 tail).
import subprocess, hashlib, json, sys
sys.stdout.reconfigure(encoding="utf-8")

G = r"K:\Fluxgroup\FluxGroup"
WM_DEC = "2bf2a0ef5c4e6384cba0e3e1f85b09da9500f850ca483a230c1fbe0cd53488c5"
WM_ORD = "a20281ea1fa1a751eab6a6922e567a191774bf0b"

def run(args, binary=False):
    r = subprocess.run(["git", "-C", G] + args, capture_output=True)
    if r.returncode != 0:
        print("GIT-FAIL", args, r.stderr.decode("utf-8", "replace")[:200]); sys.exit(2)
    return r.stdout if binary else r.stdout.decode("utf-8", "replace")

run(["fetch", "origin"])
ord_now = run(["rev-parse", "origin/main:docs/orders.md"]).strip()
dec_raw = run(["show", "origin/main:docs/decisions.md"], binary=True)
dec_now = hashlib.sha256(dec_raw).hexdigest()

facts = {
    "ord_now": ord_now, "ord_wm": WM_ORD, "ord_delta": ord_now != WM_ORD,
    "dec_now": dec_now, "dec_wm": WM_DEC, "dec_delta": dec_now != WM_DEC,
    "ts": "2026-10-13 23:1x",
    "origin_tip": run(["rev-parse", "origin/main"]).strip(),
}
print(json.dumps(facts, ensure_ascii=False))

# ---- ORD new rows: cat-file old blob if present ----
if facts["ord_delta"]:
    try:
        old_ord = run(["cat-file", "blob", WM_ORD]).splitlines()
        new_ord = run(["show", "origin/main:docs/orders.md"]).splitlines()
        old_set = set(l.rstrip("\r") for l in old_ord)
        added = [l.rstrip("\r") for l in new_ord if l.rstrip("\r") not in old_set]
        print("=== ORD ADDED LINES (%d) ===" % len(added))
        for l in added:
            print(l[:600])
    except SystemExit:
        print("ORD old blob NOT in object store; falling back to tail read below")

# ---- DEC new rows: tail after D-20261013-02 block ----
if facts["dec_delta"]:
    dec_text = dec_raw.decode("utf-8", "replace")
    lines = dec_text.splitlines()
    # find last line index containing D-20261013-02 (the last consumed anchor)
    idx = max((i for i, l in enumerate(lines) if "D-20261013-02" in l), default=None)
    print("=== DEC anchor D-20261013-02 at line", idx, "of", len(lines), "===")
    if idx is not None:
        tail = lines[idx+1:]
        nonempty = [l for l in tail if l.strip()]
        print("=== DEC TAIL NONEMPTY (%d) ===" % len(nonempty))
        for l in nonempty:
            print(l[:600])
    else:
        print("D-20261013-02 NOT FOUND — printing last 40 lines for manual anchor:")
        for l in lines[-40:]:
            print(l[:600])
