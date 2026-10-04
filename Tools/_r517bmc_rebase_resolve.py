# -*- coding: utf-8 -*-
"""r517 bm-c push-race close: churn-absorb -> pull --rebase (1 pick) ->
per-face canonical resolve (r506 v2 lineage + r516 deep-audit lessons) ->
ATOMIC add + rebase --continue (treadmill window law) -> push_verify.

Rebase semantics (r630/r627 law): s1 = "Updated upstream" = origin side;
s2 = "<pick sha>" = our content. r506 v2 laws kept: generic label anchor +
diff3 four-piece count-identity, sides from worktree text (r405, rebase
face), clean-side flip, twin-lock, ts-newer-wins, history-union (r707),
per-key union (r456/r466), in-block jsonl union (r294).
r517 adds: DAEMON_OURS explicit take-mine for bm-c live daemon faces
(r516 no-ts-fallback deep-audit law -- heartbeat_epoch-only faces must not
fall to max-ts blind side), CODELY.md block-union (r503 lineage),
post_review.jsonl union, machine-suffixed status faces in REGEN set."""
import io
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE_NO_WINDOW = 0x08000000
TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?")
MARKERS = ("<<<<<<<", "|||||||", "=======", ">>>>>>>")

log_lines = []
receipt = {"round": "r517", "files": {}, "errors": [], "phases": {}}


def log(msg):
    log_lines.append(str(msg))
    print(str(msg), flush=True)


def git(*a, **kw):
    env = dict(os.environ)
    env["GIT_EDITOR"] = "true"
    p = subprocess.run(["git"] + list(a), capture_output=True, cwd=ROOT,
                       env=env, creationflags=CREATE_NO_WINDOW,
                       text=True, encoding="utf-8", errors="replace")
    return p.returncode, p.stdout or "", p.stderr or ""


def read_text(path):
    return io.open(os.path.join(ROOT, path), encoding="utf-8",
                   errors="strict").read()


def write_text(path, text):
    io.open(os.path.join(ROOT, path), "w", encoding="utf-8",
            newline="").write(text)


def parse_blocks(text):
    lines = text.split("\n")
    n_open = sum(1 for ln in lines if ln.startswith("<<<<<<< "))
    n_close = sum(1 for ln in lines if ln.startswith(">>>>>>> "))
    n_base = sum(1 for ln in lines if ln.startswith("||||||| "))
    n_mid = sum(1 for ln in lines if ln.rstrip("\r") == "=======")
    if not (n_open == n_close == n_base == n_mid):
        raise ValueError("marker count mismatch open=%d close=%d base=%d "
                         "mid=%d" % (n_open, n_close, n_base, n_mid))
    blocks = []
    state = 0
    cur = {}
    for i, ln in enumerate(lines):
        if ln.startswith("<<<<<<< ") and state == 0:
            cur = {"total_start": i, "s1_start": i + 1}
            state = 1
        elif ln.startswith("||||||| ") and state == 1:
            cur["s1_end"] = i
            state = 2
        elif ln.rstrip("\r") == "=======" and state == 2:
            cur["s2_start"] = i + 1
            state = 3
        elif ln.startswith(">>>>>>> ") and state == 3:
            cur["s2_end"] = i
            cur["total_end"] = i
            blocks.append(cur)
            state = 0
    if state != 0 or len(blocks) != n_open:
        raise ValueError("block parse incomplete state=%d blocks=%d "
                         "expected=%d" % (state, len(blocks), n_open))
    return lines, blocks


def side_text(lines, blocks, which):
    out = []
    last = 0
    for b in blocks:
        out.extend(lines[last:b["total_start"]])
        out.extend(lines[b[which + "_start"]:b[which + "_end"]])
        last = b["total_end"] + 1
    out.extend(lines[last:])
    return "\n".join(out)


def block_union(lines, blocks):
    out = []
    last = 0
    for b in blocks:
        out.extend(lines[last:b["total_start"]])
        s1 = lines[b["s1_start"]:b["s1_end"]]
        s2 = lines[b["s2_start"]:b["s2_end"]]
        seen = set()
        for ln in s1 + s2:
            key = ln.rstrip("\r")
            if key not in seen:
                seen.add(key)
                out.append(ln)
        last = b["total_end"] + 1
    out.extend(lines[last:])
    return "\n".join(out)


