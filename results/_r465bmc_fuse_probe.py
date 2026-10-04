"""r465 bm-c crash_fuse.json pre-alignment probe + per-key max-merge builder.
r437/r440 two-split decision input: wt vs origin per-key newer-wins analysis
(ts normalized per r461 law: T->space, first 19 chars). Zero-loss assertions:
union keys == wt|origin keys per section; reparse PASS. Merged output staged to
results/_r465bmc_crash_fuse_merged.json (live face NOT touched by this probe).
File-out per r446 probe law. ASCII-only console print."""
import datetime
import json
import os
import subprocess

C = 0x08000000
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "_r465bmc_fuse_probe.json")
MERGED = os.path.join(ROOT, "results", "_r465bmc_crash_fuse_merged.json")
PATH = os.path.join(ROOT, "results", "crash_fuse.json")


def show_bytes(ref):
    r = subprocess.run(["git", "show", ref + ":results/crash_fuse.json"],
                       capture_output=True, creationflags=C, cwd=ROOT)
    return r.returncode, r.stdout


def ts_norm(v):
    if not isinstance(v, str):
        return ""
    return v.replace("T", " ")[:19]


def sig_ts(e):
    return max(ts_norm(e.get("last_refusal_ts", "")),
               ts_norm(e.get("last_crash_ts", "")))


def merge_sig(a, b, rep, k):
    if a is None:
        return dict(b)
    if b is None:
        return dict(a)
    if a == b:
        return dict(a)
    ta, tb = sig_ts(a), sig_ts(b)
    winner = dict(b if tb >= ta else a)
    for f in ("count", "refusals"):
        av, bv = a.get(f, 0), b.get(f, 0)
        if f in a or f in b:
            winner[f] = max(av, bv)
    if tb < ta:
        rep.setdefault("sigs_wt_newer", []).append(
            {"key": k, "wt": ta, "origin": tb})
    elif tb > ta:
        rep.setdefault("sigs_origin_newer", []).append(
            {"key": k, "wt": ta, "origin": tb})
    else:
        rep.setdefault("sigs_ts_equal_content_diff", []).append(k)
    return winner


def merge_cleared(a, b, rep, k):
    if a is None:
        return dict(b)
    if b is None:
        return dict(a)
    if a == b:
        return dict(a)
    ta, tb = ts_norm(a.get("cleared_ts", "")), ts_norm(b.get("cleared_ts", ""))
    winner = dict(b if tb >= ta else a)
    if tb < ta:
        rep.setdefault("cleared_wt_newer", []).append(
            {"key": k, "wt": ta, "origin": tb})
    elif tb > ta:
        rep.setdefault("cleared_origin_newer", []).append(
            {"key": k, "wt": ta, "origin": tb})
    else:
        rep.setdefault("cleared_ts_equal_content_diff", []).append(k)
    return winner


def main():
    rep = {"ts": datetime.datetime.now().isoformat(timespec="seconds")}
    rep["wt_mtime"] = datetime.datetime.fromtimestamp(
        os.path.getmtime(PATH)).isoformat(timespec="seconds")
    rc, ob = show_bytes("origin/main")
    rep["origin_show_rc"] = rc
    assert rc == 0, "git show origin/main:results/crash_fuse.json failed"
    origin = json.loads(ob.decode("utf-8"))
    with open(PATH, "rb") as f:
        wt = json.loads(f.read().decode("utf-8"))
    rep["wt_top_keys"] = sorted(wt.keys())
    rep["origin_top_keys"] = sorted(origin.keys())
    ws, wc = wt.get("sigs", {}), wt.get("cleared", {})
    os_, oc = origin.get("sigs", {}), origin.get("cleared", {})
    rep["counts"] = {"wt_sigs": len(ws), "wt_cleared": len(wc),
                     "origin_sigs": len(os_), "origin_cleared": len(oc)}
    rep["sigs_wt_only"] = sorted(set(ws) - set(os_))
    rep["sigs_origin_only"] = sorted(set(os_) - set(ws))
    rep["cleared_wt_only"] = sorted(set(wc) - set(oc))
    rep["cleared_origin_only"] = sorted(set(oc) - set(wc))
    ms = {}
    for k in sorted(set(ws) | set(os_)):
        ms[k] = merge_sig(ws.get(k), os_.get(k), rep, k)
    mc = {}
    for k in sorted(set(wc) | set(oc)):
        mc[k] = merge_cleared(wc.get(k), oc.get(k), rep, k)
    merged = dict(origin)  # preserve any other origin top-level keys
    merged["sigs"] = ms
    merged["cleared"] = mc
    # zero-loss assertions
    assert set(ms) == set(ws) | set(os_), "sigs key loss"
    assert set(mc) == set(wc) | set(oc), "cleared key loss"
    json.loads(json.dumps(merged))  # reparse gate
    with open(MERGED, "w", encoding="utf-8", newline="\n") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
        f.write("\n")
    same = (not rep["sigs_wt_only"] and not rep["sigs_wt_newer"]
            and not rep["cleared_wt_only"] and not rep["cleared_wt_newer"]
            and not rep.get("sigs_ts_equal_content_diff")
            and not rep.get("cleared_ts_equal_content_diff"))
    rep["verdict"] = ("WT_SUBSET_OF_ORIGIN_checkout_path"
                      if same else "WT_HAS_UNIQUE_OR_NEWER_maxmerge_path")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    print("VERDICT", rep["verdict"],
          "| wt_sigs", len(ws), "origin_sigs", len(os_),
          "| wt_only", len(rep["sigs_wt_only"]) + len(rep["cleared_wt_only"]),
          "| wt_newer", len(rep.get("sigs_wt_newer", [])) + len(rep.get("cleared_wt_newer", [])),
          "| origin_only", len(rep["sigs_origin_only"]) + len(rep["cleared_origin_only"]),
          "| origin_newer", len(rep.get("sigs_origin_newer", [])) + len(rep.get("cleared_origin_newer", [])))


if __name__ == "__main__":
    main()
