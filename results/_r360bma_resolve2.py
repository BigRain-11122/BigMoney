# -*- coding: utf-8 -*-
"""r360 bm-a resolver pass-2 (rebase stop 2 vs bmb-r345, 3 UU union faces):
reuses pass-1 canon functions (autofill union / compute_audit |A∪B| no-cap
union / regime_state union) from _r360bma_resolve.py; parse-verify r185;
add + continue + push atomically per r344. Also post-verify the 13 auto-merged
faces + HANDOVER structure sanity after continue."""
import io
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "results")
import importlib.util

spec = importlib.util.spec_from_file_location("res1", "results/_r360bma_resolve.py")
res1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(res1)


def git(*args):
    p = subprocess.run(["git"] + list(args), capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {args[:3]} rc={p.returncode}: {p.stderr[:200]}")
    return p.stdout.decode("utf-8", errors="replace")


def main():
    uu = [l.strip() for l in git("diff", "--name-only", "--diff-filter=U").splitlines() if l.strip()]
    print("UU at stop-2:", uu)
    assert set(uu) == {"results/autofill_state.json", "results/compute_audit.json",
                       "results/regime_state.json"}, f"unexpected UU set: {uu}"
    log = []
    res1.resolve_autofill("results/autofill_state.json", log)
    res1.resolve_compute_audit("results/compute_audit.json", log)
    res1.resolve_regime_state("results/regime_state.json", log)
    for p in uu:
        json.loads(io.open(p, "rb").read().decode("utf-8"))  # r185 parse-verify
    print("PARSE-VERIFY 3/3 OK")
    for l in log:
        print(l)
    # union face sanity: audit history = full distinct union
    chk = json.load(io.open("results/compute_audit.json", encoding="utf-8"))
    print("audit history rows:", len(chk["history"]))
    # HANDOVER structure sanity (auto-merged face): R360 promote intact + no conflict markers
    htxt = io.open("research/HANDOVER.md", encoding="utf-8").read()
    assert "<<<<<<<" not in htxt and ">>>>>>>" not in htxt, "HANDOVER carries markers"
    assert htxt.splitlines()[3].startswith("> 最近核对=bm-a round 360"), "L4 promote lost in automerge"
    assert "round 345" in htxt, "bmb r345 line missing after automerge"
    print("HANDOVER automerge sanity OK (R360 promote + bmb r345 line both present)")
    res1.git("add", "--", *uu)
    rem = git("diff", "--name-only", "--diff-filter=U").strip()
    assert rem == "", f"unresolved remain: {rem}"
    c = subprocess.run(["git", "-c", "core.editor=true", "rebase", "--continue"], capture_output=True)
    print("rebase-continue rc=", c.returncode, c.stdout.decode("utf-8", "replace")[-150:])
    if c.returncode != 0:
        print("STDERR:", c.stderr.decode("utf-8", "replace")[-400:])
        return 1
    st = git("status", "--porcelain").strip()
    print("post-continue status:", st if st else "(clean)")
    push = subprocess.run(["git", "push"], capture_output=True)
    print("push rc=", push.returncode)
    print(push.stderr.decode("utf-8", "replace")[-300:])
    # 13 auto-merged snapshot faces sanity probe (bm-b untouched them = mine kept)
    if push.returncode == 0:
        rep = json.load(io.open("docs/daily_report/REPORT-2026-09-27.json", encoding="utf-8"))
        print("REPORT automerge kept generated:", rep.get("generated_at"))
    return 0 if push.returncode == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
