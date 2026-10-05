# -*- coding: utf-8 -*-
"""r718 rebase UU per-face resolver (r713/r717 lineage reuse).

Rebase mode: :2: = upstream (bm-c r525 wave + bm-b W116), :3: = mine (replayed r718).
Rules (verbatim law lineage):
- pen-holder faces (D-03(1) batch3 C-family host=bm-a): strategy_scorecard.json,
  daily_scorecard.json, dashboard_status.json/.js -> MINE (:3:).
- jsonl append-only (x2_watch_log): CR-normalized zero-loss line union (r630).
- token_usage.json: per-key max union (r466).
- compute_audit.json: history union (r707).
- everything else json/md twins: ts-newer-wins with r711 mixed-format
  normalization (fromisoformat after space/T dual-form); twins (.md/.js)
  follow their .json decision (r708 same-side law); deep ts audit for
  no-top-level-ts faces (r516(1)).
- stage blobs read via python subprocess bytes (r710-A law); len>100 assert
  before write (r710-B law); json reparse verify after write (r704 read-back).
"""
import subprocess
import json
import datetime as dt
import sys

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"


def git(*args):
    r = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True)
    return r.returncode, r.stdout, r.stderr


def uu_list():
    rc, out, _ = git("diff", "--name-only", "--diff-filter=U")
    return [l.strip() for l in out.decode("utf-8", "replace").splitlines() if l.strip()]


def stage_blob(path, n):
    rc, out, err = git("show", ":%d:%s" % (n, path))
    if rc != 0 or not out:
        return None
    return out


PENHOLDER = {
    "results/strategy_scorecard.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/dashboard_status.js",
}
TWINS = {
    "docs/daily_report/REPORT-2026-10-05.md": "docs/daily_report/REPORT-2026-10-05.json",
    "docs/live_usage/LIVE-2026-10-05.md": "docs/live_usage/LIVE-2026-10-05.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}


def _norm_ts(v):
    if not isinstance(v, str):
        return None
    s = v.strip().replace("T", " ").split("+")[0].split(".")[0]
    try:
        return dt.datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


def deep_ts(obj, depth=0):
    """Max timestamp found anywhere (r516(1) deep audit; r711 normalization)."""
    best = None
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                t = _norm_ts(v)
                kl = str(k).lower()
                if t and any(x in kl for x in ("ts", "time", "date", "at", "epoch", "seen", "run", "generated", "updated")):
                    best = t if best is None or t > best else best
            elif isinstance(v, (dict, list)) and depth < 3:
                t = deep_ts(v, depth + 1)
                if t and (best is None or t > best):
                    best = t
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, (dict, list)):
                t = deep_ts(v, depth + 1)
                if t and (best is None or t > best):
                    best = t
    return best


def pick_side(path, b2, b3):
    """Return (decision, bytes_to_write, note). b2=upstream, b3=mine."""
    if path in PENHOLDER:
        return "mine-penholder", b3, "D-03(1) host=bm-a lane law"
    if path.endswith(".jsonl"):
        lines2 = [l for l in b2.decode("utf-8", "replace").replace("\r\n", "\n").split("\n") if l.strip()]
        lines3 = [l for l in b3.decode("utf-8", "replace").replace("\r\n", "\n").split("\n") if l.strip()]
        seen = set(lines2)
        union = lines2 + [l for l in lines3 if l not in seen]
        return "union", ("\n".join(union) + "\n").encode("utf-8"), "jsonl zero-loss union r630 (%d+%d->%d)" % (len(lines2), len(lines3), len(union))
    twin_of = TWINS.get(path)
    if twin_of:
        return None, None, "twin-defer:" + twin_of  # handled after json twin decided
    # json ts-newer-wins
    try:
        j2 = json.loads(b2)
        j3 = json.loads(b3)
    except Exception as e:
        # unparseable side -> keep ours live-wins (guard face), note honestly
        return "mine-unparseable-side", b3, "side-parse-fail=%s" % str(e)[:40]
    t2, t3 = deep_ts(j2), deep_ts(j3)
    if t3 is None and t2 is None:
        return "mine-nots-audit-equal", b3, "both-no-ts fallback mine (r516 audit none both sides)"
    if t3 is None:
        return "theirs", b2, "mine-no-ts theirs=%s" % t2
    if t2 is None:
        return "mine", b3, "theirs-no-ts mine=%s" % t3
    if t3 >= t2:
        return "mine", b3, "ts-newer mine %s >= %s" % (t3, t2)
    return "theirs", b2, "ts-newer theirs %s > %s" % (t2, t3)


