"""T-131 P1 fundamental-history one-shot backfill collector (lane bm-c).

Ticket: fleet/tasks/T-2026-09-30-131-P1.json -- GM-approved per O-1332 sec.3
("T-131 GM 签名门：批准", 2026-10-01 13:32). Probe evidence (read-only, r292 bm-c):
results/_r292bmc_probe_fundamental_sources.json -- 6 faces ALL alive on ak 1.18.96.

Faces per symbol (source fields verbatim, R258 law; consumers own semantics):
  pe_ttm     baidu  ak.stock_zh_valuation_baidu(sym, indicator="市盈率(TTM)", period="全部")
  pe_static  baidu  indicator="市盈率(静)"      (612 semi-monthly anchors 2001->now)
  pb         baidu  indicator="市净率"
  total_mv   baidu  indicator="总市值"
  roe_q      sina   ak.stock_financial_analysis_indicator(sym, start_year="2001")
                    (quarterly report periods; PIT pubdate alignment = downstream spec)
  div_events sina   ak.stock_history_dividend_detail(sym, indicator="分红")
                    (event face; TTM yield derive = downstream at price-panel join)

Storage (gitignored, regenerable):
  data/fund_history/<code>/<face>.json   per-face atomic files (symbol done = 6 faces)
  data/fund_history/_progress.json       attempts bookkeeping only -- todo is
                                         FILE-DERIVED (R235 law: zero-symbol rounds
                                         cannot stall, universe growth self-heals)
  data/fund_history/_refresh.lock       {pid, ts} while refresh runs
  data/fund_history/_refresh.log        detached child stdout/stderr
Status (tracked, lane owner writes only): results/fund_history_status.json

Semantics (update_astock_daily r280 family):
- throttle ~1.0s sleep/symbol (natural pace: 4x baidu ~1s + ROE 2.4s + div ~0.5s
  ~= 5s/sym -> ~7h full universe; checkpointed, resumable across rounds)
- fuse: 5 consecutive symbol-fetch failures -> stop; 3 consecutive connection
  errors -> source-block stop; checkpoint preserved, self-heals next spawn
- attempts[code] >= 3 -> quarantined (excluded from todo, disclosed in status)
- empty result rows = LEGITIMATE (ok face, e.g. no-dividend stock) -- never a failure
- gate: lane guard bm-c only (R31/R65: other machines stdout-only, zero writes);
  complete -> no-op; lock alive -> in-progress; 30-min spawn throttle; else spawn
Exit codes (gate): 0 = ok/no-op/spawned/in-progress; 2 = machinery failure.
refresh: 0 = universe complete; 2 = stopped (fuse/source-block) -- checkpoint kept.
"""

import csv
import datetime as dt
import io
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "fund_history")
PROG = os.path.join(DATA_DIR, "_progress.json")
LOCK = os.path.join(DATA_DIR, "_refresh.lock")
LOG = os.path.join(DATA_DIR, "_refresh.log")
STATUS = os.path.join(ROOT, "results", "fund_history_status.json")
ELIG = os.path.join(ROOT, "data", "fundamental", "eligibility.csv")

LANE_OWNER = "bm-c"
TICKET_REF = "T-2026-09-30-131-P1"
SYMBOLS_PER_SLEEP = 1.0
FUSE_FAIL = 5
FUSE_CONN = 3
QUARANTINE_AT = 3
SPAWN_THROTTLE_S = 30 * 60
CHECKPOINT_EVERY = 20

FACES = [
    ("pe_ttm", "baidu", "市盈率(TTM)"),
    ("pe_static", "baidu", "市盈率(静)"),
    ("pb", "baidu", "市净率"),
    ("total_mv", "baidu", "总市值"),
    ("roe_q", "sina_ind", None),
    ("div_events", "sina_div", None),
]
FACE_KEYS = [f[0] for f in FACES]


def now_iso():
    return dt.datetime.now().replace(microsecond=0).isoformat()


def atomic_write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    os.replace(tmp, path)


def read_json(path, default=None):
    if not os.path.exists(path):
        return default
    with io.open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def machine_id():
    try:
        return read_json(os.path.join(ROOT, "fleet", "machine.json"), {}).get("machine_id", "")
    except Exception:
        return ""


