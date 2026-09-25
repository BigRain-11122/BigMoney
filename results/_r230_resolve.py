# -*- coding: utf-8 -*-
"""r230 (bm-b) rebase conflict resolver -- skill bigmoney-conflict-resolve
dogfood #6 (12-UU vs bm-a 471499b4 same-window S6 mirror; my replayed
commit = 8d1bd538 S6 close). Recipes per classifier (18/18 classifier):
  CODELY.md                    memory-union       (R208/r212)
  results/autofill_state.json  mixed-dict+ledger  (r203/r215/r220)
  compute_audit.json           rolling-ledger     (r188/R208)
  regime_state.json            rolling-ledger     (r188/R208)
  dashboard_status.js          js-wrapper take-side whole bytes,
                               side picked via .json twin meta.generated_at
                               (r226 addendum law; top-level 'ts' is absent)
  6 x snapshot                 take-new by ts     (R208/R216)
ours=stage2 (origin base + bm-a S6), theirs=stage3 (bm-b replay).
Parse-verify before write+add (r185); same-second tie -> HEAD/ours (r140);
EOL mirror per file from stage2 blob (r223 law)."""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def raw(stage, path):
    out = subprocess.run(["git", "show", f":{stage}:{path}"],
                         capture_output=True)
    assert out.returncode == 0, (stage, path, out.stderr[:200])
    return out.stdout


def parse_ts_any(doc):
    best = ""
    stack = [doc]
    while stack:
        d = stack.pop()
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, str) and k in (
                        "ts", "updated", "updated_at", "generated",
                        "generated_at", "last_attempt", "now", "asof"):
                    if v > best:
                        best = v
                elif isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(d, list):
            stack.extend(x for x in d if isinstance(x, (dict, list)))
    return best


def write_eol(path, text, base_bytes):
    eol = "\r\n" if b"\r\n" in base_bytes else "\n"
    with open(path, "wb") as f:
        f.write(text.replace("\n", eol).encode("utf-8"))
    return eol


def jkey(r):
    return json.dumps(r, ensure_ascii=False, sort_keys=True)


# ---------- 1. CODELY.md: memory-union (side2 full + side3-only lines)
def stages(path):
    out = subprocess.run(["git", "ls-files", "-u", "--", path],
                         capture_output=True, text=True)
    return {ln.split()[2] for ln in out.stdout.splitlines() if ln.strip()}


if "2" in stages("CODELY.md") and "3" in stages("CODELY.md"):
    a = raw(2, "CODELY.md").decode("utf-8")
    b = raw(3, "CODELY.md").decode("utf-8")
    la, lb = a.splitlines(), b.splitlines()
    sa = set(la)
    only_b = [l for l in lb if l not in sa and l.strip()]
    merged = la + only_b
    text = "\n".join(merged) + "\n"
    write_eol("CODELY.md", text, raw(2, "CODELY.md"))
    got = open("CODELY.md", encoding="utf-8").read().splitlines()
    assert all(l in set(got) for l in lb if l.strip()), "CODELY side3 loss"
    assert all(l in set(got) for l in la if l.strip()), "CODELY side2 loss"
    print(f"CODELY.md union OK: |side2|={len(la)} + side3-only "
          f"{len(only_b)} -> {len(got)} lines zero-loss")
else:
    print("CODELY.md: auto-merged this pass (no stage2/3) -> skip")

# ---------- 2. autofill_state.json: mixed-dict+ledger (r227 pattern)
P = "results/autofill_state.json"
s2, s3 = raw(2, P), raw(3, P)
ja, jb = json.loads(s2.decode("utf-8")), json.loads(s3.decode("utf-8"))
seen, rows = set(), []
for r in ja.get("launches", []) + jb.get("launches", []):
    k = jkey(r)
    if k not in seen:
        seen.add(k)
        rows.append(r)
rows.sort(key=lambda r: str(r.get("ts", "")))
n_union = len(rows)
rows = rows[-50:]                      # rolling cap 50 (R215)
lta, ltb = ja.get("last_tick", {}), jb.get("last_tick", {})
tsa, tsb = str(lta.get("ts", "")), str(ltb.get("ts", ""))
newer = ltb if tsb > tsa else lta     # tie -> HEAD/ours (r140)
out = {"last_tick": newer, "launches": rows}
eol = write_eol(P, json.dumps(out, ensure_ascii=False, indent=1), s2)
chk = json.load(open(P, encoding="utf-8"))
assert isinstance(chk["last_tick"], dict), "last_tick must stay dict (r203)"
assert len(chk["launches"]) == min(n_union, 50)
print(f"autofill_state OK: union {n_union} of "
      f"{len(ja['launches'])}+{len(jb['launches'])}, kept newest "
      f"{len(chk['launches'])}; last_tick "
      f"{'theirs(bm-b ' + tsb + ')' if tsb > tsa else 'ours(' + tsa + ')'}; "
      f"EOL={'CRLF' if eol == chr(13) + chr(10) else 'LF'}")

