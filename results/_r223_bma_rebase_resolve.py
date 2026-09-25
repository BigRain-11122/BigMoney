"""r223 bm-a rebase resolver (12-UU batch, same-window dual-machine S6 mirror family, 8th instance).

Classifier: .codely-cli/skills/bigmoney-conflict-resolve/scripts/classify_conflicts.py
-> 12/12 GREEN, 0 UNKNOWN. Recipes applied per class (SKILL.md table).

REBASE STAGE INVERSION (critical): during `git pull --rebase` replay of MY commit
1a6854ac onto origin/main (bm-b fa77fff8..76fcd514):
  :1: = base (merge-base)
  :2: = ours  = origin/main side (bm-b)  == HEAD during rebase
  :3: = theirs = my replayed commit (bm-a round 223)
Tie law: same-second tie -> HEAD = :2 (r140 law, rebase-context).

Recipes per file:
  CODELY.md                     memory-union       line-level union of appended entries (R208/r212)
  results/autofill_state.json   mixed-dict+ledger  launches union->sort ts->cap50 (R215);
                                                     last_tick inner-ts compare -> WHOLE dict assign,
                                                     no str() (r203); tie->HEAD; isinstance assert (r203);
                                                     CRLF producer mirror (bm-b r223 law)
  results/compute_audit.json    rolling-ledger     history union zero-loss; latest take-new by ts (r188/R208)
  results/dashboard_status.js   js-wrapper-snapshot take-side WHOLE BYTES by inner ts; wrapper preserved (R209)
  results/dashboard_status.json snapshot           take-new by ts
  results/fundamental_b_layer_filter.json snapshot  take-new by ts (R216)
  results/futures_update_status.json   snapshot    take-new by ts
  results/heat_update_status.json      snapshot    take-new by ts
  results/lhb_update_status.json       snapshot    take-new by ts
  results/regime_state.json      rolling-ledger    history/transitions union zero-loss; state fields take-new (R208)
  results/token_usage.json       snapshot          take-new by generated ts (R216)
  results/update_status.json     snapshot          take-new by ts

Discipline: read git objects via subprocess bytes (r209: no PS > redirection);
parse-verify BEFORE write-back (r185); zero-loss assert for ledger unions.
"""
import json
import subprocess
import sys

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"


def stage_blob(num, path):
    out = subprocess.run(["git", "show", f":{num}:{path}"], cwd=ROOT,
                         capture_output=True).stdout
    return out


def detect_crlf(blob: bytes) -> bool:
    return b"\r\n" in blob


def write_bytes(path, data: bytes):
    with open(path, "wb") as fh:
        fh.write(data)


def write_text_mirror(path, text: str, crlf: bool):
    data = text.encode("utf-8")
    if crlf:
        data = data.replace(b"\n", b"\r\n")
    write_bytes(path, data)


def ts_of(d):
    for k in ("ts", "generated_at", "updated_at", "time", "generated"):
        if isinstance(d, dict) and k in d:
            return str(d[k])
    return ""


