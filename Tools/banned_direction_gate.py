"""banned_direction_gate.py -- pre-registration admission gate over falsified
directions (D-20260930-41 section 1.2 / retail-quant-conclusions-v2 section 3).

Why: the company burned 362,083 trials with 0 passing the science gates,
largely because compute kept re-entering directions that were already
falsified with real data. The registry research/BANNED_DIRECTIONS.json is the
machine-readable falsified-directions canon; this gate is its mechanical
admission face, wired into PREREG_TEMPLATE.md section 0.5 (run-before-burn).

Contract (fail-closed):
    python Tools/banned_direction_gate.py --prereg research/<BATCH>.md
        exit 0 = ADMIT   (no banned claim, or a complete section-0.5 exception)
        exit 1 = REJECT  (banned claim without complete exception; unreadable
                          prereg; missing/corrupt registry; any internal error)
    python Tools/banned_direction_gate.py --registry <path> --prereg <path>
                          (registry override, used by selftest isolation)
    python Tools/banned_direction_gate.py selftest
                          (hermetic fixtures, writes results/ evidence file)

Scan scope: the WHOLE prereg body EXCLUDING the section-0.5 block itself
(the exception declaration legitimately names the banned directions it
quotes; self-matching would be a false REJECT by construction). Any pattern
hit outside section 0.5 requires, per registry key
required_fields_in_prereg_on_match, all three exception fields inside the
section-0.5 block:
    1) citation of every matched BAN-xx id,
    2) an exception type token: new_data or new_mechanism,
    3) a non-placeholder "what the original falsification could not have
       seen" statement.
The gate is a mechanical admission face only -- whether an exception
argument is scientifically valid stays with science_gates / human review.
"""
import argparse
import io
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_REGISTRY = os.path.join(ROOT, "research", "BANNED_DIRECTIONS.json")
SELFTEST_EVIDENCE = os.path.join(ROOT, "results", "_r491bma_banned_gate_selftest.json")

S05_HEADER = "\u00a70.5"  # §0.5
EXCEPTION_TYPES = ("new_data", "new_mechanism")
CANNOT_SEE_KEY = "\u4e0d\u53ef\u80fd\u770b\u89c1"  # 不可能看见


def _load_registry(path):
    """Fail-closed registry load. Returns (data, None) or (None, reason)."""
    try:
        with io.open(path, encoding="utf-8-sig") as fh:
            data = json.load(fh)
    except OSError as exc:
        return None, f"registry unreadable: {exc}"
    except ValueError as exc:
        return None, f"registry not valid JSON: {exc}"
    dirs = data.get("directions")
    if not isinstance(dirs, list) or not dirs:
        return None, "registry has no directions list"
    for d in dirs:
        if not isinstance(d.get("id"), str) or not isinstance(d.get("patterns"), list):
            return None, f"registry direction malformed: {d.get('id')!r}"
        for pat in d["patterns"]:
            try:
                re.compile(pat, re.IGNORECASE)
            except re.error as exc:
                return None, f"pattern compile fail {d['id']}/{pat!r}: {exc}"
    return data, None


def _split_s05(text):
    """Return (body_without_s05, s05_block). Section runs from the header line
    to the next '## ' header line or EOF."""
    lines = text.splitlines()
    s05, body = [], []
    in_s05 = False
    for ln in lines:
        if S05_HEADER in ln and ln.lstrip().startswith("#"):
            in_s05 = True
            s05.append(ln)
            continue
        if in_s05 and ln.startswith("## "):
            in_s05 = False
        (s05 if in_s05 else body).append(ln)
    return "\n".join(body), "\n".join(s05)


def _find_hits(registry, body):
    """Scan body for every direction pattern. Returns list of
    {id, name, evidence: [{line, snippet}]}."""
    hits = []
    body_lines = body.splitlines()
    for d in registry["directions"]:
        ev = []
        for pat in d["patterns"]:
            rx = re.compile(pat, re.IGNORECASE)
            for no, ln in enumerate(body_lines, 1):
                m = rx.search(ln)
                if m:
                    s = max(0, m.start() - 12)
                    ev.append({"line": no, "snippet": ln[s:m.end() + 12].strip()})
                    break  # one evidence line per pattern is enough
        if ev:
            hits.append({"id": d["id"], "name": d.get("name", ""), "evidence": ev[:4]})
    return hits


