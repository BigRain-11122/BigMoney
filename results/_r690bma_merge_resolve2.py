# -*- coding: utf-8 -*-
"""r690 bm-a merge resolver leg-2: results/update_status.json single face,
per-face ts-freshness (r440/r461 canon: ts_norm before compare, probe-miss
needs dual-side review; regen face -> newer side, no-ts -> theirs)."""
import re, subprocess, io, json

CREATE_NO_WINDOW = 0x08000000
PATH = "results/update_status.json"


def blob(rev):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, PATH)],
                       capture_output=True, creationflags=CREATE_NO_WINDOW)
    return r.stdout if r.returncode == 0 else None


def norm_ts(b):
    # r461 law: normalize T-form/space-form + timezone suffix before compare
    m = re.search(r'"(?:ts|updated|asof|now|generated)"\s*:\s*"?(\d{4}-\d{2}-\d{2})'
                  r'[ T](\d{2}:\d{2}:\d{2})', b.decode("utf-8", "replace"))
    return (m.group(1) + " " + m.group(2)) if m else ""


ours, theirs = blob("HEAD"), blob("MERGE_HEAD")
t_o, t_t = norm_ts(ours), norm_ts(theirs)
assert ours is not None and theirs is not None, "blob fetch failed"
if t_o and t_t:
    pick = "ours" if t_o >= t_t else "theirs"
else:
    pick = "theirs"  # regen snapshot, origin side, r437 law
data = ours if pick == "ours" else theirs
# json reparse proof before write (r645 state-tail-comma family guard)
json.loads(data.decode("utf-8", "replace"))
with io.open(PATH, "wb") as fh:
    fh.write(data)
rec = {"path": PATH, "pick": pick, "ts_ours": t_o, "ts_theirs": t_t}
with io.open("results/_r690bma_merge_resolve2.json", "w", encoding="utf-8",
             newline="\n") as fh:
    json.dump(rec, fh, ensure_ascii=False, indent=1)
print("resolved:", rec)
