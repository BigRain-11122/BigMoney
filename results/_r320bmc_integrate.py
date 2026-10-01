# -*- coding: utf-8 -*-
# _r320bmc_integrate.py -- r320 S0 integration (bm-c)
# Rebuild r319 residual delta onto origin/main via r314 CAS route (no rebase --continue family).
# Face policy per r296 triage / r505 ride / r507 payload-side base / r481 AA sans-audit /
# r315 CODELY union / r504 ticket-note-in-string+json.loads / r512 CAS direct retry.
import subprocess, json, sys, re, time

R = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CRE = 8  # CREATE_NO_WINDOW
BK = "bmc-backup-r320"          # backup ref of pre-surgery local main (r319 family + ride)
PRE_MAIN = None                 # anchored dynamically after initial ride

def git(*a, check=True):
    p = subprocess.run(["git", "-C", R] + list(a), capture_output=True, creationflags=CRE)
    if check and p.returncode != 0:
        raise RuntimeError("git %s rc=%s\n%s" % (" ".join(a), p.returncode,
                                                  p.stderr.decode("utf-8", "replace")))
    return p.stdout.decode("utf-8", "replace"), p.returncode

def blob(ref, path):
    out, rc = git("show", "%s:%s" % (ref, path), check=False)
    return out if rc == 0 else None

TAKE_MINE = [
    "Tools/saturation_engine.py", "Tools/register_saturation_engine_task.ps1",
    "results/_r319bmc_closeout.py", "results/_r319bmc_fuse_resolve.py",
    "results/_r319bmc_rebase_resolver.py", "results/_r319bmc_s6_runner.ps1",
    "results/_r319bmc_stage_probe.py", "results/_r319bmc_stash_pop_resolve.py",
    "results/autofill_state.bm-c.json", "results/compute_audit.bm-c.json",
    "results/crash_fuse.bm-c.json", "results/dispatcher_state.bm-c.json",
    "results/futures_update_status.bm-c.json", "results/lhb_update_status.bm-c.json",
    "results/regime_state.bm-c.json", "results/token_usage.bm-c.json",
    "results/update_status.bm-c.json", "results/saturation_engine_state.bm-c.json",
    "results/runnable_pool.bm-c.json", "results/pool_dualrun.bm-c.jsonl",
    "results/fund_history_status.json", "results/fund_premium_status.json",
    "results/perpetual_faces/n1_w9_results.json",
    "fleet/machines/bm-c.json", "state-bm-c.json", "round_reports-bm-c.md",
    "fleet/inbox/MSG-20261001-1432-bmc-bmb-n1w9-ledger-head.md",
] + ["results/pool_claims/PERPETUAL-N1-W9-SHARD-%d/n1w9-%dof12.bm-c.json" % (k, k) for k in range(12)]

TAKE_ORIGIN_REFRESH = [  # shared/foreign faces: keep origin truth (refresh each attempt)
    "results/crash_fuse.json", "results/regime_state.json", "results/token_usage.json",
    "results/update_status.json", "results/lhb_update_status.json",
    "results/fundamental_b_layer_filter.json", "results/_attrition_guard_scan.json",
    "docs/live_usage/LIVE-2026-10-01.md", "docs/live_usage/LIVE-latest.md",
    "results/autofill_state.bm-a.json", "results/crash_fuse.bma-a.json".replace("bma", "bm"),
    "results/runnable_pool.bm-a.json", "results/runnable_pool.json",
] + ["results/p2cal_ext/n1_w9/shard-%d-of-12.json" % k for k in range(3, 9)]

RIDE_OK_RE = re.compile(r"(results/.*\.bm-c\.(json|jsonl)|results/(fund_history_status|fund_premium_status)\.json)$")
SHARED_RESTORE_RE = re.compile(
    r"(results/(crash_fuse|runnable_pool|regime_state|token_usage|update_status|lhb_update_status|"
    r"fundamental_b_layer_filter|_attrition_guard_scan)\.(json|jsonl)|"
    r"results/.*(bm-a|bm-b)\.(json|jsonl)|docs/live_usage/LIVE-.*|state-bm-a\.json|state\.json)$")

