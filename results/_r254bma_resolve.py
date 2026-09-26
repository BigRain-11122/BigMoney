# -*- coding: utf-8 -*-
"""R254 bm-a: push-rejection rebase batch resolver (13 UU, r242/r245/R208 law family).

Push of round 254 rejected (bm-b r257 close e5d5e2e8 landed 15:32:55 window,
overlapping S6 chains on both machines) -> single pull --rebase -> 13 UU.
Side semantics (rebase): :2 ours = upstream bm-b r257 face (S6 ~15:31-32),
:3 theirs = bm-a replayed round 254 face (S6 ~15:33-35).

Recipes (per SKILL.md, zero loss, fail-closed, exit 2 on any probe failure):
  take-side-3/2 whole bytes : ts probe per file (meta.generated_at / generated /
    updated / ts keys probed from both blobs, non-null before compare, r242 law);
    js twin follows json twin side; daily-report md twin follows json twin.
  l3_activation_table.json   : cells+canon byte-identical both sides (probed);
    only meta sha stamps differ -> take :3 (prereg_sha256_16 c2d1b990 ==
    committed tree L3_ACTIVATION_EVIDENCE.md sha16, verified pre-resolve);
    :2 prereg stamp references a dirty-tree read (6e881b69 != committed c2d1b990);
    source_prereg stamp refreshed post-rebase by market_clock_call.py re-run
    (idempotent same-day regenerate) -- addendum commit carries it.
  CODELY.md                  : line-level union (both machines' pit entries kept).
  compute_audit.json         : history union (|A u B| asserted) + latest take-new.
  regime_state.json          : history/transitions union + state fields take-new.
  autofill_state.json        : launches union -> ts ASC sort -> cap 50 -> re-sort
    ASC before write-back (r245 law); last_tick by inner ts whole-dict (no str());
    format mirrored from :3 blob (EOL/indent probed).
"""
import json
import subprocess
import sys

