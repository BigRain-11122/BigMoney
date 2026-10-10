# _r837bmb_w17_handover.py -- O-20261010-1825 sec.2.1 W17 screen shard 1-4 handover surgery (bm-c -> bm-b)
# Laws: pit-pool-edit r509 (raw-text needle surgery, no re-serialization), r694 (needle anchored to
#       entry region + count==1), r629 (reparse gate), r859 (parse gate before... for edits: after),
#       r457 (local==origin identity pre-gate), r692 (shard layer = claim truth).
# Scope: entries TRIAL-LABOR-W17-SCREEN-SHARD-1..4 only. lane_owner bm-c->bm-b, shard owner bm-c->bm-b,
#        owner_since -> now. Shards 5-7 untouched (bm-c keeps burning in parallel), shard-0 untouched (live burn).
import json, subprocess, sys, datetime

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
POOL = REPO + r"\results\runnable_pool.json"
SHARDS = [1, 2, 3, 4]
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def git(*args):
    r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git %s rc=%d" % (args, r.returncode))
    return r.stdout

# 0. identity gate: local pool == origin blob (r457)
origin = git("show", "origin/main:results/runnable_pool.json")
local = open(POOL, "rb").read()
if local != origin:
    print("IDENTITY_FAIL: local pool != origin blob (local=%dB origin=%dB)" % (len(local), len(origin)))
    sys.exit(1)
print("IDENTITY_OK local==origin %dB" % len(local))

text = local.decode("utf-8")
edits = []
for k in SHARDS:
    eid = '"id": "TRIAL-LABOR-W17-SCREEN-SHARD-%d"' % k
    p = text.find(eid)
    if p < 0:
        print("NEEDLE_FAIL: entry id not found for shard %d" % k)
        sys.exit(1)
    nxt = text.find('"id": "', p + 10)
    region = text[p:nxt if nxt > 0 else len(text)]
    for old, new in (
        ('"lane_owner": "bm-c"', '"lane_owner": "bm-b"'),
        ('"owner": "bm-c"', '"owner": "bm-b"'),
        ('"owner_since": "2026-10-10 19:04:03"', '"owner_since": "%s"' % NOW),
    ):
        c = region.count(old)
        if c != 1:
            print("NEEDLE_FAIL: shard %d needle count=%d for %r" % (k, c, old))
            sys.exit(1)
        edits.append((p, nxt, old, new, k))

# apply edits from last to first (stable offsets)
new_text = text
for p, nxt, old, new, k in reversed(edits):
    region = new_text[p:nxt if nxt > 0 else len(new_text)]
    assert region.count(old) == 1
    new_text = new_text[:p] + region.replace(old, new, 1) + new_text[nxt if nxt > 0 else len(new_text):]

# parse gate before write (r859 mirror for edits)
json.loads(new_text)
# semantic assertion: the 4 entries now carry bm-b, others untouched
d = json.loads(new_text)
for i in d.get("entries", []):
    if i.get("id", "").startswith("TRIAL-LABOR-W17-SCREEN-SHARD-"):
        sh = i.get("shards", [{}])[0]
        print(i["id"], "lane=", i.get("lane_owner"), "owner=", sh.get("owner"), "since=", sh.get("owner_since"))

if new_text.encode("utf-8") == local:
    print("NO_CHANGE_ABORT")
    sys.exit(1)

open(POOL, "wb").write(new_text.encode("utf-8"))
# post-write reparse + diff assertion
json.loads(open(POOL, "rb").read().decode("utf-8"))
r = subprocess.run(["git", "-C", REPO, "diff", "--numstat", "--", "results/runnable_pool.json"],
                   capture_output=True)
out = r.stdout.decode()
print("NUMSTAT:", out.strip())
ins = sum(int(l.split("\t")[0]) for l in out.strip().splitlines() if l)
dele = sum(int(l.split("\t")[1]) for l in out.strip().splitlines() if l)
if ins != 12 or dele != 12:
    print("SURGICAL_ASSERT_FAIL: expected 12/12 got %d/%d" % (ins, dele))
    sys.exit(1)
print("SURGERY_OK 12/12 surgical lines, now=%s" % NOW)
