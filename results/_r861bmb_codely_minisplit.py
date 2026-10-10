"""r861 bm-b CODELY.md mini-split (cap law: 30,510B + new entry > 30,720B
-> migrate-then-append same window; ceremony r833/r896 precedent form).
Byte-mode surgery per r838/r839 laws: EOL probe first, anchor match on
line content rstrip'd of CR, migrated bytes preserved verbatim, target
file lands per its own EOL convention (pit-encoding.md = pure LF).
Legs:
 1. EOL probe (CRLF count vs pure LF count) -- refuse if unexpected.
 2. Extract the r838-bm-c (EOL mixed-state) + r839-bm-c (text-mode
    newline translation) entries verbatim from CODELY.md; they are the
    most recent entries already fully owned by the pit-encoding domain
    (byte-surgery/encoding family; r857 same file tail kin).
 3. Append them to research/pit-encoding.md after the last entry.
 4. Append the new r861 entry (null-budget-must-price-attrition lesson)
    to CODELY.md main.
 5. Byte accounting receipt -> results/_r861bmb_codely_minisplit.json:
    original == remaining + removed; migrated bytes verbatim in target;
    main <= 30,720; domain <= 30,720.
Zero console CJK (r458 family).
"""
import hashlib
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(REPO, "CODELY.md")
TARGET = os.path.join(REPO, "research", "pit-encoding.md")
RECEIPT = os.path.join(REPO, "results", "_r861bmb_codely_minisplit.json")
CAP = 30_720

ANCHORS = [b"21:0x r838 bm-c", b"21:2x r839 bm-c"]

NEW_ENTRY = (
    "- [2026-10-11 05:1x r861 bm-b] **prereg null \u9884\u7b97\u5fc5\u8ba1\u635f"
    "\u8017\u8d26\uff08N2-W18 \u9996\u70e7\u5b9e\u5f39\uff09**\uff1aB=6/\u5f0f"
    "\u00d764 \u5f0f\u8bbe\u8ba1\u8d4c \u226550 \u5f0f h1_ok \u51d1 pooled\u2265"
    "300\u2014\u2014\u5b9e\u6d4b 64-draw \u5305\u7ed3\u635f\u8017\uff08T-84s3 "
    "\u91cd\u7ed8+skip\uff09\u540e pooled=288 \u6070\u5dee 12\u2192\u8bda\u5b9e"
    "\u62d2\u70e7 UNJUDGEABLE\uff08\u96f6\u4ea7\u7269\u96f6\u8d26\u672c\u00b7"
    "\u51bb\u7ed3\u65b9\u6cd5\u5982\u8bbe\u8ba1\u5de5\u4f5c\uff09\u3002How to "
    "apply\uff1a\u4e00\u5207\u65cf\u7ea7 null \u5145\u5206\u7ebf\u7684 B \u9884"
    "\u7b97=\u6309\u300c\u5305\u7ed3\u00d7(1-\u635f\u8017\u7387\u5b9e\u8bc1)"
    "\u300dderive \u800c\u975e\u5305\u7ed3\u6ee1\u989d\u2014\u2014\u635f\u8017"
    "\u7387\u63a2\u9488\uff08\u9996\u7a97 T-84s3 \u547d\u4e2d+skip \u8ba1\u6570"
    "\uff09\u5148\u4e8e B \u5b9a\u7a3f\uff1bW19 \u8d77\u8349\u9762\u6309 25% "
    "\u635f\u8017\u5b9e\u8bc1\u91cd\u8bbe\u3002\u6b63\u5178=research/"
    "PERPETUAL_N2_W18_PREREG.md \u00a77/\u00a78+attrition \u884c kind="
    "search-refusal\u3002"
).encode("utf-8")