def _exception_state(s05):
    """Inspect the section-0.5 block for the three required fields."""
    cited = sorted({int(x) for x in re.findall(r"BAN-(\d{1,2})", s05)})
    typ = next((t for t in EXCEPTION_TYPES if t in s05), None)
    # statement: value after the key on the same line, else next non-empty line
    statement_ok, statement_raw = False, ""
    idx = s05.find(CANNOT_SEE_KEY)
    if idx >= 0:
        tail = s05[idx + len(CANNOT_SEE_KEY):]
        colon = tail.find("\uff1a")  # ：
        if colon < 0:
            colon = tail.find(":")
        same_line, rest = "", ""
        if colon >= 0:
            after = tail[colon + 1:]
            same_line = after.split("\n", 1)[0].strip()
            rest = after.split("\n", 1)[1] if "\n" in after else ""
        nxt = ""
        for ln in (rest or "").splitlines():
            if ln.strip():
                nxt = ln.strip()
                break
        for cand in (same_line, nxt):
            cleaned = cand.strip(" *_\u3000-")
            if cleaned and not set(cleaned) <= set("_\uff3f"):
                statement_ok, statement_raw = True, cleaned[:80]
                break
    missing = []
    if typ is None:
        missing.append("exception type (new_data|new_mechanism)")
    if not statement_ok:
        missing.append("what-the-original-falsification-could-not-see statement")
    return {"cited_ids": cited, "exception_type": typ,
            "statement_ok": statement_ok, "statement_raw": statement_raw,
            "missing_fields": missing}


