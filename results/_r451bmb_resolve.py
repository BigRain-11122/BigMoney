"""r451 bm-b rebase collision resolver -- Tools/fill_ladder_catalog.json.

Push-rejection batch (S7 law exception): my bd5d48feb (SLOT-8 pool-entry
adoption, append at tail) vs upstream acc08c505 (bm-c r259 SLOT-9 berth
package, append at tail). Classifier = UNKNOWN (catalog not in known-form
table) -> manual recipe per SKILL.md: berth-catalog append shape = UNION by
entry id, shared entries take upstream newest state (my commit base was
older), unique entries appended (zero-loss). Read git blobs as bytes via
subprocess (PowerShell `>` redirect emits UTF-16 BOM artifacts -- r209 law).
Validates json.loads round-trip + id-set union before writing.
"""
import json
import subprocess
import sys

PATH = "Tools/fill_ladder_catalog.json"
UPSTREAM = "acc08c505"   # bm-c r259 SLOT-9 berth package (rebase HEAD side)
MINE = "bd5d48feb"       # bm-b r451 SLOT-8 pool-entry adoption (theirs side)


def blob(rev):
    out = subprocess.run(["git", "show", rev + ":" + PATH],
                          capture_output=True)
    if out.returncode != 0:
        sys.exit(f"git show failed for {rev}: {out.stderr!r}")
    return json.loads(out.stdout.decode("utf-8"))


def main():
    up = blob(UPSTREAM)
    mine = blob(MINE)
    up_ids = [e["id"] for e in up["entries"]]
    my_ids = [e["id"] for e in mine["entries"]]
    dup_up = len(up_ids) - len(set(up_ids))
    dup_my = len(my_ids) - len(set(my_ids))
    assert dup_up == 0 and dup_my == 0, "duplicate ids within one side"
    only_mine = [i for i in my_ids if i not in set(up_ids)]
    merged_ids = up_ids + only_mine
    assert len(merged_ids) == len(set(merged_ids)), "union id collision"
    # zero-loss: union id-set == superset of both sides
    assert set(merged_ids) >= set(up_ids) | set(my_ids)
    merged = dict(up)                      # top-level faces from upstream
    merged["entries"] = up["entries"] + [e for e in mine["entries"]
                                         if e["id"] in set(only_mine)]
    txt = json.dumps(merged, ensure_ascii=False, indent=1)
    json.loads(txt)                        # parse-validation before write
    with open(PATH, "w", encoding="utf-8", newline="") as fh:
        fh.write(txt)
    print(f"union OK: upstream {len(up_ids)} + only-mine {len(only_mine)} "
          f"-> {len(merged_ids)} entries; only-mine={only_mine}")


if __name__ == "__main__":
    main()
