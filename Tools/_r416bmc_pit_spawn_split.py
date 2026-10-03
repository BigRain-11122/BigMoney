# -*- coding: utf-8 -*-
"""r416 bm-c: T-144(c) D-06 batch3 -- SPAWN/TOOLING-domain split, hot layer -> research/pit-spawn.md.

Scope (r415 REMAINING list spawn/tooling cluster): r317 (detached-spawn pipe holding),
r324 (inline SR 5min behead x spawn-driver __main__ guard), r614-croc x2 (zombie relay
conn + public-relay DNS multi-A fork), r570-a (shared jsonl shell-redirect overwrite).
Mechanism = r335 machine-migration law: byte-level line surgery, no hand copying.
Modes:
    python Tools/_r416bmc_pit_spawn_split.py            # do the split
    python Tools/_r416bmc_pit_spawn_split.py --verify    # independent re-check
Laws applied: r407 (CJK surgery via script not CLI replace), r614 (os.replace atomic),
r414 (PYTHONIOENCODING=utf-8 for this very class of script), already-migrated law
(pre-assert anchors absent from existing pit-*.md incl. pit-encoding).
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
PIT_SP = os.path.join(ROOT, "research", "pit-spawn.md")
RECEIPT = os.path.join(ROOT, "results", "_r416bmc_pit_spawn_split.json")
PIT_FILES = ["pit-git.md", "pit-pool.md", "pit-engine.md", "pit-protocol.md",
             "pit-data.md", "pit-ps.md", "pit-encoding.md"]

ANCHORS = [
    "- [2026-10-01 13:4x r317 bm-c] 分离 spawn 管道持握坑",
    "- [2026-10-01 2026-10-01T16:48x r324 bm-c] 长活内联 SR 5min 无输出自动取消坑",
    "- [2026-10-02 10:4x r570 bm-a] 共享 jsonl 本地 shell 重定向覆写坑",
    "- [2026-10-03 10:5x r614 bm-b] croc sender 僵尸 relay 连接坑",
    "- [2026-10-03 11:2x r614 bm-b] croc 公共 relay DNS 多 A 记录分叉坑",
]
PTR_AFTER = "- 域指针·D-20261002-06 编码域拆件"
PTR_LINE = (
    "- 域指针·D-20261002-06 spawn/tooling 域拆件（2026-10-03 r416 bm-c·T-2026-10-02-144(c)·D-06 收口对账窗第三批）："
    "spawn/tooling 域坑律 5 条（分离 spawn 管道持握/长活内联 SR 5min 斩首×spawn 驱动 __main__ 守卫再犯/"
    "croc sender 僵尸 relay 连接/croc 公共 relay DNS 多 A 记录分叉/共享 jsonl shell 重定向覆写族）已整族 verbatim 迁出→"
    "**research/pit-spawn.md**（件内字节对账+md5 行·零丢失断言）——"
    "会话/包装器内点火分离长活（采集器/croc 双端）/spawn 驱动脚本编写/S7 步骤重定向/croc 零配对诊断前必读该件；"
    "余=pre-split 存留条+git/protocol 增量+pit-data CRLF 面+流水下沉（D-06 收口窗 10-07）。"
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

    # new CODELY: drop moved lines, insert pointer line right after encoding-domain pointer
    ptr_hits = [i for i, l in enumerate(lines) if l.decode("utf-8").startswith(PTR_AFTER)]
    assert len(ptr_hits) == 1, "encoding-domain pointer line not unique: %s" % ptr_hits
    new_lines = [l for i, l in enumerate(lines) if i not in set(moved_idx)]
    j = new_lines.index(lines[ptr_hits[0]])            # same content, new position
    new_lines.insert(j + 1, PTR_LINE.encode("utf-8"))
    new_raw = b"\r\n".join(new_lines)
    after = len(new_raw)
    ptr_len = len(PTR_LINE.encode("utf-8")) + 2
    assert after == before - moved_sum + ptr_len, "byte accounting mismatch"

    # compose pit-spawn.md (CRLF face, entries verbatim)
    header = "\r\n".join([
        "# pit-spawn —— 分离长活/工具链坑律正典（D-20261002-06 域分件·spawn/tooling 家族）",
        "",
        "> 来源：CODELY.md 整族 verbatim 迁出（2026-10-03 r416 bm-c·T-2026-10-02-144(c)·D-06 收口对账窗第三批·r415 REMAINING 清单 spawn/tooling 族：r317/r324/r614-croc×2/r570-a）。",
        "> 执法面：会话/包装器内点火分离长活（采集器/回填器/daemon/croc 双端）/一切会被 spawn 的驱动·探针·runner 脚本编写（__main__ 守卫/close_fds/内联时长预算）/S7 步骤重定向与共享 append-only 件写入/croc 传递零配对诊断——上述动作前必读本件；家族=分离长活管道持握+spawn 守卫+工具面（croc/重定向）事故。",
        "> 字节对账行（零丢失断言）：CODELY.md 迁出前 %dB（md5=%s·CRLF 工作树面）→迁出后 %dB（md5=%s·CRLF 工作树面·净变化=−%dB 迁出+%dB 指针行·blob=LF 规范化面）；移出 5 条·条目字节和（含 CRLF 行尾）=%dB==主件净删减字节·逐字节恒等零丢失；迁移核（LF blob 面）=%dB·md5=%s；本件由拆件脚本机械迁移非手抄（r335 机证律同源）。" % (before, md5_before, after, md5(new_raw), moved_sum, ptr_len, moved_sum, len(core_lf), core_md5),
        "> 亲族注记：r559/r617 PS `>`/`*>` 重定向 UTF-16 例已在 pit-ps.md（PS 宿主侧·已迁不迁律）——本件收工具宿主面（shell/重定向/croc），PS 宿主侧重定向例归 PS 域；r570-bmb append-only jsonl union pretty-blob 例与 r327 亚百 ms 池化 IPC 例=pre-split 存留条（后续批次裁定归属域），勿重复入件。",
        "> 后续批次：pre-split 存留条（r489/r294×3/r300/r303/r494/r304/r307/r311/r327/r570-bmb）+ git 增量（r366-ls-tree/r614-rebase-活写）+ protocol 增量（r366-laneio/r371）+ pit-data CRLF 面 + 流水下沉（D-06 全线收口窗 2026-10-07）。",
        "",
    ]).encode("utf-8")
    pit_raw = header + b"\r\n".join(moved) + b"\r\n"

    # ---- assertion battery before any write ----
    for l in moved:
        assert pit_raw.count(l) == 1, "moved line not exactly-once in pit-spawn"
        assert l.decode("utf-8")                                    # strict utf-8
    for a in ANCHORS:
        assert a.encode("utf-8") not in new_raw, "residue in CODELY: %s" % a[:40]
    for body in (new_raw, pit_raw):
        t = body.decode("utf-8")                                   # strict decode
        assert t.count("????") == 0, "mojibake gate: ???? run found"
        assert body.replace(b"\r\n", b"").count(b"\r") == 0, "lone CR found"

    # ---- atomic writes (r614 law) ----
    for path, data in ((CODELY, new_raw), (PIT_SP, pit_raw)):
        tmp = path + ".tmp_r416"
        with open(tmp, "wb") as fh:
            fh.write(data)
        os.replace(tmp, path)

    receipt = {
        "round": "r416 bm-c", "ticket": "T-2026-10-02-144(c)", "batch": "D-06 batch3 spawn/tooling",
        "entries_moved": [a.split("]")[0] + "]" for a in ANCHORS],
        "codely_before_B": before, "codely_before_md5": md5_before,
        "codely_after_B": after, "codely_after_md5": md5(new_raw),
        "moved_sum_CRLF_B": moved_sum, "pointer_line_B": ptr_len,
        "core_lf_B": len(core_lf), "core_lf_md5": core_md5,
        "pit_spawn_B": len(pit_raw), "pit_spawn_md5": md5(pit_raw),
        "verdict": "PASS",
    }
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print("SPLIT PASS: CODELY %dB->%dB (-%dB moved +%dB ptr) | core LF %dB md5 %s | pit-spawn %dB md5 %s"
          % (before, after, moved_sum, ptr_len, len(core_lf), core_md5, len(pit_raw), md5(pit_raw)))
    return 0


def verify() -> int:
    r = json.load(open(RECEIPT, encoding="utf-8"))
    new_raw = open(CODELY, "rb").read()
    pit_raw = open(PIT_SP, "rb").read()
    ok = []
    ok.append(("codely_after", len(new_raw) == r["codely_after_B"] and md5(new_raw) == r["codely_after_md5"]))
    ok.append(("pit_spawn", len(pit_raw) == r["pit_spawn_B"] and md5(pit_raw) == r["pit_spawn_md5"]))
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