def max_ts(text):
    hits = TS_RE.findall(text)
    return max(hits) if hits else ""


def ts_norm(s):
    return s[:10] + "T" + s[11:] if len(s) >= 12 and s[10] == " " else s


def has_linestart_marker(text):
    return any(ln.startswith(MARKERS) for ln in text.split("\n"))


def json_top_ts(doc):
    best = ""
    for k in ("generated_at", "generated", "updated_at", "updated", "now",
               "as_of", "ts", "asof", "cutoff"):
        v = doc.get(k) if isinstance(doc, dict) else None
        if isinstance(v, str):
            m = TS_RE.findall(v)
            if m and ts_norm(max(m)) > ts_norm(best):
                best = max(m)
    return best


def choose_side_json(lines, blocks):
    t1_doc = json.loads(side_text(lines, blocks, "s1"))
    t2_doc = json.loads(side_text(lines, blocks, "s2"))
    c1, c2 = json_top_ts(t1_doc), json_top_ts(t2_doc)
    if c1 and c2 and ts_norm(c1) != ts_norm(c2):
        side = "s1" if ts_norm(c1) > ts_norm(c2) else "s2"
        basis = "top-clock"
    else:
        d1 = max_ts(side_text(lines, blocks, "s1"))
        d2 = max_ts(side_text(lines, blocks, "s2"))
        if not d1 and not d2:
            raise ValueError("no-ts on either side -- deep-audit required "
                             "(r516 law), refusing blind fallback")
        side = "s1" if (ts_norm(d1) >= ts_norm(d2) if d2 else True) else "s2"
        basis = "max-ts"
    st = side_text(lines, blocks, side)
    if has_linestart_marker(st):
        side = "s2" if side == "s1" else "s1"
        st = side_text(lines, blocks, side)
        basis += "+clean-side-flip"
        if has_linestart_marker(st):
            raise ValueError("both sides carry markers")
    return side, st, basis


def resolve_regen(path):
    lines, blocks = parse_blocks(read_text(path))
    side, st, basis = choose_side_json(lines, blocks)
    json.loads(st)
    write_text(path, st)
    receipt["files"][path] = {"strategy": "regen-take-newer", "side": side,
                              "basis": basis, "blocks": len(blocks)}


def resolve_daemon_ours(path):
    lines, blocks = parse_blocks(read_text(path))
    st = side_text(lines, blocks, "s2")
    if has_linestart_marker(st):
        raise ValueError("%s: ours side carries markers" % path)
    json.loads(st)
    write_text(path, st)
    receipt["files"][path] = {"strategy": "daemon-live-ours", "blocks": len(blocks),
                              "note": "bm-c live daemon face, ownership newer "
                                      "by construction (r516 deep-audit law)"}


def resolve_twin(json_path, md_path):
    lines_j, blocks_j = parse_blocks(read_text(json_path))
    side, st_j, basis = choose_side_json(lines_j, blocks_j)
    write_text(json_path, st_j)
    lines_m, blocks_m = parse_blocks(read_text(md_path))
    st_m = side_text(lines_m, blocks_m, side)
    if has_linestart_marker(st_m):
        raise ValueError("%s: md member dirty on side %s" % (md_path, side))
    write_text(md_path, st_m)
    receipt["files"][json_path] = {"strategy": "twin-clock", "side": side,
                                   "basis": basis, "blocks": len(blocks_j)}
    receipt["files"][md_path] = {"strategy": "twin-locked", "side": side,
                                 "blocks": len(blocks_m)}


def resolve_history_union(path):
    lines, blocks = parse_blocks(read_text(path))
    o = json.loads(side_text(lines, blocks, "s1"))
    t = json.loads(side_text(lines, blocks, "s2"))
    ho, ht = o.get("history", []), t.get("history", [])
    seen = {}
    for r in ho + ht:
        k = (str(r.get("ts", "")), str(r.get("machine", "")))
        if k not in seen or str(r) > str(seen[k]):
            seen[k] = r
    merged = sorted(seen.values(), key=lambda r: str(r.get("ts", "")))
    base = t if max_ts(json.dumps(t)) > max_ts(json.dumps(o)) else o
    base["history"] = merged
    st = json.dumps(base, ensure_ascii=False, indent=1) + "\n"
    json.loads(st)
    write_text(path, st)
    receipt["files"][path] = {"strategy": "history-union-zero-loss",
                              "s1_rows": len(ho), "s2_rows": len(ht),
                              "merged_rows": len(merged)}


