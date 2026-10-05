# -*- coding: utf-8 -*-
"""r552 bm-c merge resolver (r551 bloodline verbatim: same-day S6-regen
dual-writer race pattern; face list adapted to this window's 2 UU set,
tag + receipt path only changed per r531-family lineage law).

Window: 14 UU faces, S6-regen dual-writer race (our r552 S6 15:2x vs
bm-a r731/r733 close-wave S6 pushed mid-window; second-hop merge face).

Laws applied:
  r706-A/r515: merge-mode complete side source = index stages :2:/:3: via
    python subprocess bytes (work-tree rebuild forbidden, r515 zealous law).
  r711/r709: ts probes NORMALIZED (T->space, strip +08:00) before compare;
    top-level ts keys directed first, corpus max only as fallback.
  r515: compute_audit history union (key ts+machine).
  r704: readback == written blob asserts (CR-normalized).
  r505 v2: residual marker screen, line-anchored.
Receipt -> results/_r552bmc_merge_resolve.json
Exit 0 ok / 1 gate failure / 2 mechanism fault."""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000
TS_RE = re.compile(r"20\d\d-\d\d-\d\d[ T]\d\d:\d\d:\d\d")
MARKERS = ("<<<<<<< ", ">>>>>>> ", "||||||| ", "=======")
TS_KEYS = ("ts", "updated_at", "updated", "generated_at", "generated",
           "last_run", "checked_at", "asof", "last_seen", "cutoff",
           "evidence_cutoff")


def git_show_bytes(spec):
    r = subprocess.run(["git", "show", spec], cwd=ROOT, capture_output=True,
                       creationflags=CREATE)
    if r.returncode != 0 or not r.stdout:
        raise RuntimeError("git show %s rc=%d bytes=%d" %
                           (spec, r.returncode, len(r.stdout or b"")))
    return r.stdout


def stage(rel, n):
    return git_show_bytes(":%d:%s" % (n, rel))


def crn(b):
    return b.replace(b"\r\n", b"\n")


def norm_ts(s):
    """r711 fix: uniform comparable form -- T->space, strip tz suffix."""
    return s.replace("T", " ").split("+")[0].rstrip()


def ts_hits(text):
    return [norm_ts(x) for x in TS_RE.findall(text)]


def max_ts_text(t):
    hits = ts_hits(t)
    return max(hits) if hits else ""


def side_ts(obj_text):
    """Directed top-level probe first (r711 3), corpus max fallback."""
    try:
        obj = json.loads(obj_text)
    except ValueError:
        return max_ts_text(obj_text)
    if isinstance(obj, dict):
        cands = [norm_ts(str(obj[k])) for k in TS_KEYS
                 if k in obj and isinstance(obj[k], str)
                 and TS_RE.search(str(obj[k]))]
        if cands:
            return max(cands)
    return max_ts_text(obj_text)


receipt = {"round": "r552", "faces": {}, "gates": {}}


def residual_check(rel):
    b = open(os.path.join(ROOT, rel), "rb").read()
    for ln in b.split(b"\n"):
        s = ln.rstrip(b"\r")
        if s.startswith(tuple(m.encode() for m in MARKERS[:3])) or \
           s in (b"=======", b"||||||||| "):
            raise RuntimeError("residual marker in %s: %r" % (rel, s[:40]))


def write_stage(rel, n, why):
    blob = stage(rel, n)
    if rel.endswith(".json"):
        json.loads(blob.decode("utf-8"))  # chosen side must parse
    p = os.path.join(ROOT, rel)
    with open(p, "wb") as f:
        f.write(blob)
    back = open(p, "rb").read()
    assert crn(back) == crn(blob), "read-back mismatch %s" % rel
    receipt["faces"][rel] = {"action": "write-stage-%d" % n, "why": why}
    residual_check(rel)


def take_side_by_stages(rel):
    o_txt = stage(rel, 2).decode("utf-8", "replace")
    t_txt = stage(rel, 3).decode("utf-8", "replace")
    o_ts, t_ts = side_ts(o_txt), side_ts(t_txt)
    side = 2 if o_ts >= t_ts else 3
    receipt["faces"][rel] = {"action": "resolve-stage",
                             "ours_ts": o_ts, "theirs_ts": t_ts,
                             "take": "ours" if side == 2 else "theirs"}
    write_stage(rel, side, "ts-newer-wins stage-%d (ours=%s theirs=%s)" %
                (side, o_ts, t_ts))
    return side


