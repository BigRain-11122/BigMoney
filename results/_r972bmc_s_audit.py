# -*- coding: utf-8 -*-
# r972 absorb: audit phase-B S-table aging against the W232 prereg base blob.
# STALE faces are faces OF THE BASE (a3a7aa632) that the W233 pairs must
# eliminate -> every aged "new" value must appear in the base blob.
# Old blocks AST-extracted verbatim from committed _r967bmc_tplgen_b.py
# (same law as phase B itself -- zero transcription).
import ast, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def blob_bytes(rev, path):
    b = subprocess.run([r"C:\Program Files\Git\cmd\git.exe", "-C", REPO, "show", f"{rev}:{path}"],
                       capture_output=True).stdout
    assert b, f"blob fetch failed {rev}:{path}"
    return b

base = blob_bytes("a3a7aa632", "research/PERPETUAL_N1_W232_PREREG.md").decode("utf-8")
print("base blob bytes:", len(base.encode("utf-8")))

def extract_S(path):
    src = open(path, encoding="utf-8").read()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "S":
            return ast.literal_eval(node.value)
    raise AssertionError("S not found")

S = extract_S(r"results\_r972bmc_tplgen_b.py")
print("S pairs:", len(S))
missing = []
for old, new, n in S:
    c = base.count(new)
    flag = "OK " if c >= 1 else "MISS"
    if c < 1:
        missing.append((old, new))
    print(f"{flag} base_count={c} old={old[:46]!r} new={new[:46]!r}")
print("---")
print("MISSING FROM BASE:", len(missing))
for old, new in missing:
    print(f"  old={old!r} -> new={new!r}")
    # what the base actually holds for the same semantic slot
    probe = new.replace("508,320", "506,120").replace("0.0122", "0.0007").replace("e58dbcda3", "aee0bd9fa")
    print(f"    candidate correct face base_count={base.count(probe)}: {probe[:60]!r}")
