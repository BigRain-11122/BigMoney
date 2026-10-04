"""r453 bm-c merge-resolve: 5 UU faces per r449/r450/r452 recipe.

Classification (ts-honest per r450 take-new-by-ts; ours 08:00-08:02 > theirs
07:42 on both regen faces, both derived from same evidence cutoff 2026-09-30):
- results/_attrition_guard_scan.json -> take-ours (regen scan snapshot 08:02:43 > 07:42:31)
- results/lhb_update_status.json -> take-ours (regen status 08:00:33 > 07:42:30)
- results/compute_audit.json -> cross-machine union by entry identity, latest=newest ts
- results/token_usage.json -> per-machine union (machines dict merge, per-machine ts)
- CODELY.md -> append-union: common-prefix + theirs 2 lines (r655 bm-b 07:3x/07:4x) + ours 1 line (r453 bm-c 08:04x)
Guards: post-resolve zero-marker scan on all 5 + JSON reparse + union asserts +
CODELY both-side-marker presence. Receipt printed to stdout (committed alongside).
"""
import json
import subprocess

TAKE_OURS = [
    "results/_attrition_guard_scan.json",
    "results/lhb_update_status.json",
]
UNION_AUDIT = "results/compute_audit.json"
UNION_TOKEN = "results/token_usage.json"
UNION_CODELY = "CODELY.md"
ALL = TAKE_OURS + [UNION_AUDIT, UNION_TOKEN, UNION_CODELY]


def run(args):
    r = subprocess.run(args, capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"FAIL {args}: {r.stderr.decode('utf-8', 'replace')[:300]}")


def show(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"FAIL show {stage}:{path}: {r.stderr.decode('utf-8', 'replace')[:200]}")
    return r.stdout


def main():
    receipt = {"round": "r453 bm-c merge-resolve", "take_ours": len(TAKE_OURS), "resolutions": {}}

    for p in TAKE_OURS:
        run(["git", "checkout", "--ours", "--", p])
        receipt["resolutions"][p] = "ours (newer-ts regen 08:00-08:02 > bm-b 07:42)"

    # compute_audit.json cross-machine union
    ours = json.loads(show(2, UNION_AUDIT).decode("utf-8"))
    theirs = json.loads(show(3, UNION_AUDIT).decode("utf-8"))
    oh, th = ours.get("history", []), theirs.get("history", [])
    seen, union = set(), []
    for e in th + oh:  # theirs first so ours entries win identity ties on later ts sort
        k = json.dumps(e, sort_keys=True, ensure_ascii=False)
        if k not in seen:
            seen.add(k)
            union.append(e)
    union.sort(key=lambda e: str(e.get("ts", "")))
    latest = union[-1] if union else ours.get("latest")
    merged = dict(ours)
    merged["history"] = union
    merged["latest"] = latest
    with open(UNION_AUDIT, "w", encoding="utf-8", newline="") as fh:
        json.dump(merged, fh, ensure_ascii=False, indent=1)
    receipt["resolutions"][UNION_AUDIT] = f"union hist {len(oh)}+{len(th)}->{len(union)} latest={str(latest.get('ts'))[:19]}"
    assert len(union) >= max(len(oh), len(th)), "union must cover both sides"

    # token_usage.json per-machine union
    ours = json.loads(show(2, UNION_TOKEN).decode("utf-8"))
    theirs = json.loads(show(3, UNION_TOKEN).decode("utf-8"))
    om, tm = ours.get("machines", {}), theirs.get("machines", {})
    merged_m = dict(om)
    for k, v in tm.items():
        if k not in merged_m:
            merged_m[k] = v
        else:
            def ts(x):
                return str(x.get("ts", x.get("updated", x.get("generated", ""))))
            if ts(v) > ts(merged_m[k]):
                merged_m[k] = v
    merged = dict(ours)  # ours top-level (newest generated 08:00:54)
    merged["machines"] = merged_m
    with open(UNION_TOKEN, "w", encoding="utf-8", newline="") as fh:
        json.dump(merged, fh, ensure_ascii=False, indent=1)
    receipt["resolutions"][UNION_TOKEN] = f"per-machine union machines ours={sorted(om.keys())} +theirs-keys={sorted(tm.keys())}"

    # CODELY.md append-union (common prefix + theirs entries + ours entry)
    ours_txt = show(2, UNION_CODELY).decode("utf-8")
    theirs_txt = show(3, UNION_CODELY).decode("utf-8")
    ol, tl = ours_txt.split("\n"), theirs_txt.split("\n")
    i = 0
    while i < min(len(ol), len(tl)) and ol[i] == tl[i]:
        i += 1
    ours_suffix = [l for l in ol[i:] if l.strip()]
    theirs_suffix = [l for l in tl[i:] if l.strip()]
    assert ours_suffix and all("r453 bm-c" in l for l in ours_suffix), f"ours suffix unexpected: {ours_suffix}"
    assert theirs_suffix and all("r655 bm-b" in l for l in theirs_suffix), f"theirs suffix unexpected: {theirs_suffix}"
    assert i >= 50, f"common prefix suspiciously short: {i}"
    resolved = ol[:i] + [""] + theirs_suffix + [""] + ours_suffix + [""]
    with open(UNION_CODELY, "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(resolved))
    receipt["resolutions"][UNION_CODELY] = f"append-union prefix={i} theirs={len(theirs_suffix)} ours={len(ours_suffix)} (chronological: bm-b 07:3x/07:4x then bm-c 08:04x)"

    # stage all
    for p in ALL:
        run(["git", "add", "--", p])

    # guards: zero markers + JSON reparse + both-side CODELY markers
    marker_hits = []
    for p in ALL:
        raw = open(p, "rb").read()
        for line in raw.split(b"\n"):
            if line.startswith(b"<<<<<<<") or line.startswith(b">>>>>>>"):
                marker_hits.append(p)
                break
        if p.endswith(".json"):
            json.loads(open(p, encoding="utf-8").read())
    assert not marker_hits, f"markers remain: {marker_hits}"
    codely_final = open(UNION_CODELY, encoding="utf-8").read()
    assert "r453 bm-c" in codely_final and "r655 bm-b" in codely_final, "CODELY union lost a side"
    receipt["guards"] = "zero-marker 5/5 + JSON reparse + CODELY both-sides PASS"
    print(json.dumps(receipt, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
