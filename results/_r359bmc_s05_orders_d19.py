"""r359 bm-c S0.5: orders diff + inbox unread + D-19 decisions watermark.

Laws applied:
- Full-scan orders diff (no timestamp filtering, R13).
- D-19 fresh-read: raw-blob bytes SHA-256 via python subprocess (r292 transcoding
  pit), case-normalized compare (r503).
- CREATE_NO_WINDOW on all child git calls (U060 / zero-flash defense-in-depth).
"""
import hashlib
import json
import os
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"
NO_WIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def git(args, cwd):
    return subprocess.run(
        ["git"] + args, cwd=cwd, capture_output=True,
        creationflags=NO_WIN,
    )


def main():
    out = {}

    # 1. Orders full-scan diff
    orders_dir = os.path.join(REPO, "fleet", "orders")
    all_orders = sorted(
        f for f in os.listdir(orders_dir)
        if f.startswith("O-") and f.endswith(".md")
    )
    with open(os.path.join(REPO, "fleet", "machines", "bm-c.json"), encoding="utf-8") as fh:
        ack = set(json.load(fh).get("orders_ack", []))
    unacked = [o for o in all_orders if o not in ack]
    out["orders_total"] = len(all_orders)
    out["orders_unacked"] = unacked

    # 2. Inbox unread (files in inbox/ not yet in inbox/processed/)
    inbox = os.path.join(REPO, "fleet", "inbox")
    proc = os.path.join(inbox, "processed")
    processed = set(os.listdir(proc)) if os.path.isdir(proc) else set()
    unread = sorted(
        f for f in os.listdir(inbox)
        if f.endswith(".md") and f not in processed
    )
    out["inbox_unread"] = unread

    # 3. D-19 decisions watermark (fresh read, zero tree touch)
    r = git(["fetch", "origin"], GROUP)
    if r.returncode != 0:
        out["d19"] = {"error": "fetch rc=%d %s" % (r.returncode, r.stderr.decode("utf-8", "replace")[:200])}
    else:
        r = git(["show", "origin/main:docs/decisions.md"], GROUP)
        if r.returncode != 0:
            out["d19"] = {"error": "show rc=%d %s" % (r.returncode, r.stderr.decode("utf-8", "replace")[:200])}
        else:
            new_sha = hashlib.sha256(r.stdout).hexdigest().upper()
            with open(os.path.join(REPO, "state-bm-c.json"), encoding="utf-8") as fh:
                state = json.load(fh)
            old_sha = str(state.get("last_decisions_sha", "")).upper()
            out["d19"] = {
                "verdict": "MATCH-unchanged" if new_sha == old_sha else "CHANGED",
                "new_sha": new_sha,
                "old_sha": old_sha,
            }
            if new_sha != old_sha:
                new_text = r.stdout.decode("utf-8", "replace")
                idx = new_text.find("派工通告板")
                out["d19"]["dispatch_board_tail"] = new_text[idx:idx + 4000] if idx >= 0 else "(board marker not found)"
                if idx < 0:
                    out["d19"]["tail"] = new_text[-4000:]

    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
