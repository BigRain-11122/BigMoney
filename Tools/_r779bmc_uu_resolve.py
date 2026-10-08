"""r779 bm-c rebase UU resolver (pick 2/2 window, 41 UU add/add-modify faces).

Laws applied (pit-git-resolver-rebase.md canon):
- r648: rebase-window stage reads MUST go ls-files -u -> git cat-file -p <sha>
  (never git show :N:<path> -- empty-read rc0 trap); marker scan on BOTH stage
  blobs is a hard gate before any take-side.
- r782: rebase window stage semantics INVERTED: stage2 = onto side (origin),
  stage3 = replayed side (ours). ts-newer-wins converges the correct side
  regardless of labels (deep audit, r516).
- r794: resolve exactly the ls-files -u list (no add -u retry loops); deep-ts
  newer-wins, tie -> stage2 (r140).
- r516: no-ts fallback REQUIRES deep audit (here: datetime -> pure-date
  secondary keys; no keys at all -> tie rule, receipt-disclosed).
- r570: append-only jsonl -> line-level union (stage2 lines + stage3-unique).
- r705: winning blob bytes written EXACT (binary, no EOL translation), then
  targeted git add per path (receipt follows).
"""
import json
import os
import re
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
RECEIPT = REPO + r"\results\_r779bmc_uu_resolve.json"
DT = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def git(args):
    p = subprocess.run(["git"] + args, cwd=REPO, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    return p.returncode, p.stdout, p.stderr


def blob(sha):
    rc, out, err = git(["cat-file", "-p", sha])
    assert rc == 0, "cat-file failed for %s: %s" % (sha, err.decode("utf-8", "replace"))
    return out


def side_keys(data):
    txt = data.decode("utf-8", "replace")
    dts = DT.findall(txt)
    dates = [d for d in DATE.findall(txt)]
    return (max(dts) if dts else None, max(dates) if dates else None)


def main():
    rc, out, err = git(["ls-files", "-u"])
    assert rc == 0, "ls-files -u failed"
    entries = {}
    for line in out.decode("utf-8", "replace").splitlines():
        if not line.strip():
            continue
        meta, path = line.split("\t", 1)
        parts = meta.split()
        stage = int(parts[2])
        entries.setdefault(path, {})[stage] = parts[1]
    uu = {p: s for p, s in entries.items() if 2 in s and 3 in s}
    assert len(uu) == 43, "expected 43 UU faces, got %d" % len(uu)

    record = []
    for path in sorted(uu):
        st = uu[path]
        b2, b3 = blob(st[2]), blob(st[3])
        m2, m3 = b"<<<<<<<" in b2, b"<<<<<<<" in b3
        if m2 and m3:
            print("HARD_FAIL both stage blobs carry conflict markers: %s" % path)
            sys.exit(1)
        if m2:
            winner, why, data = 3, "stage2-marker-contaminated->take-clean-ours", b3
        elif m3:
            winner, why, data = 2, "stage3-marker-contaminated->take-clean-onto", b2
        elif path == "results/x2_watch_log.jsonl":
            l2 = b2.decode("utf-8", "replace").splitlines()
            l3 = b3.decode("utf-8", "replace").splitlines()
            set2 = set(l2)
            uniq3 = [ln for ln in l3 if ln not in set2 and ln.strip()]
            base = b2 if b2.endswith(b"\n") or not b2 else b2 + b"\n"
            data = base + "".join(ln + "\n" for ln in uniq3).encode("utf-8")
            winner, why = 0, "union(stage2=%d + stage3-unique=%d)" % (len(l2), len(uniq3))
        else:
            t2, d2 = side_keys(b2)
            t3, d3 = side_keys(b3)
            if t2 or t3:
                if t2 and t3:
                    winner = 3 if t3 > t2 else 2
                else:
                    winner = 3 if t3 else 2
                why = "dt %s vs %s" % (t2, t3)
            elif d2 or d3:
                if d2 and d3:
                    winner = 3 if d3 > d2 else 2
                else:
                    winner = 3 if d3 else 2
                why = "date %s vs %s" % (d2, d3)
            else:
                winner, why = 2, "no-ts-keys-tie->stage2 (r140/r794)"
            data = b3 if winner == 3 else b2
        with open(os.path.join(REPO, path.replace("/", "\\")), "wb") as fh:
            fh.write(data)
        rc_add, _, err_add = git(["add", "--", path])
        assert rc_add == 0, "targeted add failed for %s: %s" % (path, err_add.decode("utf-8", "replace"))
        rec = {"path": path, "winner": winner, "why": why,
               "bytes": len(data), "stage2_sha": st[2], "stage3_sha": st[3]}
        if path == "results/update_status.json":
            j = json.loads(data.decode("utf-8"))
            rec["update_status_check"] = {
                "total_new_rows": j.get("total_new_rows"),
                "data_cutoff": j.get("data_cutoff"),
                "hook_ok": j.get("hook_ok"),
                "laggards": len((j.get("catchup") or {}).get("laggards") or []),
                "updated": j.get("updated"),
            }
        record.append(rec)
        print("[%s winner=%s %s]" % (path, winner, why))

    with open(RECEIPT, "w", encoding="utf-8") as fh:
        json.dump({"round": 779, "uu_count": len(uu), "resolved": record}, fh,
                  indent=1, ensure_ascii=False)
    rc, out, err = git(["ls-files", "-u"])
    left = len([ln for ln in out.decode("utf-8", "replace").splitlines() if ln.strip()])
    print("RESOLVE_DONE uu=43 resolved=43 remaining_uu=%d receipt=%s" % (left, RECEIPT))
    assert left == 0, "UU faces remain unresolved"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
