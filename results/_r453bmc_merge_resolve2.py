"""r453 bm-c merge-resolve2: 15 UU faces per r440/r450/r652 recipes (2nd race iter).

Honest-ts survey (results/_r453bmc_uu2_survey.py): bm-b r656 S6 regen wave
08:04-08:06 > our r453 wave 08:00-08:02 on ALL regen faces, same evidence
cutoff 2026-09-30 -> take-THEIRS by honest ts (zero info loss, newest regen).
- 12 regen faces (json+md twins) -> checkout --theirs
- compute_audit.json -> cross-machine union by entry identity, latest=newest ts
- token_usage.json -> per-machine union
- CODELY.md -> append-union, chronological by leading [date HH:MM marker
Guards: zero-marker 15/15 + JSON reparse + union asserts + CODELY both-sides.
"""
import json
import re
import subprocess

TAKE_THEIRS = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/update_status.json",
]
UNION_AUDIT = "results/compute_audit.json"
UNION_TOKEN = "results/token_usage.json"
UNION_CODELY = "CODELY.md"
ALL = TAKE_THEIRS + [UNION_AUDIT, UNION_TOKEN, UNION_CODELY]


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
    receipt = {"round": "r453 bm-c merge-resolve2 (2nd race iter)", "take_theirs": len(TAKE_THEIRS), "resolutions": {}}

    for p in TAKE_THEIRS:
        run(["git", "checkout", "--theirs", "--", p])
        receipt["resolutions"][p] = "theirs (newer-ts regen 08:04-08:06 > ours 08:00-08:02, survey-verified)"

    # compute_audit.json cross-machine union
    ours = json.loads(show(2, UNION_AUDIT).decode("utf-8"))
    theirs = json.loads(show(3, UNION_AUDIT).decode("utf-8"))
    oh, th = ours.get("history", []), theirs.get("history", [])
    seen, union = set(), []
    for e in th + oh:
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
    gen_o = str(ours.get("generated", ""))
    gen_t = str(theirs.get("generated", ""))
    merged = dict(theirs if gen_t > gen_o else ours)  # newest top-level
    merged["machines"] = merged_m
    with open(UNION_TOKEN, "w", encoding="utf-8", newline="") as fh:
        json.dump(merged, fh, ensure_ascii=False, indent=1)
    receipt["resolutions"][UNION_TOKEN] = f"per-machine union machines ours={sorted(om.keys())} +theirs-keys={sorted(tm.keys())} top-gen={max(gen_o, gen_t)}"

    # CODELY.md append-union, chronological by leading marker
    ours_txt = show(2, UNION_CODELY).decode("utf-8")
    theirs_txt = show(3, UNION_CODELY).decode("utf-8")
    ol, tl = ours_txt.split("\n"), theirs_txt.split("\n")
    i = 0
    while i < min(len(ol), len(tl)) and ol[i] == tl[i]:
        i += 1
    ours_suffix = [l for l in ol[i:] if l.strip()]
    theirs_suffix = [l for l in tl[i:] if l.strip()]
    assert ours_suffix, f"ours suffix empty (prefix={i})"
    assert theirs_suffix, f"theirs suffix empty (prefix={i})"
    assert i >= 50, f"common prefix suspiciously short: {i}"
    entries = theirs_suffix + ours_suffix
    marker_re = re.compile(r"^\- \[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})")
    if all(marker_re.match(e) for e in entries):
        entries.sort(key=lambda e: marker_re.match(e).group(1))
        order_note = "chronological"
    else:
        order_note = "theirs-then-ours (non-uniform markers, no sort)"
    resolved = ol[:i] + [""] + entries + [""]
    with open(UNION_CODELY, "w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(resolved))
    receipt["resolutions"][UNION_CODELY] = f"append-union prefix={i} theirs={len(theirs_suffix)} ours={len(ours_suffix)} ({order_note})"

    # stage all
    for p in ALL:
        run(["git", "add", "--", p])

    # guards: zero markers + JSON reparse + CODELY both sides
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
    assert "r453 bm-c" in codely_final and "bm-b" in codely_final, "CODELY union lost a side"
    receipt["guards"] = "zero-marker 15/15 + JSON reparse + CODELY both-sides PASS"
    print(json.dumps(receipt, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