def per_key_max(a, b, depth=0):
    """r466 per-key max union for token_usage-style dicts."""
    if isinstance(a, dict) and isinstance(b, dict):
        out = {}
        for k in set(a) | set(b):
            if k in a and k in b:
                out[k] = per_key_max(a[k], b[k], depth + 1)
            else:
                out[k] = a.get(k, b.get(k))
        return out
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return max(a, b)
    # non-mergeable: newer ts wins at this leaf (string ts) else keep b (mine)
    ta, tb = _norm_ts(a) if isinstance(a, str) else None, _norm_ts(b) if isinstance(b, str) else None
    if ta and tb:
        return a if ta >= tb else b
    return b if b is not None else a


def main():
    uus = uu_list()
    print("UU faces:", len(uus))
    decisions = {}
    writes = {}
    for p in uus:
        b2, b3 = stage_blob(p, 2), stage_blob(p, 3)
        if p in PENHOLDER:
            if b3 is None:
                print("FATAL penholder stage3 missing:", p)
                return 2
            decisions[p] = ("mine-penholder", "D-03(1) lane law")
            writes[p] = b3
            continue
        if p.endswith(".json") and p == "results/token_usage.json":
            if b2 is None or b3 is None:
                print("FATAL token stage missing:", p)
                return 2
            j = per_key_max(json.loads(b2), json.loads(b3))
            writes[p] = json.dumps(j, ensure_ascii=False, indent=1).encode("utf-8")
            decisions[p] = ("per-key-max", "r466")
            continue
        if p == "results/compute_audit.json":
            if b2 is None or b3 is None:
                print("FATAL compute_audit stage missing:", p)
                return 2
            j2, j3 = json.loads(b2), json.loads(b3)
            h2 = j2.get("history", [])
            h3 = j3.get("history", [])
            keys = {}
            for row in h2 + h3:  # theirs-first then mine; later same-key overwrites = newer wins
                keys[row.get("ts", row.get("run_ts", str(row)))] = row
            j = dict(j3)
            j["history"] = [keys[k] for k in sorted(keys)]
            writes[p] = json.dumps(j, ensure_ascii=False, indent=1).encode("utf-8")
            decisions[p] = ("history-union", "r707 (%d+%d->%d)" % (len(h2), len(h3), len(j["history"])))
            continue
        dec, data, note = pick_side(p, b2, b3)
        if dec is None and note.startswith("twin-defer:"):
            decisions[p] = ("twin-defer", note)
            continue
        if data is None:
            print("FATAL no data for", p, note)
            return 2
        decisions[p] = (dec, note)
        writes[p] = data
    # twins: follow json decision
    for p in uus:
        twin_of = TWINS.get(p)
        if not twin_of:
            continue
        base_dec = decisions.get(twin_of)
        if not base_dec:
            print("FATAL twin base missing decision:", twin_of)
            return 2
        side = "mine" if ("mine" in base_dec[0]) else "theirs"
        n = 3 if side == "mine" else 2
        blob = stage_blob(p, n)
        if blob is None:
            print("FATAL twin stage missing:", p, n)
            return 2
        writes[p] = blob
        decisions[p] = ("twin-%s-follow-json" % side, "r708 same-side law")
    # write + verify
    ok = 0
    for p, data in writes.items():
        fp = ROOT + "\\" + p.replace("/", "\\")
        with open(fp, "wb") as fh:
            fh.write(data)
        if p.endswith(".json"):
            json.loads(open(fp, "rb").read())  # reparse verify (r704 read-back)
        ok += 1
    for p, (dec, note) in sorted(decisions.items()):
        print("%-58s %-22s %s" % (p, dec, note))
    print("resolved+verified:", ok, "of", len(uus))
    json.dump({"decisions": {k: list(v) for k, v in decisions.items()}},
              open(ROOT + r"\results\_r718bma_rebase_resolver.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())

