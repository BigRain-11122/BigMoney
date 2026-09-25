"""r231 S0 stash-pop UU resolver: results/autofill_state.json (mixed-dict+ledger, classifier GREEN).

Sides:
  ours   (:2) = HEAD a2525584 (bm-a R228 face)
  theirs (:3) = stashed r230-tail (bm-b face, launched runner record)
Recipe (SKILL.md mixed-dict+ledger): launches = union by (ts,entry,machine,pid) key -> sort ts -> cap 50
  (R215 rolling window); last_tick = compare inner ts then assign WHOLE dict (r203 no-str law);
  same-second tie -> ours/HEAD (r140); write back mirroring working-tree CRLF (bm-b r223);
  parse-verify before add (r185). Zero-loss: assert union row count == |A union B|.
"""
import json, subprocess, sys

PATH = "results/autofill_state.json"

def blob(stage):
    raw = subprocess.run(["git", "show", f":{stage}:{PATH}"], capture_output=True, check=True).stdout
    return json.loads(raw.decode("utf-8"))

ours, theirs = blob(2), blob(3)
print("ours last_tick   :", repr(ours.get("last_tick")))
print("theirs last_tick :", repr(theirs.get("last_tick")))
lo, lt = ours.get("launches", []), theirs.get("launches", [])
print(f"launches ours={len(lo)} theirs={len(lt)}")

# --- launches union: dedupe by stable identity key, sort by ts, cap 50 ---
def key(e):
    return (e.get("ts"), e.get("entry"), e.get("machine"), e.get("pid"), e.get("shard"))

merged = {}
for e in lo + lt:  # ours first -> same-key ours wins (identical semantics)
    merged[key(e)] = e
union = sorted(merged.values(), key=lambda e: e.get("ts", ""), reverse=True)
assert len(union) == len(merged), "union row count must equal dedup map size"
lost = len(merged) - min(50, len(merged))
union = union[:50]  # R215 cap
print(f"union={len(union)} (dropped {lost} oldest beyond cap50)")

# --- last_tick: inner-ts compare, whole-dict assign, tie -> ours (r140) ---
lt_o, lt_t = ours.get("last_tick") or {}, theirs.get("last_tick") or {}
ts_o, ts_t = lt_o.get("ts") or "", lt_t.get("ts") or ""
if ts_t > ts_o:
    last_tick = lt_t
elif ts_t < ts_o:
    last_tick = lt_o
else:
    last_tick = lt_o  # tie -> HEAD/ours
assert isinstance(last_tick, dict), "last_tick must remain a dict (r203 type law)"
print("picked last_tick :", repr(last_tick))

# --- other keys: ours face, theirs override only if it has keys ours lacks ---
out = dict(ours)
for k, v in theirs.items():
    if k not in out:
        out[k] = v
        print(f"key adopted from theirs: {k}")
out["launches"] = union
out["last_tick"] = last_tick

# --- CRLF mirror (bm-b r223): probe working-tree bytes of conflicted file for CRLF ---
with open(PATH, "rb") as f:
    has_crlf = b"\r\n" in f.read()
text = json.dumps(out, indent=1, ensure_ascii=False)
if has_crlf:
    text = text.replace("\n", "\r\n")
with open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(text + ("\r\n" if has_crlf else "\n"))

# --- parse-verify (r185) + type asserts ---
with open(PATH, "r", encoding="utf-8") as f:
    back = json.load(f)
assert isinstance(back["last_tick"], dict), "post-write last_tick must be dict"
assert back["last_tick"] == last_tick
assert len(back["launches"]) == len(union)
print("PARSE-VERIFY OK; wrote", PATH)
