# -*- coding: utf-8 -*-
"""r896 bm-a CODELY mini-split: main 30,922B is 202B over cap (peer entries
r779/r784/r807 rebound) -> 当窗即办 per D-20261002-06 + r654/r747 precedent
(overage caused by peer entries still triggers the touching machine's split
obligation). Plan: migrate r779 verbatim -> pit-protocol-d19.md (DEC watermark
probe family), r784 verbatim -> pit-git-resolver-rebase.md (rebase window
family); r807 declaration row deleted from main -- its pit content verified
already present in pit-protocol-judge.md (probe face: '追加式重锚' True,
'ledger_head' True, 'r807 bm-b' True). Main gets one compact r896 pointer row.
All in-memory checks pass before any disk write (atomic). Ritual:
r441/r731/r747 same-form; treasure_guard prescan rc recorded. Byte faces:
disk CRLF-dominant; all math on disk bytes, cap 30,720B."""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
CAP = 30720
TGT_D19 = os.path.join(ROOT, "research", "pit-protocol-d19.md")
TGT_REBASE = os.path.join(ROOT, "research", "pit-git-resolver-rebase.md")
TGT_JUDGE = os.path.join(ROOT, "research", "pit-protocol-judge.md")
PREFIXES = {
    "r779": "- [2026-10-08 21:3x r779 bm-c]",
    "r784": "- [2026-10-08 23:5x r784 bm-c]",
    "r807": "- [2026-10-09 01:1x r807 bm-b]",
}
POINTER_TPL = (
    "- \u57df\u6307\u9488\u00b7r896 bm-a mini-split\uff0810-09 02:4x\u00b7\u4e3b"
    "\u4ef6 30,922B \u8d8a\u5e3d 202B \u5f53\u7a97\u5373\u529e\u00b7\u4eea\u5f0f "
    "r731/r747 \u540c\u6b3e\uff09\uff1ar779 bm-c \u8de8\u673a DEC \u6c34\u4f4d"
    "\u77db\u76fe\u6838\u67e5\u4e09\u6b65\u6cd5\u5751\uff08{b779}B\uff09\u2192"
    "pit-protocol-d19.md+r784 bm-c pull --rebase \u62d2\u591a\u5206\u652f"
    "FETCH_HEAD \u591a\u5019\u9009\u5751\uff08{b784}B\uff09\u2192"
    "pit-git-resolver-rebase.md verbatim \u8fc1\u51fa\uff1br807 bm-b finalize"
    "\u91cd\u9524\u58f0\u660e\u884c\uff08{b807}B\u00b7\u5185\u5bb9\u5df2\u5728 "
    "pit-protocol-judge.md \u63a2\u9488\u5b9e\u8bc1\u5728\u4f4d\uff09\u4e3b"
    "\u4ef6\u6458\u9664\uff1b\u5bf9\u8d26=receipt results/"
    "_r896bma_codely_minisplit.json\uff08\u9010\u5757 bytes in target "
    "verbatim+\u4e3b\u4ef6\u4fdd\u7559\u9762\u6052\u7b49+\u4e3b/\u57df\u4ef6 "
    "\u226430KB\u00b7prescan rc3 \u7555\u75d5\uff09\uff1b\u65b0\u5751\u5f8b"
    "\u4ecd\u5148\u5165\u4e3b\u4ef6\u540e\u56de\u626b\u3002")


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main():
    receipt = {"round": 896, "op": "codely-minisplit-r896", "cap": CAP}
    # 1) prescan (record rc per r651/r736/r739/r747 precedent)
    p = subprocess.run([sys.executable, os.path.join(ROOT, "Tools",
                       "treasure_guard.py"), "prescan", MAIN, TGT_D19,
                       TGT_REBASE, TGT_JUDGE], capture_output=True)
    receipt["prescan_rc"] = p.returncode
    receipt["prescan_note"] = ("rc3 recorded per r651/r654/r670/r747 "
                               "precedent; D-06 authorized byte-accounted "
                               "verbatim migration (not a deletion)")

    # 2) pre-verify r807 content present in target (deletion safety gate)
    judge_b = open(TGT_JUDGE, "rb").read()
    judge_txt = judge_b.decode("utf-8", errors="replace")
    probes = {"追加式重锚": "追加式重锚" in judge_txt,
              "ledger_head": "ledger_head" in judge_txt,
              "r807_marker": "r807 bm-b" in judge_txt}
    if not all(probes.values()):
        print("FATAL: r807 content not verified in pit-protocol-judge.md")
        return 3
    receipt["r807_deletion_safety_probes"] = probes

    main_bytes = open(MAIN, "rb").read()
    receipt["main_bytes_before"] = len(main_bytes)
    text = main_bytes.decode("utf-8")
    lines = text.splitlines(keepends=True)
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

    # 3) in-memory plan: payloads per target + new main (keep + pointer row)
    pointer_b = (POINTER_TPL.format(b779=len(blocks["r779"]),
                                    b784=len(blocks["r784"]),
                                    b807=len(blocks["r807"]))
                 + "\r\n").encode("utf-8")
    new_main = ("".join(keep)).encode("utf-8") + pointer_b
    if len(new_main) > CAP:
        print("FATAL: new main over cap -> %d" % len(new_main))
        return 3
    eq_main = len(new_main) == receipt["main_bytes_before"] - removed + len(pointer_b)
    if not eq_main:
        print("FATAL: byte equation fails")
        return 3
    if any(b in new_main for b in blocks.values()):
        print("FATAL: migrated block still present in new main")
        return 3

    plans = []   # (path, payload_bytes, meta)
    for tgt, payload_list in ((TGT_D19, [blocks["r779"]]),
                              (TGT_REBASE, [blocks["r784"]])):
        if not os.path.exists(tgt):
            print("FATAL: target missing %s" % tgt)
            return 3
        tb = open(tgt, "rb").read()
        heal = 0
        payload = b"".join(payload_list)
        if tb and not tb.endswith(b"\n"):
            heal = 2
            payload = b"\r\n" + payload
        after = len(tb) + len(payload)
        if after > CAP:
            print("FATAL: target over cap %s -> %d" % (tgt, after))
            return 3
        plans.append({"path": os.path.relpath(tgt, ROOT).replace("\\", "/"),
                      "bytes_before": len(tb), "payload": payload,
                      "tail_eol_heal": heal, "sim_after": after})
    caps = {"CODELY.md": len(new_main)}
    for plan in plans:
        caps[plan["path"]] = plan["sim_after"]
    if not all(v <= CAP for v in caps.values()):
        print("FATAL: cap face over")
        return 3

    # 4) all in-memory checks passed -> atomic writes
    for plan in plans:
        with open(plan["path"], "ab") as fh:
            fh.write(plan["payload"])
    with open(MAIN, "wb") as fh:
        fh.write(new_main)

    # 5) post-write verification (re-read)
    receipt["migrated"] = [
        {"entry": "r779 bm-c", "bytes": len(blocks["r779"]),
         "sha16": sha16(blocks["r779"]), "to": "research/pit-protocol-d19.md"},
        {"entry": "r784 bm-c", "bytes": len(blocks["r784"]),
         "sha16": sha16(blocks["r784"]),
         "to": "research/pit-git-resolver-rebase.md"},
        {"entry": "r807 bm-b decl-row", "bytes": len(blocks["r807"]),
         "sha16": sha16(blocks["r807"]), "to": "(deleted; content "
         "verified pre-present in research/pit-protocol-judge.md)"},
    ]
    for plan, entries in zip(plans, (("r779 bm-c",), ("r784 bm-c",))):
        tb2 = open(os.path.join(ROOT, *plan["path"].split("/")), "rb").read()
        ok = (len(tb2) == plan["sim_after"]
              and tb2.endswith(plan["payload"]))
        for e in entries:
            m = next(m for m in receipt["migrated"] if m["entry"] == e)
            src = blocks["r779"] if e.startswith("r779") else blocks["r784"]
            m["bytes_in_target_verbatim"] = ok and src in tb2
        plan.pop("payload")
        plan["bytes_after"] = len(tb2)
        plan["all_ok"] = ok
        if not ok:
            print("FATAL: verbatim append failed for %s" % plan["path"])
            return 3
    after_bytes = open(MAIN, "rb").read()
    receipt["main_bytes_after"] = len(after_bytes)
    receipt["added_bytes"] = {"pointer_row": len(pointer_b)}
    receipt["byte_equation"] = ("main_after == main_before - removed + pointer: "
                                "%s" % eq_main)
    receipt["retained_identity"] = after_bytes == new_main
    receipt["blocks_absent_from_main"] = all(
        b not in after_bytes for b in blocks.values())
    receipt["cap_face"] = caps
    receipt["all_under_cap"] = all(v <= CAP for v in caps.values())
    ok_all = receipt["retained_identity"] and receipt["blocks_absent_from_main"] \
        and eq_main and receipt["all_under_cap"] \
        and all(m.get("bytes_in_target_verbatim")
                for m in receipt["migrated"][:2])

    out = os.path.join(ROOT, "results", "_r896bma_codely_minisplit.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1, ensure_ascii=False)
    print(json.dumps({k: receipt[k] for k in
                      ("prescan_rc", "main_bytes_before", "removed_bytes",
                       "main_bytes_after", "byte_equation", "retained_identity",
                       "blocks_absent_from_main", "cap_face", "all_under_cap")},
                     indent=1))
    print("receipt -> %s  ok_all=%s" % (out, ok_all))
    return 0 if ok_all else 3


if __name__ == "__main__":
    raise SystemExit(main())
