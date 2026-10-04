"""r460 bm-c S7 orders double-scan (2nd sweep): fleet/orders O-*.md origin ls-tree
vs heartbeat orders_ack set, both sides same caliber (ls-tree vs heartbeat-list).
File-out per r446 probe law. Zero console CJK print."""
import json
import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r460bmc_orders_diff.json")


def git_ls():
    r = subprocess.run(["git", "ls-tree", "--name-only", "origin/main", "fleet/orders/"],
                       capture_output=True, cwd=ROOT,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if r.returncode != 0:
        return None
    names = set()
    for ln in r.stdout.decode("utf-8", "replace").splitlines():
        ln = ln.strip()
        if ln.startswith("fleet/orders/"):
            names.add(ln[len("fleet/orders/"):])
    return names


def main():
    with open(os.path.join(ROOT, "fleet", "machines", "bm-c.json"), encoding="utf-8-sig") as f:
        hb = json.load(f)
    ack = set(hb.get("orders_ack", []))
    tree = git_ls()
    ev = {"ts": None, "tree_count": None, "ack_count": len(ack), "un_acked": [], "stale_ack": []}
    import datetime
    ev["ts"] = datetime.datetime.now().isoformat(timespec="seconds")
    if tree is None:
        ev["error"] = "LS_TREE_FAIL"
    else:
        ev["tree_count"] = len(tree)
        ev["un_acked"] = sorted(tree - ack)
        ev["stale_ack"] = sorted(ack - tree)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1)
    print("UNACKED", len(ev["un_acked"]), "STALE", len(ev["stale_ack"]),
          "TREE", ev["tree_count"], "ACK", ev["ack_count"])


if __name__ == "__main__":
    main()
