"""r298 bm-b rebase step 1/2 UU resolver: results/runnable_pool.json (UNKNOWN class,
hand-qualified per SKILL fail-closed law). Facts (three-way structural diff):
all three stages hold identical 55-entry sets; exactly ONE entry differs from
base on each side -- CN-KLINE-PATTERN-P1. Upstream (e0fed5e9, ours-in-rebase)
= bm-a salvage done-flip (terminal state, full products committed, judged 7/7
negative, slot closed). Replay side (577c4beb, theirs-in-rebase) = bm-b
autofill tick claim of the same entry -- already superseded: the local
watchdog itself recorded verdict=claim_lost_yield for CN-KLINE-PATTERN-P1
run-0of1 at 04:50:01 (autofill_state last_tick), i.e. our lane yielded the
claim. Resolution = take upstream done-flip verbatim (byte-identical), claim
history preserved in autofill_state.json launches ledger (zero-loss face).
"""
import io
import json
import subprocess

PATH = "results/runnable_pool.json"


def blob(stage):
    return subprocess.run(
        ["git", "show", f":{stage}:{PATH}"],
        capture_output=True, check=True).stdout


b_base, b_ours, b_theirs = blob(1), blob(2), blob(3)
base, ours, theirs = (json.loads(b.decode("utf-8-sig"))
                      for b in (b_base, b_ours, b_theirs))


def key(e):
    return e.get("id") or json.dumps(e, ensure_ascii=False, sort_keys=True)


ib = {key(e): e for e in base["entries"]}
io_ = {key(e): e for e in ours["entries"]}
it = {key(e): e for e in theirs["entries"]}
assert set(ib) == set(io_) == set(it), "entry-set drift beyond single entry"

diff_o = sorted(k for k in io_ if json.dumps(io_[k], sort_keys=True)
                != json.dumps(ib[k], sort_keys=True))
diff_t = sorted(k for k in it if json.dumps(it[k], sort_keys=True)
                != json.dumps(ib[k], sort_keys=True))
assert diff_o == ["CN-KLINE-PATTERN-P1"], diff_o
assert diff_t == ["CN-KLINE-PATTERN-P1"], diff_t

oe = io_["CN-KLINE-PATTERN-P1"]
te = it["CN-KLINE-PATTERN-P1"]
assert str(oe.get("status", "")).lower() == "done", oe.get("status")

od = {k: v for k, v in oe.items()
      if json.dumps(v, sort_keys=True) != json.dumps(te.get(k), sort_keys=True)}
td = {k: v for k, v in te.items()
      if json.dumps(v, sort_keys=True) != json.dumps(oe.get(k), sort_keys=True)}
print("upstream-done delta fields :", json.dumps(od, ensure_ascii=False)[:400])
print("replay-claim delta fields  :", json.dumps(td, ensure_ascii=False)[:400])

# resolution: upstream done-flip verbatim (byte-identical write, zero format drift)
with io.open(PATH, "wb") as f:
    f.write(b_ours)

chk = json.load(io.open(PATH, encoding="utf-8-sig"))
ce = {key(e): e for e in chk["entries"]}["CN-KLINE-PATTERN-P1"]
assert str(ce.get("status", "")).lower() == "done", ce
assert len(chk["entries"]) == 55
print("RESOLVED: runnable_pool.json == upstream done-flip verbatim; "
      "CN-KLINE-PATTERN-P1 done (products committed upstream); bm-b claim "
      "superseded (watchdog claim_lost_yield 04:50:01), history preserved in "
      "autofill_state launches -- zero loss")
