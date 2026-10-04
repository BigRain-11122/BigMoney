# -*- coding: utf-8 -*-
"""r499 bm-c S0.5: orders diff-set (same-shape full filenames) + D-19 dual-key watermark.

Group tree read via raw-blob git show bytes (r660 subprocess law: no PS pipeline,
no disk-file hashing). Fleet orders via same-shape set comparison (r646/r477):
git ls-tree names (O-*.md full names) vs heartbeat orders_ack (full .md names).
All output to UTF-8 file, zero console print (r458 family).
"""
import hashlib
import json
import re
import subprocess

CREATE_NO_WINDOW = 0x08000000
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GROUP = r"K:\Fluxgroup\FluxGroup"
OUT = []

def g(args, cwd=ROOT):
    return subprocess.run(["git"] + args, capture_output=True, cwd=cwd,
                          creationflags=CREATE_NO_WINDOW)

def say(msg):
    OUT.append(msg)

# --- 1. fleet orders diff (same-shape both sides) ---
r = g(["ls-tree", "origin/main", "fleet/orders/"])
names = []
for ln in r.stdout.decode("utf-8", "replace").splitlines():
    m = re.match(r"\d+ \w+ ([0-9a-f]+)\t(fleet/orders/O-.*\.md)$", ln)
    if m:
        names.append(m.group(2).split("/")[-1])
ack = json.load(open(ROOT + r"\fleet\machines\bm-c.json", encoding="utf-8")).get("orders_ack", [])
unacked = [n for n in names if n not in ack]
extra = [a for a in ack if a not in names and a != "README.md"]
say("FLEET orders total=%d ack=%d unacked=%d extra_ack=%d" % (len(names), len(ack), len(unacked), len(extra)))
for n in unacked:
    say("UNACKED: " + n)
for e in extra:
    say("EXTRA_ACK: " + e)

# --- 2. D-19 group-tree dual-key watermark (raw-blob bytes) ---
fr = g(["fetch", "origin"], cwd=GROUP)
if fr.returncode != 0:
    say("GROUP FETCH FAIL: " + fr.stderr.decode("utf-8", "replace")[:200])
else:
    say("GROUP FETCH OK")
    for path, key, algo in (("docs/decisions.md", "last_decisions_sha", "sha256"),
                            ("docs/orders.md", "last_orders_sha", "sha1")):
        rr = g(["show", "origin/main:" + path], cwd=GROUP)
        if rr.returncode != 0:
            say("%s GIT SHOW FAIL: %s" % (path, rr.stderr.decode("utf-8", "replace")[:150]))
            continue
        digest = hashlib.sha256(rr.stdout).hexdigest() if algo == "sha256" else hashlib.sha1(rr.stdout).hexdigest()
        state = json.load(open(ROOT + r"\state-bm-c.json", encoding="utf-8"))
        stored = str(state.get(key, "")).upper()
        cur = digest.upper()
        if stored == cur:
            say("%s: SHA-%s MATCH-unchanged (%s)" % (path, algo, cur[:16]))
        else:
            say("%s: SHA-%s CHANGED stored=%s new=%s" % (path, algo, stored[:16], cur[:16]))
            if path == "docs/decisions.md":
                # extract dispatch-board lines mentioning this company
                text = rr.stdout.decode("utf-8", "replace")
                for ln in text.splitlines():
                    if re.search(r"BigMoney|quant|bm-[abc]", ln):
                        say("DECISION-LINE-RELEVANT: " + ln.strip()[:300])
            else:
                text = rr.stdout.decode("utf-8", "replace")
                m = re.search(r"CEO[^\n]*物理件[^\n]*\n(.*?)(\n#|\Z)", text, re.S)
                if m:
                    for ln in m.group(1).splitlines():
                        if re.search(r"BigMoney|quant|bm-[abc]", ln):
                            say("ORDERS-LINE-RELEVANT: " + ln.strip()[:300])

# --- 3. fleet inbox unread scan (to bm-c or ALL) ---
r = g(["ls-tree", "origin/main", "fleet/inbox/"])
inbox = []
for ln in r.stdout.decode("utf-8", "replace").splitlines():
    m = re.match(r"\d+ \w+ ([0-9a-f]+)\t(fleet/inbox/MSG-.*\.md)$", ln)
    if m:
        inbox.append(m.group(2).split("/")[-1])
r2 = g(["ls-tree", "origin/main", "fleet/inbox/processed/"])
processed = set()
for ln in r2.stdout.decode("utf-8", "replace").splitlines():
    m = re.match(r"\d+ \w+ ([0-9a-f]+)\t(fleet/inbox/processed/MSG-.*\.md)$", ln)
    if m:
        processed.add(m.group(2).split("/")[-1])
unread = [f for f in inbox if f not in processed and ("bm-c" in f or "ALL" in f or "-all" in f)]
say("INBOX unread-to-me=%d" % len(unread))
for f in unread:
    say("UNREAD-MSG: " + f)

with open(ROOT + r"\results\_r499bmc_s05.txt", "w", encoding="utf-8") as fh:
    fh.write("\n".join(OUT) + "\n")
print("S05 DONE lines=%d" % len(OUT))
