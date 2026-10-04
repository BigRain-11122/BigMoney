"""r481 bm-c: W3 screen 4-shard pool enrollment per MASS_TRIAL_W3_PREREG.md
sec.6 (FROZEN r480 commit c2141d6c1). Raw-text surgical per r678 law
(json round-trip of runnable_pool.json is NOT byte-stable -> line surgery,
reparse + count + difflib assertions). Coverage-tile guard per r670 law:
bounds contiguity == exact tiling of [0, n_rows). Anti-double-enroll gate.
Facts derive from generate products committed same commit (deps green on all
machines post-merge). Evidence -> results/_r481bmc_w3_screen_enroll.json."""
import datetime
import difflib
import hashlib
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
EVID = os.path.join(ROOT, "results", "_r481bmc_w3_screen_enroll.json")
MT = os.path.join(ROOT, "results", "mass_trial")

now_dt = datetime.datetime.now().astimezone()
now = now_dt.strftime("%Y-%m-%d %H:%M:%S")
now_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")

# --- facts from generate products (authoritative, zero hand-copy) ---
cands = json.load(open(os.path.join(MT, "w3_candidates.json"), encoding="utf-8"))
summ = json.load(open(os.path.join(MT, "w3_generate_summary.json"), encoding="utf-8"))
rost = json.load(open(os.path.join(MT, "w3_roster.json"), encoding="utf-8"))
assert cands["batch"] == summ["batch"] == rost["batch"] == "MASS_TRIAL_W3"
n_cand = len(cands["candidates"])
assert n_cand == cands["n"] == summ["enrolled"] == 4814, n_cand
n_fam = len(rost["roster"])
assert n_fam == summ["families"] == 75, n_fam
n_null = 20                      # RLSL iron rule, _combined_rows fixed count
n_rows = n_cand + n_fam + n_null  # == len(_combined_rows(ctx, 3))
assert n_rows == 4909, n_rows
assert summ["evidence_cutoff"] == "2026-09-22"
cw = summ["cross_wave_param_dupes"] + summ["cross_wave_signal_dupes"]
assert cw == 1274, cw
cw_flag_over_band = cw > 600      # sec.5.6: >600 -> honest disclosure + mechanism review

# --- shard bounds: exact tiling of [0, n_rows) per r670 coverage guard ---
NSH = 4
base = n_rows // NSH
bounds = [(i * base, n_rows if i == NSH - 1 else (i + 1) * base)
          for i in range(NSH)]
assert bounds[0][0] == 0 and bounds[-1][1] == n_rows
assert all(bounds[i][1] == bounds[i + 1][0] for i in range(NSH - 1))
sizes = [b - a for a, b in bounds]
assert sum(sizes) == n_rows and min(sizes) >= base - 1

# --- pool state + anti-double-enroll gate ---
raw = open(POOL, encoding="utf-8", newline="").read()
data = json.loads(raw)
entries = data["entries"]
n_before = len(entries)
assert not any(str(e.get("id", "")).startswith("MASS-TRIAL-W3-SCREEN")
               for e in entries), "W3-SCREEN already enrolled (anti-double gate)"
try:
    rt = json.dumps(data, indent=1, ensure_ascii=False)
    roundtrip_stable = (rt + ("\n" if raw.endswith("\n") else "")) == raw
except Exception:
    roundtrip_stable = False

ticket = ("T-2026-10-03-158 W3 stage-1 screen slice (O-2026-09-27-2250 trial-labor standing law "
          "+ O-20261004-1440 sec.3 supply pre-position CEO order; prereg FROZEN r480 commit "
          "c2141d6c1 R99 freeze-before-burn; generate LANDED r480 detached pid 3484 "
          "15:18:49->15:38:03: enrolled 4814/75 families, cross-wave dedup base "
          "w1(975)+w2(4836)=5811, cross-wave elim 916 param + 358 signal = 1274 "
          "(sec.5.6 >600 band -> mechanism review disclosed; rate 21.9% vs w2 28.6% = "
          "base-growth-consistent), quota_short 3 families honest ceiling-not-quota)")
