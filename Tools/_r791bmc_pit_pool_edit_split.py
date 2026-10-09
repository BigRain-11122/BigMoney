# -*- coding: utf-8 -*-
"""r791 bm-c: D-06 domain-file sub-split -- pit-pool-edit.md (32,616B > 30,720B
cap, r790 slot-window debt) -> research/pit-pool-burn.md (ignition-gate / burn
mechanics / double-burn-takeover race family, 15 entries) with pit-pool-edit.md
keeping the edit/write-path/settle/flip-surgery family (18 entries).

Ritual = r705 bm-b pit-pool split canon (same file family, same law set):
  - treasure_guard prescan FIRST (research/ family = fail-closed rc3 face;
    D-20261002-06 group split order authorizes verbatim migration per
    TREASURE_PROTECTION_LAW sec.2 three-piece ritual: prescan-trace + registry
    in/out row + zero-loss assertion; r703/r705 precedent rows in registry).
  - byte-level line surgery, no hand copying (r335 law);
  - atomic writes (r614 os.replace);
  - byte accounting identity: source_after == source_before - moved_block_sum
    + hdr_delta (exact mechanical assert);
  - already-migrated law: anchors absent from sibling pit files;
  - CODELY.md pool-domain pointer row append (navigation law) with cap assert;
  - knowledge/TREASURE_REGISTRY.md in/out row append (registry face);
  - receipt -> results/_r791bmc_pit_pool_edit_split_receipt.json.

Modes:
    python Tools/_r791bmc_pit_pool_edit_split.py           # do the split
    python Tools/_r791bmc_pit_pool_edit_split.py --verify  # independent re-check
All subprocesses CREATE_NO_WINDOW (U060 silence law).
"""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "research", "pit-pool-edit.md")
TGT = os.path.join(ROOT, "research", "pit-pool-burn.md")
SIB = os.path.join(ROOT, "research", "pit-pool.md")
CODELY = os.path.join(ROOT, "CODELY.md")
REG = os.path.join(ROOT, "knowledge", "TREASURE_REGISTRY.md")
RECEIPT = os.path.join(ROOT, "results", "_r791bmc_pit_pool_edit_split_receipt.json")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
CAP = 30720
CAP_MIN_MARGIN = -1

# 15 burn-family anchors (exact line-start prefixes, byte-faithful)
ANCHORS = [
    "- [2026-10-01 13:3x r316 bm-c]",
    "- [2026-10-01 11:2x r511 bm-a]",
    "- [2026-10-01 18:1x r327 bm-c]",
    "- [2026-10-03 04:4x r601 bm-b]",
    "[2026-10-03 05:1x r608 bm-a]",
    "[2026-10-03 06:1x r605 bm-b]",
    "- [2026-10-03 10:0x r618 bm-a]",
    "- [2026-10-03 13:5x r625 bm-a]",
    "- [2026-10-03 18:2x r627 bm-b]",
    "- [2026-10-03 16:4x r632 bm-a]",
    "- [2026-10-03 19:15 r637 bm-a]",
    "- [2026-10-03 23:5x r648 bm-a]",
    "- [2026-10-08 03:5x r860 bm-a] **入池 runner_args 逗号串坑",
    "- [2026-10-08 03:5x r860 bm-a] **trial-labor runner 无 worker-claim 件",
    "- [2026-10-08 03:4x r860 bm-a] **claim 提交后 4 秒 compact 覆写丢 owner_since",
]
KEPT_ANCHORS = [
    "- [2026-09-30 22:0x r289 bm-c]",
    "- [2026-10-01 10:0x r509 bm-a]",
    "- [2026-10-01 10:1x r500 bm-b]",
    "- [2026-10-01 12:4x r514 bm-a]",
    "- [2026-10-01 14:3x r507 bm-b]",
    "- [2026-10-03 07:25 r402 bm-c]",
    "- [2026-10-03 08:5x r404 bm-c]",
    "- [2026-10-03 15:1x r628 bm-a]",
    "- [2026-10-03 15:3x r629 bm-a]",
    "- [2026-10-03 16:1x r630 bm-a]",
    "- [2026-10-04 13:2x r678 bm-a]",
    "- [2026-10-04 13:3x r474 bm-c]",
    "- [2026-10-04 16:2x r483 bm-c]",
    "- [2026-10-04 17:1x r485 bm-c]",
    "- [2026-10-04 17:3x r688 bm-a]",
    "- [2026-10-04 20:1x r694 bm-a]",
    "[2026-10-05 11:1x r720 bm-a]",
    "- [2026-10-08 03:3x r859 bm-a]",
]
OLD_L4 = "> 执法面：池文件（runnable_pool.json）字节级编辑与写入路径（整文件重写禁律/文本级定点手术/roundtrip 恒等探针/EOL 与 indent 探测/needle 锚定/尾逗号/登记 id 镜像）、settle 写路（origin-tip 身份断言/sync_face 调用面）、池面冲突解与基底选择、reland/重落窗律、翻面执行与补翻手术（lane-mirror 检查域/守卫分档/孤儿击杀）、烧录进程机械（worker 池/IPC 粒度）、点火闸（host_gates/crash fuse 落闸/keepblock 时序与版本键）——上述动作前必读本件（认领/翻面语义/可见性/接管/停泊治理→pit-pool.md）。"
OLD_L5 = "> 字节对账行（零丢失断言）：自 pit-pool.md verbatim 迁出 26 条·条目字节和 26449B==源件同条目字节和（LF blob 面·逐字节恒等）·机械迁移非手抄（变体⑤ bullet-less 三条 r598/r608/r605 随宿主 blob 原样迁移）·receipt=results/_r705bmb_pit_pool_split_receipt.json（r703 范式同源）。"


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def probe_eol(raw):
    crlf = raw.count(b"\r\n")
    lone_lf = raw.replace(b"\r\n", b"").count(b"\n")
    lone_cr = raw.replace(b"\r\n", b"").count(b"\r")
    assert lone_lf == 0 and lone_cr == 0, "mixed EOL face"
    return crlf


