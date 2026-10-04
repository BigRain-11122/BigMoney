"""r464 bm-c push-race cycle-2 resolver: fetch, merge origin/main, resolve
the (smaller) conflict set with CURRENT-side ts comparison (no hardcoded
ours-newer): compute_audit union-by-ts, crash_fuse per-entry monotone,
token_usage generated-ts newer-wins, CODELY union, md twins follow json twin.
Idempotent merge step. Then commit + push_verify single-source."""
import datetime
import json
import os
import subprocess
import sys

C = 0x08000000


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, creationflags=C,
                       cwd=".")
    return p.returncode, (p.stdout or b"").decode("utf-8", "replace"), \
        (p.stderr or b"").decode("utf-8", "replace")


def show_bytes(ref, path):
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True,
                       creationflags=C, cwd=".")
    return r.returncode, r.stdout


def ts_norm(s):
    if not isinstance(s, str):
        return ""
    return s.replace("T", " ")[:19]


def json_side(path, ref):
    rc, b = show_bytes(ref, path)
    if rc != 0:
        return None
    try:
        return json.loads(b.decode("utf-8", "replace"))
    except Exception:  # noqa: BLE001
        return None


def pick_ts(d, keys):
    for k in keys:
        if k in d:
            return ts_norm(d[k])
    return ""


