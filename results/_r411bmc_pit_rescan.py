# -*- coding: utf-8 -*-
# r411 bm-c: incremental domain rescan (T-2026-10-02-144(c) D-06 line) + L56 bullet repair.
# 2 hot-layer CODELY entries -> pit-pool(1: r619 parked-lane adjudication chain) /
# pit-protocol(1: r410 fusion form = r401 block-law variant 4), verbatim, r399/r401/r402/r410 paradigm.
# NEW VARIANT DISCOVERED: L56 r607 entry written with bare "[date" (no "- " bullet, no space) --
# defeats the "- [" line-start filter AND the "- [" substring fallback leg (r410 law);
# only the startswith(sig) branch of rescan tools catches it ->
# silent never-migrates under pure "- [" scanners. Repair = 2-byte prepend. Canonized in protocol increment row.
import hashlib, json, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CODELY = ROOT + r"\CODELY.md"
PIT = {
    "pool": ROOT + r"\research\pit-pool.md",
    "protocol": ROOT + r"\research\pit-protocol.md",
}

# (domain, signature, keyword_guard) -- line-start entries
TARGETS = [
    ("pool",     "[2026-10-03 10:3x r619 bm-a]", "停泊泳道"),
    ("protocol", "[2026-10-03 10:4x r410 bm-c]", "融合形态坑"),
]
BULLET_SIG = "[2026-10-03 07:3x r607 bm-b]"   # bullet-less line-start form (variant 5)