def evaluate(prereg_path, registry_path=DEFAULT_REGISTRY):
    """Full gate evaluation. Returns (exit_code, verdict_dict)."""
    registry, reason = _load_registry(registry_path)
    if registry is None:
        return 1, {"decision": "REJECT", "fail_closed": reason,
                   "prereg": prereg_path, "registry": registry_path}
    try:
        with io.open(prereg_path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        return 1, {"decision": "REJECT", "fail_closed": f"prereg unreadable: {exc}",
                   "prereg": prereg_path, "registry": registry_path}
    except UnicodeDecodeError as exc:
        return 1, {"decision": "REJECT", "fail_closed": f"prereg not UTF-8: {exc}",
                   "prereg": prereg_path, "registry": registry_path}
    body, s05 = _split_s05(text)
    hits = _find_hits(registry, body)
    verdict = {"decision": "ADMIT", "prereg": prereg_path,
               "registry_version": registry.get("version"),
               "matched": hits, "exception": None, "reason": ""}
    if not hits:
        verdict["reason"] = "no banned direction claimed"
        return 0, verdict
    exc_state = _exception_state(s05)
    verdict["exception"] = exc_state
    matched_ids = sorted({int(h["id"].split("-")[1]) for h in hits})
    uncited = [i for i in matched_ids if i not in exc_state["cited_ids"]]
    if uncited:
        exc_state["missing_fields"].append(
            "citation for matched ids: " + ", ".join(f"BAN-{i:02d}" for i in uncited))
    if not s05.strip():
        verdict["reason"] = (
            "banned directions claimed but prereg has no section-0.5 exception block")
        verdict["decision"] = "REJECT"
    elif exc_state["missing_fields"]:
        verdict["reason"] = ("section-0.5 exception incomplete: "
                             + "; ".join(exc_state["missing_fields"]))
        verdict["decision"] = "REJECT"
    else:
        verdict["reason"] = (
            "banned directions claimed WITH complete section-0.5 exception "
            f"({exc_state['exception_type']}); scientific validity of the "
            "exception remains with science_gates / human review")
    return (0 if verdict["decision"] == "ADMIT" else 1), verdict


def _selftest():
    """Hermetic fixtures. Writes results/ evidence; returns 0 iff all PASS."""
    grid_ban = "\u7f51\u683c"  # 网格 (BAN-04 pattern)
    s05_decl = (
        f"## {S05_HEADER} \u7981\u5f00\u65b9\u5411\u786c\u95f8\n"
        "- \u547d\u4e2d\u7f16\u53f7\uff1aBAN-04\n"
        "- \u4f8b\u5916\u7c7b\u578b\uff1a`new_data`\n"
        f"- **\u539f\u5426\u8bc1{CANNOT_SEE_KEY}\u7684\u4e1c\u897f**\uff1a"
        "2016\u5e74\u524d\u9ec4\u91d1ETF\u5206\u7ea7\u57fa\u91d1\u65e5\u7ebf"
        "\uff0c\u539f\u6279\u5f53\u65f6\u65e0\u6cd5\u83b7\u53d6\n\n## \u00a71 "
        "\u03b1 \u673a\u5236\u6bb5\n- placeholder\n")
    fixtures = [
        # (name, prereg_text, registry_override, expect_exit)
        ("S1_clean_admit", "## \u00a71 \u03b1\n- low-vol carry across bond ETFs\n",
         None, 0),
        ("S2_banned_no_s05_reject",
         f"## \u00a71 \u03b1\n- strategy: {grid_ban}\u4ea4\u6613 518880\n", None, 1),
        ("S3_banned_full_exception_admit",
         s05_decl + f"## \u00a72\n- {grid_ban} on gold ETF with new data\n", None, 0),
        ("S4_placeholder_statement_reject",
         s05_decl.replace(
             "\uff1a2016\u5e74\u524d\u9ec4\u91d1ETF\u5206\u7ea7\u57fa\u91d1\u65e5\u7ebf"
             "\uff0c\u539f\u6279\u5f53\u65f6\u65e0\u6cd5\u83b7\u53d6",
             "\uff1a____________")
         + f"## \u00a72\n- {grid_ban} on gold ETF with new data\n", None, 1),
        ("S5_missing_registry_failclosed", "anything", "Z:/nope.json", 1),
        ("S6_missing_prereg_failclosed", "FILE_ABSENT", None, 1),
        ("S7_wrong_id_citation_reject",
         s05_decl.replace("BAN-04", "BAN-07")
         + f"## \u00a72\n- {grid_ban} on gold ETF\n", None, 1),
        ("S8_s05_mention_only_admit", s05_decl + "## \u00a72\n- clean body\n", None, 0),
    ]
    results, all_pass = [], True
    with tempfile.TemporaryDirectory() as td:
        for name, txt, reg, expect in fixtures:
            ppath = os.path.join(td, name + ".md")
            if txt != "FILE_ABSENT":
                with io.open(ppath, "w", encoding="utf-8") as fh:
                    fh.write(txt)
            code, v = evaluate(ppath, reg or DEFAULT_REGISTRY)
            ok = code == expect
            all_pass &= ok
            results.append({"leg": name, "expect": expect, "exit": code,
                            "ok": ok, "decision": v.get("decision"),
                            "reason": (v.get("reason") or v.get("fail_closed", ""))[:110]})
    evidence = {"tool": "Tools/banned_direction_gate.py selftest",
                "round": "r491 bm-a (T-129 D-41 gate landing, r471 adoption)",
                "legs": results, "all_pass": all_pass}
    with io.open(SELFTEST_EVIDENCE, "w", encoding="utf-8") as fh:
        json.dump(evidence, fh, ensure_ascii=False, indent=1)
    for r in results:
        print(f"[{'PASS' if r['ok'] else 'FAIL'}] {r['leg']}: "
              f"exit={r['exit']} ({r['decision']}) {r['reason']}")
    print(f"selftest: {'ALL PASS' if all_pass else 'FAILURES'} -> {SELFTEST_EVIDENCE}")
    return 0 if all_pass else 1


def main(argv=None):
    # Deterministic UTF-8 stdout: on Windows a piped stdout falls back to the
    # locale codec (GBK), which mojibakes the CJK evidence for subprocess
    # callers. The verdict JSON is a machine contract -> always UTF-8.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description="banned-directions prereg admission gate")
    ap.add_argument("--prereg", help="path to the prereg .md to admit/reject")
    ap.add_argument("--registry", default=DEFAULT_REGISTRY,
                    help="registry json (default research/BANNED_DIRECTIONS.json)")
    sub = ap.add_mutually_exclusive_group()
    sub.add_argument("--selftest", action="store_true", help="run hermetic selftest")
    sub.add_argument("selftest_word", nargs="?", choices=["selftest"])
    args = ap.parse_args(argv)
    if args.selftest or args.selftest_word:
        return _selftest()
    if not args.prereg:
        ap.print_usage()
        print("fail-closed: --prereg required")
        return 1
    code, verdict = evaluate(args.prereg, args.registry)
    print(json.dumps(verdict, ensure_ascii=False, indent=1))
    return code


if __name__ == "__main__":
    sys.exit(main())
