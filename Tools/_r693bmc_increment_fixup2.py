# -*- coding: utf-8 -*-
"""r693 bm-c increment fix-up leg-2: previous leg removed the r833
pointer line from main but died on a colliding needle guard (r833
attribution already lives in the dest pit BODY; the POINTER line itself
is absent). Recover: take the exact r833 line bytes from git HEAD
CODELY.md blob, needle = the pointer-line prefix (unique vs pit body),
append verbatim to pit-engine-freeze-editor.md, verify, write receipt."""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
DEST = os.path.join(ROOT, "research", "pit-engine-freeze-editor.md")
RECEIPT = os.path.join(ROOT, "results", "_r693bmc_codely_increment.json")
LIMIT = 30720


def eol_of(raw):
    return b"\r\n" if raw.count(b"\r\n") >= 10 else b"\n"


def main():
    # 1) main must already be under line (r833 removed by leg-1)
    post_m = open(MAIN, "rb").read()
    assert len(post_m) <= LIMIT, "main %d still over line" % len(post_m)
    assert post_m.count("\u57df\u6307\u9488\u00b7r693 bm-c".encode("utf-8")) == 1, \
        "r693 pointer must be present in main"

    # 2) exact r833 pointer line from HEAD blob
    p = subprocess.run(["git", "-C", ROOT, "show", "HEAD:CODELY.md"],
                       capture_output=True)
    assert p.returncode == 0, "git show HEAD CODELY.md fail"
    head = p.stdout
    cand = [l for l in head.splitlines() if b"16:5x r833 bm-a" in l]
    assert len(cand) == 1, "r833 pointer line must be unique in HEAD, got %d" % len(cand)
    line = cand[0]
    needle = b"- [2026-10-07 16:5x r833 bm-a]"
    assert line.startswith(needle), "r833 line form gate"

    # 3) dest: pointer line absent (pit body attribution is a DIFFERENT line)
    raw_d = open(DEST, "rb").read()
    assert raw_d.count(line) == 0, "rerun guard: exact r833 pointer line already in dest"
    eol_d = eol_of(raw_d)
    assert raw_d.endswith(eol_d), "dest tail EOL gate"
    with open(DEST, "ab") as fh:
        fh.write(line + eol_d)
    post_d = open(DEST, "rb").read()
    assert post_d.count(line) == 1, "post-verify r833 pointer line count==1"
    assert len(post_d) <= LIMIT, "dest over line"

    # 4) receipt (merge with prior heal/pit facts if receipt exists)
    receipt = {"round": 693, "machine": "bm-c",
               "action": "direct-write increment (r429/r666/r673 pattern) "
                         "+ truncation heal (line-level union per guard rc3) "
                         "+ r667-precedent pointer migration"}
    if os.path.exists(RECEIPT):
        try:
            receipt = json.load(open(RECEIPT, encoding="utf-8"))
            receipt.setdefault("action", "")
            receipt["action"] += " + fixup legs"
        except Exception:
            pass
    receipt["migration_r833"] = {
        "line_bytes": len(line),
        "sha16": hashlib.sha256(line).hexdigest()[:16],
        "from": "CODELY.md", "to": "research/pit-engine-freeze-editor.md",
        "needle_collision_note": "pit-body attribution shares 'r833 bm-a' text; "
                                 "pointer-line needle = full-line prefix",
        "main_bytes_after_remove": len(post_m),
        "main_under_line": len(post_m) <= LIMIT,
        "dest_bytes_post": len(post_d),
        "dest_under_line": len(post_d) <= LIMIT,
        "verbatim_in_dest": True}
    receipt["main_bytes_post"] = len(post_m)
    receipt["main_under_line"] = len(post_m) <= LIMIT
    receipt["migration_done"] = True
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print("r833 pointer line %dB landed in dest; main %dB; dest %dB"
          % (len(line), len(post_m), len(post_d)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
