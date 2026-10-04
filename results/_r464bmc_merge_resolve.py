"""r464 bm-c push-race merge resolver: merge origin/main then force-resolve
the 16 both-sides faces with evidence-based rules:
  - CODELY.md: union (origin full text + my added lines, r453 dedup law)
  - compute_audit.json: history union-by-ts (origin-only rows recovered,
    lossless attrition-style) + latest newer-wins
  - crash_fuse.json: sigs per-entry monotone merge (refusals,count,last_crash_ts
    lex-max; cleared identical both sides -> keep)
  - pure snapshots (attrition scan, token_usage, update_status, regime_state,
    lhb/futures status, fundamental_b_layer, REPORT+LIVE twins): ours-newer-wins
    (verified HEAD generated 11:08-11:09 > origin 11:04-11:06)
Then: reparse validation, marker scan, staged check, merge commit, push_verify
single-source delivery (r436-2). Laws: r437 (merge-over-rebase), r656/r657
(raw bytes HEAD:/MERGE_HEAD:), r657-1 (full UU count, no tail truncation),
r644 (marker check by content), r461 (ts normalize before compare)."""
import json
import re
import subprocess
import sys

C = 0x08000000
ROOT = "."


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, creationflags=C,
                       cwd=ROOT)
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace"), \
        (p.stderr or b"").decode("utf-8", "replace")


def show_bytes(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True,
                       creationflags=C, cwd=ROOT)
    return r.returncode, r.stdout


def ts_norm(s):
    """r461 law: normalize ts forms before compare (T -> space, first 19)."""
    if not isinstance(s, str):
        return ""
    return s.replace("T", " ")[:19]


OURS_NEWER = [
    "results/_attrition_guard_scan.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/regime_state.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
    "results/fundamental_b_layer_filter.json",
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
]

PROBES = [
    "results/_r464bmc_merge_analysis.py",
    "results/_r464bmc_premerge_inspect.py",
    "results/_r464bmc_cumulative_check.py",
    "results/_r464bmc_merge_resolve.py",
    "results/_r464bmc_commit_push.py",
    "results/_r464bmc_push_receipt.txt",
]


def resolve_codely():
    _, base = show_bytes("HEAD", "CODELY.md")  # my side == base + my line
    _, theirs = show_bytes("MERGE_HEAD", "CODELY.md")
    # merge-base text for added-line extraction
    rc, mb, _ = git("merge-base", "HEAD", "MERGE_HEAD")
    _, basemb = show_bytes(mb.strip(), "CODELY.md")
    mine_lines = base.decode("utf-8", "replace").splitlines()
    base_lines = basemb.decode("utf-8", "replace").splitlines()
    base_set = set(base_lines)
    added = [ln for ln in mine_lines if ln not in base_set and ln.strip()]
    theirs_text = theirs.decode("utf-8", "replace")
    out = theirs_text
    appended = []
    for ln in added:
        if ln in theirs_text:
            continue
        appended.append(ln)
    if appended:
        if not out.endswith("\n"):
            out += "\n"
        out += "\n".join(appended) + "\n"
    # markers must be gone (line-START judgment per r453 law: pit text legally
    # embeds '<<<<<<<' literals mid-line); my pit line present
    bad = [ln for ln in out.splitlines()
           if ln.startswith(("<<<<<<<", ">>>>>>>"))]
    assert not bad, "codely markers left: " + str(bad[:2])
    assert "r464 bm-c] PS 7" in out, "my pit line missing"
    with open("CODELY.md", "w", encoding="utf-8", newline="") as f:
        f.write(out)
    return {"their_lines_kept": True, "my_lines_appended": appended}


