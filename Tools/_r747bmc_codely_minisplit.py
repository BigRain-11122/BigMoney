# -*- coding: utf-8 -*-
"""r747 bm-c CODELY mini-split v2: main 31,267B is 547B over cap (bm-a r868/
r870 rebound) -> 当窗即办 per D-20261002-06 + r654 precedent (overage caused
by peer entries still triggers the touching machine's split obligation).
Plan: migrate r868+r870 verbatim to domain files; NEW r747 pit direct-writes
to research/pit-git-resolver-rebase.md (r666 direct-write precedent; resolver
main pit-git-resolver.md is at ~30,089B full since r735 -- no headroom);
main gets one compact r747 pointer row back. All in-memory checks pass
before any disk write (atomic). Ritual: r441/r731/r736/r739 same-form;
treasure_guard prescan rc recorded. Byte faces: disk CRLF-dominant; all math
on disk bytes, cap 30,720B, per r735/r736/r739 receipt convention. Target
tail-EOL heal per r735 行合并缺陷随迁治愈 precedent."""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
CAP = 30720
TGT_REBASE = os.path.join(ROOT, "research", "pit-git-resolver-rebase.md")
TGT_D19 = os.path.join(ROOT, "research", "pit-protocol-d19.md")
PREFIXES = {
    "r868": "- [2026-10-08 07:1x r868 bm-a]",
    "r870": "- [2026-10-08 08:1x r870 bm-a]",
}
NEW_PIT = (
    "- [2026-10-08 08:5x r747 bm-c] **推送竞窗 merge G4 字节恒等门对 daemon-live 面误伤坑"
    "（r746 五门正典竞窗首遇活写面假红·G4'=newer-wins 豁免）**：r747 收口推送撞 bm-a r871 closeout "
    "竞窗（post-pull pre-push 落 origin·merge-base≠origin tip）——pre-push 爪正确拦陈旧基座推送"
    "（删集含他机 REGIME5_BULL_SUPPLY_SCAN/_r871bma_closeout 两新件·r519 族执法）→pull --rebase 撞 "
    "13 UU 同窗 S6 再生面→r746 正典（rebase-abort+merge ORT ts-newer-wins）后 G4 origin-exclusive "
    "字节恒等门对 crash_fuse/daily_scorecard/dashboard_status.js 三件 daemon live 面假红"
    "（常驻引擎 merge 落盘后活写·非回退·r746 窗未触发=时序幸运非机制免疫）——正法 G4' 豁免="
    "verbatim OR disk_ts≥origin_ts（live-wins 分类门收编·stale disk 恒 fail-closed·等时 tie 采 "
    "disk-live：活面无 stage 可言，与 UU 面 r440 tie→theirs 律不冲突）；收口器两件套="
    "merge_close（r746 正典）+merge_finish（r747 新增·G4'+活面采纳+送达自证）·收据 "
    "_r747bmc_merge_gates.json。How to apply：未来竞窗解析直接克隆两件套；活面采纳前必验 "
    "disk_ts≥origin_ts（stale=回退面禁采）。")
