# -*- coding: utf-8 -*-
# W221 prereg derive PREP: five-level lineage replay + preflight + block dump
# (bm-c r925, 2026-10-12 12:5x). Companion to results/_w221bmc_prereg_derive.py.
# Method (r787 preflight law, r587 zero-transcription): replay the committed
# lineage chain -- results/_w216bmc_prereg_derive.py PAIRS literal +
# _w217 SUB + _w218 SUB + _w219 SUB + _w220 SUB (FIVE-LEVEL, one deeper than
# the W220 four-level chain) -> the 46 W220-face blocks, each assert-verified
# count==1 in the freeze-time W220 blob (git show a9aee1d05:
# research/PERPETUAL_N1_W220_PREREG.md, the exact pre-backfill face) BEFORE
# any W221 pair application. Dump all 46 blocks to results/_r925bmc_w221_replay_blocks.json
# for derive-SUB authoring. Read-only vs the research/ tree (no prereg write).
import ast, hashlib, json, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

# ---------- freeze-time W220 blob ----------
BLOB = subprocess.run(["git", "-C", REPO, "show",
                       "a9aee1d05:research/PERPETUAL_N1_W220_PREREG.md"],
                      capture_output=True).stdout
assert BLOB, "freeze-time W220 blob fetch failed"
t = BLOB.decode("utf-8")
assert "## §7" in t and "占位" in t, "not the freeze-time (pre-backfill) face"

# ---------- upstream W219 blob (for the W219-face RAM replay value) ----------
BLOB219 = subprocess.run(["git", "-C", REPO, "show",
                          "0dae35332:research/PERPETUAL_N1_W219_PREREG.md"],
                         capture_output=True).stdout
assert BLOB219, "freeze-time W219 blob fetch failed"
t219 = BLOB219.decode("utf-8")

# ---------- replay-extract literals (lineage, zero transcription) ----------
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

# W219-face RAM note (machine-read from the W219 freeze-time blob)
_m219 = re.search(r"本窗 free RAM ~(\d+\.\d)GB", t219)
assert _m219, "W219 RAM note face not found"
RAM_REPLAY_219 = "~" + _m219.group(1)
# W220-face RAM note (machine-read from the W220 freeze-time blob = what the
# W220 derive wrote live)
_m220 = re.search(r"本窗 free RAM ~(\d+\.\d)GB", t)
assert _m220, "W220 RAM note face not found"
RAM_FACE_220 = "~" + _m220.group(1)
print(f"W219-face RAM replay: {RAM_REPLAY_219!r} | W220-face RAM: {RAM_FACE_220!r}")

pairs216 = extract_lit(r"results\_w216bmc_prereg_derive.py", "PAIRS", 46)
SUB17 = extract_lit(r"results\_w217bmc_prereg_derive.py", "SUB", 46)
SUB18 = extract_lit(r"results\_w218bmc_prereg_derive.py", "SUB", 46)
SUB19 = extract_lit(r"results\_w219bmc_prereg_derive.py", "SUB", 46,
                    vars={"RAM_GB": RAM_REPLAY_219})
SUB20 = extract_lit(r"results\_w220bmc_prereg_derive.py", "SUB", 46,
                    vars={"RAM_GB": RAM_FACE_220, "RAM_REPLAY": RAM_REPLAY_219})

OLD16 = [b.replace("@L14@", "214").replace("@T15@", "15") for _, b in pairs216]
OLD17 = []
for i, old in enumerate(OLD16):
    new = old
    for find, repl in SUB17[i]:
        c = new.count(find)
        assert c == 1, f"replay SUB17[{i}] count {c} != 1 for: {find[:60]}..."
        new = new.replace(find, repl, 1)
    OLD17.append(new.replace("@L14@", "214").replace("@L15@", "215").replace("@T16@", "16"))
OLD18 = []
for i, old in enumerate(OLD17):
    new = old
    for find, repl in SUB18[i]:
        c = new.count(find)
        assert c == 1, f"replay SUB18[{i}] count {c} != 1 for: {find[:60]}..."
        new = new.replace(find, repl, 1)
    OLD18.append(new.replace("@L14@", "214").replace("@L15@", "215").replace("@L16@", "216").replace("@T17@", "17"))
OLD19 = []
for i, old in enumerate(OLD18):
    new = old
    for find, repl in SUB19[i]:
        c = new.count(find)
        assert c == 1, f"replay SUB19[{i}] count {c} != 1 for: {find[:60]}..."
        new = new.replace(find, repl, 1)
    OLD19.append(new.replace("@L14@", "214").replace("@L15@", "215").replace("@L16@", "216").replace("@L17@", "217").replace("@T18@", "18"))
OLD20 = []
for i, old in enumerate(OLD19):
    new = old
    for find, repl in SUB20[i]:
        c = new.count(find)
        assert c == 1, f"replay SUB20[{i}] count {c} != 1 for: {find[:60]}..."
        new = new.replace(find, repl, 1)
    OLD20.append(new.replace("@L14@", "214").replace("@L15@", "215").replace("@L16@", "216").replace("@L17@", "217").replace("@L18@", "218").replace("@T19@", "19"))

# ---- W220 editor_gen same-window fix replay (r923 absorb: freeze-window label
# corrected + absorb note inserted -- r923 commit msg "editor_gen parfull-msg +
# prereg-note chain typos fixed same-window"). The committed freeze-time blob
# (a9aee1d05) carries this corrected face; the lineage replay must reproduce it.
_fix_old = "【bm-c 循环班 r922 freeze 窗·2026-10-12 10:5x·"
_fix_new = "【bm-c 循环班 r923 freeze 窗（absorb r922 freeze-prep estate）·2026-10-12 11:4x·"
assert OLD20[0].count(_fix_old) == 1, "editor_gen fix replay anchor not found in block[0]"
OLD20[0] = OLD20[0].replace(_fix_old, _fix_new, 1)
print("editor_gen fix replayed into block[0] (r923 absorb face)")

# preflight: every replayed W220-face block sits exactly once in the blob
bad = 0
for i, old in enumerate(OLD20):
    c = t.count(old)
    if c != 1:
        bad += 1
        print(f"PREFLIGHT FAIL block[{i}] count {c}")
assert bad == 0, f"preflight failures: {bad}"
print("preflight OK: 46/46 replayed blocks sit count==1 in the freeze-time W220 blob")

out = {"wave": 221, "replay_levels": 5, "blob_commit": "a9aee1d05",
       "blocks": [{"i": i, "bytes": len(b.encode('utf-8')), "sha16": hashlib.sha256(b.encode('utf-8')).hexdigest()[:16], "text": b} for i, b in enumerate(OLD20)]}
open(r"results\_r925bmc_w221_replay_blocks.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
print("dump OK: results/_r925bmc_w221_replay_blocks.json")
print("total bytes:", sum(x['bytes'] for x in out['blocks']))
