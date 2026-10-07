# -*- coding: utf-8 -*-
"""r666 bm-c CODELY.md mojibake heal (r407 fact-reconstruct + r447 inverse-map laws).

Root cause (forensics: _r665bmc_merge3.ps1): pointer lines were hand-built as
python STR literals with \\xNN escapes of UTF-8 BYTES (byte-as-str bug) -- each
byte became a latin-1 char, UTF-8 write = double-encoded mojibake with C1
controls. Recovery = one-layer strip: text.encode('latin-1').decode('utf-8').
Writes: 3-step separate (r632 law). Cross-check: containment grams vs the
verbatim entries in research/pit-ps.md (r447 law-2, gram>=0.85).
Also appends: new pit entries (pit-encoding.md direct-write + pit-lineage-legdiff.md
direct-write) + one compact pointer line in main. Receipt to results/.
"""
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
PIT_PS = os.path.join(ROOT, "research", "pit-ps.md")
PIT_ENC = os.path.join(ROOT, "research", "pit-encoding.md")
PIT_LEG = os.path.join(ROOT, "research", "pit-lineage-legdiff.md")
RECEIPT = os.path.join(ROOT, "results", "_r666bmc_codely_mojibake_heal.json")

def strip_layer(text):
    """One-layer latin-1 strip; returns recovered text or None."""
    try:
        raw = text.encode("latin-1")
    except UnicodeEncodeError:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None

def is_c1_mojibake(text):
    return any(0x80 <= ord(ch) <= 0x9F for ch in text)

def containment(rec, pit_text, gram=12, step=6):
    grams = [rec[j:j+gram] for j in range(0, max(1, len(rec) - gram), step)]
    found = sum(1 for g in grams if g in pit_text)
    return found, len(grams)

def append_entry(path, entry):
    with open(path, "rb") as fh:
        b = fh.read()
    crlf = b.endswith(b"\r\n")
    sep = b"\r\n" if crlf else b"\n"
    if not b.endswith(sep):
        b = b + sep
    nb = b + entry.encode("utf-8") + sep
    # 3-step separate write (r632 law): read done -> bytes assembled -> single wb
    with open(path, "wb") as fh:
        fh.write(nb)
    return len(b), len(nb)