ROW_NOTE = {
    "pool": "；r411 bm-c 增量回扫 1 条（10-03 10:3x r619 停泊泳道裁定链扫描律）已入件（件内对账行为准）。",
    "protocol": ("；r411 bm-c 增量回扫 1 条（10-03 10:4x r410 融合形态律·块界变体④）已入件；"
                 "另修 L56 r607 行 bullet 缺失形（变体⑤·行首裸 date 无连字符——行首过滤与 substring 兜底双漏·2 字节修复）"
                 "（件内对账行为准）。"),
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

removed = []
remove_idx = []
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
    if len(line.encode("utf-8")) < 200:
        print("ABORT suspiciously short entry %s" % sig)
        sys.exit(2)
    removed.append((dom, sig, line))
    remove_idx.append(i)
    print("FOUND %s -> %s (line %d, %dB)" % (sig, dom, i + 1, len(line.encode("utf-8"))))

if len(remove_idx) != len(set(remove_idx)):
    print("ABORT duplicate line removal")
    sys.exit(2)
if len(removed) != 2:
    print("ABORT expected 2 extracted entries, got %d" % len(removed))
    sys.exit(2)

# L56 bullet repair target (bare date-start line, no "- " prefix)
bcands = [i for i, ln in enumerate(lines_c) if ln.startswith(BULLET_SIG)]
if len(bcands) != 1:
    print("ABORT bullet-less r607 cands=%d %s" % (len(bcands), bcands))
    sys.exit(2)
bi = bcands[0]
bl = lines_c[bi]
if len(bl.encode("utf-8")) < 200 or "GBK" not in bl:
    print("ABORT r607 line guard failed")
    sys.exit(2)
# rule out fusion: previous line must end complete (。 or empty), no stranded "-"
prev = lines_c[bi - 1] if bi > 0 else ""
if prev.strip() != "" and not prev.endswith("。"):
    print("ABORT prev line before r607 does not end complete: %r" % prev[-30:])
    sys.exit(2)
print("BULLET-REPAIR line %d: '%s...' -> '- %s...' (2B, bare-date variant 5)" % (bi + 1, BULLET_SIG[:20], BULLET_SIG[:20]))

# pointer-row anchors: exactly one 域指针 row per target pit file
for dom in ("pool", "protocol"):
    rows = [i for i, ln in enumerate(lines_c)
            if ("research/pit-%s.md" % dom) in ln and "域指针" in ln and "D-20261002-06" in ln]
    if len(rows) != 1:
        print("ABORT ptr rows for %s: %s" % (dom, rows))
        sys.exit(2)
    if not lines_c[rows[0]].endswith("。"):
        print("ABORT ptr row %s does not end with 。" % dom)
        sys.exit(2)
    print("PTR %s row %d edit planned" % (dom, rows[0] + 1))

# survivor assertions pre-check
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
    print("PIT %s bom=%s nl=%r bytes=%d last_scan_row=%d" % (dom, bom_p, nl_p, len(raw_p), hdr[-1] + 1))

# ---------- phase B: transform in memory ----------
entries_by_dom = {"pool": [], "protocol": []}
for dom, sig, line in removed:
    entries_by_dom[dom].append(line)
for i in sorted(set(remove_idx), reverse=True):
    del lines_c[i]
# bullet repair (re-locate by anchor post-deletion)
bcands = [i for i, ln in enumerate(lines_c) if ln.startswith(BULLET_SIG)]
if len(bcands) != 1:
    print("ABORT bullet re-locate %s" % bcands)
    sys.exit(2)
lines_c[bcands[0]] = "- " + lines_c[bcands[0]]
# pointer-row edits (re-located post-deletion)
for dom in ("pool", "protocol"):
    rows = [i for i, ln in enumerate(lines_c)
            if ("research/pit-%s.md" % dom) in ln and "域指针" in ln and "D-20261002-06" in ln]
    if len(rows) != 1:
        print("ABORT ptr re-locate %s: %s" % (dom, rows))
        sys.exit(2)
    lines_c[rows[0]] = lines_c[rows[0]][:-1] + ROW_NOTE[dom]
text_c_new = nl_c.join(lines_c)

# zero-residue assertions
for dom, sig, kw in TARGETS:
    if any((sig in ln) and (kw in ln) for ln in lines_c):
        print("ABORT residue %s" % sig)
        sys.exit(2)
# r607 line now bullet'd, present exactly once
twin = [ln for ln in lines_c if ln.startswith("- " + BULLET_SIG)]
if len(twin) != 1:
    print("ABORT r607 repaired line count=%d" % len(twin))
    sys.exit(2)
print("RESIDUE-OK r607_bullet_fixed=1")

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
report = {"round": "r411 bm-c", "ticket": "T-2026-10-02-144(c)",
          "bullet_repair": {"line": bi + 1, "sig": BULLET_SIG, "bytes_added": 2},
          "domains": {}}
for dom, path in PIT.items():
    raw_p, text_p, bom_p, nl_p, lines_p, h_last = pit_state[dom]
    ents = entries_by_dom[dom]
    block_lf = "\n" + "\n\n".join(ents) + "\n"
    block_lf_b = block_lf.encode("utf-8")
    md5 = hashlib.md5(block_lf_b).hexdigest()
    sig_list = "、".join(s for d, s, _ in TARGETS if d == dom)
    dom_label = {"pool": "池", "protocol": "协议"}[dom]
    row_full = ("> 增量回扫行（r411 bm-c·T-2026-10-02-144(c)）：热层%s域条目 %d 条 verbatim 追加"
                "（10-03 批：%s）·追加核 %d B（LF blob 面·md5=%s）·零丢失断言 PASS"
                "（逐行 verbatim 在场+源件零残留·机械迁移非手抄·r399 范式同源；整行迁移）") % (
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
        "entries": [s for d, s, _ in TARGETS if d == dom],
        "block_lf_bytes": len(block_lf_b),
        "block_lf_md5": md5,
        "pit_bytes_before": len(raw_p),
        "pit_bytes_after": len(text_p_new.encode("utf-8")) + (3 if bom_p else 0),
        "expected_numstat_adds": len(ents) * 2 + 1,
    }
    pit_state[dom] = (raw_p, text_p_new, bom_p, nl_p, None, h_last)

removed_bytes = sum(len((e + nl_c).encode("utf-8")) for _, _, e in removed)
ptr_note_bytes = sum(len(ROW_NOTE[d].encode("utf-8")) for d in ("pool", "protocol"))
codely_new_bytes = len(text_c_new.encode("utf-8")) + (3 if bom_c else 0)
report["codely"] = {
    "bytes_before": len(raw_c), "bytes_after": codely_new_bytes,
    "removed_entries_bytes_wt": removed_bytes,
    "removed_count": 2,
    "bullet_repair_bytes": 2,
    "ptr_rows_edited": 2,
    "ptr_note_bytes_wt": ptr_note_bytes,
    "expected_numstat": "3 5",
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
if sum(1 for ln in rb_lines if ln.startswith("- " + BULLET_SIG)) != 1:
    print("READBACK-FAIL r607 bullet")
    ok = False
for dom, path in PIT.items():
    _, rb_p, _, _ = read_text(path)
    for d2, s2, _k in TARGETS:
        if d2 == dom:
            src = [e for dd, ss, e in removed if dd == dom and ss == s2]
            if len(src) != 1 or rb_p.count(src[0]) != 1:
                print("READBACK-FAIL verbatim %s in %s" % (s2, dom))
                ok = False
if not ok:
    sys.exit(2)

with open(ROOT + r"\results\_r411bmc_pit_rescan.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print("ALL-WRITTEN codely %d->%d (entries out %dB, bullet +2B, ptr notes +%dB) pits=pool1/protocol1" %
      (len(raw_c), codely_new_bytes, removed_bytes, ptr_note_bytes))
print("EVIDENCE results/_r411bmc_pit_rescan.json")
