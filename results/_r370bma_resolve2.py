# r370 bm-a: autofill_state.json UU resolver (mixed-dict+ledger canon r203/r322/r245/r140).
# ours=:2: (rebase HEAD side = my tick adoption), theirs=:3: (origin-applied side).
# launches: identity union on composite key (ts,machine,pid,runner_sha256,entry,shard);
# same-key pair: field-union merge if only additive, else flag+keep both is FORBIDDEN -> keep theirs+note.
# cap 50 newest by ts, write back sorted ascending (producer append order, r245).
# last_tick: compare inner ts, whole-dict assign, same-second tie -> HEAD/ours (r140).
import json, subprocess

F = "results/autofill_state.json"
KEY = ("ts", "machine", "pid", "runner_sha256", "entry", "shard")

def stage(n):
    b = subprocess.run(["git", "show", f":{n}:{F}"], capture_output=True).stdout
    return json.loads(b.decode("utf-8")), b

ours, ob = stage(2)
theirs, tb = stage(3)
crlf = b"\r\n" in ob or b"\r\n" in tb

def k(e):
    return tuple(e.get(x) for x in KEY)

# --- launches union ---
lo, lt = ours.get("launches") or [], theirs.get("launches") or []
by_key = {}
notes = []
for e in lo + lt:
    kk = k(e)
    if kk not in by_key:
        by_key[kk] = dict(e)
    else:
        old = by_key[kk]
        if old == e:
            continue
        keys_o, keys_t = set(old), set(e)
        if keys_o | keys_t == keys_t or keys_o | keys_t == keys_o:
            merged = dict(old); merged.update(e)
            by_key[kk] = merged
        else:
            by_key[kk] = dict(e)  # true divergence on same composite key: keep theirs (last write)
            notes.append(f"same-key divergence merged-lastwrite ts={e.get('ts')}")
launches = sorted(by_key.values(), key=lambda x: x.get("ts") or "")
launches = launches[-50:] if len(launches) > 50 else launches  # cap 50 newest

# --- last_tick: max inner ts, tie -> ours ---
lt_o, lt_t = ours.get("last_tick") or {}, theirs.get("last_tick") or {}
ts_o, ts_t = lt_o.get("ts"), lt_t.get("ts")
if ts_t is None:
    last_tick = lt_o
elif ts_o is None:
    last_tick = lt_t
else:
    last_tick = lt_o if str(ts_o) >= str(ts_t) else lt_t
assert isinstance(last_tick, dict), "last_tick must be dict (r140)"

merged = {}
for src in (ours, theirs):
    for kk, vv in src.items():
        if kk not in merged:
            merged[kk] = vv
merged["launches"] = launches
merged["last_tick"] = last_tick
if "notes" in merged and isinstance(merged["notes"], list):
    merged["notes"] = list(merged["notes"]) + notes

text = json.dumps(merged, ensure_ascii=False, indent=1)
if crlf:
    text = text.replace("\n", "\r\n")
with open(F, "wb") as f:
    f.write(text.encode("utf-8"))
chk = json.loads(open(F, "rb").read().decode("utf-8"))
assert isinstance(chk["last_tick"], dict)
print(f"launches union |A|={len(lo)} |B|={len(lt)} -> {len(launches)} (cap50 asc); "
      f"last_tick ts={last_tick.get('ts')} tie->HEAD={str(ts_o) >= str(ts_t)}; notes={notes or 0}")
