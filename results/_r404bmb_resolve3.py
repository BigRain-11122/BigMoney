"""r404 bm-b S7 push-retry resolver #3: 4-UU vs origin/main (bm-c r193 landed during push window).

CODELY.md memory-union: keep 21-line common base + bm-c's cold pointer + bm-c's renumbered
75th batch (origin first-in) + MY entry renumbered 75->76 (fleet/README sec.4 commit-time
order, later-editor yields; 62-batch precedent). Snapshots take-NEW by blob ts; js-wrapper
whole-bytes per R209 (twin decides).
"""
import json
import re
import subprocess

TS_RE = re.compile(r"^20\d{2}-")
CLOCK_RE = re.compile(r"[T ]\d{2}:\d{2}")


def blob(stage, path):
    return subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True).stdout


def deep_wallclock(obj):
    best = None

    def walk(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str):
                    nk = k.replace("_", "").replace("-", "").lower()
                    if any(nk.startswith(p) for p in ("asof", "updated", "generated", "ts", "last")):
                        if TS_RE.match(v) and CLOCK_RE.search(v):
                            if best is None or v > best:
                                best = v
                walk(v)
        elif isinstance(o, list):
            for it in o:
                walk(it)

    walk(obj)
    return best


def dump_conv(raw):
    obj = json.loads(raw)
    text = raw.decode("utf-8")
    for indent in (1, 2, 3, 4):
        for ea in (False, True):
            for trail in ("", "\n"):
                cand = json.dumps(obj, ensure_ascii=ea, indent=indent) + trail
                if cand == text:
                    return obj, dict(indent=indent, ensure_ascii=ea, trail=trail)
    return obj, dict(indent=2, ensure_ascii=False, trail="\n")


report = []

# ---- 1) CODELY.md memory-union + my batch renumber 75->76 ----
p = "CODELY.md"
t2 = blob(2, p).decode("utf-8").splitlines()
t3 = blob(3, p).decode("utf-8").splitlines()
i = 0
while i < len(t2) and i < len(t3) and t2[i] == t3[i]:
    i += 1
base = t2[:i]
uniq2 = [l for l in t2[i:] if l not in set(t3)]      # bm-c new lines (cold pointer + 75th)
uniq3 = [l for l in t3[i:] if l not in set(t2)]      # my 75th entry
renumbered = []
for l in uniq3:
    if "坑律七十五批" in l:
        l = l.replace("坑律七十五批", "坑律七十六批（75 号让位=bm-c r193 七十五批先在 origin·fleet §4 commit 时间序·六十二批让位同例）", 1)
        l = l.replace("r404 bm-b 坑律七十六批", "r404 bm-b 坑律七十六批", 1)
    renumbered.append(l)
merged = base + uniq2 + renumbered
text = "\n".join(merged) + "\n"
open(p, "w", encoding="utf-8", newline="").write(text)
assert "七十六批" in open(p, encoding="utf-8").read()
report.append(f"{p}: union base={len(base)} + bm-c {len(uniq2)} + mine {len(renumbered)} (renumbered 75->76)")

# ---- 2) snapshots take-new ----
for p in ["results/dashboard_status.json", "results/prospect_promotion/_summary.json"]:
    o2, o3 = blob(2, p), blob(3, p)
    t2s = deep_wallclock(json.loads(o2)) if o2.strip() else None
    t3s = deep_wallclock(json.loads(o3)) if o3.strip() else None
    side = "theirs" if (t3s or "") > (t2s or "") else "ours"
    raw = o3 if side == "theirs" else o2
    obj, conv = dump_conv(raw)
    txt = json.dumps(obj, ensure_ascii=conv["ensure_ascii"], indent=conv["indent"]) + conv["trail"]
    open(p, "w", encoding="utf-8", newline="").write(txt)
    json.loads(open(p, encoding="utf-8").read())
    report.append(f"{p}: snapshot side={side} ts2={t2s} ts3={t3s}")

# ---- 3) js-wrapper whole-bytes (twin dashboard_status.json decides) ----
p = "results/dashboard_status.js"
o2, o3 = blob(2, p), blob(3, p)
t2j = deep_wallclock(json.loads(blob(2, "results/dashboard_status.json")))
t3j = deep_wallclock(json.loads(blob(3, "results/dashboard_status.json")))
side = "theirs" if (t3j or "") > (t2j or "") else "ours"
open(p, "wb").write(o3 if side == "theirs" else o2)
report.append(f"{p}: js-wrapper side={side} whole-bytes (twin ts2={t2j} ts3={t3j})")

print("\n".join(report))
print("RESOLVE3-OK all 4 files written+parsed")