def prescan():
    p = subprocess.run([sys.executable, "Tools/treasure_guard.py", "prescan",
                        "research/pit-pool-edit.md"], cwd=ROOT,
                       capture_output=True, creationflags=CNW)
    return p.returncode, (p.stdout + p.stderr).decode("utf-8", "replace")[-400:]


def main() -> int:
    # ---- ritual piece 1: prescan FIRST, rc recorded (r705 same-family canon) --
    prescan_rc, prescan_tail = prescan()
    print("prescan rc=%d tail=%s" % (prescan_rc, prescan_tail[-120:]))
    assert prescan_rc in (0, 3), "unexpected prescan rc %d" % prescan_rc

    # ---- load source, EOL probe ----
    assert not os.path.exists(TGT), "target pit-pool-burn.md already exists"
    raw = open(SRC, "rb").read()
    crlf_n = probe_eol(raw)
    assert crlf_n >= 30, "not a CRLF face (%d)" % crlf_n
    lines = raw.split(b"\r\n")
    before = len(raw)
    lines_txt = [l.decode("utf-8") for l in lines]

    # ---- already-migrated law: anchors absent from sibling file ----
    sib_raw = open(SIB, "rb").read().decode("utf-8")
    for a in ANCHORS:
        assert lines_txt.count(a[:30]) >= 0  # anchor sanity on source side below
        assert a not in sib_raw, "anchor already in sibling pit-pool.md: %s" % a[:40]

    # ---- locate moved entries (unique line-start match) ----
    idx = {}
    for a in ANCHORS:
        hits = [i for i, t in enumerate(lines_txt) if t.startswith(a)]
        assert len(hits) == 1, "anchor not-unique: %s -> %s" % (a[:40], hits)
        assert hits[0] >= 6, "anchor in header zone: %s" % a[:40]
        idx[a] = hits[0]
    moved_idx = sorted(idx.values())
    assert len(set(moved_idx)) == len(ANCHORS)

    # ---- kept anchors must all be present pre-surgery (sanity) ----
    for a in KEPT_ANCHORS:
        hits = [i for i, t in enumerate(lines_txt) if t.startswith(a)]
        assert len(hits) == 1, "kept anchor not-unique pre-surgery: %s -> %s" % (a[:40], hits)

    # ---- build blocks: entry line + trailing blank (if next line blank) ----
    blocks = []          # list of list-of-line-indices
    for a in ANCHORS:
        i = idx[a]
        blk = [i]
        if i + 1 < len(lines) and lines[i + 1] == b"":
            blk.append(i + 1)
        blocks.append(blk)
    moved_lines_idx = sorted(i for blk in blocks for i in blk)

    moved_entry_sum = sum(len(lines[idx[a]]) + 2 for a in ANCHORS)
    moved_block_sum = sum(len(lines[i]) + 2 for i in moved_lines_idx)
    entries_meta = []
    for a in ANCHORS:
        lb = lines[idx[a]]
        entries_meta.append({"anchor": a[:44].decode("utf-8")
                             if isinstance(a, bytes) else a[:44],
                             "bytes_crlf": len(lb) + 2,
                             "sha16": sha16(lb)})

    # ---- rewrite source header L4/L5 (moved faces carved out) ----
    new_l4 = ("> 执法面：池文件（runnable_pool.json）字节级编辑与写入路径（整文件重写禁律/文本级定点手术/"
              "roundtrip 恒等探针/EOL 与 indent 探测/needle 锚定/尾逗号/登记 id 镜像）、settle 写路"
              "（origin-tip 身份断言/sync_face 调用面）、池面冲突解与基底选择、reland/重落窗律、"
              "翻面执行与补翻手术（lane-mirror 检查域/守卫分档）——上述动作前必读本件"
              "（认领/翻面语义/可见性/接管/停泊治理→pit-pool.md；点火闸/烧录进程机械/双烧接管竞态族→pit-pool-burn.md）。")
    new_l5 = ("> 字节对账行（零丢失断言）：自 pit-pool.md verbatim 迁出 26 条·条目字节和 26449B==源件同条目字节和"
              "（LF blob 面·逐字节恒等）·机械迁移非手抄（变体⑤ bullet-less 三条 r598/r608/r605 随宿主 blob 原样迁移）"
              "·receipt=results/_r705bmb_pit_pool_split_receipt.json（r703 范式同源）；"
              "r791 bm-c sub-split（2026-10-09·r790 让位窗挂账承接·r705 仪式同款）："
              "移出 15 条（点火闸/烧录机械/双烧接管竞态族）→pit-pool-burn.md·"
              "条目字节和（含 CRLF 行尾）%dB==源件同条目字节和·逐字节恒等零丢失·"
              "本件回线 18 条（池文件编辑/写入路径/settle/reland 窗/翻面手术/冲突基底族）·"
              "receipt=results/_r791bmc_pit_pool_edit_split_receipt.json。" % moved_entry_sum)
    assert lines_txt[3] == OLD_L4, "L4 drift"
    assert lines_txt[4] == OLD_L5, "L5 drift"
    hdr_delta = ((len(new_l4.encode("utf-8")) + 2) + (len(new_l5.encode("utf-8")) + 2)) \
        - ((len(OLD_L4.encode("utf-8")) + 2) + (len(OLD_L5.encode("utf-8")) + 2))

    # ---- build new source (kept lines + new header) ----
    moved_set = set(moved_lines_idx)
    new_lines = [l for i, l in enumerate(lines) if i not in moved_set]
    new_lines[3] = new_l4.encode("utf-8")
    new_lines[4] = new_l5.encode("utf-8")
    new_raw = b"\r\n".join(new_lines)
    after = len(new_raw)
    assert after == before - moved_block_sum + hdr_delta, \
        "byte accounting mismatch: %d != %d - %d + %d" % (after, before, moved_block_sum, hdr_delta)
    assert after <= CAP, "source still over cap: %d" % after

    # ---- compose pit-pool-burn.md ----
    tgt_header = [
        "# pit-pool-burn —— 池烧录机械与点火闸坑律正典（D-20261002-06 域分件·pit-pool-edit sub-split r791）",
        "",
        "> 来源：research/pit-pool-edit.md verbatim 迁出（2026-10-09 r791 bm-c·D-20261002-06 域件 ≤30KB 再平衡·r790 让位窗挂账承接·r705 仪式同款）。",
        "> 执法面：点火闸（host_gates 登记态×本机复检/crash fuse 落闸与 sig 键/keepblock 时序律/worker-claim 收割件/runner_args 入池形）、烧录进程机械（ProcessPool worker 孤儿全树击杀/initializer fixture 复用/亚百 ms IPC 粒度选件）、双烧与接管竞态（keepalive 分叉窗滞留/checkout 空窗认领/reland 时间戳回退/整面回退吞活认领/claim 竞窗 behind 型诊断）——点火、杀烧、fuse 落闸、接管评估、claim 竞窗处置动作前必读本件；池文件字节编辑/写入路径/settle/翻面手术/池面冲突基底→pit-pool-edit.md（认领/翻面语义/可见性/停泊治理→pit-pool.md）。",
        "> 字节对账行（零丢失断言）：自 pit-pool-edit.md verbatim 迁出 15 条·条目字节和（含 CRLF 行尾）%dB==源件同条目字节和·逐字节恒等零丢失·机械迁移非手抄（变体⑤ bullet-less 两条 r608/r605 随宿主 blob 原样迁移）·receipt=results/_r791bmc_pit_pool_edit_split_receipt.json（r705 范式同源）。" % moved_entry_sum,
        "",
    ]
    tgt_parts = [h.encode("utf-8") for h in tgt_header]
    for blk in blocks:
        for i in blk:
            tgt_parts.append(lines[i])
    if tgt_parts[-1] != b"":
        tgt_parts.append(b"")
    pit_raw = b"\r\n".join(tgt_parts)
    probe_eol(pit_raw)
    assert len(pit_raw) <= CAP, "target over cap: %d" % len(pit_raw)

    # ---- assertion battery before any write ----
    pit_txt_lines = pit_raw.split(b"\r\n")
    for a in ANCHORS:
        ab = a.encode("utf-8")
        assert sum(1 for l in pit_txt_lines if l.startswith(ab)) == 1, \
            "moved entry not exactly-once in target: %s" % a[:40]
        assert ab not in new_raw, "residue in source: %s" % a[:40]
    for a in KEPT_ANCHORS:
        ab = a.encode("utf-8")
        assert sum(1 for l in new_raw.split(b"\r\n") if l.startswith(ab)) == 1, \
            "kept entry lost/dupe in source: %s" % a[:40]
        assert ab not in pit_raw, "kept entry leaked into target: %s" % a[:40]
    for body, name in ((new_raw, "src"), (pit_raw, "tgt")):
        t = body.decode("utf-8")                      # strict utf-8
        assert t.count("\ufffd") == 0 and "????" not in t, "mojibake gate " + name
        assert body.replace(b"\r\n", b"").count(b"\r") == 0, "lone CR " + name
        assert body.replace(b"\r\n", b"").count(b"\n") == 0, "lone LF " + name

    # ---- CODELY.md pool-domain pointer row append (navigation law) ----
    c_raw = open(CODELY, "rb").read()
    c_crlf = probe_eol(c_raw)
    c_lines = c_raw.split(b"\r\n")
    ptr_hits = [i for i, l in enumerate(c_lines)
                if l.decode("utf-8").startswith("- 域指针·D-20261002-06 池域拆件")]
    assert len(ptr_hits) == 1, "pool pointer row not unique: %s" % ptr_hits
    note = ("；r791 bm-c sub-split（10-09·r790 让位窗）：pit-pool-edit 32,616B→%dB 18 条"
            "+pit-pool-burn.md 15 条（点火闸/烧录机械/双烧接管族·字节和恒等·"
            "receipt=results/_r791bmc_pit_pool_edit_split_receipt.json）"
            "——点火/杀烧/fuse 落闸/接管评估动作前改读 pit-pool-burn.md"
            % (after,)).encode("utf-8")
    c_lines[ptr_hits[0]] = c_lines[ptr_hits[0]] + note
    c_new = b"\r\n".join(c_lines)
    assert len(c_new) == len(c_raw) + len(note), "codely byte accounting"
    assert len(c_new) <= CAP, "CODELY.md over cap after note: %d" % len(c_new)

    # ---- TREASURE_REGISTRY.md in/out row append (ritual piece 2) ----
    r_raw = open(REG, "rb").read()
    r_eol_crlf = probe_eol(r_raw)
    reg_row = ("- 2026-10-09 08:4x bm-c r791 D-06 域件 sub-split 迁移仪式"
               "（D-20261002-06 域件 ≤30KB 再平衡·r790 让位窗挂账承接·r705 仪式同款）："
               "prescan 实弹 rc%d 命中 research/pit-pool-edit.md（research/ 全族 fail-closed 面）"
               "——集团拆件令 D-20261002-06 授权×TREASURE_PROTECTION_LAW §2 迁移仪式三件齐："
               "①prescan 留痕（本行）②出入记录=本行 ③零丢失断言："
               "pit-pool-edit.md 32,616B/33 条→本件 18 条 %dB"
               "（池文件编辑/写入路径/settle/reland 窗/翻面手术/冲突基底族）"
               "+pit-pool-burn.md 15 条 %dB（点火闸/烧录机械/双烧接管竞态族）"
               "·条目字节和 %dB 恒等·逐条 verbatim 迁移非手抄"
               "（变体⑤ bullet-less 两条 r608/r605 随宿主 blob 原样迁移）"
               "·receipt=results/_r791bmc_pit_pool_edit_split_receipt.json；"
               "在册路径 pit-pool-edit.md 净瘦身回线 ≤30KB、新件 pit-pool-burn.md 入册。"
               % (prescan_rc, after, len(pit_raw), moved_entry_sum)).encode("utf-8")
    term = b"\r\n" if r_eol_crlf >= 10 else b"\n"
    if r_raw.endswith(term):
        r_new = r_raw + reg_row + term
    else:
        r_new = r_raw + term + reg_row + term

    # ---- ritual piece 3: receipt ----
    receipt = {
        "round": "r791 bm-c", "ticket": "D-20261002-06 (r790 slot-window debt)",
        "kind": "domain sub-split (r705 same-family canon)",
        "prescan_rc": prescan_rc, "prescan_tail": prescan_tail,
        "entries_moved": len(ANCHORS), "entries_kept": len(KEPT_ANCHORS),
        "moved_entry_sum_crlf_B": moved_entry_sum,
        "moved_block_sum_crlf_B": moved_block_sum,
        "hdr_delta_B": hdr_delta,
        "src_before_B": before, "src_after_B": after,
        "src_identity": "after == before - moved_block_sum + hdr_delta",
        "pit_pool_burn_B": len(pit_raw),
        "codely_before_B": len(c_raw), "codely_after_B": len(c_new),
        "registry_row_B": len(reg_row),
        "entries_meta": entries_meta,
        "verdict": "PASS",
    }
    json.loads(json.dumps(receipt))                   # roundtrip gate

    # ---- atomic writes (r614) ----
    for path, data in ((SRC, new_raw), (TGT, pit_raw), (CODELY, c_new), (REG, r_new)):
        tmp = path + ".tmp_r791"
        with open(tmp, "wb") as fh:
            fh.write(data)
        os.replace(tmp, path)
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)

    print("SPLIT PASS: pit-pool-edit %dB->%dB (-%dB blocks +%dB hdr) | "
          "pit-pool-burn %dB | moved entries %dB | CODELY %dB->%dB | prescan rc%d"
          % (before, after, moved_block_sum, hdr_delta, len(pit_raw),
             moved_entry_sum, len(c_raw), len(c_new), prescan_rc))
    return 0


