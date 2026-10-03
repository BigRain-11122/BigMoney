# -*- coding: utf-8 -*-
"""r439 bm-c: pit-protocol.md L14 line-merge healing -- stray r569 duplicate-tail removal.

Defect (found by the r439 surgery-sub-split already-migrated law): pit-protocol.md
L14 carries TWO entries on one line -- the r509 protocol entry (canonical, stays)
immediately followed by the FULL r569 surgery-family entry text concatenated with
no line break (split-campaign boundary bug family, r419/r420 kin). The r569 text is
byte-identical (no-terminator md5 c605cc4d11ad981d0738798a0d1ec861) to the canonical per-line
copy in pit-git.md, whose home after the same-round batch-1 sub-split is
research/pit-git-surgery.md -- so removal is a pure dedup with zero information
loss (byte-identity pre-asserted here again before any write).
Modes:
    python Tools/_r439bmc_pit_protocol_heal.py            # do the heal
    python Tools/_r439bmc_pit_protocol_heal.py --verify     # independent re-check
Laws: r335 machine surgery, r614 atomic replace, assert-before-write battery.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "research", "pit-protocol.md")
GIT = os.path.join(ROOT, "research", "pit-git.md")
RECEIPT = os.path.join(ROOT, "results", "_r439bmc_pit_protocol_heal.json")

NEEDLE = "- [2026-10-02 10:1x r569 bm-a] 让路手术窗三写者面序律"
R509_ANCHOR = "- [2026-10-01 15:2x r509 bm-b] append_ledger 返回 dict 不落盘"
R509_TAIL = "补账动作=活头 derive 禁手抄原数字。"
HDR_NEEDLE = "> 增量回扫行（r419 bm-c·T-2026-10-02-144(c)·D-06 pre-split survivors 批次二）：热层条目 1 条 verbatim 追加（pre-split 存留条·[2026-10-01 r294 bm-c]）"
HDR_LINE = (
    "> 直写行（r439 bm-c·post-split convention direct-write·D-06 sub-split batch-1 前置愈合）：L14 行界合并缺陷愈合——r509 行尾被拼接 r569 外科域条目全文（无换行·split 战役边界 bug 族 r419 kin·本件 already-migrated 门当场拦截发现）；剔除串录尾核 %dB（md5=%s·与 pit-git.md 在册行字节恒等·真本批随批迁 pit-git-surgery.md）零信息损失；本件行数-0（行内剔除非删行）+本行 2519B→1089B。"
)


def md5(b):
    return hashlib.md5(b).hexdigest()


def main() -> int:
    raw = open(SRC, "rb").read()
    assert raw.count(b"\r\n") >= 10 and b"\n" not in raw.replace(b"\r\n", b"")
    lines = raw.split(b"\r\n")
    before = len(raw)
    md5_before = md5(raw)

    hits = [i for i, l in enumerate(lines) if NEEDLE.encode("utf-8") in l]
    assert len(hits) == 1, "needle not-unique: %s" % hits
    i = hits[0]
    line = lines[i].decode("utf-8")
    assert line.startswith(R509_ANCHOR), "L14 head is not the r509 entry"

    # byte-identity pre-assert vs the pit-git.md canonical per-line copy
    git_raw = open(GIT, "rb").read()
    gl = [x for x in git_raw.split(b"\r\n")
          if x.decode("utf-8").startswith(NEEDLE)]
    assert len(gl) == 1, "pit-git canonical copy not unique"
    j = line.find(NEEDLE)
    tail = line[j:]
    assert tail.encode("utf-8") == gl[0], "embedded tail NOT byte-identical to canonical"
    assert line[:j].rstrip().endswith(R509_TAIL), "r509 part tail unexpected"
    tail_B = len(tail.encode("utf-8"))
    core_md5 = md5(tail.encode("utf-8"))
    assert core_md5 == "c605cc4d11ad981d0738798a0d1ec861", "md5 drift vs probe"

    new_line = line[:j].encode("utf-8")
    assert len(new_line) + tail_B == len(lines[i]), "split accounting mismatch"

    # insert header note after the r419 increment-scan line
    hdr_hits = [k for k, l in enumerate(lines)
               if l.decode("utf-8").startswith(HDR_NEEDLE)]
    assert len(hdr_hits) == 1, "header needle not unique: %s" % hdr_hits
    new_lines = list(lines)
    new_lines[i] = new_line
    new_lines.insert(hdr_hits[0] + 1, HDR_LINE.encode("utf-8"))
    new_raw = b"\r\n".join(new_lines)
    after = len(new_raw)
    hdr_B = len(HDR_LINE.encode("utf-8")) + 2
    assert after == before - tail_B + hdr_B, "byte accounting mismatch"
    assert new_raw.count(NEEDLE.encode("utf-8")) == 0, "residue after heal"
    assert len(new_lines) == len(lines) + 1, "line count accounting"

    # battery: strict utf-8, no mojibake, no lone CR, r509 intact
    t = new_raw.decode("utf-8")
    assert t.count("????") == 0
    assert new_raw.replace(b"\r\n", b"").count(b"\r") == 0
    kept = [x for x in new_raw.split(b"\r\n")
            if x.decode("utf-8").startswith(R509_ANCHOR)]
    assert len(kept) == 1 and kept[0].decode("utf-8").endswith(R509_TAIL), \
        "r509 entry not intact"

    tmp = SRC + ".tmp_r439"
    with open(tmp, "wb") as fh:
        fh.write(new_raw)
    os.replace(tmp, SRC)

    receipt = {
        "round": "r439 bm-c", "ticket": "T-2026-10-02-144(c)",
        "batch": "D-06 pit-protocol L14 line-merge heal (pre batch-1)",
        "removed_tail_B": tail_B, "removed_tail_md5": core_md5,
        "removed_needle": NEEDLE, "hdr_line_B": hdr_B,
        "protocol_before_B": before, "protocol_before_md5": md5_before,
        "protocol_after_B": after, "protocol_after_md5": md5(new_raw),
        "r509_kept_intact": True,
        "canonical_home": "research/pit-git.md -> pit-git-surgery.md (same round)",
        "verdict": "PASS",
    }
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print("HEAL PASS: pit-protocol %dB->%dB (-%dB stray tail +%dB hdr) "
          "tail md5 %s" % (before, after, tail_B, hdr_B, core_md5))
    return 0


def verify() -> int:
    r = json.load(open(RECEIPT, encoding="utf-8"))
    raw = open(SRC, "rb").read()
    ok = []
    ok.append(("after-bytes-md5", len(raw) == r["protocol_after_B"]
               and md5(raw) == r["protocol_after_md5"]))
    ok.append(("needle-absent", NEEDLE.encode("utf-8") not in raw))
    ok.append(("hdr-line-present", HDR_LINE in raw.decode("utf-8")))
    kept = [x for x in raw.split(b"\r\n")
            if x.decode("utf-8").startswith(R509_ANCHOR)]
    ok.append(("r509-intact", len(kept) == 1
               and kept[0].decode("utf-8").endswith(R509_TAIL)))
    bad = [n for n, v in ok if not v]
    print("VERIFY %s (%d checks, fail=%s)"
          % ("PASS" if not bad else "FAIL", len(ok), bad or "none"))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(verify() if "--verify" in sys.argv else main())
