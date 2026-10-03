# -*- coding: utf-8 -*-
"""r415 bm-c: T-144(c) D-06 batch2 -- ENCODING-domain split, hot layer -> research/pit-encoding.md.

Scope (r414 REMAINING list encoding family): r593 (subprocess GBK decode crash),
r607 (round_reports GBK pollution byte tolerant-read), r407 (mojibake write-channel
fact-reconstructed entry), r414 (session-shell CJK probe GBK console crash).
Mechanism = r335 machine-migration law: byte-level line surgery, no hand copying.
Modes:
    python Tools/_r415bmc_pit_encoding_split.py           # do the split
    python Tools/_r415bmc_pit_encoding_split.py --verify   # independent re-check
Laws applied: r407 (CJK surgery via script not CLI replace), r614 (os.replace atomic),
r414 (PYTHONIOENCODING=utf-8 for this very class of script), already-migrated law
(pre-assert anchors absent from existing pit-*.md).
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
PIT_ENC = os.path.join(ROOT, "research", "pit-encoding.md")
RECEIPT = os.path.join(ROOT, "results", "_r415bmc_pit_encoding_split.json")
PIT_FILES = ["pit-git.md", "pit-pool.md", "pit-engine.md", "pit-protocol.md",
             "pit-data.md", "pit-ps.md"]

ANCHORS = [
    "- [2026-10-02 20:4x r593 bm-b] python subprocess 捕获子进程 UTF-8 输出默认 GBK 解码崩坑",
    "- [2026-10-03 07:3x r607 bm-b] round_reports.md 含 r506 遗留 GBK 污染字节",
    "- [2026-10-03 09:1x r407 bm-c]（r409 事实重建注记",
    "- [2026-10-03 12:5x r414 bm-c] python 探针脚本 CJK 预览打印 GBK console 崩坑",
]
PTR_AFTER = "- 域指针·D-20261002-06 PS 域拆件"
PTR_LINE = (
    "- 域指针·D-20261002-06 编码域拆件（2026-10-03 r415 bm-c·T-2026-10-02-144(c)·D-06 收口对账窗第二批）："
    "编码域坑律 4 条（subprocess 捕获解码 GBK 崩/共享台账 GBK 污染字节容错读/mojibake 落盘事故事实重建/"
    "会话壳 CJK 探针 console 编码崩族）已整域 verbatim 迁出→**research/pit-encoding.md**"
    "（件内字节对账+md5 行·零丢失断言）——python 驱动器捕获子进程输出（dump-dom/CLI stdout）/"
    "读共享大台账（round_reports 族）/CJK 件落盘与 replace 手术/会话壳 CJK 探针打印前必读该件；"
    "余=spawn/tooling 族+pre-split 存留条+pit-data CRLF 面+流水下沉（D-06 收口窗 10-07）。"
)


def md5(b):
    return hashlib.md5(b).hexdigest()


def split_lines(raw: bytes):
    """CRLF-face file -> list of lines without terminators (trailing blank kept)."""
    assert raw.count(b"\r\n") >= 10, "not a CRLF-face file"
    assert b"\n" not in raw.replace(b"\r\n", b""), "lone LF found"
    return raw.split(b"\r\n")


def main() -> int:
    raw = open(CODELY, "rb").read()
    lines = split_lines(raw)
    before = len(raw)
    md5_before = md5(raw)

    # already-migrated law: anchors must be absent from every existing pit file
    for pf in PIT_FILES:
        p = os.path.join(ROOT, "research", pf)
        if os.path.exists(p):
            body = open(p, "rb").read()
            for a in ANCHORS:
                assert a.encode("utf-8") not in body, "anchor already in %s" % pf

    idx = {}
    for a in ANCHORS:
        hits = [i for i, l in enumerate(lines) if l.decode("utf-8").startswith(a)]
        assert len(hits) == 1, "anchor not-unique: %s -> %s" % (a[:40], hits)
        idx[a] = hits[0]
    moved_idx = sorted(idx.values())

    moved = [lines[i] for i in moved_idx]
    moved_sum = sum(len(l) + 2 for l in moved)          # CRLF terminators included
    core_lf = b"".join(l.replace(b"\r", b"") + b"\n" for l in moved)
    core_md5 = md5(core_lf)

    # new CODELY: drop moved lines, insert pointer line right after PS-domain pointer
    ptr_hits = [i for i, l in enumerate(lines) if l.decode("utf-8").startswith(PTR_AFTER)]
    assert len(ptr_hits) == 1, "PS-domain pointer line not unique: %s" % ptr_hits
    new_lines = [l for i, l in enumerate(lines) if i not in set(moved_idx)]
    j = new_lines.index(lines[ptr_hits[0]])            # same content, new position
    new_lines.insert(j + 1, PTR_LINE.encode("utf-8"))
    new_raw = b"\r\n".join(new_lines)
    after = len(new_raw)
    ptr_len = len(PTR_LINE.encode("utf-8")) + 2
    assert after == before - moved_sum + ptr_len, "byte accounting mismatch"

    # compose pit-encoding.md (CRLF face, entries verbatim)
    header = "\r\n".join([
        "# pit-encoding —— 编码域坑律正典（D-20261002-06 域分件·编码事故家族）",
        "",
        "> 来源：CODELY.md 整域 verbatim 迁出（2026-10-03 r415 bm-c·T-2026-10-02-144(c)·D-06 收口对账窗第二批·r414 REMAINING 清单 encoding 族：r593/r607/r407-mojibake+r414 GBK-console）。",
        "> 执法面：python 驱动器消费子进程输出（dump-dom/CLI stdout 捕获）/读共享大台账（round_reports 族）/CJK 件落盘与 CLI replace 手术/会话壳 CJK 探针打印——上述编写动作与 UnicodeDecodeError、r.stdout=None 型验收门自崩、「断言全过后 exit 1」类诊断前必读本件；家族=GBK 本地码页三宿（subprocess 捕获/文件读取/console 输出）+mojibake 落盘事故事实重建律。",
        "> 字节对账行（零丢失断言）：CODELY.md 迁出前 %dB（md5=%s·CRLF 工作树面）→迁出后 %dB（md5=%s·CRLF 工作树面·净变化=−%dB 迁出+%dB 指针行·blob=LF 规范化面）；移出 4 条·条目字节和（含 CRLF 行尾）=%dB==主件净删减字节·逐字节恒等零丢失；迁移核（LF blob 面）=%dB·md5=%s；本件由拆件脚本机械迁移非手抄（r335 机证律同源）。" % (before, md5_before, after, md5(new_raw), moved_sum, ptr_len, moved_sum, len(core_lf), core_md5),
        "> 亲族注记：r559/r617 PS5 `>`/`*>` 重定向 UTF-16 编码例已在 pit-ps.md（PS 宿主侧·已迁不迁律）——编码域按「被调侧/数据面编码事故」归域，PS 宿主侧重定向例归 PS 域；两族同根不同宿，读本件时连带读 pit-ps 编码例。",
        "> 后续批次：spawn/tooling cluster + pre-split 存留条 + pit-data CRLF face 裁定 + 流水下沉（D-06 全线收口窗 2026-10-07）。",
        "",
    ]).encode("utf-8")
    pit_raw = header + b"\r\n".join(moved) + b"\r\n"

    # ---- assertion battery before any write ----
    for l in moved:
        assert pit_raw.count(l) == 1, "moved line not exactly-once in pit-encoding"
        assert l.decode("utf-8")                                    # strict utf-8
    for a in ANCHORS:
        assert a.encode("utf-8") not in new_raw, "residue in CODELY: %s" % a[:40]
    for body in (new_raw, pit_raw):
        t = body.decode("utf-8")                                   # strict decode
        assert t.count("????") == 0, "mojibake gate: ???? run found"
        assert body.replace(b"\r\n", b"").count(b"\r") == 0, "lone CR found"

    # ---- atomic writes (r614 law) ----
    for path, data in ((CODELY, new_raw), (PIT_ENC, pit_raw)):
        tmp = path + ".tmp_r415"
        with open(tmp, "wb") as fh:
            fh.write(data)
        os.replace(tmp, path)

    receipt = {
        "round": "r415 bm-c", "ticket": "T-2026-10-02-144(c)", "batch": "D-06 batch2 encoding",
        "entries_moved": [a.split("]")[0] + "]" for a in ANCHORS],
        "codely_before_B": before, "codely_before_md5": md5_before,
        "codely_after_B": after, "codely_after_md5": md5(new_raw),
        "moved_sum_CRLF_B": moved_sum, "pointer_line_B": ptr_len,
        "core_lf_B": len(core_lf), "core_lf_md5": core_md5,
        "pit_encoding_B": len(pit_raw), "pit_encoding_md5": md5(pit_raw),
        "verdict": "PASS",
    }
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print("SPLIT PASS: CODELY %dB->%dB (-%dB moved +%dB ptr) | core LF %dB md5 %s | pit-encoding %dB md5 %s"
          % (before, after, moved_sum, ptr_len, len(core_lf), core_md5, len(pit_raw), md5(pit_raw)))
    return 0


def verify() -> int:
    r = json.load(open(RECEIPT, encoding="utf-8"))
    new_raw = open(CODELY, "rb").read()
    pit_raw = open(PIT_ENC, "rb").read()
    ok = []
    ok.append(("codely_after", len(new_raw) == r["codely_after_B"] and md5(new_raw) == r["codely_after_md5"]))
    ok.append(("pit_encoding", len(pit_raw) == r["pit_encoding_B"] and md5(pit_raw) == r["pit_encoding_md5"]))
    for a in ANCHORS:
        ok.append(("absent-in-codely " + a[3:20], a.encode("utf-8") not in new_raw))
        ok.append(("exactly-once-in-pit " + a[3:20], pit_raw.count(a.encode("utf-8") + b"") >= 1
                   and sum(1 for l in pit_raw.split(b"\r\n") if l.decode("utf-8").startswith(a)) == 1))
    t_c, t_p = new_raw.decode("utf-8"), pit_raw.decode("utf-8")
    ok.append(("strict-utf8+no-mojibake", "????" not in t_c and "????" not in t_p))
    ok.append(("pointer-line-present", PTR_LINE in t_c))
    bad = [n for n, v in ok if not v]
    print("VERIFY %s (%d checks, fail=%s)" % ("PASS" if not bad else "FAIL", len(ok), bad or "none"))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(verify() if "--verify" in sys.argv else main())
