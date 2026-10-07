"""r739 bm-c CODELY mini-split: new-pit append pushes main over 30,720B cap
(disk 30,422B + ~430B new pit entry) -> migrate 1 entry verbatim to domain
file per D-20261002-06 standing law. Ritual: r441/r731/r736 same-form.
- r736 (clone-replace misses bare numeric round arg, QA ignite) ->
  research/pit-lineage.md [tool-lineage clone family; charter per r592
  split: chain/tool lineage clone/legdiff/close/bookkeeping scripts]
- New r739 pit (CAS update-index --cacheinfo comma-form rejection on this
  git build) STAYS in main (new-pit-first law) + r739 pointer row.
treasure_guard prescan rc recorded (r651/r654/r670/r703/r731/r736 precedent:
D-06 authorized byte-accounted verbatim migration, not a deletion).
Byte faces: disk CRLF-dominant (autocrlf LF blob on commit); all math on
disk bytes, cap 30,720B, per r735/r736 receipt convention.
"""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
CAP = 30720
TARGETS = {"r736": os.path.join(ROOT, "research", "pit-lineage.md")}
PREFIXES = {"r736": "- [2026-10-08 06:1x r736 bm-c]"}
NEW_PIT = (
    "- [2026-10-08 07:1x r739 bm-c] **CAS 直投 update-index --cacheinfo 连等形态拒收坑（OH- 集团树外科推送实弹·fetch 重建基座一次过）**：本机 git 的 update-index --cacheinfo=<mode>,<sha>,<path> 连等形态报「option `cacheinfo' takes no value」拒收（老版本语法面）；正法=空格三参形态 --cacheinfo <mode> <sha> <path> 必过；CAS 撞拒（fetch first）=fetch 重建基座重投一次即达（实弹：base 前移 c78d0b5→673fac4 竞争窗吸收·ed9140adbcb4 落集团树 TIP VERIFIED）。How to apply：CAS 直投模板（r849 族）在老 git 机上必带空格三参形态；撞拒=重 fetch+重跑脚本（幂等·防重复投递门=cat-file -e origin/main:<path> 前置）。")
