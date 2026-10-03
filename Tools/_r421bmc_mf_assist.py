"""r421 bm-c: moneyflow EM rank-face assist pull (MSG-2026-10-03-1452 option A).

Lane owner (bm-a) is IP-hard-blocked on push2/push2his (sustained
RemoteDisconnected, 14:24-14:33 probes). bm-a's option A explicitly invites
"a machine claiming option A"; bm-c has no p1c/bars dependency (MSG-1452).

Imports the collector's rank-face kernels SINGLE-SOURCE
(scripts/update_moneyflow.py), does ONE full-universe rank cross-section pull
from bm-c's IP, captures RAW per-page JSONs as a replayable payload. On the
lane owner's side Tools/mf_assist_replay.py feeds the pages back through
fetch_page injection into the EXACT canonical rank_pass -- zero new canonical
code, zero semantic drift, zero bm-c writes to canonical faces (R31 guard).

Run modes (r324 law: >3min live MUST be detached + self-logging + polled;
first inline attempt was auto-decapitated at 5.0min silent -- honest budget
disclosure: that run consumed up to ~60 rank requests with zero evidence
landed; this detached rerun re-spends the daily face budget, disclosed in
evidence JSON):
    python Tools\_r421bmc_mf_assist.py spawn   # detach the run, return at once
    python Tools\_r421bmc_mf_assist.py run    # the worker itself (detached)
    python Tools\_r421bmc_mf_assist.py status  # one-line progress read

Writes (bm-c-owned faces only):
  logs/mf_assist_r421.log                       incremental worker log (ignored)
  fleet/transfers/T-2026-10-03-157-rank-pages-<stamp>.json.gz   payload
  fleet/transfers/T-2026-10-03-157-sender.json  transfer manifest
  results/_r421bmc_mf_assist.json                round evidence (flushed per leg)
"""
import csv as _csv
import datetime as dt
import gzip
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TICKET = "T-2026-10-03-157"
STAMP_FALLBACK = "2026-09-30"
LOG = os.path.join(ROOT, "logs", "mf_assist_r421.log")
EVID = os.path.join(ROOT, "results", "_r421bmc_mf_assist.json")
RANK_DEADLINE_S = 1500.0        # overall rank-leg fuse (hang-storm abort)
PROBE_SYMS = (("600519", "sh"), ("000001", "sz"), ("300750", "sz"))


def logw(line):
    stamp = dt.datetime.now().isoformat(timespec="seconds")
    with io.open(LOG, "a", encoding="utf-8") as fh:
        fh.write(f"[{stamp}] {line}\n")
        fh.flush()


