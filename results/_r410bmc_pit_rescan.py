# -*- coding: utf-8 -*-
# r410 bm-c: incremental domain rescan (T-2026-10-02-144(c) D-06 line).
# 9 hot-layer CODELY entries -> pit-git(3) / pit-pool(4) / pit-engine(2), verbatim,
# r399/r401/r402 paradigm: ASCII signatures + keyword guards, all pre-write assertions
# (zero partial write), lone-CR gate, BOM/CRLF preserve, in-file accounting rows,
# byte accounting + md5 (LF blob face), evidence JSON.
# r410 discovery: L75 = r612+r613 FUSED inline (bm-b append missing newline) --
# coupled split surgery dissolves the fusion; new pit entry canonized in-place.
import hashlib, json, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CODELY = ROOT + r"\CODELY.md"
PIT = {
    "git": ROOT + r"\research\pit-git.md",
    "pool": ROOT + r"\research\pit-pool.md",
    "engine": ROOT + r"\research\pit-engine.md",
}

# (domain, signature, keyword_guard) -- line-start entries only
TARGETS = [
    ("git",    "[2026-10-03 06:4x r606 bm-b]", "reland"),
    ("git",    "[2026-10-03 09:1x r405 bm-c]", "rebase"),
    ("git",    "[2026-10-03 09:4x r612 bm-b]", "push"),          # fused line: also carries r613
    ("pool",   "[2026-10-03 07:25 r402 bm-c]", "dualrun"),
    ("pool",   "[2026-10-03 08:5x r404 bm-c]", "merge_lane_views"),
    ("pool",   "[2026-10-03 09:3x r617 bm-a]", "keep-block"),
    ("pool",   "[2026-10-03 10:0x r618 bm-a]", "parent_pid"),
    ("engine", "[2026-10-03 09:2x r611 bm-b]", "autofill"),
]
FUSED_SIG = "[2026-10-03 10:3x r613 bm-b]"   # engine; fused into the r612 line

NEW_PIT = ("- [2026-10-03 10:4x r410 bm-c] CODELY 热层条目行内融合形态坑（r401 块界律第④变体·r410 域回扫实弹抓回）："
           "多机 append 缺换行分隔时后条目头「- [date rNNN bm-x]」被前条目尾吞成同行内联"
           "（实弹：CODELY L75 r612 bm-b 尾吞 r613 bm-b 头·两整条目同行·git grep -c 假象=单行双条目）——"
           "按「bullet 行起始=块界」的回扫器 startswith 过滤恒漏检（cands=0 fail-closed 当场拦·零部分写）；"
           "两融合条目恰双属迁移目标时整行删除=融合自然拆解（本窗 r612→pit-git、r613→pit-engine 双拆实证）。"
           "How to apply：域回扫器必带行内「- [」锚兜底腿（line-start 零候选后 substring 定位+前置句号边界断言再拆）；"
           "多机共写 append 面（CODELY/轮报告类）写前核尾字节为换行。")

ROW_NOTE = {
    "git": "；r410 bm-c 增量回扫 3 条（10-03 06:4x r606~09:4x r612 批）已入件（件内对账行为准）。",
    "pool": "；r410 bm-c 增量回扫 4 条（10-03 07:25 r402~10:0x r618 批）已入件（件内对账行为准）。",
    "engine": "；r410 bm-c 增量回扫 2 条（10-03 09:2x r611~10:3x r613 批·r613 自 r612 融合行拆出）已入件（件内对账行为准）。",
}


def read_text(path):
    with open(path, "rb") as f:
        raw = f.read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    lone = sum(1 for i, b in enumerate(raw) if b == 0x0D and (i + 1 >= len(raw) or raw[i + 1] != 0x0A))
    if lone:
        print("ABORT lone_CR=%d in %s" % (lone, path))
        sys.exit(2)
    nl = "\r\n" if "\r\n" in text else "\n"
    return raw, text, bom, nl


# ---------- phase A: read + verify + plan (zero writes) ----------
raw_c, text_c, bom_c, nl_c = read_text(CODELY)
lines_c = text_c.split(nl_c)
if nl_c.join(lines_c) != text_c:
    print("ABORT CODELY split/join roundtrip")
    sys.exit(2)
