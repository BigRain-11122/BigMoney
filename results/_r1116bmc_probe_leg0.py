# r1116 bm-c: leg0-face disappearance probe (SIM MUST count=0 diagnosis, one-shot).
# Execs the builder's entire pre-sim section (deterministic) and inspects the generated-script
# text: the leg0 VMAP entry, the leg0 MUST entry, then manually runs VMAP/POST_LEGS on T0 to
# find where the 96-face dies.
import io, re
B = io.open("results/_r1116bmc_build_w278_derive.py", encoding="utf-8", newline="").read()
cut = B.index("# ---------------- FULL PRE-FLIGHT SIMULATION")
ns = {"__name__": "probe_not_main", "__file__": io.open("results/_r1116bmc_build_w278_derive.py", encoding="utf-8").name and r"K:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r1116bmc_build_w278_derive.py"}
exec(compile(B[:cut], "builder_prefix", "exec"), ns)
txt = ns["txt"]
print("=== VMAP leg0 entry in generated script ===")
for m in re.finditer(r'\("probe leg0[^"]*",\s*"probe leg0[^"]*"\),', txt):
    print(m.group(0)[:400])
print()
print("=== MUST leg0 entry in generated script ===")
for m in re.finditer(r'"probe leg0[^"]*"', txt):
    print(m.group(0)[:250])
print()
T0 = ns["T0"]
print("=== T0 leg0 face ===")
i = T0.index("probe leg0")
print(T0[i:i + 180])
print()
# manually apply the VMAP to T0
VMAP = None
seg_start = txt.index("VMAP = [")
seg_end = txt.index("VMAP_FLOORS = {", seg_start)
ns2 = {"P1": "\x01W\x01", "P2": "\x01N\x01", "P3": "\x01B\x01"}
exec(txt[seg_start:seg_end], ns2)
T1 = T0
for o, n in ns2["VMAP"]:
    if "probe leg0" in o:
        print("VMAP leg0 o-side hits on T0:", T0.count(o))
    T1 = T1.replace(o, n)
print()
print("=== T1 leg0 face (post-VMAP) ===")
i = T1.find("probe leg0")
print(T1[i:i + 200] if i >= 0 else "GONE")
