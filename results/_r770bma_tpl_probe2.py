# r770 bm-a probe 2: all delivery-window / sec8 / 153 contexts in template
import re

s = open("results/_r768bma_w155_freeze_edits.py", "rb").read().decode("utf-8")

print("=== all 'delivery window' contexts ===")
for m in re.finditer(r"delivery window", s):
    a, b = max(0, m.start() - 260), m.end() + 200
    print(repr(s[a:b]))
    print("---")

print("=== all 'sec8' contexts ===")
for m in re.finditer(r"sec8", s):
    a, b = max(0, m.start() - 120), m.end() + 90
    print(repr(s[a:b]))
    print("---")

print("=== all '153' contexts ===")
for m in re.finditer(r"153", s):
    a, b = max(0, m.start() - 60), m.end() + 60
    print(repr(s[a:b]))
    print("---")

print("=== 'behind-2' count:", s.count("behind-2"))
print("=== 'same-window self-ack' count:", s.count("same-window self-ack"))
print("=== 'move r768' count:", s.count("move r768"))
print("=== '1fedffbe4' count:", s.count("1fedffbe4"))
print("=== 'MSG-2026-10-06-0943' count:", s.count("MSG-2026-10-06-0943"))
print("=== 'W155 finalize' count:", s.count("W155 finalize"))
print("=== 'zero in-flight upstream' count:", s.count("in-flight upstream"))
print("=== 'r610' count:", s.count("r610"))