def clean_tree():
    out, _ = git("status", "--porcelain")
    ride, restore, foreign = [], [], []
    for line in out.splitlines():
        if not line.strip():
            continue
        st, path = line[:2], line[3:].strip().strip('"')
        if st == "??":
            continue
        if RIDE_OK_RE.search(path):
            ride.append(path)
        elif SHARED_RESTORE_RE.search(path):
            restore.append(path)
        else:
            foreign.append(line)
    if foreign:
        print("ABORT: unexpected dirty faces (possible interactive session):")
        print("\n".join(foreign))
        sys.exit(2)
    if ride:
        git("add", "--", *ride)
        git("commit", "-m", "r320 ride-2: bm-c lane faces mid-surgery (daemon writes)")
        print("ride-2 committed:", ride)
    if restore:
        git("checkout", "HEAD", "--", *restore)
        print("restored-to-HEAD (shared derived, origin lands):", restore)

def strip_audit(obj):
    if isinstance(obj, dict):
        return {k: strip_audit(v) for k, v in obj.items() if k != "audit"}
    if isinstance(obj, list):
        return [strip_audit(x) for x in obj]
    return obj

def apply_delta():
    git("checkout", BK, "--", *TAKE_MINE)
    # AA sans-audit assert on p2cal shards 3..8 (deterministic frozen batch, r481 law)
    for k in range(3, 9):
        p = "results/p2cal_ext/n1_w9/shard-%d-of-12.json" % k
        a = json.loads(blob("HEAD", p)); b = json.loads(blob(BK, p))
        if strip_audit(a) != strip_audit(b):
            print("AA-FAIL %s: science payload differs beyond audit envelope -- ABORT" % p)
            sys.exit(2)
    # runnable_pool.json payload check (r507): local-only entries carried, else origin stands
    o_pool = json.loads(blob("HEAD", "results/runnable_pool.json"))
    b_pool = json.loads(blob(BK, "results/runnable_pool.json"))
    def entries(x):
        d = x if isinstance(x, dict) else {"_": x}
        return {e.get("id"): e for e in d.get("entries", []) if isinstance(e, dict)}
    oe, be = entries(o_pool), entries(b_pool)
    only_local = [i for i in be if i not in oe]
    if only_local:
        print("WARN pool local-only entries carried:", only_local)
        merged = dict(o_pool); have = {e.get("id") for e in o_pool.get("entries", [])}
        for i in only_local:
            if i not in have:
                merged["entries"] = list(o_pool.get("entries", [])) + [be[i]]
        with open(R + r"\results\runnable_pool.json", "w", newline="", encoding="utf-8") as f:
            f.write(json.dumps(merged, ensure_ascii=False, indent=2))
        git("add", "--", "results/runnable_pool.json")
    print("pool check: origin_entries=%d backup_entries=%d local_only=%d" % (len(oe), len(be), len(only_local)))
    # CODELY.md union: origin base + my added bullet lines appended (r315 de-facto append)
    o_codely = blob("HEAD", "CODELY.md") or ""
    b_codely = blob(BK, "CODELY.md") or ""
    mine_lines = [ln for ln in b_codely.splitlines()
                  if ln.startswith("- [") and ln not in set(o_codely.splitlines())]
    if mine_lines:
        base = o_codely if o_codely.endswith("\n") else o_codely + "\n"
        merged = base + "\n".join(mine_lines) + "\n"
        for ln in mine_lines:
            assert merged.count(ln) == 1, "CODELY dedupe violated"
        with open(R + r"\CODELY.md", "w", newline="", encoding="utf-8") as f:
            f.write(merged)
        git("add", "--", "CODELY.md")
        print("CODELY union: appended %d line(s)" % len(mine_lines))
    # pool_core_samples.jsonl union (line-set, append-only jsonl face)
    o_j = blob("HEAD", "results/pool_core_samples.jsonl") or ""
    b_j = blob(BK, "results/pool_core_samples.jsonl") or ""
    o_lines = [l for l in o_j.splitlines() if l.strip()]
    b_lines = [l for l in b_j.splitlines() if l.strip()]
    extra = [l for l in b_lines if l not in set(o_lines)]
    if extra:
        for l in (o_lines + extra):
            json.loads(l)
        with open(R + r"\results\pool_core_samples.jsonl", "w", newline="", encoding="utf-8") as f:
            f.write("\n".join(o_lines + extra) + "\n")
        git("add", "--", "results/pool_core_samples.jsonl")
        print("pool_core_samples union: +%d line(s), total=%d" % (len(extra), len(o_lines) + len(extra)))
    # T-141 ticket merge (r504: json.loads whole-file gate + surgical size check)
    tp = "fleet/tasks/T-2026-10-01-141-P1.json"
    t = json.loads(blob("HEAD", tp))
    cl = t.setdefault("claims", {})
    cl["s1"] = {"bm-c": {
        "claimed_at": "2026-10-01 14:19", "status": "done",
        "result_ref": "Tools/saturation_engine.py (resident, schtasks Bigmoney-SaturationEngine 1-min IgnoreNew, 15/15 selftest); N1-W9 wave 12/12 engine-burned+finalized (results/perpetual_faces/n1_w9_results.json, K=19920, ledger 382239); acceptance face per law sec.6 in flight (3-workday py>=70% measurement)",
        "scope": "bm-c engine core instance per spec (local perpetual queue N1 v0.1, band slot shard%3, PreIgnitionChecks r316, 26/32 cap, close_fds r317, self-restart, state self-derived)"}}
    if "s2-ledger-conversion" not in cl:
        cl["s2-ledger-conversion"] = {
            "claimed_by": "bm-c", "claimed_at": "2026-10-01 14:58", "status": "in_progress",
            "note": "first-claim verified against origin claims+progress (s2 open first-claim) at r320 push window per r239; build start r320: async-batched ledger appends + perpetual-burn pre-claim exemption + grammar-registry consumption logged at generation window (law sec.2)"}
    add = "s1 bm-c instance DONE r319-r320 (engine live, N1-W9 12/12 via engine, sources on origin); s2 ledger-conversion first-claimed by bm-c r320."
    if add not in t.get("progress", ""):
        t["progress"] = (t.get("progress", "") + " " + add).strip()
    new_text = json.dumps(t, ensure_ascii=False, indent=1)
    json.loads(new_text)
    if len(new_text.splitlines()) - len((blob("HEAD", tp) or "").splitlines()) > 60:
        print("ABORT: T-141 round-trip diff too large (format flip risk)")
        sys.exit(2)
    with open(R + "\\" + tp.replace("/", "\\"), "w", newline="", encoding="utf-8") as f:
        f.write(new_text)
    git("add", "--", tp)
    print("T-141 merged: s1-bm-c done + s2 first-claim")
    git("checkout", "HEAD", "--", *TAKE_ORIGIN_REFRESH)
    git("add", "--", "results/_r320bmc_integrate.py")