print("CODELY bom=%s nl=%r bytes=%d lines=%d" % (bom_c, nl_c, len(raw_c), len(lines_c)))

removed = []          # (domain, sig, entry_text)
remove_idx = []
fused_info = None
for dom, sig, kw in TARGETS:
    cands = [i for i, ln in enumerate(lines_c)
             if (ln.startswith("- " + sig) or ln.startswith(sig))]
    if kw:
        cands = [i for i in cands if kw in lines_c[i]]
    if len(cands) != 1:
        print("ABORT sig=%s cands=%d %s" % (sig, len(cands), cands))
        sys.exit(2)
    i = cands[0]
    line = lines_c[i]
    if "???" in line:
        print("ABORT mojibake run in %s" % sig)
        sys.exit(2)
    if sig == "[2026-10-03 09:4x r612 bm-b]":
        marker = "- " + FUSED_SIG
        if line.count(marker) != 1:
            print("ABORT fused marker count=%d (expected fused form on r612 line)" % line.count(marker))
            sys.exit(2)
        idx = line.index(marker)
        if not line[:idx].endswith("。"):
            print("ABORT fused split boundary lacks preceding 。")
            sys.exit(2)
        e612 = line[:idx]
        e613 = line[idx:]
        if "selftest" not in e613 or "镜像" not in e613:
            print("ABORT fused r613 guard failed")
            sys.exit(2)
        if len(e612.encode("utf-8")) < 400 or len(e613.encode("utf-8")) < 400:
            print("ABORT fused parts too short")
            sys.exit(2)
        removed.append(("git", sig, e612))
        removed.append(("engine", FUSED_SIG, e613))
        fused_info = {"line_index": i, "e612_bytes": len(e612.encode("utf-8")),
                      "e613_bytes": len(e613.encode("utf-8")),
                      "orig_line_bytes": len(line.encode("utf-8"))}
        print("FOUND %s -> git (line %d, %dB) + FUSED r613 -> engine (%dB)" %
              (sig, i, fused_info["e612_bytes"], fused_info["e613_bytes"]))
    else:
        if len(line.encode("utf-8")) < 200:
            print("ABORT suspiciously short entry %s" % sig)
            sys.exit(2)
        removed.append((dom, sig, line))
        print("FOUND %s -> %s (line %d, %dB)" % (sig, dom, i, len(line.encode("utf-8"))))
    remove_idx.append(i)

if len(remove_idx) != len(set(remove_idx)):
    print("ABORT duplicate line removal")
    sys.exit(2)
if len(removed) != 9:
    print("ABORT expected 9 extracted entries, got %d" % len(removed))
    sys.exit(2)

# pointer-row anchors: exactly one 域指针 row per target pit file
for dom in ("git", "pool", "engine"):
    rows = [i for i, ln in enumerate(lines_c)
            if ("research/pit-%s.md" % dom) in ln and "域指针" in ln and "D-20261002-06" in ln]
    if len(rows) != 1:
        print("ABORT ptr rows for %s: %s" % (dom, rows))
        sys.exit(2)
    if not lines_c[rows[0]].endswith("。"):
        print("ABORT ptr row %s does not end with 。" % dom)
        sys.exit(2)
    print("PTR %s row %d edit planned" % (dom, rows[0]))

# survivor assertions pre-check (r401 five-piece law)
surv = {
    "ptr_rows": sum(1 for ln in lines_c if "域指针·D-20261002-06" in ln),
    "sec4_pin": sum(1 for ln in lines_c if "跳位语义钉定行" in ln or "跳位语义钉死行" in ln),
    "h_user": sum(1 for ln in lines_c if ln.strip() == "### User"),
    "h_project": sum(1 for ln in lines_c if ln.strip() == "### Project"),
    "h_reference": sum(1 for ln in lines_c if ln.strip() == "### Reference"),
}
print("SURVIVOR pre: %s" % surv)
if surv["ptr_rows"] != 5 or surv["sec4_pin"] != 2 or surv["h_user"] < 1 or surv["h_project"] < 1 or surv["h_reference"] < 1:
    print("ABORT survivor pre-check failed")
    sys.exit(2)

