"""r1049 bm-a: memory-gov origin-gap closeout via CAS surgical delivery.

Receipts: MSG-20261018-0753-bmb (gaps 1+2) + MSG-20261018-0831-bmc (gap 3).
Delivers to GROUP origin (FluxGroup repo), zero worktree touch:
  1. cph4/skills/memory-curator/SKILL.md        (untracked local canon -> origin)
  2. cph4/research/R-20261018-memory-control-01.md (untracked local canon -> origin)
  3. Tools/fleet-poke-worker.ps1 = origin v1.10 blob with the union/memsync
     block replaced by the v1.9 RETIRED tombstone (extracted from the local
     v1.9 worktree face). Zero revert of the v1.10 hung-round revival.

Laws: r486 CAS recipe + r798 40-hex hard verification + push-output four-word
check (fatal/rejected/failed/error) + post-push origin blob byte-equality
self-verify (machine-delivery reconciliation law, --no-filters byte-exact).
"""
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCR = os.path.join(HERE, "_r1049bma_gap")
G = r"C:\Users\sjs20\Desktop\FluxGroup"
IDX = os.path.join(SCR, "cas_index")
os.makedirs(SCR, exist_ok=True)

FILES = [
    ("cph4/skills/memory-curator/SKILL.md",
     os.path.join(G, "cph4", "skills", "memory-curator", "SKILL.md"), "copy"),
    ("cph4/research/R-20261018-memory-control-01.md",
     os.path.join(G, "cph4", "research", "R-20261018-memory-control-01.md"), "copy"),
    ("Tools/fleet-poke-worker.ps1", None, "merge"),
]

MSG = """bm-a memory-gov origin-gap closeout (receipts MSG-20261018-0753-bmb + MSG-20261018-0831-bmc):

1. cph4/skills/memory-curator/SKILL.md canon pushed (AGENT-LIBRARY v1.0.2 registration now has its body on origin; bm-b re-install next window)
2. cph4/research/R-20261018-memory-control-01.md research canon pushed (CEO memory-gov order 00:2x estate authored by the dead window, never pushed; bm-c read-back verification next window)
3. Tools/fleet-poke-worker.ps1: v1.9 union-block retire (tombstone) surgically merged onto origin v1.10 hung-round revival -- zero revert of v1.10, union/memsync spawn retired per memory.md S8/S10

Delivery = CAS surgical (temp index + commit-tree + push sha:main), zero worktree touch.
-- bm-a r1049 loop window
"""


def run(args, env_extra=None):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(args, capture_output=True, env=env)
    return r.returncode, r.stdout, r.stderr


def is40(s):
    return bool(re.fullmatch(r"[0-9a-f]{40}", (s or "").decode().strip()
                             if isinstance(s, bytes) else (s or "").strip()))


def build_merged_poke_worker():
    """origin v1.10 blob + v1.9 tombstone replacing the union/memsync block."""
    rc, blob, err = run(["git", "-C", G, "show",
                         "origin/main:Tools/fleet-poke-worker.ps1"])
    assert rc == 0, "origin blob fetch failed: %r" % err
    text = blob.decode("utf-8")
    crlf = "\r\n" in text
    with open(os.path.join(G, "Tools", "fleet-poke-worker.ps1"), "rb") as f:
        local = f.read().decode("utf-8", errors="replace")
    m = re.search(r"# ---- global memory union-sync RETIRED.*?history\. ----",
                  local, re.S)
    assert m, "v1.9 tombstone not found in local worktree face"
    eol = "\r\n" if crlf else "\n"
    tomb = eol.join(m.group(0).replace("\r\n", "\n").split("\n"))
    pat = re.compile(
        re.escape("# ---- global memory union-sync (O-20261009-1845:")
        + r".*?"
        + re.escape("} catch { WK-Log 'memsync-fail' ([string]$_.Exception.Message) }"),
        re.S)
    hits = pat.findall(text)
    assert len(hits) == 1, "union block hits=%d (expect 1)" % len(hits)
    merged = pat.sub(lambda _m: tomb, text, count=1)
    # hard asserts: v1.10 intact, union call gone, tombstone in
    assert "hung-round revival" in merged, "v1.10 header comment lost"
    assert "HUNG-RESTART" in merged, "v1.10 revival code lost"
    assert "union-sync RETIRED" in merged, "tombstone missing"
    assert "Bypass -File $memSync" not in merged, "memsync spawn still present"
    assert merged.count("global memory union-sync") == 1, "union residue"
    out = os.path.join(SCR, "poke_worker_merged.ps1")
    with open(out, "wb") as f:
        f.write(merged.encode("utf-8"))
    return out, len(blob), len(merged.encode("utf-8"))


