# -*- coding: utf-8 -*-
"""r750 bm-a state update: round_no 749->750 + D-19 dual watermark
(decisions SHA-256 + orders SHA-1, r537 dual-algorithm pin law)."""
import json, time

st = json.load(open("state-bm-a.json", encoding="utf-8"))
assert st["round_no"] == 749, f"round_no drift: {st['round_no']}"
st["round_no"] = 750
st["last_decisions_sha"] = "7674e37b"  # placeholder, replaced below
st.pop("last_decisions_sha", None)

# full shas recomputed live (python bytes direct, r706 law)
import subprocess, hashlib
p1 = subprocess.run(["git", "-C", "C:/Users/sjs20/Desktop/FluxGroup", "show",
                     "origin/main:docs/decisions.md"], capture_output=True)
assert p1.returncode == 0 and len(p1.stdout) > 100000, "decisions blob fetch failed (r710-2 empty-return law)"
st["last_decisions_sha"] = hashlib.sha256(p1.stdout).hexdigest()
p2 = subprocess.run(["git", "-C", "C:/Users/sjs20/Desktop/FluxGroup", "show",
                     "origin/main:docs/orders.md"], capture_output=True)
assert p2.returncode == 0 and len(p2.stdout) > 100000, "orders blob fetch failed"
st["last_orders_sha"] = hashlib.sha1(p2.stdout).hexdigest()
now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00", time.localtime())
st["last_decisions_at"] = now
st["last_decisions_ts"] = now
st["last_orders_at"] = now
st["last_round"] = 750
st["last_round_at"] = now
st["last_round_ts"] = now
st["last_run"] = "r750: W143 freeze chain full delivery (seat 3a7640311 + freeze 86d3b070c + ignition n1w143 pid=25400) + S6 r750 chain + D-19 dual watermark consumed (D-20261006-01/02/03 zero BigMoney new dispatch)"
st["current_task"] = "W143 burn in flight (engine tick queue) + next: W144 freeze window (staircase + same-freeze mutual exclusion mandatory notes)"
st["next"] = "W144 freeze window (re-derive on post-W143 universe + own-A reservation when deriving B; W143 B band 331_404..331_603 will refuse naive W144 A window)"

json.dump(st, open("state-bm-a.json", "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)
# readback verification
rb = json.load(open("state-bm-a.json", encoding="utf-8"))
assert rb["round_no"] == 750 and rb["last_decisions_sha"].startswith("7674e37b") \
    and rb["last_orders_sha"].startswith("99182969"), "readback drift"
print("state updated: round_no=750, decisions", rb["last_decisions_sha"][:12],
      "orders", rb["last_orders_sha"][:12])
