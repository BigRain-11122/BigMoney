# -*- coding: utf-8 -*-
"""r751 bm-c closeout push ladder: commit round products -> push; on race:
fetch -> churn-absorb own daemon faces (net-tree law r642) -> merge ORT
(r743/r745/r746 proven route) -> per-face stage-identity-verified ts-duel
(r738 deep-ts; identity by blob-sha vs HEAD/origin, merge-semantics-proof)
with union faces (compute_audit history by-ts union r678; token_usage per-key
max-union r658) -> conclude merge -> push again; last resort fallback branch
machine/bm-c-r751 (D-20260925-01(3)). Post-push fetch + rev-list not-at-origin
self-verify (O-20261001-1108 delivery gate). Receipt ->
results/_r751bmc_push_receipt.json."""
import datetime
import json
import os
import re
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MSG = os.path.join(ROOT, "Tools", "_r751bmc_commitmsg.txt")
RECEIPT = os.path.join(ROOT, "results", "_r751bmc_push_receipt.json")
MARKERS = ("_roundzero", "orphan", "autofill", "dispatcher", "idle_trigger",
           "saturation", "_r751bmc_", "commitmsg", "s0msg", "mergemsg",
           "precommitmsg", "watermark_probe")
TS_RE = re.compile(r'"(generated|generated_at|ts|asof|asof_ts)"\s*:\s*"([0-9T:+\-\.Z ]{8,32})"')
UNION_FACES = {"results/compute_audit.json", "results/token_usage.json"}


def git(args, check=False):
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True)
    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    if check and p.returncode != 0:
        print("GITFAIL rc=%d args=%s out=%s" % (p.returncode, args[:3], out[:400]))
        sys.exit(1)
    return p.returncode, out


def classify():
    rc, st = git(["status", "--porcelain"])
    lines = [l for l in st.splitlines() if l.strip()]
    own = [l for l in lines if any(m in l for m in MARKERS)]
    other = [l for l in lines if not any(m in l for m in MARKERS)]
    return lines, own, other


def blob(sha):
    return subprocess.run(["git", "-C", ROOT, "cat-file", "blob", sha],
                          capture_output=True).stdout


def rev_of(rev, path):
    rc, out = git(["rev-parse", rev + ":" + path])
    return out.strip() if rc == 0 else None


def getts(raw):
    try:
        m = TS_RE.search(raw.decode("utf-8", "replace"))
        return m.group(2) if m else None
    except Exception:
        return None


def norm(x):
    import datetime as dt
    try:
        return dt.datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    except Exception:
        return None


def union_json(o2, o3):
    if isinstance(o2, dict) and isinstance(o3, dict):
        out = dict(o2)
        for k, v in o3.items():
            out[k] = union_json(out[k], v) if k in out else v
        return out
    if isinstance(o2, (int, float)) and isinstance(o3, (int, float)):
        return max(o2, o3)
    if isinstance(o2, list) and isinstance(o3, list):
        if all(isinstance(x, dict) for x in o2 + o3):
            seen = {}
            for x in o2 + o3:
                k = x.get("ts")
                seen[k if k is not None else id(x)] = x   # later write wins same ts
            return list(seen.values())
        return o3 if len(o3) >= len(o2) else o2
    return o3


def resolve_merge_conflicts():
    rc, out = git(["ls-files", "-u"])
    faces = []
    for ln in out.splitlines():
        parts = ln.split("\t")
        if len(parts) == 2 and parts[1].strip() not in faces:
            faces.append(parts[1].strip())
    print("UU faces: %d" % len(faces))
    res = {}
    for f in faces:
        rel = f.replace("\\", "/")
        rc, info = git(["ls-files", "-u", "--", f])
        st = {}
        for l in info.splitlines():
            cols = l.split("\t")[0].split()
            if len(cols) >= 3:
                st[int(cols[2])] = cols[1]
        mine_sha = rev_of("HEAD", rel)
        org_sha = rev_of("origin/main", rel)
        # stage identity by blob-sha (merge-semantics-proof)
        my_stage = next((s for s, sha in st.items() if sha == mine_sha), None)
        org_stage = next((s for s, sha in st.items() if sha == org_sha), None)
        if my_stage is None and org_stage is None:
            # neither matches (content-merged base drift): fall back merge convention s2=ours s3=theirs
            my_stage, org_stage = (2, 3) if mine_sha is not None else (None, None)
        my_raw = blob(st[my_stage]) if my_stage in st else b""
        org_raw = blob(st[org_stage]) if org_stage in st else b""
        t_m, t_o = getts(my_raw), getts(org_raw)
        n_m, n_o = norm(t_m), norm(t_o)
        if rel in UNION_FACES:
            try:
                merged = union_json(json.loads(my_raw or b"{}"), json.loads(org_raw or b"{}"))
                if n_o and (not n_m or n_o > n_m) and isinstance(merged, dict):
                    for k in ("ts", "generated", "generated_at"):
                        if k in json.loads(org_raw):
                            merged[k] = json.loads(org_raw)[k]
                with open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n") as fh:
                    json.dump(merged, fh, indent=1, ensure_ascii=False)
                git(["add", "--", f])
                res[rel] = ("union", t_m, t_o)
                print("%-46s UNION zero-loss (mine=%s origin=%s)" % (rel, t_m, t_o))
                continue
            except Exception as e:
                print("%-46s union FAILED (%s) -> ts-duel" % (rel, e))
        if my_stage is not None and org_stage is None:
            side_raw = my_raw                       # origin deleted, mine lives -> keep mine
            side = "MINE(origin-absent)"
        elif org_stage is not None and my_stage is None:
            side_raw = org_raw                       # mine deleted, origin lives -> keep origin
            side = "ORIGIN(mine-absent)"
        elif n_m and (not n_o or n_m > n_o):
            side_raw = my_raw                        # newer-wins (r738 deep-ts)
            side = "MINE"
        else:
            side_raw = org_raw                       # tie -> origin (r440)
            side = "ORIGIN"
        with open(os.path.join(ROOT, rel), "wb") as fh:
            fh.write(side_raw)
        git(["add", "--", f])
        res[rel] = (side, t_m, t_o)
        print("%-46s ts-duel mine=%s origin=%s -> %s" % (rel, t_m, t_o, side))
    return res


