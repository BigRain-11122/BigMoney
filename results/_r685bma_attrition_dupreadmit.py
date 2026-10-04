"""r685 bm-a: re-add my superseded duplicate-run attrition row (post-merge).

Guard law r448: keys (batch,ts) monotone -- my HEAD key must survive the merge.
Resolution: origin r483 row (16:13:57) = canonical single-source; my duplicate
deterministic run (identical numbers) re-added with superseded annotation.
Surgical tail insert (roundtrip differs, r678).
"""
import difflib, json, subprocess

PATH = r"results/gate_attrition.json"

# my row from HEAD blob (the one whose ts != 16:13:57)
hb = subprocess.run(["git", "show", "HEAD:results/gate_attrition.json"],
                    capture_output=True).stdout
h = json.loads(hb.decode("utf-8"))
mine = [e for e in h["entries"]
        if e.get("batch") == "MASS_TRIAL_W3" and e.get("ts") != "2026-10-04 16:13:57"]
assert len(mine) == 1, f"expected 1 local dup row, got {len(mine)}"
row = dict(mine[0])
row["note"] = ("[SUPERSEDED duplicate run -- r483 bm-c origin row ts 16:13:57 "
               "= canonical single-source; parallel same-window deterministic "
               "finalize, identical numbers 4814/785/646799; retained per r448 "
               "monotone-key law] " + row.get("note", ""))
row["adjudicated"] = "duplicate-run superseded by r483 bm-c origin row"

raw = open(PATH, "rb").read()
d = json.loads(raw.decode("utf-8"))
assert not any(e.get("batch") == "MASS_TRIAL_W3" and e.get("ts") == row["ts"]
              for e in d["entries"]), "my row already present"

text = raw.decode("utf-8")
lines = text.split("\n")
ci = None
for i, ln in enumerate(lines):
    if ln.rstrip("\r") == " ]," and i + 1 < len(lines) \
            and lines[i + 1].rstrip("\r").startswith(' "history"'):
        ci = i
        break
assert ci is not None, "entries closer not found"
assert lines[ci - 1].rstrip("\r") == "  }", f"unexpected close: {lines[ci-1]!r}"

row_text = json.dumps(row, ensure_ascii=False, indent=1)
row_lines = [" " + l for l in row_text.split("\n")]
new = lines[:ci - 1] + ["  },"] + row_lines + lines[ci:]

d2 = json.loads("\n".join(new))
assert len(d2["entries"]) == len(d["entries"]) + 1
assert any(e.get("batch") == "MASS_TRIAL_W3" and e.get("ts") == row["ts"]
           for e in d2["entries"])
assert d2["entries"][:-1] == d["entries"], "earlier entries mutated"
diff = sum(1 for l in difflib.unified_diff(lines, new, lineterm="", n=0)
           if (l.startswith("+") and not l.startswith("+++")) or
              (l.startswith("-") and not l.startswith("---")))
assert diff == 2 + len(row_lines), f"changed {diff} != {2+len(row_lines)}"

open(PATH, "w", encoding="utf-8", newline="").write("\n".join(new))
print(json.dumps({"re_added": "MASS_TRIAL_W3@" + row["ts"],
                  "entries": len(d2["entries"]), "changed_lines": diff}))
