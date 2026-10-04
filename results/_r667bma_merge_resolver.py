"""r667 bm-a merge UU resolver: json-twin ts-settle + snapshot ts-newer-wins.

Faces (r652/r656/r661 recipe):
  - docs/daily_report/REPORT-2026-10-04.{json,md}  : deep ts in json picks side; md copied from same side
  - docs/live_usage/LIVE-2026-10-04.{json,md}      : same twin law
  - docs/live_usage/LIVE-latest.{json,md}         : same twin law
  - results/_attrition_guard_scan.json            : snapshot, ts-newer-wins
  - results/fundamental_b_layer_filter.json      : snapshot, ts-newer-wins
Every pick prints the compared ts values (probe-miss default banned: both sides
must be read and disclosed per r656 law). Zero-loss = byte copy of winning side.
"""
import json
import subprocess
import sys


def show(ref, path):
    return subprocess.run(["git", "show", f"{ref}:{path}"],
                           capture_output=True).stdout


def deep_ts(blob):
    d = json.loads(blob)

    def find_ts(o, depth=0):
        if depth > 4:
            return None
        if isinstance(o, dict):
            for k in ("ts", "updated", "updated_at", "generated", "now",
                      "scan_ts", "written_at"):
                if k in o and isinstance(o[k], str):
                    return (k, o[k])
            for v in o.values():
                r = find_ts(v, depth + 1)
                if r:
                    return r
        return None
    return find_ts(d)


def settle_twin(base):
    jo = show("HEAD", base + ".json")
    jt = show("MERGE_HEAD", base + ".json")
    to, tt = deep_ts(jo), deep_ts(jt)
    print(f"{base}.json ours_ts={to} theirs_ts={tt}")
    if (to or ("", ""))[1] >= (tt or ("", ""))[1]:
        side, jb, mb = "ours", jo, show("HEAD", base + ".md")
    else:
        side, jb, mb = "theirs", jt, show("MERGE_HEAD", base + ".md")
    with open(base + ".json", "wb") as fh:
        fh.write(jb)
    with open(base + ".md", "wb") as fh:
        fh.write(mb)
    json.loads(open(base + ".json", "rb").read())  # parse-verify
    print(f"  -> settled {side} (json+md byte copy, parse OK)")
    return side


def settle_snapshot(path):
    o = show("HEAD", path)
    t = show("MERGE_HEAD", path)
    to, tt = deep_ts(o), deep_ts(t)
    print(f"{path} ours_ts={to} theirs_ts={tt}")
    if (to or ("", ""))[1] >= (tt or ("", ""))[1]:
        side, b = "ours", o
    else:
        side, b = "theirs", t
    with open(path, "wb") as fh:
        fh.write(b)
    json.loads(open(path, "rb").read())
    print(f"  -> settled {side} (byte copy, parse OK)")
    return side


if __name__ == "__main__":
    for base in ("docs/daily_report/REPORT-2026-10-04",
                 "docs/live_usage/LIVE-2026-10-04",
                 "docs/live_usage/LIVE-latest"):
        settle_twin(base)
    for p in ("results/_attrition_guard_scan.json",
              "results/fundamental_b_layer_filter.json"):
        settle_snapshot(p)
    print("resolver done")