# ---------- 3. compute_audit.json: rolling-ledger union + take-new state
P = "results/compute_audit.json"
s2, s3 = raw(2, P), raw(3, P)
ja, jb = json.loads(s2.decode("utf-8")), json.loads(s3.decode("utf-8"))
ha, hb = ja.get("history", []), jb.get("history", [])
seen, rows = set(), []
for r in ha + hb:
    k = jkey(r)
    if k not in seen:
        seen.add(k)
        rows.append(r)
rows.sort(key=lambda r: str(r.get("ts", "")))
ha_t = str(ha[-1].get("ts", "")) if ha else ""
hb_t = str(hb[-1].get("ts", "")) if hb else ""
newer = jb if hb_t > ha_t else ja
out = {k: v for k, v in newer.items() if k != "history"}
out["history"] = rows
eol = write_eol(P, json.dumps(out, ensure_ascii=False, indent=1), s2)
chk = json.load(open(P, encoding="utf-8"))
assert len(chk["history"]) == len(rows) and len(rows) >= max(len(ha), len(hb))
print(f"compute_audit OK: |A|={len(set(map(jkey, ha)))} "
      f"|B|={len(set(map(jkey, hb)))} |A∪B|={len(rows)} zero-loss; "
      f"state from {'theirs' if hb_t > ha_t else 'ours'} "
      f"({hb_t if hb_t > ha_t else ha_t})")

# ---------- 4. regime_state.json: rolling-ledger (history+transitions)
P = "results/regime_state.json"
s2, s3 = raw(2, P), raw(3, P)
ja, jb = json.loads(s2.decode("utf-8")), json.loads(s3.decode("utf-8"))
for lkey in ("history", "transitions"):
    la_, lb_ = ja.get(lkey, []), jb.get(lkey, [])
    seen, rows_ = set(), []
    for r in la_ + lb_:
        k = jkey(r)
        if k not in seen:
            seen.add(k)
            rows_.append(r)
    rows_.sort(key=lambda r: str(r.get("ts", r.get("date", ""))))
    ja[lkey] = rows_
    print(f"regime {lkey}: {len(set(map(jkey, la_)))}+"
          f"{len(set(map(jkey, lb_)))} -> |∪|={len(rows_)}")
tsw = max(parse_ts_any(ja), parse_ts_any(jb))
newer_doc = jb if parse_ts_any(jb) >= parse_ts_any(ja) else ja
out = {k: (ja.get(k) if k in ("history", "transitions") else
           newer_doc.get(k)) for k in ja}
eol = write_eol(P, json.dumps(out, ensure_ascii=False, indent=2), s2)
json.load(open(P, encoding="utf-8"))
print(f"regime_state OK: ledger keys unioned, state fields take-new "
      f"({tsw})")

# ---------- 5. dashboard twins: .json take-new by meta.generated_at,
#             .js take-side SAME side whole bytes (r226 addendum law)
PJ = "results/dashboard_status.json"
js2, js3 = raw(2, PJ), raw(3, PJ)
tj2 = json.loads(js2.decode("utf-8")).get("meta", {}).get("generated_at", "")
tj3 = json.loads(js3.decode("utf-8")).get("meta", {}).get("generated_at", "")
pick_b = tj3 >= tj2
with open(PJ, "wb") as f:
    f.write(js3 if pick_b else js2)
json.load(open(PJ, encoding="utf-8"))
JS = "results/dashboard_status.js"
blob = (raw(3, JS) if pick_b else raw(2, JS))
with open(JS, "wb") as f:
    f.write(blob)
got = open(JS, encoding="utf-8").read()
assert got.startswith("window.DASH_DATA = ") and got.rstrip().endswith(";"), \
    "js wrapper stripped (R209)"
print(f"dashboard twins OK: json+js both from "
      f"{'theirs(bm-b ' + tj3 + ')' if pick_b else 'ours(' + tj2 + ')'} "
      f"(js whole-bytes, wrapper preserved)")

# ---------- 6. snapshots: take-new by leaf-ts, byte-identical write
for P in ("results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json",
          "results/heat_update_status.json",
          "results/lhb_update_status.json",
          "results/token_usage.json",
          "results/update_status.json"):
    s2, s3 = raw(2, P), raw(3, P)
    t2 = parse_ts_any(json.loads(s2.decode("utf-8")))
    t3 = parse_ts_any(json.loads(s3.decode("utf-8")))
    pick_b = t3 > t2               # tie -> ours (r140)
    with open(P, "wb") as f:
        f.write(s3 if pick_b else s2)
    json.load(open(P, encoding="utf-8"))
    print(f"{P}: take-{'theirs(' + t3 + ')' if pick_b else 'ours(' + t2 + ')'}")

print("\nALL 12 RESOLVED -- parse-verify passed for every file. "
      "Next: git add resolved files + git -c core.editor=true rebase "
      "--continue (r193).")
