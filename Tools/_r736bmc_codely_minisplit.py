"""r736 bm-c CODELY mini-split: new-pit append pushes main over 30,720B cap
(disk 30,654B + ~520B new pit entry) -> migrate 2 entries verbatim to domain
files per D-20261002-06 standing law. Ritual: r441/r731/r735 same-form.
- r847 (cross-machine no-BOM ps1 GBK parse crash) -> research/pit-encoding.md
  [PS-host encoding family, r521/r666 kin]
- r849 (surgical push double pit: NUL in -F msg + push missing repo param)
  -> research/pit-git-staged.md [commit entry gate + push arg family, r731/r734 kin]
- New r736 pit (clone-replace misses bare numeric round arg) STAYS in main
  (new-pit-first law) + r736 pointer row.
treasure_guard prescan rc recorded (r651/r654/r670/r703/r731/r735 precedent:
D-06 authorized byte-accounted verbatim migration, not a deletion).
Byte faces: disk CRLF-dominant (autocrlf LF blob on commit); all math on
disk bytes, cap 30,720B, per r735 receipt convention.
"""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
CAP = 30720
TARGETS = {"r847": os.path.join(ROOT, "research", "pit-encoding.md"),
           "r849": os.path.join(ROOT, "research", "pit-git-staged.md")}
PREFIXES = {"r847": "- [2026-10-07 22:5x r847 bm-a]",
            "r849": "- [2026-10-07 23:4x r849 bm-a]"}
NEW_PIT = (
    u"""- [2026-10-08 06:1x r736 bm-c] **轮驱动脚本克隆替换漏裸数字参数坑（QA ignite 实弹·3 秒内自证捕获·杀错标 runner 重启零损失）**：克隆带显式 --round 数字参数的轮驱动脚本（_r7NNbmc_qa_ignite.py 族）时 `-replace 'r735','r736'` 只覆盖 rNNN 形——Popen 参数表 `"735"` 与 print 文案 round=735 不含 r 前缀=漏改，点火即产错标 QA 包（r640/r758 显式轮标法·错标=红）；正法=克隆替换双模式（rNNN 形+带引号裸 NNN 形两趟）+点火后 3 秒内读 runner .out 首行核 round 标签，错标即 Stop-Process 杀+删错标产物+重启。How to apply：凡克隆轮号脚本必双模式替换+点火即验标（本条 3 秒窗捕获即得救于验标步）。""")
POINTER_TPL = (
    "- \u57df\u6307\u9488\u00b7r736 bm-c mini-split\uff0810-08 06:2x\u00b7\u65b0"
    "\u5751\u5f8b append \u8d8a\u5e3d\u89e6\u53d1\uff5b30,654B+\u65b0\u6761>"
    "30,720B\uff5d\u00b7\u4eea\u5f0f r441/r731/r735 \u540c\u6b3e\uff09\uff1a\u4e3b"
    "\u4ef6 2 \u884c verbatim \u8fc1\u51fa\u2014\u2014r847 \u8de8\u673a\u90e8\u7f72"
    "\u65e0 BOM ps1 GBK \u89e3\u6790\u70b8\u5751\uff08{b847}B\uff09\u2192pit-"
    "encoding.md\uff3bPS \u5bbf\u4e3b\u7f16\u7801\u65cf\u00b7r521/r666 \u540c\u57df"
    "\uff3d+r849 \u5916\u79d1\u63a8\u9001\u53cc\u5751\uff08{b849}B\uff09\u2192pit-"
    "git-staged.md\uff3bcommit \u5165\u573a\u95e8+push \u53c2\u6570\u65cf\u00b7"
    "r731/r734 \u540c\u57df\uff3d\uff1br736 \u8f6e\u9a71\u52a8\u514b\u9686\u6f0f"
    "\u88f8\u6570\u5b57\u53c2\u6570\u5751\uff08\u65b0\u5f8b\uff09\u7559\u4e3b\u4ef6"
    "\u2014\u2014\u9010\u6761\u5b57\u8282+sha16 \u5bf9\u8d26=receipt results/_r736"
    "bmc_codely_minisplit.json\uff08\u96f6\u4e22\u5931\u65ad\u8a00=\u9010\u5757 "
    "bytes in target verbatim+\u4e3b\u4ef6\u4fdd\u7559\u9762\u6052\u7b49+\u4e3b/"
    "\u57df\u4ef6 \u226430KB\u00b7prescan rc \u7559\u75d5\uff09\uff1b\u65b0\u5751"
    "\u5f8b\u4ecd\u5148\u5165\u672c\u4ef6\u540e\u56de\u626b\u3002")


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main():
    receipt = {"round": 736, "op": "codely-minisplit-r736", "cap": CAP}
    # 1) prescan (record rc per r651/r735 precedent)
    p = subprocess.run([sys.executable, os.path.join(ROOT, "Tools",
                       "treasure_guard.py"), "prescan", MAIN]
                       + list(TARGETS.values()), capture_output=True)
    receipt["prescan_rc"] = p.returncode
    receipt["prescan_note"] = ("rc recorded per r651/r654/r670/r703/r731/r735 "
                               "precedent; D-06 authorized byte-accounted "
                               "verbatim migration (not a deletion)")

    main_bytes = open(MAIN, "rb").read()
    receipt["main_bytes_before"] = len(main_bytes)
    text = main_bytes.decode("utf-8")
    lines = text.splitlines(keepends=True)
    # 2) locate + extract the two single-line blocks
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

    # 3) append blocks verbatim to targets
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
    pointer_b = (POINTER_TPL.format(b847=len(blocks["r847"]),
                                    b849=len(blocks["r849"])) + "\r\n") \
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
    receipt["added_bytes"] = {"new_pit_r736": len(new_pit_b),
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

    out = os.path.join(ROOT, "results", "_r736bmc_codely_minisplit.json")
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
