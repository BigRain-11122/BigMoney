# -*- coding: utf-8 -*-
"""r454 bm-c merge UU resolver: 3 regen faces, honest-ts take-newer (r450/r452/
r453 recipes, r661 bm-a precedent). Stage-2=ours, stage-3=theirs. Deterministic
same-day regen faces -> side choice = zero info loss; ts survey decides."""
import json
import re
import subprocess

CREATE = 0x08000000
REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
FILES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "results/prospect_paper/_summary.json",
    "results/t35_open_fill_verify.json",
]

TS_KEY = re.compile(r"(generated|updated|ts|asof|time|clock)", re.I)


def git(*a):
    r = subprocess.run(["git"] + list(a), capture_output=True, cwd=REPO,
                       creationflags=CREATE)
    return r.returncode, (r.stdout or b""), (r.stderr or b"")


def collect_ts(obj, out):
    """Recursively collect ISO-ish / epoch ts values from JSON."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                if TS_KEY.search(str(k)) and (
                        re.search(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}", v)):
                    out.append((str(k), v))
            elif isinstance(v, (int, float)):
                if TS_KEY.search(str(k)) and v > 1.7e9:
                    out.append((str(k), v))
            else:
                collect_ts(v, out)
    elif isinstance(obj, list):
        for it in obj:
            collect_ts(it, out)


def max_ts(blob_bytes):
    try:
        obj = json.loads(blob_bytes.decode("utf-8", "replace"))
    except Exception as e:
        return None, "PARSE_FAIL:" + str(e)
    hits = []
    collect_ts(obj, hits)
    best = None
    for k, v in hits:
        s = str(v)
        if best is None or s > str(best[1]):
            best = (k, v)
    return best, None


def main():
    decisions = {}
    for path in FILES:
        rc2, b2, _ = git("show", ":2:" + path)
        rc3, b3, _ = git("show", ":3:" + path)
        ours_ts, e2 = max_ts(b2) if rc2 == 0 else (None, "stage2 rc=%d" % rc2)
        theirs_ts, e3 = max_ts(b3) if rc3 == 0 else (None, "stage3 rc=%d" % rc3)
        print(f"SURVEY| {path}")
        print(f"  OURS   max_ts={ours_ts} {e2 or ''}")
        print(f"  THEIRS max_ts={theirs_ts} {e3 or ''}")
        if ours_ts is None or theirs_ts is None:
            side = "ours"  # regen face fallback: ours (this machine's latest cycle)
            why = "one side unparseable -> ours fallback"
        else:
            ov = str(ours_ts[1])
            tv = str(theirs_ts[1])
            if ov >= tv:
                side, why = "ours", f"ours ts {ov} >= theirs {tv}"
            else:
                side, why = "theirs", f"theirs ts {tv} > ours {ov}"
        decisions[path] = (side, why)
        print(f"  DECISION={side} ({why})")

    for path, (side, why) in decisions.items():
        flag = "--ours" if side == "ours" else "--theirs"
        rc, _, err = git("checkout", flag, "--", path)
        assert rc == 0, f"checkout {flag} {path} rc={rc} {err!r}"
        with open(REPO.replace("\\", "/") + "/" + path, "rb") as f:
            raw = f.read()
        assert b"<<<<<<<" not in raw, f"marker残留 in {path}"
        assert b">>>>>>>" not in raw, f"marker残留 in {path}"
        try:
            json.loads(raw.decode("utf-8", "replace"))
        except Exception as e:
            raise AssertionError(f"JSON reparse FAIL {path}: {e}")
        rc, _, err = git("add", path)
        assert rc == 0, f"add {path} rc={rc} {err!r}"
        print(f"RESOLVED| {path} -> {side} | {why} | zero-marker + JSON reparse PASS")
    print("ALL_RESOLVED")


if __name__ == "__main__":
    main()
