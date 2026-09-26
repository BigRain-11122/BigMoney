"""r295 bm-b S0-uu rebase resolver (round-close commit replay vs bm-a r292 closeout).

Canonical recipes:
- 14 generated mirrors -> LWW whole-file (mine 04:12-04:15 > upstream 04:00-04:01,
  and mine carries the re-anchored head 198,389; R148 generated_at LWW law).
  Handled by caller via `git checkout --theirs` BEFORE this script.
- results/autofill_state.json -> launches union cap50 ASC (r245) + last_tick newer
  internal ts (r140; tie -> upstream).
- CODELY.md -> conflict-block union: bm-a [04:1x] entry first, mine [04:2x] second
  (r281 append-union law); then hot-cold reorg if over the 10240B hard line:
  migrate the oldest flow-type entry ([03:0x] execution record) verbatim to
  research/memory-archive/202609.md per O-20260927-0230 <=10KB discipline.
"""
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def stage(n, path):
    out = subprocess.run(["git", "show", ":%d:%s" % (n, path)], capture_output=True,
                         cwd=ROOT)
    assert out.returncode == 0, (n, path, out.stderr[:200])
    return out.stdout.decode("utf-8")


# ---- autofill_state union -------------------------------------------------
P = "results/autofill_state.json"
up = json.loads(stage(2, P))
mine = json.loads(stage(3, P))


def sig(launch):
    return json.dumps({k: launch.get(k) for k in ("ts", "entry", "machine", "pid",
                                                   "shard")}, sort_keys=True)


merged = {}
for l in up.get("launches", []) + mine.get("launches", []):
    merged[sig(l)] = l
launches = sorted(merged.values(), key=lambda l: str(l.get("ts", "")))
dropped = max(0, len(launches) - 50)
launches = launches[-50:]
lt_u, lt_m = up.get("last_tick", {}), mine.get("last_tick", {})
last_tick = lt_u if str(lt_u.get("ts", "")) >= str(lt_m.get("ts", "")) else lt_m
state = {**mine, "launches": launches, "last_tick": last_tick}
if "note" in up and "note" not in state:
    state["note"] = up["note"]
with open(os.path.join(ROOT, P), "w", encoding="utf-8", newline="\n") as fh:
    json.dump(state, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("autofill_state: launches union %d+%d -> %d (dropped oldest %d), last_tick ts=%s machine=%s" % (
    len(up.get("launches", [])), len(mine.get("launches", [])), len(launches), dropped,
    last_tick.get("ts"), last_tick.get("machine")))

# ---- CODELY union + hot-cold reorg ---------------------------------------
CP = "CODELY.md"
raw = open(os.path.join(ROOT, CP), "rb").read().decode("utf-8")
m = re.search(r"<<<<<<< HEAD\r?\n(.*?)\r?\n=======\r?\n(.*?)\r?\n>>>>>>> [^\r\n]*\r?\n",
              raw, re.S)
assert m, "CODELY conflict block not found"
head_entry, my_entry = m.group(1), m.group(2)
raw = raw[:m.start()] + head_entry + "\n" + my_entry + "\n" + raw[m.end():]
assert ">>>>>>> " not in raw and "<<<<<<< " not in raw

migrated = None
size = len(raw.encode("utf-8"))
if size > 10240:
    mm = re.search(r"- \[2026-09-27 03:0x\] 执行记录（[^\n]*\n", raw)
    if mm:
        migrated = mm.group(0)
        raw = raw[:mm.start()] + raw[mm.end():]
size = len(raw.encode("utf-8"))
with open(os.path.join(ROOT, CP), "wb") as fh:
    fh.write(raw.encode("utf-8"))
print("CODELY: union both entries (bm-a 04:1x + bm-b 04:2x), size=%d B (line=%d)" % (size, 10240))
assert size <= 10240, "CODELY over 10KB hard line even after reorg: %d" % size

if migrated:
    AP = os.path.join(ROOT, "research", "memory-archive", "202609.md")
    with open(AP, "ab") as fh:
        fh.write(("\n" + migrated.rstrip("\r\n") +
                  "（r295 bm-b 热冷整编迁自 CODELY.md·行级零丢失·O-20260927-0230 硬线）\n").encode("utf-8"))
    print("archive: migrated execution-record entry -> research/memory-archive/202609.md")
print("RESOLVE OK")
