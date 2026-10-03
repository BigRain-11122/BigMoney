# -*- coding: utf-8 -*-
"""r447 bm-c codec diagnostic v3: per-line anatomy of the mojibake span."""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "CODELY.md")
OUT = os.path.join(ROOT, "results", "_r447bmc_diag_codec3.txt")

Z3_TRAILS = [x for x in range(0x40, 0xA1) if x != 0x7F]

def win_cp936_bytes(text):
    out = bytearray()
    fails = []
    for idx, ch in enumerate(text):
        cp = ord(ch)
        if cp == 0x20AC:
            out.append(0x80)
        elif 0xE000 <= cp <= 0xE233:
            off = cp - 0xE000
            out += bytes([0xAA + off // 94, 0xA1 + off % 94])
        elif 0xE234 <= cp <= 0xE4C5:
            off = cp - 0xE234
            out += bytes([0xF8 + off // 94, 0xA1 + off % 94])
        elif 0xE4C6 <= cp <= 0xE759:
            off = cp - 0xE4C6
            out += bytes([0xA1 + off // 96, Z3_TRAILS[off % 96]])
        elif 0xE75A <= cp <= 0xE817:
            off = cp - 0xE75A
            out += bytes([0xA8 + off // 96, Z3_TRAILS[off % 96]])
        else:
            try:
                out += ch.encode("cp936")
            except UnicodeEncodeError:
                fails.append((idx, "U+%04X" % cp, text[max(0, idx-6):idx+6]))
    return bytes(out), fails

raw = open(SRC, "rb").read()
texts = [b.decode("utf-8", "replace") for b in raw.split(b"\r\n")]
buf = []
for i in range(60, min(len(texts), 96)):
    t = texts[i]
    b, fails = win_cp936_bytes(t)
    rec = b.decode("utf-8", errors="replace")
    fffd = rec.count("\ufffd")
    cjk = len(re.findall(r"[\u4e00-\u9fff]", rec)) / max(1, len(rec))
    qmark = t.count("?")
    euro = t.count("\u20ac")
    pua = len(re.findall(r"[\ue000-\ue817]", t))
    changed = rec != t
    buf.append("L%03d len=%5d qmark=%3d euro=%2d pua=%3d encfail=%d fffd=%3d(%.3f) cjk=%.3f changed=%s %s" % (
        i + 1, len(t), qmark, euro, pua, len(fails), fffd, fffd / max(1, len(rec)), cjk, changed,
        (repr(fails[0][1]) + " " + repr(fails[0][2])[:40]) if fails else ""))
    if fails:
        buf.append("      fail-chars: %s" % fails[:6])
with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(buf))
print("DIAG3-WRITTEN rows=%d" % len(buf))
