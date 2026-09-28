"""r408 bm-a rebase conflict resolve: results/token_usage.json
(single UU face). Symmetric per-machine union (r402 law: side picked by
BLOB CONTENT ts, never by identity; both sides printed + asserted before
write). Per-machine key authority: the machine's own latest write wins;
generated = newer side."""
import json
import subprocess

PATH = "results/token_usage.json"


def stage(n):
    r = subprocess.run(["git", "show", f":{n}:{PATH}"],
                       capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"stage {n} read fail: {r.stderr[:200]}")
    return json.loads(r.stdout.decode("utf-8"))


a, b = stage(2), stage(3)
ts_a, ts_b = a.get("generated", ""), b.get("generated", "")
print(f"stage2 generated = {ts_a}")
print(f"stage3 generated = {ts_b}")
assert ts_a and ts_b and ts_a != ts_b, "ts probe failed (identical/empty)"
newer, older = (b, a) if ts_b > ts_a else (a, b)
print(f"newer side = {'stage3' if ts_b > ts_a else 'stage2'} ({ts_b if ts_b > ts_a else ts_a})")

# machines dict union: per key, the value from the side where that
# machine's numbers are authoritative. Attribution probe: the side whose
# `generated` matches that machine's OWN most recent chain write carries
# that machine's fresh key. Machine-of-side attribution comes from the
# lane heartbeat (not identity assumption on rebase direction): the
# newer side (02:12) is the bm-a chain write (bm-a token_meter in the
# r408 S6 chain, 02:12:03); the older side (01:54) is the bm-c round-192
# chain write. Cross-check: the bm-a side must show bm-a report_bytes>0
# growth vs the other side, and vice versa.
mA_new = newer["machines"]; mOld = older["machines"]
print("newer-side machine keys:", sorted(mA_new.keys()))
print("older-side machine keys:", sorted(mOld.keys()))


def pick(machine_key):
    # choose the side carrying the FRESHER value for this machine:
    # the machine's own write is on the side whose chain ran last FOR
    # THAT MACHINE. Attribution: bm-a side = the 02:12:03 write (this
    # box's S6 chain); bm-c side = the 01:54:24 write (bm-c r192).
    # Symmetric-content check: report_bytes on own side must be >= the
    # other side's copy (fresh append grows the byte count).
    cand_new, cand_old = mA_new.get(machine_key), mOld.get(machine_key)
    if cand_new is None and cand_old is None:
        return None
    if cand_new is None:
        return ("old", cand_old)
    if cand_old is None:
        return ("new", cand_new)
    rb_new = cand_new.get("report_bytes", 0)
    rb_old = cand_old.get("report_bytes", 0)
    return ("new", cand_new) if rb_new >= rb_old else ("old", cand_old)


machines = {}
attribution = {}
for k in sorted(set(mA_new) | set(mOld)):
    r = pick(k)
    if r is None:
        continue
    side, val = r
    machines[k] = val
    attribution[k] = side

resolved = dict(newer)          # newer top-level (generated/method/order)
resolved["machines"] = machines
print("attribution:", attribution)

tmp = PATH + ".resolved.tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(resolved, fh, ensure_ascii=False, indent=1)
back = json.load(open(tmp, encoding="utf-8"))
assert set(back["machines"]) == set(mA_new) | set(mOld), "key loss"
assert back["generated"] == (ts_b if ts_b > ts_a else ts_a)
print("resolved ok:", back["generated"], sorted(back["machines"]))
import os
os.replace(tmp, PATH)
print("written:", PATH)
