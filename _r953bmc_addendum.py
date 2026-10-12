# -*- coding: utf-8 -*-
# r953 addendum: delivery self-proof + pitfall disclosure ledger line
p = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\logs\iteration-loop\round_reports-bm-c.md"
line = (
"2026-10-13T04:12:00+08:00 | r953-addendum | bm-c delivery self-proof: bigmoney push LANDED "
"47cdf3f51..d6446b120 (ahead_unpushed=0, 4 commits incl r953+repair) + group repo push LANDED "
"768941b..982b3fd via worktree cherry-pick (he-window dirty tree zero-touch, 2 new files "
"blob-verified in origin tree) | 本地未达 origin commit 数=0 both repos | PITFALLS disclosed: "
"(1) Tools/Invoke-SilentExe.ps1 positional args = param bind error false-MISSING (must use "
"-Exe/-ArgString named params); (2) PS semicolon-chain ran git add after resolver crash = "
"conflict markers staged into replayed commit 27967cfdd -- pre-commit claw does NOT fire on "
"rebase --continue (claw gap) -- healed same-window by repair commit a35722fab (compute_audit "
"top=mine+history union 72, two bm-c faces wholesale) before any push, zero marker ever reached "
"origin; (3) rebase base raced twice (bm-b pushed 47cdf3f51 mid-window) = second rebase replay "
"resolved, push claw caught the stale-base deletion-set correctly before any damage | "
"[r953 bm-c addendum]"
)
with open(p, "r", encoding="utf-8") as f:
    body = f.read()
assert "r953 bm-c addendum" not in body, "already appended"
if not body.endswith("\n"):
    body += "\n"
body += line + "\n"
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write(body)
print("ADDENDUM_APPENDED")