def load_universe():
    """eligibility.csv 6-digit codes; B-share (2x/9x) + bj (4x/8x/920x) honestly skipped."""
    codes, skips = [], {"b_sz": 0, "b_sh": 0, "bj": 0, "short": 0}
    with io.open(ELIG, "r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            c = (row.get("code") or "").strip()
            if len(c) != 6 or not c.isdigit():
                if c:
                    skips["short"] += 1
                continue
            if c[0] == "2":
                skips["b_sz"] += 1
            elif c[0] == "9":
                skips["b_sh"] += 1
            elif c[0] in ("4", "8"):
                skips["bj"] += 1
            else:
                codes.append(c)
    return codes, skips


def face_path(code, face_key):
    return os.path.join(DATA_DIR, code, face_key + ".json")


def symbol_faces_present(code):
    return [k for k in FACE_KEYS if os.path.exists(face_path(code, k))]


def derive_todo(codes, quarantined):
    return [c for c in codes if c not in quarantined and len(symbol_faces_present(c)) < len(FACES)]


def _ak():
    import akshare as ak
    return ak


def fetch_face(code, face_key, src, indicator):
    """Returns rows list (possibly empty = legitimate). Raises on fetch failure."""
    ak = _ak()
    if src == "baidu":
        df = ak.stock_zh_valuation_baidu(symbol=code, indicator=indicator, period="全部")
    elif face_key == "roe_q":
        df = ak.stock_financial_analysis_indicator(symbol=code, start_year="2001")
    else:
        df = ak.stock_history_dividend_detail(symbol=code, indicator="分红")
    if df is None:
        return []
    return json.loads(df.to_json(orient="records", force_ascii=False, date_format="iso"))


def is_conn_error(exc):
    en = type(exc).__name__ + " " + str(exc)
    return any(t in en for t in ("Connection", "Timeout", "timed out", "HTTP", "ReadError", "SSLError"))


def write_lock():
    atomic_write(LOCK, json.dumps({"pid": os.getpid(), "ts": now_iso()}, ensure_ascii=False))


def clear_lock():
    try:
        os.remove(LOCK)
    except FileNotFoundError:
        pass


def lock_alive():
    lk = read_json(LOCK)
    if not lk or "pid" not in lk:
        return False
    try:
        if os.name == "nt":
            import ctypes
            k32 = ctypes.windll.kernel32
            SYNCHRONIZE = 0x00100000
            h = k32.OpenProcess(SYNCHRONIZE, False, int(lk["pid"]))
            if h:
                k32.CloseHandle(h)
                return True
            return False
        os.kill(int(lk["pid"]), 0)
        return True
    except Exception:
        return False


def build_status(extra=None):
    codes, skips = load_universe()
    prog = read_json(PROG, {"attempts": {}})
    attempts = prog.get("attempts", {})
    quarantined = sorted([c for c, n in attempts.items() if n >= QUARANTINE_AT])
    todo = derive_todo(codes, set(quarantined))
    done_n = len(codes) - len(todo) - len([c for c in quarantined if c not in set(todo)])
    done_faces = 0
    for c in codes:
        if c not in set(todo):
            done_faces += len(symbol_faces_present(c))
    st = {
        "lane": LANE_OWNER, "machine": machine_id(), "ticket_ref": TICKET_REF,
        "generated": now_iso(),
        "universe_n": len(codes), "skipped": skips,
        "done_symbols": len(codes) - len(todo) - len(quarantined),
        "todo_symbols": len(todo), "quarantine_n": len(quarantined),
        "quarantined": quarantined[:50],
        "faces_done": done_faces, "faces_total": len(codes) * len(FACES),
        "complete": len(todo) == 0,
        "note": "one-shot backfill (T-131 scope); PIT pubdate alignment + census H-row unlock = separate follow-up slices",
    }
    if extra:
        st.update(extra)
    return st


def write_status(st):
    atomic_write(STATUS, json.dumps(st, ensure_ascii=False, indent=1))
    # r504 law: json.loads whole-file verify on every tracked-JSON write
    json.loads(io.open(STATUS, "r", encoding="utf-8").read())


def spawn_detached(arg):
    os.makedirs(DATA_DIR, exist_ok=True)
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
             | subprocess.CREATE_NO_WINDOW)
    with io.open(LOG, "a", encoding="utf-8") as lf:
        # close_fds=True: the detached child must NOT inherit the spawning
        # process's stdout pipe handle -- an inherited write end makes the
        # parent's ReadToEndAsync wait for EOF until the (hours-long) child
        # exits (r317 live-fire: 5-min tool hang, child itself healthy).
        subprocess.Popen([sys.executable, os.path.abspath(__file__), arg],
                         stdout=lf, stderr=subprocess.STDOUT,
                         stdin=subprocess.DEVNULL, creationflags=flags,
                         close_fds=True)


