# -*- coding: utf-8 -*-
"""r456 bm-c token_usage merge-face correction: the r456 merge_resolve per-key
union leg found no per-key ts (machines entries carry no ts; sole freshness
key = top 'generated') and effectively wrote a theirs-based base -- losing our
08:52 bm-c face. r455 recipe for identical-keyset + ours-newer = whole-file
OURS. Sides re-taken from HEAD/MERGE_HEAD blobs (r657 law-2: add smears
stages; MERGE_HEAD still in place pre-commit = equivalent + add-immune)."""
import json
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PATH = "results/token_usage.json"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def raw(args):
    return subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                          creationflags=CNW).stdout


def main():
    o = raw(["show", "HEAD:" + PATH])
    t = raw(["show", "MERGE_HEAD:" + PATH])
    jo = json.loads(o.decode("utf-8"))
    jt = json.loads(t.decode("utf-8"))
    go = jo.get("generated", "")
    gt = jt.get("generated", "")
    assert go and gt, "generated keys missing: %r / %r" % (go, gt)
    assert go >= gt, "ours NOT newer (%s vs %s) -- whole-ours unlawful" % (go, gt)
    ko, kt = set(jo.get("machines", {})), set(jt.get("machines", {}))
    assert ko == kt, "machine keyset diverged: %r" % (ko ^ kt,)
    with open(ROOT + "\\" + PATH.replace("/", "\\"), "wb") as f:
        f.write(o)
    back = open(ROOT + "\\" + PATH.replace("/", "\\"), "rb").read()
    chk = json.loads(back.decode("utf-8"))
    assert chk["generated"] == go, "roundtrip generated mismatch"
    assert not any(ln.startswith(b"<<<<<<<") or ln.startswith(b">>>>>>>")
                   or ln.strip() == b"=======" for ln in back.split(b"\n")), "marker"
    r = subprocess.run(["git", "add", PATH], capture_output=True, cwd=ROOT,
                       creationflags=CNW)
    assert r.returncode == 0, "add failed"
    print("TOKEN_USAGE whole-ours by generated %s > %s (identical machine "
          "keyset %d keys; r455 recipe; ours bm-c face 08:52 preserved)"
          % (go, gt, len(ko)))


if __name__ == "__main__":
    main()
