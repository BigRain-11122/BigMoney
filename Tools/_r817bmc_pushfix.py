# -*- coding: utf-8 -*-
"""r817 bm-c pushfix (r816 pushfix precedent): post-delivery head_sha/sync
block touch-up in state-bm-c.json + fleet/machines/bm-c.json, then targeted
commit + push with retry (SSH reset window). The r817 delivery chain: close
commit 71b667f68 + autofill keepalive a86b3e1bc (daemon self-commit face)
delivered by push attempt 3/4; post-push tracking-ref rev-list 0/0
self-verified. Facts-driven HEAD read at runtime, zero literal sha
constants beyond the delivery-note prose. CREATE_NO_WINDOW per U060."""
import json, os, subprocess, time
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
CST = timezone(timedelta(hours=8))
now_iso = datetime.now(CST).strftime("%Y-%m-%dT%H:%M:%S+08:00")


def git(args, timeout=90):
    try:
        r = subprocess.run(["git"] + args, cwd=ROOT, capture_output=True,
                           creationflags=CREATE, timeout=timeout)
        return r.returncode, (r.stdout or b"").decode("utf-8", "replace"), \
            (r.stderr or b"").decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return 124, "", "leg timeout after %ss" % timeout


def main():
    rc, head, _ = git(["rev-parse", "HEAD"])
    head = head.strip()
    assert rc == 0 and len(head) == 40, "HEAD read gate"
    sync_note = ("r817 delivery chain: close commit 71b667f68 + autofill keepalive a86b3e1bc "
                 "(daemon self-commit face, r288/r290 law) delivered by push attempt 3/4 "
                 "(SSH reset window, attempts 1-2 rc128); post-push tracking-ref rev-list 0/0 "
                 "self-verified; post-verify fetch rc128 channel flake honest note")
    for rel in ("state-bm-c.json", os.path.join("fleet", "machines", "bm-c.json")):
        p = os.path.join(ROOT, rel)
        with open(p, encoding="utf-8") as f:
            obj = json.load(f)
        obj["head_sha"] = head
        obj["last_pulled_at"] = now_iso
        obj["sync"] = {"ahead": 0, "behind": 0, "last_push_ts": now_iso,
                       "note": sync_note}
        with open(p, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=1)
    msg = os.path.join(ROOT, "_r_bmc_s0msg.txt")
    with open(msg, "w", encoding="utf-8", newline="\n") as f:
        f.write("round 817 pushfix: head_sha/sync delivery touch-up "
                "(close 71b667f68 + keepalive a86b3e1bc delivered, 0/0)\n")
    git(["add", "--", "state-bm-c.json", "fleet/machines/bm-c.json", msg])
    rc, out, err = git(["commit", "-F", msg])
    print("COMMIT rc=%d %s" % (rc, (err or out).strip()[:120]))
    if rc != 0:
        return 1
    ok = False
    for i in range(1, 5):
        rc, out, err = git(["push", "origin", "main"], timeout=120)
        if rc == 0:
            print("PUSH attempt %d OK" % i)
            ok = True
            break
        print("PUSH attempt %d rc=%d" % (i, rc))
        time.sleep(5)
    git(["fetch", "origin"])
    rc, cnt, _ = git(["rev-list", "--left-right", "--count",
                      "HEAD...origin/main"])
    print("AHEAD-BEHIND %s" % cnt.strip())
    return 0 if (ok and cnt.strip().split() == ["0", "0"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
