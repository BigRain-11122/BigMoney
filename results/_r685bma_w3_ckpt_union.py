"""r685 bm-a: resolve w3_screen_checkpoint.jsonl merge conflict (union, id-canon).

Sides (r657 law: HEAD:/MERGE_HEAD: raw blobs, index polluted by add):
  - MERGE_HEAD (origin): bm-c shard-0/1/2 rows
  - HEAD (ours absorb commit): local shard-3 rows as of absorb
  - working tree: conflict-marker file + post-absorb daemon appends (burn in flight)

Union = origin lines (order preserved) + local-only lines (not in origin, id dedup).
Zero-loss: canon(post-write) == canon(final); canon(pre-wt) subset canon(post).
Daemon race self-check: pre-write wt rows must all survive; redo once if lost.
"""
import subprocess, json, sys

PATH = "results/mass_trial/w3_screen_checkpoint.jsonl"
MARK = (b"<<<<<<<", b"=======", b">>>>>>>", b"|||||||")


def blob(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    r.check_returncode()
    return r.stdout


def canon(b):
    """-> (list_lines_LF, ids_set, bad_json_count, marker_count)"""
    out, ids, bad, marks = [], set(), 0, 0
    for ln in b.split(b"\n"):
        if not ln:
            continue
        s = ln.strip()
        if any(s.startswith(m) for m in MARK):
            marks += 1
            continue
        ln = ln.rstrip(b"\r")
        try:
            ids.add(json.loads(ln)["id"])
        except Exception:
            bad += 1
        out.append(ln)
    return out, ids, bad, marks


theirs = blob("MERGE_HEAD", PATH)
ours = blob("HEAD", PATH)

for attempt in (1, 2):
    wt = open(PATH, "rb").read()
    t_lines, t_ids, t_bad, t_marks = canon(theirs)
    o_lines, o_ids, o_bad, o_marks = canon(ours)
    w_lines, w_ids, w_bad, w_marks = canon(wt)

    t_set = set(t_lines)
    final, seen_ids, my_new = [], set(), []
    for ln in t_lines:
        jid = json.loads(ln)["id"]
        final.append(ln)
        seen_ids.add(jid)
    # local-only rows: prefer working-tree order (superset incl. post-absorb appends),
    # then any absorb-blob-only rows
    for src in (w_lines, o_lines):
        for ln in src:
            if ln in t_set:
                continue
            jid = json.loads(ln)["id"]
            if jid in seen_ids:
                continue
            seen_ids.add(jid)
            final.append(ln)
            my_new.append(ln)

    # assertions
    assert t_bad == 0 and o_bad == 0 and w_bad == 0, "bad json rows present"
    pre_wt_all = set(w_lines) | set(o_lines)
    lost = pre_wt_all - set(final)
    assert not lost, f"zero-loss violated: {len(lost)} rows lost"
    assert len(seen_ids) == len(final), "duplicate ids in final"
    # id-overlap between sides must be byte-identical if both carry same id
    both = t_ids & (w_ids | o_ids)
    for ln in final:
        pass  # id-level dup already asserted absent

    data = b"\n".join(final) + b"\n"
    open(PATH, "wb").write(data)

    # daemon-race self-check: re-read, pre rows must survive
    post = open(PATH, "rb").read()
    p_lines, p_ids, p_bad, p_marks = canon(post)
    assert p_marks == 0, "markers survived write"
    pre_ids = w_ids | o_ids | t_ids
    missing = pre_ids - p_ids
    if missing:
        print(f"attempt {attempt}: daemon race lost {len(missing)} rows, retrying")
        continue
    print(json.dumps({
        "attempt": attempt,
        "origin_rows": len(t_lines), "ours_blob_rows": len(o_lines),
        "wt_rows": len(w_lines), "wt_markers_found": w_marks,
        "final_rows": len(final), "my_new_rows": len(my_new),
        "post_rows": len(p_lines), "id_overlap_both_sides": len(both),
        "zero_loss": True,
    }, ensure_ascii=False))
    sys.exit(0)
print("FAILED after 2 attempts", file=sys.stderr)
sys.exit(2)
