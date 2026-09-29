# r444 bm-b rebase pool-flip union: mine = TRIAL-LABOR-W11-JUDGE ready->done
# (dead-round bookkeeping closure); origin side (bm-c r246) = INNOVATION-
# QUOTA-SLOT-4 ready->done surgical flip + last_tick 02:18:02 drift.  Different
# entries + different top fields -> surgical overlay of my flipped entry onto
# the origin side, both flips preserved, entry count and order preserved.
import json, subprocess, io, sys

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
PATH = "results/runnable_pool.json"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def blob(n):
    r = subprocess.run(["git", "show", ":%d:%s" % (n, PATH)],
                       capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode("utf-8", "replace"))
    return json.loads(r.stdout.decode("utf-8"))

ours, theirs = blob(2), blob(3)
assert len(ours["entries"]) == len(theirs["entries"]), "entry count drift"

mine = [e for e in theirs["entries"] if e.get("id") == "TRIAL-LABOR-W11-JUDGE"]
assert len(mine) == 1 and mine[0].get("status") == "done", "my flip missing"
origin_slot4 = [e for e in ours["entries"] if e.get("id") == "INNOVATION-QUOTA-SLOT-4"]
assert len(origin_slot4) == 1 and origin_slot4[0].get("status") == "done", "bm-c slot4 flip missing"

out_entries = []
for e in ours["entries"]:
    if e.get("id") == "TRIAL-LABOR-W11-JUDGE":
        assert e.get("status") == "ready", "origin side unexpectedly touched my entry"
        out_entries.append(mine[0])
    else:
        out_entries.append(e)
ours["entries"] = out_entries

ids_done = [e["id"] for e in out_entries if e.get("status") == "done"]
assert "TRIAL-LABOR-W11-JUDGE" in ids_done and "INNOVATION-QUOTA-SLOT-4" in ids_done
assert len([e for e in out_entries if e.get("status") == "ready"]) == 0, "ready faces remain"

data = json.dumps(ours, ensure_ascii=False, indent=1) + "\n"
json.loads(data)
io.open(REPO + "\\" + PATH, "w", encoding="utf-8", newline="\n").write(data)
print("pool union done: entries=%d, W11-JUDGE done + SLOT-4 done both present, "
      "last_tick kept from origin side, zero ready faces" % len(out_entries))
