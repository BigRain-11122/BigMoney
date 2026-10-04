# r697 bm-b merge-window resolver: 18 UU S6 regen faces.
# Policy: per-face in-content ts-newer-wins (r657 direct git-show both sides,
# r461 ts_norm, r440 S6-regen origin-newer-wins on tie/missing);
# md twins locked to their json twin side; token_usage per-key union +
# r456/r466 freshness fallback. -*- coding: utf-8 -*-
import json
import re
import subprocess
import sys

TS_KEYS = ("generated", "generated_at", "written_at", "updated_at", "updated",
           "last_run", "asof", "ts", "written", "date")

FACES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

TWIN_LOCK = {
    "docs/daily_report/REPORT-2026-10-04.md": "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md": "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}


def show(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def ts_norm(v):
    if not isinstance(v, str):
        return ""
    s = v.strip().replace("T", " ")
    return s[:19]


def pick_ts(obj, depth=0):
    """Max normalized ts across candidate keys at top + one nesting level."""
    best = ""
    if isinstance(obj, dict):
        for k, v in obj.items():
            lk = str(k).lower()
            if any(t in lk for t in TS_KEYS) and isinstance(v, str) and len(v) >= 10:
                n = ts_norm(v)
                if n > best:
                    best = n
            elif depth < 1 and isinstance(v, (dict, list)):
                sub = pick_ts(v, depth + 1)
                if sub > best:
                    best = sub
    elif isinstance(obj, list) and depth < 1:
        for v in obj:
            sub = pick_ts(v, depth + 1)
            if sub > best:
                best = sub
    return best


def resolve_token(ours, theirs):
    """Per-key union on machines + r456/r466 fallback to freshness."""
    o = json.loads(ours)
    t = json.loads(theirs)
    side = {"ours": 0, "theirs": 0}
    for k, v in t.items():
        if k == "machines":
            m_o = o.get("machines", {})
            m_t = v
            merged = dict(m_o)
            for mk, mv in m_t.items():
                if mk not in m_o:
                    merged[mk] = mv
                    side["theirs"] += 1
                else:
                    no = ts_norm(str(m_o[mk].get("ts", "")))
                    nt = ts_norm(str(mv.get("ts", "")))
                    if nt > no:
                        merged[mk] = mv
                        side["theirs"] += 1
                    elif no > nt:
                        side["ours"] += 1
            o["machines"] = merged
        else:
            no = ts_norm(str(o.get(k, ""))) if isinstance(o.get(k), str) else ""
            nt = ts_norm(str(v)) if isinstance(v, str) else ""
            if isinstance(v, str) and isinstance(o.get(k), str) and no and nt:
                if nt > no:
                    o[k] = v
                    side["theirs"] += 1
                elif no > nt:
                    side["ours"] += 1
            elif k not in o:
                o[k] = v
                side["theirs"] += 1
    if side["ours"] == 0 and side["theirs"] == 0:
        # r456/r466: per-key zero side-pick -> explicit whole-face freshness
        no, nt = pick_ts(o), pick_ts(t)
        if nt >= no:
            o = t
            side["theirs"] += 1
        else:
            side["ours"] += 1
    return json.dumps(o, ensure_ascii=True, indent=1).encode("utf-8"), side


def main():
    receipt = {}
    for path in FACES:
        ours = show("HEAD", path)
        theirs = show("MERGE_HEAD", path)
        if ours is None or theirs is None:
            receipt[path] = "MISSING-SIDE ours=%s theirs=%s" % (
                ours is not None, theirs is not None)
            continue
        if ours == theirs:
            receipt[path] = "identical"
            data = theirs
        elif path == "results/token_usage.json":
            data, side = resolve_token(ours, theirs)
            receipt[path] = "token union side_pick=%s" % side
        elif path in TWIN_LOCK:
            # md/js twin: locked to json twin decision (filled in second pass)
            receipt[path] = "TWIN-PENDING"
            data = None
        else:
            # json/js regen faces: in-content ts newer-wins, tie->theirs
            try:
                jo = json.loads(ours)
                jt = json.loads(theirs)
            except Exception:
                data = theirs
                receipt[path] = "unparseable -> theirs"
            else:
                no, nt = pick_ts(jo), pick_ts(jt)
                if nt == "" and no == "":
                    data = theirs
                    receipt[path] = "no-ts-both -> theirs (r440 S6-regen)"
                elif nt >= no:
                    data = theirs
                    receipt[path] = "theirs-fresh %s>=%s" % (nt, no)
                else:
                    data = ours
                    receipt[path] = "ours-fresh %s>%s" % (no, nt)
        if data is not None:
            marker = data.count(b"<<<<<<<")
            assert marker == 0, "marker in resolved %s" % path
            if path.endswith((".json", ".js")):
                try:
                    json.loads(data)
                except Exception as e:
                    if path != "results/dashboard_status.js":
                        raise AssertionError("reparse fail %s: %r" % (path, e))
            with open(path, "wb") as f:
                f.write(data)

    # second pass: md twins locked to json twin side
    def json_side(jpath):
        ours = show("HEAD", jpath)
        theirs = show("MERGE_HEAD", jpath)
        if ours == theirs or ours is None:
            return "theirs"
        try:
            no = pick_ts(json.loads(ours))
            nt = pick_ts(json.loads(theirs))
        except Exception:
            return "theirs"
        return "ours" if no > nt else "theirs"

    for mdp, jp in TWIN_LOCK.items():
        if mdp in receipt and receipt[mdp] == "TWIN-PENDING":
            side = json_side(jp)
            data = show("HEAD" if side == "ours" else "MERGE_HEAD", mdp)
            assert data is not None
            assert data.count(b"<<<<<<<") == 0
            with open(mdp, "wb") as f:
                f.write(data)
            receipt[mdp] = "twin-locked to json side=%s" % side

    json.dump(receipt, open("results/_r697bmb_merge_resolve.json", "w",
                            encoding="utf-8"), ensure_ascii=True, indent=1)
    for k, v in receipt.items():
        print("%s -> %s" % (k, v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
