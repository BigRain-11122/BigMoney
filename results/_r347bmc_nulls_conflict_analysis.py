# r347 bm-c: nulls.jsonl rebase-conflict ground-truth analysis (READ-ONLY)
# Laws: r294 (union domain), r297 (determinism byte-identity), r321 (inspect real shape before parse),
# r322 (no dangling refs), r503/r292 (raw-bytes git show, no PS pipeline).
import json, subprocess, os, re, glob

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
REL = "results/lowamp_p3/nulls.jsonl"
FULL = os.path.join(REPO, REL)

def git_show(spec):
    return subprocess.check_output(["git", "-C", REPO, "show", spec])

def parse_lines(lines):
    rows, dup_identical, bad = {}, [], []
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        try:
            obj = json.loads(s)
            k = obj.get("k")
            if k in rows:
                if rows[k] == s:
                    dup_identical.append(k)
                else:
                    bad.append(("same-k-diff-bytes", k))
            else:
                rows[k] = s
        except Exception:
            bad.append(("unparseable", s[:60]))
    return rows, dup_identical, bad

report = {}

# --- 1. git stages (raw bytes) ---
try:
    ours_b = git_show(":2:" + REL)      # rebase ours = new base = origin side (r533 checkpoint)
    theirs_b = git_show(":3:" + REL)    # theirs = my ride1 commit
    base_b = git_show(":1:" + REL)      # merge base (r346 push)
    ours_rows, ours_dup, ours_bad = parse_lines(ours_b.decode("utf-8").splitlines())
    theirs_rows, theirs_dup, theirs_bad = parse_lines(theirs_b.decode("utf-8").splitlines())
    base_rows, _, _ = parse_lines(base_b.decode("utf-8").splitlines())
    report["stages"] = {
        "origin_side_rows": len(ours_rows), "origin_k_range": [min(ours_rows), max(ours_rows)] if ours_rows else None,
        "origin_dup_identical": len(ours_dup), "origin_bad": ours_bad[:5],
        "mine_ride1_rows": len(theirs_rows), "mine_ride1_k_range": [min(theirs_rows), max(theirs_rows)] if theirs_rows else None,
        "mine_ride1_bad": theirs_bad[:5],
        "base_rows": len(base_rows),
    }
    # origin k-coverage within 0..max (hole check)
    kmax = max(ours_rows) if ours_rows else -1
    missing = [k for k in range(0, kmax + 1) if k not in ours_rows]
    report["stages"]["origin_missing_k_in_range"] = missing[:20]
    report["stages"]["origin_missing_k_count"] = len(missing)
    # byte-identity: my ride1 rows vs origin rows for same k
    mism = [k for k in theirs_rows if k in ours_rows and theirs_rows[k] != ours_rows[k]]
    mine_only = sorted(k for k in theirs_rows if k not in ours_rows)
    report["stages"]["ride1_vs_origin_byte_mismatch_k"] = mism[:20]
    report["stages"]["ride1_vs_origin_byte_mismatch_count"] = len(mism)
    report["stages"]["ride1_mine_only_k"] = mine_only[:20]
    report["stages"]["ride1_mine_only_count"] = len(mine_only)
except Exception as e:
    report["stages_error"] = repr(e)

# --- 2. working file structure ---
try:
    wf = open(FULL, "rb").read().decode("utf-8")
    lines = wf.splitlines()
    marks = {"start": [], "base": [], "mid": [], "end": []}
    for i, ln in enumerate(lines):
        if ln.startswith("<<<<<<<"): marks["start"].append(i + 1)
        elif ln.startswith("|||||||"): marks["base"].append(i + 1)
        elif ln.startswith("======="): marks["mid"].append(i + 1)
        elif ln.startswith(">>>>>>>"): marks["end"].append(i + 1)
    report["working"] = {"total_lines": len(lines), "markers": marks}
    if len(marks["start"]) == 1 and len(marks["end"]) == 1:
        s, b, m, e = marks["start"][0], marks["base"][0], marks["mid"][0], marks["end"][0]
        post = lines[e:]
        post_rows, post_dup, post_bad = parse_lines(post)
        # byte-identity: post rows (active burn appends) vs origin
        pm = [k for k in post_rows if k in ours_rows and post_rows[k] != ours_rows[k]]
        p_only = sorted(k for k in post_rows if k not in ours_rows)
        report["working"]["post_rows"] = len(post_rows)
        report["working"]["post_k_range"] = [min(post_rows), max(post_rows)] if post_rows else None
        report["working"]["post_vs_origin_byte_mismatch_k"] = pm[:20]
        report["working"]["post_vs_origin_mismatch_count"] = len(pm)
        report["working"]["post_mine_only_k"] = p_only[:20]
        report["working"]["post_mine_only_count"] = len(p_only)
except Exception as e:
    report["working_error"] = repr(e)

# --- 3. pool entry for lowamp p3 nulls ---
try:
    pool = json.load(open(os.path.join(REPO, "results", "runnable_pool.json"), encoding="utf-8"))
    entries = pool.get("entries", pool if isinstance(pool, list) else [])
    hits = []
    for en in entries:
        eid = str(en.get("id", ""))
        if "nulls" in eid.lower() and ("lowamp" in eid.lower() or "p3" in eid.lower()):
            hits.append(en)
    report["pool_entries"] = hits
except Exception as e:
    report["pool_error"] = repr(e)

# --- 4. prereg nulls target ---
try:
    targets = []
    for f in glob.glob(os.path.join(REPO, "research", "*LOWAMP*")) + glob.glob(os.path.join(REPO, "research", "*lowamp*")):
        if os.path.isfile(f):
            txt = open(f, "r", encoding="utf-8", errors="replace").read().splitlines()
            for i, ln in enumerate(txt):
                if re.search(r"null", ln, re.I) and re.search(r"\d{3,}", ln):
                    targets.append({"file": os.path.basename(f), "line": i + 1, "text": ln.strip()[:160]})
    report["prereg_null_mentions"] = targets[:25]
except Exception as e:
    report["prereg_error"] = repr(e)

out = os.path.join(REPO, "results", "_r347bmc_nulls_conflict_analysis.json")
json.dump(report, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(report, ensure_ascii=False, indent=1))