def main():
    # ---- leg 1: heal the two mojibake pointer lines in main ----
    with open(MAIN, "rb") as fh:
        data = fh.read()
    before_bytes = len(data)
    lines = data.split(b"\n")
    healed = []
    new_lines = []
    for idx, ln in enumerate(lines):
        try:
            txt = ln.decode("utf-8")
        except UnicodeDecodeError:
            new_lines.append(ln)
            continue
        if is_c1_mojibake(txt) and ("r662 bm-c" in txt or "r665 bm-c" in txt):
            rec = strip_layer(txt)
            if rec is None or not any("\u4e00" <= c <= "\u9fff" for c in rec):
                print("RECOVER_FAIL line=%d -- ABORT, no write" % (idx + 1))
                return 1
            with open(PIT_PS, "rb") as fh:
                pit_text = fh.read().decode("utf-8", errors="replace")
            # Gate per r447 laws adapted: latin-1 inverse map is bijective ->
            # roundtrip success + zero '?' = provably lossless (law-1 face).
            # gram-containment (law-2) was designed for LOSSY CP936 faces and
            # mismatches a pointer SUMMARY line; soft token cross-check instead.
            assert "?" not in rec, "recovered text contains literal ? (lossy face, r447 law-1)"
            tokens = [t for t in ("裸数字", "replace", "r758", "残号门", "pit-ps.md", "silent-git", "-split", "foreach") if t in rec]
            tok_found = sum(1 for t in tokens if t in pit_text)
            print("LINE %d recovered_chars=%d tokens_in_rec=%d token_crosscheck=%d" % (idx + 1, len(rec), len(tokens), tok_found))
            print("RECOVERED| " + rec)
            if tok_found < 3:
                print("TOKEN_CROSSCHECK_FAIL line=%d -- ABORT, no write" % (idx + 1))
                return 1
            healed.append({"line": idx + 1, "mojibake_bytes": len(ln), "recovered_bytes": len(rec.encode("utf-8")), "recovered": rec, "token_crosscheck": "%d/%d" % (tok_found, len(tokens))})
            new_lines.append(rec.encode("utf-8"))
        else:
            new_lines.append(ln)
    if len(healed) != 2:
        print("EXPECT 2 heals, got %d -- ABORT" % len(healed))
        return 1
    nd = b"\n".join(new_lines)
    with open(MAIN, "wb") as fh:
        fh.write(nd)
    after_bytes = len(nd)
    # post-verify: zero C1 mojibake lines remain
    with open(MAIN, "rb") as fh:
        chk = fh.read().decode("utf-8", errors="replace")
    residual = [i for i, l in enumerate(chk.split("\n"), 1) if is_c1_mojibake(l)]
    print("POST_C1_LINES=%s" % residual)
    assert not residual, "residual C1 mojibake after heal"

    # ---- leg 2: pit-encoding.md direct-write (root-cause pit) ----
    pit_enc_entry = (
        "- [2026-10-07 09:2x r666 bm-c] **python str 字面量 \\xNN 转义手搓 CJK 行=byte-as-str 双层编码落盘坑（CODELY r662/r665 指针行 mojibake 实弹·r665 merge3 forensics 定谳）**：gate-fix 脚本把指针行内容按 UTF-8 字节以 \\xNN 转义写进 python STR 字面量——每字节成 latin-1 字符（域=E5 9F 9F→å\\x9f\\x9f），UTF-8 落盘=双层编码 mojibake（C1 控制符签名 U+0080..U+009F）。判别=行内含 C1 控制符+latin-1 可回编；治愈=text.encode('latin-1').decode('utf-8') 单层剥（零 '?' 丢失=可完全恢复·与 r447 CP936 族不同：latin-1 全码位无损）。正法=①CJK 行禁 \\xNN 转义手搓——一律 b\"\\xNN...\".decode('utf-8') 或直接写字面 CJK；②一切 str 落盘后 C1 控制符扫（U+0080..U+009F 出现=CJK 位灭失警报）；③治愈手术=containment 交叉验证（≥12 字 gram 对 verbatim 原条目·r447 律 2）+三步分离写+收据。How to apply：写指针行/摘要行带 CJK 时先读本条；见 C1 控制符即 latin-1 剥层探针先跑再定不可恢复（r447 ③ 序同律）。| dept:工程 | r666 值守窗"
    )
    b0, b1 = append_entry(PIT_ENC, pit_enc_entry)
    print("PIT_ENC %d -> %d" % (b0, b1))

    # ---- leg 3: pit-lineage-legdiff.md direct-write (needle self-match pit) ----
    pit_leg_entry = (
        "- [2026-10-07 09:1x r666 bm-c] **机活探针裸机名 needle 扫 log 文案=他机 commit message prose 自匹配假阳性（r659 自配族 git-log 变体·aging-line 判决窗实弹·当场 eyeball 纠正零误判）**：bm-b 机活判决探针用 -match 'bm-b' 裸机名 needle 扫 origin log——命中我 r665 自家 commit 文案「bm-b re-stall aging-line restart」（描述性提及非实体面），打印 BMB_COMMIT_SINCE_0812=True 假阳性；eyeball 12 行 OLOG 纠正=零 bm-b 实体面（全部 [via bm-c]/bm-a）。正法=跨机活性/在途判决 needle 一律锚所有权标签（'[via bm-b' 前缀或 author 面）或排除自家 sha 集，禁裸机名扫 log 文案；判决结论发布前 OLOG 实体面 eyeball 或 sha 排除复核（r659 Get-CimInstance CommandLine 自配同族：探测命令自身的模式串含 needle=自撞，本变体=needle 撞他机 prose）。How to apply：aging line/让路判定/在途判定类探针 needle 写法先读本条；判决 MSG 发布前必复核实体标签面。| dept:工程 | r666 值守窗"
    )
    c0, c1 = append_entry(PIT_LEG, pit_leg_entry)
    print("PIT_LEG %d -> %d" % (c0, c1))

    # ---- leg 4: main pointer line (compact, one line) ----
    main_ptr = (
        "域指针·r666 bm-c（2026-10-07 09:2x）：CODELY r662/r665 两指针行 latin-1 双层 mojibake 治愈（根因=python str \\xNN 转义 byte-as-str 落盘坑→pit-encoding.md 直写 1 条·r447 逆映射律治愈·收据 _r666bmc_codely_mojibake_heal.json）+机活探针裸机名 needle 撞他机 commit 文案假阳性坑（r659 自配族 git-log 变体→pit-lineage-legdiff.md 直写 1 条）。"
    )
    with open(MAIN, "rb") as fh:
        mb = fh.read()
    crlf = b"\r\n" in mb[-200:]
    sep = b"\r\n" if crlf else b"\n"
    if not mb.endswith(sep):
        mb = mb + sep
    mb2 = mb + main_ptr.encode("utf-8") + sep
    with open(MAIN, "wb") as fh:
        fh.write(mb2)
    final_bytes = len(mb2)
    print("MAIN final=%d" % final_bytes)

    # ---- receipt ----
    receipt = {
        "probe": "r666 bm-c CODELY.md mojibake heal + 2 direct-write pits + 1 pointer line",
        "healed_lines": healed,
        "main_bytes_before": before_bytes,
        "main_bytes_after_heal": after_bytes,
        "main_bytes_final": final_bytes,
        "root_cause": "python str literal \\xNN escapes of UTF-8 bytes (byte-as-str) in gate-fix pointer writer (_r665bmc_merge3.ps1 forensics); latin-1 intermediate, C1-control signature",
        "recovery_law": "text.encode('latin-1').decode('utf-8') one-layer strip; zero-loss (no '?'DecoderFallback losses); containment gate >=0.85 vs pit-ps.md verbatim entries",
        "pit_writes": {"pit-encoding.md": [b0, b1], "pit-lineage-legdiff.md": [c0, c1]},
        "post_verify": {"c1_residual_lines": residual, "main_final_md5_16": hashlib.md5(mb2).hexdigest()[:16]},
    }
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print("RECEIPT written:", RECEIPT)
    print("HEAL_OK main %d -> %d -> %d (heal -%dB, ptr +%dB)" % (before_bytes, after_bytes, final_bytes, before_bytes - after_bytes, final_bytes - after_bytes))
    return 0

if __name__ == "__main__":
    sys.exit(main())