def resolve_key_union(path):
    lines, blocks = parse_blocks(read_text(path))
    o = json.loads(side_text(lines, blocks, "s1"))
    t = json.loads(side_text(lines, blocks, "s2"))

    def merge(a, b):
        if isinstance(a, dict) and isinstance(b, dict):
            out = dict(a)
            for k, v in b.items():
                out[k] = merge(out[k], v) if k in out else v
            return out
        ta, tb = max_ts(str(a)), max_ts(str(b))
        if ta and tb:
            return b if ts_norm(tb) > ts_norm(ta) else a
        return a

    st = json.dumps(merge(o, t), ensure_ascii=False, indent=1) + "\n"
    json.loads(st)
    write_text(path, st)
    receipt["files"][path] = {"strategy": "per-key-union"}


def resolve_jsonl_union(path):
    lines, blocks = parse_blocks(read_text(path))
    st = block_union(lines, blocks)
    for ln in st.split("\n"):
        if ln.strip():
            json.loads(ln)
    write_text(path, st)
    receipt["files"][path] = {"strategy": "in-block-union-dedupe(r294)",
                              "blocks": len(blocks)}


def resolve_codely(path):
    lines, blocks = parse_blocks(read_text(path))
    st = block_union(lines, blocks)
    n_ours = st.count("[2026-10-05 06:1x r517 bm-c]")
    n_516 = st.count("[2026-10-05 05:5x r516 bm-c]")
    if n_ours != 1 or n_516 < 1:
        raise ValueError("CODELY union assertion failed r517=%d r516=%d"
                         % (n_ours, n_516))
    write_text(path, st)
    receipt["files"][path] = {"strategy": "block-union-append-only",
                              "blocks": len(blocks), "r517_entries": n_ours}


def resolve_paper(path):
    lines, blocks = parse_blocks(read_text(path))
    d1 = json.loads(side_text(lines, blocks, "s1"))
    d2 = json.loads(side_text(lines, blocks, "s2"))
    c1, c2 = json_top_ts(d1), json_top_ts(d2)
    if c1 and c2 and ts_norm(c1) != ts_norm(c2):
        base, other = (d1, d2) if ts_norm(c1) > ts_norm(c2) else (d2, d1)
    else:
        m1, m2 = max_ts(json.dumps(d1)), max_ts(json.dumps(d2))
        if not m1 and not m2:
            raise ValueError("paper no-ts both sides -- refusing blind pick")
        base, other = (d1, d2) if (ts_norm(m1) >= ts_norm(m2) if m2 else True) \
            else (d2, d1)
    spliced = 0
    if isinstance(base, dict) and isinstance(other, dict):
        for k, v in other.items():
            if isinstance(v, list) and isinstance(base.get(k), list) \
                    and len(v) > len(base[k]):
                have = {json.dumps(x, ensure_ascii=False, sort_keys=True)
                        for x in base[k]}
                for item in v:
                    ij = json.dumps(item, ensure_ascii=False, sort_keys=True)
                    if ij not in have:
                        base[k].append(item)
                        spliced += 1
    st = json.dumps(base, ensure_ascii=False, indent=1) + "\n"
    json.loads(st)
    write_text(path, st)
    receipt["files"][path] = {"strategy": "paper-newer-base+list-splice",
                              "spliced": spliced}


TWINS = [
    ("docs/daily_report/REPORT-2026-10-05.json", "docs/daily_report/REPORT-2026-10-05.md"),
    ("docs/live_usage/LIVE-2026-10-05.json", "docs/live_usage/LIVE-2026-10-05.md"),
    ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"),
]
PAPER = ["results/paper/" + f for f in (
    "COMPOSITE-CE-01_paper.json", "COMPOSITE-CE-02_paper.json",
    "DROUGHT-CE-01_paper.json", "ENGULF-CE-01_paper.json",
    "NEEDLE-DE-01_paper.json", "VOLATILITY-CE-01_paper.json")]