POINTER_TPL = (
    "- \u57df\u6307\u9488\u00b7r739 bm-c mini-split\uff0810-08 07:1x\u00b7\u65b0"
    "\u5751\u5f8b append \u8d8a\u5e3d\u89e6\u53d1\uff5b30,422B+\u65b0\u6761>"
    "30,720B\uff5d\u00b7\u4eea\u5f0f r441/r731/r736 \u540c\u6b3e\uff09\uff1a\u4e3b"
    "\u4ef6 1 \u884c verbatim \u8fc1\u51fa\u2014\u2014r736 \u8f6e\u9a71\u52a8\u811a"
    "\u672c\u514b\u9686\u6f0f\u88f8\u6570\u5b57\u53c2\u6570\u5751\uff08{b736}B"
    "\uff09\u2192pit-lineage.md\uff3b\u5de5\u5177\u8840\u7edf\u590d\u5236\u65cf"
    "\u00b7\u514b\u9686\u66ff\u6362\u673a\u68b0\u9762\uff3d\uff1br739 CAS \u76f4"
    "\u6295 cacheinfo \u8fde\u7b49\u5f62\u6001\u62d2\u6536\u5751\uff08\u65b0\u5f8b"
    "\uff09\u7559\u4e3b\u4ef6\u2014\u2014\u9010\u6761\u5b57\u8282+sha16 \u5bf9\u8d26"
    "=receipt results/_r739bmc_codely_minisplit.json\uff08\u96f6\u4e22\u5931\u65ad"
    "\u8a00=\u9010\u5757 bytes in target verbatim+\u4e3b\u4ef6\u4fdd\u7559\u9762"
    "\u6052\u7b49+\u4e3b/\u57df\u4ef6 \u226430KB\u00b7prescan rc \u7555\u75d5"
    "\uff09\uff1b\u65b0\u5751\u5f8b\u4ecd\u5148\u5165\u672c\u4ef6\u540e\u56de\u626b"
    "\u3002")


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main():
    receipt = {"round": 739, "op": "codely-minisplit-r739", "cap": CAP}
    # 1) prescan (record rc per r651/r736 precedent)
    p = subprocess.run([sys.executable, os.path.join(ROOT, "Tools",
                       "treasure_guard.py"), "prescan", MAIN]
                       + list(TARGETS.values()), capture_output=True)
    receipt["prescan_rc"] = p.returncode
    receipt["prescan_note"] = ("rc recorded per r651/r654/r670/r703/r731/r736 "
                               "precedent; D-06 authorized byte-accounted "
                               "verbatim migration (not a deletion)")

    main_bytes = open(MAIN, "rb").read()
    receipt["main_bytes_before"] = len(main_bytes)
    text = main_bytes.decode("utf-8")
    lines = text.splitlines(keepends=True)
    # 2) locate + extract the single-line block
    blocks = {}
    keep = []
    for ln in lines:
        hit = None
        for key, pfx in PREFIXES.items():
            if ln.startswith(pfx):
                hit = key
                break
        if hit:
            if hit in blocks:
                print("FATAL: duplicate prefix %s" % hit)
                return 3
            blocks[hit] = ln.encode("utf-8")
        else:
            keep.append(ln)
    if set(blocks) != set(PREFIXES):
        print("FATAL: missing blocks: %s" % (set(PREFIXES) - set(blocks)))
        return 3
    removed = sum(len(b) for b in blocks.values())
    receipt["removed_bytes"] = removed

    # 3) append block verbatim to target
    receipt["migrated"] = []
    for key, tgt in TARGETS.items():
        tb = open(tgt, "rb").read()
        with open(tgt, "ab") as fh:
            fh.write(blocks[key])
        after = open(tgt, "rb").read()
        ok = after.startswith(tb) and after[len(tb):] == blocks[key] \
            and blocks[key] in after
        receipt["migrated"].append({
            "entry": key, "bytes": len(blocks[key]), "sha16": sha16(blocks[key]),
            "to": os.path.relpath(tgt, ROOT).replace("\\", "/"),
            "target_bytes_before": len(tb), "target_bytes_after": len(after),
            "bytes_in_target_verbatim": ok})
        if not ok:
            print("FATAL: verbatim append failed for %s" % key)
            return 3

    # 4) rebuild main: retained lines + new pit + pointer row
    new_pit_b = (NEW_PIT + "\r\n").encode("utf-8")
    pointer_b = (POINTER_TPL.format(b736=len(blocks["r736"])) + "\r\n") \
        .encode("utf-8")
    new_main = ("".join(keep)).encode("utf-8") + new_pit_b + pointer_b
    with open(MAIN, "wb") as fh:
        fh.write(new_main)
    after_bytes = open(MAIN, "rb").read()
    # 5) zero-loss assertions
    kept_identity = after_bytes == new_main
    blocks_gone = all(b not in after_bytes for b in blocks.values())
    eq_main = len(after_bytes) == receipt["main_bytes_before"] - removed \
        + len(new_pit_b) + len(pointer_b)
    receipt["main_bytes_after"] = len(after_bytes)
    receipt["added_bytes"] = {"new_pit_r739": len(new_pit_b),
                              "pointer_row": len(pointer_b)}
    receipt["byte_equation"] = ("main_after == main_before - removed + "
                                "new_pit + pointer: %s" % eq_main)
    receipt["retained_identity"] = kept_identity
    receipt["blocks_absent_from_main"] = blocks_gone
    # 6) cap checks
    caps = {"CODELY.md": len(after_bytes)}
    for tgt in TARGETS.values():
        caps[os.path.relpath(tgt, ROOT).replace("\\", "/")] = \
            os.path.getsize(tgt)
    receipt["cap_face"] = caps
    receipt["all_under_cap"] = all(v <= CAP for v in caps.values())
    ok_all = kept_identity and blocks_gone and eq_main \
        and receipt["all_under_cap"] \
        and all(m["bytes_in_target_verbatim"] for m in receipt["migrated"])

    out = os.path.join(ROOT, "results", "_r739bmc_codely_minisplit.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1, ensure_ascii=False)
    print(json.dumps({k: receipt[k] for k in
                      ("prescan_rc", "main_bytes_before", "removed_bytes",
                       "main_bytes_after", "all_under_cap", "byte_equation",
                       "retained_identity", "blocks_absent_from_main")},
                     indent=1))
    print("receipt -> %s  ok_all=%s" % (out, ok_all))
    return 0 if ok_all else 3


if __name__ == "__main__":
    raise SystemExit(main())
