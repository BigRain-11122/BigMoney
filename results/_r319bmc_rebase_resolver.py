# r319 bm-c rebase resolver -- conflict families per law:
#  AA deterministic products (r481): assert science-payload equal, take origin
#  ticket claims: union (slice-declared claims, both machines)
#  CODELY.md: entry-extraction union (r315 law: base=origin full text + my entry append)
#  same-day idempotent faces + shared derive faces (r505): wall-clock newer side, raw bytes
#  append-only jsonl (r294): line-set union (conflict-zone domain only)
import json, re, subprocess, sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def stage(path, n):  # n=2 ours(being-applied) / 3 theirs(origin)
    r = subprocess.run(["git", "-C", ROOT, "show", ":%d:%s" % (n, path)],
                       capture_output=True)
    if r.returncode != 0:
        raise SystemExit("stage read fail %s :%d: %s" % (path, n, r.stderr[:200]))
    return r.stdout

def ts_of(raw):
    m = re.search(rb'"ts"\s*:\s*"([^"]+)"', raw) or \
        re.search(rb'"generated[_a-z]*"\s*:\s*"([^"]+)"', raw) or \
        re.search(rb'"updated_at"\s*:\s*"([^"]+)"', raw)
    return m.group(1).decode("utf-8", "ignore") if m else None

def resolve_ts_newer(path):
    a, b = stage(path, 2), stage(path, 3)
    ta, tb = ts_of(a), ts_of(b)
    win = a if (ta or "") > (tb or "") else b      # string compare works for ISO ts
    with open(ROOT + "\\" + path.replace("/", "\\"), "wb") as fh:
        fh.write(win)
    print("  ts-newer %-46s mine=%s origin=%s -> %s" %
          (path, ta, tb, "MINE" if win is a else "ORIGIN"))

def resolve_union_jsonl(path):
    probe = subprocess.run(["git", "-C", ROOT, "show", ":2:%s" % path],
                           capture_output=True)
    if probe.returncode != 0:
        print("  jsonl-union %-44s no conflict stages (auto-merged) -> skip" % path)
        return
    a, b = stage(path, 2).decode("utf-8"), stage(path, 3).decode("utf-8")
    la, lb = [l for l in a.splitlines() if l.strip()], [l for l in b.splitlines() if l.strip()]
    seen, out = set(), []
    for l in lb + la:                              # origin order first, my lines appended
        if l in seen:
            continue
        seen.add(l); out.append(l)
    eol = "\r\n" if "\r\n" in b else "\n"
    with open(ROOT + "\\" + path.replace("/", "\\"), "w", encoding="utf-8", newline="") as fh:
        fh.write(eol.join(out) + eol)
    print("  jsonl-union %-44s origin=%d mine=%d -> %d" % (path, len(lb), len(la), len(out)))

def resolve_aa_product(path, audit_keys):
    # rebase semantics (fact-probed r319): :2: = origin/base, :3: = our commit
    probe = subprocess.run(["git", "-C", ROOT, "show", ":2:%s" % path],
                           capture_output=True)
    if probe.returncode != 0:
        print("  aa-product %-45s no conflict stages (auto-merged) -> skip" % path)
        return
    a, b = stage(path, 2), stage(path, 3)          # a=origin, b=ours
    da, db = json.loads(a), json.loads(b)
    pa = {k: v for k, v in da.items() if k not in audit_keys}
    pb = {k: v for k, v in db.items() if k not in audit_keys}
    assert pa == pb, "AA science payload DIFFERS at %s -- escalate, do not blind-take" % path
    with open(ROOT + "\\" + path.replace("/", "\\"), "wb") as fh:
        fh.write(a)                                # ORIGIN side verbatim (r481: pool-lane basis)
    print("  aa-product %-45s payload IDENTICAL -> ORIGIN (envelope diff only)" % path)

