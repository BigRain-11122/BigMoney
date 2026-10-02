# r357 bm-c: fix the indentation corruption introduced by the replace-tool
# whitespace normalization in the W63 materializer insertion region
# (perpetual_faces_n1.py). Deterministic content-anchored surgery:
# - 5 corrupted W62-tail lines restored to exact indentation
# - W63 leg block (comment+try/finally) shifted -8 spaces uniformly
# - trailing T-141 comment header line shifted -8
# Asserts: anchors found exactly once, py_compile passes, block boundaries sane.
import py_compile
import sys

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\scripts\perpetual_faces_n1.py"
with open(P, "r", encoding="utf-8") as f:
    lines = f.readlines()  # keepends

# anchors
START = '                     "W62 prior-wave set must derive from registry keys (no 15, " \\\n'
T141 = "            # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n"

start_idx = [i for i, l in enumerate(lines) if l == START]
assert len(start_idx) == 1, "start anchor count=%d" % len(start_idx)
start_idx = start_idx[0]

t141_idx = [i for i, l in enumerate(lines) if l == T141]
assert len(t141_idx) == 1, "t141 anchor count=%d" % len(t141_idx)
t141_idx = t141_idx[0]

# sanity: expected structure between anchors
assert lines[start_idx + 1] == '                    "incl. 48..61)"\n'
assert lines[start_idx + 2] == '                assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"\n'
assert lines[start_idx + 3] == "            finally:\n"
assert lines[start_idx + 4] == "                _set_wave(2)\n"
assert lines[start_idx + 5].strip() == ""
assert lines[start_idx + 6] == "            # --- W63 materializer face (r357 bm-c freeze, own-series law\n"
# the W63 leg's closing finally right before the T-141 comment
assert lines[t141_idx - 1].strip() == "", "expected blank before T-141 comment"
assert lines[t141_idx - 2] == "                _set_wave(2)\n"
assert lines[t141_idx - 3] == "            finally:\n"

# 1) W62 tail: 5 exact-indent lines
lines[start_idx + 0] = '            "W62 prior-wave set must derive from registry keys (no 15, " \\\n'
lines[start_idx + 1] = '            "incl. 48..61)"\n'
lines[start_idx + 2] = '        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"\n'
lines[start_idx + 3] = "    finally:\n"
lines[start_idx + 4] = "        _set_wave(2)\n"

# 2) W63 block (start_idx+6 .. t141_idx-1): -8 leading spaces on non-empty lines
for i in range(start_idx + 6, t141_idx):
    l = lines[i]
    if l.strip() == "":
        continue
    assert l.startswith(" " * 8), "line %d lacks 8-space prefix: %r" % (i + 1, l[:20])
    lines[i] = l[8:]

# 3) T-141 comment header: -8
lines[t141_idx] = "    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim\n"

with open(P, "w", encoding="utf-8", newline="") as f:
    f.writelines(lines)

py_compile.compile(P, doraise=True)
print("FIXED: W62 tail restored + W63 leg -8 re-indent + T-141 header fixed")
print("py_compile OK")
