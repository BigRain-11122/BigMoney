"""_r256bmb_resolve.py -- R256 S7 push-collision rebase resolver (record copy).

Conflict: replaying bm-b round-256 commit (T-80 adjudication fix) onto
origin/main+replayed-watchdog-commit; UU = results/runnable_pool.json with
TWO both-touched entries needing OPPOSITE takes (split resolution):

  CN-DIV-LOWVOL-ROT-P1  -> take :2: (ours = upstream bm-a r252 harvested
      done face, landed 14:50:53; the local watchdog's 15:00:04 claim was a
      stale-view blind claim against a tree whose push was rejected -- r239
      claim-window family; NO launch ever happened (no launch record, no
      process, empty ckpt), zero duplicate burn, zero ledger double-count)
  T80-AGGR-FULLPOOL-BATTERY -> take :3: (theirs = this round's A1 caliber
      pin: data_gates + adjudication note; bm-b is the T-80 owner)

All other entries/fields: identical across faces (verified by the probe
below before writing). Fail-closed: refuses to write on any unexpected
both-touched entry.
"""
import json
import subprocess
import sys

PATH = "results/runnable_pool.json"


def blob(ref):
    out = subprocess.run(["git", "show", ref], capture_output=True)
    return json.loads(out.stdout.decode("utf-8"))


def main():
    ours, theirs = blob(":2:" + PATH), blob(":3:" + PATH)
    io_ = {e["id"]: e for e in ours["entries"]}
    it_ = {e["id"]: e for e in theirs["entries"]}
    assert set(io_) == set(it_), "entry id sets diverge"
    diffs = [k for k in io_ if io_[k] != it_[k]]
    assert sorted(diffs) == ["CN-DIV-LOWVOL-ROT-P1",
                             "T80-AGGR-FULLPOOL-BATTERY"], \
        f"unexpected both-touched set: {sorted(diffs)}"
    # CN-DIV: upstream harvested face (drop stale local claim)
    cn_div_ours = io_["CN-DIV-LOWVOL-ROT-P1"]
    cn_div_theirs = it_["CN-DIV-LOWVOL-ROT-P1"]
    assert cn_div_ours["status"] == "done" and \
        cn_div_ours["shards"][0]["owner"] == "bm-a", "upstream face sanity"
    assert cn_div_theirs["status"] == "ready" and \
        cn_div_theirs["shards"][0]["owner"] == "bm-b", "claim face sanity"
    # T80: this round's A1 fix face
    t80_theirs = it_["T80-AGGR-FULLPOOL-BATTERY"]
    assert "A1 caliber pin" in t80_theirs["data_gates"], "A1 gates missing"
    assert "R256 bm-b adjudication DELIVERED" in t80_theirs["note"]
    merged = dict(ours)
    entries = []
    for e in ours["entries"]:
        if e["id"] == "T80-AGGR-FULLPOOL-BATTERY":
            entries.append(t80_theirs)     # take ours(=this round's) face
        else:
            entries.append(e)             # upstream face (incl. CN-DIV done)
    merged["entries"] = entries
    with open(PATH, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(merged, fh, indent=1, ensure_ascii=False)
    # post-write validation
    with open(PATH, encoding="utf-8") as fh:
        check = json.load(fh)
    ids = [e["id"] for e in check["entries"]]
    assert len(ids) == len(set(ids)) == 46, "entry census broke"
    got_cn = [e for e in check["entries"]
              if e["id"] == "CN-DIV-LOWVOL-ROT-P1"][0]
    got_t80 = [e for e in check["entries"]
               if e["id"] == "T80-AGGR-FULLPOOL-BATTERY"][0]
    assert got_cn["status"] == "done" and \
        got_cn["shards"][0]["owner"] == "bm-a", "CN-DIV resolution lost"
    assert "A1 caliber pin" in got_t80["data_gates"], "T80 A1 lost"
    print("resolver: pool merged (CN-DIV=upstream done/bm-a; "
          "T80=A1 fix face); 46 entries; validation PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
