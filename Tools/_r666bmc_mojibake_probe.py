# -*- coding: utf-8 -*-
"""r666 bm-c CODELY.md mojibake-heal probe (r407 fact-reconstruct + r447 inverse-map laws).

Scans main CODELY.md for cp1252-double-encoded mojibake lines, recovers the
proper text via encode('cp1252').decode('utf-8'), cross-checks against the
verbatim pit entries in research/pit-ps.md (r447 law-2 containment), and
reports a proposed heal diff. Read-only probe: no writes here.
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")
PIT = os.path.join(ROOT, "research", "pit-ps.md")

def is_mojibake(line):
    """Signature: line re-encodes to cp1252 cleanly AND decodes back as UTF-8
    with CJK content = cp1252 double-encoding (r662/r665 pointer family)."""
    try:
        raw = line.encode("cp1252")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None
    try:
        rec = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if any("\u4e00" <= ch <= "\u9fff" for ch in rec):
        return rec
    return None

def main():
    with open(MAIN, "rb") as fh:
        data = fh.read()
    print("MAIN_BYTES=%d" % len(data))
    text = data.decode("utf-8", errors="replace")
    lines = text.split("\n")
    hits = []
    for i, ln in enumerate(lines, 1):
        # skip obviously clean lines fast
        if "Ã" not in ln and "Â" not in ln and "ï¼" not in ln and "åæ" not in ln:
            continue
        rec = is_mojibake(ln)
        if rec is not None:
            hits.append((i, ln, rec))
    print("MOJIBAKE_HITS=%d" % len(hits))
    for i, ln, rec in hits:
        print("---- line %d ----" % i)
        print("MOJIBAKE_LEN_CHARS=%d" % len(ln))
        print("RECOVERED_LEN_CHARS=%d" % len(rec))
        print("RECOVERED|%s" % rec)
        # containment cross-check: net >=12-char CJK grams present in pit-ps entry
        with open(PIT, "rb") as fh:
            pit_text = fh.read().decode("utf-8", errors="replace")
        grams = [rec[j:j+12] for j in range(0, max(0, len(rec)-12), 6)]
        found = sum(1 for g in grams if g in pit_text)
        print("CONTAINMENT_GRAMS=%d/%d" % (found, len(grams)))
    # proposed byte math
    before = len(data)
    after = len(data)
    for i, ln, rec in hits:
        after -= len(ln.encode("utf-8")) - len(rec.encode("utf-8"))
    print("HEAL_BYTE_MATH before=%d after=%d delta=%d" % (before, after, after-before))
    return 0

if __name__ == "__main__":
    sys.exit(main())
