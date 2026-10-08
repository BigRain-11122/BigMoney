# -*- coding: utf-8 -*-
"""r775 bm-c lineage clone gate (r749/r774 pattern): sequence-sensitive double
replacement 774->775 over the four r774 tool faces (s05 probe / s6 driver /
s6 ignite / qa ignite), stale-token zero gate ((?<!\\d)774(?!\\d) per r639
\\b-false-edge pit law), py_compile gate on all outputs, sha16+bytes receipt.
r775 post-clone narrative fixes (facts-driven, pre-checked this window 20:0x):
(a) qa collision probe for r775 = CLEAN FIRST-WRITE (qa/smoke-r775.md and
qa/equity-curve-r775.png both ABSENT from origin/main ls-tree probe 20:0x,
next-ptr item-5 executed) -> r774's case-#11 collision narrative REPLACED
with the clean-probe fact (retired disclosure-canon list dropped with it);
(b) s6 watch-faces: 10-08 post-holiday FIRST-BAR landing attempt replaces
the r774 sina-late-bar retry stamp (cutoff 09-30 held through 19:47 close;
fund_premium 10-08 NAV first-snapshot attempt; cta_p1 first-bar wiring).
Stale gate BEFORE narrative fixes (r772 law); post-fix bare 774 re-check on
qa face (citation-free fix text, zero legal residual). Pattern credit:
Tools/_r774bmc_clone.py (canonical clone chain)."""
import hashlib
import json
import os
import py_compile
import re
import datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
SRC = os.path.join(REPO, "Tools")
FILES = [
    "_r774bmc_s05.py",
    "_r774bmc_s6.py",
    "_r774bmc_s6_ignite.py",
    "_r774bmc_qa_ignite.py",
]
# order-sensitive: r774->r775 first, then bare 774 (ROUND=, --round, paths)
REPL = [("r774", "r775"), ("774", "775")]
# qa_ignite collision narrative fix (r774 case-#11 collision -> r775 clean)
QA_FIX = [
    ("Pre-ignite collision probe result: qa/smoke-r775.md ALREADY on origin/main\n"
     "(blob 6360ac35, bm-b pack) -> collision case #11, follow\n"
     "r761/r764/r766/r767/r768/r770/r771/r772/r773 disclosure canon (deterministic same frozen\n"
     "numbers, same-path overwrite, bm-b version git-preserved via its own commit).",
     "Pre-ignite collision probe result: qa/smoke-r775.md NOT on origin/main\n"
     "(r775 ls-tree probe 20:0x window, next-ptr item-5 executed; det-95th\n"
     "clean first-write, zero collision, no disclosure canon needed)."),
]
# s6 watch-faces window stamp refresh (facts-driven, no-op safe)
S6_FIX = [
    ("update_daily sina 10-08 late-bar self-heal retry\n"
     "(cutoff 09-30 held through 19:3x); update_fund_premium fresh no-op\n"
     "expected (09-30 NAV covered); cta_p1_paper first-bar wiring (pending\n"
     "bar); W189 seat reserved by bm-a -- engine lane untouched by bm-c.",
     "update_daily 10-08 post-holiday FIRST-BAR landing attempt (cutoff\n"
     "09-30 held through 19:47 close; bar due after 15:30, sina lag watch);\n"
     "update_fund_premium 10-08 NAV first-snapshot attempt; cta_p1_paper\n"
     "first-bar wiring (fires when the 10-08 bar lands); W189 seat reserved\n"
     "by bm-a -- engine lane untouched by bm-c."),
]


def main():
    receipt = {"round": 775, "machine": "bm-c",
               "ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
               "files": []}
    for name in FILES:
        with open(os.path.join(SRC, name), encoding="utf-8") as fh:
            text = fh.read()
        for old, new in REPL:
            text = text.replace(old, new)
        # stale gate BEFORE narrative fixes: bare 774 must be fully gone
        stale = re.findall(r"(?<!\d)774(?!\d)", text)
        assert not stale, "stale 774 tokens in %s: %d" % (name, len(stale))
        if name == "_r774bmc_qa_ignite.py":
            for old, new in QA_FIX:
                assert old in text, "qa_fix needle missing: %r" % old[:60]
                text = text.replace(old, new)
            # after QA_FIX zero bare 774 (citation-free replacement text)
            bare = re.findall(r"(?<!\d)774(?!\d)", text)
            assert not bare, "bare 774 after QA_FIX: %d" % len(bare)
            stale = []  # gate satisfied: 0 stale, 0 citation residual
        if name == "_r774bmc_s6.py":
            for old, new in S6_FIX:
                assert old in text, "s6_fix needle missing: %r" % old[:60]
                text = text.replace(old, new)
        dst = os.path.join(SRC, name.replace("r774", "r775"))
        with open(dst, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        py_compile.compile(dst, doraise=True)
        blob = open(dst, "rb").read()
        receipt["files"].append({
            "src": name, "dst": os.path.basename(dst),
            "bytes": len(blob), "sha16": hashlib.sha256(blob).hexdigest()[:16],
            "stale774": len(stale), "compile": "ok",
        })
    out = os.path.join(REPO, "results", "_r775bmc_clone_receipt.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1, ensure_ascii=False)
    print("CLONE_OK r775 files=%d stale774=0 compile=ok receipt=%s"
          % (len(FILES), out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
