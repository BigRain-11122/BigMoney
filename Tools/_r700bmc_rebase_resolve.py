"""r700 bm-c rebase-conflict resolver (1 UU face: results/compute_audit.json,
r570/r806 append-history union law; REBASE ours/theirs INVERSION per r688:
REBASE_HEAD blob = mine). Then atomic add+continue (r787 law). Remaining
replay steps handled by caller if further conflicts arise."""
import json
import re
import subprocess

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CA = "results/compute_audit.json"
MARKER_RE = re.compile(r"^(<<<<<<<|=======|>>>>>>>)", re.M)


def raw(rev, path):
    r = subprocess.run(["git", "-C", REPO, "show", f"{rev}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"blob read fail {rev}:{path}: {r.stderr[:200]}")
    return r.stdout


def main():
    # confirm single UU
    r = subprocess.run(["git", "-C", REPO, "status", "--porcelain"],
                       capture_output=True)
    uu = [ln[3:].strip() for ln in r.stdout.decode().splitlines()
          if ln.startswith("UU")]
    print("UU faces:", uu)
    assert uu == [CA], "unexpected conflict set: %s" % uu

    d_mine = json.loads(raw("REBASE_HEAD", CA))
    d_theirs = json.loads(raw("origin/main", CA))
    by_ts = {}
    for e in d_theirs.get("history", []):
        by_ts[e.get("ts")] = e
    for e in d_mine.get("history", []):
        by_ts[e.get("ts")] = e
    merged = sorted(by_ts.values(), key=lambda x: x.get("ts") or "")
    union_ca = {"latest": merged[-1], "history": merged}
    blob = (json.dumps(union_ca, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with open(REPO + "\\" + CA.replace("/", "\\"), "wb") as fh:
        fh.write(blob)
    # post-validate: marker-free + parses + round-trip
    txt = open(REPO + "\\" + CA.replace("/", "\\"), encoding="utf-8").read()
    assert not MARKER_RE.search(txt), "marker pollution"
    json.loads(txt)
    receipt = {
        "path": CA, "history_n": len(merged),
        "theirs_n": len(d_theirs.get("history", [])),
        "mine_n": len(d_mine.get("history", [])),
        "latest_ts": union_ca["latest"].get("ts"),
        "mine_latest_ts": d_mine.get("latest", {}).get("ts"),
        "theirs_latest_ts": d_theirs.get("latest", {}).get("ts"),
    }
    print("union receipt:", json.dumps(receipt))

    # atomic add + continue (r787 law)
    for args in (["add", "--", CA], ["rebase", "--continue"]):
        p = subprocess.run(["git", "-C", REPO] + args, capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        print("%s rc=%d" % (" ".join(args), p.returncode))
        print((p.stdout + p.stderr).strip()[-500:])
        if p.returncode != 0:
            raise SystemExit(2)

    r = subprocess.run(["git", "-C", REPO, "status", "--porcelain"],
                      capture_output=True)
    uu_left = [ln for ln in r.stdout.decode().splitlines()
               if ln.startswith("UU") or ln.startswith("AA")]
    print("UU/AA left:", uu_left or "none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
