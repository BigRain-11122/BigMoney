# -*- coding: utf-8 -*-
"""R262 bm-b: resolver finisher -- compute_audit latest.ts re-adjudication
(the first pass defaulted on None-vs-None), dashboard_status.json
meta.generated_at, 7 snapshot files take :3 (mine newer, per-file probed)."""
import io
import json
import subprocess


def stage(n, path):
    return subprocess.run(["git", "show", f":{n}:{path}"],
                          capture_output=True).stdout


def jload(n, path):
    return json.loads(stage(n, path).decode("utf-8-sig"))


def face_of(raw):
    return {"bom": raw.startswith(b"\xef\xbb\xbf"),
            "crlf": b"\r\n" in raw,
            "trailing_nl": raw.endswith(b"\n")}


def dump_face(d, face):
    txt = json.dumps(d, ensure_ascii=False, indent=1)
    if not face["trailing_nl"]:
        txt = txt.rstrip("\n")
    out = txt.encode("utf-8")
    if face["bom"]:
        out = b"\xef\xbb\xbf" + out
    if face["crlf"]:
        out = out.replace(b"\n", b"\r\n")
    return out


# --- compute_audit redo: keep on-disk union history, re-adjudicate latest ---
p = "results/compute_audit.json"
c2, c3 = jload(2, p), jload(3, p)
t2 = c2["latest"].get("ts")
t3 = c3["latest"].get("ts")
disk = json.loads(io.open(p, encoding="utf-8-sig").read())
winner_latest = c3["latest"] if (t3 or "") >= (t2 or "") else c2["latest"]
out = dict(c3 if (t3 or "") >= (t2 or "") else c2)
out["latest"] = winner_latest
out["history"] = disk["history"]            # union from pass 1 (zero-loss)
face2 = face_of(stage(2, p))
io.open(p, "wb").write(dump_face(out, face2))
json.loads(io.open(p, encoding="utf-8-sig").read())
print(f"compute_audit redo: latest.ts {t3} vs {t2} -> "
      f"{'mine(:3)' if (t3 or '') >= (t2 or '') else 'bm-a(:2)'}; "
      f"union history {len(disk['history'])} kept")

# --- dashboard_status.json: meta.generated_at, whole-byte take-side ---
p = "results/dashboard_status.json"
d2, d3 = jload(2, p), jload(3, p)
g2 = (d2.get("meta") or {}).get("generated_at")
g3 = (d3.get("meta") or {}).get("generated_at")
win = 3 if (g3 or "") >= (g2 or "") else 2
io.open(p, "wb").write(stage(win, p))
json.loads(io.open(p, encoding="utf-8-sig").read())
print(f"dashboard_status.json: meta.generated_at {g3} vs {g2} -> :{win}")

# --- 7 snapshots: :3 whole bytes (all probed mine-newer) ---
SNAPS = ["results/fundamental_b_layer_filter.json",
         "results/futures_update_status.json",
         "results/heat_update_status.json",
         "results/lhb_update_status.json",
         "results/token_usage.json",
         "results/update_status.json"]
for p in SNAPS:
    io.open(p, "wb").write(stage(3, p))
    json.loads(io.open(p, encoding="utf-8-sig").read())
    print(f"{p}: take :3 whole bytes (probed mine-newer)")

print("FINISHER DONE")
