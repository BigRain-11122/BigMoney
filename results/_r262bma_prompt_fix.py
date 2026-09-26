# _r262bma_prompt_fix.py -- R262: pin the clock_read ISO spec in the standing
# iteration prompt so the S7 heartbeat writer cannot reproduce smoke F7 red.
# R261 root cause: spec said "ISO 含 UTC 偏移" without pinning the separator;
# writer used a space ("2026-09-26 17:53:59+08:00") and smoke F7 checks `"T" in
# clock_read`. Binary read/replace/write preserves BOM/EOL byte faces (R255 law).
import sys

P = "Tools/iteration_prompt.txt"
raw = open(P, "rb").read()
bom = raw.startswith(b"\xef\xbb\xbf")
t = raw.decode("utf-8-sig")
old = "clock_read（本机钟 ISO 含 UTC 偏移，T-04 F5 钟漂探测字段）"
new = ("clock_read（本机钟 ISO 8601 含 UTC 偏移、必须 T 分隔——"
       "如 2026-09-26T17:59:32+08:00，空格分隔＝smoke F7 红项·R262 实证；"
       "T-04 F5 钟漂探测字段）")
n = t.count(old)
if n != 1:
    print(f"FAIL: expect 1 occurrence, got {n}")
    sys.exit(1)
t2 = t.replace(old, new)
data = t2.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
with open(P, "wb") as fh:
    fh.write(data)
chk = open(P, "rb").read().decode("utf-8-sig")
assert new in chk and old not in chk
print(f"replaced OK; bom={bom}; len_delta={len(t2) - len(t)}")
