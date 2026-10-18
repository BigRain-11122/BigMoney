# -*- coding: utf-8 -*-
# r1088 bm-c: follow-up needle probe (overlap forms + stale faces + stamps)
import io, os, re, subprocess, datetime

t = io.open(r"results/_w266bmc_freeze_edits.py", encoding="utf-8", newline="").read()
forms = [
 "own W247..W264 legs (18)", "own W247..W264 legs", "W247..W264 legs",
 "W211..W265 legs 54", "W211..W265 legs", "m211",
 "W266 FREEZE UNBLOCKED", "W266 block parity = 121 rows",
 "bm-a r1085 window", "bm-a own-seat continuity", "bm-c own-seat continuity",
 "bma rows 129 + candidate 130th", "(bm-a seat owner expected)",
 "rows {len(bma_rows_live)}", "ONE HUNDRED AND THIRTIETH", "bma_ordinal",
 "fifty-three", "W245..W262", "W211..W262", "fifty-two", "editor template",
 "thirty-five", "593901", "W259..W250", "registered wave below 263 composes",
 "W244 leg boundary", "rows 255 + candidate", "w265_freeze_sha",
 "w266_prereg_sha", "w266_receipt_sha", "probe leg0 face", "PRE-W266-splice",
 "PRE-splice post-W265", "post-W265 registration", "expect 255/130/84",
 "W266+W259..W250", "fifty-fourth consecutive fully-clean",
 "clean-precondition fifty-fourth consecutive window", "anchors W265",
 "dual-window parity", "bm-c five-face freeze upstream seat",
 "bm-c (upstream seat honored)", "owner=bm-c seat honored",
 "was published AFTER", "W267 walk", "engine_owner==bm-c rows 84",
 "bm-c rows 84 + candidate = 85th owned", "zero waits-upstream face",
 "n1_w266_results.json present", "post-W266 universe",
]
for s in forms:
    print(f"{t.count(s):5d}  {s!r}")

mt = os.path.getmtime(r"results/_w267bmc_prereg_derive.py")
print("w267 prereg derive script mtime:",
      datetime.datetime.fromtimestamp(mt).strftime("%Y-%m-%d %H:%M:%S"))
mt2 = os.path.getmtime(r"research/PERPETUAL_N1_W267_PREREG.md")
print("w267 prereg mtime:",
      datetime.datetime.fromtimestamp(mt2).strftime("%Y-%m-%d %H:%M:%S"))

r = subprocess.run(["git", "log", "--format=%H", "--diff-filter=A", "--",
                    "results/_w265bmc_freeze_edits_TOL.py"],
                   capture_output=True, text=True)
sha = r.stdout.strip().splitlines()[0]
r2 = subprocess.run(["git", "show", sha + ":results/_w265bmc_freeze_edits_TOL.py"],
                    capture_output=True)
tol = r2.stdout.decode("utf-8", errors="replace")
m = re.search(r'"wave": (\d+),', tol)
print("W265 TOL canon wave field:", m.group(1) if m else "NOT FOUND")
