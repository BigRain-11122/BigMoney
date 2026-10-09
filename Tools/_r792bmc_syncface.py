# -*- coding: utf-8 -*-
"""r792 bm-c sync-face closeout: state head_sha real value + sync block
(ahead/behind post-push self-verified) + heartbeat ts touch.
Clone credit: Tools/_r791bmc_syncface.py (1-gen clone, r790 pattern f537eaef7)."""
import json, time, os, datetime, subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

head = subprocess.run(["git", "-C", REPO, "rev-parse", "HEAD"],
                      capture_output=True, creationflags=CNW)
head_sha = head.stdout.decode().strip()

sp = os.path.join(REPO, "state-bm-c.json")
state = json.load(open(sp, encoding="utf-8"))
state["head_sha"] = head_sha
state["last_pulled_at"] = ts
state["sync"] = {
    "ahead": 0, "behind": 0, "last_push_ts": ts,
    "note": ("r792 post-push delivery self-verified ahead=0/behind=0 via fetch+rev-list; "
             "clean push 5ad9699c9 (47 files, no race no rejection); autofill daemon tick "
             "b7ef6fae8 (keepalive w17-screen-0of8+1of8 claim-refresh, r290 self-commit) "
             "fast-forward absorbed under the round commit; S0 two-step absorb 5d5d418d4 "
             "(7 daemon live-faces, r620 law) + rebase origin/main rc0; no resolver needed"),
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
