"""r691 bm-a: per-leg key lines from S6 log (dual-decode, ASCII-safe, UTF-8 out)."""
import re, io, sys

sys.stdout = io.TextIOWrapper(open("results/_r691bma_s6_facts.txt", "wb", buffering=0),
                             encoding="utf-8", errors="replace")
b = open("results/_r691bma_s6_log.txt", "rb").read()
t8 = b.decode("utf-8", "replace")
t16 = b.decode("utf-16-le", "replace")
for name, t in (("u16", t16), ("u8", t8)):
    for m in re.finditer(r"=== LEG (\w+) start[\s\S]{0,900}?=== LEG \1 rc=", t):
        leg, seg = m.group(1), m.group(0)
        for pat in ["consecutive_green", "verdict", "flags", "CALL", "streak",
                    "drift", "DRIFT", "token", "L2", "red=", "next_pick"]:
            for mm in re.finditer(r"^[^\r\n]*" + pat + r"[^\r\n]*$", seg, re.M):
                s = mm.group(0).strip()
                if s and len(s) < 180 and s.count("\ufffd") < 3:
                    print(f"{name} {leg} | {s}")
