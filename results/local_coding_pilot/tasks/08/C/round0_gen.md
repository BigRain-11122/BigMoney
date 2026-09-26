```python
import sys
import os
import json
import re

def recon(cells_lines, panel_text):
    # 解析 panel
    try:
        panel = json.loads(panel_text)
    except Exception:
        panel = {}

    def get_panel_int(key, default=-1):
        val = panel.get(key)
        if isinstance(val, int):
            return val
        return default

    def get_panel_str(key, default="-"):
        val = panel.get(key)
        if isinstance(val, str):
            return val
        return default

    def get_panel_list(key, default=[]):
        val = panel.get(key)
        if isinstance(val, list):
            return val
        return default

    # 初始化计数器
    blank = 0
    malformed = 0
    valid = 0
    codes_unique = set()
    dup_codes = set()
    kind_live = 0
    kind_extra = 0
    kind_other = 0
    status_ok = 0
    status_fail = 0
    appended_sum = 0

    # 解析 cells 行
    for line in cells_lines:
        stripped = line.strip()
        if not stripped:
            blank += 1
            continue

        try:
            obj = json.loads(stripped)
        except Exception:
            malformed += 1
            continue

        if not isinstance(obj, dict):
            malformed += 1
            continue

        # 验证字段契约
        code = obj.get("code")
        pass_val = obj.get("pass")
        kind = obj.get("kind")
        status = obj.get("status")
        appended = obj.get("appended")

        if not isinstance(code, str) or not code:
            malformed += 1
            continue

        if not isinstance(pass_val, str):
            malformed += 1
            continue

        if not isinstance(kind, str):
            malformed += 1
            continue

        if not isinstance(status, str):
            malformed += 1
            continue

        if appended is not None and not isinstance(appended, int):
            malformed += 1
            continue

        # 计数有效行
        valid += 1
        codes_unique.add(code)
        if list(codes_unique).count(code) > 1:
            dup_codes.add(code)

        if kind == "live":
            kind_live += 1
        elif kind == "extra":
            kind_extra += 1
        else:
            kind_other += 1

        if status == "ok":
            status_ok += 1
        else:
            status_fail += 1

        appended_sum += appended if appended is not None else 0

    # 派生统计
    codes_unique_count = len(codes_unique)
    dup_codes_count = len(dup_codes)
    pass_set = set()
    for line in cells_lines:
        stripped = line.strip()
        if not stripped:
            continue
        try:
            obj = json.loads(stripped)
        except Exception:
            continue
        if isinstance(obj, dict):
            pass_val = obj.get("pass")
            if isinstance(pass_val, str):
                pass_set.add(pass_val)

    # pass 渲染规则
    if len(pass_set) == 0:
        pass_render = "-"
    elif len(pass_set) == 1:
        pass_render = list(pass_set)[0]
    else:
        pass_render = "MULTI"

    # 对账检查
    panel_universe = get_panel_int("universe")
    panel_attempted = get_panel_int("attempted")
    panel_appended = get_panel_int("appended")
    panel_last_pass_date = get_panel_str("last_pass_date")
    panel_fails = get_panel_list("fails")
    panel_mismatches = get_panel_list("mismatches")

    # 检查 c0
    c0_ok = (malformed == 0)

    # 检查 c1
    c1_ok = False
    if panel_attempted != -1:
        c1_ok = (valid == panel_attempted)

    # 检查 c2
    c2_ok = False
    if panel_universe != -1:
        c2_ok = (codes_unique_count == panel_universe)

    # 检查 c3
    c3_ok = False
    if panel_last_pass_date != "-":
        if pass_render == panel_last_pass_date:
            c3_ok = True
    else:
        if pass_render == "-":
            c3_ok = True

    # 检查 c4
    c4_ok = False
    if panel_appended != -1:
        c4_ok = (appended_sum == panel_appended)

    # 检查 c5
    c5_ok = True
    panel_fails_len = len(panel_fails) if isinstance(panel_fails, list) else -1
    panel_mismatches_len = len(panel_mismatches) if isinstance(panel_mismatches, list) else -1
    if status_fail > 0 or panel_fails_len != 0 or panel_mismatches_len != 0:
        c5_ok = False

    # 判读
    fails = sum([not c0_ok, not c1_ok, not c2_ok, not c3_ok, not c4_ok, not c5_ok])
    verdict = "MATCH" if fails == 0 else f"MISMATCH fails={fails}"

    return {
        "lines": len(cells_lines),
        "blank": blank,
        "malformed": malformed,
        "valid": valid,
        "codes_unique": codes_unique_count,
        "dup_codes": dup_codes_count,
        "kind_live": kind_live,
        "kind_extra": kind_extra,
        "kind_other": kind_other,
        "status_ok": status_ok,
        "status_fail": status_fail,
        "appended_sum": appended_sum,
        "pass": pass_render,
        "c0_malformed": malformed,
        "c1_count_valid": valid,
        "c1_count_attempted": panel_attempted,
        "c2_universe_codes_unique": codes_unique_count,
        "c2_universe_universe": panel_universe,
        "c3_pass_cells_pass": pass_render,
        "c3_pass_panel_pass": panel_last_pass_date,
        "c4_appended_cells": appended_sum,
        "c4_appended_panel": panel_appended,
        "c5_status_cells_fail": status_fail,
        "c5_status_panel_fails": panel_fails_len,
        "c5_status_panel_mismatches": panel_mismatches_len,
        "c0_ok": c0_ok,
        "c1_ok": c1_ok,
        "c2_ok": c2_ok,
        "c3_ok": c3_ok,
        "c4_ok": c4_ok,
        "c5_ok": c5_ok,
        "verdict": verdict,
        "fails": fails
    }

def run_selftest():
    # 样例一：对齐面，5 行全 ok
    cells1 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok","appended":1}',
        '{"code":"b","pass":"2024-01-01","kind":"live","status":"ok","appended":1}',
        '{"code":"c","pass":"2024-01-01","kind":"extra","status":"ok","appended":0}',
        '{"code":"d","pass":"2024-01-01","kind":"extra","status":"ok","appended":0}',
        '{"code":"e","pass":"2024-01-01","kind":"extra","status":"ok","appended":1}'
    ]
    panel1 = '{"universe":5,"attempted":5,"appended":3,"last_pass_date":"2024-01-01","fails":[],"mismatches":[]}'
    result1 = recon(cells1, panel1)
    expected1 = {
        "lines": 5,
        "blank": 0,
        "malformed": 0,
        "valid": 5,
        "codes_unique": 5,
        "dup_codes": 0,
        "kind_live": 2,
        "kind_extra": 3,
        "kind_other": 0,
        "status_ok": 5,
        "status_fail": 0,
        "appended_sum": 3,
        "pass": "2024-01-01",
        "c0_malformed": 0,
        "c1_count_valid": 5,
        "c1_count_attempted": 5,
        "c2_universe_codes_unique": 5,
        "c2_universe_universe": 5,
        "c3_pass_cells_pass": "2024-01-01",
        "c3_pass_panel_pass": "2024-01-01",
        "c4_appended_cells": 3,
        "c4_appended_panel": 3,
        "c5_status_cells_fail": 0,
        "c5_status_panel_fails": 0,
        "c5_status_panel_mismatches": 0,
        "c0_ok": True,
        "c1_ok": True,
        "c2_ok": True,
        "c3_ok": True,
        "c4_ok": True,
        "c5_ok": True,
        "verdict": "MATCH",
        "fails": 0
    }
    assert all(result1[k] == expected1[k] for k in expected1), f"Sample 1 failed: {result1}"

    # 样例二：计数缺口
    cells2 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok"}',
        '{"code":"b","pass":"2024-01-01","kind":"extra","status":"ok"}',
        '{"code":"c","pass":"2024-01-01","kind":"extra","status":"ok"}',
        '{"code":"d","pass":"2024-01-01","kind":"extra","status":"ok"}'
    ]
    panel2 = '{"universe":4,"attempted":5,"appended":0,"last_pass_date":"2024-01-01","fails":[],"mismatches":[]}'
    result2 = recon(cells2, panel2)
    assert result2["c1_ok"] == False and result2["verdict"] == "MISMATCH fails=1", f"Sample 2 failed: {result2}"

    # 样例三：重复 code
    cells3 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok"}',
        '{"code":"b","pass":"2024-01-01","kind":"extra","status":"ok"}',
        '{"code":"c","pass":"2024-01-01","kind":"extra","status":"ok"}',
        '{"code":"a","pass":"2024-01-01","kind":"extra","status":"ok"}'
    ]
    panel3 = '{"universe":4,"attempted":4,"appended":0,"last_pass_date":"2024-01-01","fails":[],"mismatches":[]}'
    result3 = recon(cells3, panel3)
    assert result3["c2_ok"] == False and result3["dup_codes"] == 1 and result3["verdict"] == "MISMATCH fails=1", f"Sample 3 failed: {result3}"

    # 样例四：pass 双值
    cells4 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok"}',
        '{"code":"b","pass":"2024-01-02","kind":"extra","status":"ok"}'
    ]
    panel4 = '{"universe":2,"attempted":2,"appended":0,"last_pass_date":"2024-01-01","fails":[],"mismatches":[]}'
    result4 = recon(cells4, panel4)
    assert result4["pass"] == "MULTI" and result4["c3_ok"] == False and result4["verdict"] == "MISMATCH fails=1", f"Sample 4 failed: {result4}"

    # 样例五：appended 缺口 + status 面
    cells5 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok","appended":1}',
        '{"code":"b","pass":"2024-01-01","kind":"extra","status":"ok","appended":1}',
        '{"code":"c","pass":"2024-01-01","kind":"extra","status":"fail","appended":1}'
    ]
    panel5 = '{"universe":3,"attempted":3,"appended":2,"last_pass_date":"2024-01-01","fails":["10011425"],"mismatches":[]}'
    result5 = recon(cells5, panel5)
    assert result5["c4_ok"] == False and result5["c5_ok"] == False and result5["verdict"] == "MISMATCH fails=2", f"Sample 5 failed: {result5}"

    # 边界/违规族
    cells6 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok"}',
        '{"code":5,"pass":"2024-01-01","kind":"extra","status":"ok"}',  # code 非 str
        '{"code":"b","pass":"2024-01-01","kind":"extra","status":"ok"}',
        '{"code":"c","pass":"2024-01-01","kind":"extra","status":"ok"}',
        '{"code":"d","pass":"2024-01-01","kind":"extra","status":"ok"}'
    ]
    panel6 = '{"universe":4,"attempted":4,"appended":0,"last_pass_date":"2024-01-01","fails":[],"mismatches":[]}'
    result6 = recon(cells6, panel6)
    assert result6["malformed"] == 1 and result6["valid"] == 3, f"Sample 6 failed: {result6}"

    cells7 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok"}',
        '{"code":"b","pass":"2024-01-01","kind":"extra","status":"ok"}'
    ]
    panel7 = '{"universe":4,"attempted":2,"appended":0,"last_pass_date":"2024-01-01","fails":[],"mismatches":[]}'
    result7 = recon(cells7, panel7)
    assert result7["c1_ok"] == True and result7["c2_ok"] == False, f"Sample 7 failed: {result7}"

    print("ALL PASS")
    return 0

def main():
    if len(sys.argv) == 1:
        print("Usage: python scripts/opt_cells_recon.py [results_dir]")
        sys.exit(2)
    elif sys.argv[1] == "selftest":
        run_selftest()
        sys.exit(0)
    else:
        results_dir = sys.argv[1]
        if not os.path.isdir(results_dir):
            print(f"Error: {results_dir} is not a directory")
            sys.exit(2)

        cells_file = os.path.join(results_dir, "options_update_cells.jsonl")
        status_file = os.path.join(results_dir, "options_update_status.json")

        try:
            with open(cells_file, "r", encoding="utf-8-sig") as f:
                cells_lines = [line.rstrip('\n') for line in f]
        except Exception as e:
            print(f"Error reading {cells_file}: {e}")
            sys.exit(2)

        try:
            with open(status_file, "r", encoding="utf-8-sig") as f:
                panel_text = f.read()
        except Exception as e:
            print(f"Error reading {status_file}: {e}")
            sys.exit(2)

        result = recon(cells_lines, panel_text)

        # 输出头行
        print(
            f"RECON lines={result['lines']} blank={result['blank']} malformed={result['malformed']} "
            f"valid={result['valid']} codes_unique={result['codes_unique']} dup_codes={result['dup_codes']} "
            f"kind_live={result['kind_live']} kind_extra={result['kind_extra']} kind_other={result['kind_other']} "
            f"status_ok={result['status_ok']} status_fail={result['status_fail']} appended_sum={result['appended_sum']} "
            f"pass={result['pass']}"
        )

        # 输出检查行
        print(f"CHECK c0_malformed malformed={result['c0_malformed']} ok={1 if result['c0_ok'] else 0}")
        print(f"CHECK c1_count valid={result['c1_count_valid']} attempted={result['c1_count_attempted']} ok={1 if result['c1_ok'] else 0}")
        print(f"CHECK c2_universe codes_unique={result['c2_universe_codes_unique']} universe={result['c2_universe_universe']} ok={1 if result['c2_ok'] else 0}")
        print(f"CHECK c3_pass cells_pass={result['c3_pass_cells_pass']} panel_pass={result['c3_pass_panel_pass']} ok={1 if result['c3_ok'] else 0}")
        print(f"CHECK c4_appended cells={result['c4_appended_cells']} panel={result['c4_appended_panel']} ok={1 if result['c4_ok'] else 0}")
        print(f"CHECK c5_status cells_fail={result['c5_status_cells_fail']} panel_fails={result['c5_status_panel_fails']} panel_mismatches={result['c5_status_panel_mismatches']} ok={1 if result['c5_ok'] else 0}")

        # 输出判读行
        print(result["verdict"])

        # 判断 exit code
        if result["fails"] == 0:
            sys.exit(0)
        else:
            sys.exit(1)

if __name__ == "__main__":
    main()
```