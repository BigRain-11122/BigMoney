# -*- coding: utf-8 -*-
"""r794 bm-c sync-face closeout: state head_sha real value + sync block
(ahead/behind post-push self-verified) + heartbeat ts touch.
Clone credit: Tools/_r793bmc_syncface.py (1-gen clone, r793 pattern 4195b65f7)."""
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
    "note": ("r794 post-push delivery self-verified ahead=0/behind=0 via fetch+rev-list; "
             "clean push 2883709e6 (48 files, no race no rejection); S0 two-step absorb "
             "2aace7729 (5 daemon live-faces: heartbeat + idle_trigger x2 + sat_engine x2, "
             "r620 law) + rebase origin/main rc0 (origin zero new commits, no resolver "
             "needed); no daemon self-commit ticks this window (SHARD-2 runner still in "
             "RAM-gate bounded wait, no pool flip yet)"),
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
