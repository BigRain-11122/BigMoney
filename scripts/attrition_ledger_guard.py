"""attrition_ledger_guard -- append-only attrition ledger integrity tripwire.

r448 bm-a law (r442-family 4th recurrence): the gate_attrition*.json faces are
append-only ledgers; multi-writer clobbers (storm-window rebases, killed-session
absorbs, foreign/stale writers) can silently drop rows. Manual line-count
reconciliation (r446 law) is not enough -- this guard mechanizes it.

Invariants:
  I1 history monotonicity: for consecutive commits touching a ledger file,
     the newer commit's entry-key set must be a SUPERSET of the older's.
  I2 active-loss tripwire: the working-tree file must be a SUPERSET of HEAD.
     (Would have caught the 2026-09-29 21:40 clobber at absorb time.)

Key: (batch, ts) composite -- same batch may carry multiple measurement rows
(REPO_CALENDAR_P2 x2 precedent, 09-28).

Exit codes: 0 = no active loss (historical shrinks reported with healed flag),
1 = ACTIVE LOSS (work file missing rows that HEAD has -- repair before commit),
2 = mechanism error. Evidence JSON written to results/_attrition_guard_scan.json.

Subcommands: scan | selftest (hermetic, offline).
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
EVIDENCE = os.path.join(RESULTS, "_attrition_guard_scan.json")
MAX_COMMITS = 100

# Adjudicated shrink events (legitimate de-dups with in-repo adjudication; never re-add these rows).
# key = (at_rev, "batch|ts") -> adjudication pointer
ADJUDICATED = {
    ("8281d640e", "CN_TREND_ETF_P1|2026-09-27 03:42:52"):
        "bm-b r295 double-append de-dup (surviving twin ts 03:27:59, +2007 cells)",
}


def entry_keys(payload):
    """(batch, ts) keys of an attrition payload dict."""
    return {(e.get("batch"), e.get("ts")) for e in payload.get("entries", [])}


# ------------------------- pure core (selftestable) -------------------------

def check_chain(chain):
    """chain: list of (rev, keys_set) oldest-first. Returns violation events."""
    events = []
    for older, newer in zip(chain, chain[1:]):
        lost = older[1] - newer[1]
        if lost:
            events.append({
                "after_rev": older[0], "at_rev": newer[0],
                "lost_keys": sorted(f"{b}|{t}" for b, t in lost),
            })
    return events


def check_active(head_keys, work_keys):
    """Rows in HEAD missing from work tree = ACTIVE LOSS (must repair)."""
    return head_keys - work_keys


def classify(events, current_keys):
    current_fmt = {f"{b}|{t}" for b, t in current_keys}
    for ev in events:
        ev["healed"] = all(k in current_fmt for k in ev["lost_keys"])
    return events


# ------------------------------ git plumbing --------------------------------

def git(args):
    out = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT)
    if out.returncode != 0:
        raise RuntimeError(f"git {args[:2]} rc={out.returncode}: {out.stderr[:200]}")
    return out.stdout.decode("utf-8", errors="replace")


def file_at(rev, path):
    out = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, cwd=ROOT)
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout.decode("utf-8"))
    except json.JSONDecodeError:
        return None


def scan():
    files = sorted(
        f for f in os.listdir(RESULTS)
        if f.startswith("gate_attrition") and f.endswith(".json")
    )
    report = {"ts": None, "files": {}, "active_loss": False, "rc": 0}
    import datetime
    report["ts"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

    for fname in files:
        path = os.path.join(RESULTS, fname)
        revs = git(["log", "--format=%H", f"-n", str(MAX_COMMITS), "--", f"results/{fname}"]).split()
        revs = list(reversed(revs))  # oldest-first
        chain, rev_payloads = [], {}
        for rev in revs:
            payload = file_at(rev, f"results/{fname}")
            if payload is None:
                continue  # unparsable historical blob: skip, never fabricate
            rev_payloads[rev] = payload
            chain.append((rev, entry_keys(payload)))

        events = check_chain(chain)
        for ev in events:
            ev["adjudicated"] = [
                note for (rev, k), note in ADJUDICATED.items()
                if ev["at_rev"].startswith(rev) and k in ev["lost_keys"]
            ]

        head = rev_payloads.get(revs[-1]) if revs else None
        # HEAD of the branch = last rev from git log of this path
        work_payload = json.load(open(path, encoding="utf-8"))
        work_keys = entry_keys(work_payload)
        head_keys = entry_keys(head) if head is not None else set()
        active = check_active(head_keys, work_keys)
        events = classify(events, work_keys)

        f_report = {
            "history_commits": len(chain),
            "work_entries": len(work_payload.get("entries", [])),
            "head_entries": len(head.get("entries", [])) if head else None,
            "historical_shrinks": events,
            "active_loss_keys": sorted(f"{b}|{t}" for b, t in active),
        }
        report["files"][fname] = f_report
        if active:
            report["active_loss"] = True
            report["rc"] = 1
        for ev in events:
            if ev["adjudicated"]:
                continue  # adjudicated de-dup: information only, never UNHEALED noise
            flag = "healed" if ev["healed"] else "UNHEALED"
            print(f"[{fname}] shrink {len(ev['lost_keys'])} rows at {ev['at_rev'][:9]} "
                  f"(after {ev['after_rev'][:9]}) [{flag}]")
        if active:
            print(f"[{fname}] ACTIVE LOSS: work missing {len(active)} rows present in HEAD -> REPAIR BEFORE COMMIT")

    with open(EVIDENCE, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    ok = "ACTIVE-LOSS" if report["active_loss"] else "CLEAN (no active loss)"
    print(f"guard scan: {len(files)} ledger files, {ok}; evidence -> results/_attrition_guard_scan.json")
    return report["rc"]


# ------------------------------- selftest ------------------------------------

def selftest():
    ok = []

    # [1] append-only chain -> zero violations
    chain = [("a", {(1, 1)}), ("b", {(1, 1), (2, 2)}), ("c", {(1, 1), (2, 2), (3, 3)})]
    ok.append(("monotonic chain clean", check_chain(chain) == []))

    # [2] shrink detected with correct lost keys
    chain = [(("a", {("A", "t1"), ("B", "t2"), ("C", "t3")})),
             ("b", {("A", "t1"), ("B", "t2")})]
    ev = check_chain(chain)
    ok.append(("shrink detected", len(ev) == 1 and ev[0]["lost_keys"] == ["C|t3"]))

    # [3] active loss: work missing HEAD rows
    ok.append(("active loss listed", check_active({(1, 1), (2, 2)}, {(1, 1)}) == {(2, 2)}))

    # [4] superset work -> no active loss
    ok.append(("superset clean", check_active({(1, 1)}, {(1, 1), (9, 9)}) == set()))

    # [5] healed classification
    ev = classify([{"lost_keys": ["2|2"], "after_rev": "x", "at_rev": "y"}], {(2, 2), (1, 1)})
    ok.append(("healed classification", ev[0]["healed"] is True))
    ev = classify([{"lost_keys": ["2|2"], "after_rev": "x", "at_rev": "y"}], {(1, 1)})
    ok.append(("unhealed classification", ev[0]["healed"] is False))

    bad = [name for name, passed in ok if not passed]
    for name, passed in ok:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    print(f"selftest: {len(ok) - len(bad)}/{len(ok)} PASS")
    return 0 if not bad else 1


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if cmd == "scan":
        try:
            return scan()
        except Exception as exc:  # mechanism error -> rc 2 honest
            print(f"guard mechanism error: {exc}")
            return 2
    if cmd == "selftest":
        return selftest()
    print("usage: attrition_ledger_guard.py [scan|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