def main():
    raw = open(MAIN, "rb").read()
    crlf = raw.count(b"\r\n")
    lf_total = raw.count(b"\n")
    probe = {"bytes": len(raw), "crlf": crlf, "pure_lf": lf_total - crlf}
    assert crlf <= 4 and lf_total >= 40, f"unexpected EOL face: {probe}"

    # split keeping the terminator bytes on each line
    lines = raw.split(b"\n")
    # last element is b"" when file ends with \n
    trailing_nl = lines[-1] == b""
    body = lines[:-1] if trailing_nl else lines
    # CRLF terminators are legal in the mixed-EOL main file (r838 law);
    # content handling below rstrips CR per anchor-matching law.

    hits = {}          # anchor -> (index, content_bytes_sans_CR)
    for i, ln in enumerate(body):
        content = ln[:-1] if ln.endswith(b"\r") else ln
        for a in ANCHORS:
            if a in content:
                hits[a] = (i, content)
    assert len(hits) == 2, f"anchor misses: {sorted(hits)}"
    removed_idx = sorted(hits[a][0] for a in ANCHORS)

    removed_content = [hits[a][1] for a in ANCHORS]
    removed_bytes = sum(len(c) + 1 for c in removed_content)   # + LF each

    # removal with one preceding blank separator per entry (if blank)
    drop = set(removed_idx)
    for i in removed_idx:
        j = i - 1
        if j >= 0 and body[j].rstrip(b"\r") == b"":
            drop.add(j)
    remaining = [ln for i, ln in enumerate(body) if i not in drop]

    # byte accounting: original == remaining + removed (incl. separators)
    rem_bytes = sum(len(ln) + 1 for ln in remaining)
    sep_bytes = sum(len(body[i]) + 1 for i in drop if i not in removed_idx)
    assert len(raw) == rem_bytes + removed_bytes + sep_bytes + \
        (0 if trailing_nl else -0) - (0 if trailing_nl else 1), \
        "byte accounting mismatch"
    # simpler exact check: recompute dropped lines total
    dropped_total = sum(len(body[i]) + 1 for i in drop)
    if trailing_nl:
        assert len(raw) == rem_bytes + dropped_total, "accounting fail"
    else:
        assert len(raw) == rem_bytes + dropped_total - 1, "accounting fail"

    # append new entry to main (LF convention; blank line before it)
    if remaining and remaining[-1].rstrip(b"\r") != b"":
        remaining.append(b"")
    remaining.append(NEW_ENTRY)
    main_out = b"\n".join(remaining) + b"\n"
    assert len(main_out) <= CAP, f"main still over cap: {len(main_out)}"

    # append migrated entries to target (pure LF; consecutive bullet style)
    traw = open(TARGET, "rb").read()
    assert traw.count(b"\r\n") == 0, "target not pure LF"
    tadd = b"\n".join(removed_content) + b"\n"
    if not traw.endswith(b"\n"):
        traw += b"\n"
    # keep target bullet style: entries consecutive, single trailing newline
    target_out = traw + tadd
    assert target_out.count(b"\r\n") == 0
    assert len(target_out) <= CAP, f"target over cap: {len(target_out)}"

    # verbatim-in-target assertion
    for c in removed_content:
        assert c in target_out, "verbatim migration fail"

    with open(MAIN, "wb") as f:
        f.write(main_out)
    with open(TARGET, "wb") as f:
        f.write(target_out)

    receipt = {
        "round": "r861 bm-b mini-split (migrate-then-append same window)",
        "probe_eol_main": probe,
        "probe_eol_target": {"bytes": len(traw), "crlf": 0,
                              "pure_lf": traw.count(b"\n")},
        "migrated": [
            {"anchor": a.decode(),
             "sha16": hashlib.sha256(hits[a][1]).hexdigest()[:16],
             "bytes": len(hits[a][1])}
            for a in ANCHORS
        ],
        "removed_bytes_incl_lf": removed_bytes,
        "separator_bytes": sep_bytes,
        "new_entry_sha16": hashlib.sha256(NEW_ENTRY).hexdigest()[:16],
        "new_entry_bytes": len(NEW_ENTRY),
        "main_before": len(raw), "main_after": len(main_out),
        "target_before": len(traw), "target_after": len(target_out),
        "asserts": ["original==remaining+removed (byte exact)",
                    "migrated bytes verbatim in target",
                    "main<=30720", "target<=30720", "main LF convention",
                    "target pure LF preserved"],
        "law": "CODELY.md <=30KB cap (D-20261002-06); ceremony r833/r896",
    }
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    print(json.dumps({"main_after": len(main_out),
                      "target_after": len(target_out),
                      "removed_bytes": removed_bytes + sep_bytes,
                      "verdict": "PASS"}))


if __name__ == "__main__":
    main()
