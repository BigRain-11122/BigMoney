# r315 bm-c dance resolver v3: UU faces from cherry-pick of round commit onto origin tip
# Laws applied: CODELY = entry-union at EOF (de-facto append-at-end); JSON derive faces =
# deep-ts probe take-newer, fallback take-theirs(mine, freshest by round-session construction);
# ALL writes = raw blob bytes from the chosen git stage (zero re-serialization, r289/r509 format laws).
# v3.1: BASE from argv[1] (re-pick cycles pass the new merge-base); ts tie -> theirs.
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
BASE = sys.argv[1] if len(sys.argv) > 1 else "84cc68234"
TS_KEYS = ("ts", "generated", "generated_at", "updated", "updated_at", "asof", "date", "timestamp")

UU = [
    "CODELY.md",
    "docs/daily_report/REPORT-2026-10-01.json",
    "docs/daily_report/REPORT-2026-10-01.md",
    "docs/live_usage/LIVE-2026-10-01.json",
    "docs/live_usage/LIVE-2026-10-01.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]


def show(ref):
    try:
        return subprocess.check_output(["git", "-C", REPO, "show", ref])
    except subprocess.CalledProcessError:
        return None


def probe_ts(raw):
    import json
    try:
        d = json.loads(raw.decode("utf-8"))
    except Exception:
        return None, None
    if not isinstance(d, dict):
        return "list", len(d) if isinstance(d, list) else -1
    for k in TS_KEYS:
        v = d.get(k)
        if isinstance(v, str) and v:
            return "dict-ts", v
    return "dict-nots", None


def main():
    # auto-detect UU set from index (re-race cycles may present a different conflict set)
    st = subprocess.check_output(["git", "-C", REPO, "status", "--porcelain"]).decode("utf-8")
    uu_paths = [l[3:].strip() for l in st.splitlines() if l.startswith("UU ")]
    assert uu_paths, "no UU conflicts detected -- nothing to resolve"
    log = []
    for path in uu_paths:
        ours = show(":2:" + path)
        theirs = show(":3:" + path)
        assert ours is not None and theirs is not None, f"stage missing for {path}"
        if path == "CODELY.md":
            base = show(f"{BASE}:CODELY.md").decode("utf-8")
            o = ours.decode("utf-8")
            t = theirs.decode("utf-8")
            bl, ol, tl = base.splitlines(), o.splitlines(), t.splitlines()
            base_s, ours_s = set(bl), set(ol)
            theirs_new = [l for l in tl if l not in base_s and l not in ours_s and l.strip()]
            assert theirs_new, "no new entries on theirs side for CODELY -- unexpected"
            dup = [l for l in theirs_new if l in o]
            assert not dup, f"CODELY theirs_new already present in ours: {dup[:1]}"
            out = o
            if not out.endswith("\n"):
                out += "\n"
            out += "\n" + "\n".join(theirs_new)
            if t.endswith("\n"):
                out += "\n"
            with open(REPO + "\\" + path, "wb") as f:
                f.write(out.encode("utf-8"))
            log.append(f"{path}: UNION base={len(bl)} ours={len(ol)} theirs_new={len(theirs_new)}")
            continue
        shape_o, ts_o = probe_ts(ours)
        shape_t, ts_t = probe_ts(theirs)
        if shape_o == "list" or shape_t == "list":
            # append-only rows face: line-set union, ours rows first then theirs-new (r294 domain law)
            ol = ours.decode("utf-8").splitlines()
            tl = theirs.decode("utf-8").splitlines()
            os_ = set(ol)
            new = [l for l in tl if l not in os_ and l.strip()]
            body = "\n".join(ol + new)
            if theirs.decode("utf-8").endswith("\n"):
                body += "\n"
            with open(REPO + "\\" + path, "wb") as f:
                f.write(body.encode("utf-8"))
            log.append(f"{path}: ROWS-UNION ours={len(ol)} theirs_new={len(new)}")
            continue
        if ts_o and ts_t:
            take = "theirs" if ts_t >= ts_o else "ours"   # take NEWER ts; tie -> mine (round session freshest)
            why = f"ts-newer (ours {ts_o} vs theirs {ts_t})"
        else:
            take = "theirs"
            why = "no-ts-fallback-take-theirs(mine freshest by construction)"
        raw = theirs if take == "theirs" else ours
        with open(REPO + "\\" + path, "wb") as f:
            f.write(raw)
        log.append(f"{path}: TAKE-{take.upper()} shape={shape_o}/{shape_t} :: {why}")
    for line in log:
        print(line)


if __name__ == "__main__":
    main()
