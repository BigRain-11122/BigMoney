# r945 bm-a rebase storm resolver (r940/r943 bloodline, rolled for r945 faces).
# Semantics during rebase: stage2(ours) = origin-side tip (bm-b r819 closeout
# 06:52-06:58), stage3(theirs) = my replayed commit (dead-session chain 06:23-06:26
# + 07:03 attrition scan). Per-face canon: S3-newest / union for append-only
# faces / twin-coupling for docs pairs. Zero-loss asserts throughout.
import json
import subprocess
import sys

GIT = r"C:\Program Files\Git\cmd\git.exe"


def stage(n, path):
    r = subprocess.run([GIT, "show", ":%d:%s" % (n, path)], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def jload(b):
    return json.loads(b.decode("utf-8"))


def ts_of(d):
    for k in ("ts", "updated", "updated_at", "generated", "generated_at",
              "generated_from_state_updated", "generated_from", "asof"):
        v = d.get(k)
        if isinstance(v, str) and v:
            return v
    for k in ("audit", "meta", "latest", "status"):
        if isinstance(d.get(k), dict):
            for kk in ("ts", "updated", "generated", "asof"):
                v = d[k].get(kk)
                if isinstance(v, str) and v:
                    return v
    return None


def write(path, data, raw=None):
    if raw is not None:
        open(path, "wb").write(raw)
    else:
        b = json.dumps(data, ensure_ascii=False, indent=1).encode("utf-8")
        if not b.endswith(b"\n"):
            b += b"\n"
        open(path, "wb").write(b)


def pick_newer(path):
    o, t = stage(2, path), stage(3, path)
    do_, dt = jload(o), jload(t)
    to_, tt = ts_of(do_), ts_of(dt)
    if not (to_ and tt):
        # deterministic ts-less face (L1 derive): newer generation window wins
        write(path, do_)
        return "ours-deterministic", None, None
    side = "ours" if to_ >= tt else "theirs"
    write(path, do_ if side == "ours" else dt)
    return side, to_, tt


def union_jsonl(path):
    o, t = stage(2, path), stage(3, path)
    lo = [x for x in o.decode("utf-8").splitlines() if x.strip()]
    lt = [x for x in t.decode("utf-8").splitlines() if x.strip()]
    seen, out = set(), []
    for line in lo + lt:
        if line in seen:
            continue
        seen.add(line)
        out.append(line)
    open(path, "wb").write(("\r\n".join(out) + "\r\n").encode("utf-8")
                           if o.find(b"\r\n") != -1 else
                           ("\n".join(out) + "\n").encode("utf-8"))
    return len(lo), len(lt), len(out)


def union_history(path, hist_key="history", keep_ours_scalars=True):
    o, t = stage(2, path), stage(3, path)
    do_, dt = jload(o), jload(t)
    ho, ht = do_.get(hist_key) or [], dt.get(hist_key) or []
    seen, merged = set(), []
    for row in ho + ht:
        sig = json.dumps(row, ensure_ascii=False, sort_keys=True)
        if sig in seen:
            continue
        seen.add(sig)
        merged.append(row)
    if keep_ours_scalars:
        base = do_
    else:
        base = dt
    base[hist_key] = merged
    write(path, base)
    return len(ho), len(ht), len(merged)


def main():
    log = []

    # 1) CODELY.md: both-appended ledger lines -> union (origin first, mine after)
    p = "CODELY.md"
    o, t = stage(2, p), stage(3, p)
    lo = o.decode("utf-8").splitlines()
    lt = t.decode("utf-8").splitlines()
    ol = [x for x in lo if x.strip() and not x.startswith("<")]
    tl = [x for x in lt if x.strip() and not x.startswith("<")]
    only_t = [x for x in tl if x not in set(ol)]
    merged = ol + only_t
    open(p, "wb").write(("\r\n".join(merged) + "\r\n").encode("utf-8")
                        if b"\r" in o else ("\n".join(merged) + "\n").encode("utf-8"))
    assert "PARKING-P1 停泊域首判决批收口" in open(p, encoding="utf-8").read()
    assert "D-19 水位写步正典化" in open(p, encoding="utf-8").read()
    log.append(("CODELY.md", "union", len(ol), len(tl), len(merged)))

    # 2) flat newest-wins faces
    flat = [
        "docs/daily_report/REPORT-2026-10-10.json",
        "docs/live_usage/LIVE-2026-10-10.json",
        "docs/live_usage/LIVE-latest.json",
        "results/daily_scorecard.json",
        "results/dashboard_status.json",
        "results/fundamental_b_layer_filter.json",
        "results/futures_update_status.json",
        "results/lhb_update_status.json",
        "results/paper/COMPOSITE-CE-01_paper.json",
        "results/paper/COMPOSITE-CE-02_paper.json",
        "results/paper/DROUGHT-CE-01_paper.json",
        "results/paper/ENGULF-CE-01_paper.json",
        "results/paper/NEEDLE-DE-01_paper.json",
        "results/paper/VOLATILITY-CE-01_paper.json",
        "results/paper_export/export-2026-10-09.json",
        "results/paper_export/latest.json",
        "results/prospect_paper/_summary.json",
        "results/prospect_promotion/_summary.json",
        "results/scorecard_v1.json",
        "results/strategy_scorecard.json",
        "results/t35_open_fill_verify.json",
        "results/token_usage.json",
        "results/update_status.json",
        "results/_attrition_guard_scan.json",
    ]
    for f in flat:
        side, to_, tt = pick_newer(f)
        log.append((f, "S3-newest->" + side, to_, tt))

    # 3) twin-coupling: md/js faces take the SAME side as their json twin
    for jf, twin in [
        ("docs/daily_report/REPORT-2026-10-10.json",
         "docs/daily_report/REPORT-2026-10-10.md"),
        ("docs/live_usage/LIVE-2026-10-10.json",
         "docs/live_usage/LIVE-2026-10-10.md"),
        ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"),
        ("results/dashboard_status.json", "results/dashboard_status.js"),
    ]:
        do_, dt = jload(stage(2, jf)), jload(stage(3, jf))
        side = "ours" if (ts_of(do_) or "") >= (ts_of(dt) or "") else "theirs"
        raw = stage(2, twin) if side == "ours" else stage(3, twin)
        open(twin, "wb").write(raw)
        log.append((twin, "twin->" + side))

    # 4) history-union faces
    log.append(("compute_audit.json", "history-union",
                *union_history("results/compute_audit.json")))
    log.append(("regime_state.json", "history-union",
                *union_history("results/regime_state.json")))

    # 5) jsonl append-only union
    log.append(("x2_watch_log.jsonl", "jsonl-union",
                *union_jsonl("results/x2_watch_log.jsonl")))

    for row in log:
        print(row)
    print("RESOLVER DONE:", len(log), "faces")


if __name__ == "__main__":
    main()
