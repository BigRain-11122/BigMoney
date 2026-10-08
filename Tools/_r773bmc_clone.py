"""r773 bm-c lineage clone gate (r749/r772 pattern): sequence-sensitive double
replacement 772->773 over the four r772 tool faces (s05 probe / s6 driver /
s6 ignite / qa ignite), stale-token zero gate ((?<!\\d)772(?!\\d) per r639
\\b-false-edge pit law), py_compile gate on all outputs, sha16+bytes receipt.
r773 post-clone narrative fix (facts-driven, pre-checked this window 19:1x):
qa collision case #10 CONFIRMED (qa/smoke-r773.md blob 54125349 already on
origin/main = bm-b pack; equity-curve-r773.png blob 4c8b8e6a same handling)
-> collision narrative updated to case #10 + disclosure canon list extended
with r772. Pattern credit: Tools/_r749bmc clone gate family."""
import hashlib
import json
import os
import py_compile
import re
import datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
SRC = os.path.join(REPO, "Tools")
FILES = [
    "_r772bmc_s05.py",
    "_r772bmc_s6.py",
    "_r772bmc_s6_ignite.py",
    "_r772bmc_qa_ignite.py",
]
# order-sensitive: r772->r773 first, then bare 772 (ROUND=, --round, paths)
REPL = [("r772", "r773"), ("772", "773")]
# qa_ignite collision narrative fix (case #9 -> #10 with real r773 blob sha)
QA_FIX = [
    ("blob 12edbb33, bm-b pack) -> collision case #9, follow",
     "blob 54125349, bm-b pack) -> collision case #10, follow"),
    ("r761/r764/r766/r767/r768/r770/r771 disclosure canon",
     "r761/r764/r766/r767/r768/r770/r771/r772 disclosure canon"),
]


def main():
    receipt = {"round": 773, "machine": "bm-c",
               "ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
               "files": []}
    for name in FILES:
        with open(os.path.join(SRC, name), encoding="utf-8") as fh:
            text = fh.read()
        for old, new in REPL:
            text = text.replace(old, new)
        # stale gate BEFORE narrative fixes: bare 772 must be fully gone
        stale = re.findall(r"(?<!\d)772(?!\d)", text)
        assert not stale, "stale 772 tokens in %s: %d" % (name, len(stale))
        if name == "_r772bmc_qa_ignite.py":
            for old, new in QA_FIX:
                assert old in text, "qa_fix needle missing: %r" % old
                text = text.replace(old, new)
            # after QA_FIX the ONLY legal 772 = canon citation "/r772" (1x)
            post = re.findall(r"/r772(?!\d)", text)
            assert len(post) == 1, "canon-citation 772 count != 1: %d" % len(post)
            bare = [m for m in re.finditer(r"(?<!\d)772(?!\d)", text)
                    if text[m.start() - 2:m.start()] != "/r"]
            assert not bare, "bare 772 after QA_FIX: %d" % len(bare)
            stale = []  # gate satisfied: 0 stale, 1 canon citation
        dst = os.path.join(SRC, name.replace("r772", "r773"))
        with open(dst, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        py_compile.compile(dst, doraise=True)
        blob = open(dst, "rb").read()
        receipt["files"].append({
            "src": name, "dst": os.path.basename(dst),
            "bytes": len(blob), "sha16": hashlib.sha256(blob).hexdigest()[:16],
            "stale772": len(stale), "compile": "ok",
        })
    out = os.path.join(REPO, "results", "_r773bmc_clone_receipt.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1, ensure_ascii=False)
    print("CLONE_OK r773 files=%d stale772=0 compile=ok receipt=%s"
          % (len(FILES), out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