prereg = ("research/MASS_TRIAL_W3_PREREG.md sec.6 screen pool face FROZEN r480 commit c2141d6c1 "
          "(4 shards, pos bounds from actual n=4909 combined rows = 4814 candidates + 75 "
          "controls + 20 nulls; screen_pass = beat_rate_6m >= 0.60 AND n_trades >= 30 AND "
          "max_drawdown >= -0.35 per sec.4; w2-stack engine face RW-1/RW-3; evidence_cutoff "
          "2026-09-22 D2 lockbox; screen finalize = separate round work after 4/4 shards done)")

new_entries = []
for i, (a, b) in enumerate(bounds):
    new_entries.append({
        "id": "MASS-TRIAL-W3-SCREEN-SHARD-%d" % i,
        "ticket_ref": ticket,
        "prereg_ref": prereg,
        "runner": "scripts/mass_trial_w1.py",
        "runner_args": ["screen", "--wave", "3", "--pos-from", str(a), "--pos-to", str(b)],
        "lane_owner": None,
        "priority": 1,
        "status": "ready",
        "entered_at": now_iso,
        "workers_plan": {
            "workers": "worker_cap() pool BelowNormal (O-1136 CPU 10% reserve law; machine-derived cap)",
            "priority": "BelowNormal",
            "note": ("rows [%d:%d) of %d = %d rows x ~6.4s/row w2-measured single-core -> "
                     "~%.1fh serial, ~6-11min wall at worker_cap() workers; per-row jsonl "
                     "checkpoint w3_screen_checkpoint.jsonl append-only single-file "
                     "multi-writer (w2 three-executor relay proven safe, finalize dedups by id); "
                     "done-flip duty = burner-side session adopts per r488/r489 two-layer law"
                     % (a, b, n_rows, b - a, (b - a) * 6.4 / 3600.0)),
        },
        "data_gates": ("in-runner fail-closed exit 2: w3_candidates.json + w3_roster.json required "
                       "(committed r481 SAME commit as this enrollment = deps green on all "
                       "machines post-merge), core48 panel in-repo, evidence_cutoff 2026-09-22 "
                       "D2 lockbox (engine face identical to w2 screen stack RW-1/RW-3)"),
        "data_deps": ["results/mass_trial/w3_candidates.json",
                      "results/mass_trial/w3_roster.json",
                      "data/daily/"],
        "shards": [{
            "key": "w3-screen-%dof4" % i,
            "status": "ready",
            "checkpoint": ("results/mass_trial/w3_screen_checkpoint.jsonl (append-per-row; "
                           "multi-writer safe w2 relay-proven; finalize gate refuses missing ids)"),
            "note": ("rows [%d:%d) of %d combined rows; multi-machine shard-claim legal "
                     "(ticket lock holds science face only); stale-owner takeover >20min per "
                     "fleet law; wave-level screen finalize = separate round work "
                     "(--wave 3 finalize after 4/4 + completeness probe)" % (a, b, n_rows)),
        }],
        "entered_by": "bm-c r481",
        "worker_class": "self-contained",
    })

# --- raw-text surgical insert (r678 law) ---
tail_probe = raw[-200:]
eol = "\r\n" if "\r\n" in tail_probe else "\n"
tail_marker = eol + " ]" + eol + "}"
idx = raw.rfind(tail_marker)
assert idx != -1, "tail marker not found"
pre = raw[:idx]
assert pre.endswith(eol + "  }"), "last entry close shape unexpected: %r" % pre[-10:]


def ser(e):
    t = json.dumps(e, indent=1, ensure_ascii=False)
    return "  " + "\n  ".join(t.split("\n"))


insertion = "," + eol + (("," + eol).join(ser(e) for e in new_entries))
new_raw = pre + insertion + raw[idx:]

