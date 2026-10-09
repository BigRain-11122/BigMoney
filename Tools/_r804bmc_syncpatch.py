# -*- coding: utf-8 -*-
"""r804 bm-c sync patch: heartbeat head_sha + delivery self-verification
(fetch + rev-list ahead/behind), then targeted commit (heartbeat file only)
and push. Pattern credit: r803 closeout sync patch (ddf30aeab canon).
CREATE_NO_WINDOW on every git subprocess (zero-desktop-flash law)."""
import datetime
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def git(args):
    p = subprocess.run(["git", "-C", str(ROOT)] + args, capture_output=True,
                        creationflags=CNW)
    return p.returncode, p.stdout.decode("utf-8", "replace").strip(), p.stderr


rc, out, err = git(["fetch", "origin"])
assert rc == 0, "fetch failed: %s" % err
rc, out, err = git(["rev-list", "--left-right", "--count", "HEAD...origin/main"])
ahead, behind = (int(x) for x in out.split())
rc, sha, _ = git(["rev-parse", "--short=9", "HEAD"])
now_iso = datetime.datetime.now(datetime.timezone(
    datetime.timedelta(hours=8))).strftime("%Y-%m-%dT%H:%M:%S+08:00")

hb_path = ROOT / "fleet" / "machines" / "bm-c.json"
hb = json.loads(hb_path.read_text(encoding="utf-8"))
hb["head_sha"] = sha
hb["last_pulled_at"] = now_iso
hb["sync"] = {
    "ahead": ahead,
    "behind": behind,
    "last_push_ts": now_iso,
    "note": ("r804 post-push delivery self-verified ahead=%d/behind=%d via fetch+rev-list "
             "(push %s clean, pre-push claw passed, no escape needed); round chain: S0 absorb "
             "de9f36cff -> pull --rebase up-to-date zero-UU -> S0.5 double-sweep consumed ORD "
             "delta 4AA1A8F6->31542B89 (+2 rows = O-20261009-1246/1257, BigMoney no-queue "
             "violation -> same-round fix mandate (a) state/queue three-file build + "
             "auditor-mirror verify GREEN) -> S1 smoke 49/49 -> QA r804 5/5 -> S6 40/40 "
             "(25th green) -> S7 self-heal batch -> closeout -> round commit %s -> push -> "
             "sync patch" % (ahead, behind, sha, sha)),
}
hb_path.write_text(json.dumps(hb, ensure_ascii=False, indent=1), encoding="utf-8")
st_path = ROOT / "state-bm-c.json"
st = json.loads(st_path.read_text(encoding="utf-8"))
st["head_sha"] = sha
st_path.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")

print("sync patch facts: head=%s ahead=%d behind=%d" % (sha, ahead, behind))
assert ahead == 0 and behind == 0, "delivery not clean: ahead=%d behind=%d" % (ahead, behind)
rc, out, err = git(["add", "fleet/machines/bm-c.json", "state-bm-c.json"])
assert rc == 0, err
rc, out, err = git(["commit", "-m",
                    "r804 closeout sync patch: heartbeat head_sha=%s + delivery "
                    "self-verified ahead=0/behind=0 (post-push face)" % sha])
print("commit:", out or err or "(no change)")
rc, out, err = git(["push"])
print("push rc=%d" % rc, out or err)
assert rc == 0, "push failed"
rc, out, _ = git(["rev-list", "--left-right", "--count", "HEAD...origin/main"])
a2, b2 = (int(x) for x in out.split())
print("final delivery: ahead=%d behind=%d" % (a2, b2))
assert a2 == 0 and b2 == 0
print("SYNC-PATCH OK")