def refresh():
    """Long-running full-universe pull. Checkpointed + fused; detached-safe."""
    os.makedirs(DATA_DIR, exist_ok=True)
    write_lock()
    t0 = time.time()
    consec_fail = consec_conn = 0
    pulled = 0
    try:
        codes, _ = load_universe()
        prog = read_json(PROG, {"attempts": {}})
        attempts = prog.setdefault("attempts", {})
        quarantined = {c for c, n in attempts.items() if n >= QUARANTINE_AT}
        todo = derive_todo(codes, quarantined)
        print(f"refresh start: universe={len(codes)} todo={len(todo)} quarantined={len(quarantined)}", flush=True)
        for i, code in enumerate(todo):
            sym_t0 = time.time()
            try:
                for face_key, src, ind in FACES:
                    fp = face_path(code, face_key)
                    if os.path.exists(fp):
                        continue
                    rows = fetch_face(code, face_key, src, ind)
                    atomic_write(fp, json.dumps(
                        {"code": code, "face": face_key, "rows": rows, "n": len(rows),
                         "fetched_at": now_iso()}, ensure_ascii=False))
                consec_fail = consec_conn = 0
                attempts.pop(code, None)
                pulled += 1
            except Exception as e:
                attempts[code] = attempts.get(code, 0) + 1
                consec_fail += 1
                if is_conn_error(e):
                    consec_conn += 1
                print(f"FAIL {code} {type(e).__name__}: {str(e)[:160]} "
                      f"(consec_fail={consec_fail} consec_conn={consec_conn})", flush=True)
                if consec_conn >= FUSE_CONN:
                    print("source-level connection block -- stop, checkpoint kept", flush=True)
                    break
                if consec_fail >= FUSE_FAIL:
                    print("consecutive-failure fuse -- stop, checkpoint kept", flush=True)
                    break
            if (i + 1) % CHECKPOINT_EVERY == 0:
                atomic_write(PROG, json.dumps(prog, ensure_ascii=False, indent=1))
                el = time.time() - t0
                st = build_status({"last_refresh_ts": now_iso(),
                                   "pace_sec_per_sym": round(el / (i + 1), 2)})
                write_status(st)
                print(f"  ... {i + 1}/{len(todo)} elapsed={el:.0f}s "
                      f"pace={st['pace_sec_per_sym']}s/sym", flush=True)
            time.sleep(SYMBOLS_PER_SLEEP)
        atomic_write(PROG, json.dumps(prog, ensure_ascii=False, indent=1))
        el = time.time() - t0
        st = build_status({"last_refresh_ts": now_iso(),
                           "last_refresh_elapsed_sec": round(el, 1),
                           "last_pulled_n": pulled})
        write_status(st)
        print(f"refresh end: pulled={pulled} elapsed={el:.0f}s complete={st['complete']} "
              f"done={st['done_symbols']}/{st['universe_n']}", flush=True)
        return 0 if st["complete"] else 2
    finally:
        clear_lock()


def probe():
    """Live single-symbol 6-face verification leg (r506 law: first real run)."""
    t0 = time.time()
    code = "600519"
    out = {"probe": "T-131 collector live-face leg", "machine": machine_id(),
           "ticket_ref": TICKET_REF, "probed_at": now_iso(), "symbol": code, "faces": {}}
    try:
        for face_key, src, ind in FACES:
            ft = time.time()
            rows = fetch_face(code, face_key, src, ind)
            out["faces"][face_key] = {
                "ok": True, "n": len(rows), "sec": round(time.time() - ft, 2),
                "head": str(rows[0])[:160] if rows else None,
            }
        out["elapsed_sec"] = round(time.time() - t0, 1)
        out["ok"] = True
    except Exception as e:
        out["ok"] = False
        out["err"] = f"{type(e).__name__}: {str(e)[:200]}"
    atomic_write(os.path.join(ROOT, "results", "_r317bmc_fund_history_probe.json"),
                 json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps(out, ensure_ascii=False)[:900])
    return 0 if out.get("ok") else 2


