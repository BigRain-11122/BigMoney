"""r514 bm-a: update T-140 ticket progress (action-4 runner+probe+pool
registration done this round; burn in flight via daemon). Format-mirror
write (probe indent/EOL first -- r289 law)."""
import json

P = "fleet/tasks/T-2026-10-01-140-P1.json"
raw = open(P, "rb").read()
crlf = b"\r\n" in raw
t = json.loads(raw.decode("utf-8"))
ind1 = open(P, encoding="utf-8").readline()
ind = 1  # probe: measure second line indent
lines = raw.decode("utf-8").splitlines()
for l in lines[1:]:
    if l.strip().startswith('"'):
        ind = len(l) - len(l.lstrip(" "))
        break
trailing = raw.endswith(b"\n")

t["progress"] = (
    t["progress"]
    + " ACTION-4 EXECUTION (bm-a r514 loop adoption, 2026-10-01 12:3x-13:2x): "
    "(a) runner scripts/lowamp_p2.py built copy-adapt from lowamp_p1.py "
    "(sec.0.6 exit-axis HOLD-THROUGH -- engine default exit stack disabled "
    "key-by-key in run_cell_portfolio params: take_profit_levels=() / "
    "trailing_stop_activate=1e12 / initial_stop=-1.0 / time_decay_period=1e9 "
    "/ loss_time_days=1e9 / global_hard_limit=1e9, engine/ zero-touch; "
    "selftest 10/10; seeds 20334500/20333500; r494 real-run law satisfied by "
    "live probe) -- commit 7a8acfb37 (rebased; freeze lineage c3c825c2a); "
    "(b) D6 probe PASS 14/14 in 13.2s: hold-through fresh face max|corr|="
    "0.1738 vs 0.7 reject -> ADMIT (P1 pre-void face was 0.1688; exit-axis "
    "change measured fresh per prereg sec.1) -> results/lowamp_p2/probe.json; "
    "(c) pool +18 entries registered raw-text surgical (16 cell-shards + "
    "NULLS + SENS; ids+shard-keys verified against runner _entry_of 18/18 "
    "after catching an LA-REP/LAREP key-drift near-miss pre-push); "
    "(d) ignition LIVE: daemon claim-to-saturation burning (LAREP legacy "
    "base+x2 done ~50s/shard, fleet joining). REMAINING: (e) finalize after "
    "shards complete (append_ledger batch_trials=2008 + sec.7/sec.8 "
    "backfill + E1 known-answer reconciliation r492 law BEFORE consuming "
    "verdict) -- next round(s)."
)

out = json.dumps(t, ensure_ascii=False, indent=ind)
if crlf:
    out = out.replace("\n", "\r\n")
if trailing and not out.endswith("\r\n" if crlf else "\n"):
    out += "\r\n" if crlf else "\n"
open(P, "wb").write(out.encode("utf-8"))
back = json.load(open(P, encoding="utf-8"))
assert back == t, "parse-verify failed"
print(f"ticket updated (indent={ind}, crlf={crlf}, trailing={trailing})")
