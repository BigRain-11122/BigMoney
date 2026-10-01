# r326 bm-c: deterministic post-quit conflict resolution (explicit blobs, no index stages)
# CODELY union = 5b73868c6 (origin, has bm-a r527 line) + my r326 line (from 7abed5a39)
# attrition = my blob (wall-clock newer 17:43:21 vs 17:41:45)
import json, subprocess, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
BM = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"


def blob(ref, path):
    o = subprocess.check_output(["git", "-C", BM, "show", f"{ref}:{path}"])
    return o.decode("utf-8", errors="replace")


origin = blob("5b73868c6", "CODELY.md")
mine = blob("7abed5a39", "CODELY.md")
my_line = [ln for ln in mine.splitlines()
           if ln.startswith("- [2026-10-01 17:4x r326 bm-c]")]
assert len(my_line) == 1, f"r326 lines: {len(my_line)}"
assert any(ln.startswith("- [2026-10-01 17:4x r527 bm-a]")
           for ln in origin.splitlines()), "r527 line missing on origin blob"
if my_line[0] not in origin:
    resolved = origin.rstrip("\n") + "\n" + my_line[0] + "\n"
else:
    resolved = origin
bad = [ln for ln in resolved.splitlines()
       if ln.startswith("<<<<<<< ") or ln == "======="
       or ln.startswith(">>>>>>> ")]
assert not bad, f"line-anchored markers remain: {bad[:3]}"
with open(BM + r"\CODELY.md", "w", encoding="utf-8", newline="") as fh:
    fh.write(resolved)
print("CODELY union OK (r527 + r326 both present, zero line-anchored markers)")

att = blob("7abed5a39", "results/_attrition_guard_scan.json")
j = json.loads(att)
assert "<<" not in att[:200]
with open(BM + r"\results\_attrition_guard_scan.json", "w",
          encoding="utf-8") as fh:
    fh.write(att)
print("attrition = my 17:43:21 blob OK, ts", j.get("ts"))
