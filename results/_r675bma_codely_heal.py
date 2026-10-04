"""r675 CODELY.md union heal -- block-level append (origin full + mine-new lines)
r453 canon correct form: dedup applies to the APPENDED ENTRY BLOCK, never
line-collapses the whole file (blank/separator rows are structural).
"""
import subprocess, sys

PICK = "ffb452610"

def show(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    assert r.returncode == 0, (rev, path, r.stderr[:200])
    return r.stdout.decode("utf-8", "replace")

o_txt = show("HEAD", "CODELY.md")
m_txt = show(PICK, "CODELY.md")
o_lines, m_lines = o_txt.splitlines(), m_txt.splitlines()

# lines mine has that origin lacks, in mine's order (append-only new rows)
o_set = set(o_lines)
mine_new = [ln for ln in m_lines if ln not in o_set]
marker_new = [ln for ln in mine_new if ln.startswith(("<<<<<<<", "=======", ">>>>>>>"))]
assert not marker_new, f"markers in mine-new block: {marker_new}"

union_lines = o_lines + mine_new
union = "\n".join(union_lines)
if not union.endswith("\n"): union += "\n"

# assertions: every origin line preserved exactly once in order; every
# mine-new line present; no conflict markers; r675 entry present
assert union.startswith(o_txt.rstrip("\n")), "origin block damaged"
assert all(ln in union.splitlines() for ln in mine_new), "mine-new lost"
assert not any(ln.startswith(("<<<<<<<", ">>>>>>>")) for ln in union.splitlines())
assert any("r675 bm-a" in ln for ln in union.splitlines()), "r675 entry missing"
n_r675 = sum(1 for ln in union.splitlines() if "r675 bm-a] 后冻结批" in ln)
assert n_r675 == 1, f"r675 entry count={n_r675}"

open("CODELY.md", "wb").write(union.encode("utf-8"))
print(f"HEAL-OK: origin {len(o_lines)} lines + mine-new {len(mine_new)} lines = {len(union_lines)}")
for ln in mine_new:
    print("  NEW:", ln[:110])
