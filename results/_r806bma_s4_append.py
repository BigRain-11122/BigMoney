"""r806 bm-a S4 memory append: r804 marker-pollution pit (one line, python single-file
fresh-read-modify-write per r575 multi-writer law; CODELY.md <=30KB gate; conflict
markers written as HTML entities so the pre-commit claw does not flag this file)."""
import io

LINE = "- [2026-10-07 03:1x r806 bm-a] **S0 absorb/closeout commit marker-gate failure (r804 real incident -- MSG-2026-10-07-0250 bm-c reveal: regime_state.json/update_status.json shipped to origin carrying raw &lt;&lt;&lt;&lt;&lt;&lt;&lt;-HEAD conflict blocks, healed bm-c r648)**: the r804 close/absorb path committed a conflicted worktree state with the pre-commit claw not intercepting (claw missing/drifted at that moment; in-process reinstall this window restored both claws). Why: absorb windows commit fast under daemon-churn pressure; regenerable S6 faces get staged without reparse. How to apply: (1) before any absorb/closeout `git add` run reparse + marker scan over the changed set (r710B write gates); (2) claw verification belongs at session START (S0), not only S7; (3) marker pollution is zero-loss for regenerable faces (replay-side clean blob wins) but enters origin history -- strict json.loads consumers on the polluted tip lineage hit JSONDecodeError.\n"

p = "CODELY.md"
s = io.open(p, encoding="utf-8", newline="").read()
assert "r804 real incident" not in s, "pit already present"
i = s.rindex("### Reference")
s = s[:i] + LINE + "\n" + s[i:]
io.open(p, "w", encoding="utf-8", newline="").write(s)
print("appended; new size bytes:", len(s.encode("utf-8")))
