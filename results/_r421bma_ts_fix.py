# -*- coding: utf-8 -*-
"""_r421bma_ts_fix.py -- one-shot pre-push timestamp correction (r421).

Draft-time wall-clock assumption (09:3x) was wrong; actual clock ~09:06
(compute_audit ts 09:02:42). Pre-push window = the only correction window
(pit law). Fixes: banner 09:3x->09:0x, ticket 09:35->09:05, MSG id
0935->0905 (file rename + all references), CODELY pit 09:4x->09:0x.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fix_file(path: Path, subs) -> str:
    text = path.read_text(encoding="utf-8")
    orig = text
    for old, new in subs:
        text = text.replace(old, new)
    if text != orig:
        path.write_text(text, encoding="utf-8")
        return "FIXED"
    return "no-change"


def main() -> int:
    report = []

    # 1. prereg banner + trigger receipt + MSG refs
    p = ROOT / "research" / "TRIAL_LABOR_W7_PREREG.md"
    report.append("prereg: " + fix_file(p, [
        ("2026-09-29 09:3x·bm-a r421", "2026-09-29 09:0x·bm-a r421"),
        ("机械回执 2026-09-29 09:2x 实读", "机械回执 2026-09-29 09:0x 实读"),
        ("MSG-20260929-0935", "MSG-20260929-0905"),
    ]))

    # 2. ticket
    p = ROOT / "fleet" / "tasks" / "T-2026-09-29-118-P1.json"
    report.append("ticket: " + fix_file(p, [
        ("2026-09-29 09:35", "2026-09-29 09:05"),
        ("MSG-20260929-0935", "MSG-20260929-0905"),
    ]))

    # 3. MSG file rename + inner banner
    old_msg = ROOT / "fleet" / "inbox" / "MSG-20260929-0935-bma-ALL-W7-prereg-freeze.md"
    new_msg = ROOT / "fleet" / "inbox" / "MSG-20260929-0905-bma-ALL-W7-prereg-freeze.md"
    if old_msg.exists():
        text = old_msg.read_text(encoding="utf-8")
        text = text.replace("MSG-20260929-0935", "MSG-20260929-0905")
        text = text.replace("（2026-09-29 09:3x·bm-a r421", "（2026-09-29 09:0x·bm-a r421")
        new_msg.write_text(text, encoding="utf-8")
        old_msg.unlink()
        report.append("msg: RENAMED 0935->0905 + banner fixed")
    elif new_msg.exists():
        report.append("msg: already-0905")
    else:
        report.append("msg: NOT FOUND")

    # 4. science_gates.py seed comment
    p = ROOT / "scripts" / "science_gates.py"
    report.append("gates: " + fix_file(p, [("MSG-20260929-0935", "MSG-20260929-0905")]))

    # 5. CODELY.md pit timestamp
    p = ROOT / "CODELY.md"
    report.append("codely: " + fix_file(p, [("[2026-09-29 09:4x r421 bm-a]", "[2026-09-29 09:0x r421 bm-a]")]))

    # 6. round report line MSG ref
    p = ROOT / "logs" / "iteration-loop" / "round_reports-bm-a.md"
    report.append("report: " + fix_file(p, [("MSG-20260929-0935", "MSG-20260929-0905")]))

    # 7. state + heartbeat MSG refs
    for name in ("state-bm-a.json",):
        p = ROOT / name
        report.append(name + ": " + fix_file(p, [("MSG-0935", "MSG-0905")]))
    p = ROOT / "fleet" / "machines" / "bm-a.json"
    report.append("heartbeat: " + fix_file(p, [("MSG-0935", "MSG-0905")]))

    # residual scan: any 0935 r421 refs left (excluding this fixer + append helper)
    import subprocess
    res = subprocess.run(
        ["git", "grep", "-n", "MSG-20260929-0935", "--", "."],
        cwd=ROOT, capture_output=True, text=True)
    left = [ln for ln in res.stdout.splitlines() if "_r421bma" not in ln.split(":")[0]]
    report.append("residual-0935-refs: " + (str(len(left)) if left else "0"))
    for ln in left[:5]:
        report.append("  " + ln)
    print("\n".join(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
