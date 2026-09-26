"""r283 bm-b: T-87 ticket progress_r283_bmb insert (byte-face law R255/R257).

Five-face probe done pre-write: BOM=no, EOL=LF-only, ensure_ascii=False,
indent=1, trailing_newline=yes. Write mirrors all five; git diff --stat
must stay field-increment level (R255 double gate).
"""
import io
import json
import subprocess

P = "fleet/tasks/T-2026-09-26-87-P1.json"
PROGRESS_R283 = (
    "T-87 r283 bm-b supply-lane pass mid-flight health probe #3: "
    "results/_r283bmb_astock_pass_probe.py/.json -- verdict on_track "
    "@2026-09-27T00:34:08: per_files 591/5228 (11.3%), rate 12.61/min "
    "(lock-start face), ETA 2026-09-27T06:41:49 = ~32.5h before Mon 09-28 "
    "09:15 first live fire; 590/591 files at expected cutoff 2026-09-24 "
    "(1 early-tail 2026-09-03 = suspended face, honest); frozen-header "
    "check 0 mismatches across all 591 files; OHLC sanity 3-sample 0 bad; "
    "lock alive; attempts=1 (000019, self-heal on next gate spawn per "
    "family law); r282 probe #2 (450/5228, results/_r282bmb_astock_pass_"
    "probe.json) same face on_track -- pass-completion re-probe next "
    "rounds; stragglers gate self-heal lands with Mon first "
    "daily-continuation fire"
)

raw = open(P, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf", "BOM face drifted"
assert b"\r\n" not in raw, "EOL face drifted"
assert raw.endswith(b"\n"), "tail-newline face drifted"
assert b"\\u" not in raw, "ensure_ascii face drifted"

d = json.loads(raw.decode("utf-8"))
assert "progress_r283_bmb" not in d, "field already present"
assert d.get("progress_r281_bmb"), "anchor field missing"

# insert after progress_r281_bmb preserving key order
items = list(d.items())
out = {}
for k, v in items:
    out[k] = v
    if k == "progress_r281_bmb":
        out["progress_r283_bmb"] = PROGRESS_R283

with io.open(P, "w", encoding="utf-8", newline="\n") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
    f.write("\n")

# post-write self-checks: five faces + field-increment diff gate
raw2 = open(P, "rb").read()
assert raw2.endswith(b"\n") and b"\r\n" not in raw2 and raw2[:3] != b"\xef\xbb\xbf"
d2 = json.loads(raw2.decode("utf-8"))
assert d2["progress_r283_bmb"] == PROGRESS_R283
stat = subprocess.run(["git", "diff", "--stat", "--", P],
                      capture_output=True, text=True).stdout.strip()
print("DIFF_STAT:", stat)
lines = [l for l in stat.splitlines() if "|" in l]
if lines:
    add_del = lines[0].split("|")[-1].strip()
    print("ADD_DEL:", add_del)
    assert "3 insertions" in add_del or "2 insertions" in add_del, \
        f"non-increment diff face: {add_del}"
print("OK: field insert verified, byte faces stable")