def main():
    # 1. fetch fresh
    rc, out, err = git("fetch", "origin")
    print("FETCH_RC", rc, (err or "")[:150])
    # 2. merge (idempotent)
    if os.path.exists(".git/MERGE_HEAD"):
        print("MERGE_ALREADY_IN_PROGRESS")
    else:
        rc, out, err = git("merge", "origin/main", "--no-edit")
        print("MERGE_RC", rc)
        print((out + err).strip()[:500])
    rc2, st, _ = git("status", "--porcelain")
    uu = [ln[3:].strip().strip('"') for ln in st.splitlines()
          if ln.startswith("UU")]
    print("UU_COUNT", len(uu))
    for u in uu:
        print("  UU", u)
    ev = {}
    for path in uu:
        if path == "CODELY.md":
            _, base = show_bytes("HEAD", "CODELY.md")
            _, theirs = show_bytes("MERGE_HEAD", "CODELY.md")
            rc3, mb, _ = git("merge-base", "HEAD", "MERGE_HEAD")
            _, basemb = show_bytes(mb.strip(), "CODELY.md")
            mine_lines = base.decode("utf-8", "replace").splitlines()
            base_set = set(basemb.decode("utf-8", "replace").splitlines())
            added = [ln for ln in mine_lines
                     if ln not in base_set and ln.strip()]
            out2 = theirs.decode("utf-8", "replace")
            appended = [ln for ln in added if ln not in out2]
            if appended:
                if not out2.endswith("\n"):
                    out2 += "\n"
                out2 += "\n".join(appended) + "\n"
            bad = [ln for ln in out2.splitlines()
                   if ln.startswith(("<<<<<<<", ">>>>>>>"))]
            assert not bad, "codely markers left"
            with open("CODELY.md", "w", encoding="utf-8", newline="") as f:
                f.write(out2)
            ev[path] = {"appended": len(appended)}
        elif path == "results/compute_audit.json":
            a = json_side(path, "HEAD")
            b = json_side(path, "MERGE_HEAD")
            merged = {}
            for row in a.get("history", []):
                merged[ts_norm(row.get("ts"))] = row
            o_only = 0
            for row in b.get("history", []):
                k = ts_norm(row.get("ts"))
                if k not in merged:
                    merged[k] = row
                    o_only += 1
            hist = sorted(merged.values(), key=lambda r: ts_norm(r.get("ts")))
            latest = a.get("latest", {})
            if pick_ts(b.get("latest", {}), ["ts"]) > pick_ts(latest, ["ts"]):
                latest = b.get("latest", {})
            outd = dict(a)
            outd["history"] = hist
            outd["latest"] = latest
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                json.dump(outd, f, ensure_ascii=False, indent=1)
            json.loads(open(path, encoding="utf-8").read())
            ev[path] = {"hist": len(hist), "recovered": o_only,
                        "latest": pick_ts(latest, ["ts"])}
        elif path == "results/crash_fuse.json":
            a = json_side(path, "HEAD")
            b = json_side(path, "MERGE_HEAD")

            def score(e):
                return (e.get("refusals", 0) or 0, e.get("count", 0) or 0,
                        ts_norm(e.get("last_crash_ts", "")))
            sigs = {}
            for k in sorted(set(a.get("sigs", {})) | set(b.get("sigs", {}))):
                ea, eb = a.get("sigs", {}).get(k), b.get("sigs", {}).get(k)
                if ea is None:
                    sigs[k] = eb
                elif eb is None:
                    sigs[k] = ea
                else:
                    sigs[k] = eb if score(eb) > score(ea) else ea
            outd = dict(a)
            outd["sigs"] = sigs
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                json.dump(outd, f, ensure_ascii=False, indent=1)
            json.loads(open(path, encoding="utf-8").read())
            ev[path] = {"entries": len(sigs)}
        elif path.endswith(".json"):
            # generic snapshot: internal-ts newer-wins (either side)
            a = json_side(path, "HEAD")
            b = json_side(path, "MERGE_HEAD")
            assert a is not None and b is not None, "parse fail " + path
            ta = pick_ts(a, ["generated", "generated_at", "updated",
                             "updated_at", "ts"])
            tb = pick_ts(b, ["generated", "generated_at", "updated",
                             "updated_at", "ts"])
            win = "HEAD" if ta >= tb else "MERGE_HEAD"
            _, wb = show_bytes(win, path)
            with open(path, "wb") as f:
                f.write(wb)
            json.loads(open(path, encoding="utf-8", errors="replace").read())
            ev[path] = {"HEAD_ts": ta, "MERGE_HEAD_ts": tb, "winner": win}
        elif path.endswith(".md"):
            # md twin: follow the json twin winner
            jpath = path[:-3] + ".json"
            a = json_side(jpath, "HEAD")
            b = json_side(jpath, "MERGE_HEAD")
            ta = pick_ts(a or {}, ["generated", "generated_at"])
            tb = pick_ts(b or {}, ["generated", "generated_at"])
            win = "HEAD" if ta >= tb else "MERGE_HEAD"
            _, wb = show_bytes(win, path)
            with open(path, "wb") as f:
                f.write(wb)
            ev[path] = {"winner": win, "twin_ts": (ta, tb)}
        else:
            raise SystemExit("UNKNOWN UU FACE, inspect manually: " + path)
    # stage all resolved + probes
    staging = list(uu) + [
        "results/_r464bmc_merge_cycle2.py",
        "results/_r464bmc_push_receipt2.txt",
    ]
    if os.path.exists("results/_r464bmc_push_receipt3.txt"):
        staging.append("results/_r464bmc_push_receipt3.txt")
    rc4, out4, err4 = git("add", "--", *staging)
    assert rc4 == 0, "add fail " + err4[:200]
    # marker scan (content judgment r644/r453)
    rc5, chk, _ = git("diff", "--cached", "--check")
    marker_hits = [ln for ln in chk.splitlines() if "conflict marker" in ln]
    assert not marker_hits, "marker residue"
    rc6, grep, _ = git("grep", "--cached", "-l", "-e", "^<<<<<<<")
    assert not grep.strip(), "staged marker hit"
    # commit (merge in progress -> concludes merge)
    if os.path.exists(".git/MERGE_HEAD"):
        msg = ("merge origin/main: r464 push-race cycle-2 (fresh ts-compare: "
               "audit union/fuse monotone/token newer-wins) after second "
               "non-ff race; fleet active window " +
               datetime.datetime.now().strftime("%H:%M"))
        rc7, out7, err7 = git("commit", "-m", msg)
        print("COMMIT_RC", rc7, (out7 + err7).strip()[:200])
        if rc7 != 0:
            sys.exit(1)
    # push_verify single-source
    pr = subprocess.run([sys.executable, "Tools/push_verify.py"],
                        capture_output=True, cwd=".", creationflags=C)
    ptxt = ((pr.stdout or b"").decode("utf-8", "replace") + " || " +
            (pr.stderr or b"").decode("utf-8", "replace"))
    with open("results/_r464bmc_push_receipt3.txt", "w", encoding="utf-8",
              newline="\n") as f:
        f.write(ptxt)
    print("PUSH_VERIFY_RC", pr.returncode)
    print(ptxt[-300:])
    print("EV_KEYS", json.dumps({k: v for k, v in ev.items()},
                                ensure_ascii=False)[:500].encode(
                                    "ascii", "replace").decode())
    sys.exit(pr.returncode if pr.returncode in (0, 1) else 2)


if __name__ == "__main__":
    main()
