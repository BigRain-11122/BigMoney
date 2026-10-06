import json, os, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S+08:00")
gp = json.load(open(os.path.join(ROOT, "results", "_r650bmc_codely_gate_pin.json"), encoding="utf-8"))
assert gp["gate_ok"] and gp["delivered"], "gate-pin receipt must be green"

RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
row = ("{ts} | r650 bm-c S7 close addendum | dept:工程/舰队 | tail gate-pin receipt per r646 law: "
      "post-commit blob face git cat-file -s HEAD:CODELY.md = 30,570B (blob c65a0678b·gate 30,720 headroom 150B gate-ok BUT razor-thin) -- "
      "rebase closeout integrated bm-a r806 wave (their marker-gate pit append + healed r804 faces) is what consumed the headroom; "
      "15 UU faces resolved per ts-law (my S6 03:21-03:24 newer than bm-a 03:03-03:07: 10 ts-faces take-mine + 7 empty-ts faces fix-leg to mine "
      "[twin convergence LIVE md/json + dashboard js/json + regime_state updated-field-only diff origin 03:03:41 vs mine 03:21:36 content-identical] "
      "+ token per-key max-union + compute_audit history ts-union 203 rows; marker hard-gate both sides all clean; receipt results/_r650bmc_merge_resolve.json; "
      "resolver sha-channel per r648 law) | P0 next-round first item: D-06 mini-split of main-file recent pit entries (r646 double-pit + r648 :N:-read pit + "
      "r649 silent-git pit + bm-a marker-gate pit, ~3.6KB pool) to pit domain files per r642 batch-5 precedent (split executed at 30,523B) -- "
      "150B headroom means ANY next CODELY append breaches gate; execute per verbatim migration ritual (needle count==1 + treasure_guard prescan + receipt)\n"
      ).format(ts=now)
with open(RR, "ab") as fh:
    fh.write(row.encode("utf-8") + b"\r\n")
print("RR addendum appended")