def verify() -> int:
    r = json.load(open(RECEIPT, encoding="utf-8"))
    src_raw = open(SRC, "rb").read()
    tgt_raw = open(TGT, "rb").read()
    c_raw = open(CODELY, "rb").read()
    ok = []
    ok.append(("src_size", len(src_raw) == r["src_after_B"]))
    ok.append(("tgt_size", len(tgt_raw) == r["pit_pool_burn_B"]))
    ok.append(("codely_size", len(c_raw) == r["codely_after_B"]
               and len(c_raw) <= CAP))
    ok.append(("cap_both", len(src_raw) <= CAP and len(tgt_raw) <= CAP))
    src_l = [l.decode("utf-8") for l in src_raw.split(b"\r\n")]
    tgt_l = [l.decode("utf-8") for l in tgt_raw.split(b"\r\n")]
    for a in ANCHORS:
        ok.append(("moved-once-in-tgt " + a[3:24],
                   sum(1 for t in tgt_l if t.startswith(a)) == 1))
        ok.append(("absent-in-src " + a[3:24],
                   sum(1 for t in src_l if t.startswith(a)) == 0))
    for a in KEPT_ANCHORS:
        ok.append(("kept-once-in-src " + a[3:24],
                   sum(1 for t in src_l if t.startswith(a)) == 1))
        ok.append(("kept-not-in-tgt " + a[3:24],
                   sum(1 for t in tgt_l if t.startswith(a)) == 0))
    sum_chk = sum(len(l.encode("utf-8")) + 2
                  for t_l in tgt_l for l in [t_l]
                  if any(l.startswith(a) for a in ANCHORS))
    ok.append(("moved_entry_sum_identity", sum_chk == r["moved_entry_sum_crlf_B"]))
    for body, nm in ((src_raw, "src"), (tgt_raw, "tgt"), (c_raw, "codely")):
        t = body.decode("utf-8")
        ok.append((nm + "-utf8-clean", "????" not in t and "\ufffd" not in t))
    bad = [n for n, v in ok if not v]
    print("VERIFY %s (%d checks, fail=%s)" % ("PASS" if not bad else "FAIL",
                                             len(ok), bad or "none"))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(verify() if "--verify" in sys.argv else main())
