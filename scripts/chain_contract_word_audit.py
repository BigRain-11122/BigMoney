"""Which chain legs can never heal themselves?

The S6 chain pays a leg's writer only when that leg's own probe prints the literal word
STALE (or "face missing") -- `run_leg` in Tools/s6_chain_bmc.py:

    _repairable = ("stale" in text.lower() or "face missing" in text.lower())
    if rc != 0 and refresh and _repairable:   # ... pay the rebuild
    # INCONSISTENT stays red on purpose: paying a rebuild would make red go away

That contract is right (r1934/r1850).  Its consequence is mechanical: a leg whose check
describes a moved upstream with words like "behind", "moved" or "advanced" but never says
STALE is a *permanent* red -- no writer is ever bought, the face freezes on an old bar, and
the only way it turns green is a human running the writer by hand.  r2159 found three of
these by hand (ticket_band, cash_roll_today, k_grid) and fixed them; this face asks how
many are left, and which of them are red right now.

Readings:

  candidates        legs that declare a writer but whose check source never says the word
  red now           of those, the ones failing on this tree today (a frozen face)
  says it moved     candidates whose source does describe a move (behind/moved/advanced/
                    drift) -- the ones that look like drift to a reader but not to the chain

Verdict:

  PERMANENT_REDS_PRESENT   at least one writer leg is red today and cannot pay for itself
  NO_PERMANENT_RED         every red writer leg can pay for its own rebuild
  STRUCTURAL_RISK_ONLY     nothing is red, but N legs would freeze the day their input moves

Usage:
    python scripts/chain_contract_word_audit.py run
    python scripts/chain_contract_word_audit.py --check
    python scripts/chain_contract_word_audit.py --selftest

`run` executes only the candidate checks (never the 110 legs that already speak the
contract), so it is bounded by the size of the defect.  `check` re-reads the chain source
and the candidate scripts (static, ~0.2s) and calls the stored live rows STALE as soon as
one of those scripts or the chain table changes -- the live column is only as fresh as the
digests it prints.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAIN = os.path.join("Tools", "s6_chain_bmc.py")
OUT_JSON = os.path.join(ROOT, "results", "chain_contract_word_audit.json")
OUT_MD = os.path.join(ROOT, "research", "CHAIN_CONTRACT_WORD_AUDIT.md")

CONTRACT = ("stale", "face missing")
DRIFT_WORDS = ("behind", "moved", "advanced", "drift", "changed")
CHECK_TIMEOUT = 60    # r2159: a deep sweep of 134 legs is unbounded at 180s -- the first
                      # deep run sat past 11 minutes on slow checks and was killed by hand


def _digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def legs_from(src_text):
    """The chain's LEGS table, read as data (no import: importing would run the chain)."""
    tree = ast.parse(src_text)
    for node in tree.body:
        targets = getattr(node, "targets", None) or [getattr(node, "target", None)]
        if node.__class__.__name__ in ("Assign", "AnnAssign") and \
                any(getattr(t, "id", None) == "LEGS" for t in targets if t is not None):
            try:
                return ast.literal_eval(node.value)
            except (ValueError, SyntaxError):
                return None
    return None


def script_of(cmd):
    for arg in cmd or []:
        if isinstance(arg, str) and arg.endswith(".py"):
            return arg.replace("\\", "/")
    return None


def speaks_contract(script_text):
    low = script_text.lower()
    return any(w in low for w in CONTRACT)


def drift_words(script_text):
    low = script_text.lower()
    return [w for w in DRIFT_WORDS if w in low]


def scan(root=ROOT, chain=CHAIN):
    """Every writer leg whose check source cannot say the word the chain pays on."""
    path = os.path.join(root, chain)
    legs = legs_from(_read(path))
    if legs is None:
        return {"ok": False, "why": "no LEGS table in %s" % chain}
    rows, n_writer, writers = [], 0, []
    for leg in legs:
        name = leg[0]
        chk = leg[1] if len(leg) > 1 else None
        run_cmd = leg[2] if len(leg) > 2 else None
        if not run_cmd:
            continue                       # check-only legs have no writer to buy
        n_writer += 1
        writers.append([name, chk, run_cmd])
        rel = script_of(chk)
        if not rel:
            rows.append({"leg": name, "script": None, "why": "no script in the check command",
                         "check_cmd": chk})
            continue
        full = os.path.join(root, rel)
        if not os.path.exists(full):
            rows.append({"leg": name, "script": rel, "why": "script not on disk",
                         "check_cmd": chk})
            continue
        text = _read(full)
        if speaks_contract(text):
            continue
        rows.append({"leg": name, "script": rel, "check_cmd": chk,
                     "script_sha256": _digest(full),
                     "drift_words": drift_words(text)})
    return {"ok": True, "n_legs": len(legs), "n_writer_legs": n_writer,
            "chain_sha256": _digest(path), "candidates": rows, "writer_legs": writers}


