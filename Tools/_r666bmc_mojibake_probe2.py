# -*- coding: utf-8 -*-
"""r666 bm-c CODELY.md byte-level forensics on suspect lines (read-only)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, "CODELY.md")

def main():
    with open(MAIN, "rb") as fh:
        data = fh.read()
    lines = data.split(b"\n")
    for i, ln in enumerate(lines, 1):
        # suspect lines: contain b'r662 bm-c' or b'r665 bm-c' AND non-ascii high bytes
        if (b"r662 bm-c" in ln or b"r665 bm-c" in ln):
            has_high = any(b >= 0x80 for b in ln)
            print("LINE %d len=%d has_high=%s" % (i, len(ln), has_high))
            print("  head_hex=" + ln[:48].hex())
            # show as utf-8 with repr of first 120 chars
            txt = ln.decode("utf-8", errors="replace")
            print("  REPR=" + repr(txt[:120]))
            # try latin1 roundtrip
            try:
                t2 = ln.decode("latin-1")
                rec = t2.encode("latin-1").decode("utf-8")
                print("  LATIN1_ROUNDTRIP_RECOVERED=" + repr(rec[:80]))
                print("  RECOVERED_FULL=" + rec)
            except Exception as e:
                print("  LATIN1_ROUNDTRIP_FAIL=" + repr(e))
    # global scan: lines with U+0080-U+009F C1 controls after utf-8 decode
    text = data.decode("utf-8", errors="replace")
    c1_lines = [i for i, ln in enumerate(text.split("\n"), 1)
                if any(0x80 <= ord(ch) <= 0x9F for ch in ln)]
    print("C1_CONTROL_LINES=" + repr(c1_lines[:20]))
    return 0

if __name__ == "__main__":
    sys.exit(main())
