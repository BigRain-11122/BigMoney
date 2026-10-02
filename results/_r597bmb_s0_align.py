"""S0 pure-FF alignment driver for round 597 (bm-b), 2026-10-03 00:3x.

Laws applied: r585 pure-FF route, r569-iii full-40-char CAS, r593 execution-time
rev-parse, r570/r580/r388 append-only union (origin-verbatim base + local dict
lines, execution-time git show origin), r380/r388 porcelain parse (no whole-
output strip, XY two-column D test), r580 python subprocess argv (no PS path
passing), r578 reset --mixed re-anchor then face-split checkout.

Keep-local faces = bm-b-owned live-write faces + adopted predecessor work
(Tools/autofill.py r598 perf fix, PERPETUAL_N2_W15_PREREG r597 claim note) +
3 union jsonl outputs. Everything else M/D after reset -> checkout origin.
"""
import json
import os
import subprocess
import sys

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

KEEP_LOCAL = {
    "Tools/autofill.py",
    "research/PERPETUAL_N2_W15_PREREG.md",
    "results/autofill_state.bm-b.json",
    "results/compute_audit.bm-b.json",
    "results/token_usage.bm-b.json",
    "results/pool_dualrun.bm-b.jsonl",
    "results/update_status.bm-b.json",
    "results/futures_update_status.bm-b.json",
    "results/lhb_update_status.bm-b.json",
    "results/minute_feed_status.bm-b.json",
    "results/minute_feed_status.json",
    "results/regime_state.bm-b.json",
    "results/runnable_pool.bm-b.json",
    "results/saturation_engine/face_bm-b.json",
    "results/saturation_engine/history_bm-b.jsonl",
    "results/saturation_engine/state_bm-b.json",
    "results/etf_daily_pull_status.json",
    "results/astock_daily_update_status.json",
    "results/lowamp_deep_p1/nulls.jsonl",
    "results/pool_core_samples.jsonl",
    "results/pool_worker_ledger.jsonl",
    "results/post_review.jsonl",
}

UNION_FILES = [
    "results/pool_core_samples.jsonl",
    "results/pool_worker_ledger.jsonl",
    "results/post_review.jsonl",
]


def git(*args):
    r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True)
    return r.returncode, r.stdout, r.stderr


def main():
    # --- execution-time rev-parse (r593) ---
    rc, out, err = git("rev-parse", "HEAD")
    assert rc == 0, err
    head = out.decode().strip()
    rc, out, err = git("rev-parse", "origin/main")
    assert rc == 0, err
    origin = out.decode().strip()
    assert len(head) == 40 and len(origin) == 40, (head, origin)
    rc, out, _ = git("merge-base", "HEAD", "origin/main")
    mb = out.decode().strip()
    assert mb == head, "NOT pure FF: merge-base != HEAD"
    print(f"probe: head={head[:10]} origin={origin[:10]} pure-FF OK")

    # --- unions first (r580: before any tree move) ---
    for path in UNION_FILES:
        rc, ob, err = git("show", f"origin/main:{path}")
        assert rc == 0, (path, err)
        full = os.path.join(REPO, path)
        with open(full, "rb") as fh:
            lb = fh.read()
        crlf = lb.count(b"\r\n")
        lf_only = lb.count(b"\n") - crlf
        ln = lb.replace(b"\r\n", b"\n")
        origin_lines = ob.split(b"\n")
        if origin_lines and origin_lines[-1] == b"":
            origin_lines = origin_lines[:-1]
        origin_dict_n = 0
        for l in origin_lines:
            try:
                if isinstance(json.loads(l.decode("utf-8")), dict):
                    origin_dict_n += 1
            except Exception:
                pass
        seen = set(l for l in origin_lines if l.strip())
        local_lines = [l for l in ln.split(b"\n") if l.strip()]
        keep, dropped = [], 0
        for l in local_lines:
            if l in seen:
                continue
            try:
                obj = json.loads(l.decode("utf-8"))
            except Exception:
                dropped += 1
                continue
            if not isinstance(obj, dict):
                dropped += 1  # r570 dict-only gate
                continue
            keep.append(l)
            seen.add(l)
        base = ob if ob.endswith(b"\n") else ob + b"\n"
        merged = base + (b"".join(l + b"\n" for l in keep))
        # write in the local file's own EOL convention (r373 disk-face)
        if crlf > lf_only:
            merged = merged.replace(b"\n", b"\r\n")
        with open(full, "wb") as fh:
            fh.write(merged)
        print(
            f"union {path}: origin_lines={len(origin_lines)} "
            f"(dict {origin_dict_n}) + local_new={len(keep)} "
            f"dropped_non_dict_or_frag={dropped} "
            f"eol={'CRLF' if crlf > lf_only else 'LF'}"
        )

    # --- FF move: CAS update-ref + reset --mixed (r569-iii, r578) ---
    rc, _, err = git("update-ref", "refs/heads/main", origin, head)
    assert rc == 0, ("update-ref CAS failed (daemon commit raced?):", err)
    rc, _, err = git("reset", "--mixed", origin)
    assert rc == 0, err
    print(f"ff: main {head[:10]} -> {origin[:10]} (reset --mixed done)")

    # --- face-split checkout (r578/r580) ---
    rc, out, _ = git("status", "--porcelain")
    # r380: never strip whole output; per-line only
    lines = out.decode("utf-8", errors="replace").split("\n")
    restore, d_cnt, skipped = [], 0, []
    for line in lines:
        if len(line) < 4:
            continue
        xy = line[:2]
        path = line[3:]
        if xy == "??":
            continue
        if path in KEEP_LOCAL:
            skipped.append(path)
            continue
        if "D" in xy:
            d_cnt += 1
        restore.append(path)
    if restore:
        rc, _, err = git("checkout", "--", *restore)
        assert rc == 0, ("checkout failed:", err[:2000])
    print(f"checkout: restored={len(restore)} (D faces={d_cnt}) kept_local={len(skipped)}")

    # --- verify: remaining M/D faces must be subset of KEEP_LOCAL ---
    rc, out, _ = git("status", "--porcelain")
    bad = []
    for line in out.decode("utf-8", errors="replace").split("\n"):
        if len(line) < 4 or line[:2] == "??":
            continue
        path = line[3:]
        if path not in KEEP_LOCAL:
            bad.append(line)
    assert not bad, ("non-keep M/D remain:", bad[:10])

    rc, out, _ = git("rev-list", "--count", "origin/main..HEAD")
    assert out.decode().strip() == "0", "ahead != 0 after FF"
    print("verify: remaining dirty faces all in KEEP_LOCAL; ahead=0")
    # untracked faces listed for r586 duplicate handling (driver does not delete)
    rc, out, _ = git("status", "--porcelain")
    unt = [l[3:] for l in out.decode("utf-8", errors="replace").split("\n") if l.startswith("??")]
    for u in unt:
        print(f"untracked: {u}")
    print("S0 ALIGN OK")


if __name__ == "__main__":
    main()
