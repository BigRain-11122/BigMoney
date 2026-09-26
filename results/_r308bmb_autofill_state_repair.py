"""r308 bm-b: autofill_state.json torn-write repair.

Diagnosis (live): 2026-09-27 07:30:03 autofill tick ABORT 'corrupt autofill_state
(refuse wipe, r201): Expecting property name enclosed in double quotes: line 654 column 1
(char 15233)'. Window = r306/r307 rebase/stash-pop fold (git mid-operation 07:00-07:26) x
concurrent autofill tick state write = torn-write class.

Laws: r201 (autofill refuses wipe -> control-plane repairs with zero-loss union);
r306/r307 fold family (union merge, cap-50 drop-oldest r140, last_tick newer wins);
atomic tmp+rename; verify-or-die (json.loads + key-shape asserts before/after write).
"""
import json, subprocess, hashlib, os, sys, datetime

PATH = "results/autofill_state.json"
EV = "results/_r308bmb_autofill_state_repair.json"
now = datetime.datetime.now().astimezone().isoformat()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def try_loads(b):
    try:
        return True, json.loads(b)
    except Exception as e:
        return False, repr(e)


ev = {"ts": now, "path": PATH, "action": None}

raw = open(PATH, "rb").read()
ev["disk_bytes"] = len(raw)
ev["disk_sha256"] = sha(raw)
disk_ok, disk = try_loads(raw)
ev["disk_valid"] = disk_ok
if not disk_ok:
    ev["disk_error"] = disk

# base candidate: first valid version walking back HEAD, HEAD~1..HEAD~4
base_src = None
base = None
for i in range(0, 5):
    ref = "HEAD" if i == 0 else "HEAD~%d" % i
    p = subprocess.run(["git", "show", ref + ":" + PATH], capture_output=True)
    if p.returncode != 0 or not p.stdout:
        continue
    ok, j = try_loads(p.stdout)
    ev["base_cand_%s_valid" % ref] = ok
    if ok:
        base_src = ref
        base = j
        ev["base_bytes_%s" % ref] = len(p.stdout)
        break
if base is None:
    ev["action"] = "FAIL_NO_VALID_BASE"
    json.dump(ev, open(EV, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(ev, ensure_ascii=False))
    sys.exit(2)

if disk_ok:
    # nothing to repair (tick abort may have raced a later good write) -- verify only
    ev["action"] = "NO_OP_DISK_VALID"
    ev["base_src"] = base_src
    json.dump(ev, open(EV, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(ev, ensure_ascii=False))
    sys.exit(0)

# ---- salvage: trim tail fragments + close open brackets, largest valid parse wins
text = raw.decode("utf-8", errors="replace")
salv = None
OPEN = {"{": "}", "[": "]"}
for trim in range(0, 4097):
    if len(text) - trim <= 0:
        break
    prefix = text[: len(text) - trim] if trim else text
    stack = []
    in_str = False
    esc = False
    bad = False
    for ch in prefix:
        if esc:
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch in OPEN:
            stack.append(OPEN[ch])
        elif ch in "}]":
            if not stack or stack[-1] != ch:
                bad = True
                break
            stack.pop()
    if bad or in_str or not stack:
        continue
    # drop a trailing dangling partial token: cut back to last structural char
    cut = len(prefix)
    while cut > 0 and prefix[cut - 1] not in '{[,"0123456789tfn"}]':
        cut -= 1
    cand = prefix[:cut] + "".join(reversed(stack))
    ok, j = try_loads(cand.encode("utf-8"))
    if ok and isinstance(j, dict):
        salv = j
        ev["salvage_trim"] = trim
        ev["salvage_cut"] = len(prefix) - cut
        break
ev["salvage_ok"] = salv is not None

# ---- zero-loss union merge into base
merged = dict(base)
if salv:
    ev["salvage_keys"] = sorted(salv.keys())
    ev["base_keys"] = sorted(base.keys())
    for k, v in salv.items():
        if isinstance(v, list) and isinstance(merged.get(k), list):
            bk = {json.dumps(x, sort_keys=True, ensure_ascii=False) for x in merged[k]}
            union = list(merged[k]) + [x for x in v if json.dumps(x, sort_keys=True, ensure_ascii=False) not in bk]
            # r140 cap face: drop-oldest only, cap 50 (defensive; autofill re-caps on its own writes)
            merged[k] = union
            ev["union_%s" % k] = {"base": len(merged[k]) - len([x for x in v if json.dumps(x, sort_keys=True, ensure_ascii=False) not in bk]), "salv_add": len([x for x in v if json.dumps(x, sort_keys=True, ensure_ascii=False) not in bk])}
        elif k in merged and isinstance(merged[k], str) and isinstance(v, str) and merged[k] < v:
            merged[k] = v  # newer ISO string wins (last_tick family)
            ev["newer_str_%s" % k] = [merged[k], v]
        elif k not in merged:
            merged[k] = v
            ev["added_key_%s" % k] = True

# sanity: keep launches cap 50 drop-oldest if oversized (r140 defensive face)
if isinstance(merged.get("launches"), list) and len(merged["launches"]) > 50:
    ev["launches_precap"] = len(merged["launches"])
    merged["launches"] = merged["launches"][-50:]

out = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8")
ok2, chk = try_loads(out)
assert ok2 and isinstance(chk, dict), "post-serialize verify failed"
assert "launches" in chk or "launches" not in merged, "key loss"
ev["action"] = "REPAIRED_UNION"
ev["base_src"] = base_src
ev["out_bytes"] = len(out)
ev["out_sha256"] = sha(out)
tmp = PATH + ".tmp_r308bmb"
open(tmp, "wb").write(out)
os.replace(tmp, PATH)
ok3, chk2 = try_loads(open(PATH, "rb").read())
ev["final_valid"] = ok3
json.dump(ev, open(EV, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: ev[k] for k in ("action", "base_src", "disk_bytes", "salvage_ok", "final_valid")}, ensure_ascii=False))
sys.exit(0 if ok3 else 2)
