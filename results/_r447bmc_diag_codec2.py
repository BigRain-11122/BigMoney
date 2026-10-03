# -*- coding: utf-8 -*-
"""r447 bm-c codec diagnostic v2: first failure point of the win-cp936
reverse map per mojibake line."""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "CODELY.md")
OUT = os.path.join(ROOT, "results", "_r447bmc_diag_codec2.txt")

Z3_TRAILS = [x for x in range(0x40, 0xA1) if x != 0x7F]

def win_cp936_bytes(text):
    out = bytearray()
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
                raise RuntimeError("ENCFAIL char %d U+%04X ctx=%r" % (
                    idx, cp, text[max(0, idx-12):idx+12]))
    return bytes(out)

raw = open(SRC, "rb").read()
texts = [b.decode("utf-8", "replace") for b in raw.split(b"\r\n")]
buf = []
# candidate mojibake lines by euro-or-PUA signature
sig = re.compile(r"[\u20ac\ue000-\ue817]")
cands = [i for i, t in enumerate(texts) if sig.search(t)]
buf.append("signature candidates (1-based): %s" % [i + 1 for i in cands])
for i in cands:
    t = texts[i]
    try:
        b = win_cp936_bytes(t)
    except RuntimeError as e:
        buf.append("L%d ENCODE-FAIL %s" % (i + 1, str(e)[:160]))
        continue
    try:
        rec = b.decode("utf-8")
        buf.append("L%d ROUNDTRIP-OK len=%d rec_head=%r" % (i + 1, len(rec), rec[:40]))
    except UnicodeDecodeError as e:
        p = e.start
        ctx = b[max(0, p-8):p+8]
        buf.append("L%d DECODE-FAIL at byte %d reason=%s ctx=%s hex=%s" % (
            i + 1, p, str(e)[:60], ctx, " ".join("%02x" % c for c in ctx)))
with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(buf))
print("DIAG2-WRITTEN rows=%d" % len(buf))
