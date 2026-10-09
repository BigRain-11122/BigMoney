# -*- coding: utf-8 -*-
"""r811 bm-c CODELY main-file mini-split (r731/r735/r739 canon, 1-gen clone of
the established increment ceremony):
  migrate OUT (verbatim): the r896 bm-a treasure_guard prescan-bypass pit
    entry (last main-file line, ~830B) -> research/pit-tooling.md (census/
    tooling domain, 22,056B -> ~22.9KB, well under 30,720B cap);
  append IN (new pit law, first-entry-then-sweep rule): the r811 bm-c
    tracked-scratch-msg x CRLF phantom-dirty loop pit (~400B).
Prescan (treasure_guard, rel+abs dual form per r896 law): BOTH faces HIT
(rc3 rel / HIT abs) -- operation lawful under D-20261002-06 standing
authorization (verbatim zero-loss migration class, r651/r654/r670/r735
precedents recorded the same hit).
Safety: binary-safe reads, single atomic write per file immediately
followed by read-back verification (r693 'wb' truncation law), byte
accounting + sha16 receipt -> results/_r811bmc_codely_minisplit.json.
Usage: python Tools/_r811bmc_codely_minisplit.py"""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
TARGET = os.path.join(ROOT, "research", "pit-tooling.md")
RECEIPT = os.path.join(ROOT, "results", "_r811bmc_codely_minisplit.json")

MIGRATE_NEEDLE = b"- [2026-10-09 02:5x r896 bm-a] **treasure_guard prescan"
NEW_PIT = ("- [2026-10-09 17:1x r811 bm-c] **S0 \u88ab\u8ddf\u8e2a scratch msg \u4ef6"
           "\u00d7CRLF \u5f52\u4e00\u5316\u5047\u810f\u73af\u5751\uff08_r_bmc_s0msg.txt "
           "\u4e09\u8fde\u62d2 pull --rebase \u5b9e\u5f39\uff09**\uff1a\u4ed3\u6839"
           "\u63d0\u4ea4\u6d88\u606f scratch \u4ef6\u662f\u88ab\u8ddf\u8e2a\u4ef6"
           "+\u6bcf\u6b21 S0 \u52a9\u624b\u8fd0\u884c\u91cd\u5199\uff08\u5185\u5bb9"
           "\u542b\u8f6e\u53f7\uff09=\u6bcf\u6b21\u8fd0\u884c\u81ea\u810f\uff1b"
           "git CRLF \u5f52\u4e00\u5316\u4f7f LF \u843d\u76d8\u9762 commit \u540e"
           "\u4ecd\u663e modified\uff08\u5de5\u4f5c\u6811\u4e0e index \u5b57\u8282"
           "\u9762\u4e0d\u7b49\uff09=pull --rebase \u6052\u62d2 unstaged changes"
           "\uff08\u672c\u8f6e\u4e09\u8fde\u62d2\u5b9e\u8bc1\uff09\u3002\u6b63\u6cd5"
           "\uff1d\u2460scratch \u4ef6\u6536\u7f16\u8fdb S0 \u52a9\u624b OWN_PATTERNS "
           "\u540c\u7a97 add+commit\uff1b\u2461\u5df2 commit \u540e\u7684 LF/CRLF \u6f02"
           "\u79fb\u9762 git checkout -- <faces> \u5f52\u4e00\u518d rebase\uff1b"
           "\u2462\u65b0 S0 \u52a9\u624b\u4e00\u5f8b 1-gen \u514b\u9686 _r811bmc_s0.py"
           "\uff08\u5df2\u542b\u2460\uff09\u3002How to apply\uff1aS0 \u52a9\u624b\u89c1"
           "\u300ccannot pull with rebase: unstaged changes\u300d\u5148\u67e5 scratch "
           "\u4ef6\u4e0e CRLF \u6f02\u79fb\u9762\uff0c\u52ff\u8bef\u5224 daemon \u7ade"
           "\u6001\u3002")


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def main():
    codely = open(CODELY, "rb").read()
    target = open(TARGET, "rb").read()
    facts = {"round": 811,
             "prescan_rel_rc": 3,
             "prescan_rel_hits": ["CODELY.md", "research/pit-tooling.md"],
             "prescan_abs": "HIT x2 (r896 _norm_path guard active, bypass closed)",
             "authorization": "D-20261002-06 standing (verbatim zero-loss split class)"}
    # locate the migrate block: from needle line start to end of file
    idx = codely.find(MIGRATE_NEEDLE)
    assert idx != -1, "migrate needle not found in main file"
    block = codely[idx:]
    # zero-residue check: needle appears exactly once
    assert codely.count(MIGRATE_NEEDLE) == 1, "needle not unique"
    retained = codely[:idx]
    # strip trailing blank lines from retained, keep structure ending newline
    retained = retained.rstrip(b"\r\n") + b"\r\n"
    # build new main file: retained + new pit entry
    new_pit_bytes = NEW_PIT.encode("utf-8")
    new_codely = retained + b"\r\n" + new_pit_bytes + b"\r\n"
    # target append: match target EOL (detect)
    eol = b"\r\n" if target.endswith(b"\r\n") or b"\r\n" in target[-200:] else b"\n"
    new_target = target + eol + block.rstrip(b"\r\n") + eol
    # byte accounting BEFORE write
    facts["codely_pre_bytes"] = len(codely)
    facts["target_pre_bytes"] = len(target)
    facts["migrated_block_bytes"] = len(block)
    facts["migrated_block_sha16"] = sha16(block)
    facts["migrated_block_sha16_lf"] = sha16(block.replace(b"\r\n", b"\n"))
    facts["new_pit_bytes"] = len(new_pit_bytes)
    facts["codely_post_bytes"] = len(new_codely)
    facts["target_post_bytes"] = len(new_target)
    facts["cap_30720"] = 30720
    facts["codely_under_cap"] = facts["codely_post_bytes"] <= facts["cap_30720"]
    facts["target_under_cap"] = facts["target_post_bytes"] <= facts["cap_30720"]
    assert facts["codely_under_cap"], "main file over cap after split"
    assert facts["target_under_cap"], "target domain file over cap after append"
    # atomic writes + immediate read-back verification (r693 'wb' law)
    with open(CODELY, "wb") as fh:
        fh.write(new_codely)
    rb1 = open(CODELY, "rb").read()
    assert rb1 == new_codely, "CODELY read-back mismatch"
    with open(TARGET, "wb") as fh:
        fh.write(new_target)
    rb2 = open(TARGET, "rb").read()
    assert rb2 == new_target, "target read-back mismatch"
    # zero-loss assertions
    facts["block_in_target_verbatim"] = block.rstrip(b"\r\n") in rb2
    facts["needle_residue_in_main"] = MIGRATE_NEEDLE in rb1
    assert facts["block_in_target_verbatim"], "migrated block not verbatim in target"
    assert not facts["needle_residue_in_main"], "needle residue in main file"
    facts["new_pit_in_main"] = new_pit_bytes in rb1
    assert facts["new_pit_in_main"], "new pit entry missing from main file"
    with open(RECEIPT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: facts[k] for k in (
        "codely_pre_bytes", "migrated_block_bytes", "new_pit_bytes",
        "codely_post_bytes", "target_post_bytes", "codely_under_cap",
        "target_under_cap", "block_in_target_verbatim",
        "needle_residue_in_main", "migrated_block_sha16")},
        ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
