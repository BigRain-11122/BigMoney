# r370 bm-a: hot-cold archive 25th batch (CODELY.md 10,099B > 10,000B hardline, same-window edit per O-20260927-0230).
# Migrate the nine settled pit-law entries (r349/r350/r119/r120/r368x2/r121/r369/r351) verbatim into
# research/memory-archive/202609.md 'twenty-fifth batch' section; keep User meta + cold pointers +
# the new r370 entry in CODELY.md; line-level zero-loss verify both sides.
import re

CM = "CODELY.md"
AR = "research/memory-archive/202609.md"

cl = open(CM, "rb").read()
crlf = b"\r\n" in cl
lines = cl.decode("utf-8").splitlines()
keep, migrate = [], []
for ln in lines:
    if re.match(r"- \[2026-09-28 .*坑律：", ln) and " r370 bm-a] " not in ln:
        migrate.append(ln)
    else:
        keep.append(ln)
assert len(migrate) == 10, f"expect 10 migrate lines, got {len(migrate)}: {[m[:40] for m in migrate]}"

# index-pointer line replaces migrated block (inserted right before the kept r370 entry)
r370_idx = next(i for i, ln in enumerate(keep) if " r370 bm-a] " in ln)
ptr = ("冷层指针：坑律正典 2026-09-28 风暴批十条（r349/r366/r350/r119/r120/r368×2/r121/r369/r351）已 verbatim "
       "整编至 research/memory-archive/202609.md『坑律归档 2026-09-28 二十五批』节（r370 bm-a 窗·行级零丢失校验）。")
keep.insert(r370_idx, ptr)

head = "\n\n## 坑律归档 2026-09-28 二十五批（r370 bm-a 窗·O-20260927-0230 ≤10KB 硬线当窗整编）\n\n"
with open(AR, "a", encoding="utf-8", newline="") as f:
    f.write(head + "\n".join(migrate) + "\n")
with open(CM, "wb") as f:
    out = "\n".join(keep) + "\n"
    f.write(out.replace("\n", "\r\n").encode("utf-8") if crlf else out.encode("utf-8"))

# zero-loss verify
ar_txt = open(AR, encoding="utf-8").read()
missing = [m[:60] for m in migrate if m not in ar_txt]
assert not missing, f"archive missing migrated lines: {missing}"
cm_txt = open(CM, encoding="utf-8").read()
resid = [m[:60] for m in migrate if m in cm_txt]
assert not resid, f"CODELY.md still contains migrated lines: {resid}"
import os
print(f"migrated 9 lines verbatim to archive; CODELY.md now {os.path.getsize(CM)}B; verify PASS both sides")
