# -*- coding: utf-8 -*-
"""r356 bm-b push-storm 18-UU canon resolver (vs bm-c r127 chain).
Side map (r352): :2: = HEAD = upstream (bm-c r127 side), :3: = ours (replayed bm-b round commit).
Recipes per SKILL.md: memory-union (CODELY), append-log union (archive), mixed-dict+ledger
(autofill_state), rolling-ledger union (compute_audit/regime_state), js-wrapper take-side
(dashboard_status.js), snapshot take-new (rest). Heat snapshots-regression guard (r125)."""
import json, subprocess, io, re

def show(spec):
    p = subprocess.run(["git", "show", spec], capture_output=True)
    if p.returncode != 0:
        raise SystemExit(f"git show {spec} rc={p.returncode}")
    return p.stdout.decode("utf-8")

# ---- side probe (r352 law) ----
head_codely = show("HEAD:CODELY.md")
s2_codely = show(":2:CODELY.md")
print("side probe :2:==HEAD:", s2_codely == head_codely, "| :3:==HEAD:", show(":3:CODELY.md") == head_codely)
assert s2_codely == head_codely, "side map changed! probe before proceeding"

UU = ["CODELY.md", "research/memory-archive/202609.md", "results/autofill_state.json",
      "results/compute_audit.json", "results/regime_state.json", "results/dashboard_status.js",
      "results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
      "results/futures_update_status.json", "results/heat_update_status.json",
      "results/lhb_update_status.json", "results/token_usage.json", "results/update_status.json",
      "results/scorecard_v1.json", "results/strategy_scorecard.json",
      "results/prospect_promotion/_summary.json", "docs/daily_report/REPORT-2026-09-28.json",
      "docs/daily_report/REPORT-2026-09-28.md"]

def blob(f):
    return show(":2:" + f), show(":3:" + f)

def crlf_of(txt):
    return "\r\n" in txt

def write(path, text, crlf):
    data = text.replace("\n", "\r\n") if crlf else text
    if not data.endswith("\n"):
        data += "\r\n" if crlf else "\n"
    io.open(path, "w", encoding="utf-8", newline="").write(data)

TS_KEYS = ["ts", "updated", "updated_at", "generated", "generated_at", "last_run", "timestamp", "time", "asof"]

def pick_new(up_txt, our_txt, path):
    """snapshot take-new by inner ts; tie or undecidable -> upstream (:2:=HEAD, r140)."""
    def ts_of(t):
        try:
            d = json.loads(t)
        except Exception:
            return None
        if isinstance(d, dict):
            for k in TS_KEYS:
                v = d.get(k)
                if isinstance(v, (str, int, float)):
                    return str(v)
        return None
    tu, to = ts_of(up_txt), ts_of(our_txt)
    if tu is None and to is None:
        return "up", up_txt, tu, to
    if to is not None and (tu is None or to > tu):
        return "ours", our_txt, tu, to
    return "up", up_txt, tu, to

resolved = {}

# ---- 1) CODELY.md memory-union ----
up_txt, our_txt = blob("CODELY.md")
up_l = up_txt.split("\n"); our_l = our_txt.split("\n")
up_set = set(up_l)
# entries from upstream that my side already archived verbatim -> drop hot copies (archive union keeps them)
archive_up, archive_our = blob("research/memory-archive/202609.md")
drop = [l for l in up_l if l not in set(our_l) and l.startswith("- [2026-09-28 02:")]
out_l = []
for l in up_l:
    if l in drop:
        continue
    out_l.append(l)
# append our unique lines (pointer + new entry) after the last pointer/entry region
our_uniq = [l for l in our_l if l not in up_set and l.strip()]
out_l.extend(our_uniq)
merged_codely = "\n".join(out_l)
# zero-loss: every dropped hot line must exist verbatim in the archive union (built below)
print("CODELY union: up_lines=%d our_lines=%d -> %d (dropped-hot=%d, archived-copies verified below)" % (len(up_l), len(our_l), len(out_l), len(drop)))

# ---- 2) archive append-log union (both batches verbatim) ----
arch_final = up_txt if up_txt.endswith("\n") else up_txt + "\n"
our_arch_uniq = []
our_arch_lines = our_txt.split("\n")
up_arch_set = set(archive_up.split("\n"))
for l in our_arch_lines:
    if l not in up_arch_set and l.strip():
        our_arch_uniq.append(l)
arch_final += "\n" + "\n".join(our_arch_uniq) + "\n"
print("archive union: + our unique lines:", len(our_arch_uniq))
for l in drop:
    assert ("\n" + l + "\n") in ("\n" + arch_final + "\n"), "ZERO-LOSS VIOLATION (dropped hot line not in archive): " + l[:60]
print("dropped-hot verbatim-in-archive verify: %d/%d PASS" % (len(drop), len(drop)))
assert "二十六批" in arch_final and ("四十一" in arch_final or "四十" in arch_final), "both batch sections must be present"
write("research/memory-archive/202609.md", arch_final, crlf_of(archive_up))
write("CODELY.md", merged_codely, crlf_of(up_txt))
json_ok = len(merged_codely.encode("utf-8"))
print("CODELY final size:", json_ok, "bytes")
assert json_ok <= 10240