# pit files pre-read
pit_state = {}
for dom, path in PIT.items():
    raw_p, text_p, bom_p, nl_p = read_text(path)
    if not text_p.endswith(nl_p):
        print("ABORT pit file %s lacks trailing newline" % dom)
        sys.exit(2)
    lines_p = text_p.split(nl_p)
    hdr = [i for i, ln in enumerate(lines_p) if ln.startswith("> 增量回扫行")]
    if not hdr:
        print("ABORT pit %s has no 增量回扫行 row" % dom)
        sys.exit(2)
    pit_state[dom] = (raw_p, text_p, bom_p, nl_p, lines_p, hdr[-1])
    print("PIT %s bom=%s nl=%r bytes=%d last_scan_row=%d" % (dom, bom_p, nl_p, len(raw_p), hdr[-1]))

# ---------- phase B: transform in memory ----------
entries_by_dom = {"git": [], "pool": [], "engine": []}
for dom, sig, line in removed:
    entries_by_dom[dom].append(line)
for i in sorted(set(remove_idx), reverse=True):
    del lines_c[i]
# pointer-row edits: re-locate by anchor post-deletion (indices shift safety)
for dom in ("git", "pool", "engine"):
    rows = [i for i, ln in enumerate(lines_c)
            if ("research/pit-%s.md" % dom) in ln and "域指针" in ln and "D-20261002-06" in ln]
    if len(rows) != 1:
        print("ABORT ptr re-locate %s: %s" % (dom, rows))
        sys.exit(2)
    lines_c[rows[0]] = lines_c[rows[0]][:-1] + ROW_NOTE[dom]
# append the new fusion pit entry at file end (before trailing terminator)
if lines_c and lines_c[-1] == "":
    lines_c.insert(len(lines_c) - 1, NEW_PIT)
else:
    lines_c.append(NEW_PIT)
text_c_new = nl_c.join(lines_c)

# zero-残留 assertions (per-line sig+keyword joint filter; r404 twin shares the sig)
for dom, sig, kw in TARGETS:
    if any((sig in ln) and (kw in ln) for ln in lines_c):
        print("ABORT residue %s" % sig)
        sys.exit(2)
if any(FUSED_SIG in ln for ln in lines_c):
    print("ABORT residue %s" % FUSED_SIG)
    sys.exit(2)
# twin check: r404 $args twin must remain exactly once
twin = [ln for ln in lines_c if ln.startswith("- [2026-10-03 08:5x r404 bm-c]") or ln.startswith("[2026-10-03 08:5x r404 bm-c]")]
if len(twin) != 1 or "merge_lane_views" in twin[0]:
    print("ABORT r404 twin check: %d" % len(twin))
    sys.exit(2)
print("RESIDUE-OK twin_kept=1 new_pit_appended=1")

# survivor assertions post-transform
surv_post = {
    "ptr_rows": sum(1 for ln in lines_c if "域指针·D-20261002-06" in ln),
    "sec4_pin": sum(1 for ln in lines_c if "跳位语义钉定行" in ln or "跳位语义钉死行" in ln),
    "h_user": sum(1 for ln in lines_c if ln.strip() == "### User"),
    "h_project": sum(1 for ln in lines_c if ln.strip() == "### Project"),
    "h_reference": sum(1 for ln in lines_c if ln.strip() == "### Reference"),
}
if surv_post != surv:
    print("ABORT survivor post-check %s" % surv_post)
    sys.exit(2)
print("SURVIVOR post: identical %s" % surv_post)

# pit file transforms + accounting
report = {"round": "r410 bm-c", "ticket": "T-2026-10-02-144(c)",
          "fusion_repaired": fused_info, "domains": {}}
