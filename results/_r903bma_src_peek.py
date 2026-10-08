# -*- coding: utf-8 -*-
import io
s = io.open(r"results/_r903bma_w194_prereg_src.txt", encoding="utf-8").read()
i = s.find("W192=bm-c r787 freeze\uff08f8703842c\uff09")
tail = s[i:i+30]
print("tail_codepoints:", [hex(ord(c)) for c in tail])
print("tail_names:", " ".join(c if ord(c) < 128 else "U+%04X" % ord(c) for c in tail))
lines = s.split("\n")
print("line2_len:", len(lines[2]))
print("line2_tail_codepoints:", [hex(ord(c)) for c in lines[2][-12:]])
# also line 4 (带位) and line 43 (§5 anch) structure checks
print("line4_head:", ascii(lines[4][:40]))
print("line43_head:", ascii(lines[43][:40]))
