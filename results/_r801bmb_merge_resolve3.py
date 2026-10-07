# r801-3 bm-b merge resolver: 14 UU S6 shared-regen family, per-face ts-empirical (r773 law, strptime-normalized per r709/r756).
import subprocess, json, hashlib, datetime, re

def blob(stage, path):
    h = subprocess.run(["git", "rev-parse", "-q", "--verify", f":{stage}:{path}"],
                       capture_output=True, text=True).stdout.strip()
    assert h, f"stage {stage} missing for {path}"
    return subprocess.run(["git", "cat-file", "blob", h], capture_output=True).stdout.decode("utf-8", "replace")

def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)

TS_KEYS = ("generated", "updated", "ts", "updated_at", "scan_at", "generated_at")
def face_ts(d):
    best = None
    def walk(x):
        nonlocal best
        if isinstance(x, dict):
            for k, v in x.items():
                if k in TS_KEYS and isinstance(v, str):
                    s = v.strip().replace(" ", "T")
                    m = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})", s)
                    if m:
                        t = m.group(1)
                        if best is None or t > best: best = t
                else:
                    walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(d)
    return best

receipt = {"round": "r801-3", "faces": {}}
SNAP = ["results/_attrition_guard_scan.json", "results/fundamental_b_layer_filter.json",
        "results/futures_update_status.json", "results/lhb_update_status.json", "results/update_status.json",
        "docs/daily_report/REPORT-2026-10-07.json", "docs/live_usage/LIVE-2026-10-07.json",
        "docs/live_usage/LIVE-latest.json"]
for p in SNAP:
    jo, jt = json.loads(blob(2, p)), json.loads(blob(3, p))
    to, tt = face_ts(jo), face_ts(jt)
    side = "ours" if (to or "") >= (tt or "") else "theirs"
    src = jo if side == "ours" else jt
    out = json.dumps(src, ensure_ascii=False, indent=1) + "\n"
    write(p, out)
    receipt["faces"][p] = {"recipe": f"ts-newer-wins -> {side}", "ours_ts": to, "theirs_ts": tt,
                           "sha16": hashlib.sha256(out.encode()).hexdigest()[:16]}

# md twins follow their json same side (r708 twin law)
for md, js in [("docs/daily_report/REPORT-2026-10-07.md", "docs/daily_report/REPORT-2026-10-07.json"),
               ("docs/live_usage/LIVE-2026-10-07.md", "docs/live_usage/LIVE-2026-10-07.json"),
               ("docs/live_usage/LIVE-latest.md", "docs/live_usage/LIVE-latest.json")]:
    side = receipt["faces"][js]["recipe"].split("-> ")[1].strip()
    st = 2 if side == "ours" else 3
    b = blob(st, md)
    write(md, b)
    receipt["faces"][md] = {"recipe": f"twin byte-copy follows json ({side})",
                            "sha16": hashlib.sha256(b.encode()).hexdigest()[:16]}

# compute_audit/regime_state: state=ts-newer side + row-union zero-loss
for p, keys in [("results/compute_audit.json", ["history"]),
                ("results/regime_state.json", ["history", "transitions", "triggers"])]:
    jo, jt = json.loads(blob(2, p)), json.loads(blob(3, p))
    to, tt = face_ts(jo), face_ts(jt)
    base, base_side = (jo, "ours") if (to or "") >= (tt or "") else (jt, "theirs")
    other = jt if base_side == "ours" else jo
    for k in keys:
        vb, vo = base.get(k) or [], other.get(k) or []
        seen, un = set(), []
        for row in vb + vo:
            sig = json.dumps(row, ensure_ascii=False, sort_keys=True)
            if sig not in seen:
                seen.add(sig); un.append(row)
        receipt["faces"][f"{p}::{k}"] = {"base": base_side, "ours_rows": len(vo) if base_side=="theirs" else len(vb),
                                         "other_rows": len(vo) if base_side=="ours" else len(vb), "union_rows": len(un)}
        base[k] = un
    out = json.dumps(base, ensure_ascii=False, indent=1) + "\n"
    write(p, out)
    receipt["faces"][p] = {"recipe": f"{base_side} state (ts-newer) + row-union zero-loss",
                           "sha16": hashlib.sha256(out.encode()).hexdigest()[:16]}

# token_usage: theirs-or-ours base by ts + per-key numeric max-union overlay (direction-agnostic, r781 recipe)
o, t = json.loads(blob(2, "results/token_usage.json")), json.loads(blob(3, "results/token_usage.json"))
def overlay(newer, older):
    out = dict(newer)
    for k, v in older.items():
        if k not in out:
            out[k] = v
        elif isinstance(v, (int, float)) and isinstance(out[k], (int, float)) and not isinstance(v, bool) and not isinstance(out[k], bool):
            out[k] = max(out[k], v)
        elif isinstance(v, dict) and isinstance(out[k], dict):
            out[k] = overlay(out[k], v)
    return out
merged = overlay(o, t)
out = json.dumps(merged, ensure_ascii=False, indent=1) + "\n"
write("results/token_usage.json", out)
receipt["faces"]["results/token_usage.json"] = {"recipe": "ours base + per-key numeric max-union overlay (r781 direction-agnostic)",
                                                "sha16": hashlib.sha256(out.encode()).hexdigest()[:16]}

with open("results/_r801bmb_merge_resolve3.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
for k, v in receipt["faces"].items():
    print(k, v.get("recipe", ""), v.get("ours_ts", ""), v.get("theirs_ts", ""))
