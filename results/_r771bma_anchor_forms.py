# -*- coding: utf-8 -*-
"""r771 bm-a probe: exact SOURCE-byte forms of the W155 template anchors
(quote-continuation breaks included) so the generator needles can be
rewritten to match template source text."""
import io

s = io.open(r"results/_r768bma_w155_freeze_edits.py", "r", encoding="utf-8", newline="").read()


def span(tag, start_needle, end_needle, tail=0):
    i = s.find(start_needle)
    if i < 0:
        print(f"=== {tag}: START NOT FOUND: {start_needle[:50]!r}")
        return
    j = s.find(end_needle, i)
    print(f"=== {tag}: @{i}..{j + tail}")
    print(repr(s[i:j + tail]))
    print()


span("a1-def", "a1 = (", "')\n", 3)
span("a2-def", "a2 = (", "'}')", 5)
span("a3-def", "a3 = '", "'\n", 1)
span("a4-def", "a4 = (", "')\n", 3)
print("--- parity start line ---")
i = s.find("registered row parity")
print(repr(s[i - 60:i + 120]))
print("--- parity end line ---")
j = s.find("W154 row parity drift")
print(repr(s[j - 120:j + 80]))
