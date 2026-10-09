# -*- coding: utf-8 -*-
"""r796 bm-c post-push sync face: heartbeat sync note + head_sha +
last_pulled_at refresh after delivery self-verify 0/0 (r795 tail canon).
No other fields touched (closeout owns the round fields)."""
import json, subprocess, sys, os, datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

def git(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True,
                       creationflags=CNW)
    return p.returncode, p.stdout.decode("utf-8", "replace").strip()

rc, head = git(["rev-parse", "HEAD"])
ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["sync"] = {
    "ahead": 0, "behind": 0,
    "last_push_ts": ts,
    "note": ("r796 post-push delivery self-verified ahead=0/behind=0 via fetch+rev-list; "
             "push-rejected first try (origin advanced 4 = bm-a r909/r910 W195 finalize + W196 seat) "
             "-> churn-absorb a736c56f6 (E42/r884) -> merge origin/main single-stop c93e143eb "
             "(6-UU: ts-duel 4-ours/1-theirs deep-ts r738 + 1 jsonl union r742; "
             "receipt results/_r796bmc_merge_resolver.json) -> clean push c93e143eb; "
             "1 autofill daemon self-commit in window (4f27e6d76 keepalive claim-refresh "
             "w17-screen-0/1/2of8 owner=bm-c, daemon-lane), absorbed by merge history"),
}
hb["head_sha"] = head
hb["last_pulled_at"] = ts
with open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, indent=1, ensure_ascii=False)
chk = json.load(open(hp, encoding="utf-8"))
print(json.dumps({"head": head, "sync_ts": chk["sync"]["last_push_ts"],
                  "head_sha": chk["head_sha"][:12]}, indent=1))
