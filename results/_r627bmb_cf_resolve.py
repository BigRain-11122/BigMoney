"""r627 bm-b: canonical resolve of results/crash_fuse.json (rebase UU).

Conflict: r626e churn-absorb (bm-b keepblock re-stamp @17:56:04 with
post-r626d runner shas 014fe069/7392ea8) vs origin r634 addendum side
(bm-a trio NULLS fuse re-stamp @17:44:04 with pre-fix shas efd7b44a/
2744ee59). Recipe = per-sig max-merge, whole-dict newer-wins by
last_refusal_ts (tie -> ours/HEAD, r140 law); cleared faces identical on
both sides (verified pre-merge). Correctness anchor: post-r626d every
machine's runner files hash 014fe069 (value) / 7392ea8 (divlowvol), so the
fuse sigs MUST carry those or the autofill gate auto-clears -> r616
ghost-claim double-burn. refusals counters drift (ours +4 each) is
informational telemetry only -- whole-dict assignment per canon, next
autofill tick re-increments.

Write-back: line-ending + indent mirrored from the origin (ours) blob.
Receipt: printed + asserted before add.
"""
import hashlib
import json
import subprocess
import sys

PATH = "results/crash_fuse.json"


def side(ref):
    b = subprocess.run(["git", "show", ref], capture_output=True).stdout
    return b, json.loads(b.decode("utf-8"))


def sig_ts(v):
    # None sorts as '' (oldest): a sig with no refusal ts never blocks anyway
    return v.get("last_refusal_ts") or ""


def main():
    bo, ours = side(":2:" + PATH)   # origin/main side (bm-a r634)
    bt, theirs = side(":3:" + PATH)  # r626e side (bm-b keepblock)

    # --- detect origin formatting (line ending + indent) ---
    eol = "\r\n" if b"\r\n" in bo else "\n"
    probe = bo.decode("utf-8").split(eol)
    indent = 0
    for ln in probe[1:]:
        if ln.strip():
            indent = len(ln) - len(ln.lstrip())
            break

    # --- cleared: per-key union (verified identical pre-merge; defensive) ---
    cleared = dict(ours.get("cleared", {}))
    for k, v in theirs.get("cleared", {}).items():
        cleared.setdefault(k, v)

    # --- sigs: per-key whole-dict newer-wins by last_refusal_ts ---
    sigs, taken = {}, {}
    for k in sorted(set(ours.get("sigs", {})) | set(theirs.get("sigs", {}))):
        o = ours.get("sigs", {}).get(k)
        t = theirs.get("sigs", {}).get(k)
        if o is None:
            sigs[k], taken[k] = t, "theirs-only"
        elif t is None:
            sigs[k], taken[k] = o, "ours-only"
        elif sig_ts(t) > sig_ts(o):
            sigs[k], taken[k] = t, "theirs-newer"
        else:
            sigs[k], taken[k] = o, "ours-newer-or-tie"
    out = {"cleared": cleared, "sigs": sigs}

    # --- correctness anchors (the reason this resolution is not take-new) ---
    cur = lambda p: hashlib.sha256(
        open(p.replace("/", "\\"), "rb").read()).hexdigest()[:16]
    v_sig = sigs["scripts/fund_value_p1.py|run,--nulls"]
    d_sig = sigs["scripts/fund_divlowvol_p1.py|run,--nulls"]
    q_sig = sigs["scripts/fund_quality_p1.py|run,--nulls"]
    assert v_sig["code_sha256"] == cur("scripts/fund_value_p1.py") == \
        "014fe069e80cfa06", "value sig must carry post-r626d sha"
    assert d_sig["code_sha256"] == cur("scripts/fund_divlowvol_p1.py") == \
        "7392ea8cd2f00469", "divlowvol sig must carry post-r626d sha"
    # quality sig = bm-a-local containment pin (r615/MSG-0842 off-caliber
    # cache; refusals increment ON bm-a where their local runner hashes to
    # 8f62ed17 -- their local file intentionally diverges from origin's
    # 88c06450). Both conflict sides agree on the sha; NOT compared to the
    # local file hash here (would false-fire on every non-bm-a machine).
    assert q_sig["code_sha256"] == "8f62ed1711cd27f6", \
        "quality containment pin sha must stay as both sides agreed"
    assert sig_ts(v_sig) == "2026-10-03 17:56:04"
    assert sig_ts(d_sig) == "2026-10-03 17:56:04"
    assert sig_ts(q_sig) == "2026-10-03 17:44:04"
    assert q_sig["refusals"] == 178, "newer quality stamp carries the"
    " higher refusal counter (bm-a 17:44:04 side)"

    # --- write back with origin formatting, newline translation mode ---
    text = json.dumps(out, ensure_ascii=False, indent=indent or 1)
    with open(PATH, "w", encoding="utf-8", newline=eol) as fh:
        fh.write(text)

    # --- re-parse validation before add (r185 law) ---
    chk = json.load(open(PATH, encoding="utf-8"))
    assert chk["sigs"]["scripts/fund_value_p1.py|run,--nulls"] == v_sig
    assert chk["sigs"]["scripts/fund_divlowvol_p1.py|run,--nulls"] == d_sig
    assert chk["sigs"]["scripts/fund_quality_p1.py|run,--nulls"] == q_sig
    assert set(chk["sigs"]) == set(sigs)
    assert set(chk["cleared"]) == set(cleared)

    diff3 = {k: taken[k] for k in taken if taken[k] != "ours-newer-or-tie"
             and taken[k] != "ours-only"}
    print(json.dumps({
        "resolved": PATH, "sig_total": len(sigs),
        "cleared_total": len(cleared),
        "divergent_sigs": {k: taken[k] for k in
                           ("scripts/fund_value_p1.py|run,--nulls",
                            "scripts/fund_divlowvol_p1.py|run,--nulls",
                            "scripts/fund_quality_p1.py|run,--nulls")},
        "other_divergent": {k: v for k, v in diff3.items()
                            if k not in
                            ("scripts/fund_value_p1.py|run,--nulls",
                             "scripts/fund_divlowvol_p1.py|run,--nulls",
                             "scripts/fund_quality_p1.py|run,--nulls")},
        "eol": "CRLF" if eol == "\r\n" else "LF", "indent": indent or 1,
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
