"""r777 bm-a merge resolver: 18-UU window vs bm-c r622 close (shared S6 regen faces).

Laws applied: r515 (merge-mode sides from index stages), r710 (python subprocess
bytes, never PS redirection; len>100 + reparse gates), r711 (ts probe: explicit
top-level key priority, space->T normalize, fromisoformat numeric compare),
r709 (no blind corpus max), r708/r510 (twin faces same-side lock: .md/.js follow
their .json anchor), r522 (union = values() + isinstance dict type gate),
r704 (write-back read-verify == chosen side), r609/r506 (independent line-anchored
marker scan on resolved files), r611 (re-serialized faces: content-gate not
blob-sha), r773 (compute_audit history ts-union; regime_state base=newer +
history asof-union; token_usage content-equal-take-new).
"""
import json
import subprocess
import io
import os
import hashlib
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))

TWIN_FOLLOWERS = {
    "results/dashboard_status.json": ["results/dashboard_status.js"],
    "docs/daily_report/REPORT-2026-10-06.json": ["docs/daily_report/REPORT-2026-10-06.md"],
    "docs/live_usage/LIVE-2026-10-06.json": ["docs/live_usage/LIVE-2026-10-06.md"],
    "docs/live_usage/LIVE-latest.json": ["docs/live_usage/LIVE-latest.md"],
}
TS_KEYS = ["generated_at", "generated", "updated", "updated_at", "ts", "clock_read", "timestamp", "last_run"]
UNION_HISTORY_FACES = {"results/compute_audit.json", "results/regime_state.json"}
CONTENT_EQUAL_TAKE_NEW = {"results/token_usage.json"}


def git(args):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=ROOT)
    return r.stdout, r.returncode


def uu_paths():
    out, _ = git(["ls-files", "-u"])
    paths = sorted({line.split("\t")[1] for line in out.decode("utf-8", "replace").splitlines() if line.strip()})
    return paths


def stage_blob(path, stage):
    out, rc = git(["show", f":{stage}:{path}"])
    assert rc == 0 and len(out) > 100, f"stage {stage} empty/missing for {path} (r710-B gate)"
    return out


def parse_ts(v):
    if not isinstance(v, str) or not v.strip():
        return None
    s = v.strip().replace(" ", "T")
    for cut in (len(s),):
        try:
            return datetime.fromisoformat(s[:cut])
        except ValueError:
            pass
    # strip trailing timezone for bare forms
    try:
        return datetime.fromisoformat(s.split("+")[0].split("Z")[0])
    except ValueError:
        return None


def probe_ts(obj):
    """r711-2: explicit top-level key priority, first hit wins; normalized compare.
    Tier-2 nested anchors (r516 deep-audit): meta.generated_at, data.update.last_run."""
    for k in TS_KEYS:
        if isinstance(obj, dict) and k in obj:
            t = parse_ts(obj[k])
            if t is not None:
                return t, k
    if isinstance(obj, dict):
        for path in (("meta", "generated_at"), ("data", "update", "last_run")):
            cur = obj
            ok = True
            for seg in path:
                if isinstance(cur, dict) and seg in cur:
                    cur = cur[seg]
                else:
                    ok = False
                    break
            if ok:
                t = parse_ts(cur)
                if t is not None:
                    return t, ".".join(path)
    return None, None


def union_history(ours, theirs, key_hint):
    """r522: dedupe by serialized identity ts-key, union = values(), type gates."""
    oid = {}
    for row in ours:
        if not isinstance(row, dict):
            raise AssertionError("history row not dict (r522 type gate)")
        k = json.dumps(row, sort_keys=True, ensure_ascii=False)
        oid.setdefault(k, row)
    for row in theirs:
        if not isinstance(row, dict):
            raise AssertionError("history row not dict (r522 type gate)")
        k = json.dumps(row, sort_keys=True, ensure_ascii=False)
        oid.setdefault(k, row)
    return list(oid.values())


