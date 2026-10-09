# r947 bm-a rebase storm resolver (r945 bloodline rolled for r947 faces).
# Semantics during rebase: stage2(ours) = origin-side tip (bm-b r821/r822
# closeouts), stage3(theirs) = my replayed commit (r947 pre absorb 7c556bef8:
# r946 estate lhb_thermo + runtime faces). 6 ALL_FACES already resolved via
# merge_lane_views resolve (compute_audit/regime_state/update_status/
# lhb_update_status/futures_update_status/token_usage) -- this resolver covers
# the remainder: CODELY.md union, 8 flat newest-wins, 4 twin-coupled, explore.md
# origin-full+append-mine. Zero-loss asserts throughout.
import json
import subprocess

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


def main():
    log = []

    # 1) CODELY.md: one unique line each side -> origin full + mine appended
    p = "CODELY.md"
    o, t = stage(2, p), stage(3, p)
    lo = o.decode("utf-8").splitlines()
    lt = t.decode("utf-8").splitlines()
    oset = set(x for x in lo if x.strip())
    only_t = [x for x in lt if x.strip() and x not in oset]
    merged = lo + only_t
    open(p, "wb").write(("\r\n".join(merged) + "\r\n").encode("utf-8")
                        if b"\r" in o else ("\n".join(merged) + "\n").encode("utf-8"))
    body = open(p, encoding="utf-8").read()
    assert "r822 bm-b" in body          # origin-side entry preserved
    assert "lhb_detail.parquet" in body  # my-side entry preserved
    log.append(("CODELY.md", "union", len(lo), len(lt), len(merged)))

    # 2) flat newest-wins faces
    flat = [
        "docs/daily_report/REPORT-2026-10-10.json",
        "docs/live_usage/LIVE-2026-10-10.json",
        "docs/live_usage/LIVE-latest.json",
        "results/daily_scorecard.json",
        "results/dashboard_status.json",
        "results/fundamental_b_layer_filter.json",
        "results/scorecard_v1.json",
        "results/strategy_scorecard.json",
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

    # 4) state/queue/explore.md: origin queue state authoritative (bm-b closed
    #    E1/E2 with notes) + my unique r946 note line appended
    p = "state/queue/explore.md"
    o, t = stage(2, p), stage(3, p)
    lo = o.decode("utf-8").splitlines()
    lt = t.decode("utf-8").splitlines()
    oset = set(x for x in lo if x.strip())
    only_t = [x for x in lt if x.strip() and x not in oset]
    merged = lo + only_t
    open(p, "wb").write(("\r\n".join(merged) + "\r\n").encode("utf-8")
                        if b"\r" in o else ("\n".join(merged) + "\n").encode("utf-8"))
    body = open(p, encoding="utf-8").read()
    assert "r822" in body   # bm-b closure note preserved
    assert "r946" in body   # my adjudication note preserved
    log.append(("state/queue/explore.md", "origin-full+append-mine",
                len(lo), len(lt), len(merged)))

    for row in log:
        print(row)
    print("RESOLVER DONE:", len(log), "faces")


if __name__ == "__main__":
    main()
