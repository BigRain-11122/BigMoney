"""r507 bm-c rebase conflict resolver v2 (r506 canon copy; replay onto 0ed3be165-era
origin tip during round-close push window).

Rebase semantics (r630/r627 law): side1 = "Updated upstream" = origin/main tip;
side2 = "<pick sha>" = our e52b86943 content. v1 false-negative lineage fixed in
r506 v2 (marker-label generic anchor, diff3 four-piece block order, worktree
sides, line-start residual assertions). Laws: r417 marker blocks; r405 single
source ts regex; r643/r433-2 twin regen top-clock both members same side;
r423-1 clean-side law; r510/r505-bmb same-day idempotent regen wall-clock
newer; r510-bma compute_audit history union (ts,machine) zero-loss; r294
in-block union dedupe. Receipt: results/_r507bmc_rebase_resolve.json + .log
"""
import io
import json
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE_NO_WINDOW = 0x08000000
TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?")
MARKERS = ("<<<<<<<", "|||||||", "=======", ">>>>>>>")

log_lines = []
receipt = {"round": "r507", "files": {}, "errors": []}


def log(msg):
    log_lines.append(str(msg))


def read_text(path):
    return io.open(os.path.join(ROOT, path), encoding="utf-8", errors="strict").read()


def write_text(path, text):
    io.open(os.path.join(ROOT, path), "w", encoding="utf-8", newline="").write(text)


def parse_blocks(text):
    lines = text.split("\n")
    n_open = sum(1 for ln in lines if ln.startswith("<<<<<<< "))
    n_close = sum(1 for ln in lines if ln.startswith(">>>>>>> "))
    n_base = sum(1 for ln in lines if ln.startswith("||||||| "))
    n_mid = sum(1 for ln in lines if ln.rstrip("\r") == "=======")
    if not (n_open == n_close == n_base == n_mid):
        raise ValueError("marker count mismatch open=%d close=%d base=%d mid=%d" % (n_open, n_close, n_base, n_mid))
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
        raise ValueError("block parse incomplete state=%d blocks=%d expected=%d" % (state, len(blocks), n_open))
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


def max_ts(text):
    hits = TS_RE.findall(text)
    return max(hits) if hits else ""


def ts_norm(s):
    return s[:10] + "T" + s[11:] if len(s) >= 12 and s[10] == " " else s


def side_newer(t1, t2):
    if not t2:
        return True
    if not t1:
        return False
    return ts_norm(t1) >= ts_norm(t2)


def has_linestart_marker(text):
    return any(ln.startswith(MARKERS) for ln in text.split("\n"))


def json_top_ts(doc):
    best = ""
    for k in ("generated_at", "generated", "updated_at", "updated", "now", "as_of", "ts"):
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
        d1, d2 = max_ts(side_text(lines, blocks, "s1")), max_ts(side_text(lines, blocks, "s2"))
        side = "s1" if side_newer(d1, d2) else "s2"
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
    receipt["files"][path] = {"strategy": "regen-take-newer", "side": side, "basis": basis,
                              "blocks": len(blocks)}


def resolve_twin(json_path, md_path):
    lines_j, blocks_j = parse_blocks(read_text(json_path))
    side, st_j, basis = choose_side_json(lines_j, blocks_j)
    write_text(json_path, st_j)
    lines_m, blocks_m = parse_blocks(read_text(md_path))
    st_m = side_text(lines_m, blocks_m, side)
    if has_linestart_marker(st_m):
        raise ValueError("%s: md member dirty on side %s" % (md_path, side))
    write_text(md_path, st_m)
    receipt["files"][json_path] = {"strategy": "twin-clock", "side": side, "basis": basis, "blocks": len(blocks_j)}
    receipt["files"][md_path] = {"strategy": "twin-locked", "side": side, "blocks": len(blocks_m)}


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
    receipt["files"][path] = {"strategy": "history-union-zero-loss", "s1_rows": len(ho),
                              "s2_rows": len(ht), "merged_rows": len(merged)}


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


TWINS = [
    ("docs/daily_report/REPORT-2026-10-05.json", "docs/daily_report/REPORT-2026-10-05.md"),
    ("docs/live_usage/LIVE-2026-10-05.json", "docs/live_usage/LIVE-2026-10-05.md"),
    ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"),
]
REGEN = [
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/update_status.json",
]


def main():
    out = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
                         cwd=ROOT, capture_output=True, text=True,
                         creationflags=CREATE_NO_WINDOW)
    uu = [p for p in out.stdout.split("\n") if p.strip()]
    log("UU set (%d): %s" % (len(uu), sorted(uu)))
    done = set()
    for j, m in TWINS:
        if j in uu:
            resolve_twin(j, m)
            done.update((j, m))
    if "results/dashboard_status.json" in uu and "results/dashboard_status.js" in uu:
        resolve_twin("results/dashboard_status.json", "results/dashboard_status.js")
        done.update(("results/dashboard_status.json", "results/dashboard_status.js"))
    if "results/compute_audit.json" in uu:
        resolve_history_union("results/compute_audit.json")
        done.add("results/compute_audit.json")
    if "results/token_usage.json" in uu:
        resolve_key_union("results/token_usage.json")
        done.add("results/token_usage.json")
    if "results/x2_watch_log.jsonl" in uu:
        log("x2_watch_log.jsonl in UU -- no jsonl union strategy wired this copy; manual review")
        receipt["errors"].append("UNHANDLED-JSONL: results/x2_watch_log.jsonl")
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
    receipt["uu_count"] = len(uu)
    receipt["resolved"] = sorted(done)
    json.dump(receipt, io.open(os.path.join(ROOT, "results", "_r507bmc_rebase_resolve.json"),
                               "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
    io.open(os.path.join(ROOT, "results", "_r507bmc_rebase_resolve.log"),
            "w", encoding="utf-8", newline="\n").write("\n".join(log_lines))
    print("RESOLVED %d/%d UU; errors=%d" % (len(done), len(uu), len(receipt["errors"])))


if __name__ == "__main__":
    main()