def resolve():
    paths = uu_paths()
    assert paths, "no UU paths found"
    receipt = {"window": "r777-bma merge vs bm-c r622", "faces": {}, "law_ref": "pit-git-resolver r515/r708/r709/r710/r711/r522/r704/r609"}
    decided = {}
    for p in paths:
        oB, tB = stage_blob(p, 2), stage_blob(p, 3)
        try:
            oJ = json.loads(oB.decode("utf-8"))
            tJ = json.loads(tB.decode("utf-8"))
            jsonable = True
        except Exception:
            jsonable = False
        if jsonable:
            to, ko = probe_ts(oJ)
            tt, kt = probe_ts(tJ)
            if p in CONTENT_EQUAL_TAKE_NEW and oJ == tJ:
                decided[p] = ("theirs", "content-equal-take-new", oB, tB)
                receipt["faces"][p] = {"decision": "theirs", "basis": "content-equal-take-new (r773)", "ts_ours": str(to), "ts_theirs": str(tt)}
                continue
            if p in UNION_HISTORY_FACES:
                # union history face: base scalars from newer side (deep-audit r516: probe 'latest' sub-face when top-level misses); history lists unioned
                bo, bko = (probe_ts(oJ) if to else (probe_ts(oJ.get("latest")) if isinstance(oJ.get("latest"), dict) else (None, None)))
                bt, bkt = (probe_ts(tJ) if tt else (probe_ts(tJ.get("latest")) if isinstance(tJ.get("latest"), dict) else (None, None)))
                assert bo or bt, f"{p}: union face base has no probeable ts even in 'latest' (r516 deep-audit)"
                base = "ours" if (bo and (not bt or bo >= bt)) else "theirs"
                merged = dict(oJ) if base == "ours" else dict(tJ)
                union_done = False
                for hk in ("history", "history_rows"):
                    oh = oJ.get(hk) if isinstance(oJ.get(hk), list) else []
                    th = tJ.get(hk) if isinstance(tJ.get(hk), list) else []
                    if oh or th:
                        merged[hk] = union_history(oh, th, hk)
                        union_done = True
                payload = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8")
                decided[p] = ("union", f"base={base}" + ("+history-union" if union_done else ""), payload, payload)
                receipt["faces"][p] = {"decision": "union", "basis": f"base={base} (latest.ts {bko}={bo} vs {bkt}={bt})", "history_union": union_done}
                continue
            if to and tt:
                side = "ours" if to >= tt else "theirs"
                basis = f"ts {ko}={to} vs {kt}={tt}"
            elif to and not tt:
                side, basis = "ours", f"theirs no-ts (probe miss), ours {ko}={to}"
            elif tt and not to:
                side, basis = "theirs", f"ours no-ts (probe miss), theirs {kt}={tt}"
            else:
                if oJ == tJ:
                    side, basis = "theirs", "no-ts content-equal-take-new"
                else:
                    raise AssertionError(f"{p}: no probeable ts on either side and content differs — manual adjudication required (r516 deep-audit law)")
            decided[p] = (side, basis, oB, tB)
            receipt["faces"][p] = {"decision": side, "basis": basis}
        else:
            decided[p] = ("ours-unparsed-follow", "non-json face pending twin-lock", oB, tB)
            receipt["faces"][p] = {"decision": "PENDING-TWIN", "basis": "non-json"}

    # r708 twin-lock: followers adopt anchor decision
    for anchor, followers in TWIN_FOLLOWERS.items():
        if anchor in decided:
            side, basis, oB, tB = decided[anchor]
            for f in followers:
                if f in decided and decided[f][0] == "PENDING-TWIN" or (f in decided and decided[f][0] == "ours-unparsed-follow"):
                    foB, ftB = stage_blob(f, 2), stage_blob(f, 3)
                    decided[f] = (side, f"twin-follow {anchor} ({basis})", foB, ftB)
                    receipt["faces"][f] = {"decision": side, "basis": f"twin-follow anchor {anchor}: {basis}"}
    for p, (side, basis, oB, tB) in decided.items():
        if side == "PENDING-TWIN" or side == "ours-unparsed-follow":
            raise AssertionError(f"{p}: twin-lock incomplete (r510 two-member dispatch law)")

    # write phase
    MARKERS = [b"\n<<<<<<< ", b"\n>>>>>>> ", b"\n=======\n"]
    for p, (side, basis, oB, tB) in decided.items():
        payload = oB if side == "ours" else tB
        full = os.path.join(ROOT, p)
        with open(full, "wb") as f:
            f.write(payload)
        # r704 write-back read-verify
        back = open(full, "rb").read()
        if side in ("ours", "theirs"):
            assert back == payload, f"{p}: write-back mismatch vs chosen stage blob"
        else:  # union: content gate (r611)
            assert json.loads(back.decode("utf-8")) is not None
        probe = b"\n" + back
        for m in MARKERS:
            assert m not in probe, f"{p}: residual conflict marker (r609/r506)"
        receipt["faces"][p]["sha16"] = hashlib.sha256(back).hexdigest()[:16]
        receipt["faces"][p]["bytes"] = len(back)

    with io.open(os.path.join(ROOT, "results", "_r777bma_merge_resolve.json"), "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print(json.dumps({p: receipt["faces"][p]["decision"] + " | " + str(receipt["faces"][p]["basis"])[:60] for p in receipt["faces"]}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys_exit = resolve()
    raise SystemExit(sys_exit)
