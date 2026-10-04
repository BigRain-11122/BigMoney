# r500 bm-c CODELY.md hot/cold re-archival surgery (watermark law D-20260925-01).
# Scope (machine-unilateral; in-service laws stay hot per r504 note):
#   A. migrate 2 flow/receipt entries (L87 r447 D-06 closeout, L167 r479 O-1440 receipt)
#      verbatim -> research/memory-archive/202610.md new section; one combined cold-pointer
#      line stays in hot file (r444 pattern).
#   B. delete L155 stale duplicate of the D-20261002-06 git-domain pointer entry
#      (clause-containment proof, r479 substring-containment law).
#   C. remove duplicate header block (L103-L107 union artifact); collapse blank runs >=2 -> 1.
# Zero-loss proof: multiset(post non-blank) == multiset(pre) - deleted + added,
# plus exact byte identity and post-write read-back verification.
import hashlib, json, re
from collections import Counter

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CODELY = REPO + r"\CODELY.md"
ARCHIVE = REPO + r"\research\memory-archive\202610.md"
PRE_MD5 = "168523767c47e9c5b34c585573b8530d"  # census anchor (r641 drift gate)
SECTION = "热冷整编 2026-10-04 r500 bm-c 窗批（CODELY.md 水位律·流水/回执迁移+结构治愈）"

with open(CODELY, "rb") as f:
    raw = f.read()
assert hashlib.md5(raw).hexdigest() == PRE_MD5, "CODELY.md drifted since census"
text = raw.decode("utf-8")
lines = text.split("\r\n")
assert lines[-1] == "", "expected trailing CRLF newline"

def L(n):
    return lines[n - 1]

# --- anchors (content + position dual assertion) ---
a_r447 = L(87)
assert a_r447.startswith("- [2026-10-04 06:4x r447 bm-c] D-06 全线收口"), "L87 anchor"
a_r479 = L(167)
assert a_r479.startswith("- [2026-10-04 14:53:34 r479 bm-c] O-20261004-1440"), "L167 anchor"
a_dup = L(155)
assert a_dup.startswith("- 域指针·D-20261002-06 首拆件"), "L155 anchor"
a_canon = L(6)
assert a_canon.startswith("- 域指针·D-20261002-06 首拆件"), "L6 anchor"
hdr_texts = ["## Codely Structured Memories", "### User", "### Feedback",
             "### Project", "### Reference"]
for i, h in enumerate(hdr_texts):
    assert L(103 + i) == h, "L%d header anchor" % (103 + i)

# --- B. clause-containment proof: every L155 clause exists in L6 modulo trailing 。 ---
c6 = {c.rstrip("。") for c in a_canon.split("；")}
missing = [c for c in a_dup.split("；") if c.rstrip("。") not in c6]
assert not missing, "L155 has non-contained clauses: %r" % missing[:2]

# --- build new CODELY.md ---
pointer = ("- 冷层指针（r500 整编·r444 范式）：r447 bm-c D-06 全线收口记录（T-144 全票收口+CODELY mojibake"
           " 尾巴治愈处置·receipt=results/_r447bmc_d06_codely_heal.json）+r479 bm-c O-20261004-1440 "
           "闲置复发点火令执行回执——两条全文 verbatim=research/memory-archive/202610.md『%s』节。" % SECTION)

out = []
deleted = []   # exact line contents removed (zero-loss ledger)
blank_run = 0
for idx, ln in enumerate(lines[:-1], start=1):
    if idx == 87:
        deleted.append(ln)        # migrated to archive; pointer takes its place
        out.append(pointer)
        continue
    if idx in (155, 167):
        deleted.append(ln)
        continue
    if 103 <= idx <= 107:
        deleted.append(ln)
        continue
    if ln.strip() == "":
        blank_run += 1
        if blank_run >= 2:
            continue              # collapse run to first blank
        out.append(ln)
    else:
        blank_run = 0
        out.append(ln)

new_text = "\r\n".join(out) + "\r\n"

# --- zero-loss multiset proof ---
pre_c = Counter(x for x in lines[:-1] if x.strip() != "")
post_c = Counter(x for x in out if x.strip() != "")
del_c = Counter(deleted)
add_c = Counter([pointer])
assert not (del_c - pre_c), "deleted line not present in pre (drift!)"
assert post_c == pre_c - del_c + add_c, "multiset zero-loss FAIL"

