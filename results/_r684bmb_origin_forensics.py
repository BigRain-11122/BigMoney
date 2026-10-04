# r684 bm-b: origin-side forensics (who wrote round-688; what state/report faces say)
import subprocess, json

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.stdout + r.stderr

print("=== origin delta commits w/ author+date ===")
out = run(["git", "log", "--format=%h %an %ae %ad %s", "--date=iso",
           "HEAD..origin/main"])
for l in out.splitlines():
    print(l[:170])
print()
print("=== origin state.json round_no ===")
st = json.loads(run(["git", "show", "origin/main:state.json"]))
print("round_no =", st.get("round_no"))
print()
print("=== origin heartbeat bm-b ===")
hb = json.loads(run(["git", "show", "origin/main:fleet/machines/bm-b.json"]))
for k in ("last_seen", "heartbeat_epoch_utc", "clock_read", "current_task",
          "verdict"):
    print(k, "=", str(hb.get(k))[:150])
print()
print("=== origin round_reports tail 6 lines (raw, any lane) ===")
out = run(["git", "show", "origin/main:logs/iteration-loop/round_reports.md"])
lines = out.splitlines()
for l in lines[-6:]:
    print(l[:200])
print()
print("=== grep 685-688 in origin report ===")
for l in lines:
    if any(m in l for m in ("r685", "r686", "r687", "r688", "round 688")):
        print(l[:200])
