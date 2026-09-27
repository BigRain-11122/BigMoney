# -*- coding: utf-8 -*-
"""r327 bm-a resolver-v2 probe -- CODELY.md three-stage shape (archival
adjudication) + UU batch face summary."""
import subprocess, sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def sh(*a): return subprocess.run(list(a), capture_output=True, cwd=REPO).stdout

p = "CODELY.md"
b1, b2, b3 = sh("git","show",":1:"+p), sh("git","show",":2:"+p), sh("git","show",":3:"+p)
def strip(b): return b.rstrip(b"\r\n")
s1, s2, s3 = strip(b1), strip(b2), strip(b3)
print("sizes: base=%d origin=%d mine=%d" % (len(s1), len(s2), len(s3)))
print("origin startswith base:", s2.startswith(s1))
print("mine startswith base:", s3.startswith(s1))
# what suffix does each side carry vs base
if s3.startswith(s1):
    suf3 = s3[len(s1):]
    print("--- MINE suffix (%dB) head 600:" % len(suf3))
    print(repr(suf3[:600]))
if s2.startswith(s1):
    suf2 = s2[len(s1):]
    print("--- ORIGIN suffix (%dB):" % len(suf2))
    print(repr(suf2[:400]))
else:
    # archival case: find base tail in origin
    print("--- origin NOT base+suffix (archival). base tail 300:")
    print(repr(s1[-300:]))
    print("--- origin head 600:")
    print(repr(s2[:600]))
    print("--- origin tail 500:")
    print(repr(s2[-500:]))
# does origin still contain my r326 asi8 entry and r83 entry?
for probe in (b"asi8", b"r326 bm-a", b"r83 bm-c", b"union", b"DatetimeIndex"):
    print("origin contains %r:" % probe, probe in s2)
    print("mine   contains %r:" % probe, probe in s3)

print("=" * 70)
uu = sh("git","diff","--name-only","--diff-filter=U").decode().splitlines()
print("UU list:", json.dumps(uu, indent=0))
# quick face: for json UUs show stage2/3 generated/ts-ish keys
import re
for f in uu:
    if f.endswith(".json"):
        try:
            d2 = json.loads(sh("git","show",":2:"+f).decode("utf-8"))
            d3 = json.loads(sh("git","show",":3:"+f).decode("utf-8"))
        except Exception as e:
            print(f, "parse fail:", e); continue
        def deep_ts(d):
            best = ""
            st = [d]
            while st:
                x = st.pop()
                if isinstance(x, dict): st.extend(x.values())
                elif isinstance(x, list): st.extend(x)
                elif isinstance(x, str):
                    m = re.search(r"2026-09-2[67][ T]\d{2}:\d{2}(:\d{2})?", x)
                    if m and m.group(0) > best: best = m.group(0)
            return best
        k2 = {k: (str(v)[:40]) for k, v in list(d2.items())[:8]} if isinstance(d2, dict) else type(d2).__name__
        k3 = {k: (str(v)[:40]) for k, v in list(d3.items())[:8]} if isinstance(d3, dict) else type(d3).__name__
        print("---", f)
        print("  S2 deep_ts=%s keys=%s" % (deep_ts(d2), k2))
        print("  S3 deep_ts=%s keys=%s" % (deep_ts(d3), k3))