# --- structural assertions ---
assert new_text.count("## Codely Structured Memories") == 1
for h in hdr_texts[1:]:
    assert new_text.count(h) == 1, "header dup remains: %s" % h
ENTRY = re.compile(r"^(?:- )?(?:\[(?:20\d\d)-[0-9]{2}-[0-9]{2}[^\]]*\]|域指针|冷层指针|坑律正典全量归档)")
entry_count = sum(1 for x in out if ENTRY.match(x))
assert entry_count == 117, "entry count %d != 117" % entry_count

# --- exact byte identity ---
def B(s):
    return len(s.encode("utf-8"))
blanks_pre = sum(1 for x in lines[:-1] if x.strip() == "")
blanks_post = sum(1 for x in out if x.strip() == "")
hdr_content_sum = sum(B(h) for h in hdr_texts)
expected_post = len(raw) - (B(a_r447) + B(a_dup) + B(a_r479) + hdr_content_sum) + B(pointer) \
               - 2 * (len(deleted) + (blanks_pre - blanks_post)) + 2  # +2: pointer line's own CRLF
assert len(new_text.encode("utf-8")) == expected_post, "byte identity FAIL"

# --- archive append (CRLF host, marker count 0->1, read-back verify) ---
with open(ARCHIVE, "rb") as f:
    arch_raw = f.read()
assert SECTION.encode("utf-8") not in arch_raw, "section marker already present"
assert arch_raw.endswith(b"\r\n")
arch_text = arch_raw.decode("utf-8")[:-2]
block = "\r\n\r\n## %s\r\n\r\n%s\r\n\r\n%s\r\n" % (SECTION, a_r447, a_r479)
new_arch = arch_text + block

with open(CODELY, "wb") as f:
    f.write(new_text.encode("utf-8"))
with open(ARCHIVE, "wb") as f:
    f.write(new_arch.encode("utf-8"))

# --- post-write read-back verification (evidence before claim) ---
with open(CODELY, "rb") as f:
    chk = f.read()
assert chk == new_text.encode("utf-8"), "CODELY readback mismatch"
with open(ARCHIVE, "rb") as f:
    achk = f.read()
achk_text = achk.decode("utf-8")
assert achk_text.count("## " + SECTION) == 1, "archive section marker count != 1"
assert a_r447 in achk_text, "archive missing r447 entry verbatim"
assert a_r479 in achk_text, "archive missing r479 entry verbatim"

receipt = {
    "law": "D-20260925-01 watermark >50KB -> hot/cold re-archival; r504 note: in-service laws stay hot",
    "pre": {"bytes": len(raw), "lines": len(lines) - 1, "md5": PRE_MD5},
    "post": {"bytes": len(new_text.encode("utf-8")), "lines": len(out),
             "md5": hashlib.md5(new_text.encode("utf-8")).hexdigest()},
    "migrated_to_archive": [
        {"head": a_r447[:56], "bytes": B(a_r447)},
        {"head": a_r479[:56], "bytes": B(a_r479)},
    ],
    "dup_entry_deleted": {"head": a_dup[:56], "bytes": B(a_dup),
                          "proof": "clause-containment modulo trailing 。 (r479 law), non-contained=%d" % len(missing)},
    "dup_header_block_removed_bytes": hdr_content_sum + 2 * len(hdr_texts),
    "blank_collapse": {"pre": blanks_pre, "post": blanks_post,
                       "bytes_removed": (blanks_pre - blanks_post) * 2},
    "pointer_line_bytes": B(pointer),
    "archive": {"pre_bytes": len(arch_raw), "post_bytes": len(achk),
                "delta": len(achk) - len(arch_raw),
                "md5": hashlib.md5(achk).hexdigest()},
    "entry_count_pre": 119, "entry_count_post": entry_count,
    "zero_loss": "multiset equality + byte identity + archive verbatim readback all proven",
    "residual_note": "residual hot layer = in-service pit-law canon (structural per r504); threshold re-anchor / legislation-merge window = GM ruling face",
}
with open(REPO + r"\results\_r500bmc_codely_rearch.json", "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("REARCH-OK post_bytes=%d post_lines=%d entries=%d arch_delta=%d" % (
    receipt["post"]["bytes"], len(out), entry_count, receipt["archive"]["delta"]))
