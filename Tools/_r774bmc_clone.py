"""r774 bm-c lineage clone gate (r749/r773 pattern): sequence-sensitive double
replacement 773->774 over the four r773 tool faces (s05 probe / s6 driver /
s6 ignite / qa ignite), stale-token zero gate ((?<!\\d)773(?!\\d) per r639
\\b-false-edge pit law), py_compile gate on all outputs, sha16+bytes receipt.
r774 post-clone narrative fixes (facts-driven, pre-checked this window 19:3x):
(a) qa collision case #11 CONFIRMED (qa/smoke-r774.md blob 6360ac35 already
on origin/main = bm-b pack; equity-curve-r774.png blob 5c0d0a46 same
handling) -> collision narrative updated to case #11 + disclosure canon list
extended with r773; (b) s6 watch-faces window stamp 18:4x -> 19:3x.
Stale gate BEFORE narrative fixes (r772 law); canon-citation exemption assert
after fix (only legal bare 773 = "/r773" citation, exactly 1x).
Pattern credit: Tools/_r773bmc_clone.py (canonical clone chain)."""
import hashlib
import json
import os
import py_compile
import re
import datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
SRC = os.path.join(REPO, "Tools")
FILES = [
    "_r773bmc_s05.py",
    "_r773bmc_s6.py",
    "_r773bmc_s6_ignite.py",
    "_r773bmc_qa_ignite.py",
]
# order-sensitive: r773->r774 first, then bare 773 (ROUND=, --round, paths)
REPL = [("r773", "r774"), ("773", "774")]
# qa_ignite collision narrative fix (case #10 -> #11 with real r774 blob sha)
QA_FIX = [
    ("blob 54125349, bm-b pack) -> collision case #10, follow",
     "blob 6360ac35, bm-b pack) -> collision case #11, follow"),
    ("r761/r764/r766/r767/r768/r770/r771/r772 disclosure canon",
     "r761/r764/r766/r767/r768/r770/r771/r772/r773 disclosure canon"),
]
# s6 watch-faces window stamp refresh (facts-driven, no-op safe)
S6_FIX = [
    ("cutoff 09-30 held through 18:4x", "cutoff 09-30 held through 19:3x"),
]


def main():
    receipt = {"round": 774, "machine": "bm-c",
               "ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
               "files": []}
    for name in FILES:
        with open(os.path.join(SRC, name), encoding="utf-8") as fh:
            text = fh.read()
        for old, new in REPL:
            text = text.replace(old, new)
        # stale gate BEFORE narrative fixes: bare 773 must be fully gone
        stale = re.findall(r"(?<!\d)773(?!\d)", text)
        assert not stale, "stale 773 tokens in %s: %d" % (name, len(stale))
        if name == "_r773bmc_qa_ignite.py":
            for old, new in QA_FIX:
                assert old in text, "qa_fix needle missing: %r" % old
                text = text.replace(old, new)
            # after QA_FIX the ONLY legal 773 = canon citation "/r773" (1x)
            post = re.findall(r"/r773(?!\d)", text)
            assert len(post) == 1, "canon-citation 773 count != 1: %d" % len(post)
            bare = [m for m in re.finditer(r"(?<!\d)773(?!\d)", text)
                    if text[m.start() - 2:m.start()] != "/r"]
            assert not bare, "bare 773 after QA_FIX: %d" % len(bare)
            stale = []  # gate satisfied: 0 stale, 1 canon citation
        if name == "_r773bmc_s6.py":
            for old, new in S6_FIX:
                if old in text:
                    text = text.replace(old, new)
        dst = os.path.join(SRC, name.replace("r773", "r774"))
        with open(dst, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        py_compile.compile(dst, doraise=True)
        blob = open(dst, "rb").read()
        receipt["files"].append({
            "src": name, "dst": os.path.basename(dst),
            "bytes": len(blob), "sha16": hashlib.sha256(blob).hexdigest()[:16],
            "stale773": len(stale), "compile": "ok",
        })
    out = os.path.join(REPO, "results", "_r774bmc_clone_receipt.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1, ensure_ascii=False)
    print("CLONE_OK r774 files=%d stale773=0 compile=ok receipt=%s"
          % (len(FILES), out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