def probe(cmd, timeout=CHECK_TIMEOUT, cwd=None):
    """Run one candidate check exactly as the chain would, and keep its first line."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout, cwd=cwd or ROOT)
        rc = r.returncode
        text = ((r.stdout or "") + (r.stderr or "")).strip()
    except subprocess.TimeoutExpired:
        rc, text = 124, "TIMEOUT after %ds" % timeout
    first = ""
    for line in text.splitlines():
        if line.strip():
            first = line.strip()
            break
    return rc, first, text


def classify(rc, text):
    """A leg that cannot say the word can only heal by a human -- name that."""
    if rc == 0:
        return "CURRENT"
    if speaks_contract(text):
        return "WORD_APPEARS_AT_RUNTIME"
    return "PERMANENT_RED"


def verdict_of(rows):
    reds = [r for r in rows if r.get("state") == "PERMANENT_RED"]
    if reds:
        return "PERMANENT_REDS_PRESENT", len(reds)
    return ("STRUCTURAL_RISK_ONLY" if rows else "NO_PERMANENT_RED"), 0


def run(root=ROOT, chain=CHAIN, deep=False):
    s = scan(root, chain)
    if not s.get("ok"):
        print(json.dumps(s, ensure_ascii=False))
        return 2
    t0 = time.time()
    rows = [dict(r) for r in s["candidates"]]
    if deep:
        # The static filter cannot see which *branch* the word sits on: a script can carry
        # "stale" in an option name and still describe a moved input as "drifted".  --deep
        # probes every writer leg, which is the only honest count (and costs minutes).
        had = {r["leg"] for r in rows}
        for name, chk, _run_cmd in s["writer_legs"]:
            if name in had:
                continue
            rows.append({"leg": name, "script": script_of(chk), "check_cmd": chk,
                         "contract_in_source": True})
    for row in rows:
        if row.get("state"):
            continue
        cmd = list(row.get("check_cmd") or [])
        if not cmd:
            row["state"] = "NO_CHECK_COMMAND"
            continue
        rc, first, text = probe(cmd, cwd=root)
        row["state"] = classify(rc, text)
        row["rc"] = rc
        row["first_line"] = first[:300]
    state, n_red = verdict_of(rows)
    out = {
        "artifact": "chain_contract_word_audit",
        "face": "results/chain_contract_word_audit.json",
        "script": "scripts/chain_contract_word_audit.py",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "contract": {"word": "stale / face missing",
                     "source": "Tools/s6_chain_bmc.py::run_leg::_repairable"},
        "chain": chain,
        "chain_sha256": s["chain_sha256"],
        "n_legs": s["n_legs"],
        "n_writer_legs": s["n_writer_legs"],
        "n_candidates": len([r for r in rows if r.get("script_sha256")]),
        "n_probed": len([r for r in rows if r.get("state")]),
        "deep": bool(deep),
        "n_permanent_red": n_red,
        "verdict": state,
        "elapsed_sec": round(time.time() - t0, 1),
        "rows": rows,
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(json.dumps({k: out[k] for k in ("verdict", "n_legs", "n_writer_legs",
                                          "n_candidates", "n_permanent_red",
                                          "elapsed_sec")}, ensure_ascii=False))
    render_md(out)
    return 0


def _rows_md(rows):
    L = ["| 腿 | 脚本 | 现在 | 它用来描述「上游动了」的词 | 首行 |", "|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda x: (x.get("state") != "PERMANENT_RED",
                                         x.get("leg") or "")):
        L.append("| %s | `%s` | %s | %s | %s |" % (
            r.get("leg"), r.get("script") or "-", r.get("state") or "-",
            ", ".join(r.get("drift_words") or []) or "（一个都没有）",
            (r.get("first_line") or "").replace("|", "/")[:120] or "-"))
    return L


def render_md(out):
    L = ["# 哪些链腿永远不会自己好\n"]
    L.append("> 生成 %s ｜ 链 `%s` ｜ %d 腿 / %d 条带写者的腿\n"
             % (out.get("generated"), out.get("chain"), out.get("n_legs"),
                out.get("n_writer_legs")))
    L.append("## 一句话\n")
    L.append("链只在探针自己印出 **STALE**（或“face missing”）时才付钱重生一张面（r1934/r1850 判例，"
             "这条规矩是对的——放宽它等于用重生把真缺陷抹掉）。于是凡是把「上游动了」写成 "
             "“behind / moved / advanced” 而从不写 STALE 的腿，就成了**永久红**：写者永远不会被买，"
             "面停在旧 bar 上，只有人手动跑一次才会绿。\n")
    L.append("读数：**%d 条带写者的腿里 %d 条不会说那个词，其中今天红着、且无法自愈的 %d 条**。"
             "判词 **%s**。\n" % (out.get("n_writer_legs"), out.get("n_candidates"),
                                 out.get("n_permanent_red"), out.get("verdict")))
    L.append("## 逐腿\n")
    L.extend(_rows_md(out.get("rows") or []))
    L.append("")
    L.append("## 这张面不回答什么\n")
    L.append("- 它不判这些面算得对不对：`CURRENT` 只说明此刻是绿的，`PERMANENT_RED` 只说明"
             "它红了且没有写者会被买。\n")
    L.append("- 源码里出现 STALE 不等于运行时一定会印（词可能在另一条分支上），反向也只对本次"
             "运行成立——所以 live 列带着每条腿脚本的摘要，脚本一改这张面的 live 列就 STALE。\n")
    L.append("- 只查 `s6_chain_bmc.py` 的 LEGS 表；冒烟腿与人工跑的面不在射程。\n")
    L.append("复现：`python scripts\\chain_contract_word_audit.py run`（只跑候选腿，约 %ss）"
             "；`--check` 静态复核 + 摘要门；`--selftest` 离线行为腿。\n"
             % (out.get("elapsed_sec")))
    os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    return OUT_MD


def check():
    """Static re-derivation plus a digest gate on the live column."""
    problems = []
    if not os.path.exists(OUT_JSON):
        print(json.dumps({"ok": False, "problems": ["face missing"]}, ensure_ascii=False))
        return 2
    with open(OUT_JSON, "r", encoding="utf-8") as fh:
        pub = json.load(fh)
    s = scan()
    if not s.get("ok"):
        print(json.dumps({"ok": False, "problems": [s.get("why")]}, ensure_ascii=False))
        return 1
    moved = []
    if pub.get("chain_sha256") != s["chain_sha256"]:
        moved.append("the chain's leg table changed since this face was written")
    for key in ("n_legs", "n_writer_legs"):
        if pub.get(key) != s[key]:
            problems.append("%s re-derives to %s, face says %s" % (key, s[key], pub.get(key)))
    if pub.get("n_candidates") != len(s["candidates"]):
        problems.append("n_candidates re-derives to %d, face says %s"
                        % (len(s["candidates"]), pub.get("n_candidates")))
    want = sorted((l[0] for l in s["writer_legs"]) if pub.get("deep")
                  else (r["leg"] for r in s["candidates"]))
    got = sorted(r.get("leg") or "" for r in (pub.get("rows") or []))
    if got != want:
        problems.append("the probed leg list changed (%d rows now, %d on the face)"
                        % (len(want), len(got)))
    cur = {r["leg"]: r.get("script_sha256") for r in s["candidates"]}
    for row in (pub.get("rows") or []):
        if row.get("script") and cur.get(row["leg"]) and \
                row.get("script_sha256") != cur.get(row["leg"]):
            moved.append("the check script of leg %s changed since its live reading"
                         % row["leg"])
    # This face is a claim about what each candidate script does when it runs, so a moved
    # digest alone is enough to make the live column unknown -- unlike a face of numbers,
    # where drift with identical readings is still the truth it prints.
    if moved:
        problems = ["STALE " + m for m in moved] + (
            ["these moved with the sources: " + " | ".join(problems)] if problems else [])
    elif problems:
        problems = ["CHECK FAILED " + p for p in problems]
    print(json.dumps({"ok": not problems, "problems": problems,
                      "verdict": pub.get("verdict"), "moved_inputs": moved,
                      "n_current": sum(1 for r in (pub.get("rows") or [])
                                       if r.get("state") == "CURRENT")},
                     ensure_ascii=False))
    return 0 if not problems else 1


# ---------------------------------------------------------------- selftest

def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append({"leg": name, "pass": True})
        except AssertionError as exc:
            legs.append({"leg": name, "pass": False, "why": str(exc)})

    SYNTH = ('LEGS = [\n'
             '    ("a", ["python", "scripts/with_word.py", "check"],\n'
             '     ["python", "scripts/with_word.py", "run"]),\n'
             '    ("b", ["python", "scripts/no_word.py", "check"],\n'
             '     ["python", "scripts/no_word.py", "run"]),\n'
             '    ("c", ["python", "scripts/with_word.py", "check"], None),\n'
             ']\n')

    def l1():
        got = legs_from(SYNTH)
        assert got is not None and len(got) == 3, got

    def l2():
        assert speaks_contract("stale: the panel moved") is True
        assert speaks_contract("face missing on disk") is True
        assert speaks_contract("the panel moved / is behind") is False

    def l3():
        assert classify(0, "") == "CURRENT"
        assert classify(1, "the ledger moved") == "PERMANENT_RED"
        assert classify(1, "STALE the ledger moved") == "WORD_APPEARS_AT_RUNTIME"
        assert classify(124, "TIMEOUT") == "PERMANENT_RED"

    def l4():
        rows = [{"state": "CURRENT"}] * 3
        assert verdict_of(rows)[0] == "STRUCTURAL_RISK_ONLY"
        assert verdict_of([{"state": "PERMANENT_RED"}])[0] == "PERMANENT_REDS_PRESENT"
        assert verdict_of([])[0] == "NO_PERMANENT_RED"

    def l5():
        assert script_of(["python", "scripts\\x.py", "check"]) == "scripts/x.py"
        assert script_of(["python", "-m", "smoke_test"]) is None

    def l6():
        assert set(drift_words("it moved")) == {"moved"}
        assert drift_words("STALE the panel is behind") == ["behind"]

    def _check_on(mutator):
        """Run the real check() against a poisoned copy of the published face."""
        import contextlib
        import copy
        import io as _io
        import tempfile
        global OUT_JSON
        with open(OUT_JSON, "r", encoding="utf-8") as fh:
            poisoned = copy.deepcopy(json.load(fh))
        mutator(poisoned)
        old = OUT_JSON
        with tempfile.TemporaryDirectory() as d:
            tmp = os.path.join(d, "face.json")
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(poisoned, fh)
            OUT_JSON = tmp
            buf = _io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    rc = check()
            finally:
                OUT_JSON = old
        return rc, buf.getvalue()

    def l7():
        def poison(p):
            p["rows"][0]["script_sha256"] = "deadbeef"
        rc, text = _check_on(poison)
        assert rc == 1, (rc, text)
        assert "STALE" in text, text
        assert "CHECK FAILED" not in text, text

    def l8():
        def poison(p):
            p["n_candidates"] = int(p["n_candidates"]) + 1
        rc, text = _check_on(poison)
        assert rc == 1, (rc, text)
        assert "CHECK FAILED" in text, text
        assert "STALE" not in text, text

    for name, fn in (("the LEGS table is read as data", l1),
                     ("the contract word is a literal, not a description", l2),
                     ("a red leg without the word is a permanent red", l3),
                     ("the verdicts follow the rows", l4),
                     ("the script is found inside the check command", l5),
                     ("drift words are listed, not guessed", l6),
                     ("a changed check script makes the live column STALE", l7),
                     ("a disagreeing count with still digests is a defect", l8)):
        leg(name, fn)
    npass = sum(1 for x in legs if x["pass"])
    for x in legs:
        if not x["pass"]:
            print("FAIL", x)
    print("selftest %d/%d" % (npass, len(legs)))
    return 0 if npass == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest", "check"])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--deep", action="store_true",
                    help="probe every writer leg, not only the statically flagged ones")
    args = ap.parse_args(argv)
    if args.selftest or args.cmd == "selftest":
        return selftest()
    if args.check or args.cmd == "check":
        return check()
    return run(deep=args.deep)


if __name__ == "__main__":
    sys.exit(main())