def main():
    facts = {"round": 751, "steps": []}
    # 1) commit round products
    lines, own, other = classify()
    if other:
        print("OTHER-SESSION FACES PRESENT, targeted add only:")
        for l in other:
            print("  O " + l)
        for l in own:
            git(["add", "--", l.split(" ", 1)[1].strip()])
    else:
        git(["add", "-A"])
    rc, out = git(["commit", "-F", MSG])
    if rc != 0:
        if "nothing to commit" in out:
            print("COMMIT skipped (clean)")
            facts["steps"].append("commit-skip")
        else:
            print("COMMIT_FAIL rc=%d out=%s" % (rc, out[:400]))
            return 4
    else:
        sha = git(["rev-parse", "--short=9", "HEAD"])[1].strip()
        print("COMMIT %s" % sha)
        facts["steps"].append("commit-" + sha)
    # 2) push attempt 1
    rc, out = git(["push", "origin", "main"])
    facts["push1_rc"] = rc
    if rc == 0:
        print("PUSH1 DELIVERED")
    else:
        print("PUSH1 rc=%d tail=%s" % (rc, out.strip().splitlines()[-1][:220] if out.strip() else ""))
        # 3) race path: fetch + churn-absorb + merge ORT
        git(["fetch", "origin"], check=True)
        lines, own, other = classify()
        if other:
            print("RACE-ABORT: other-session faces appeared -> local commit kept, fallback branch")
            facts["race_abort_other"] = [l.strip() for l in other]
        else:
            if own:
                git(["add", "-A"])
                rc2, out2 = git(["commit", "-m", "round 751: churn-absorb daemon faces (r642 net-tree law)"])
                if rc2 == 0:
                    sha = git(["rev-parse", "--short=9", "HEAD"])[1].strip()
                    print("CHURN-ABSORB %s (%d faces)" % (sha, len(own)))
                    facts["steps"].append("churn-absorb-" + sha)
            rc3, out3 = git(["merge", "origin", "main", "-m", "round 751: merge origin wave (r743 ORT route)"])
            facts["merge_rc"] = rc3
            if rc3 != 0:
                res = resolve_merge_conflicts()
                facts["resolved"] = {k: v[0] for k, v in res.items()}
                rc4, out4 = git(["commit", "--no-edit"])
                if rc4 != 0 and "nothing to commit" not in out4:
                    print("MERGE_CONCLUDE_FAIL rc=%d out=%s" % (rc4, out4[:300]))
                    return 5
                sha = git(["rev-parse", "--short=9", "HEAD"])[1].strip()
                print("MERGE concluded %s (resolved %d faces)" % (sha, len(facts.get("resolved", {}))))
            else:
                print("MERGE clean ORT auto-concluded")
            rc, out = git(["push", "origin", "main"])
            facts["push2_rc"] = rc
            print("PUSH2 rc=%d %s" % (rc, out.strip().splitlines()[-1][:220] if out.strip() else ""))
    # 4) fallback branch
    if facts.get("push1_rc") != 0 and facts.get("push2_rc", 1) != 0:
        rc, out = git(["push", "origin", "HEAD:refs/heads/machine/bm-c-r751"])
        facts["fallback_rc"] = rc
        print("FALLBACK branch push rc=%d out=%s" % (rc, out.strip()[-200:]))
    # 5) delivery self-verify
    git(["fetch", "origin"])
    rc, out = git(["rev-list", "--count", "origin/main..HEAD"])
    not_at_origin = out.strip()
    facts["not_at_origin"] = not_at_origin
    print("NOT-AT-ORIGIN=%s" % not_at_origin)
    facts["ts"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    with open(RECEIPT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    return 0 if not_at_origin == "0" else 6


if __name__ == "__main__":
    raise SystemExit(main())
