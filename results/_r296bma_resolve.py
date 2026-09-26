"""R296 bm-a resolver: autostash-pop UU on results/autofill_state.json (mixed-dict+ledger).

Skill recipe (r203/R208/r215/r220): launches = union both sides -> sort ts desc ->
cap 50 (rolling window) -> write back RE-SORTED ts ASC (r245 law); last_tick =
compare inner ts then assign WHOLE dict (same-second tie -> HEAD/ours, r140);
newline mirror base blob; parse-verify BEFORE add (r185); stash dropped after
resolve (r268 no-dangling-stash law); lane file stays UNSTAGED (r290 law).

Sides: ours = HEAD (post-rebase = bm-b r300 face), theirs = autostash (bm-a
watchdog tick face).
"""
import json
import os
import subprocess

PATH = "results/autofill_state.json"


def blob(side):
    return subprocess.run(["git", "show", f":{side}:{PATH}"],
                          capture_output=True).stdout


def parse(b):
    return json.loads(b.decode("utf-8"))


ours = parse(blob(1))       # index stage1 = HEAD
theirs = parse(blob(3))     # index stage3 = stash

# ---- launches union (key = entry identity; dedupe by full-content)
lo, lt = ours.get("launches", []), theirs.get("launches", [])
seen = set()
union = []
for e in lo + lt:
    key = json.dumps(e, sort_keys=True, ensure_ascii=False)
    if key in seen:
        continue
    seen.add(key)
    union.append(e)
union_sorted = sorted(union, key=lambda e: str(e.get("ts", "")), reverse=True)
capped = union_sorted[:50]
capped_asc = sorted(capped, key=lambda e: str(e.get("ts", "")))   # r245: write back ts ASC

# ---- last_tick: inner-ts compare, whole-dict assign; tie -> HEAD
to, tt = ours.get("last_tick"), theirs.get("last_tick")


def ts_of(x):
    return str(x.get("ts", "")) if isinstance(x, dict) else ""


if not isinstance(tt, dict):
    last_tick = to
elif not isinstance(to, dict):
    last_tick = tt
elif ts_of(tt) > ts_of(to):
    last_tick = tt
else:
    last_tick = to          # includes same-second tie -> HEAD (r140)

# ---- other keys: prefer ours (HEAD) face, fill missing from theirs
out = dict(ours)
for k, v in theirs.items():
    if k not in out:
        out[k] = v
out["launches"] = capped_asc
out["last_tick"] = last_tick

# ---- newline mirror of base blob (CRLF producer face)
raw = blob(1)
crlf = b"\r\n" in raw.split(b"\n", 1)[0] + (b"\r\n" if raw.count(b"\r\n") else b"")
ending = "\r\n" if crlf else "\n"
text = json.dumps(out, ensure_ascii=False, indent=1) + ending
if crlf:
    text = text.replace("\n", "\r\n")

with open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(text)

# ---- parse-verify BEFORE add (r185) + structural asserts
d = json.load(open(PATH, encoding="utf-8-sig"))
assert isinstance(d.get("last_tick"), dict), "last_tick not dict"
assert isinstance(d.get("launches"), list), "launches not list"
tss = [str(e.get("ts", "")) for e in d["launches"]]
assert tss == sorted(tss), "launches not ts-ASC after write-back (r245)"
assert len(d["launches"]) <= 50, "cap50 violated"
n_union = len(union)
print(f"resolve OK: launches |ours|={len(lo)} |theirs|={len(lt)} union={n_union} "
      f"capped={len(d['launches'])} (dropped {n_union - len(d['launches'])} oldest)")
print(f"last_tick ours={ts_of(to)} theirs={ts_of(tt)} -> took {ts_of(d['last_tick'])} "
      f"(tie->HEAD law)")
print(f"newline={'CRLF' if crlf else 'LF'}; parse-verify PASS; "
      f"isinstance(last_tick,dict) PASS")