def resolve_ticket_union(path):
    a, b = json.loads(stage(path, 2)), json.loads(stage(path, 3))
    out = dict(b)                                  # origin base (has bm-b claims)
    ca = a.get("claims") or {}
    co = out.get("claims") or {}
    for slice_name, machines in ca.items():
        co.setdefault(slice_name, {}).update(machines)
    out["claims"] = co
    eol = "\r\n" if b"\r\n" in stage(path, 3)[:2000] else "\n"
    text = json.dumps(out, ensure_ascii=False, indent=1) + eol
    with open(ROOT + "\\" + path.replace("/", "\\"), "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    print("  ticket-union %-45s claims slices=%s" %
          (path, {k: sorted(v) for k, v in co.items()}))

def resolve_codely_union(path, my_marker, my_line):
    # rebase semantics: stage 2 = ORIGIN full text (the side that may carry the
    # peer's same-window re-compile) -> base MUST be origin, my entry appended
    base = stage(path, 2).decode("utf-8")
    if my_marker in base:
        print("  codely-union: my entry already present (dedupe no-op)")
    else:
        base = base.rstrip("\r\n") + "\r\n\r\n" + my_line.rstrip("\r\n") + "\r\n"
        print("  codely-union: my entry appended to ORIGIN base")
    with open(ROOT + "\\" + path.replace("/", "\\"), "w", encoding="utf-8", newline="") as fh:
        fh.write(base)

if __name__ == "__main__":
    print("resolver start")
    # 1) same-day idempotent + shared derive faces: wall-clock newer (r505)
    for p in ["docs/daily_report/REPORT-2026-10-01.json",
              "docs/daily_report/REPORT-2026-10-01.md",
              "docs/live_usage/LIVE-2026-10-01.json",
              "docs/live_usage/LIVE-2026-10-01.md",
              "docs/live_usage/LIVE-latest.json",
              "docs/live_usage/LIVE-latest.md",
              "results/compute_audit.json",
              "results/fundamental_b_layer_filter.json",
              "results/futures_update_status.json",
              "results/lhb_update_status.json",
              "results/regime_state.json",
              "results/scorecard_v1.json",
              "results/strategy_scorecard.json",
              "results/update_status.json"]:
        resolve_ts_newer(p)
    # 2) append-only jsonl union
    resolve_union_jsonl("results/pool_core_samples.jsonl")
    # 3) AA deterministic products: r481 assert + take origin
    audit_keys = {"machine", "workers", "elapsed", "elapsed_sec", "host", "pid",
                  "ts", "generated", "generated_at", "owner", "claim", "audit"}
    for p in ["results/p2cal_ext/n1_w9/shard-0-of-12.json",
              "results/p2cal_ext/n1_w9/shard-1-of-12.json"]:
        resolve_aa_product(p, audit_keys)
    # 4) ticket claims union
    resolve_ticket_union("fleet/tasks/T-2026-10-01-141-P1.json")
    # 5) CODELY union (entry extraction, r315)
    my_marker = "r319 bm-c] psutil process_iter"
    my_line = ("- [2026-10-01 14:3x r319 bm-c] psutil process_iter 首读 0.0 过载误判坑"
               "（T-141 s1 饱和引擎首窗实弹）：process_iter([\"cpu_percent\"]) 对每进程首次调用恒返 0.0"
               "（无既往采样点）→新起常驻监督器首个周期把满载机器读成空载→过量点火"
               "（本窗：S6 链+T-131 在飞时引擎仍连点 12 分片·audit cap_violation 旗瞬态〔CEO 90 帽〕）；"
               "正解=启动时先空跑一次 _py_cpu_pct() 预读（丢弃结果·进程级计数器落锚）"
               "+点火双门（py<70 fill 线 + MACHINE_IGNITE_HOLD 88 机器面）；"
               "连带=psutil.cpu_percent(interval=None) 机器面同样需 prime。"
               "How to apply：一切 psutil 常驻采样器启动必 prime 双面（机器+进程）再进判定循环；"
               "首周期判定结果一律丢弃或走保守门。")
    resolve_codely_union("CODELY.md", my_marker, my_line)
    print("resolver done -- verify with git add + rebase --continue")
