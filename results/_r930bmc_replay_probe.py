# -*- coding: utf-8 -*-
# r930 W222 prereg replay probe: build OLD21 (W221-face blocks) from the
# committed lineage chain (pairs216 + SUB17..SUB21), apply the two r927
# prose fixes (cf0b51d21 corrective steps replayed), preflight each block
# count==1 in the freeze-time W221 blob (98da27a40 face), then dump blocks
# + scan the blob complement for leftover W221-self tokens (47th-pair hunt).
import ast, json, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def blob(rev, path):
    b = subprocess.run(["git", "-C", REPO, "show", f"{rev}:{path}"],
                       capture_output=True).stdout
    assert b, f"blob fetch failed {rev}:{path}"
    return b.decode("utf-8")

t219 = blob("0dae35332", "research/PERPETUAL_N1_W219_PREREG.md")
t220 = blob("a9aee1d05", "research/PERPETUAL_N1_W220_PREREG.md")
t = blob("98da27a40", "research/PERPETUAL_N1_W221_PREREG.md")
assert "## §7" in t and "占位" in t, "not the freeze-time (pre-backfill) face"

def ram_face(txt):
    m = re.search(r"本窗 free RAM ~(\d+\.\d)GB", txt)
    assert m, "RAM note face not found"
    return "~" + m.group(1)

RAM_REPLAY_219 = ram_face(t219)
RAM_FACE_220 = ram_face(t220)
RAM_FACE_221 = ram_face(t)
print(f"RAM anchors: W219 {RAM_REPLAY_219!r} | W220 {RAM_FACE_220!r} | W221 {RAM_FACE_221!r}")

def resolve_node(node, vars):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.List):
        return [resolve_node(x, vars) for x in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(resolve_node(x, vars) for x in node.elts)
    if isinstance(node, ast.Dict):
        return {resolve_node(k, vars): resolve_node(v, vars) for k, v in zip(node.keys, node.values)}
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return resolve_node(node.left, vars) + resolve_node(node.right, vars)
    if isinstance(node, ast.Name) and node.id in vars:
        return vars[node.id]
    raise AssertionError(f"unresolvable AST node: {ast.dump(node)[:100]}")

def extract_lit(path, varname, expect, vars=None):
    vars = vars or {}
    src = open(path, encoding="utf-8").read()
    val = None
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == varname:
            try:
                cand = resolve_node(node.value, vars)
            except Exception:
                cand = None
            if cand:
                val = cand
                break
    assert val and len(val) == expect, f"{varname} extract failed: {len(val) if val else 0}"
    return val

pairs216 = extract_lit(r"results\_w216bmc_prereg_derive.py", "PAIRS", 46)
SUB17 = extract_lit(r"results\_w217bmc_prereg_derive.py", "SUB", 46)
SUB18 = extract_lit(r"results\_w218bmc_prereg_derive.py", "SUB", 46)
SUB19 = extract_lit(r"results\_w219bmc_prereg_derive.py", "SUB", 46,
                    vars={"RAM_GB": RAM_REPLAY_219})
SUB20 = extract_lit(r"results\_w220bmc_prereg_derive.py", "SUB", 46,
                    vars={"RAM_GB": RAM_FACE_220, "RAM_REPLAY": RAM_REPLAY_219})
SUB21 = extract_lit(r"results\_w221bmc_prereg_derive.py", "SUB", 46,
                    vars={"RAM_FACE_220": RAM_FACE_220, "RAM_GB": RAM_FACE_221})

OLD16 = [b.replace("@L14@", "214").replace("@T15@", "15") for _, b in pairs216]
def lvl(prev, SUB, mats):
    out = []
    for i, old in enumerate(prev):
        new = old
        for find, repl in SUB[i]:
            c = new.count(find)
            assert c == 1, f"replay count {c} != 1 idx{i}: {find[:60]}..."
            new = new.replace(find, repl, 1)
        for tok, num in mats:
            new = new.replace(tok, num)
        out.append(new)
    return out

OLD17 = lvl(OLD16, SUB17, [("@L14@", "214"), ("@L15@", "215"), ("@T16@", "16")])
OLD18 = lvl(OLD17, SUB18, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@T17@", "17")])
OLD19 = lvl(OLD18, SUB19, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@T18@", "18")])
OLD20 = lvl(OLD19, SUB20, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@T19@", "19")])

# W220 editor_gen same-window fix replay (r923 absorb freeze-window label;
# committed W220 face carries the corrected label, lineage must reproduce it)
_fixW_old = "【bm-c 循环班 r922 freeze 窗·2026-10-12 10:5x·"
_fixW_new = "【bm-c 循环班 r923 freeze 窗（absorb r922 freeze-prep estate）·2026-10-12 11:4x·"
assert OLD20[0].count(_fixW_old) == 1, "W220 editor_gen fix anchor missing"
OLD20[0] = OLD20[0].replace(_fixW_old, _fixW_new, 1)

OLD21 = lvl(OLD20, SUB21, [("@L14@", "214"), ("@L15@", "215"), ("@L16@", "216"), ("@L17@", "217"), ("@L18@", "218"), ("@L19@", "219"), ("@T15@", "15"), ("@T16@", "16"), ("@T17@", "17"), ("@T18@", "18"), ("@T19@", "20")])

# r927 corrective steps (committed face carries both; lineage must reproduce)
fixA_old = "账本头 907,589 机读·n1_w220_results.json·12:0x"
fixA_new = "账本头 907,789 机读·n1_w220_results.json·12:0x"
assert OLD21[3].count(fixA_old) == 1, "fixA anchor missing"
OLD21[3] = OLD21[3].replace(fixA_old, fixA_new, 1)
fixB_old = "W219 块的 W218 leg（1 行）不入 estate 路径·提取后新增 W218+W219 leg 构成 W221 块 parity 79 行"
fixB_new = "W220 块的 W219 leg（1 行）不入 estate 路径·提取后新增 W219+W220 leg 构成 W221 块 parity 79 行"
assert OLD21[30].count(fixB_old) == 1, "fixB anchor missing"
OLD21[30] = OLD21[30].replace(fixB_old, fixB_new, 1)

bad = 0
for i, old in enumerate(OLD21):
    c = t.count(old)
    if c != 1:
        bad += 1
        print(f"PREFLIGHT FAIL block[{i}] count={c}")
print(f"preflight: {46 - bad}/46 blocks count==1 in freeze-time W221 blob")

# complement scan: mask all blocks, look for leftover W221-self tokens
masked = t
for old in OLD21:
    masked = masked.replace(old, "\x00" * len(old), 1)
leftover_lines = []
for ln in masked.splitlines():
    if re.search(r"W221|n1_w221|PERPETUAL-N1-W221|501_004|503_004\.\.503_203|EIGHTY-FIRST|第八十一|第五十一|第 219 枚|1225-bmc|063bb5a77|r925 freeze", ln):
        leftover_lines.append(ln.strip())
print(f"--- leftover self-token lines (complement): {len(leftover_lines)} ---")
for ln in leftover_lines:
    print(">>", ln[:400])

with open(r"results\_r930bmc_old21_blocks.txt", "w", encoding="utf-8") as f:
    for i, old in enumerate(OLD21):
        f.write(f"===== BLOCK {i} ({len(old)} ch) =====\n{old}\n\n")
print("blocks dumped: results/_r930bmc_old21_blocks.txt")
print("blob bytes:", len(t.encode("utf-8")), "| sha16:", __import__("hashlib").sha256(t.encode("utf-8")).hexdigest()[:16])
