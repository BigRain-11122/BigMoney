import sys, py_compile
py_compile.compile(r"scripts\parallel_runner.py", doraise=True)
py_compile.compile(r"scripts\census_fusion_s2_w2.py", doraise=True)


def _sq(x):
    return {"v": x * x}


def main():
    sys.path.insert(0, "scripts")
    from parallel_runner import run_cells_parallel
    r = run_cells_parallel([("a", _sq, (2,)), ("b", _sq, (5,))], workers=2)
    assert r["a"] == {"v": 4} and r["b"] == {"v": 25} and r["__workers__"] == 2, r
    seen = []
    r2 = run_cells_parallel([("a", _sq, (3,)), ("b", _sq, (7,))], workers=2,
                            on_result=lambda k, p: seen.append((k, p)))
    assert sorted(seen) == [("a", {"v": 9}), ("b", {"v": 49})], (seen, r2)
    assert r2["a"] == {"v": 9} and r2["b"] == {"v": 49}, r2
    print("PYCOMPILE-PASS x2 + SYNTHETIC-ONRESULT-PASS legacy+flush")


if __name__ == "__main__":
    main()