def flush_evid(ev):
    ev["updated"] = dt.datetime.now().isoformat(timespec="seconds")
    with io.open(EVID, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(ev, fh, ensure_ascii=False, indent=1)


def load_umf():
    spec = importlib.util.spec_from_file_location(
        "umf_assist_r421", os.path.join(ROOT, "scripts", "update_moneyflow.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)          # module carries __main__ guard (r324 law)
    return m


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def spawn():
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
             | subprocess.CREATE_NO_WINDOW)
    with io.open(LOG, "a", encoding="utf-8") as lf:
        subprocess.Popen(
            [sys.executable, os.path.abspath(__file__), "run"],
            stdout=lf, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
            creationflags=flags, close_fds=True)      # r317 close_fds law
    print("spawned detached mf_assist run; poll: logs/mf_assist_r421.log")
    return 0


def status():
    try:
        with io.open(LOG, "r", encoding="utf-8") as fh:
            lines = fh.read().strip().splitlines()
        print("\n".join(lines[-8:]) if lines else "(log empty)")
    except FileNotFoundError:
        print("(no log yet)")
    if os.path.exists(EVID):
        with io.open(EVID, encoding="utf-8") as fh:
            ev = json.load(fh)
        print("evid verdict:", ev.get("verdict", "(pending)"))
    else:
        print("evid: (not written yet)")
    return 0


def run():
    t0 = time.time()
    logw("worker start (detached)")
    ev = {
        "ts": dt.datetime.now().isoformat(timespec="seconds"),
        "machine": "bm-c", "round": "r421",
        "action": "MSG-2026-10-03-1452 option A claim (rank-face assist pull)",
        "ticket": TICKET,
        "budget_disclosure": ("first inline attempt auto-decapitated at 5.0min "
                              "silent (r324 law violation by the round driver; "
                              "zero evidence landed) -- this detached rerun "
                              "re-spends the ~60-req rank face budget"),
        "verdict": "in_progress",
    }
    flush_evid(ev)

    umf = load_umf()
    now = dt.datetime.now()
    allowed, why = umf.rank_pull_allowed(now)
    ev["window_guard"] = {"allowed": allowed, "reason": why}
    logw(f"window guard: allowed={allowed} why={why}")
    stamp = None
    try:
        stamp = umf.expected_latest_bar_date(now)
    except Exception as e:
        ev["stamp_error"] = f"{type(e).__name__}: {str(e)[:120]}"
    ev["expected_stamp"] = stamp
    logw(f"expected stamp: {stamp}")

    umf._clear_proxy_env()              # Clash hijack law (J13/r39/R34)

    # ---- leg 1: rank face, full pull, capture raw pages -------------------
    pages = []
    page_lat = []
    rank_err = None

    def fetch_page_capture(pn, timeout=10):
        nonlocal rank_err
        if time.time() - t0 > RANK_DEADLINE_S:
            rank_err = f"rank deadline fuse {RANK_DEADLINE_S:.0f}s exceeded at page {pn}"
            raise TimeoutError(rank_err)
        t = time.time()
        try:
            js = umf._fetch_rank_page_impl(pn, timeout=timeout)
        except Exception as e:
            logw(f"page {pn} FAIL {type(e).__name__}: {str(e)[:120]} "
                 f"({time.time() - t:.1f}s)")
            raise
        lat = round(time.time() - t, 2)
        page_lat.append({"pn": pn, "latency_s": lat})
        pages.append({"pn": pn, "js": js})
        n = len((js or {}).get("data") or {}).get("diff") or []
        logw(f"page {pn} ok {lat}s items_so_far={len(pages)} diff_n={len(n)}")
        return js

    t_rank = time.time()
    try:
        items, total, pages_walked, err = umf.fetch_rank_all_pages(
            fetch_page=fetch_page_capture)
        if rank_err:
            err = err or rank_err
    except Exception as e:
        items, total, pages_walked, err = {}, None, 0, \
            f"outer abort {type(e).__name__}: {str(e)[:200]}"
    ev["rank_fetch"] = {
        "total": total, "pages_walked": pages_walked, "n_items": len(items),
        "err": err, "elapsed_s": round(time.time() - t_rank, 1),
        "latency_first3": page_lat[:3],
        "latency_last": page_lat[-1] if page_lat else None,
    }
    rank_ok = (err is None) and bool(items) and (not total or len(items) >= total)
    ev["rank_fetch"]["complete"] = rank_ok
    ev["rank_fetch"]["pages_captured"] = len(pages)
    logw(f"rank leg done: ok={rank_ok} items={len(items)} total={total} "
         f"pages={len(pages)} err={err}")
    ev["verdict"] = "rank leg done" if rank_ok else "RANK PULL FAILED from bm-c"
    flush_evid(ev)

    # ---- leg 2: daykline face probe (read-only feasibility) ---------------
    probe = []
    for code, mkt in PROBE_SYMS:
        t = time.time()
        try:
            rows = umf.fetch_one(code, mkt)
            probe.append({"code": code, "market": mkt, "ok": True,
                          "n_rows": len(rows),
                          "first": rows[0]["date"] if rows else None,
                          "last": rows[-1]["date"] if rows else None,
                          "latency_s": round(time.time() - t, 2)})
            logw(f"daykline probe {code}.{mkt} OK rows={len(rows)}")
        except Exception as e:
            probe.append({"code": code, "market": mkt, "ok": False,
                          "exc": f"{type(e).__name__}: {str(e)[:160]}",
                          "latency_s": round(time.time() - t, 2)})
            logw(f"daykline probe {code}.{mkt} FAIL {type(e).__name__}")
        time.sleep(2.5)                  # citizenship pace (spec SLEEP_S)
    ev["daykline_probe"] = probe
    ev["daykline_probe_verdict"] = (
        "alive" if all(p.get("ok") for p in probe) else
        "blocked" if not any(p.get("ok") for p in probe) else "mixed")
    logw(f"daykline probe verdict: {ev['daykline_probe_verdict']}")
    flush_evid(ev)

    # ---- universe preview vs eligibility.csv (info-only) ------------------
    try:
        codes = set()
        col = None
        with io.open(os.path.join(ROOT, "data", "fundamental",
                                  "eligibility.csv"),
                     encoding="utf-8-sig") as fh:
            for row in _csv.DictReader(fh):
                if col is None:
                    col = next((k for k in row if "code" in str(k).lower()
                                or "代码" in str(k)), None)
                    if col is None:
                        break
                codes.add(str(row[col]).strip())
        if rank_ok:
            in_elig = sum(1 for c in items if c in codes)
            ev["universe_preview"] = {
                "eligibility_n": len(codes), "rank_n": len(items),
                "rank_in_eligibility": in_elig,
                "note": ("info-only; canonical bars-universe join happens at "
                         "replay on the lane owner (bm-a)"),
            }
        else:
            ev["universe_preview"] = {"eligibility_n": len(codes)}
    except Exception as e:
        ev["universe_preview"] = {"error": f"{type(e).__name__}: {str(e)[:160]}"}

    # ---- payload + manifest (only on clean full pull) ---------------------
    if rank_ok:
        payload = json.dumps(pages, ensure_ascii=True, separators=(",", ":"))
        gz_name = f"{TICKET}-rank-pages-{stamp or STAMP_FALLBACK}.json.gz"
        gz_path = os.path.join(ROOT, "fleet", "transfers", gz_name)
        os.makedirs(os.path.dirname(gz_path), exist_ok=True)
        with gzip.open(gz_path, "wb", compresslevel=6) as fh:
            fh.write(payload.encode("ascii"))
        sha = sha256_file(gz_path)
        manifest = {
            "ticket": TICKET,
            "kind": "moneyflow-rank-pages-replay-payload",
            "from": "bm-c", "to": "bm-a",
            "stamp": stamp,
            "n_pages": len(pages), "n_items": len(items), "total": total,
            "bytes_raw": len(payload), "bytes_gz": os.path.getsize(gz_path),
            "sha256_gz": sha,
            "replay_cmd": ("python Tools\\mf_assist_replay.py "
                           f"\"fleet\\transfers\\{gz_name}\""),
            "authorization": ("bm-a MSG-2026-10-03-1452 option A invitation "
                              "(lane owner); O-1620 GM-approved moneyflow "
                              "domain; watermark next_pick claimed lane"),
            "channel": ("git control-plane (<1MB artifact; TRANSFER.md B2 "
                        "croc is the fallback channel)"),
        }
        with io.open(os.path.join(ROOT, "fleet", "transfers",
                                  f"{TICKET}-sender.json"), "w",
                     encoding="utf-8", newline="\n") as fh:
            json.dump(manifest, fh, ensure_ascii=False, indent=1)
        ev["payload"] = {"file": gz_name, "sha256_gz": sha,
                         "bytes_gz": os.path.getsize(gz_path)}
        ev["verdict"] = "RANK PULL OK -- payload ready for bm-a replay"
    else:
        ev["verdict"] = ("RANK PULL FAILED from bm-c (option A feasibility "
                         "evidence; see rank_fetch.err + daykline_probe)")

    ev["elapsed_total_s"] = round(time.time() - t0, 1)
    flush_evid(ev)
    logw(f"worker done verdict={ev['verdict']} elapsed={ev['elapsed_total_s']}s")
    return 0 if rank_ok else 2


def main(argv):
    if argv and argv[0] == "spawn":
        return spawn()
    if argv and argv[0] == "status":
        return status()
    if argv and argv[0] == "run":
        return run()
    print("usage: _r421bmc_mf_assist.py spawn|run|status")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
