# -*- coding: utf-8 -*-
"""R253 bm-a: push-rejection rebase batch resolver (13 UU, r242/r245 law family).

Push of round 253 rejected (bm-b r256 close 7282e1cd landed 15:09-15:10 window,
overlapping S6 chains on both machines) -> single pull --rebase -> 13 UU.
Side semantics (rebase): :2 ours = upstream bm-b face (S6 at 15:08-15:09),
:3 theirs = bm-a replayed round 253 face (S6 at 15:12-15:14, all probe ts
match local chain wallclock). Classifier: 11 classified + 2 UNKNOWN
(daily_report pair = same-day regenerated snapshot, r242 precedent: take-side
by json twin generated_at, md same side whole-byte).

Recipes (per SKILL.md, zero loss, fail-closed):
  take-3 whole bytes  : ts probe per file -- bm-a side newer on all 10
                        (meta.generated_at / generated / updated / ts keys probed
                        from both blobs, non-null before compare, r242 law)
  union, line-level   : CODELY.md (memory-union, both machines' entries kept)
  union, ledger       : compute_audit.json history + regime_state.json
                        history/transitions (dedupe by canonical row json,
                        |union| == |A set-union B| asserted) + state fields
                        take-new by ts; write-back format self-calibrated by
                        round-trip match against the :3 blob (indent/EOL/ascii)
Exit 0 = all resolved + verified + written + git add staged.
Exit 2 = any probe/verify failure, nothing staged (fail-closed).
"""
import json
import subprocess
import sys

ROOT = "\\".join(__file__.split("\\")[:-2])

TAKE3 = [
    ("results/dashboard_status.json", "meta.generated_at"),
    ("results/dashboard_status.js", None),  # twin of dashboard_status.json
    ("results/token_usage.json", "generated"),
    ("results/update_status.json", "updated"),
    ("results/futures_update_status.json", "ts"),
    ("results/heat_update_status.json", "updated"),
    ("results/lhb_update_status.json", "updated"),
    ("results/fundamental_b_layer_filter.json", "updated"),
    ("docs/daily_report/REPORT-2026-09-26.json", "generated_at"),
    ("docs/daily_report/REPORT-2026-09-26.md", None),  # same side as json twin
]