DAEMON_OURS = [
    "results/autofill_state.bm-c.json",
    "results/dispatcher_state.bm-c.json",
    "results/token_usage.bm-c.json",
    "results/saturation_engine/face_bm-c.json",
    "results/saturation_engine_state.bm-c.json",
]
REGEN = [
    "results/_attrition_guard_scan.json",
    "results/compute_audit.bm-c.json",
    "results/daily_scorecard.json",
    "results/fund_premium_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.bm-c.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.bm-c.json",
    "results/lhb_update_status.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.bm-c.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/update_status.bm-c.json",
    "results/update_status.json",
]
JSONL_UNION = ["results/x2_watch_log.jsonl", "results/post_review.jsonl"]


def phase_absorb():
    """Dynamic absorb: whatever bm-c daemon faces churned since last commit
    (results/* + Tools/_r517* only -- anti-swallow restriction stays)."""
    rc, st, _ = git("status", "--porcelain")
    faces = []
    for l in st.splitlines():
        if not l.strip():
            continue
        path = l[3:].strip().strip('"')
        if path.startswith("results/") or path.startswith("Tools/_r517"):
            faces.append(path)
    if not faces:
        log("ABSORB nothing to absorb")
        return True
    for f in faces:
        rc, out, err = git("add", "--", f)
        if rc != 0:
            log("ABSORB-ADD-FAIL %s %s" % (f, err[:120]))
            return False
    rc, out, err = git("commit", "-m",
                       "churn-absorb r517: dynamic daemon faces (r620 law, "
                       "pre-rebase absorb)")
    log("ABSORB-COMMIT rc=%d %s" % (rc, (out or err).strip()[:120]))
    return rc == 0


def phase_pull_rebase():
    for attempt in (1, 2, 3):
        rc, out, err = git("pull", "--rebase", "origin", "main")
        log("PULL-REBASE#%d rc=%d %s" % (attempt, rc,
            (out or err).strip()[:200]))
        if rc == 0:
            receipt["phases"]["pull"] = "clean"
            return "clean"
        if "have unstaged changes" in (out + err) or \
                "cannot pull" in (out + err):
            rc2, st, _ = git("status", "--porcelain")
            dirty = [l for l in st.splitlines()
                     if l.strip() and l[3:].strip().startswith("results/")]
            log("unstaged churn mid-window: %s" % dirty)
            if not phase_absorb():
                return "fail"
            continue
        rc3, uu, _ = git("ls-files", "-u")
        if uu.strip():
            receipt["phases"]["pull"] = "conflicts"
            return "conflicts"
        log("pull rc!=0 zero-UU unexpected: %s" % err[:200])
        return "fail"
    return "fail"


def phase_resolve():
    rc, out, _ = git("diff", "--name-only", "--diff-filter=U")
    uu = [p for p in out.split("\n") if p.strip()]
    log("UU set (%d): %s" % (len(uu), sorted(uu)))
    receipt["uu_count"] = len(uu)
    done = set()
    for j, m in TWINS:
        if j in uu:
            resolve_twin(j, m)
            done.update((j, m))
    if "results/dashboard_status.json" in uu and \
            "results/dashboard_status.js" in uu:
        resolve_twin("results/dashboard_status.json", "results/dashboard_status.js")
        done.update(("results/dashboard_status.json",
                     "results/dashboard_status.js"))
    if "CODELY.md" in uu:
        resolve_codely("CODELY.md")
        done.add("CODELY.md")
    for p in PAPER:
        if p in uu:
            resolve_paper(p)
            done.add(p)
    for p in DAEMON_OURS:
        if p in uu:
            resolve_daemon_ours(p)
            done.add(p)
    if "results/compute_audit.json" in uu:
        resolve_history_union("results/compute_audit.json")
        done.add("results/compute_audit.json")
    if "results/token_usage.json" in uu:
        resolve_key_union("results/token_usage.json")
        done.add("results/token_usage.json")
    for p in JSONL_UNION:
        if p in uu:
            resolve_jsonl_union(p)
            done.add(p)
    for p in REGEN:
        if p in uu and p not in done:
            resolve_regen(p)
            done.add(p)
    leftover = [p for p in uu if p not in done]
    for p in leftover:
        receipt["errors"].append("UNHANDLED: " + p)
    for p in sorted(done):
        if not os.path.exists(os.path.join(ROOT, p)):
            receipt["errors"].append("MISSING after write: " + p)
            continue
        if has_linestart_marker(read_text(p)):
            receipt["errors"].append("MARKER REMAINS: " + p)
    receipt["resolved"] = sorted(done)
    receipt.setdefault("pick_windows", []).append(sorted(done))
    log("RESOLVED %d/%d UU; errors=%d" % (len(done), len(uu),
        len(receipt["errors"])))
    return len(receipt["errors"]) == 0