POINTER_TPL = (
    "- \u57df\u6307\u9488\u00b7r747 bm-c mini-split\uff0810-08 08:5x\u00b7\u4e3b"
    "\u4ef6 31,267B \u8d8a\u5e3d 547B \u5f53\u7a97\u5373\u529e\u00b7\u4eea\u5f0f "
    "r731/r739 \u540c\u6b3e\uff09\uff1ar868 bm-a \u534a\u5f00 rebase \u76f2\u5199"
    "\u5751\uff08{b868}B\uff09\u2192pit-git-resolver-rebase.md+r870 bm-a D-19 "
    "\u6c34\u4f4d\u952e\u4f2a\u4fee\u590d\u5751\uff08{b870}B\uff09\u2192"
    "pit-protocol-d19.md verbatim \u8fc1\u51fa\uff1br747 \u7ade\u7a97 G4' \u6d3b"
    "\u9762\u8c41\u514d\u5751\uff08{bnpit}B\u00b7\u65b0\u5f8b\uff09\u76f4\u5199 "
    "pit-git-resolver-rebase.md\uff3br666 \u76f4\u5199\u5148\u4f8b\u00b7resolver "
    "\u4e3b\u4ef6\u6ee1\u5458\uff3d\uff1b\u5bf9\u8d26=receipt results/"
    "_r747bmc_codely_minisplit.json\uff08\u9010\u5757 bytes in target verbatim+"
    "\u4e3b\u4ef6\u4fdd\u7559\u9762\u6052\u7b49+\u4e3b/\u57df\u4ef6 \u226430KB\u00b7"
    "prescan rc \u7555\u75d5\uff09\uff1b\u65b0\u5751\u5f8b\u4ecd\u5148\u5165\u57df"
    "\u4ef6\u540e\u56de\u626b\uff08\u76f4\u5199\u4f8b\u5916 r666 \u8303\u5f0f\uff09\u3002")


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main():
    receipt = {"round": 747, "op": "codely-minisplit-r747-v2", "cap": CAP}
    # 1) prescan (record rc per r651/r736/r739 precedent)
    p = subprocess.run([sys.executable, os.path.join(ROOT, "Tools",
                       "treasure_guard.py"), "prescan", MAIN, TGT_REBASE,
                       TGT_D19], capture_output=True)
    receipt["prescan_rc"] = p.returncode
    receipt["prescan_note"] = ("rc recorded per r651/r654/r670/r703/r731/r736/r739 "
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

    # 3) in-memory plan: payloads per target + new main (keep + pointer row)
    new_pit_b = (NEW_PIT + "\r\n").encode("utf-8")
    pointer_b = (POINTER_TPL.format(b868=len(blocks["r868"]),
                                    b870=len(blocks["r870"]),
                                    bnpit=len(new_pit_b) - 2) + "\r\n").encode("utf-8")
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
    for tgt, payload_list in ((TGT_REBASE, [blocks["r868"], new_pit_b]),
                              (TGT_D19, [blocks["r870"]])):
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
        {"entry": "r868 bm-a", "bytes": len(blocks["r868"]),
         "sha16": sha16(blocks["r868"]), "to": "research/pit-git-resolver-rebase.md"},
        {"entry": "r747 new-pit direct-write", "bytes": len(new_pit_b),
         "sha16": sha16(new_pit_b), "to": "research/pit-git-resolver-rebase.md"},
        {"entry": "r870 bm-a", "bytes": len(blocks["r870"]),
         "sha16": sha16(blocks["r870"]), "to": "research/pit-protocol-d19.md"},
    ]
    for plan, entries in zip(plans, (("r868 bm-a", "r747 new-pit direct-write"),
                                     ("r870 bm-a",))):
        tb2 = open(os.path.join(ROOT, *plan["path"].split("/")), "rb").read()
        ok = (len(tb2) == plan["sim_after"]
              and tb2.endswith(plan["payload"]))
        for e in entries:
            m = next(m for m in receipt["migrated"] if m["entry"] == e)
            m["bytes_in_target_verbatim"] = ok and m["sha16"] in [
                sha16(plan["payload"]), sha16(plan["payload"][plan["tail_eol_heal"]:])]
            # verbatim membership: block bytes must appear in target tail
            src = blocks["r868"] if e.startswith("r868") else (
                new_pit_b if e.startswith("r747") else blocks["r870"])
            m["bytes_in_target_verbatim"] = ok and src in tb2
        plan.pop("payload")
        plan["bytes_after"] = tb2.__len__() if False else len(tb2)
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
        and all(m.get("bytes_in_target_verbatim") for m in receipt["migrated"])

    out = os.path.join(ROOT, "results", "_r747bmc_codely_minisplit.json")
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
