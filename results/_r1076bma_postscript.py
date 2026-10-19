# r1076 bm-a postscript: push_verified face (first-try clean delivery)
import json, time, datetime, io, os, subprocess

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
tip = subprocess.run(["git", "-C", ROOT, "rev-parse", "origin/main"], capture_output=True, text=True).stdout.strip()
behind = subprocess.run(["git", "-C", ROOT, "rev-list", "--count", "origin/main..main"], capture_output=True, text=True).stdout.strip()
ahead = subprocess.run(["git", "-C", ROOT, "rev-list", "--count", "main..origin/main"], capture_output=True, text=True).stdout.strip()
assert len(tip) == 40, "tip sha not 40-hex: %r" % tip
assert behind == "0" and ahead == "0", "behind/ahead not zero: %r/%r" % (behind, ahead)

face = {
    "ts": ts,
    "origin_tip": tip,
    "behind": 0,
    "ahead": 0,
    "note": "r1076 delivery first-try clean: S0 zero-rebase window (behind=0 at round head), push 6508346ed0..046518c02 main->main no race; post-push fetch ls-tree behind-0 ahead-0",
}
for p in (os.path.join(ROOT, "state-bm-a.json"), os.path.join(ROOT, "fleet", "machines", "bm-a.json")):
    d = json.load(io.open(p, encoding="utf-8"))
    d["push_verified"] = face
    d["sync"] = face
    d["last_delivery_verified_at"] = ts
    json.dump(d, io.open(p, "w", encoding="utf-8", newline=""), indent=1, ensure_ascii=False)

d2 = json.load(io.open(os.path.join(ROOT, "state-bm-a.json"), encoding="utf-8"))
assert d2["push_verified"]["origin_tip"] == tip and d2["sync"]["behind"] == 0
print("push_verified face written both faces; tip=%s behind=0 ahead=0" % tip[:12])
