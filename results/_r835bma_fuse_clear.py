# -*- coding: utf-8 -*-
"""r835 bm-a crash-fuse 4-face clear surgery: FUND-DIVLOWVOL-P1-NULLS --nulls sig.

Laws: r393 (clear-with-reason MSG same-window), r400 (cleared_ts = action-time),
r603 (cleared_ts > lane-tail refusal/crash ts), r616 (all-lane consistency),
r637 four-face surgery precedent, r617 (version-key law N/A: anchor==current).
Evidence: r625 keep-block own clearing condition MET (T-156 verified 10-03);
current sig = r637 ghost-claim kill artifact (nulls.log zero-error zero-progress);
probe PASS 16/16 legs re-verified 2026-10-07; takeover ladder OPEN (bm-b stale 186min).
"""
import datetime
import json

KEY = "scripts/fund_divlowvol_p1.py|run,--nulls"
FACES = [
    "results/crash_fuse.json",
    "results/crash_fuse.bm-a.json",
    "results/crash_fuse.bm-b.json",
    "results/crash_fuse.bm-c.json",
]
NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
REASON = (
    "data_fixed_takeover_20261007: r625 keep-block own clearing condition MET "
    "(T-156 p1c_stock TRANSFER+verify 10-03 14:39 four-point ALL PASS incl 13/13 "
    "sha256==sender manifest + n_base 3292==bm-b basis; DIVLOWVOL-SENS clean burn "
    "500/500 rc0 r630 + r632 caliber verdict canonical CLEAN); this sig = 18:53:16 "
    "re-arm artifact of r637 ghost-claim release surgery (pid 19856 killed 5min in, "
    "nulls.log zero-error zero-progress = external kill, r696 false-crash family, "
    "NOT runner/data fault); probe PASS 16/16 legs re-verified 2026-10-07 "
    "(transfer-manifest sha256 match + t0 frozen reproduction 2006-02-06 + sidecar "
    "zero-missing); takeover ladder OPEN (bm-b hb stale 186min, claim stale 2.2h, "
    "r297/r603); NULLS rows deterministic per-k union-safe (r297 LOWAMP precedent); "
    "family finalize unblocked only by NULLS completion (r632)"
)


def main():
    for path in FACES:
        with open(path, "rb") as f:
            raw = f.read()
        d = json.loads(raw.decode("utf-8-sig"))
        sig = d["sigs"].pop(KEY, None)
        if sig is None:
            print("WARN %s: sig already absent" % path)
            continue
        d.setdefault("cleared", {})[KEY] = {
            "crashes": sig.get("count", 1),
            "old_code_sha256": sig.get("code_sha256"),
            "cleared_by": "bm-a",
            "cleared_ts": NOW,
            "reason": REASON,
        }
        text = json.dumps(d, indent=1, ensure_ascii=False)
        out = text.replace("\n", "\r\n").encode("utf-8")
        with open(path, "wb") as f:
            f.write(out)
        # verify
        d2 = json.loads(open(path, "rb").read().decode("utf-8-sig"))
        assert KEY not in d2["sigs"], "resurrect on " + path
        assert d2["cleared"][KEY]["cleared_ts"] == NOW, "cleared ts mismatch " + path
        print("CLEARED %s (old refusals=%s)" % (path, sig.get("refusals")))
    print("ACTION_TS=%s" % NOW)


if __name__ == "__main__":
    main()
