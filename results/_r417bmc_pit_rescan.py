# -*- coding: utf-8 -*-
# r417 bm-c: D-06 batch4 git/protocol domain incremental rescan (T-2026-10-02-144(c)).
# 5 hot-layer CODELY entries verbatim -> pit-git(2: r366-ls-tree / r614-rebase-livefile)
# / pit-protocol(3: r366-laneio / r371 / r415-HANDOVER-machine-id), r399/r401/r411 paradigm.
# Variant-5 (bullet-less) lines found on L43/L44: 2B "- " normalization applied BEFORE
# verbatim migration (r411 bullet-repair precedent; accounting row records the 4B separately).
import hashlib, json, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CODELY = ROOT + r"\CODELY.md"
PIT = {
    "git": ROOT + r"\research\pit-git.md",
    "protocol": ROOT + r"\research\pit-protocol.md",
}

# (domain, signature, keyword_guard, bullet_less)
TARGETS = [
    ("git",      "[2026-10-02 13:1x r366 bm-c]", "外科 update-index", True),
    ("git",      "[2026-10-03 11:2x r614 bm-b]", "rebase checkout 截断活写文件", False),
    ("protocol", "[2026-10-02 13:2x r366 bm-c]", "lane_io 守卫本地树心跳读面", True),
    ("protocol", "[2026-10-02 15:3x r371 bm-c]", "lane_io origin-ref 心跳读腿", False),
    ("protocol", "[2026-10-03 13:0x r415 bm-c]", "HANDOVER 5x 行插入唯一性断言", False),
]

