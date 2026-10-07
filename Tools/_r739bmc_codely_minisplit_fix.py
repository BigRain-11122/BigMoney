"""r739 bm-c CODELY mini-split FIX pass: first pass freed 753B but new-pit
(+pointer) face 1,338B exceeded it (main 31,007B > 30,720B cap, byte
equation held, zero-loss held). Second migration per r735 fix-pass
precedent: r703 E42 porcelain-parse pit (800B, mature new-pit from r703
batch, re-sweep age reached) -> research/pit-git-parse.md [git-output
parsing family]. Pointer row rewritten to carry both migrations. Receipt
results/_r739bmc_codely_minisplit.json updated in place (second-pass
block appended, caps recomputed)."""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
CAP = 30720
TARGET = os.path.join(ROOT, "research", "pit-git-parse.md")
PREFIX = "- [2026-10-07 22:2x r703 bm-c]"
POINTER_PREFIX = "- \u57df\u6307\u9488\u00b7r739 bm-c mini-split"
POINTER_NEW = (
    "- \u57df\u6307\u9488\u00b7r739 bm-c mini-split\uff0810-08 07:1x\u00b7\u65b0"
    "\u5751\u5f8b append \u8d8a\u5e3d\u89e6\u53d1\uff5b30,422B+\u65b0\u6761>"
    "30,720B\uff5d\u00b7\u4eea\u5f0f r441/r731/r736 \u540c\u6b3e\u00b7\u53cc\u8fc1"
    "\u884c\uff09\uff1a\u4e3b\u4ef6 2 \u884c verbatim \u8fc1\u51fa\u2014\u2014"
    "r736 \u8f6e\u9a71\u52a8\u811a\u672c\u514b\u9686\u6f0f\u88f8\u6570\u5b57\u53c2"
    "\u6570\u5751\uff08753B\uff09\u2192pit-lineage.md\uff3b\u5de5\u5177\u8840\u7edf"
    "\u590d\u5236\u65cf\u00b7\u514b\u9686\u66ff\u6362\u673a\u68b0\u9762\uff3d"
    "+r703 E42 porcelain \u591a\u884c\u5355\u4e32\u5047 0 UU \u89e3\u6790\u5751"
    "\uff08800B\uff09\u2192pit-git-parse.md\uff3b\u89e3\u6790 git \u8f93\u51fa\u65cf"
    "\u00b7r703 \u6279\u65b0\u5f8b\u56de\u626b\u5f52\u4f4d\uff3d\uff1br739 CAS "
    "\u76f4\u6295 cacheinfo \u8fde\u7b49\u5f62\u6001\u62d2\u6536\u5751\uff08\u65b0"
    "\u5f8b\uff09\u7559\u4e3b\u4ef6\u2014\u2014\u9010\u6761\u5b57\u8282+sha16 \u5bf9"
    "\u8d26=receipt results/_r739bmc_codely_minisplit.json\uff08\u96f6\u4e22\u5931"
    "\u65ad\u8a00=\u9010\u5757 bytes in target verbatim+\u4e3b\u4ef6\u4fdd\u7559\u9762"
    "\u6052\u7b49+\u4e3b/\u57df\u4ef6 \u226430KB\u00b7prescan rc \u7555\u75d5\uff09"
    "\uff1b\u65b0\u5751\u5f8b\u4ecd\u5148\u5165\u672c\u4ef6\u540e\u56de\u626b\u3002")
RECEIPT = os.path.join(ROOT, "results", "_r739bmc_codely_minisplit.json")


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main():
    p = subprocess.run([sys.executable, os.path.join(ROOT, "Tools",
                       "treasure_guard.py"), "prescan", MAIN, TARGET],
                       capture_output=True)
    prescan_rc = p.returncode

    main_bytes = open(MAIN, "rb").read()
    text = main_bytes.decode("utf-8")
    lines = text.splitlines(keepends=True)
    block = None
    keep = []
    pointer_old_b = None
    for ln in lines:
        if ln.startswith(PREFIX):
            if block is not None:
                print("FATAL: duplicate r703 prefix")
                return 3
            block = ln.encode("utf-8")
        elif ln.startswith(POINTER_PREFIX):
            if pointer_old_b is not None:
                print("FATAL: duplicate r739 pointer")
                return 3
            pointer_old_b = ln.encode("utf-8")
        else:
            keep.append(ln)
    if block is None or pointer_old_b is None:
        print("FATAL: missing r703 block or r739 pointer")
        return 3

    tb = open(TARGET, "rb").read()
    with open(TARGET, "ab") as fh:
        fh.write(block)
    ta = open(TARGET, "rb").read()
    ok_target = ta.startswith(tb) and ta[len(tb):] == block and block in ta
    if not ok_target:
        print("FATAL: verbatim append failed")
        return 3

    pointer_new_b = (POINTER_NEW + "\r\n").encode("utf-8")
    new_main = ("".join(keep)).encode("utf-8") + pointer_new_b
    with open(MAIN, "wb") as fh:
        fh.write(new_main)
    after = open(MAIN, "rb").read()

    kept_identity = after == new_main
    block_gone = block not in after
    pointer_old_gone = pointer_old_b not in after
    eq = len(after) == len(main_bytes) - len(block) - len(pointer_old_b) \
        + len(pointer_new_b)

    caps = {"CODELY.md": len(after),
            "research/pit-lineage.md": os.path.getsize(
                os.path.join(ROOT, "research", "pit-lineage.md")),
            "research/pit-git-parse.md": len(ta)}
    all_under = all(v <= CAP for v in caps.values())

    receipt = json.load(open(RECEIPT, encoding="utf-8"))
    receipt["fix_pass"] = {
        "prescan_rc": prescan_rc,
        "second_migration": {
            "entry": "r703 E42 porcelain multi-line single-string false-0-UU",
            "bytes": len(block), "sha16": sha16(block),
            "to": "research/pit-git-parse.md",
            "target_bytes_before": len(tb), "target_bytes_after": len(ta),
            "bytes_in_target_verbatim": ok_target},
        "pointer_row_rewritten": {"old_bytes": len(pointer_old_b),
                                  "new_bytes": len(pointer_new_b)},
        "main_bytes_before_pass2": len(main_bytes),
        "main_bytes_after": len(after),
        "byte_equation_pass2": eq,
        "retained_identity": kept_identity,
        "block_absent": block_gone,
        "pointer_old_absent": pointer_old_gone,
        "cap_face_pass2": caps,
        "all_under_cap_pass2": all_under}
    receipt["cap_face"] = caps
    receipt["all_under_cap"] = all_under
    with open(RECEIPT, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1, ensure_ascii=False)
    ok_all = kept_identity and block_gone and pointer_old_gone and eq \
        and all_under and ok_target
    print(json.dumps({"prescan_rc": prescan_rc,
                      "main_before_pass2": len(main_bytes),
                      "main_after": len(after),
                      "pit-git-parse_after": len(ta),
                      "all_under_cap": all_under,
                      "eq": eq, "ok_all": ok_all}, indent=1))
    return 0 if ok_all else 3


if __name__ == "__main__":
    raise SystemExit(main())
