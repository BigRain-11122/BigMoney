# -*- coding: utf-8 -*-
"""r341 bm-b: verify census_fusion_s2.py run()/run_unc() incremental-flush
mirror of the r340 W2-A fix. Hermetic: py_compile + parallel_runner
on_result contract re-proof + source-contract asserts (no real data, no
network, no burn). Evidence for round 341 S3 closed loop."""
import ast
import py_compile
import sys

sys.path.insert(0, "scripts")

py_compile.compile(r"scripts\census_fusion_s2.py", doraise=True)


def _sq(x):
    return {"v": x * x}


def main():
    # [1] parallel_runner on_result contract re-proof (r340 primitive,
    #     exercised against current disk code: legacy None path unchanged,
    #     flush path fires per completed job)
    from parallel_runner import run_cells_parallel
    r = run_cells_parallel([("a", _sq, (2,)), ("b", _sq, (5,))], workers=2)
    assert r["a"] == {"v": 4} and r["b"] == {"v": 25}, r
    seen = []
    r2 = run_cells_parallel([("a", _sq, (3,)), ("b", _sq, (7,))], workers=2,
                            on_result=lambda k, p: seen.append((k, p)))
    assert sorted(seen) == [("a", {"v": 9}), ("b", {"v": 49})], (seen, r2)
    print("PASS [1] parallel_runner on_result contract (legacy + flush)")

    # [2] source contract: both run() and run_unc() wire on_result=_flush
    #     with flushed-set safety net; _append_ckpt/_append_unc_ckpt live
    #     INSIDE the flush callback (incremental), post-loop guarded.
    src = open(r"scripts\census_fusion_s2.py", encoding="utf-8").read()
    tree = ast.parse(src)
    wired = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in ("run", "run_unc"):
            has_flush_def = has_on_result = has_guard = False
            for n in ast.walk(node):
                if isinstance(n, ast.FunctionDef) and n.name == "_flush":
                    body_src = ast.dump(n)
                    apnd = ("_append_ckpt" if node.name == "run"
                            else "_append_unc_ckpt")
                    has_flush_def = apnd in body_src
                if (isinstance(n, ast.keyword) and n.arg == "on_result"
                        and isinstance(n.value, ast.Name)
                        and n.value.id == "_flush"):
                    has_on_result = True
            has_guard = "_blk not in flushed" in src
            wired[node.name] = (has_flush_def and has_on_result and has_guard)
    assert wired.get("run") and wired.get("run_unc"), wired
    print("PASS [2] run()+run_unc() on_result=_flush wiring + safety net")

    # [3] flaw-family residual sweep: any remaining run_cells_parallel call
    #     inside THIS file without on_result (should be zero after fix)
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call)
             and getattr(getattr(n, "func", None), "id", "") ==
             "run_cells_parallel"]
    missing = []
    for c in calls:
        if not any(k.arg == "on_result" for k in c.keywords):
            missing.append(c.lineno)
    assert not missing, f"residual collect-only-tail calls at lines {missing}"
    print(f"PASS [3] zero residual collect-only-tail calls in file "
          f"({len(calls)} run_cells_parallel calls, all on_result-wired)")
    print("verify: ALL PASS")


if __name__ == "__main__":
    main()
