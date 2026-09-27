import json
import io
import datetime as dt

p = "fleet/tasks/T-2026-09-27-93-P1.json"
t = json.load(io.open(p, encoding="utf-8-sig"))
assert t["status"] == "open", f"ticket not open: {t['status']}"
t["status"] = "claimed"
t["claimed_by"] = ("bm-a (OS iteration loop R314 S7 discovery; P1 transfer ticket "
                   "= claim-and-start same round per collaboration law)")
t["claimed_at"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
t["progress_r314_bma"] = ("R314 bm-a claim-and-start: sender-face inventory + Plan A "
                          "staging + manifest + transfer branch push this round; "
                          "honest missing-list face if any of the 30 absent")
with io.open(p, "w", encoding="utf-8") as f:
    json.dump(t, f, ensure_ascii=False, indent=1)
print("claimed at", t["claimed_at"])