TAKE_TS = [
    ("results/dashboard_status.json", "meta.generated_at"),
    ("results/dashboard_status.js", None),  # twin of dashboard_status.json
    ("results/token_usage.json", "generated"),
    ("results/update_status.json", "updated"),
    ("results/futures_update_status.json", "ts"),
    ("results/heat_update_status.json", "updated"),
    ("results/lhb_update_status.json", "updated"),
    ("results/fundamental_b_layer_filter.json", "updated"),
    ("docs/daily_report/REPORT-2026-09-26.json", "generated_at"),
    ("docs/daily_report/REPORT-2026-09-26.md", None),  # twin follows json side
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

    # ---- take-side snapshots (probe ts both sides, non-null, newer wins) ----
    for path, key in TAKE_TS:
        b2, b3 = blob(2, path), blob(3, path)
        if key is None:
            side, why = None, "twin/pair-follows-json-side (r242 law)"
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
        if side is not None:
            resolved[path] = (f"take-{side}", b3 if side == 3 else b2, why)

    # twin-side coherence
    djs = resolved.get("results/dashboard_status.json")
    js = resolved.get("results/dashboard_status.js")
    if djs and js and not js[0].endswith(djs[0][-1]):
        fails.append(f"dashboard js twin side {js[0]} != json side {djs[0]}")
    rj = resolved.get("docs/daily_report/REPORT-2026-09-26.json")
    rm = resolved.get("docs/daily_report/REPORT-2026-09-26.md")
    if rj and rm and rj[0] != rm[0]:
        fails.append(f"daily report pair sides differ json={rj[0]} md={rm[0]}")

    # ---- l3_activation_table.json: take :3 (cells identical, prereg stamp
    #      matches committed tree; source stamp refreshed post-rebase) ----
    b2 = blob(2, "results/market_clock/l3_activation_table.json")
    b3 = blob(3, "results/market_clock/l3_activation_table.json")
    d2, d3 = json.loads(b2), json.loads(b3)
    if d2["cells"] != d3["cells"] or d2["canon"] != d3["canon"]:
        fails.append("l3 cells/canon unexpectedly differ (probe said identical)")
    else:
        resolved["results/market_clock/l3_activation_table.json"] = (
            "take-3", b3,
            "cells identical; prereg_sha16 c2d1b990 == committed L3 file; "
            "source stamp refreshed by post-rebase producer re-run")

    # ---- CODELY.md line-level union ----
    c2 = blob(2, "CODELY.md").decode("utf-8")
    c3 = blob(3, "CODELY.md").decode("utf-8")
    l2 = [l.rstrip("\r") for l in c2.splitlines()]
    l3 = [l.rstrip("\r") for l in c3.splitlines()]
    seen = set(l2)
    new3 = [l for l in l3 if l not in seen and l.strip()]
    union = l2 + new3
    resolved["CODELY.md"] = ("union", "\n".join(union) + "\n",
                             f"lines {len(l2)}+{len(new3)} "
                             f"(bm-b r256 EOL/transfer laws + bm-a R254 entry)")

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
    s = None
    for indent, ascii_ in ((2, False), (2, True)):
        rt = json.dumps({"latest": a3["latest"], "history": h3},
                        ensure_ascii=ascii_, indent=indent)
        if rt == fmt3.decode("utf-8"):
            s = json.dumps(out, ensure_ascii=ascii_, indent=indent)
            break
    if s is None:
        fails.append("compute_audit self-calibration failed (no format match)")
        s = json.dumps(out, ensure_ascii=False, indent=2)
    resolved["results/compute_audit.json"] = (
        "union", s, f"history {len(h2)}|{len(h3)} -> {len(merged)}, "
        f"latest ts {latest['ts']}")

    # ---- regime_state.json: lists union + state fields take-new ----
    r2, r3 = json.loads(blob(2, "results/regime_state.json")), json.loads(
        blob(3, "results/regime_state.json"))
    t2r, t3r = dig(r2, "updated"), dig(r3, "updated")
    if t2r is None or t3r is None:
        fails.append("regime updated ts absent")
    newer = r3 if (t3r or "") >= (t2r or "") else r2
    out = dict(newer)
    for lk in ("history", "transitions"):
        merged_l, keys_l = [], set()
        for row in r2[lk] + r3[lk]:
            k = canon(row)
            if k not in keys_l:
                keys_l.add(k)
                merged_l.append(row)
        if len(merged_l) != len(set(canon(x) for x in r2[lk]) | set(canon(x) for x in r3[lk])):
            fails.append(f"regime {lk} union != |A u B|")
        out[lk] = merged_l
    fmt3 = blob(3, "results/regime_state.json").decode("utf-8")
    s = None
    for indent, ascii_ in ((2, False), (2, True)):
        rt = json.dumps(newer, ensure_ascii=ascii_, indent=indent)
        if rt == fmt3:
            s = json.dumps(out, ensure_ascii=ascii_, indent=indent)
            break
    if s is None:
        fails.append("regime self-calibration failed")
        s = json.dumps(out, ensure_ascii=False, indent=2)
    resolved["results/regime_state.json"] = (
        "union", s, f"updated {out.get('updated')}, history "
        f"{len(r2['history'])}|{len(r3['history'])} -> {len(out['history'])}, "
        f"transitions -> {len(out['transitions'])}")

    # ---- autofill_state.json: launches union + last_tick by inner ts ----
    f2, f3 = json.loads(blob(2, "results/autofill_state.json")), json.loads(
        blob(3, "results/autofill_state.json"))
    la2, la3 = f2["launches"], f3["launches"]
    rows, seen_k = [], set()
    for row in la2 + la3:
        k = canon(row)
        if k not in seen_k:
            seen_k.add(k)
            rows.append(row)
    rows.sort(key=lambda r: r.get("ts", ""))
    n_uncapped = len(rows)
    rows = rows[-50:]  # cap 50 = keep newest 50 (rolling window, R215)
    rows.sort(key=lambda r: r.get("ts", ""))  # r245 law: write-back order = ts ASC
    lt2, lt3 = f2["last_tick"], f3["last_tick"]
    t2a, t3a = lt2.get("ts"), lt3.get("ts")
    if t2a is None or t3a is None:
        fails.append(f"autofill last_tick ts absent ({t2a!r} {t3a!r})")
        last_tick = lt3
    else:
        # rebase side: same-second tie -> HEAD (ours = :2 upstream, r140 law)
        last_tick = lt3 if t3a > t2a else (lt2 if t2a > t3a else lt2)
    out = {"launches": rows, "last_tick": last_tick}
    if not isinstance(last_tick, dict):
        fails.append("last_tick not a dict after resolve")
    fmt3b = blob(3, "results/autofill_state.json")
    crlf = b"\r\n" in fmt3b[:400]
    s = None
    for indent in (1, 2):
        rt = json.dumps(f3, ensure_ascii=False, indent=indent)
        if rt.encode("utf-8") == fmt3b.replace(b"\r\n", b"\n"):
            s = json.dumps(out, ensure_ascii=False, indent=indent)
            break
    if s is None:
        # fallback: direct format mirror via round-trip on :3 with newline strip
        rt1 = json.dumps(f3, ensure_ascii=False, indent=1)
        if rt1.encode("utf-8") == fmt3b.replace(b"\r\n", b"\n"):
            s = json.dumps(out, ensure_ascii=False, indent=1)
        else:
            fails.append("autofill self-calibration failed")
            s = json.dumps(out, ensure_ascii=False, indent=1)
    data = s.encode("utf-8")
    if crlf:
        data = data.replace(b"\n", b"\r\n")
    resolved["results/autofill_state.json"] = (
        "union", data,
        f"launches {len(la2)}|{len(la3)} -> union {n_uncapped} -> cap {len(rows)} "
        f"(ts ASC), last_tick ts {last_tick.get('ts')} "
        f"(sides {t2a}|{t3a}), CRLF={crlf}")

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
        report.append({"path": path, "mode": mode, "why": why, "bytes": len(data)})
    print(json.dumps({"resolver": "PASS", "resolved": report},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