ROW_NOTE = {
    "git": "；r417 bm-c 增量回扫 2 条（r366 ls-tree 列位切错〔变体⑤ bullet-less 形迁移前 2B 归正·r411 前例同源〕+r614 rebase-截断活写）已入件（件内对账行为准）。",
    "protocol": "；r417 bm-c 增量回扫 3 条（r366 lane_io stale-view 假接管〔变体⑤ bullet-less 形迁移前 2B 归正〕/r371 origin-ref 心跳读腿/r415 HANDOVER 5x 机号限定）已入件（件内对账行为准）。",
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

removed = []   # (dom, sig, line_final)  line_final = after bullet normalization
remove_idx = []
bullet_fixed = 0
for dom, sig, kw, bl in TARGETS:
    cands = [i for i, ln in enumerate(lines_c)
             if (ln.startswith("- " + sig) or ln.startswith(sig))]
    if kw:
        cands = [i for i in cands if kw in lines_c[i]]
    if len(cands) != 1:
        print("ABORT sig=%s cands=%d %s" % (sig, len(cands), cands))
        sys.exit(2)
    i = cands[0]
    line = lines_c[i]
    if bl:
        if line.startswith("- " + sig):
            print("ABORT expected bullet-less but has bullet: %s" % sig)
            sys.exit(2)
        line = "- " + line
        bullet_fixed += 1
    else:
        if not line.startswith("- " + sig):
            print("ABORT expected bullet form missing: %s" % sig)
            sys.exit(2)
    if "???" in line:
        print("ABORT mojibake run in %s" % sig)
        sys.exit(2)
    if len(line.encode("utf-8")) < 300:
        print("ABORT suspiciously short entry %s" % sig)
        sys.exit(2)
    removed.append((dom, sig, line))
    remove_idx.append(i)
    print("FOUND %s -> %s (line %d, %dB%s)" % (sig, dom, i + 1, len(line.encode("utf-8")),
          " [bullet+2B]" if bl else ""))

if len(remove_idx) != len(set(remove_idx)):
    print("ABORT duplicate line removal")
    sys.exit(2)
if len(removed) != 5:
    print("ABORT expected 5 extracted entries, got %d" % len(removed))
    sys.exit(2)
if bullet_fixed != 2:
    print("ABORT bullet_fixed=%d expected 2" % bullet_fixed)
    sys.exit(2)

# pointer-row anchors: exactly one 域指针 row per target pit file, ends with 。
ptr_rows = {}
for dom in ("git", "protocol"):
    rows = [i for i, ln in enumerate(lines_c)
            if ("research/pit-%s.md" % dom) in ln and "域指针" in ln and "D-20261002-06" in ln]
    if len(rows) != 1:
        print("ABORT ptr rows for %s: %s" % (dom, rows))
        sys.exit(2)
    if not lines_c[rows[0]].endswith("。"):
        print("ABORT ptr row %s does not end with 。" % dom)
        sys.exit(2)
    ptr_rows[dom] = rows[0]
    print("PTR %s row %d edit planned" % (dom, rows[0] + 1))

# survivor assertions
surv = {
    "ptr_rows": sum(1 for ln in lines_c if "域指针·D-20261002-06" in ln),
    "sec4_pin": sum(1 for ln in lines_c if "跳位语义钉定行" in ln or "跳位语义钉死行" in ln),
    "h_user": sum(1 for ln in lines_c if ln.strip() == "### User"),
    "h_project": sum(1 for ln in lines_c if ln.strip() == "### Project"),
    "h_reference": sum(1 for ln in lines_c if ln.strip() == "### Reference"),
}
print("SURVIVOR pre: %s" % surv)
if surv["ptr_rows"] != 8 or surv["sec4_pin"] != 2 or surv["h_user"] < 1 or surv["h_project"] < 1 or surv["h_reference"] < 1:
    print("ABORT survivor pre-check failed")
    sys.exit(2)

# pit files pre-read
pit_state = {}
for dom, path in PIT.items():
    raw_p, text_p, bom_p, nl_p = read_text(path)
    tail_fix = 0
    if not text_p.endswith(nl_p) and text_p.endswith("\n") and nl_p == "\r\n":
        # lone-LF trailing terminator (r410-batch residue): normalize to file-dominant CRLF, +1B
        text_p = text_p[:-1] + "\r\n"
        tail_fix = 1
        print("PIT %s tail lone-LF normalized to CRLF (+1B)" % dom)
    if not text_p.endswith(nl_p):
        print("ABORT pit file %s lacks trailing newline" % dom)
        sys.exit(2)
    lines_p = text_p.split(nl_p)
    hdr = [i for i, ln in enumerate(lines_p) if ln.startswith("> 增量回扫行")]
    if not hdr:
        print("ABORT pit %s has no 增量回扫行 row" % dom)
        sys.exit(2)
    pit_state[dom] = (raw_p, text_p, bom_p, nl_p, lines_p, hdr[-1], tail_fix)
    print("PIT %s bom=%s nl=%r bytes=%d last_scan_row=%d tail_fix=%d" % (dom, bom_p, nl_p, len(raw_p), hdr[-1] + 1, tail_fix))

# ---------- phase B: transform in memory ----------
entries_by_dom = {"git": [], "protocol": []}
for dom, sig, line in removed:
    entries_by_dom[dom].append(line)
for i in sorted(set(remove_idx), reverse=True):
    del lines_c[i]
# pointer-row edits (re-located post-deletion)
for dom in ("git", "protocol"):
    rows = [i for i, ln in enumerate(lines_c)
            if ("research/pit-%s.md" % dom) in ln and "域指针" in ln and "D-20261002-06" in ln]
    if len(rows) != 1:
        print("ABORT ptr re-locate %s: %s" % (dom, rows))
        sys.exit(2)
    lines_c[rows[0]] = lines_c[rows[0]][:-1] + ROW_NOTE[dom]
text_c_new = nl_c.join(lines_c)

# zero-residue assertions
for dom, sig, kw, _bl in TARGETS:
    if any((sig in ln) and (kw in ln) for ln in lines_c):
        print("ABORT residue %s" % sig)
        sys.exit(2)

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
report = {"round": "r417 bm-c", "ticket": "T-2026-10-02-144(c)",
          "bullet_fixed_before_migration": {"count": bullet_fixed, "bytes": bullet_fixed * 2},
          "domains": {}}
for dom, path in PIT.items():
    raw_p, text_p, bom_p, nl_p, lines_p, h_last, tail_fix = pit_state[dom]
    ents = entries_by_dom[dom]
    block_lf = "\n" + "\n\n".join(ents) + "\n"
    block_lf_b = block_lf.encode("utf-8")
    md5 = hashlib.md5(block_lf_b).hexdigest()
    sig_list = "、".join(s for d, s, _k, _b in TARGETS if d == dom)
    dom_label = {"git": "git", "protocol": "协议"}[dom]
    row_full = ("> 增量回扫行（r417 bm-c·T-2026-10-02-144(c)）：热层%s域条目 %d 条 verbatim 追加"
                "（r417 批：%s·其中变体⑤ bullet-less 形迁移前 2B/条归正）·追加核 %d B（LF blob 面·md5=%s）"
                "·零丢失断言 PASS（逐行 verbatim 在场+源件零残留·机械迁移非手抄·r399 范式同源；整行迁移）") % (
        dom_label, len(ents), sig_list, len(block_lf_b), md5)
    lines_p2 = list(lines_p)
    lines_p2.insert(h_last + 1, row_full)
    block_wt = block_lf.replace("\n", nl_p)
    text_p_new = nl_p.join(lines_p2) + block_wt
    for e in ents:
        if text_p_new.count(e) != 1:
            print("ABORT verbatim count !=1 in %s" % dom)
            sys.exit(2)
    report["domains"][dom] = {
        "entries": [s for d, s, _k, _b in TARGETS if d == dom],
        "block_lf_bytes": len(block_lf_b),
        "block_lf_md5": md5,
        "pit_bytes_before": len(raw_p),
        "pit_bytes_after": len(text_p_new.encode("utf-8")) + (3 if bom_p else 0),
        "tail_lf_to_crlf_fix_bytes": tail_fix,
    }
    pit_state[dom] = (raw_p, text_p_new, bom_p, nl_p, None, h_last, tail_fix)

removed_bytes = sum(len((e + nl_c).encode("utf-8")) for _, _, e in removed)
ptr_note_bytes = sum(len(ROW_NOTE[d].encode("utf-8")) for d in ("git", "protocol"))
codely_new_bytes = len(text_c_new.encode("utf-8")) + (3 if bom_c else 0)
report["codely"] = {
    "bytes_before": len(raw_c), "bytes_after": codely_new_bytes,
    "removed_entries_bytes_wt": removed_bytes,
    "removed_count": 5,
    "bullet_fixed_bytes": bullet_fixed * 2,   # included in removed_bytes (normalized form migrated)
    "ptr_rows_edited": 2,
    "ptr_note_bytes_wt": ptr_note_bytes,
    "expected_numstat": "7 2",
}

# ---------- phase C: write everything ----------
data_c = text_c_new.encode("utf-8")
if bom_c:
    data_c = b"\xef\xbb\xbf" + data_c
with open(CODELY, "wb") as f:
    f.write(data_c)
for dom, path in PIT.items():
    raw_p, text_p_new, bom_p, nl_p, _, _, _ = pit_state[dom]
    data_p = text_p_new.encode("utf-8")
    if bom_p:
        data_p = b"\xef\xbb\xbf" + data_p
    with open(path, "wb") as f:
        f.write(data_p)

# read-back verification
_, rb_text, _, rb_nl = read_text(CODELY)
ok = True
rb_lines = rb_text.split(rb_nl)
for dom, sig, kw, _bl in TARGETS:
    if any((sig in ln) and (kw in ln) for ln in rb_lines):
        print("READBACK-FAIL residue %s" % sig)
        ok = False
for dom, path in PIT.items():
    _, rb_p, _, _ = read_text(path)
    for d2, s2, _k, _b in TARGETS:
        if d2 == dom:
            src = [e for dd, ss, e in removed if dd == dom and ss == s2]
            if len(src) != 1 or rb_p.count(src[0]) != 1:
                print("READBACK-FAIL verbatim %s in %s" % (s2, dom))
                ok = False
if not ok:
    sys.exit(2)

with open(ROOT + r"\results\_r417bmc_pit_rescan.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print("ALL-WRITTEN codely %d->%d (5 entries out %dB incl 4B bullet-normalize, ptr notes +%dB) pits=git2/protocol3" %
      (len(raw_c), codely_new_bytes, removed_bytes, ptr_note_bytes))
print("EVIDENCE results/_r417bmc_pit_rescan.json")
