# r1116 bm-c: seat-window face probe (SIM MUST count=0 diagnosis #2, one-shot).
import io, re
B = io.open("results/_r1116bmc_build_w278_derive.py", encoding="utf-8", newline="").read()
cut = B.index("# ---------------- FULL PRE-FLIGHT SIMULATION")
ns = {"__name__": "probe_not_main", "__file__": r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r1116bmc_build_w278_derive.py"}
exec(compile(B[:cut], "builder_prefix", "exec"), ns)
txt = ns["txt"]
print("=== generated-script faces containing 席位窗实跑 ===")
for m in re.finditer(r'.{0,10}席位窗实跑[^"]*"', txt):
    print(repr(m.group(0)[:200]))
print()
T0 = ns["T0"]
print("=== T0 faces containing 席位窗实跑 ===")
for m in re.finditer(r'.{0,20}席位窗实跑.{0,60}', T0):
    print(repr(m.group(0)))
print()
seg_start = txt.index("VMAP = [")
seg_end = txt.index("VMAP_FLOORS = {", seg_start)
ns2 = {"P1": "\x01W\x01", "P2": "\x01N\x01", "P3": "\x01B\x01"}
exec(txt[seg_start:seg_end], ns2)
T1 = T0
for o, n in ns2["VMAP"]:
    if "席位窗实跑" in o:
        print("VMAP seat-entry:", repr(o[:80]), "->", repr(n[:80]), "| T0 hits:", T0.count(o))
    T1 = T1.replace(o, n)
i = T1.find("席位窗实跑")
print()
print("=== T1 seat face (post-VMAP) ===")
print(repr(T1[max(0, i - 30):i + 80]) if i >= 0 else "GONE")
