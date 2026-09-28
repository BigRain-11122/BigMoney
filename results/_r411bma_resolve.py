# r411 bm-a rebase-storm resolver (13-UU vs bm-b r405 S6 twin-regen + bm-c r194 pitlaw-78)
# Laws applied:
#  - CODELY.md: memory-union (append-only tail union, merge-base byte-anchor law)
#    + MY batch 78 YIELDS to bm-c r194 batch-78 (origin-first, fleet sec.4
#    commit-time order; 62/75 yield precedents) -> renumbered to 79.
#  - HANDOVER.md: head-insert union (both 5x lines preserved, newest on top).
#  - compute_audit.json: history ts-key union (162+162 -> 163 dedup).
#  - daily-regen pairs (REPORT/LIVE json+md, status faces, token, regime,
#    b_layer): take-NEW = stage3 (mine 03:13-03:17 > origin 03:10 twins;
#    r404 bm-b batch-76 law: side=theirs iff t3>t2 in rebase frame).
import json, subprocess, sys

def stage(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        sys.exit(f"git show {spec} failed: {r.stderr.decode()[:200]}")
    return r.stdout

def write_bytes(path, data):
    with open(path, "wb") as f:
        f.write(data)

# ---------- 1) CODELY.md: tail union + my line renumbered 78->79 ----------
s2 = stage(":2:CODELY.md").decode("utf-8")
s3 = stage(":3:CODELY.md").decode("utf-8")
base = stage(":1:CODELY.md").decode("utf-8")
# my newly added line(s): lines in s3 beyond base, not present verbatim in s2
base_lines = base.splitlines()
s2_lines = s2.splitlines()
s3_lines = s3.splitlines()
s2_set = set(s2_lines)
base_set = set(base_lines)
my_new = [l for l in s3_lines if l not in s2_set and l not in base_set]
if len(my_new) != 1:
    sys.exit(f"CODELY union expected exactly 1 new line of mine, got {len(my_new)}: {my_new[:3]}")
mine = my_new[0]
old_head = "坑律七十八批（5x 核对漏检=轮末指针非承诺律）："
new_head = ("坑律七十九批（78 号让位=bm-c r194 七十八批先在 origin·fleet §4 commit 时间序·"
            "六十二/七十五批让位同例）（5x 核对漏检=轮末指针非承诺律）：")
if old_head not in mine:
    sys.exit("CODELY my-line renumber anchor missing")
mine79 = mine.replace(old_head, new_head, 1)
out = s2
if not out.endswith("\n"):
    out += "\n"
out += mine79 + "\n"
write_bytes("CODELY.md", out.encode("utf-8"))
print("CODELY.md union: origin face + my line renumbered 78->79")

# ---------- 2) HANDOVER.md: head-insert union ----------
h2 = stage(":2:research/HANDOVER.md").decode("utf-8")
h3 = stage(":3:research/HANDOVER.md").decode("utf-8")
h2_lines = h2.splitlines()
h2_set = set(h2_lines)
h3_lines = h3.splitlines()
my_h = [l for l in h3_lines if l.startswith("> bm-a round 410") and l not in h2_set]
if len(my_h) != 1:
    sys.exit(f"HANDOVER expected exactly 1 new line of mine, got {len(my_h)}")
# insert after the doc header line (the "> 2026-09-23 11:35" line, index 2 in file: blank, title, header)
idx = None
for i, l in enumerate(h2_lines):
    if l.startswith("> 2026-09-23 11:35"):
        idx = i
        break
if idx is None:
    sys.exit("HANDOVER header anchor missing")
res = h2_lines[:idx+1] + [my_h[0]] + h2_lines[idx+1:]
write_bytes("research/HANDOVER.md", ("\n".join(res) + "\n").encode("utf-8"))
print("HANDOVER.md union: my r410 line on top + bm-b r405 line preserved")

# ---------- 3) compute_audit.json: history ts-key union ----------
j2 = json.loads(stage(":2:results/compute_audit.json").decode("utf-8"))
j3 = json.loads(stage(":3:results/compute_audit.json").decode("utf-8"))
h2h, h3h = j2.get("history", []), j3.get("history", [])
seen, merged = set(), []
for row in h2h + h3h:
    key = row.get("ts")
    if key in seen:
        continue
    seen.add(key)
    merged.append(row)
j3["history"] = merged
write_bytes("results/compute_audit.json", json.dumps(j3, ensure_ascii=False, indent=1).encode("utf-8"))
print(f"compute_audit.json union: {len(h2h)}+{len(h3h)} -> {len(merged)} history rows")

# ---------- 4) take-NEW stage3 regen faces ----------
take_new = [
    "docs/daily_report/REPORT-2026-09-29.json",
    "docs/daily_report/REPORT-2026-09-29.md",
    "docs/live_usage/LIVE-2026-09-29.json",
    "docs/live_usage/LIVE-2026-09-29.md",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]
for f in take_new:
    write_bytes(f, stage(":3:" + f))
print("take-NEW stage3 x", len(take_new))

# ---------- 5) consistency: my round report + state mention batch number ----------
rp_path = "logs/iteration-loop/round_reports-bm-a.md"
rp = open(rp_path, encoding="utf-8").read()
rp_new = rp.replace("S4 CODELY 坑律七十八批", "S4 CODELY 坑律七十九批（78 号让位=bm-c r194 七十八批先在 origin）")
if rp_new != rp:
    write_bytes(rp_path, rp_new.encode("utf-8"))
    print("round report: batch-78 -> 79 consistency fix")
st_path = "state-bm-a.json"
stt = open(st_path, encoding="utf-8").read()
stt_new = stt.replace("pit-law batch-78 (next-pointer obligation checklist law)",
                      "pit-law batch-79 (78 yielded to bm-c r194 first-in-origin; next-pointer obligation checklist law)")
if stt_new != stt:
    write_bytes(st_path, stt_new.encode("utf-8"))
    print("state: batch-78 -> 79 consistency fix")
print("RESOLVER DONE")