def blob(side, path):
    r = subprocess.run(["git", "show", f":{side}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"blob read fail {side}:{path}: {r.stderr[:200]!r}")
    return r.stdout


def dig(doc, dotted):
    cur = doc
    for k in dotted.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def canon(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False)


def main():
    fails = []
    resolved = {}

    # ---- take-side-3 snapshots (probe ts both sides, non-null, newer wins) --
    json_ts = None
    for path, key in TAKE3:
        b2, b3 = blob(2, path), blob(3, path)
        if key is None:
            side, why = 3, "twin/pair-follows-json-side (r242 law)"
        else:
            d2, d3 = json.loads(b2), json.loads(b3)
            t2, t3 = dig(d2, key), dig(d3, key)
            if t2 is None or t3 is None:
                fails.append(f"{path}: ts key {key!r} absent (t2={t2!r} t3={t3!r}) "
                             "-> UNKNOWN manual, no blind take")
                continue
            if t3 >= t2:
                side, why = 3, f"{key} {t3} >= {t2}"
            else:
                side, why = 2, f"{key} {t2} > {t3}"
        if path.endswith("REPORT-2026-09-26.json"):
            json_ts = (side, dig(json.loads(b3 if side == 3 else b2), key))
        if path == "results/dashboard_status.json" and side != 3:
            # js twin must follow the json twin side regardless of order
            pass
        resolved[path] = (side, b3 if side == 3 else b2, why)
        if path.endswith(".json") and side == 3:
            pass

    # dashboard twin-side coherence check
    djs = next(p for p, k in TAKE3 if p.endswith("dashboard_status.json"))
    djs_side = resolved[djs][0]
    js_side = resolved["results/dashboard_status.js"][0]
    if djs_side != js_side:
        fails.append(f"dashboard js twin side {js_side} != json side {djs_side}")
    # daily report pair coherence
    rj = resolved["docs/daily_report/REPORT-2026-09-26.json"][0]
    rm = resolved["docs/daily_report/REPORT-2026-09-26.md"][0]
    if rj != rm:
        fails.append(f"daily report pair sides differ json={rj} md={rm}")

    # ---- CODELY.md line-level union ----
    c2 = blob(2, "CODELY.md").decode("utf-8")
    c3 = blob(3, "CODELY.md").decode("utf-8")
    l2 = [l.rstrip("\r") for l in c2.splitlines()]
    l3 = [l.rstrip("\r") for l in c3.splitlines()]
    seen = set(l2)
    union = l2 + [l for l in l3 if l not in seen and l.strip()]
    dup = len(l2) + len([l for l in l3 if l not in seen and l.strip()])
    if len(union) != dup:
        fails.append(f"CODELY union line count {len(union)} != {dup}")
    resolved["CODELY.md"] = ("union", "\n".join(union) + "\n",
                             f"lines {len(l2)}+{len(union)-len(l2)} "
                             f"(bm-b r256 entry + bm-a r253 entry)")

    # ---- compute_audit.json: history union + latest take-new ----
    a2, a3 = json.loads(blob(2, "results/compute_audit.json")), json.loads(
        blob(3, "results/compute_audit.json"))
    h2, h3 = a2["history"], a3["history"]
    merged, keys = [], set()
    for row in h2 + h3:
        k = canon(row)
        if k not in keys:
            keys.add(k)
            merged.append(row)
    if len(merged) != len(set(canon(r) for r in h2) | set(canon(r) for r in h3)):
        fails.append("compute_audit history union != |A u B|")
    latest = a3["latest"] if (a3["latest"]["ts"] >= a2["latest"]["ts"]) else a2["latest"]
    out = {"latest": latest, "history": merged}
    fmt3 = blob(3, "results/compute_audit.json")
    for indent, ascii_ in ((2, False), (2, True)):
        s = json.dumps(out, ensure_ascii=ascii_, indent=indent)
        rt = json.dumps({"latest": a3["latest"], "history": h3},
                        ensure_ascii=ascii_, indent=indent)
        if rt == fmt3.decode("utf-8"):
            break
    else:
        fails.append("compute_audit self-calibration failed (no format match)")
        s = json.dumps(out, ensure_ascii=False, indent=2)
    resolved["results/compute_audit.json"] = (
        "union", s, f"history {len(h2)}|{len(h3)} -> {len(merged)} "
        f"(loss {len(h2)+len(h3)-len(merged)} dupes), latest ts {latest['ts']}")

    # ---- regime_state.json: lists union + state fields take-new ----
    r2, r3 = json.loads(blob(2, "results/regime_state.json")), json.loads(
        blob(3, "results/regime_state.json"))
    out = dict(r3)  # state fields take-new (bm-a updated 15:13:04 > 15:08:45)
    if r3["updated"] < r2["updated"]:
        fails.append("regime take-new side assumption broken")
    for lk in ("history", "transitions"):
        merged, keys = [], set()
        for row in r2[lk] + r3[lk]:
            k = canon(row)
            if k not in keys:
                keys.add(k)
                merged.append(row)
        if len(merged) != len(set(canon(x) for x in r2[lk]) | set(canon(x) for x in r3[lk])):
            fails.append(f"regime {lk} union != |A u B|")
        out[lk] = merged
    fmt3 = blob(3, "results/regime_state.json").decode("utf-8")
    s = None
    for indent, ascii_ in ((2, False), (2, True)):
        rt = json.dumps(r3, ensure_ascii=ascii_, indent=indent)
        if rt == fmt3:
            s = json.dumps(out, ensure_ascii=ascii_, indent=indent)
            break
    if s is None:
        fails.append("regime self-calibration failed")
        s = json.dumps(out, ensure_ascii=False, indent=2)
    resolved["results/regime_state.json"] = (
        "union", s, f"updated {out['updated']}, history "
        f"{len(r2['history'])}|{len(r3['history'])} -> {len(out['history'])}, "
        f"transitions -> {len(out['transitions'])}")

    if fails:
        print(json.dumps({"resolver": "FAIL", "fails": fails},
                         ensure_ascii=False, indent=1))
        return 2

    # ---- write back + parse-verify + stage ----
    report = []
    for path, (mode, content, why) in sorted(resolved.items()):
        data = content.encode("utf-8") if isinstance(content, str) else content
        with open(path, "wb") as fh:
            fh.write(data)
        if path.endswith(".json"):
            json.loads(open(path, "rb").read())  # r185 law: parse before add
        subprocess.run(["git", "add", "--", path], check=True)
        report.append({"path": path, "mode": mode, "why": why,
                       "bytes": len(data)})
    print(json.dumps({"resolver": "PASS", "resolved": report},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