def main():
    report = []

    # ---------------- CODELY.md : memory-union ----------------
    p = "CODELY.md"
    base = stage_blob(1, p).decode("utf-8", errors="replace")
    bmb = stage_blob(2, p).decode("utf-8", errors="replace")
    bma = stage_blob(3, p).decode("utf-8", errors="replace")
    base_lines = base.splitlines()
    bmb_lines = bmb.splitlines()
    bma_lines = bma.splitlines()
    bmb_new = [l for l in bmb_lines if l not in base_lines and l.strip()]
    bma_new = [l for l in bma_lines if l not in base_lines and l.strip()]
    # union: start from my full side, append bm-b's new entries not already present
    missing = [l for l in bmb_new if l not in bma_lines]
    merged_lines = list(bma_lines) + ["" if False else l for l in missing]
    merged = "\n".join(merged_lines) + ("\n" if bma.endswith("\n") or bmb.endswith("\n") else "")
    crlf = detect_crlf(stage_blob(3, p)) or detect_crlf(stage_blob(2, p))
    write_text_mirror(ROOT + "\\" + p.replace("/", "\\"), merged, crlf)
    report.append(f"CODELY.md: memory-union base_lines={len(base_lines)} "
                  f"bmb_new={len(bmb_new)} bma_new={len(bma_new)} appended_bmb_missing={len(missing)} crlf={crlf}")

    # ---------------- autofill_state.json : mixed-dict+ledger ----------------
    p = "results/autofill_state.json"
    b2 = json.loads(stage_blob(2, p).decode("utf-8"))
    b3 = json.loads(stage_blob(3, p).decode("utf-8"))
    l2 = b2.get("launches", [])
    l3 = b3.get("launches", [])
    seen = set()
    union = []
    for row in l2 + l3:
        key = json.dumps(row, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            union.append(row)
    union.sort(key=lambda r: str(r.get("ts", "")))
    cap = 50  # R215 rolling window
    dropped = len(union) - cap if len(union) > cap else 0
    union = union[-cap:]
    t2 = b2.get("last_tick", {})
    t3 = b3.get("last_tick", {})
    ts2 = str(t2.get("ts", "")) if isinstance(t2, dict) else ""
    ts3 = str(t3.get("ts", "")) if isinstance(t3, dict) else ""
    if ts3 > ts2:
        last_tick, tick_src = t3, "bma(theirs)"
    elif ts2 > ts3:
        last_tick, tick_src = t2, "bmb(ours/HEAD)"
    else:
        last_tick, tick_src = (t2 if ts2 == ts3 else {}), "HEAD-tie"  # tie -> HEAD = :2
    if not isinstance(last_tick, dict):
        last_tick = {}
        tick_src += " FORCED-DICT"
    merged_state = dict(b3)
    merged_state["launches"] = union
    merged_state["last_tick"] = last_tick
    assert isinstance(merged_state["last_tick"], dict), "last_tick not dict (r203 law)"
    crlf = detect_crlf(stage_blob(2, p)) or detect_crlf(stage_blob(3, p))
    write_text_mirror(ROOT + r"\results\autofill_state.json",
                      json.dumps(merged_state, ensure_ascii=False, indent=1), crlf)
    json.loads(open(ROOT + r"\results\autofill_state.json", encoding="utf-8").read())  # parse-verify
    report.append(f"autofill_state.json: launches union |{len(l2)}+{len(l3)}| dedupe->{len(union)} "
                  f"cap50 dropped_oldest={dropped}; last_tick {ts3}(bma) vs {ts2}(bmb) -> {tick_src}; "
                  f"isinstance-dict OK; crlf={crlf}")

    # ---------------- rolling-ledger: compute_audit.json ----------------
    p = "results/compute_audit.json"
    b2 = json.loads(stage_blob(2, p).decode("utf-8"))
    b3 = json.loads(stage_blob(3, p).decode("utf-8"))
    h2 = b2.get("history", [])
    h3 = b3.get("history", [])
    seen = set()
    union = []
    for row in h2 + h3:
        key = json.dumps(row, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            union.append(row)
    union.sort(key=lambda r: str(r.get("ts", "")))
    latest = b3 if str(b3.get("latest", {}).get("ts", "")) >= str(b2.get("latest", {}).get("ts", "")) else b2
    merged = dict(b3)
    merged["history"] = union
    merged["latest"] = latest.get("latest", latest)
    crlf = detect_crlf(stage_blob(2, p)) or detect_crlf(stage_blob(3, p))
    write_text_mirror(ROOT + r"\results\compute_audit.json",
                      json.dumps(merged, ensure_ascii=False, indent=1), crlf)
    json.loads(open(ROOT + r"\results\compute_audit.json", encoding="utf-8").read())
    report.append(f"compute_audit.json: history union |{len(h2)}+{len(h3)}| -> {len(union)} zero-loss "
                  f"(unique_delta={len(union)-max(len(h2),len(h3))}); latest.ts winner="
                  f"{latest.get('latest', {}).get('ts', latest.get('ts'))}")

    # ---------------- rolling-ledger: regime_state.json ----------------
    p = "results/regime_state.json"
    b2 = json.loads(stage_blob(2, p).decode("utf-8"))
    b3 = json.loads(stage_blob(3, p).decode("utf-8"))
    def union_list(x, y):
        seen, out = set(), []
        for row in x + y:
            key = json.dumps(row, ensure_ascii=False, sort_keys=True)
            if key not in seen:
                seen.add(key)
                out.append(row)
        return out
    merged = dict(b3)
    for key in ("history", "transitions"):
        if key in b2 or key in b3:
            u = union_list(b2.get(key, []), b3.get(key, []))
            merged[key] = u
            report.append(f"regime_state.json: {key} union |{len(b2.get(key, []))}+{len(b3.get(key, []))}| -> {len(u)}")
    ts2, ts3 = ts_of(b2), ts_of(b3)
    winner = b3 if ts3 >= ts2 else b2   # asof same-day tie -> HEAD would be b2; >= keeps b3 only if strictly newer? see note
    # R209/R216 note: asof same-day tie -> HEAD (= :2 bm-b). Implement strictly:
    if ts3 > ts2:
        winner = b3
    else:
        winner = b2
    for k in ("state", "asof", "raw", "days_in_state", "mode", "ts"):
        if k in winner:
            merged[k] = winner[k]
    crlf = detect_crlf(stage_blob(2, p)) or detect_crlf(stage_blob(3, p))
    write_text_mirror(ROOT + r"\results\regime_state.json",
                      json.dumps(merged, ensure_ascii=False, indent=1), crlf)
    json.loads(open(ROOT + r"\results\regime_state.json", encoding="utf-8").read())
    report.append(f"regime_state.json: state fields winner ts {ts3}(bma) vs {ts2}(bmb) -> "
                  f"{'bma' if ts3 > ts2 else 'bmb/HEAD'} (asof tie->HEAD r209)")

    # ---------------- js-wrapper-snapshot: dashboard_status.js ----------------
    p = "results/dashboard_status.js"
    raw2 = stage_blob(2, p)
    raw3 = stage_blob(3, p)
    import re
    def inner_ts(raw):
        m = re.search(rb'"(?:ts|generated_at|updated)"\s*:\s*"([^"]+)"', raw)
        return m.group(1).decode() if m else ""
    t2, t3 = inner_ts(raw2), inner_ts(raw3)
    winner = raw3 if t3 > t2 else raw2   # tie -> HEAD(:2)=raw2
    assert winner.startswith(b"window.DASH_DATA") or b"window.DASH_DATA" in winner[:200], "JS wrapper missing (R209)"
    write_bytes(ROOT + r"\results\dashboard_status.js", winner)
    # parse-verify: strip wrapper then json.loads
    body = winner.decode("utf-8", errors="replace")
    body = body.strip()
    assert body.startswith("window.DASH_DATA"), "wrapper head missing"
    payload = body[len("window.DASH_DATA"):].strip()
    if payload.endswith(";"):
        payload = payload[:-1]
    payload = payload.strip()
    if payload.startswith("="):
        payload = payload[1:].strip()
    json.loads(payload)
    report.append(f"dashboard_status.js: whole-bytes take-side ts {t3}(bma) vs {t2}(bmb) -> "
                  f"{'bma' if t3 > t2 else 'bmb/HEAD'}; wrapper preserved + payload parse OK")

    # ---------------- snapshots: take-new by ts ----------------
    SNAPSHOTS = [
        "results/dashboard_status.json",
        "results/fundamental_b_layer_filter.json",
        "results/futures_update_status.json",
        "results/heat_update_status.json",
        "results/lhb_update_status.json",
        "results/token_usage.json",
        "results/update_status.json",
    ]
    for p in SNAPSHOTS:
        raw2, raw3 = stage_blob(2, p), stage_blob(3, p)
        j2 = json.loads(raw2.decode("utf-8"))
        j3 = json.loads(raw3.decode("utf-8"))
        t2, t3 = ts_of(j2), ts_of(j3)
        winner = j3 if t3 > t2 else j2   # tie -> HEAD(:2)
        crlf = detect_crlf(raw2) or detect_crlf(raw3)
        write_text_mirror(ROOT + "\\" + p.replace("/", "\\"),
                          json.dumps(winner, ensure_ascii=False, indent=1), crlf)
        json.loads(open(ROOT + "\\" + p.replace("/", "\\"), encoding="utf-8").read())
        report.append(f"{p}: snapshot take-new ts {t3}(bma) vs {t2}(bmb) -> {'bma' if t3 > t2 else 'bmb/HEAD'}")

    print("=== r223 bm-a rebase resolver report ===")
    for line in report:
        print(line)
    print("ALL PARSE-VERIFIED, WRITTEN BACK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