MSG = ("round 320: S0 integration -- r319 residual delta rebuilt onto origin/main (r314 CAS route, "
       "rebase-continue family avoided): saturation engine sources + N1-W9 finalize (K=19920 ledger 382239) "
       "+ bm-c lane/claims faces + shared faces origin-side truth; "
       "T-141 s1-bm-c done + s2 first-claim [via bm-c]")

def main():
    global PRE_MAIN
    clean_tree()
    PRE_MAIN, _ = git("rev-parse", "main")
    PRE_MAIN = PRE_MAIN.strip()
    print("PRE_MAIN anchor:", PRE_MAIN[:9])
    for attempt in range(1, 4):
        git("fetch", "origin")
        o_sha, _ = git("rev-parse", "origin/main")
        print("attempt %d base=%s" % (attempt, o_sha.strip()[:9]))
        _, rc = git("checkout", "--detach", "origin/main", check=False)
        if rc != 0:
            clean_tree()
            git("checkout", "--detach", "origin/main")
        apply_delta()
        staged, _ = git("diff", "--cached", "--stat")
        print("staged faces:\n%s" % staged)
        git("commit", "-m", MSG)
        new_sha, _ = git("rev-parse", "HEAD")
        out, rc = git("push", "origin", "HEAD:main", check=False)
        print("push rc=%d %s" % (rc, out.strip()[:300]))
        if rc == 0:
            _, rc2 = git("update-ref", "refs/heads/main", new_sha.strip(), PRE_MAIN, check=False)
            if rc2 != 0:
                print("WARN: local-main CAS failed (daemon moved main) -- main untouched, origin has delivery; manual sync next round")
                sys.exit(3)
            git("checkout", "main")
            git("fetch", "origin")
            behind, _ = git("rev-list", "--count", "main..origin/main")
            ahead, _ = git("rev-list", "--count", "origin/main..main")
            print("DELIVERED: behind=%s ahead=%s main=%s" % (behind.strip(), ahead.strip(), new_sha.strip()[:9]))
            sys.exit(0)
        print("push rejected -- origin moved; re-applying on new base (r512 CAS direct retry)")
        time.sleep(3)
    print("PUSH-FAIL after 3 attempts (fleet peak window) -- machine-branch fallback next")
    sys.exit(4)

if __name__ == "__main__":
    main()