def phase_add_continue():
    # atomic window: add all resolved faces + continue in one breath
    # (r516 treadmill law: 分步跑必被再 tick 挡)
    rc, out, err = git("add", "-A", "--", ".")
    if rc != 0:
        log("ADD-ALL-FAIL %s" % err[:160])
        return False
    rc, out, err = git("rebase", "--continue")
    log("REBASE-CONTINUE rc=%d %s" % (rc, (out or err).strip()[:200]))
    if rc != 0:
        rc2, uu, _ = git("ls-files", "-u")
        rc3, st, _ = git("status", "--porcelain")
        log("post-continue UU=%d dirty-tail:" % len(uu.splitlines()))
        log(st.strip()[-300:])
        return False
    return True


def phase_push_verify():
    p = subprocess.run([sys.executable, "Tools/push_verify.py"],
                       capture_output=True, creationflags=CREATE_NO_WINDOW,
                       cwd=ROOT)
    log("PUSH_VERIFY rc=%d" % p.returncode)
    log((p.stdout or b"").decode("utf-8", "replace").strip()[-500:])
    verr = (p.stderr or b"").decode("utf-8", "replace").strip()
    if verr:
        log("PV-STDERR " + verr[-200:])
    return p.returncode == 0


def main():
    if not phase_absorb():
        log("PHASE-ABSORB-FAIL -> stop (manual window)")
        return 1
    state = phase_pull_rebase()
    if state == "clean":
        receipt["phases"]["resolve"] = "not-needed"
        receipt["phases"]["continue"] = "not-needed"
        ok = phase_push_verify()
    elif state == "conflicts":
        guard = 0
        while guard < 6:
            guard += 1
            if not phase_resolve():
                log("RESOLVE-ERRORS -> stop (manual window), rebase left open")
                return 2
            if not phase_add_continue():
                rc2, uu, _ = git("ls-files", "-u")
                if uu.strip():
                    log("stopped at next pick window (UU=%d) -> resolve "
                        "loop continues" % len(uu.splitlines()))
                    continue
                log("CONTINUE-FAIL (non-pick) -> stop, rebase state:")
                return 3
            receipt["phases"]["continue"] = "ok (windows=%d)" % guard
            break
        else:
            log("PICK-WINDOW-GUARD-EXHAUSTED -> stop")
            return 3
        ok = phase_push_verify()
    else:
        log("PULL-FAIL -> stop (manual window)")
        return 4
    rc, head, _ = git("rev-parse", "HEAD")
    rc2, behind, _ = git("rev-list", "--count", "HEAD..origin/main")
    rc3, ahead, _ = git("rev-list", "--count", "origin/main..HEAD")
    receipt["phases"]["push_verify"] = "DELIVERED" if ok else "NOT-DELIVERED"
    receipt["head"] = head.strip()
    receipt["behind"] = behind.strip()
    receipt["ahead"] = ahead.strip()
    log("HEAD %s behind=%s ahead=%s delivered=%s" %
        (head.strip()[:12], behind.strip(), ahead.strip(), ok))
    json.dump(receipt, io.open(os.path.join(
        ROOT, "results", "_r517bmc_rebase_resolve.json"), "w",
        encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    io.open(os.path.join(ROOT, "results", "_r517bmc_rebase_resolve.log"),
            "w", encoding="utf-8", newline="\n").write("\n".join(log_lines))
    return 0 if ok else 5


if __name__ == "__main__":
    sys.exit(main())
