"""r416-cont bm-a push-storm resolver CYCLE-2 (after bm-b r412-successor 1a8a7d0c4).

Conflicts this cycle: 6 ALL_FACES (resolved via merge_lane_views, called from shell)
+ CODELY.md custom:
  - origin tail now: ptr(81-83) + ptr(84-86) + batch-87(bm-c r201) + batch-88(bm-b r412)
  - mine: ptr(81-83) + ptr(84-86) + batch-87(origin, kept in 1st cycle) + my line (labeled 88 -> RENUMBER 89)
  - merged hot layer = origin's 27 lines + my line as batch-89 -> ~10.9KB > 10KB hard line
  - -> hot-cold same window: migrate batch-87 + batch-88 verbatim to archive
     (new section), replace with one pointer line; final target <=10KB.
x2_watch_log automerge verified separately (row count + tail ts monotonic).
"""
import json, re, subprocess, sys, os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def stage(n, path):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"stage read fail {n}:{path}")
    return r.stdout.decode("utf-8")


print("== x2_watch_log automerge sanity (no conflict this cycle) ==")
t = open("results/x2_watch_log.jsonl", encoding="utf-8").read().splitlines()
rows = [l for l in t if l.strip()]
ts = [re.search(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", l).group(0) for l in rows[-8:]]
print(f"  rows={len(rows)} (expect 3126); tail ts monotonic={ts == sorted(ts)} tail={ts[-2:]}")
assert len(rows) == 3126, f"unexpected row count {len(rows)}"
for l in rows[-2:]:
    json.loads(l)

print("== CODELY.md cycle-2 memory-union + renumber 89 + hot-cold(87,88) ==")
o = stage(2, "CODELY.md").splitlines()
m = stage(3, "CODELY.md").splitlines()
b = stage(1, "CODELY.md").splitlines()
n = 0
while n < len(o) and n < len(m) and n < len(b) and o[n] == m[n] == b[n]:
    n += 1
print(f"  common prefix={n} (base {len(b)} lines)")
suf_o, suf_m = o[n:], m[n:]
b87_o = [o[n - 1]] if "坑律八十七批" in o[n - 1] else []
b88_o = [l for l in suf_o if "坑律八十八批" in l]
mine = [l for l in suf_m if "坑律八十八批" in l and "r416-cont" in l]
assert len(b87_o) == 1 and len(b88_o) == 1 and len(mine) == 1, (len(b87_o), len(b88_o), len(mine))
assert o[n - 2].startswith("冷层指针"), "line before batch-87 should be a pointer"
mine89 = mine[0].replace("坑律八十八批", "坑律八十九批", 1)
assert "坑律八十九批" in mine89
# hot layer final: prefix-minus-87 + ptr(87/88 new) + b89
ptr_new = ("冷层指针：坑律正典 2026-09-29 八十七/八十八批（r201 bm-c pool_worker 车道门未移植+closed-fail "
           "写读契约断裂双坑+r412 bm-b 死会话继任收割序律·一次推送解锁三面）全文 verbatim=archive 202609.md"
           "『坑律归档 2026-09-29 r416-cont bm-a 窗批二』节（行级零丢失校验·cycle-2 水位律当窗整编）。")
merged = o[: n - 1] + [ptr_new, mine89]
open("CODELY.md", "w", encoding="utf-8", newline="\n").write("\n".join(merged) + "\n")
print(f"  hot layer lines={len(merged)} size={os.path.getsize('CODELY.md')}B")

print("== archive append (migrate 87+88 verbatim -> new section) ==")
sec = ("\n## 坑律归档 2026-09-29 r416-cont bm-a 窗批二（cycle-2 水位律当窗整编：CODELY 并集 10.9KB 超线"
       "-> 八十七/八十八批迁此·行级零丢失校验）\n\n" + b87_o[0] + "\n" + b88_o[0] + "\n")
a = open("research/memory-archive/202609.md", encoding="utf-8").read()
assert b87_o[0] not in a, "batch-87 already in archive (unexpected)"
assert b88_o[0] not in a, "batch-88 already in archive (unexpected)"
open("research/memory-archive/202609.md", "a", encoding="utf-8", newline="\n").write(sec)
achk = open("research/memory-archive/202609.md", encoding="utf-8").read()
assert b87_o[0] in achk and b88_o[0] in achk
print(f"  archive now {len(achk.splitlines())} lines; 87+88 verbatim verified")

# final size gate
sz = os.path.getsize("CODELY.md")
assert sz <= 10240, f"CODELY {sz}B > 10KB hard line"
print(f"RESOLVER-2 DONE (CODELY {sz}B <= 10KB)")
