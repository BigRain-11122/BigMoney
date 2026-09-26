"""r284 bm-b: T-87 ticket progress_r284_bmb insert (byte-face law R255/R257).

Five-face probe pre-write: BOM=no, EOL=LF-only, ensure_ascii=False,
indent=1, trailing_newline=yes. Write mirrors all five; git diff --stat
must stay field-increment level (R255 double gate).
"""
import io
import json
import subprocess

P = "fleet/tasks/T-2026-09-26-87-P1.json"
PROGRESS_R284 = (
    "T-87 r284 bm-b supply-lane pass mid-flight health probe #4: "
    "results/_r284bmb_astock_pass_probe.py/.json -- verdict on_track "
    "@2026-09-27T00:43:43: per_files 714/5228 (13.7%), rate 12.65/min "
    "(lock-start face), ETA 2026-09-27T06:40:36 = ~26.5h before Mon 09-28 "
    "09:15 first live fire; 713/714 files at expected cutoff 2026-09-24 "
    "(1 early-tail = suspended face, honest); frozen-header check 0 "
    "mismatches across all 714 files; OHLC sanity 3-sample 0 bad; lock "
    "alive; r283 probe #3 (591/5228, ETA 06:41:49) same face on_track -- "
    "rate face stable across probes 3->4 (12.61 -> 12.65/min); "
    "pass-completion re-probe queued for after ETA ~06:41; stragglers gate "
    "self-heal lands with Mon first daily-continuation fire"
)

raw = open(P, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf", "BOM face drifted"
assert b"\r\n" not in raw, "EOL face drifted"
assert raw.endswith(b"\n"), "tail-newline face drifted"
assert b"\\u" not in raw, "ensure_ascii face drifted"

d = json.loads(raw.decode("utf-8"))
assert d.get("progress_r283_bmb"), "anchor field missing"

if "progress_r284_bmb" in d:
    # idempotent re-verify mode (r284: first write already landed, gate bug fixed)
    assert d["progress_r284_bmb"] == PROGRESS_R284, "existing field drift"
    print("field already present -> verify-only mode")
else:
    # insert after progress_r283_bmb preserving key order
    items = list(d.items())
    out = {}
    for k, v in items:
        out[k] = v
        if k == "progress_r283_bmb":
            out["progress_r284_bmb"] = PROGRESS_R284

    with io.open(P, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")

# post-write self-checks: five faces + field-increment diff gate
raw2 = open(P, "rb").read()
assert raw2.endswith(b"\n") and b"\r\n" not in raw2 and raw2[:3] != b"\xef\xbb\xbf"
d2 = json.loads(raw2.decode("utf-8"))
assert d2["progress_r284_bmb"] == PROGRESS_R284
stat = subprocess.run(["git", "diff", "--stat", "--", P],
                      capture_output=True, text=True).stdout.strip()
print("DIFF_STAT:", stat)
# summary line = last line "N file(s) changed, X insertions(+), Y deletions(-)"
summary = stat.splitlines()[-1] if stat else ""
import re as _re
m = _re.search(r"(\d+) insertion", summary)
assert m and int(m.group(1)) <= 3, f"non-increment diff face: {summary}"
assert "deletion" not in summary or int(_re.search(r"(\d+) deletion", summary).group(1)) <= 2, \
    f"non-increment diff face: {summary}"
print("SUMMARY:", summary)
print("OK: field insert verified, byte faces stable")