for dom, path in PIT.items():
    raw_p, text_p, bom_p, nl_p, lines_p, h_last = pit_state[dom]
    ents = entries_by_dom[dom]
    block_lf = "\n" + "\n\n".join(ents) + "\n"
    block_lf_b = block_lf.encode("utf-8")
    md5 = hashlib.md5(block_lf_b).hexdigest()
    sig_list = "、".join(s for d, s, _ in TARGETS if d == dom) + ("、" + FUSED_SIG if dom == "engine" else "")
    dom_label = {"git": "git", "pool": "池", "engine": "引擎"}[dom]
    row_full = ("> 增量回扫行（r410 bm-c·T-2026-10-02-144(c)）：热层%s域条目 %d 条 verbatim 追加"
                "（10-03 批：%s）·追加核 %d B（LF blob 面·md5=%s）·零丢失断言 PASS"
                "（逐行 verbatim 在场+源件零残留·机械迁移非手抄·r399 范式同源；%s）") % (
        dom_label, len(ents), sig_list, len(block_lf_b), md5,
        "r613 自 r612 行内融合行拆出" if dom == "engine" else "整行迁移")
    lines_p2 = list(lines_p)
    lines_p2.insert(h_last + 1, row_full)
    block_wt = block_lf.replace("\n", nl_p)
    text_p_new = nl_p.join(lines_p2) + block_wt
    for e in ents:
        if text_p_new.count(e) != 1:
            print("ABORT verbatim count !=1 in %s" % dom)
            sys.exit(2)
    report["domains"][dom] = {
        "entries": ([s for d, s, _ in TARGETS if d == dom] + ([FUSED_SIG] if dom == "engine" else [])),
        "block_lf_bytes": len(block_lf_b),
        "block_lf_md5": md5,
        "pit_bytes_before": len(raw_p),
        "pit_bytes_after": len(text_p_new.encode("utf-8")) + (3 if bom_p else 0),
        "expected_numstat_adds": len(ents) * 2 + 1,
    }
    pit_state[dom] = (raw_p, text_p_new, bom_p, nl_p, None, h_last)

removed_bytes = sum(len((e + nl_c).encode("utf-8")) for _, _, e in removed)
codely_new_bytes = len(text_c_new.encode("utf-8")) + (3 if bom_c else 0)
report["codely"] = {
    "bytes_before": len(raw_c), "bytes_after": codely_new_bytes,
    "removed_entries_bytes_wt": removed_bytes,
    "removed_count": 9,
    "ptr_rows_edited": 3,
    "new_pit_appended": NEW_PIT[:40],
    "expected_numstat": "4 11",
}

# ---------- phase C: write everything ----------
data_c = text_c_new.encode("utf-8")
if bom_c:
    data_c = b"\xef\xbb\xbf" + data_c
with open(CODELY, "wb") as f:
    f.write(data_c)
for dom, path in PIT.items():
    raw_p, text_p_new, bom_p, nl_p, _, _ = pit_state[dom]
    data_p = text_p_new.encode("utf-8")
    if bom_p:
        data_p = b"\xef\xbb\xbf" + data_p
    with open(path, "wb") as f:
        f.write(data_p)

# read-back verification
_, rb_text, _, rb_nl = read_text(CODELY)
ok = True
rb_lines = rb_text.split(rb_nl)
for dom, sig, kw in TARGETS:
    if any((sig in ln) and (kw in ln) for ln in rb_lines):
        print("READBACK-FAIL residue %s" % sig)
        ok = False
if any(FUSED_SIG in ln for ln in rb_lines):
    print("READBACK-FAIL residue fused sig")
    ok = False
twin = [ln for ln in rb_lines if ln.startswith("- [2026-10-03 08:5x r404 bm-c]")]
if len(twin) != 1:
    print("READBACK-FAIL r404 twin=%d" % len(twin))
    ok = False
if sum(1 for ln in rb_lines if ln.startswith("- [2026-10-03 10:4x r410 bm-c]")) != 1:
    print("READBACK-FAIL new pit entry missing")
    ok = False
for dom, path in PIT.items():
    _, rb_p, _, _ = read_text(path)
    for d2, s2, _k in TARGETS:
        if d2 == dom:
            src = [e for dd, ss, e in removed if dd == dom and ss == s2]
            if len(src) != 1 or rb_p.count(src[0]) != 1:
                print("READBACK-FAIL verbatim %s in %s" % (s2, dom))
                ok = False
    if dom == "engine":
        src = [e for dd, ss, e in removed if dd == "engine" and ss == FUSED_SIG]
        if len(src) != 1 or rb_p.count(src[0]) != 1:
            print("READBACK-FAIL verbatim fused r613 in engine")
            ok = False
if not ok:
    sys.exit(2)

with open(ROOT + r"\results\_r410bmc_pit_rescan.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print("ALL-WRITTEN codely %d->%d (entries out %dB) pits=git3/pool4/engine2 fusion_repaired=%s" %
      (len(raw_c), codely_new_bytes, removed_bytes, bool(fused_info)))
print("EVIDENCE results/_r410bmc_pit_rescan.json")