def resolve_compute_audit():
    a = json.loads(show_bytes("HEAD", "results/compute_audit.json")[1]
                   .decode("utf-8", "replace"))
    b = json.loads(show_bytes("MERGE_HEAD", "results/compute_audit.json")[1]
                   .decode("utf-8", "replace"))
    ha, hb = a.get("history", []), b.get("history", [])
    merged = {}
    for row in ha:
        merged[ts_norm(row.get("ts"))] = row
    o_only = 0
    for row in hb:
        k = ts_norm(row.get("ts"))
        if k not in merged:
            merged[k] = row
            o_only += 1
    hist = sorted(merged.values(), key=lambda r: ts_norm(r.get("ts")))
    latest = a.get("latest", {})
    if ts_norm(b.get("latest", {}).get("ts", "")) > ts_norm(latest.get("ts", "")):
        latest = b.get("latest", {})
    out = dict(a)
    out["history"] = hist
    out["latest"] = latest
    with open("results/compute_audit.json", "w", encoding="utf-8",
              newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    json.loads(open("results/compute_audit.json", encoding="utf-8").read())
    return {"history_len": len(hist), "origin_only_recovered": o_only,
            "latest_ts": latest.get("ts")}


def fuse_key_score(e):
    return (e.get("refusals", 0) or 0, e.get("count", 0) or 0,
            ts_norm(e.get("last_crash_ts", "")))


def resolve_crash_fuse():
    a = json.loads(show_bytes("HEAD", "results/crash_fuse.json")[1]
                   .decode("utf-8", "replace"))
    b = json.loads(show_bytes("MERGE_HEAD", "results/crash_fuse.json")[1]
                   .decode("utf-8", "replace"))
    sigs = {}
    taken_mine = taken_theirs = 0
    for k in sorted(set(a.get("sigs", {})) | set(b.get("sigs", {}))):
        ea, eb = a.get("sigs", {}).get(k), b.get("sigs", {}).get(k)
        if ea is None:
            sigs[k] = eb
            taken_theirs += 1
        elif eb is None:
            sigs[k] = ea
            taken_mine += 1
        elif fuse_key_score(eb) > fuse_key_score(ea):
            sigs[k] = eb
            taken_theirs += 1
        else:
            sigs[k] = ea
            taken_mine += 1
    # cleared: identical on both sides (verified pre-merge); keep HEAD's.
    out = dict(a)
    out["sigs"] = sigs
    with open("results/crash_fuse.json", "w", encoding="utf-8",
              newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    json.loads(open("results/crash_fuse.json", encoding="utf-8").read())
    return {"entries": len(sigs), "mine": taken_mine, "theirs": taken_theirs}


def main():
    # 1. merge (expect UU stop); idempotent: skip if merge already in progress
    import os
    if os.path.exists(".git/MERGE_HEAD"):
        print("MERGE_ALREADY_IN_PROGRESS")
    else:
        rc, out, err = git("merge", "origin/main", "--no-edit")
        print("MERGE_RC", rc)
        print((out + err).strip()[:400])
    rc2, st, _ = git("status", "--porcelain")
    uu = [ln[3:].strip().strip('"') for ln in st.splitlines()
          if ln.startswith("UU")]
    print("UU_COUNT", len(uu))
    for u in uu:
        print("  UU", u)
    ev = {}
    # 2. resolve union/cumulative faces
    ev["codely"] = resolve_codely()
    ev["compute_audit"] = resolve_compute_audit()
    ev["crash_fuse"] = resolve_crash_fuse()
    # 3. ours-newer snapshots: take HEAD bytes verbatim
    for p in OURS_NEWER:
        rc3, b = show_bytes("HEAD", p)
        assert rc3 == 0, "show HEAD fail " + p
        with open(p, "wb") as f:
            f.write(b)
        if p.endswith(".json"):
            json.loads(open(p, encoding="utf-8", errors="replace").read())
    ev["snapshots_ours_newer"] = len(OURS_NEWER)
    # 4. stage resolved + probes
    allp = ["CODELY.md", "results/compute_audit.json",
            "results/crash_fuse.json"] + OURS_NEWER + PROBES
    rc4, out4, err4 = git("add", "--", *allp)
    assert rc4 == 0, "add fail: " + err4[:300]
    # 5. marker scan on staged content (r644: content judgment, not bare rc)
    rc5, chk, _ = git("diff", "--cached", "--check")
    marker_hits = [ln for ln in chk.splitlines() if "conflict marker" in ln]
    assert not marker_hits, "marker residue: " + str(marker_hits[:3])
    rc6, grep, _ = git("grep", "--cached", "-l", "-e", "^<<<<<<<")
    assert not grep.strip(), "staged marker grep hit: " + grep[:200]
    # 6. merge commit
    msg = ("merge origin/main: r464 push-race resolve (16 both-sides faces: "
           "snapshots ours-newer 11:08-09 > origin 11:04-06; compute_audit "
           "history union-by-ts +2 origin-only rows recovered incl 10-02 row; "
           "crash_fuse sigs per-entry monotone; CODELY union append) -- r437 "
           "merge-over-rebase after non-ff push (bm-a r672 closeout race)")
    rc7, out7, err7 = git("commit", "-m", msg)
    print("COMMIT_RC", rc7)
    print((out7 + err7).strip()[:300])
    if rc7 != 0:
        sys.exit(1)
    # 7. delivery single-source
    pr = subprocess.run([sys.executable, "Tools/push_verify.py"],
                        capture_output=True, cwd=ROOT, creationflags=C)
    ptxt = ((pr.stdout or b"").decode("utf-8", "replace") + " || " +
            (pr.stderr or b"").decode("utf-8", "replace"))
    with open("results/_r464bmc_push_receipt2.txt", "w", encoding="utf-8",
              newline="\n") as f:
        f.write(ptxt)
    print("PUSH_VERIFY_RC", pr.returncode)
    print(ptxt[-400:])
    print("EV", json.dumps(ev, ensure_ascii=False)[:400])
    sys.exit(pr.returncode if pr.returncode in (0, 1) else 2)


if __name__ == "__main__":
    main()
