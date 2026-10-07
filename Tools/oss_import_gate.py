"""oss_import_gate.py -- O-20261007-2245 bm-c lane: OSS-supply pool-enrollment
admission gate (registration-time door for OSS- prefixed pool entries).

Why: O-2245 opened external-import supply (r705 schema +entries[].source /
permit / adapt_status, OSS- prefix namespace reserved) but enrollment had no
mechanical door -- the scan faces (scripts/oss_eng_scan.py r706, scripts/
oss_license_probe.py r707) produce evidence, they do not admit. This gate is
the single mandatory check BEFORE any OSS- entry lands in results/
runnable_pool.json: every machine enrolling an OSS- supply item must run it
and keep the verdict receipt (lai-na != mian-jian iron face; the gate is a
mechanical admission face only -- scientific validity stays with
science_gates / human review, banned_direction_gate wording).

Legs (all evaluated, no short-circuit; any red = REJECT):
  id_prefix        id must start with "OSS-" (r705 reserved namespace)
  id_unique        id must not already exist in the pool
  schema_declares  pool schema still declares the three r705 OSS fields
  oss_fields       source / permit / adapt_status present, non-empty strings
  permit_pure      permit in the pure bucket (MIT/Apache/BSD/ISC); AGPL/GPL/
                   LGPL forbidden (charter sec.5 spark-arc-studio precedent);
                   NOASSERTION/PENDING/conditional = adjudicate via
                   scripts/oss_license_probe.py first (r707 E2/E5 precedent:
                   REF-ONLY/CONDITIONAL-REF-ONLY cannot enroll)
  adapt_status     must be "adapted" (scanning/adapting = not enrollable;
                   rejected = register to negative-results library, not pool)
  attrition_cross  source tokens + dup_tags vs gate_attrition carriers
                   (judged-negative families must not resurrect; r706 wiring,
                   MOM/clock/wild-way families)
  in_service       source tokens vs in-service registry (akshare/tushare =
                   registered channels, not re-import; r706 precedent)
  prereg_exit_axis prereg_ref resolves to an in-repo .md that declares an
                   explicit exit axis (O-20261001-1108: no declaration = no
                   freeze, no burn)
  runner_exists    runner path exists in-repo (pool law: ready = prereg
                   frozen + runner present)
  status_ready     status == "ready" (enrollment face)
  fields_standard  ticket_ref/lane_owner/priority/entered_at/shards present
                   (shards = non-empty list of {key,status})

Contract (fail-closed, banned_direction_gate bloodline):
    python Tools/oss_import_gate.py --candidate <entry.json>
        exit 0 = ADMIT  (enroll via canonical settle path
                          scripts/merge_lane_views.py sync_face + same-round
                          commit/push per r598 pool-registration law)
        exit 1 = REJECT (any leg red; candidate unreadable; fail-closed)
        exit 2 = MECHANISM FAILURE (pool or attrition carriers unreadable)
    overrides (selftest isolation): --pool <path> --attrition <path> (repeatable)
    python Tools/oss_import_gate.py selftest   (hermetic fixtures + live legs)
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_POOL = os.path.join(ROOT, "results", "runnable_pool.json")
DEFAULT_ATTRITION_FILES = [os.path.join(ROOT, "results", f)
                          for f in ("gate_attrition.json", "gate_attrition.bm-a.json",
                                    "gate_attrition.bm-b.json", "gate_attrition.bm-c.json")]
SELFTEST_EVIDENCE = os.path.join(ROOT, "results", "_r714bmc_oss_import_gate_selftest.json")
LIVECHECK_EVIDENCE = os.path.join(ROOT, "results", "_r714bmc_oss_import_gate_livecheck.json")

OSS_PREFIX = "OSS-"
OSS_SCHEMA_KEYS = ("entries[].source", "entries[].permit", "entries[].adapt_status")
ALLOW_PURE = {"MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", "ISC"}
FORBIDDEN = {"AGPL-3.0", "AGPL-2.0", "GPL-3.0", "GPL-2.0", "LGPL-3.0", "LGPL-2.1"}
IN_SERVICE = {"akshare", "tushare"}
TOKEN_STOP = {"http", "https", "www", "com", "org", "io", "net", "github", "gitee", "gitlab"}
EXIT_AXIS_KEY = "\u51fa\u573a\u8f74"  # 出场轴
EXIT_AXIS_CHOICES = ("\u7b56\u7565\u81ea\u6709\u51fa\u573a",  # 策略自有出场
                     "\u6301\u6709\u5230\u5e95",               # 持有到底
                     "\u65e0\u51fa\u573a",                     # 无出场
                     "\u6301\u6709\u7a7f\u8d8a",               # 持有穿越
                     "template_default")


def _load_json(path):
    """Fail-closed JSON load. Returns (data, None) or (None, reason)."""
    try:
        with io.open(path, encoding="utf-8-sig") as fh:
            return json.load(fh), None
    except OSError as exc:
        return None, f"unreadable: {exc}"
    except ValueError as exc:
        return None, f"not valid JSON: {exc}"


def _attrition_tokens(paths):
    """Parameterized verbatim of oss_eng_scan.load_attrition_tokens walk
    (dict/list/str key-and-value harvest, keys<64 str, values<64 str, lower).
    Missing individual files are skipped (r706 semantic); an EMPTY total set
    is a mechanism failure for the gate (cannot verify = fail-closed)."""
    tokens = set()
    for p in paths:
        if not os.path.exists(p):
            continue
        data, reason = _load_json(p)
        if data is None:
            return None, f"{os.path.basename(p)} {reason}"
        stack = [data]
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                for k, v in cur.items():
                    if isinstance(k, str) and len(k) < 64:
                        tokens.add(k.lower())
                    stack.append(v)
            elif isinstance(cur, list):
                stack.extend(cur)
            elif isinstance(cur, str) and len(cur) < 64:
                tokens.add(cur.lower())
    return tokens, None


def _source_tokens(source, dup_tags):
    """Lowercase tokens from the source string + optional dup_tags list.
    Protocol/host noise is stopped out; short fragments ignored."""
    toks = set()
    for piece in re.split(r"[/:\s]+", str(source)):
        for frag in piece.split("."):
            frag = frag.strip().lower()
            if len(frag) >= 3 and frag not in TOKEN_STOP:
                toks.add(frag)
    for t in dup_tags or []:
        t = str(t).strip().lower()
        if len(t) >= 3:
            toks.add(t)
    return toks


def _leg(name, ok, reason):
    return {"leg": name, "ok": bool(ok), "reason": reason}


def evaluate(candidate_path, pool_path=DEFAULT_POOL,
             attrition_paths=None):
    """Full gate evaluation. Returns (exit_code, verdict_dict).
    exit 0 ADMIT / 1 REJECT / 2 mechanism failure."""
    attrition_paths = list(attrition_paths) if attrition_paths else DEFAULT_ATTRITION_FILES
    pool, reason = _load_json(pool_path)
    if pool is None or not isinstance(pool.get("entries"), list):
        return 2, {"decision": "MECHANISM", "fail_closed": f"pool carrier {reason}",
                   "candidate": candidate_path, "pool": pool_path}
    attr, reason = _attrition_tokens(attrition_paths)
    if attr is None or not attr:
        return 2, {"decision": "MECHANISM",
                   "fail_closed": ("attrition carriers empty/unreadable: "
                                   + (reason or "zero tokens loaded")),
                   "candidate": candidate_path, "pool": pool_path}
    cand, reason = _load_json(candidate_path)
    if cand is None or not isinstance(cand, dict):
        return 1, {"decision": "REJECT", "fail_closed": f"candidate {reason}",
                   "candidate": candidate_path, "pool": pool_path}

    legs = []
    cid = str(cand.get("id", ""))
    # id_prefix
    legs.append(_leg("id_prefix", cid.startswith(OSS_PREFIX),
                     f"id={cid!r} must start with {OSS_PREFIX!r} (r705 namespace)"))
    # id_unique
    pool_ids = {str(e.get("id", "")) for e in pool["entries"]}
    legs.append(_leg("id_unique", cid not in pool_ids,
                     f"id={cid!r} already in pool ({len(pool_ids)}-entry namespace)" if cid in pool_ids
                     else f"unique vs {len(pool_ids)} pool ids"))
    # schema_declares
    schema_keys = set((pool.get("schema") or {}).keys())
    missing_keys = [k for k in OSS_SCHEMA_KEYS if k not in schema_keys]
    legs.append(_leg("schema_declares", not missing_keys,
                     "pool schema missing r705 keys: " + ",".join(missing_keys)
                     if missing_keys else "r705 three OSS fields declared"))
    # oss_fields
    src = cand.get("source"); permit = cand.get("permit"); adapt = cand.get("adapt_status")
    fields_ok = all(isinstance(v, str) and v.strip() for v in (src, permit, adapt))
    legs.append(_leg("oss_fields", fields_ok,
                     "source/permit/adapt_status all required non-empty strings (r705 schema)"
                     if fields_ok else
                     "missing/empty: " + ",".join(
                         n for n, v in (("source", src), ("permit", permit),
                                        ("adapt_status", adapt))
                         if not (isinstance(v, str) and v.strip()))))
    # permit_pure
    if isinstance(permit, str) and permit.strip():
        p = permit.strip()
        if p in FORBIDDEN:
            legs.append(_leg("permit_pure", False,
                             f"{p} forbidden (charter sec.5; backtrader GPL / "
                             "QuantMind AGPL precedents)"))
        elif p in ALLOW_PURE:
            legs.append(_leg("permit_pure", True, f"{p} in pure bucket, direct-use"))
        else:
            legs.append(_leg("permit_pure", False,
                             f"{p} not in pure bucket {sorted(ALLOW_PURE)}; adjudicate via "
                             "scripts/oss_license_probe.py (r707: NOASSERTION often = "
                             "Commons-Clause overlay or dual-license; REF-ONLY cannot enroll)"))
    else:
        legs.append(_leg("permit_pure", False, "permit absent -- cannot verify"))
    # adapt_status
    if adapt == "adapted":
        legs.append(_leg("adapt_status", True, "adapted = enrollment-ready"))
    elif adapt == "rejected":
        legs.append(_leg("adapt_status", False,
                         "rejected items register into the negative-results library "
                         "(anti-resurrection), never into the pool"))
    else:
        legs.append(_leg("adapt_status", False,
                         f"adapt_status={adapt!r} not enrollable (only 'adapted' may enroll)"))
    # attrition_cross (source tokens + dup_tags vs negative-results carriers)
    toks = _source_tokens(src or "", cand.get("dup_tags"))
    hits = sorted(t for t in toks if t in attr)
    legs.append(_leg("attrition_cross", not hits,
                     f"judged-negative family token hit(s): {hits} (anti-resurrection: "
                     "MOM/clock/wild-way families must not resurrect)" if hits
                     else f"clean vs {len(attr)} attrition tokens"))
    # in_service
    svc_hits = sorted(t for t in toks if t in IN_SERVICE)
    legs.append(_leg("in_service", not svc_hits,
                     f"in-service channel {svc_hits} = register-not-import (r706)" if svc_hits
                     else "not an in-service channel re-import"))
    # prereg_exit_axis
    prereg_ref = str(cand.get("prereg_ref", "") or "")
    m = re.search(r"[\w\-./\\:]+\.md", prereg_ref)
    axis_note = ""
    axis_ok = False
    if not prereg_ref.strip():
        axis_note = "prereg_ref empty (pool law: ready = prereg frozen + runner present)"
    elif not m:
        axis_note = f"prereg_ref has no resolvable in-repo .md path: {prereg_ref[:60]!r}"
    else:
        ppath = m.group(0)
        full = ppath if os.path.isabs(ppath) else os.path.join(ROOT, ppath)
        if not os.path.exists(full):
            axis_note = f"prereg path not found in-repo: {ppath}"
        else:
            try:
                with io.open(full, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            except OSError as exc:
                axis_note = f"prereg unreadable: {exc}"
            else:
                has_key = EXIT_AXIS_KEY in text
                has_choice = any(c in text for c in EXIT_AXIS_CHOICES)
                if has_key and has_choice:
                    axis_ok = True
                    axis_note = f"explicit exit axis declared in {ppath}"
                else:
                    axis_note = (f"{ppath} lacks explicit exit-axis declaration "
                                 f"(key={has_key} choice={has_choice}; O-20261001-1108: "
                                 "no declaration = no freeze, no burn)")
    legs.append(_leg("prereg_exit_axis", axis_ok, axis_note))
    # runner_exists
    runner = str(cand.get("runner", "") or "")
    if not runner.strip():
        legs.append(_leg("runner_exists", False, "runner empty"))
    else:
        rfull = runner if os.path.isabs(runner) else os.path.join(ROOT, runner)
        legs.append(_leg("runner_exists", os.path.exists(rfull),
                         f"runner not found in-repo: {runner}"))
    # status_ready
    status = cand.get("status")
    legs.append(_leg("status_ready", status == "ready",
                     f"status={status!r} (enrollment face requires 'ready')"))
    # fields_standard
    missing_std = [n for n, v in (("ticket_ref", cand.get("ticket_ref")),
                                  ("lane_owner", cand.get("lane_owner")),
                                  ("entered_at", cand.get("entered_at")))
                   if not (isinstance(v, str) and v.strip())]
    if not isinstance(cand.get("priority"), int):
        missing_std.append("priority(int)")
    shards = cand.get("shards")
    if not (isinstance(shards, list) and shards and
            all(isinstance(s, dict) and s.get("key") and s.get("status")
                for s in shards)):
        missing_std.append("shards(list of {key,status})")
    legs.append(_leg("fields_standard", not missing_std,
                     "standard pool fields present" if not missing_std
                     else "missing/malformed: " + ",".join(missing_std)))

    reds = [l for l in legs if not l["ok"]]
    decision = "ADMIT" if not reds else "REJECT"
    verdict = {"decision": decision,
               "candidate": candidate_path,
               "next_step_if_admit": ("canonical settle: python scripts/merge_lane_views.py "
                                      "sync_face + same-round commit/push (r598 "
                                      "pool-registration push law); keep this verdict as "
                                      "the enrollment receipt",
                                      ) if decision == "ADMIT" else None,
               "legs": legs,
               "reason": "; ".join(f"{l['leg']}: {l['reason']}" for l in reds) or
                         "all legs green -- mechanical admission face only; scientific "
                         "validity stays with science_gates / human review"}
    return (0 if decision == "ADMIT" else 1), verdict


def _fixture_candidate(**over):
    """Baseline ADMIT-shaped candidate (temp prereg + runner resolved by caller)."""
    c = {"id": "OSS-FIXTURE-01", "ticket_ref": "T-20261008-fixture selftest",
         "prereg_ref": "RESEARCH_PREREG_PATH FROZEN r714 (fixture)",
         "runner": "scripts/oss_eng_scan.py", "runner_args": ["run"],
         "lane_owner": "bm-c", "priority": 1, "status": "ready",
         "entered_at": "2026-10-08 01:5x",
         "source": "github.com/fixture/ossfix", "permit": "MIT",
         "adapt_status": "adapted",
         "shards": [{"key": "fix-0of1", "status": "ready"}]}
    c.update(over)
    return c


def _selftest():
    """Hermetic fixtures + live carrier legs. Writes results/ evidence;
    returns 0 iff all PASS."""
    results, all_pass = [], True
    with tempfile.TemporaryDirectory() as td:
        # carriers: temp pool with r705 schema + one existing entry; temp attrition
        pool_path = os.path.join(td, "pool.json")
        with io.open(pool_path, "w", encoding="utf-8") as fh:
            json.dump({"schema": {"entries[].source": "x", "entries[].permit": "x",
                                  "entries[].adapt_status": "x"},
                       "entries": [{"id": "OSS-EXISTING-01"}]}, fh)
        attr_path = os.path.join(td, "attr.json")
        with io.open(attr_path, "w", encoding="utf-8") as fh:
            json.dump({"fake_negfamily": {"verdict": "judged-negative"}}, fh)
        # temp prereg WITH explicit exit axis
        prereg_ok = os.path.join(td, "FIXTURE_PREREG.md")
        with io.open(prereg_ok, "w", encoding="utf-8") as fh:
            fh.write("# fixture prereg\n## out\n- \u51fa\u573a\u8f74\uff1a"
                     "\u2460\u7b56\u7565\u81ea\u6709\u51fa\u573a"
                     " (family-defined exits, 20d stop)\n")
        prereg_noax = os.path.join(td, "FIXTURE_NOAXIS.md")
        with io.open(prereg_noax, "w", encoding="utf-8") as fh:
            fh.write("# fixture prereg without exit axis\n- buy and hold\n")

        def cand_path(name, **over):
            c = _fixture_candidate(**over)
            c["prereg_ref"] = c["prereg_ref"].replace(
                "RESEARCH_PREREG_PATH", prereg_ok.replace("\\", "/"))
            p = os.path.join(td, name + ".json")
            with io.open(p, "w", encoding="utf-8") as fh:
                json.dump(c, fh, ensure_ascii=False)
            return p

        attr = [attr_path]
        cases = [
            ("L01_admit_mit_full", cand_path("L01"), 0),
            ("L02_no_oss_prefix_reject", cand_path("L02", id="E1-FOO"), 1),
            ("L03_dup_id_reject", cand_path("L03", id="OSS-EXISTING-01"), 1),
            ("L04_missing_oss_fields", cand_path("L04", source=""), 1),
            ("L05_gpl_forbidden", cand_path("L05", permit="GPL-3.0"), 1),
            ("L06_agpl_forbidden", cand_path("L06", permit="AGPL-3.0"), 1),
            ("L07_noassertion_reject", cand_path("L07", permit="NOASSERTION"), 1),
            ("L08_scanning_reject", cand_path("L08", adapt_status="scanning"), 1),
            ("L09_rejected_to_negative_lib", cand_path("L09", adapt_status="rejected"), 1),
            ("L10_attrition_hit_reject",
             cand_path("L10", dup_tags=["fake_negfamily"]), 1),
            ("L11_in_service_reject",
             cand_path("L11", source="github.com/akfamily/akshare"), 1),
            ("L12_exit_axis_missing",
             cand_path("L12", prereg_ref=prereg_noax.replace("\\", "/") + " FROZEN"), 1),
            ("L13_runner_missing", cand_path("L13", runner="scripts/nope_absent.py"), 1),
            ("L14_preref_unresolvable",
             cand_path("L14", prereg_ref="research/NOWHERE_ABSENT.md FROZEN r1"), 1),
            ("L15_status_not_ready", cand_path("L15", status="done"), 1),
            ("L16_schema_drift_reject",
             cand_path("L16"), 1),  # same candidate, drift pool below
            ("L17_broken_candidate_reject", os.path.join(td, "ABSENT.json"), 1),
        ]
        for name, cpath, expect in cases:
            pp = pool_path
            if name == "L16_schema_drift_reject":
                drift = os.path.join(td, "pool_drift.json")
                with io.open(drift, "w", encoding="utf-8") as fh:
                    json.dump({"schema": {"entries[].status": "x"}, "entries": []}, fh)
                pp = drift
            code, v = evaluate(cpath, pool_path=pp, attrition_paths=attr)
            ok = code == expect
            all_pass &= ok
            results.append({"leg": name, "expect": expect, "exit": code, "ok": ok,
                            "reason": v.get("reason", v.get("fail_closed", ""))[:120]})
        # mechanism legs
        broken_pool = os.path.join(td, "pool_broken.json")
        with io.open(broken_pool, "w", encoding="utf-8") as fh:
            fh.write("{not json")
        code, v = evaluate(cand_path("L18"), pool_path=broken_pool, attrition_paths=attr)
        ok = code == 2
        all_pass &= ok
        results.append({"leg": "L18_pool_unreadable_mechanism", "expect": 2,
                        "exit": code, "ok": ok, "reason": v.get("fail_closed", "")[:120]})
        empty_attr = os.path.join(td, "attr_empty.json")
        with io.open(empty_attr, "w", encoding="utf-8") as fh:
            json.dump({}, fh)
        code, v = evaluate(cand_path("L19"), pool_path=pool_path,
                            attrition_paths=[empty_attr])
        ok = code == 2
        all_pass &= ok
        results.append({"leg": "L19_attrition_empty_mechanism", "expect": 2,
                        "exit": code, "ok": ok, "reason": v.get("fail_closed", "")[:120]})
        # CLI face legs (arg-parse + rc contract through subprocess)
        for name, cpath, expect in (("L20_cli_admit_rc0", cand_path("L20"), 0),
                                    ("L21_cli_reject_rc1", cand_path("L21", permit="GPL-3.0"), 1)):
            p = subprocess.run([sys.executable, os.path.abspath(__file__),
                                "--candidate", cpath, "--pool", pool_path,
                                "--attrition", attr_path],
                               capture_output=True, timeout=120)
            ok = p.returncode == expect
            all_pass &= ok
            results.append({"leg": name, "expect": expect, "exit": p.returncode,
                            "ok": ok, "reason": "CLI rc contract"})
    # live carrier legs (read-only against real repo faces)
    real_pool, reason = _load_json(DEFAULT_POOL)
    ok = real_pool is not None and len(real_pool.get("entries", [])) >= 300
    all_pass &= ok
    results.append({"leg": "L22_real_pool_loads", "expect": True, "exit": 0 if ok else 1,
                    "ok": ok, "reason": (f"{len((real_pool or {}).get('entries', []))} entries"
                                         if ok else f"real pool {reason}")})
    real_attr, reason = _attrition_tokens(DEFAULT_ATTRITION_FILES)
    ok = bool(real_attr) and len(real_attr or ()) >= 1000
    all_pass &= ok
    results.append({"leg": "L23_real_attrition_loads", "expect": True, "exit": 0 if ok else 1,
                    "ok": ok, "reason": (f"{len(real_attr)} tokens (r706 recorded 1434)"
                                         if ok else f"real attrition {reason}")})
    # parity: this gate's parameterized walk == oss_eng_scan carrier walk (bloodline)
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "oss_eng_scan", os.path.join(ROOT, "scripts", "oss_eng_scan.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        carrier = mod.load_attrition_tokens()
        ok = carrier == real_attr
        reason = f"parity {len(carrier)} vs {len(real_attr)}"
    except Exception as exc:  # noqa: BLE001 -- fail-closed honest leg
        ok, reason = False, f"carrier import failed: {exc}"
    all_pass &= ok
    results.append({"leg": "L24_attrition_walk_parity", "expect": True, "exit": 0 if ok else 1,
                    "ok": ok, "reason": reason[:120]})

    evidence = {"tool": "Tools/oss_import_gate.py selftest",
                "round": "r714 bm-c (O-20261007-2245 bm-c lane enrollment-door leg)",
                "legs": results, "all_pass": all_pass}
    with io.open(SELFTEST_EVIDENCE, "w", encoding="utf-8") as fh:
        json.dump(evidence, fh, ensure_ascii=False, indent=1)
    for r in results:
        print(f"[{'PASS' if r['ok'] else 'FAIL'}] {r['leg']}: exit={r['exit']} {r['reason']}")
    print(f"selftest: {'ALL PASS' if all_pass else 'FAILURES'} -> {SELFTEST_EVIDENCE}")
    return 0 if all_pass else 1


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description="OSS-supply pool-enrollment admission gate "
                                             "(O-20261007-2245 bm-c lane)")
    ap.add_argument("--candidate", help="candidate pool-entry JSON to admit/reject")
    ap.add_argument("--pool", default=DEFAULT_POOL,
                    help="pool json (default results/runnable_pool.json)")
    ap.add_argument("--attrition", action="append",
                    help="attrition carrier json (repeatable; default gate_attrition x4)")
    sub = ap.add_mutually_exclusive_group()
    sub.add_argument("--selftest", action="store_true", help="run hermetic selftest")
    sub.add_argument("selftest_word", nargs="?", choices=["selftest"])
    args = ap.parse_args(argv)
    if args.selftest or args.selftest_word:
        return _selftest()
    if not args.candidate:
        ap.print_usage()
        print("fail-closed: --candidate required")
        return 1
    code, verdict = evaluate(args.candidate, pool_path=args.pool,
                              attrition_paths=args.attrition)
    print(json.dumps(verdict, ensure_ascii=False, indent=1))
    return code


if __name__ == "__main__":
    sys.exit(main())
