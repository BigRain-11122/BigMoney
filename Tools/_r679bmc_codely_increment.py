# -*- coding: utf-8 -*-
"""r679 bm-c CODELY increment batch (D-20261002-06 main-file <=30KB criterion
leg; in-window mandatory trigger = main blob 31,287B > 30,720B after bm-a
r825 first-in pit append, whose commit message designated "next dedicated
increment window per r653 full-seat-yield precedent" = THIS window).
Migrates 1 line / 1 pit verbatim: r825 rebase-UU-markers-polluting-daemon-
state pit -> research/pit-git-resolver.md (mother file, post-split append
convention r441/r669; rebase conflict-window family r787/r794/r808/r817
same-domain per r654/r789 precedent).
Ceremony: r651/r654/r670/r672 lineage -- treasure_guard prescan rc3
recorded (registry hit on CODELY.md, disclosed; verbatim zero-loss
line-level migration is the sanctioned path, content preserved verbatim in
domain file + git history, NOT a deletion), byte+sha16 accounting, zero-loss
assertion (bytes-in-target verbatim + main retained-face identity + main
<=30KB + all pit-* domain files <=30KB), receipt measure-at-use (r653)."""
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
TARGET = os.path.join(ROOT, "research", "pit-git-resolver.md")
RECEIPT = os.path.join(ROOT, "results", "_r679bmc_codely_increment.json")
CREATE_NO_WINDOW = 0x08000000

NEEDLE = "- [2026-10-07 14:3x r825 bm-a]".encode("utf-8")
POINTER = ("- 域指针·r679 bm-c 增量批（2026-10-07 13:5x·触发=主件 31,287B>30,720B〔bm-a r825 首入回弹〕）："
           "r825 rebase UU 标记污染 daemon 状态面坑 1 条 verbatim 迁 pit-git-resolver.md（rebase 冲突窗族）"
           "·收据 _r679bmc_codely_increment.json；新坑律仍先入本件后回扫。").encode("utf-8")


def blob_size(path):
    r = subprocess.run(["git", "cat-file", "-s", ":%s" % os.path.basename(path)],
                       cwd=ROOT, capture_output=True, creationflags=CREATE_NO_WINDOW)
    return int(r.stdout.decode().strip()) if r.returncode == 0 else None


