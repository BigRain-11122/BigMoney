"""Map the smoke legs that cannot be re-asked on their own, and say what to hoist.

Why this exists
---------------
`smoke_red_recheck.py` can re-run any leg whose argv lives in the suite's
declarative table.  The rest are inline blocks inside `smoke_test.py:main()`:
they can only be re-asked by running all 767 legs, so a single red leg costs a
full suite pass.  r2090 measured this: of 18 red legs, 14 had no independent
command at all.

This tool is a read-only inventory.  It parses `smoke_test.py`, finds every
`check("<leg>", ...)` call site, and reports for each leg:

  kind            "table" (re-runnable verbatim) or "inline" (suite-only)
  spans           the top-level statement(s) inside main() that carry the leg
  module_deps     helpers/globals of smoke_test.py the block reads
  main_deps       names assigned elsewhere in main() that the block reads,
                  with the statement that defines each one and whether that
                  statement itself reads other main() locals
  shape           "ready" (no main deps) / "one_hop" (deps are self-contained
                  statements) / "chained" (deps read other main locals)

`shape` answers the only question an extraction round needs: which legs can be
moved into their own script mechanically, and which need a fixture hoisted
first.  Nothing here writes a shared face, calls the network, or imports the
suite -- it only reads source text.

Exit: 0 ok, 2 mechanism failure.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSON = os.path.join(ROOT, "results", "smoke_inline_leg_map.bm-c.json")
OUT_MD = os.path.join(ROOT, "research", "SMOKE_INLINE_LEG_MAP.md")
SUITE = os.path.join(ROOT, "smoke_test.py")
RECHECK = os.path.join(ROOT, "results", "smoke_red_recheck.bm-c.json")

# Same shape as smoke_red_recheck.leg_table(): the suite's own argv triple.
TABLE_RE = re.compile(
    r'\(\s*"((?:[^"\\]|\\.)*)"\s*,\s*"(scripts[\\/][^"\\]+\.py)"\s*,'
    r'\s*\[([^\]]*)\]\s*\)')

LEG_FUNCS = {"check", "check_unsettled", "check_child_killed"}


def table_legs(src: str) -> dict:
    out = {}
    for m in TABLE_RE.finditer(src):
        out.setdefault(m.group(1), m.group(2))
    return out


def _loaded(stmt) -> set:
    return {n.id for n in ast.walk(stmt)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}


def _assigned(stmt) -> set:
    out = set()
    for n in ast.walk(stmt):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
            out.add(n.id)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            out.add(n.name)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(n.name)
            for a in n.args.args if hasattr(n, "args") else []:
                out.add(a.arg)
    return out


def _module_names(tree) -> set:
    out = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                out.add((a.asname or a.name).split(".")[0])
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            out |= _assigned(node)
    return out


def _leg_names(call) -> str:
    if not isinstance(call.func, ast.Name) or call.func.id not in LEG_FUNCS:
        return ""
    if not call.args:
        return ""
    a0 = call.args[0]
    if isinstance(a0, ast.Constant) and isinstance(a0.value, str):
        return a0.value
    return ""


def analyze(src: str, verdicts: dict | None = None) -> dict:
    """Pure function so the selftest can drive it with synthetic source."""
    tree = ast.parse(src)
    module_names = _module_names(tree)
    tbl = table_legs(src)

    funcs = [n for n in tree.body
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    main = next((f for f in funcs if f.name == "main"), None)
    legs = {}

    if main is not None:
        body = main.body
        # where is each main-local assigned, at the top level of main()?
        defined = {}
        for idx, stmt in enumerate(body):
            for name in _assigned(stmt):
                defined.setdefault(name, idx)
        main_locals = set(defined)
        for node in ast.walk(main):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                main_locals.add(node.id)
            elif isinstance(node, ast.ExceptHandler) and node.name:
                main_locals.add(node.name)

        # top-level statement index of each call site
        site_of = {}
        for idx, stmt in enumerate(body):
            for call in [n for n in ast.walk(stmt) if isinstance(n, ast.Call)]:
                leg = _leg_names(call)
                if leg:
                    site_of.setdefault(leg, []).append(idx)

        for leg, sites in site_of.items():
            stmt_idxs = sorted(set(sites))
            loads = set()
            for i in stmt_idxs:
                loads |= _loaded(body[i])
            own = set()
            for i in stmt_idxs:
                own |= _assigned(body[i])
            reading = loads - own
            main_deps = {}
            for name in sorted(reading & main_locals):
                i = defined.get(name)
                if i is None:
                    main_deps[name] = {"defined_in_stmt": None, "lines": None,
                                       "stmt_reads_main_local": None}
                    continue
                d_stmt = body[i]
                d_reads = (_loaded(d_stmt) - _assigned(d_stmt)) & main_locals
                main_deps[name] = {
                    "defined_in_stmt": i,
                    "lines": [d_stmt.lineno, getattr(d_stmt, "end_lineno", d_stmt.lineno)],
                    "stmt_reads_main_local": sorted(d_reads),
                }
            unresolved = sorted(reading - main_locals - module_names)
            if not main_deps:
                shape = "ready"
            elif all(v["stmt_reads_main_local"] == [] for v in main_deps.values()):
                shape = "one_hop"
            else:
                shape = "chained"
            spans = [[body[i].lineno, getattr(body[i], "end_lineno", body[i].lineno)]
                     for i in stmt_idxs]
            legs[leg] = {
                "leg": leg,
                "kind": "table" if leg in tbl else "inline",
                "table_script": tbl.get(leg),
                "spans": spans,
                "module_deps": sorted(reading & module_names),
                "main_deps": main_deps,
                "unresolved": unresolved[:8],
                "shape": shape,
                "verdict": (verdicts or {}).get(leg),
            }

    # table legs never appear as check() calls in some shapes -- add them back
    for leg, script in tbl.items():
        if leg not in legs:
            legs[leg] = {"leg": leg, "kind": "table", "table_script": script,
                         "spans": [], "module_deps": [], "main_deps": {},
                         "unresolved": [], "shape": "ready",
                         "verdict": (verdicts or {}).get(leg)}

    inline = {k: v for k, v in legs.items() if v["kind"] == "inline"}
    # A leg the recheck face actually judged comes first: the map's job is
    # "of the legs we cannot re-ask, which can be moved out first".
    order = sorted(inline.values(),
                   key=lambda v: (0 if v.get("verdict") else 1,
                                  len(v["main_deps"]), len(v["spans"]), v["leg"]))
    summary = {
        "legs_total": len(legs),
        "table_legs": len(legs) - len(inline),
        "inline_legs": len(inline),
        "inline_ready": sum(1 for v in inline.values() if v["shape"] == "ready"),
        "inline_one_hop": sum(1 for v in inline.values() if v["shape"] == "one_hop"),
        "inline_chained": sum(1 for v in inline.values() if v["shape"] == "chained"),
        "inline_with_verdict": sum(1 for v in inline.values() if v.get("verdict")),
    }
    return {"summary": summary, "extraction_order": order, "legs": legs,
            "table_legs": sorted(tbl)}


def read_verdicts(path=RECHECK) -> dict:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            rows = json.load(fh)
    except Exception:
        return {}
    rows = rows.get("rows") or rows.get("legs") or []
    return {r.get("leg"): r.get("verdict") for r in rows if r.get("leg")}


def render_md(face: dict) -> str:
    s = face["summary"]
    lines = [
        "# 冒烟内联腿地图（哪几条腿能单独重问，剩下的要先搬什么）",
        "",
        f"generated {face['generated']} ｜ source=smoke_test.py sha256 {face['source_sha'][:12]}…",
        f"｜ 腿 {s['legs_total']}：声明式 {s['table_legs']} / 内联 {s['inline_legs']}"
        f"（ready {s['inline_ready']} · one_hop {s['inline_one_hop']}"
        f" · chained {s['inline_chained']}）",
        "",
        "本表只读源码，不改冒烟、不跑脚本。`shape` 的含义：",
        "",
        "- `ready`：块内只读模块级名字 —— 代码上可原样搬出（仍要给它一个 check 入口）；",
        "- `one_hop`：读到 main() 的局部变量，但那些变量所在的语句自身不再读别的局部；",
        "- `chained`：连局部变量都在读别的局部，搬之前要先把读取链造成夹具。",
        "",
        "**先看有判决的腿**：排在最前的几行带判决，来自 "
        "`results/smoke_red_recheck.bm-c.json` —— 那是「红且没有独立命令」的实测集合；",
        "其余内联腿只是盘点，不代表现在有问题。",
        "",
        "## 按搬动成本排序（main 局部依赖少的先搬）",
        "",
        "| # | 腿 | shape | main 局部依赖 | smoke_test.py 行 | 最近判决 |",
        "|---|----|-------|---------------|------------------|----------|",
    ]
    for i, v in enumerate(face["extraction_order"], 1):
        deps = ", ".join(v["main_deps"]) or "—"
        spans = ", ".join("%d-%d" % (a, b) for a, b in v["spans"]) or "—"
        lines.append("| %d | %s | %s | %s | %s | %s |"
                     % (i, v["leg"], v["shape"], deps, spans, v.get("verdict") or "—"))
    lines += ["", "## 逐腿要搬的名字", ""]
    for v in face["extraction_order"]:
        if not v["main_deps"]:
            lines.append(f"- **{v['leg']}**：无需搬动（{v['shape']}）。")
            continue
        lines.append(f"- **{v['leg']}**（{v['shape']}）")
        for name, d in sorted(v["main_deps"].items()):
            lines.append(
                "  - `%s` ← 第 %s 条语句（行 %s）%s"
                % (name, d["defined_in_stmt"],
                   "%d-%d" % tuple(d["lines"]) if d["lines"] else "?",
                   "" if not d["stmt_reads_main_local"]
                   else "·它自己还读：`%s`" % "`, `".join(d["stmt_reads_main_local"])))
        if v["unresolved"]:
            lines.append("  - 未归因名字：`%s`" % "`, `".join(v["unresolved"]))
    lines += [
        "",
        "## 这张表不回答的事",
        "",
        "- 它只认得**字面写出**的 `check(\"腿名\", …)`：suite 运行时计数比本表多出的腿",
        "  （循环里拼名字的、按名单生成的）静态解析看不见，差额如实不补。",
        "- 它不判断某条腿值不值得搬：判决来自 `results/smoke_red_recheck.bm-c.json`，",
        "  只那张面说它是红的、且无独立命令，才值得动。",
        "- 它不猜命令。声明式腿的 argv 由 `smoke_red_recheck.py` 从表里逐字取；",
        "  内联腿没有 argv，所以本表只给「要搬什么」，不给「怎么跑」。",
    ]
    return "\n".join(lines) + "\n"


def selftest() -> int:
    import hashlib  # noqa: F401  (kept for parity with other selftests)
    src = (
        "import os\n"
        "LEVEL = 1\n"
        "def helper(x):\n"
        "    return x\n"
        "def main():\n"
        "    a = LEVEL\n"
        "    b = a + 1\n"
        "    try:\n"
        "        c = helper(a)\n"
        "        check('leg one hop', c == 2, 'd')\n"
        "    except Exception as e:\n"
        "        check('leg one hop', False, str(e))\n"
        "    try:\n"
        "        check('leg chained', b > 0, 'd')\n"
        "    except Exception as e:\n"
        "        check('leg chained', False, str(e))\n"
        '    ("leg table", "scripts/x.py", ["check"])\n'
    )
    f = analyze(src, {"leg one hop": "RED_CONTRADICTION"})
    ok = 0
    bad = []

    def chk(name, cond, detail=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            bad.append("%s %s" % (name, detail))

    chk("table leg is detected from the declared argv triple",
        f["legs"]["leg table"]["kind"] == "table")
    chk("inline leg is not mistaken for a table leg",
        f["legs"]["leg one hop"]["kind"] == "inline")
    one = f["legs"]["leg one hop"]["main_deps"]
    chk("a name assigned inside the block is not a dependency",
        "c" not in one, sorted(one))
    chk("only the name the block actually reads is a dependency",
        set(one) == {"a"}, sorted(one))
    chk("the defining statement is located", one["a"]["defined_in_stmt"] == 0,
        one["a"])
    chk("a self-contained defining statement makes the leg one_hop",
        f["legs"]["leg one hop"]["shape"] == "one_hop",
        f["legs"]["leg one hop"]["shape"])
    chk("a try/except pair counts as one leg on one top-level statement",
        len(f["legs"]["leg one hop"]["spans"]) == 1,
        f["legs"]["leg one hop"]["spans"])
    chk("module-level helper is reported as a module dep",
        "helper" in f["legs"]["leg one hop"]["module_deps"],
        f["legs"]["leg one hop"]["module_deps"])
    chk("verdict from the recheck face is carried through",
        f["legs"]["leg one hop"]["verdict"] == "RED_CONTRADICTION")
    chk("a leg the recheck face judged sorts ahead of an unjudged one",
        f["extraction_order"][0]["leg"] == "leg one hop",
        [v["leg"] for v in f["extraction_order"][:2]])
    chk("summary counts inline legs", f["summary"]["inline_legs"] == 2,
        f["summary"])
    chk("chained is recognised when the dep's own statement reads a main local",
        f["legs"]["leg chained"]["shape"] == "chained",
        f["legs"]["leg chained"]["shape"])
    chk("second-order reads are printed, not silently dropped",
        f["legs"]["leg chained"]["main_deps"]["b"]["stmt_reads_main_local"] == ["a"],
        f["legs"]["leg chained"]["main_deps"]["b"])
    chk("ready is recognised when the block only reads module names",
        analyze("def main():\n    check('leg r', 1 == 1, '')\n")["legs"]["leg r"]["shape"]
        == "ready")
    chk("a leg with no check() site still appears if the table declares it",
        analyze('("leg only table", "scripts/y.py", ["check"])\n')["legs"]
        ["leg only table"]["kind"] == "table")
    # real suite
    if os.path.exists(SUITE):
        with open(SUITE, encoding="utf-8", errors="replace") as fh:
            real = analyze(fh.read())
        chk("the real suite parses and yields both kinds",
            real["summary"]["table_legs"] > 0 and real["summary"]["inline_legs"] > 0,
            real["summary"])
        chk("every inline leg names the statement it lives in",
            all(v["spans"] for v in real["extraction_order"]),
            [v["leg"] for v in real["extraction_order"] if not v["spans"]][:3])
    print("selftest %d/%d PASS" % (ok, ok + len(bad)))
    for b in bad:
        print("  FAIL " + b)
    return 0 if not bad else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json-out", default=OUT_JSON)
    ap.add_argument("--md-out", default=OUT_MD)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not os.path.exists(SUITE):
        print("mechanism failure: smoke_test.py missing", file=sys.stderr)
        return 2
    with open(SUITE, encoding="utf-8", errors="replace") as fh:
        src = fh.read()
    import hashlib
    face = analyze(src, read_verdicts())
    face["generated"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    face["source_sha"] = hashlib.sha256(src.encode("utf-8", "replace")).hexdigest()
    face["source"] = "smoke_test.py"
    os.makedirs(os.path.dirname(a.json_out), exist_ok=True)
    with open(a.json_out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    os.makedirs(os.path.dirname(a.md_out), exist_ok=True)
    with open(a.md_out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_md(face))
    s = face["summary"]
    print("SMOKE-INLINE-LEG-MAP legs=%d table=%d inline=%d (ready %d / one_hop %d / chained %d)"
          % (s["legs_total"], s["table_legs"], s["inline_legs"],
             s["inline_ready"], s["inline_one_hop"], s["inline_chained"]))
    for v in face["extraction_order"]:
        print("  %-22s %-8s deps=%d  %s"
              % (v["shape"], "", len(v["main_deps"]), v["leg"][:96]))
    print("face -> %s" % os.path.relpath(a.json_out, ROOT))
    print("doc  -> %s" % os.path.relpath(a.md_out, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
