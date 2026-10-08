"""r772 bm-c lineage clone gate (r749 pattern): sequence-sensitive double
replacement 771->772 over the four r771 tool faces (s05 probe / s6 driver /
s6 ignite / qa ignite), stale-token zero gate ((?<!\\d)771(?!\\d) per r639
\\b-false-edge pit law), py_compile gate on all outputs, sha16+bytes receipt.
r772 post-clone narrative fixes (facts-driven, pre-checked this window):
qa collision case #9 CONFIRMED (qa/smoke-r772.md blob 12edbb33 already on
origin/main = bm-b pack) -> disclosure canon list extended with r771.
Pattern credit: Tools/_r749bmc clone gate family."""
import hashlib
import json
import os
import py_compile
import re
import datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
SRC = os.path.join(REPO, "Tools")
FILES = [
    "_r771bmc_s05.py",
    "_r771bmc_s6.py",
    "_r771bmc_s6_ignite.py",
    "_r771bmc_qa_ignite.py",
]
# order-sensitive: r771->r772 first, then bare 771 (ROUND=, --round, paths)
REPL = [("r771", "r772"), ("771", "772")]
# qa_ignite collision narrative fix (case #8 -> #9 with real r772 blob sha)
QA_FIX = [
    ("blob 9bf1dcfb, bm-b pack) -> collision case #8, follow",
     "blob 12edbb33, bm-b pack) -> collision case #9, follow"),
    ("r761/r764/r766/r767/r768/r770 disclosure canon",
     "r761/r764/r766/r767/r768/r770/r771 disclosure canon"),
]


def main():
    receipt = {"round": 772, "machine": "bm-c",
               "ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
               "files": []}
    for name in FILES:
        with open(os.path.join(SRC, name), encoding="utf-8") as fh:
            text = fh.read()
        for old, new in REPL:
            text = text.replace(old, new)
        # stale gate BEFORE narrative fixes: bare 771 must be fully gone
        stale = re.findall(r"(?<!\d)771(?!\d)", text)
        assert not stale, "stale 771 tokens in %s: %d" % (name, len(stale))
        if name == "_r771bmc_qa_ignite.py":
            for old, new in QA_FIX:
                assert old in text, "qa_fix needle missing: %r" % old
                text = text.replace(old, new)
            # after QA_FIX the ONLY legal 771 = canon citation "/r771" (1x)
            post = re.findall(r"/r771(?!\d)", text)
            assert len(post) == 1, "canon-citation 771 count != 1: %d" % len(post)
            bare = [m for m in re.finditer(r"(?<!\d)771(?!\d)", text)
                    if text[m.start() - 2:m.start()] != "/r"]
            assert not bare, "bare 771 after QA_FIX: %d" % len(bare)
            stale = []  # gate satisfied: 0 stale, 1 canon citation
        dst = os.path.join(SRC, name.replace("r771", "r772"))
        with open(dst, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        py_compile.compile(dst, doraise=True)
        blob = open(dst, "rb").read()
        receipt["files"].append({
            "src": name, "dst": os.path.basename(dst),
            "bytes": len(blob), "sha16": hashlib.sha256(blob).hexdigest()[:16],
            "stale771": len(stale), "compile": "ok",
        })
    out = os.path.join(REPO, "results", "_r772bmc_clone_receipt.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1, ensure_ascii=False)
    print("CLONE_OK r772 files=%d stale771=0 compile=ok receipt=%s"
          % (len(FILES), out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
