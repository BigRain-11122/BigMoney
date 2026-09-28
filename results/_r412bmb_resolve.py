# -*- coding: utf-8 -*-
"""r412 bm-b rebase-conflict resolver (skill: bigmoney-conflict-resolve).

Face: round-412 harvest commit (dead-session S6 outputs + autofill v3-0of1
shard products, all written 06:0x local) replaying on top of origin/main
1615386d3 (bm-a r415 S6 completion, same-kind status writes 05:4x) +
bm-c worker claim commits. 6 UU, classifier verdicts:

  - results/compute_audit.json    rolling-ledger -> union history zero-loss
    (dedup ts+machine+flags identity, r188/R208) + latest take-new by deep
    nested ts probe (r311); producer format = indent=2 ensure_ascii=False
    (scripts/compute_audit.py L488 verified)
  - results/regime_state.json     rolling-ledger -> union history/transitions
    + state fields take-new; union degenerates to s3 history (both sides
    byte-identical 2 rows) -> whole doc equals s3 verbatim (asserted, no
    re-serialization)
  - results/{futures_update_status,lhb_update_status,update_status,
    token_usage}.json  snapshot -> take-new whole doc by deep ts probe
    (s3 local 06:02-06:06 > s2 origin 05:41-05:42 all four), blob verbatim

Rebase stage semantics (r411 law): stage2 = upstream/base (origin side),
stage3 = my replayed commit. Tie -> replay side.
"""
import json
import subprocess
import sys

ROOT = r"E:\Fluxgroup\FluxGroup\quant\bigmoney"


def blob(stage, path):
    out = subprocess.run(["git", "show", f":{stage}:{path}"], cwd=ROOT,
                         capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(f"git show :{stage}:{path} rc={out.returncode}")
    return out.stdout.decode("utf-8-sig")


def jload(stage, path):
    return json.loads(blob(stage, path))


def write(path, text):
    with open(path.replace("/", "\\"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(text)


def deepts(d):
    """Deep-scan nested 2026-prefixed wall-clock ts strings (r311 + R350
    time-of-day law: bare 10-char dates excluded)."""
    best = ""
    stack = [d]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            for k, v in cur.items():
                if isinstance(v, str) and v[:4] == "2026" and len(v) > 10 \
                        and (" " in v or "T" in v):
                    if v > best:
                        best = v
                elif isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(cur, list):
            stack.extend(x for x in cur if isinstance(x, (dict, list)))
    return best


def resolve_snapshot(path, probe_hint=None):
    """take-new whole doc by deep ts probe; tie -> replay side (s3)."""
    s2, s3 = blob(2, path), blob(3, path)
    t2, t3 = deepts(json.loads(s2)), deepts(json.loads(s3))
    side = 3 if t3 >= t2 else 2
    write(path, s3 if side == 3 else s2)
    return {"path": path, "ts_s2": t2, "ts_s3": t3, "took_stage": side}


def resolve_audit():
    s2, s3 = jload(2, "results/compute_audit.json"), \
        jload(3, "results/compute_audit.json")
    h2 = s2.get("history") or []
    h3 = s3.get("history") or []

    def ident(row):
        return (str(row.get("ts")), str(row.get("machine")),
                json.dumps(row.get("flags"), sort_keys=True))

    seen = {}
    for row in h2 + h3:
        seen.setdefault(ident(row), row)
    merged = sorted(seen.values(), key=lambda r: str(r.get("ts")))
    assert len(merged) >= max(len(h2), len(h3)), "union zero-loss violated"
    base = s3 if str(s3.get("latest", {}).get("ts", "")) >= \
        str(s2.get("latest", {}).get("ts", "")) else s2
    out = dict(base)
    out["history"] = merged
    text = json.dumps(out, ensure_ascii=False, indent=2) + "\n"
    write("results/compute_audit.json", text)
    return {"history_s2": len(h2), "history_s3": len(h3),
            "history_merged": len(merged),
            "latest_from": "s3" if base is s3 else "s2"}


def resolve_regime():
    s2b, s3b = blob(2, "results/regime_state.json"), \
        blob(3, "results/regime_state.json")
    s2, s3 = json.loads(s2b), json.loads(s3b)

    def row_ident(e):
        return (str(e.get("asof")), str(e.get("raw")), str(e.get("state")),
                str(e.get("green_streak")), str(e.get("days_in_state")))

    seen = {}
    for e in (s2.get("history") or []) + (s3.get("history") or []):
        seen.setdefault(row_ident(e), e)
    merged = sorted(seen.values(), key=lambda r: str(r.get("asof")))
    base = s3 if str(s3.get("updated", "")) >= str(s2.get("updated", "")) \
        else s2
    tseen = {}
    for t in (s2.get("transitions") or []) + (s3.get("transitions") or []):
        tseen.setdefault(json.dumps(t, sort_keys=True), t)
    out = dict(base)
    out["history"] = merged
    out["transitions"] = list(tseen.values())
    # degenerate check: if computed == s3 structurally, write s3 blob verbatim
    if base is s3 and out == s3:
        write("results/regime_state.json", s3b)
        verbatim = True
    else:
        write("results/regime_state.json",
              json.dumps(out, ensure_ascii=False, indent=1) + "\n")
        verbatim = False
    return {"history_merged": len(merged), "base": "s3" if base is s3
            else "s2", "verbatim_s3": verbatim}


def main():
    snaps = [resolve_snapshot(p) for p in (
        "results/futures_update_status.json",
        "results/lhb_update_status.json",
        "results/update_status.json",
        "results/token_usage.json",
    )]
    audit = resolve_audit()
    regime = resolve_regime()
    # parse-validate every written json (r185 law)
    for p in ("results/futures_update_status.json",
              "results/lhb_update_status.json",
              "results/update_status.json", "results/token_usage.json",
              "results/compute_audit.json", "results/regime_state.json"):
        with open(p.replace("/", "\\"), encoding="utf-8") as fh:
            json.load(fh)
    print(json.dumps({"snapshots": snaps, "audit": audit,
                      "regime": regime}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
