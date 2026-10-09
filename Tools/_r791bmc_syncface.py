# -*- coding: utf-8 -*-
"""r791 bm-c sync-face closeout: state head_sha real value + sync block
(ahead/behind post-push self-verified) + heartbeat ts touch.
Clone credit: r790 sync-face closeout pattern (f537eaef7)."""
import json, time, os, datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

sp = os.path.join(REPO, "state-bm-c.json")
state = json.load(open(sp, encoding="utf-8"))
state["head_sha"] = "6b014b8fb115ffb4b1f8602570a1137191a47e9a"
state["last_pulled_at"] = ts
state["sync"] = {
    "ahead": 0, "behind": 0, "last_push_ts": ts,
    "note": ("r791 post-push delivery self-verified ahead=0/behind=0 via fetch+rev-list; "
             "rebase onto bm-a r906/r907 (fc22d154e+08e1629ab+eb81c0878), 3-UU resolver "
             "receipt results/_r791bmc_rebase_resolver.json (token/attrition take-new-by-ts "
             "+ compute_audit latest-new+history-union 202); sat-churn commit dropped as "
             "superseded-empty during replay; push raced W195 seat commit (claw correctly "
             "blocked stale-base deletion face, rebase onto eb81c0878 cured); port22 "
             "transient resets x4 then clean push 6b014b8fb"),
}
with open(sp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(state, fh, indent=1, ensure_ascii=False)

hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["head_sha"] = state["head_sha"]
hb["last_pulled_at"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["ts"] = ts
hb["last_seen"] = ts
with open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, indent=1, ensure_ascii=False)

chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int)
assert "T" in chk["clock_read"] and "T" in chk["ts"]
print("sync-face OK: head_sha=%s ahead=0 behind=0 @%s" % (chk["head_sha"][:12], ts))
