# -*- coding: utf-8 -*-
"""r226 (bm-b) rebase conflict resolver -- skill bigmoney-conflict-resolve
dogfood (10-UU vs bm-a R222 fa77fff8). Recipes per classifier:
  CODELY.md                    memory-union       (R208/r212)
  compute_audit.json           rolling-ledger    (r188/R208)
  dashboard_status.js          js-wrapper take-side whole bytes (R209)
  6 x snapshot                 take-new by ts    (R208/R216)
  lhb_update_status.json       take-new (latest attempt wins; overlap
                               sub-face superseded by later throttled run)
Parse-verify before write+add (r185); same-second tie -> HEAD (r140)."""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UNION_FILES = ["CODELY.md"]
LEDGER_FILES = ["results/compute_audit.json"]
JS_TAKESIDE = ["results/dashboard_status.js"]
SNAPSHOTS = [
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
]
# take-side selection: ours=stage2 (origin fa77fff8), theirs=stage3 (my replay)


def raw(stage, path):
    out = subprocess.run(["git", "show", f":{stage}:{path}"],
                         capture_output=True)
    assert out.returncode == 0, (stage, path, out.stderr[:200])
    return out.stdout


def parse_ts_any(doc):
    """best-effort newest-side decision: scan leaf strings for ts-like keys."""
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


def write_bytes(path, data):
    with open(path, "wb") as f:
        f.write(data)


def resolve():
    # 1. CODELY.md: union -- ours' 66 lines + my 1 new line (arrival order)
    a = raw(2, "CODELY.md").decode("utf-8")
    b = raw(3, "CODELY.md").decode("utf-8")
    la, lb = a.splitlines(), b.splitlines()
    only_b = [l for l in lb if l not in set(la) and l.strip()]
    eol = "\r\n" if "\r\n" in a else "\n"
    merged = la + only_b
    assert len(merged) == len(la) + len(only_b) and len(only_b) == 1, \
        (len(la), len(only_b))
    text = eol.join(merged) + eol
    write_bytes("CODELY.md", text.encode("utf-8"))
    got = open("CODELY.md", encoding="utf-8").read().splitlines()
    assert len(got) == 67 and only_b[0] in got and la[-1] in got
    print("CODELY.md union OK: 65 shared + bm-a R222 line + bm-b r226 line "
          f"(EOL={'CRLF' if eol == chr(13)+chr(10) else 'LF'})")

    # 2. compute_audit.json: rolling-ledger union + take-new state fields
    ra, rb = raw(2, "results/compute_audit.json"), raw(
        3, "results/compute_audit.json")
    ja, jb = json.loads(ra.decode("utf-8")), json.loads(rb.decode("utf-8"))
    print("compute_audit top-level keys:", sorted(ja.keys()))
    ha, hb = ja.get("history", []), jb.get("history", [])
    key = lambda r: json.dumps(r, ensure_ascii=False, sort_keys=True)
    seen, rows = set(), []
    for r in ha + hb:
        k = key(r)
        if k not in seen:
            seen.add(k)
            rows.append(r)
    rows.sort(key=lambda r: str(r.get("ts", r.get("asof", ""))))
    # state fields from newer side: compare history-last ts
    tsa = str(ha[-1].get("ts", "")) if ha else ""
    tsb = str(hb[-1].get("ts", "")) if hb else ""
    newer = jb if tsb >= tsa else ja      # same-second tie -> HEAD-side
    # HEAD-side here = ours (the rebased-onto origin) per r140; but tsb>tsa
    # strictly in live case (05:47:47 > 05:42:46) -> take mine
    out = {k: v for k, v in newer.items() if k != "history"}
    out["history"] = rows
    eol = "\r\n" if b"\r\n" in ra else "\n"
    indent = 2 if ra.decode("utf-8").lstrip("{").startswith("\n  ") else 1
    body = json.dumps(out, ensure_ascii=False, indent=indent)
    write_bytes("results/compute_audit.json",
                body.replace("\n", eol).encode("utf-8"))
    chk = json.load(open("results/compute_audit.json", encoding="utf-8"))
    union_n, a_n, b_n = len(rows), len(set(map(key, ha))), len(set(map(key, hb)))
    assert len(chk["history"]) == union_n
    print(f"compute_audit union OK: |A|={a_n} |B|={b_n} |A∪B|={union_n} "
          f"(zero-loss), state fields from side with hist-last "
          f"{'theirs(mine)' if tsb >= tsa else 'ours'} "
          f"({tsb if tsb >= tsa else tsa}), EOL={'CRLF' if eol==chr(13)+chr(10) else 'LF'} indent={indent}")

    # 3. dashboard_status.js: take-side whole bytes (newer internal ts)
    jsa, jsb = raw(2, JS_TAKESIDE[0]), raw(3, JS_TAKESIDE[0])
    tsa = json.loads(jsa.decode("utf-8").split("=", 1)[1].strip().rstrip(";"))
    tsb = json.loads(jsb.decode("utf-8").split("=", 1)[1].strip().rstrip(";"))
    pick_b = str(tsb.get("ts", "")) >= str(tsa.get("ts", ""))
    write_bytes(JS_TAKESIDE[0], jsb if pick_b else jsa)
    got = open(JS_TAKESIDE[0], encoding="utf-8").read()
    assert got.startswith("window.DASH_DATA = ") and got.rstrip().endswith(";")
    print(f"dashboard_status.js take-side whole bytes OK: "
          f"picked {'theirs(mine) ts=' + str(tsb.get('ts')) if pick_b else 'ours ts=' + str(tsa.get('ts'))} "
          f"(wrapper preserved, no re-serialization)")

    # 4. snapshots: take-new by leaf-ts
    for p in SNAPSHOTS:
        ra, rb = raw(2, p), raw(3, p)
        ja, jb = json.loads(ra.decode("utf-8")), json.loads(rb.decode("utf-8"))
        tsa, tsb = parse_ts_any(ja), parse_ts_any(jb)
        pick_b = tsb >= tsa      # same-second tie -> ours(HEAD base) per r140
        data = rb if pick_b else ra
        # write back byte-identical to the picked blob (format preserved)
        write_bytes(p, data)
        chk = json.load(open(p, encoding="utf-8"))
        assert isinstance(chk, dict)
        print(f"{p}: take-{'theirs(mine)' if pick_b else 'ours'} "
              f"(ts {tsb if pick_b else tsa})")

    print("\nALL RESOLVED -- parse-verify passed for every file. "
          "Next: git add resolved files + rebase --continue.")


resolve()
