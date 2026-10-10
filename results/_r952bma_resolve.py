# -*- coding: utf-8 -*-
"""r952 bm-a rebase storm resolver (per bigmoney-conflict-resolve skill).
Stage semantics during rebase: :2: = origin side (HEAD at replay base), :3: = my commit being replayed.
Recipes: queue md = manual union (T20 renumber-yield per fleet README S4, E8/E9 row + record union);
snapshots = deep-ts take-new (r311 deep-scan law); single-writer bm-a faces = take :3: (R216);
md twins byte-copy from winning json side (r329 twin coupling).
"""
import subprocess, json, os, re, sys, io

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"

def git_bytes(*args):
    r = subprocess.run([GIT] + list(args), capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} rc={r.returncode}: {r.stderr.decode('utf-8', 'replace')[:200]}")
    return r.stdout

def stage_blob(path, n):
    return git_bytes("show", f":{n}:{path}")

def wbytes(path, b):
    assert isinstance(b, bytes)
    with io.open(os.path.join(ROOT, path.replace("/", os.sep)), "wb") as f:
        f.write(b)

def jload(b):
    return json.loads(b.decode("utf-8"))

TS_KEYS = ("generated_at", "generated", "ts", "timestamp", "asof", "updated_at", "updated", "scanned_at", "last_run", "run_ts")

def deep_ts(obj):
    """Deep-scan for ts-like keys; returns max ISO/epoch-normalized string with path."""
    best = [None, None]
    def norm(s):
        s = str(s)
        if re.fullmatch(r"\d{10}", s):
            return "E:" + s
        if re.fullmatch(r"\d{13}", s):
            return "E:" + s[:-3]  # ms->s truncate for compare
        m = re.match(r"(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}(:\d{2})?)", s)
        if m:
            return "I:" + m.group(1) + "T" + m.group(2)
        return None
    def walk(o, p):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, (str, int, float)) and not isinstance(v, bool):
                    kl = str(k).lower()
                    if kl in TS_KEYS and norm(v) is not None:
                        nv = norm(v)
                        if best[0] is None or nv > best[0]:
                            best[0], best[1] = nv, p + "." + str(k)
                walk(v, p + "." + str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o[:200]):  # cap scan depth for huge ledgers
                walk(v, p + f"[{i}]")
    walk(obj, "$")
    return tuple(best)

log = []

def resolve_snapshot_pair(path_json, path_md):
    """REPORT/LIVE twin: probe generated ts in json stages, take newer side; md byte-copy same side. Tie -> :2: (r140)."""
    b2, b3 = stage_blob(path_json, 2), stage_blob(path_json, 3)
    t2, t3 = deep_ts(jload(b2)), deep_ts(jload(b3))
    if t3[0] is not None and (t2[0] is None or t3[0] > t2[0]):
        side, n = 3, ":3(mine)"
    else:
        side, n = 2, ":2(origin)"
    wbytes(path_json, stage_blob(path_json, side))
    wbytes(path_md, stage_blob(path_md, side))
    log.append(f"{path_json}: take {n} (ts2={t2} ts3={t3}) + md twin same side")

def resolve_take_new(path):
    b2, b3 = stage_blob(path, 2), stage_blob(path, 3)
    try:
        t2, t3 = deep_ts(jload(b2)), deep_ts(jload(b3))
    except Exception as e:
        log.append(f"{path}: parse-probe fail ({e}); fallback :2:")
        wbytes(path, b2); return
    if t3[0] is not None and (t2[0] is None or t3[0] > t2[0]):
        side, n = 3, ":3(mine)"
    else:
        side, n = 2, ":2(origin)"
    wbytes(path, stage_blob(path, side))
    log.append(f"{path}: take {n} (ts2={t2[0]} ts3={t3[0]})")

def resolve_take_mine(path):
    b3 = stage_blob(path, 3)
    if path.endswith(".json"):
        jload(b3)  # parse-verify
    if path.endswith(".js"):
        assert b"window.DASH_DATA" in b3, "js wrapper missing"
    wbytes(path, b3)
    log.append(f"{path}: take :3(mine) [single-writer host=bm-a lane, R216]")

