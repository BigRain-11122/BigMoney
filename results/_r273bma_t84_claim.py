# r273 bm-a: claim T-2026-09-26-84-P1 per CEO immediate law (O-20260926-2229, claim-and-start same round).
# Byte-face probed: no-BOM / CRLF / indent=1 / WITH trailing newline (mirrored).

import json, datetime

p = "fleet/tasks/T-2026-09-26-84-P1.json"
d = json.load(open(p, encoding="utf-8-sig"))
assert d.get("status") == "open", "must claim from open state"
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
d["status"] = "claimed"
d["claimed_by"] = "bm-a (OS iteration loop, round 273; CEO immediate ticket per O-20260926-2229: claim-and-start same round)"
d["claimed_at"] = now
d["progress_r273"] = (
    "CLAIMED same round @ " + now + " (immediate law). s1 STARTED same round: D:\\Money census (58 py verified) + "
    "lookahead-pattern mechanical scan (shift(-)/rolling center/overlap windows/eval-window overlap) -> "
    "results/r273_t84_s1_lookahead_scan.json. IC=1.0 / Sharpe 5.89 red flags from O-2229 sec-1 held pending "
    "this audit; GM V60_CONVERGENCE_MAP.md (79ded1e5) consumed as s4 input, zero overlap with s1 lane. "
    "Continuation point: per-file audit of flagged hits + IC/Sharpe recompute de-bloat slices."
)
out = json.dumps(d, ensure_ascii=False, indent=1) + "\n"
open(p, "wb").write(out.replace("\n", "\r\n").encode("utf-8"))
back = json.load(open(p, encoding="utf-8-sig"))
assert back["status"] == "claimed" and "bm-a" in back["claimed_by"]
b = open(p, "rb").read()
assert b.endswith(b"\r\n"), "trailing newline must be preserved"
print("T-84 claimed by bm-a @", now, "| byte-face mirrored (CRLF, indent=1, trail-NL)")