def attempt(receipt):
    rc, tip, err = run(["git", "-C", G, "rev-parse", "origin/main"])
    assert rc == 0 and is40(tip), "origin tip resolve failed: %r" % err
    tip = tip.decode().strip()
    blob_shas = {}
    for path, src, kind in FILES:
        if kind == "merge":
            src, n0, n1 = build_merged_poke_worker()
            receipt["poke_worker_bytes"] = {"origin": n0, "merged": n1}
        else:
            dst = os.path.join(SCR, os.path.basename(src))
            shutil.copyfile(src, dst)
            src = dst
        rc, sha, err = run(["git", "-C", G, "hash-object", "-w", "--no-filters", src])
        assert rc == 0 and is40(sha), "hash-object failed for %s: %r" % (path, err)
        blob_shas[path] = sha.decode().strip()
    if os.path.exists(IDX):
        os.unlink(IDX)
    env = {"GIT_INDEX_FILE": IDX}
    rc, _, err = run(["git", "-C", G, "read-tree", tip], env_extra=env)
    assert rc == 0, "read-tree failed: %r" % err
    for path, sha in blob_shas.items():
        rc, _, err = run(["git", "-C", G, "update-index", "--add",
                          "--cacheinfo", "100644,%s,%s" % (sha, path)],
                         env_extra=env)
        assert rc == 0, "update-index failed for %s: %r" % (path, err)
    rc, tree, err = run(["git", "-C", G, "write-tree"], env_extra=env)
    assert rc == 0 and is40(tree), "write-tree failed: %r" % err
    tree = tree.decode().strip()
    msgf = os.path.join(SCR, "commitmsg.txt")
    with open(msgf, "w", encoding="utf-8", newline="\n") as f:
        f.write(MSG)
    rc, newc, err = run(["git", "-C", G, "commit-tree", tree, "-p", tip, "-F", msgf])
    assert rc == 0 and is40(newc), "commit-tree failed: %r" % err
    newc = newc.decode().strip()
    rc, out, err = run(["git", "-C", G, "push", "origin", "%s:main" % newc])
    combined = (out + err).decode("utf-8", errors="replace").lower()
    receipt["push_rc"] = rc
    receipt["push_out_tail"] = (out + err).decode("utf-8", errors="replace")[-400:]
    ok = rc == 0 and not any(w in combined for w in
                             ("fatal", "rejected", "failed", "error"))
    receipt["push_ok"] = ok
    if not ok:
        return None
    return (newc, tip, tree, dict(blob_shas))


def main():
    receipt = {"ts_round": "r1049"}
    result = None
    for i in (1, 2):
        result = attempt(receipt)
        if result:
            receipt["attempt"] = i
            break
        rc, _, _ = run(["git", "-C", G, "fetch", "origin"])
        receipt["retry"] = True
    if not result:
        receipt["verdict"] = "PUSH_FAILED_TWICE"
        json.dump(receipt, open(os.path.join(SCR, "receipt.json"), "w"),
                  ensure_ascii=True, indent=1)
        print("PUSH_FAIL_TAIL: " + receipt.get("push_out_tail", ""))
        return 2
    newc, tip, tree, blobs = result
    # post-push self-verify: fetch + tip equality + per-path blob equality
    run(["git", "-C", G, "fetch", "origin"])
    rc, otip, _ = run(["git", "-C", G, "rev-parse", "origin/main"])
    otip = otip.decode().strip()
    assert otip == newc, "origin tip %s != pushed %s" % (otip, newc)
    for path, sha in blobs.items():
        rc, psha, _ = run(["git", "-C", G, "rev-parse", "origin/main:%s" % path])
        assert rc == 0 and psha.decode().strip() == sha, \
            "blob mismatch on %s" % path
    if os.path.exists(IDX):
        os.unlink(IDX)
    receipt.update({"verdict": "DELIVERED", "newc": newc, "parent": tip,
                    "tree": tree, "blobs": blobs,
                    "origin_tip_verified": otip})
    json.dump(receipt, open(os.path.join(SCR, "receipt.json"), "w"),
              ensure_ascii=True, indent=1)
    print(json.dumps({"verdict": "DELIVERED", "newc": newc,
                      "blobs": {k: v[:12] for k, v in blobs.items()}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