def main():
    try:
        chosen = {}
        # 1. take-side faces by directed normalized ts probe
        for rel in ("results/regime_state.json",
                    "results/update_status.json",
                    "results/fundamental_b_layer_filter.json",
                    "results/futures_update_status.json",
                    "results/lhb_update_status.json",
                    "results/_attrition_guard_scan.json",
                    "docs/daily_report/REPORT-2026-10-05.json",
                    "docs/live_usage/LIVE-2026-10-05.json",
                    "docs/live_usage/LIVE-latest.json"):
            chosen[rel] = take_side_by_stages(rel)
        # 2. twins locked to their json verdict (r708 same-side law)
        twin_map = {
            "docs/daily_report/REPORT-2026-10-05.md":
                "docs/daily_report/REPORT-2026-10-05.json",
            "docs/live_usage/LIVE-2026-10-05.md":
                "docs/live_usage/LIVE-2026-10-05.json",
            "docs/live_usage/LIVE-latest.md":
                "docs/live_usage/LIVE-latest.json",
        }
        for rel, jrel in twin_map.items():
            n = chosen[jrel]
            write_stage(rel, n, "twin-locked-to-json %s side=%d" % (jrel, n))
        # 3. compute_audit history union from stage sides (r515 law)
        rel = "results/compute_audit.json"
        o = json.loads(stage(rel, 2).decode("utf-8"))
        t = json.loads(stage(rel, 3).decode("utf-8"))
        ho, ht = o.get("history", []), t.get("history", [])
        seen = {}
        for r in ho + ht:
            k = (str(r.get("ts", "")), str(r.get("machine", "")))
            if k not in seen or str(r) > str(seen[k]):
                seen[k] = r
        base = o if side_ts(json.dumps(o)) >= side_ts(json.dumps(t)) else t
        base["history"] = sorted(seen.values(),
                                 key=lambda r: str(r.get("ts", "")))
        blob = (json.dumps(base, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
        with open(os.path.join(ROOT, rel), "wb") as f:
            f.write(blob)
        assert crn(open(os.path.join(ROOT, rel), "rb").read()) == crn(blob)
        receipt["faces"][rel] = {"action": "history-union stage-sides",
                                 "ours_rows": len(ho), "theirs_rows": len(ht),
                                 "merged_rows": len(base["history"])}
        residual_check(rel)
        # 4. token per-key recursive union from stage sides (r515 law,
        #    r522 values-direction verified: union takes VALUES not keys)
        rel = "results/token_usage.json"
        o = json.loads(stage(rel, 2).decode("utf-8"))
        t = json.loads(stage(rel, 3).decode("utf-8"))

        def merge(a, b):
            if isinstance(a, dict) and isinstance(b, dict):
                out = dict(a)
                for k, v in b.items():
                    out[k] = merge(out[k], v) if k in out else v
                return out
            if isinstance(a, list) and isinstance(b, list):
                return a + [x for x in b if x not in a]
            return b if max_ts_text(str(b)) > max_ts_text(str(a)) else a

        m = merge(o, t)
        blob = (json.dumps(m, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
        with open(os.path.join(ROOT, rel), "wb") as f:
            f.write(blob)
        assert crn(open(os.path.join(ROOT, rel), "rb").read()) == crn(blob)
        receipt["faces"][rel] = {"action": "per-key-union stage-sides"}
        residual_check(rel)
        # 5. residual screen across all 14 faces + count assertion
        allf = sorted(set(list(receipt["faces"].keys())))
        assert len(allf) == 14, "face count %d != 14" % len(allf)
        for rel in allf:
            residual_check(rel)
        receipt["gates"]["residual_screen"] = "PASS 14/14"
        receipt["gates"]["readback"] = "PASS (every face write back-asserted)"
        sides = {k: v.get("take", v.get("action")) for k, v in receipt["faces"].items()}
        receipt["gates"]["side_summary"] = sides
    except Exception as e:
        receipt["error"] = repr(e)
        with open(os.path.join(ROOT, "results", "_r552bmc_merge_resolve.json"),
                  "wb") as f:
            f.write(json.dumps(receipt, ensure_ascii=False, indent=1).encode("utf-8"))
        print("FAIL:", e)
        return 1
    with open(os.path.join(ROOT, "results", "_r552bmc_merge_resolve.json"),
              "wb") as f:
        f.write(json.dumps(receipt, ensure_ascii=False, indent=1).encode("utf-8"))
    print("RESOLVED 14/14")
    for k, v in sorted(receipt["faces"].items()):
        print(" ", k, "->", v.get("action"), "ours=", v.get("ours_ts", ""),
              "theirs=", v.get("theirs_ts", ""), v.get("why", ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