# top-level bookkeeping lines (updated_at + _stamp_note) -- line-surgery on
# keepends lines (file is CRLF: regex $ collides with trailing \r; the exact
# 1-space line head is unique -- entries carry own updated_at at 3-space
# indent which does not match the 1-space startswith)
lines = new_raw.splitlines(True)
ua_idx = [k for k, ln in enumerate(lines)
          if ln.startswith(' "updated_at":')]
assert len(ua_idx) == 1, "updated_at line count=%d" % len(ua_idx)
lines[ua_idx[0]] = ' "updated_at": "%s",%s' % (now_iso, eol)
sn_idx = [k for k, ln in enumerate(lines)
          if ln.startswith(' "_stamp_note":')]
assert len(sn_idx) == 1, "stamp_note line count=%d" % len(sn_idx)
stamp = ('r481 bm-c W3 screen enrollment: +4 entries MASS-TRIAL-W3-SCREEN-SHARD-0..3 '
         '(n_rows 4909 = 4814 cand + 75 ctrl + 20 null; bounds %s; prereg sec.6 frozen '
         'c2141d6c1; cross-wave dedup 1274 >600 band disclosed per sec.5.6)'
         % "; ".join("[%d,%d)" % (a, b) for a, b in bounds))
stamp_json = json.dumps(stamp, ensure_ascii=False)
lines[sn_idx[0]] = ' "_stamp_note": %s,%s' % (stamp_json, eol)
new_raw = "".join(lines)

# --- post-surgery assertions ---
data2 = json.loads(new_raw)
ids2 = [str(e.get("id", "")) for e in data2["entries"]]
assert len(ids2) == n_before + 4, len(ids2)
for i, (a, b) in enumerate(bounds):
    e = next(x for x in data2["entries"]
             if x.get("id") == "MASS-TRIAL-W3-SCREEN-SHARD-%d" % i)
    assert e["runner_args"] == ["screen", "--wave", "3",
                                "--pos-from", str(a), "--pos-to", str(b)]
    assert e["status"] == "ready" and e["shards"][0]["status"] == "ready"
    assert e["worker_class"] == "self-contained" and e["lane_owner"] is None
old_ids = [str(e.get("id", "")) for e in entries]
assert all(ids2.count(i) == 1 for i in old_ids), "old entry lost/duplicated"
diff = list(difflib.unified_diff(raw.splitlines(), new_raw.splitlines(),
                                 lineterm="", n=0))
added = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
assert removed == 2, "expected exactly 2 replaced top-level lines, got %d" % removed

with open(POOL, "w", encoding="utf-8", newline="") as f:
    f.write(new_raw)
data3 = json.loads(open(POOL, encoding="utf-8").read())
assert len(data3["entries"]) == n_before + 4

sha = hashlib.sha256(open(os.path.join(MT, "w3_candidates.json"), "rb").read()).hexdigest()
ev = {
    "round": "r481 bm-c",
    "ts": now_iso,
    "n_candidates": n_cand, "n_families": n_fam, "n_nulls": n_null,
    "n_rows": n_rows, "bounds": bounds, "sizes": sizes,
    "candidates_sha256_16": sha[:16],
    "cross_wave_elim": cw, "cross_wave_over_600_band": cw_flag_over_band,
    "quota_short": summ["quota_short"],
    "pool_entries_before": n_before, "pool_entries_after": n_before + 4,
    "new_ids": ["MASS-TRIAL-W3-SCREEN-SHARD-%d" % i for i in range(NSH)],
    "roundtrip_stable": roundtrip_stable,
    "diff_added_lines": added, "diff_removed_lines": removed,
    "eol_detected": repr(eol),
    "prereg": "research/MASS_TRIAL_W3_PREREG.md sec.6 frozen r480 c2141d6c1",
}
with open(EVID, "w", encoding="utf-8") as f:
    json.dump(ev, f, ensure_ascii=False, indent=1)
print("ENROLL OK: +4 W3-SCREEN shards, n_rows=%d bounds=%s, pool %d->%d, "
      "cw_elim=%d (>600 disclosed), added=%d removed=%d"
      % (n_rows, bounds, n_before, n_before + 4, cw, added, removed))