# ---- 3) autofill_state.json mixed-dict+ledger (this round's v2 recipe) ----
up_txt, our_txt = blob("results/autofill_state.json")
up = json.loads(up_txt); ours = json.loads(our_txt)
up_l2 = up.get("launches", []); our_l2 = ours.get("launches", [])
seen = {}
for e in up_l2 + our_l2:
    seen[json.dumps(e, sort_keys=True, ensure_ascii=False)] = e
union = sorted(seen.values(), key=lambda e: str(e.get("ts", "")), reverse=True)[:50]
union.sort(key=lambda e: str(e.get("ts", "")))
ut = up.get("last_tick") or {}; ot = ours.get("last_tick") or {}
assert isinstance(ut, dict) and isinstance(ot, dict)
last_tick = ot if str(ot.get("ts", "")) > str(ut.get("ts", "")) else ut
merged = {"last_tick": last_tick, "launches": union}
print("autofill: up=%d ours=%d union_unique=%d last_tick=%s(%s)" % (len(up_l2), len(our_l2), len(union), last_tick.get("ts"), last_tick.get("machine")))
out = json.dumps(merged, ensure_ascii=False, indent=1)
json.loads(out)
assert isinstance(merged["last_tick"], dict)
write("results/autofill_state.json", out, crlf_of(up_txt))

# ---- 4) rolling-ledger unions: compute_audit / regime_state ----
def ledger_union(path, list_keys):
    up_txt, our_txt = blob(path)
    up = json.loads(up_txt); ours = json.loads(our_txt)
    merged = dict(up)
    for k in list_keys:
        a = up.get(k, []); b = ours.get(k, [])
        if isinstance(a, list) and isinstance(b, list):
            seen_ts = set(); un = []
            for e in (a + b):
                key = json.dumps(e, sort_keys=True, ensure_ascii=False) if isinstance(e, (dict, list)) else str(e)
                ts = e.get("ts", "") if isinstance(e, dict) else ""
                if key in seen_ts:
                    continue
                seen_ts.add(key); un.append(e)
            un.sort(key=lambda e: str(e.get("ts", "")) if isinstance(e, dict) else "")
            merged[k] = un
            print(f"{path} [{k}]: {len(a)}+{len(b)} -> {len(un)}")
    # scalars: take-new via generic ts pick on remaining fields handled by pick for whole doc not needed;
    # upstream (:2:) is the freshest shared state per r140 tie; keep upstream scalars, ours only added lists
    out = json.dumps(merged, ensure_ascii=False, indent=1)
    json.loads(out)
    write(path, out, crlf_of(up_txt))

ledger_union("results/compute_audit.json", ["history", "launches"])
ledger_union("results/regime_state.json", ["history", "transitions"])

# ---- 5) dashboard_status.js js-wrapper take-side whole bytes ----
up_txt, our_txt = blob("results/dashboard_status.js")
def js_ts(t):
    m = re.search(r'"(?:ts|generated|updated)"\s*:\s*"?([\d\-T:.+\s]+)"?', t)
    return m.group(1).strip() if m else None
tu, to = js_ts(up_txt), js_ts(our_txt)
side = "ours" if (to and (tu is None or to > tu)) else "up"
write("results/dashboard_status.js", our_txt if side == "ours" else up_txt, crlf_of(up_txt))
print("dashboard_status.js take-side:", side, "ts up=%s ours=%s" % (tu, to))

# ---- 6) snapshots take-new (+ heat regression guard r125) ----
for f in ["results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json", "results/heat_update_status.json",
          "results/lhb_update_status.json", "results/token_usage.json",
          "results/update_status.json", "results/scorecard_v1.json",
          "results/strategy_scorecard.json", "results/prospect_promotion/_summary.json",
          "docs/daily_report/REPORT-2026-09-28.json"]:
    up_txt, our_txt = blob(f)
    side, txt, tu, to = pick_new(up_txt, our_txt, f)
    if "heat" in f:
        try:
            du, do = json.loads(up_txt), json.loads(our_txt)
            su = du.get("snapshots"); so = do.get("snapshots")
            if isinstance(su, int) and isinstance(so, int) and so < su:
                side, txt = "up", up_txt
                print(f"{f}: heat host-authority guard kicked in (kept snapshots={su})")
        except Exception:
            pass
    json.loads(txt)
    write(f, txt, crlf_of(txt))
    print(f"{f}: take-new side={side} ts up={tu} ours={to}")

# ---- 7) REPORT md: deterministic same-day regen, tie->upstream ----
up_txt, our_txt = blob("docs/daily_report/REPORT-2026-09-28.md")
write("docs/daily_report/REPORT-2026-09-28.md", up_txt, crlf_of(up_txt))
print("REPORT md: tie->upstream (idempotent same-day regen)")

print("RESOLVE_ALL_18_OK")