def selftest():
    """Offline legs (zero network)."""
    failed = []

    def leg(name, cond, detail=""):
        print(f"[{'PASS' if cond else 'FAIL'}] {name}" + (f" | {detail}" if detail else ""))
        if not cond:
            failed.append(name)

    codes, skips = load_universe()
    leg("universe parse", len(codes) > 5000 and len(set(codes)) == len(codes),
        f"n={len(codes)} skips={skips}")
    leg("universe all 6-digit", all(len(c) == 6 and c.isdigit() for c in codes))

    tmp = os.path.join(DATA_DIR, "_selftest")
    fake = "999999"
    for k in FACE_KEYS:
        p = face_path(fake, k)
        if os.path.exists(p):
            os.remove(p)
    atomic_write(face_path(fake, "pe_ttm"), json.dumps({"rows": [{"v": 1.0}]}))
    leg("face atomic round-trip", read_json(face_path(fake, "pe_ttm"))["rows"][0]["v"] == 1.0)
    leg("partial symbol = todo", len(symbol_faces_present(fake)) == 1)
    for k in ("pe_static", "pb", "total_mv", "roe_q", "div_events"):
        atomic_write(face_path(fake, k), json.dumps({"rows": []}))
    leg("full symbol = done", len(symbol_faces_present(fake)) == len(FACES))
    leg("file-derived todo excludes done", fake not in derive_todo([fake], set()))
    leg("file-derived todo includes missing", "888888" in derive_todo(["888888"], set()))
    try:
        os.rmdir(os.path.join(DATA_DIR, fake))
    except OSError:
        pass

    leg("conn-error classify", is_conn_error(ConnectionError("refused"))
        and is_conn_error(TimeoutError()) and not is_conn_error(ValueError("bad shape")))
    attempts = {"700700": 3, "700701": 1}
    quarantined = {c for c, n in attempts.items() if n >= QUARANTINE_AT}
    leg("quarantine gate", "700700" in quarantined and "700701" not in quarantined)

    atomic_write(LOCK, json.dumps({"pid": os.getpid(), "ts": now_iso()}))
    leg("lock alive own pid", lock_alive())
    atomic_write(LOCK, json.dumps({"pid": 999999, "ts": now_iso()}))
    leg("lock dead foreign pid", not lock_alive())
    clear_lock()
    leg("lock cleared", not os.path.exists(LOCK))

    st = build_status()
    json.dumps(st)
    leg("status build serializes", st["universe_n"] > 5000 and "faces_total" in st)

    leg("lane owner resolves", LANE_OWNER == "bm-c")
    print(f"selftest: {len(failed)} FAIL")
    return 0 if not failed else 1


def gate():
    """One-shot-backfill gate: complete no-op / in-progress / throttled / spawn."""
    mid = machine_id()
    if mid != LANE_OWNER:
        print(f"fund_history gate: lane owner={LANE_OWNER}, this machine={mid} -> stdout-only no-op")
        return 0
    st = build_status()
    prev = read_json(STATUS, {})
    last_spawn = prev.get("last_spawn_ts")
    if st["complete"]:
        st.pop("last_refresh_ts", None)
        st["last_spawn_ts"] = last_spawn
        write_status(st)
        print(f"fund_history gate: complete ({st['done_symbols']}/{st['universe_n']}) -> no-op")
        return 0
    if lock_alive():
        write_status(st)
        print("fund_history gate: refresh in progress -> no-op (resumable)")
        return 0
    if last_spawn:
        try:
            ls = dt.datetime.fromisoformat(last_spawn)
            if (dt.datetime.now() - ls).total_seconds() < SPAWN_THROTTLE_S:
                write_status(st)
                print("fund_history gate: 30-min spawn throttle active -> no-op")
                return 0
        except ValueError:
            pass
    st["last_spawn_ts"] = now_iso()
    write_status(st)
    spawn_detached("refresh")
    print(f"fund_history gate: spawned detached refresh (todo={st['todo_symbols']})")
    return 0


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "gate"
    if cmd == "refresh":
        return refresh()
    if cmd == "probe":
        return probe()
    if cmd == "selftest":
        return selftest()
    if cmd == "status":
        st = build_status()
        write_status(st)
        print(json.dumps({k: st[k] for k in ("complete", "done_symbols", "todo_symbols",
                                             "quarantine_n", "universe_n")}, ensure_ascii=False))
        return 0
    if cmd == "gate":
        return gate()
    print("usage: update_fund_history.py [gate|refresh|probe|status|selftest]")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as e:  # machinery failure contract
        print(f"machinery failure: {type(e).__name__}: {e}", flush=True)
        sys.exit(2)
