"""r278 bm-c rebase wave-1 resolver (13-UU vs bm-a r479 S6 same-window lane).

Replay of round-277 commit (0b4635ed3 content) onto origin/main cd28cd595.
All 13 faces = shared snapshot family (F-20260927-06 structural face).
Helpers deep_ts/take_new_snapshot/twin/raw/write are VERBATIM from the r277/r478
canon resolver (禁重写律: canon mechanism reuse; r100 value-shape gate, r311 deep
scan, staged-only idempotence, twin-side coupling r329, SCORECARD twin same-side
forced per r274 four-twin-group precedent).
In rebase: :2 = origin side (bm-a r479, ~16:0x), :3 = replayed mine (~15:4x).
"""
import json
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def raw(stage: str, path: str) -> bytes:
    r = subprocess.run(["git", "show", f"{stage}:{path}"], capture_output=True)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError(f"blob read failed {stage}:{path} rc={r.returncode} err={r.stderr[:120]}")
    return r.stdout


def write(path: str, data: bytes):
    with open(path, "wb") as f:
        f.write(data)


def deep_ts(obj, out, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = k.lower().replace("_", "").replace("-", "")
            if isinstance(v, str) and v[:2] == "20" and (
                "ts" in kl or "generated" in kl or "updated" in kl or "asof" in kl or "at" == kl[-2:]
            ):
                if "T" in v or " " in v[10:]:
                    out[f"{prefix}/{k}"] = v
            deep_ts(v, out, f"{prefix}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:5]):
            deep_ts(v, out, f"{prefix}[{i}]")


def take_new_snapshot(path: str):
    o = json.loads(raw(':2', path))
    l = json.loads(raw(':3', path))
    to, tl = {}, {}
    deep_ts(o, to)
    deep_ts(l, tl)
    if not to and not tl:
        if raw(':2', path) == raw(':3', path):
            write(path, raw(':2', path))
            return "identical"
        raise RuntimeError(f"{path}: no ts probe, sides differ -- manual adjudication required")
    omax = max(to.values()) if to else ""
    lmax = max(tl.values()) if tl else ""
    side = ":2" if omax >= lmax else ":3"
    write(path, raw(side, path))
    return f"take {side} (o={omax} l={lmax})"


def twin(base_dir: str, stem: str):
    j, m = f"{base_dir}/{stem}.json", f"{base_dir}/{stem}.md"
    oj, lj = json.loads(raw(':2', j)), json.loads(raw(':3', j))
    og, lg = oj.get("generated_at", oj.get("generated", "")), lj.get("generated_at", lj.get("generated", ""))
    if not og or not lg:
        raise RuntimeError(f"twin {j}: no generated/generated_at probe on one side -- manual adjudication")
    side = ":2" if og >= lg else ":3"
    write(j, raw(side, j))
    write(m, raw(side, m))
    return f"twin {side} (o={og} l={lg})"


def main():
    log = []
    # snapshots: per-face ts probe decides side
    for p in ["results/_attrition_guard_scan.json", "results/dashboard_status.json",
              "results/futures_update_status.json", "results/lhb_update_status.json",
              "results/token_usage.json"]:
        log.append(f"{p}: {take_new_snapshot(p)}")
    # SCORECARD twin group (scorecard_v1.json + strategy_scorecard.json): same side forced
    # (r274 four-twin-group precedent; both written by the same strategy_scorecard.py run)
    sc = "results/strategy_scorecard.json"
    o, l = json.loads(raw(':2', sc)), json.loads(raw(':3', sc))
    to, tl = {}, {}
    deep_ts(o, to)
    deep_ts(l, tl)
    omax = max(to.values()) if to else ""
    lmax = max(tl.values()) if tl else ""
    side = ":2" if omax >= lmax else ":3"
    write(sc, raw(side, sc))
    write("results/scorecard_v1.json", raw(side, "results/scorecard_v1.json"))
    log.append(f"SCORECARD twin: take {side} (o={omax} l={lmax})")
    # docs twins
    log.append(twin("docs/daily_report", "REPORT-2026-09-30"))
    log.append(twin("docs/live_usage", "LIVE-2026-09-30"))
    log.append(twin("docs/live_usage", "LIVE-latest"))
    for line in log:
        print(line)
    print(f"\nOK wave-1 {len(log)} faces resolved")


if __name__ == "__main__":
    sys.exit(main())
