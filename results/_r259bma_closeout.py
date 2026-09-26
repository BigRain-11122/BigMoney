# -*- coding: utf-8 -*-
"""R259 bm-a closeout: state file 258->259 (byte-mirrored: utf-8 no BOM,
CRLF EOL, no trailing newline, indent=1) + heartbeat update."""
import io
import json
import time

P = "state-bm-a.json"
raw = io.open(P, "rb").read()
assert not raw.startswith(b"\xef\xbb\xbf") and not raw.endswith(b"\n")
d = json.loads(raw.decode("utf-8"))
assert d["round_no"] == 258

d["round_no"] = 259
d["did"] = (
    "R259: T-73 s2 slice-E style-rotation FULL ARC ONE ROUND (last s2 "
    "topic -> s2 COMPLETE): prereg freeze cb2e0e84 pre-burn (runner header + "
    "SEED_REGISTRY t73_style_rot_s1 20261030 one-step R250); LAW "
    "STYLE-MOM-252-63 year->quarter style momentum ALIVE both sides THIN "
    "(IS +0.100/1.04x p95, OOS +0.151/1.08x p95) + STYLE-MOM-63-21 frozen "
    "one-sided NOT alive with OOS -0.192 beyond null -0.146 = quarter-"
    "reversal post-hoc face (future prereg candidate) -> dual-horizon "
    "rotation structure (annual trend + quarterly mean-reversion); "
    "narrative: 2017 core CONFIRMED (+38pp spread), 2024 dividend "
    "CONFIRMED (div_lowvol 4-year dynasty), 2021 growth PARTIAL, 2023 "
    "micro modest rel-win (corpus-from-Sep disclosed); envelope fund-event "
    "guard caught 4 artifacts (+248.6%/+176.3%/-51.1%/-12.7% all "
    "base-flat days); E1 defects x2 self-caught: run1 raw-face descriptive "
    "poison (+454%/+124%/-41% cells) -> clean_value bridge + defective "
    "archive; ledger self-echo (187789 intermediate discarded) -> prev="
    "head-minus-own-row guard, canonical 187585+102=187687 single-count; "
    "post_review row registered same round + 2nd R256-family check-rot "
    "repaired depth=30 -> reviewer 21 YES/0 NO/5 WAIT; S6 22 legs all "
    "exit 0 weekend no-ops; smoke 25/25"
)
d["verdict"] = (
    "GREEN R259: s2 COMPLETE (A/B/C/D/E all landed); style-rotation = "
    "dual-horizon law (annual momentum thin-alive + quarterly reversal "
    "face); dividend dynasty ended 2024, current 2025+ = growth/small "
    "regime; no fabricated busywork O-1137 (pool starvation honestly "
    "answered: board clear + pool 47/47 + zero runnable candidates, "
    "real supply = this slice full arc)"
)
d["next"] = (
    "s3 remaining CN-native model consumption (CN-CORE-SATELLITE evidence "
    "base complete: ballast=lowvol all-era + dividend defense, satellite="
    "rotation dual-scale, regime=v3 guard); 09-28 Monday new-bar chain; "
    "10-01 monthly trio + REGIME_GUARD v3 activation window; T-70 C-arm "
    "verdict 10-09; transfer/t80-deep-bcd-basis arrival check each S0.5"
)
ts = time.strftime("%Y-%m-%d %H:%M:%S")
d["ts"] = ts
d["last_round_ts"] = ts
d["updated_at"] = ts
d["current_task"] = (
    "T-73 s3 remaining CN-native consumption next; slice-E closed; fleet "
    "maintenance"
)
d["last_round"] = "R258"
d["last_round_at"] = d.get("updated_at") or ts
d["updated"] = ts
d["last_run"] = ts

txt = json.dumps(d, ensure_ascii=False, indent=1)
out = txt.replace("\n", "\r\n").encode("utf-8")
io.open(P, "wb").write(out)
print("state 258->259 written; CRLF faces:",
      b"\r\n" in out, "ends_nl:", out.endswith(b"\n"))