def main():
    # ---- prescan (treasure_guard; rc recorded per r651/r654/r670/r672) ----
    pr = subprocess.run([sys.executable, os.path.join(ROOT, "Tools", "treasure_guard.py"),
                         "prescan", "CODELY.md"], cwd=ROOT, capture_output=True,
                        text=True, encoding="utf-8", errors="replace",
                        creationflags=CREATE_NO_WINDOW)
    prescan_rc = pr.returncode
    prescan_tail = (pr.stdout or "").strip().splitlines()[-1:] or [""]

    main_blob_pre = blob_size(MAIN)
    assert main_blob_pre == 31287, "main blob pre gate: %s" % main_blob_pre

    raw = open(MAIN, "rb").read()
    tgt = open(TARGET, "rb").read()
    assert raw.count(NEEDLE) == 1, "main needle count==1 gate"
    assert tgt.count(NEEDLE) == 0, "already-migrated gate"
    assert raw.endswith(b"\r\n"), "main tail EOL gate"

    idx = raw.find(NEEDLE)
    seg = raw[idx:]
    nl = seg.find(b"\r\n")
    assert nl > 0, "entry terminator gate"
    entry = seg[:nl]                       # verbatim entry bytes, no EOL
    after = seg[nl:]                       # \r\n (nothing after: last line)
    assert after == b"\r\n", "entry-is-last-line gate"
    assert idx + nl + 2 == len(raw), "tail boundary gate"

    # ---- retained-face identity anchors ----
    retained_pre = raw[:idx]
    retained_pre_sha16 = hashlib.sha256(retained_pre).hexdigest()[:16]

    # ---- append entry verbatim to mother domain file (CRLF convention) ----
    assert tgt.endswith(b"\r\n"), "target tail EOL gate"
    tgt_new = tgt + entry + b"\r\n"
    open(TARGET, "wb").write(tgt_new)
    tgt_chk = open(TARGET, "rb").read()
    assert tgt_chk.count(entry) == 1, "bytes-in-target verbatim gate"
    assert tgt_chk.endswith(entry + b"\r\n"), "target append tail gate"

    # ---- main surgery: remove entry line, append pointer line ----
    main_new = retained_pre + POINTER + b"\r\n"
    open(MAIN, "wb").write(main_new)
    main_chk = open(MAIN, "rb").read()
    assert main_chk == main_new, "main write identity gate"
    assert main_chk.count(NEEDLE) == 0, "entry-removed gate"
    assert main_chk.count(POINTER) == 1, "pointer count==1 gate"
    # retained-face identity: bytes before entry unchanged, in place
    assert main_chk[:idx] == retained_pre, "main retained-face identity gate"
    assert hashlib.sha256(main_chk[:idx]).hexdigest()[:16] == retained_pre_sha16

    # ---- LF-normalized (blob-side) size gates ----
    main_lf = main_chk.replace(b"\r\n", b"\n")
    main_blob_post = len(main_lf)
    assert main_blob_post <= 30720, "main <=30KB gate: %d" % main_blob_post
    tgt_lf = tgt_chk.replace(b"\r\n", b"\n")
    tgt_blob_post = len(tgt_lf)
    assert tgt_blob_post <= 30720, "target <=30KB gate: %d" % tgt_blob_post

    dom_sizes = {}
    for name in sorted(os.listdir(os.path.join(ROOT, "research"))):
        if name.startswith("pit-") and name.endswith(".md"):
            b = open(os.path.join(ROOT, "research", name), "rb").read()
            dom_sizes[name] = len(b.replace(b"\r\n", b"\n"))
    over = {k: v for k, v in dom_sizes.items() if v > 30720}
    assert not over, "domain-files <=30KB gate: %s" % over

    receipt = {
        "round": 679,
        "batch": "r679 bm-c CODELY increment (1 line / 1 pit)",
        "trigger": "main blob 31,287B > 30,720B (bm-a r825 first-in append rebound; its designated next-increment window)",
        "prescan_rc": prescan_rc,
        "prescan_tail": prescan_tail[-1] if prescan_tail else "",
        "prescan_note": "registry hit on CODELY.md disclosed per r651/r654/r670/r672 lineage; verbatim zero-loss line-level migration (content preserved verbatim in pit-git-resolver.md + git history, not a deletion)",
        "entry_head": NEEDLE.decode("utf-8"),
        "entry_bytes": len(entry),
        "entry_sha16": hashlib.sha256(entry).hexdigest()[:16],
        "target": "research/pit-git-resolver.md",
        "target_blob_pre_lf": len(tgt.replace(b"\r\n", b"\n")),
        "target_blob_post_lf": tgt_blob_post,
        "bytes_in_target_verbatim": True,
        "main_blob_pre": main_blob_pre,
        "main_blob_post": main_blob_post,
        "main_margin_bytes": 30720 - main_blob_post,
        "main_retained_face_sha16": retained_pre_sha16,
        "pointer_bytes": len(POINTER),
        "pointer_sha16": hashlib.sha256(POINTER).hexdigest()[:16],
        "zero_loss_assert": "entry bytes verbatim in target (count==1) + main retained-face identity (sha16 equal) + main <=30KB + all pit-* <=30KB",
        "domain_files_max": max(dom_sizes.values()),
        "domain_files_count": len(dom_sizes),
    }
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print("INCREMENT OK: entry %dB sha16=%s -> pit-git-resolver.md; main %d -> %dB (margin %dB); prescan rc=%d" % (
        len(entry), receipt["entry_sha16"], main_blob_pre, main_blob_post,
        receipt["main_margin_bytes"], prescan_rc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