def resolve_tech_md():
    p = "state/queue/tech.md"
    l2 = stage_blob(p, 2).decode("utf-8").splitlines(keepends=False)
    l3 = stage_blob(p, 3).decode("utf-8").splitlines(keepends=False)
    t20_2 = [x for x in l2 if x.startswith("| T20 |")]
    t20_3 = [x for x in l3 if x.startswith("| T20 |")]
    assert len(t20_2) == 1 and len(t20_3) == 1, f"tech T20 rows: {len(t20_2)}/{len(t20_3)}"
    my_row = t20_3[0]
    # renumber mine T20->T21 with yield note (bm-b r828 10:07:48 < mine 10:31:38 -> I yield, fleet README S4)
    note = "【原拟 T20·与 bm-b r828 T20 同窗撞号·后到让号 per fleet README §4（r952 bm-a 注记）】"
    assert my_row.count("|") >= 4
    parts = my_row.split("|")
    parts[1] = " T21 "
    parts[2] = parts[2].rstrip() + note
    new_row = "|".join(parts)
    out = []
    for x in l2:
        out.append(x)
        if x.startswith("| T20 |"):
            out.append(new_row)
    wbytes(p, ("\r\n".join(out) + "\r\n").encode("utf-8"))
    log.append(f"{p}: union both T20 rows; mine renumbered -> T21 (yield per S4)")

def resolve_explore_md():
    p = "state/queue/explore.md"
    l2 = stage_blob(p, 2).decode("utf-8").splitlines(keepends=False)
    l3 = stage_blob(p, 3).decode("utf-8").splitlines(keepends=False)
    e9_2 = [x for x in l2 if x.startswith("| E9 |")]
    e9_3 = [x for x in l3 if x.startswith("| E9 |")]
    r951_3 = [x for x in l3 if x.startswith("> r951 收口记录")]
    r828_2 = [x for x in l2 if x.startswith("> r828 消耗记录")]
    assert len(e9_2) == 1 and len(e9_3) == 1 and len(r951_3) == 1 and len(r828_2) == 1, \
        f"e9_2={len(e9_2)} e9_3={len(e9_3)} r951={len(r951_3)} r828={len(r828_2)}"
    out = []
    for x in l2:
        if x.startswith("| E9 |"):
            out.append(e9_3[0])  # my side: done (r951 completed E9)
        else:
            out.append(x)
        if x.startswith("> r828 消耗记录"):
            out.append(r951_3[0])  # append my r951 record after bm-b r828 (chronological)
    wbytes(p, ("\r\n".join(out) + "\r\n").encode("utf-8"))
    log.append(f"{p}: E8 done row kept (origin healed side); E9 row -> mine (done); r827 healed + r828 + r951 records union")

def main():
    # 1) twin-regen snapshots (json probe + md byte-copy same side)
    resolve_snapshot_pair("docs/daily_report/REPORT-2026-10-10.json", "docs/daily_report/REPORT-2026-10-10.md")
    for jm, mm in [("docs/live_usage/LIVE-2026-10-10.json", "docs/live_usage/LIVE-2026-10-10.md"),
                   ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md")]:
        # LIVE family: probe once on dated json, apply side to all four (r439)
        b2, b3 = stage_blob("docs/live_usage/LIVE-2026-10-10.json", 2), stage_blob("docs/live_usage/LIVE-2026-10-10.json", 3)
        t2, t3 = deep_ts(jload(b2)), deep_ts(jload(b3))
        side = 3 if (t3[0] is not None and (t2[0] is None or t3[0] > t2[0])) else 2
        wbytes(jm, stage_blob(jm, side)); wbytes(mm, stage_blob(mm, side))
        log.append(f"{jm}+{mm}: take :{side} (ts2={t2[0]} ts3={t3[0]})")
    # 2) single-writer bm-a faces -> :3:
    for p in ["results/dashboard_status.json", "results/dashboard_status.js",
              "results/strategy_scorecard.json", "results/scorecard_v1.json"]:
        resolve_take_mine(p)
    # 3) take-new snapshots
    for p in ["results/prospect_promotion/_summary.json",
              "results/_attrition_guard_scan.json",
              "results/queue_head_collision_probe.json"]:
        resolve_take_new(p)
    # 4) queue md unions (manual adjudication: UNKNOWN class)
    resolve_tech_md()
    resolve_explore_md()
    for line in log:
        print(line)
    print("RESOLVE-OK", len(log))

if __name__ == "__main__":
    main()
