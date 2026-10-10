# -*- coding: utf-8 -*-
# r852 clone helper: _r851bmc_rebase_resolver.py -> _r852bmc_rebase_resolver.py
src = open("results/_r851bmc_rebase_resolver.py", "rb").read().decode("utf-8")
s = src.replace(
    "# r851 bm-c rebase resolver: 32 UU shared regen faces (bm-b r860 same-window S6 co-run)",
    "# r852 bm-c rebase resolver: 31 UU shared regen faces (bm-b r861 same-window S6 co-run)")
s = s.replace("bloodline: _r845bmc_rebase_resolver.py",
              "bloodline: _r851bmc_rebase_resolver.py (verbatim clone, face-count 31)")
s = s.replace("rebase mode: :2: = ours (r851 close), :3: = theirs (bm-b r860).",
              "rebase mode: :2: = ours (r852 close), :3: = theirs (bm-b r861).")
s = s.replace('assert len(report) == 32, "expected 32 resolved faces, got %d" % len(report)',
              'assert len(report) == 31, "expected 31 resolved faces, got %d" % len(report)')
s = s.replace('print("RESOLVED %d files (32 UU expected)" % len(report))',
              'print("RESOLVED %d files (31 UU expected)" % len(report))')
open("results/_r852bmc_rebase_resolver.py", "w", encoding="utf-8", newline="").write(s)
print("clone OK")
