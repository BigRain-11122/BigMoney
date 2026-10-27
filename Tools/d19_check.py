# -*- coding: utf-8 -*-
"""d19_check.py -- D-20260930-19 decisions watermark standing check (P-32 wiring).

Law: D-20260930-19 fresh-read = git -C <group> fetch + git show
origin/main:docs/decisions.md RAW-BLOB bytes -> SHA-256 (r292: PS pipeline
join = transcoding false-drift; r503: upper() case-normalize both sides).
Zero tree touch on the group repo. Watermark lives in state-<id>.json
last_decisions_sha / last_orders_sha in TRIPLE form `<sha16>@<commit7>/<bytes>`
(D-20261024-03: compare commit+length first, then the content hash -- a bare
hash that cannot be reproduced on origin loses its judging power, r1142/r1143/
r1145 evidence). Legacy bare 64-hex watermarks are accepted and upgraded in
place on --update.

Usage (from repo root, any machine):
    python Tools/d19_check.py            # print MATCH/CHANGED + context
    python Tools/d19_check.py --update   # also rewrite state last_decisions_*
                                        # fields (call ONLY after consumption)

On CHANGED prints: the 派工通告板 dispatch-block rows + docs/orders.md CEO
待办区 rows touching this repo, plus the tail of decisions.md (newest rows)
for the round to consume. All child git calls carry CREATE_NO_WINDOW
(session-host flash guard, U060/O-67fbec7 law family).
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

# r755 root fix (r521 family): a CHANGED window prints decision rows that
# carry U+2713/CJK; on a zh-CN GBK console/pipe print() raises
# UnicodeEncodeError mid-report and kills the gate BEFORE the --update
# watermark write. Self-heal stdout/stderr to UTF-8 (errors=replace) so the
# gate always completes regardless of console codepage -- callers no longer
# need to remember PYTHONIOENCODING=utf-8 (bm-b r755 live crash evidence).
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CREATE_NO_WINDOW = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUP_CANDIDATES = [
    os.path.normpath(os.path.join(ROOT, "..", "..")),   # bigmoney -> quant -> FluxGroup (bm-a/bm-c layout)
    r"C:\Users\Administrator\FluxGroup",                 # bm-b group-tree location (r626 note)
    r"K:\Fluxgroup\FluxGroup",                           # legacy mapped drive probe (r579 lineage)
]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from group_root import pick as _pick_group_root_impl
except Exception:                                    # pragma: no cover
    _pick_group_root_impl = None


def _pick_group_root(candidates):
    """D-20261028-04: one implementation, shared (Tools/group_root.py).

    Validate first, then take the LIVE tree (newest ledger mtime) -- a candidate
    list is a hint, never a decision. Kept as a thin wrapper so this probe reads
    the same way it always did.
    """
    if _pick_group_root_impl is None:
        return None, [(c, "group_root-import-failed") for c in candidates]
    return _pick_group_root_impl(candidates)


RE_KEYWORD = re.compile(r"BigMoney|bigmoney|quant|bm-[abc]", re.IGNORECASE)


def _find_group():
    """Delegates to _pick_group_root (D-20261028-04); keeps the old name so the
    rest of this probe does not care where the root came from."""
    path, rejected = _pick_group_root(GROUP_CANDIDATES)
    if path is None and rejected:
        sys.stderr.write("d19_check: no viable group tree: %s\n" % (rejected,))
    return path


GROUP = _find_group()


def _git(group_args, cwd):
    r = subprocess.run(["git"] + group_args, capture_output=True, cwd=cwd,
                       creationflags=CREATE_NO_WINDOW)
    if r.returncode != 0:
        sys.exit("GIT FAIL %s -> %s" % (group_args[:3],
                                        r.stderr.decode("utf-8", "replace")))
    return r.stdout


def _wm(sha_hex, commit, nbytes):
    """D-20261024-03 triple watermark: <sha16>@<commit7>/<bytes>."""
    return "%s@%s/%d" % (sha_hex[:16].lower(), (commit or "")[:7].lower(), nbytes)


def _repo_id(group):
    """Origin URL as the machine-independent repo identity (D-20261025-08 'repo')."""
    try:
        return _git(["remote", "get-url", "origin"], group).decode().strip()
    except SystemExit:
        return group


def _v2_entry(repo, commit, blob, path):
    """D-20261025-08 quartet {repo, commit_sha, blob_bytes, sha256} + fetch command."""
    return {
        "repo": repo,
        "commit_sha": commit,
        "blob_bytes": len(blob),
        "sha256": hashlib.sha256(blob).hexdigest(),
        "path": path,
        "fetch_command": "git -C <group-tree> show origin/main:%s" % path,
    }


def _v2_compare(prev, cur):
    """D-20261025-08 (2): repo+commit_sha+blob_bytes first, then sha256.

    Returns 'match' | 'stale' | 'changed'.  A content-equal blob behind a
    different source commit is STALE (never advances, never judges).
    """
    if not prev:
        return "changed"
    if (prev.get("repo") != cur["repo"]
            or prev.get("commit_sha") != cur["commit_sha"]
            or prev.get("blob_bytes") != cur["blob_bytes"]):
        return "stale" if prev.get("sha256") == cur["sha256"] else "changed"
    return "match" if prev.get("sha256") == cur["sha256"] else "changed"


def _persist_v2(st, group, blob, commit):
    """Record the D-20261025-08 quartet for both faces (additive to the triple form)."""
    repo = _repo_id(group)
    v2 = st.get("d19_watermark_v2") or {}
    dec = _v2_entry(repo, commit, blob, "docs/decisions.md")
    verdict = _v2_compare(v2.get("decisions"), dec)
    v2["decisions"] = dec
    v2["decisions_verdict"] = verdict
    try:
        oblob = _git(["show", "origin/main:docs/orders.md"], group)
        oentry = _v2_entry(repo, commit, oblob, "docs/orders.md")
        overdict = _v2_compare(v2.get("orders"), oentry)
        v2["orders"] = oentry
        v2["orders_verdict"] = overdict
    except SystemExit:
        pass
    v2["law"] = "D-20261025-08 watermark v2 quartet {repo, commit_sha, blob_bytes, sha256}"
    v2["compare_order"] = "repo+commit_sha+blob_bytes first, then sha256; source mismatch = stale"
    v2["updated_at"] = st.get("clock_read") or ""
    st["d19_watermark_v2"] = v2
    print("D-19 v2 quartet: decisions %s (%s B, commit %s) verdict=%s"
          % (dec["sha256"][:16], dec["blob_bytes"], dec["commit_sha"][:7], verdict))
    return v2


_WM_RE = re.compile(r"^([0-9a-fA-F]{16})@([0-9a-fA-F]{7,40})/(\d+)$")
_SHA_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _parse_wm(v):
    """-> (sha16, commit7, bytes) or None for a legacy bare sha."""
    v = (v or "").strip()
    m = _WM_RE.match(v)
    if m:
        return (m.group(1).lower(), m.group(2)[:7].lower(), int(m.group(3)))
    if _SHA_RE.match(v):
        return ("", "", -1)
    return None


def machine_id():
    with open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8-sig") as fh:
        return json.load(fh)["machine_id"]


def state_path(mid):
    # bm-b uses the shared-repo legacy state.json filename (fleet README S5 law);
    # every other machine uses state-<id>.json.
    if mid == "bm-b":
        return os.path.join(ROOT, "state.json")
    return os.path.join(ROOT, "state-%s.json" % mid)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--update", action="store_true")
    args = ap.parse_args()

    mid = machine_id()
    sp = state_path(mid)
    with open(sp, encoding="utf-8-sig") as fh:
        st = json.load(fh)
    prev_raw = st.get("last_decisions_sha") or ""
    prev = _parse_wm(prev_raw)

    if GROUP is None:
        print("D-19 HONEST SKIP: no group worktree found in candidates %s"
              % [c for c in GROUP_CANDIDATES])
        return 0
    _git(["fetch", "origin"], GROUP)
    blob = _git(["show", "origin/main:docs/decisions.md"], GROUP)
    sha = hashlib.sha256(blob).hexdigest()
    commit = _git(["rev-parse", "origin/main"], GROUP).decode().strip()
    wm = _wm(sha, commit, len(blob))
    cur = (sha[:16].lower(), commit[:7].lower(), len(blob))
    legacy_match = bool(prev) and prev[2] < 0 and prev_raw.strip().upper() == sha.upper()

    if cur == prev or legacy_match:
        print("D-19 MATCH (decisions watermark unchanged: %s)" % wm)
        if args.update:
            if legacy_match:
                st["last_decisions_sha"] = wm
                print("state watermark upgraded to triple form")
            now = st.get("clock_read") or ""
            st["last_decisions_at"] = now
            st["last_decisions_read_at"] = now
            try:
                oblob = _git(["show", "origin/main:docs/orders.md"], GROUP)
                st["last_orders_sha"] = _wm(hashlib.sha256(oblob).hexdigest(), commit,
                                            len(oblob))
            except SystemExit:
                print("(orders.md watermark not refreshed -- file absent on origin)")
            _persist_v2(st, GROUP, blob, commit)
            with open(sp, "w", encoding="utf-8", newline="") as fh:
                json.dump(st, fh, ensure_ascii=False, indent=1)
        return 0

    print("D-19 CHANGED: %s -> %s" % (prev_raw[:24], wm))
    text = blob.decode("utf-8", "replace")
    lines = text.splitlines()
    # dispatch board rows + keyword rows + file tail for new-decision review
    hits = [ln for ln in lines if RE_KEYWORD.search(ln)]
    print("--- keyword rows (%d) ---" % len(hits))
    for ln in hits[-40:]:
        print(ln[:300])
    print("--- decisions.md tail (last 30 lines) ---")
    for ln in lines[-30:]:
        print(ln[:300])
    try:
        orders = _git(["show", "origin/main:docs/orders.md"], GROUP).decode("utf-8", "replace")
        print("--- orders.md keyword rows ---")
        for ln in orders.splitlines():
            if RE_KEYWORD.search(ln):
                print(ln[:300])
    except SystemExit:
        print("(orders.md not found on origin -- skip)")
    if args.update:
        st["last_decisions_sha"] = wm
        try:
            oblob = _git(["show", "origin/main:docs/orders.md"], GROUP)
            ocommit = _git(["rev-parse", "origin/main"], GROUP).decode().strip()
            st["last_orders_sha"] = _wm(hashlib.sha256(oblob).hexdigest(), ocommit,
                                        len(oblob))
        except SystemExit:
            print("(orders.md watermark not refreshed -- file absent on origin)")
        # machines disagree on the timestamp field name (bm-a/bm-b _at vs
        # bm-c _read_at) -- write both so every consumer stays satisfied.
        now = st.get("clock_read") or ""
        st["last_decisions_at"] = now
        st["last_decisions_read_at"] = now
        _persist_v2(st, GROUP, blob, commit)
        with open(sp, "w", encoding="utf-8", newline="") as fh:
            json.dump(st, fh, ensure_ascii=False, indent=1)
        print("state last_decisions_sha updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
