```python
import sys
import os
import json
import re

def recon(cells_lines, panel_text):
    # 解析 panel
    try:
        panel = json.loads(panel_text)
    except:
        panel = {}
    
    def get_panel_int(key, default=-1):
        val = panel.get(key)
        if isinstance(val, int):
            return val
        else:
            return default
    
    def get_panel_str(key, default="-"):
        val = panel.get(key)
        if isinstance(val, str):
            return val
        else:
            return default
    
    def get_panel_list(key, default=[]):
        val = panel.get(key)
        if isinstance(val, list):
            return val
        else:
            return default

    # 初始化计数器
    blank = 0
    malformed = 0
    valid = 0
    codes_unique = set()
    dup_codes = 0
    kind_live = 0
    kind_extra = 0
    kind_other = 0
    status_ok = 0
    status_fail = 0
    appended_sum = 0
    pass_set = set()

    # 解析 cells 行
    for line in cells_lines:
        stripped = line.strip()
        if not stripped:
            blank += 1
            continue

        try:
            obj = json.loads(stripped)
        except:
            malformed += 1
            continue

        if not isinstance(obj, dict):
            malformed += 1
            continue

        # 验证字段契约
        code = obj.get("code")
        if not isinstance(code, str) or not code:
            malformed += 1
            continue

        pass_val = obj.get("pass", "")
        kind = obj.get("kind", "")
        status = obj.get("status", "")

        # 验证字段类型
        if not isinstance(pass_val, str):
            malformed += 1
            continue
        if not isinstance(kind, str):
            malformed += 1
            continue
        if not isinstance(status, str):
            malformed += 1
            continue

        appended = obj.get("appended", 0)
        if not isinstance(appended, int):
            malformed += 1
            continue

        # 计数
        valid += 1
        codes_unique.add(code)
        pass_set.add(pass_val)
        appended_sum += appended

        # kind 分类
        if kind == "live":
            kind_live += 1
        elif kind == "extra":
            kind_extra += 1
        else:
            kind_other += 1

        # status 分类
        if status == "ok":
            status_ok += 1
        else:
            status_fail += 1

    codes_unique_count = len(codes_unique)
    dup_codes_count = sum(1 for c in codes_unique if [x for x in cells_lines if json.loads(x.strip()).get("code") == c].count(c) > 1)

    # pass 渲染
    if len(pass_set) == 0:
        render_pass = "-"
    elif len(pass_set) == 1:
        render_pass = list(pass_set)[0]
    else:
        render_pass = "MULTI"

    # 对账检查
    attempted = get_panel_int("attempted")
    universe = get_panel_int("universe")
    appended = get_panel_int("appended")
    last_pass_date = get_panel_str("last_pass_date")
    fails = get_panel_list("fails")
    mismatches = get_panel_list("mismatches")

    c0_malformed_ok = (malformed == 0)
    c1_count_ok = (valid == attempted) if attempted != -1 else False
    c2_universe_ok = (codes_unique_count == universe) if universe != -1 else False
    c3_pass_ok = (render_pass == last_pass_date) if last_pass_date != "-" and render_pass not in ["MULTI", "-"] else False
    c4_appended_ok = (appended_sum == appended) if appended != -1 else False
    c5_status_ok = (status_fail == 0 and len(fails) == 0 and len(mismatches) == 0)

    # 检查失败数
    fails_count = sum(1 for ok in [c0_malformed_ok, c1_count_ok, c2_universe_ok, c3_pass_ok, c4_appended_ok, c5_status_ok] if not ok)

    # 构造输出
    output = {
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
        "pass": render_pass,
        "c0_malformed": malformed,
        "c1_count_valid": valid,
        "c1_count_attempted": attempted,
        "c2_universe_codes_unique": codes_unique_count,
        "c2_universe_universe": universe,
        "c3_pass_cells_pass": render_pass,
        "c3_pass_panel_pass": last_pass_date,
        "c4_appended_cells": appended_sum,
        "c4_appended_panel": appended,
        "c5_status_cells_fail": status_fail,
        "c5_status_panel_fails": len(fails),
        "c5_status_panel_mismatches": len(mismatches),
        "c0_malformed_ok": c0_malformed_ok,
        "c1_count_ok": c1_count_ok,
        "c2_universe_ok": c2_universe_ok,
        "c3_pass_ok": c3_pass_ok,
        "c4_appended_ok": c4_appended_ok,
        "c5_status_ok": c5_status_ok,
        "verdict": "MATCH" if fails_count == 0 else f"MISMATCH fails={fails_count}"
    }

    return output

def selftest():
    # 测试样例一：对齐面
    cells1 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok","appended":1}',
        '{"code":"b","pass":"2024-01-01","kind":"live","status":"ok","appended":1}',
        '{"code":"c","pass":"2024-01-01","kind":"extra","status":"ok","appended":0}',
        '{"code":"d","pass":"2024-01-01","kind":"extra","status":"ok","appended":0}',
        '{"code":"e","pass":"2024-01-01","kind":"extra","status":"ok","appended":1}'
    ]
    panel1 = '{"universe":5,"attempted":5,"appended":3,"last_pass_date":"2024-01-01","fails":[],"mismatches":[]}'
    result1 = recon(cells1, panel1)
    assert result1["lines"] == 5
    assert result1["blank"] == 0
    assert result1["malformed"] == 0
    assert result1["valid"] == 5
    assert result1["codes_unique"] == 5
    assert result1["dup_codes"] == 0
    assert result1["kind_live"] == 2
    assert result1["kind_extra"] == 3
    assert result1["kind_other"] == 0
    assert result1["status_ok"] == 5
    assert result1["status_fail"] == 0
    assert result1["appended_sum"] == 3
    assert result1["pass"] == "2024-01-01"
    assert result1["c0_malformed_ok"]
    assert result1["c1_count_ok"]
    assert result1["c2_universe_ok"]
    assert result1["c3_pass_ok"]
    assert result1["c4_appended_ok"]
    assert result1["c5_status_ok"]
    assert result1["verdict"] == "MATCH"

    # 测试样例二：计数缺口
    cells2 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok"}',
        '{"code":"b","pass":"2024-01-01","kind":"extra","status":"ok"}',
        '{"code":"c","pass":"2024-01-01","kind":"extra","status":"ok"}',
        '{"code":"d","pass":"2024-01-01","kind":"extra","status":"ok"}'
    ]
    panel2 = '{"universe":4,"attempted":5,"appended":0,"last_pass_date":"2024-01-01","fails":[],"mismatches":[]}'
    result2 = recon(cells2, panel2)
    assert not result2["c1_count_ok"]
    assert result2["verdict"] == "MISMATCH fails=1"

    # 测试样例三：重复 code
    cells3 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok"}',
        '{"code":"b","pass":"2024-01-01","kind":"extra","status":"ok"}',
        '{"code":"c","pass":"2024-01-01","kind":"extra","status":"ok"}',
        '{"code":"a","pass":"2024-01-01","kind":"extra","status":"ok"}'
    ]
    panel3 = '{"universe":4,"attempted":4,"appended":0,"last_pass_date":"2024-01-01","fails":[],"mismatches":[]}'
    result3 = recon(cells3, panel3)
    assert result3["c1_count_ok"]
    assert not result3["c2_universe_ok"]
    assert result3["dup_codes"] == 1
    assert result3["verdict"] == "MISMATCH fails=1"

    # 测试样例四：pass 双值
    cells4 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok"}',
        '{"code":"b","pass":"2024-01-02","kind":"extra","status":"ok"}'
    ]
    panel4 = '{"universe":2,"attempted":2,"appended":0,"last_pass_date":"2024-01-01","fails":[],"mismatches":[]}'
    result4 = recon(cells4, panel4)
    assert result4["pass"] == "MULTI"
    assert not result4["c3_pass_ok"]
    assert result4["verdict"] == "MISMATCH fails=1"

    # 测试样例五：appended 缺口 + status 面
    cells5 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok","appended":1}',
        '{"code":"b","pass":"2024-01-01","kind":"extra","status":"ok","appended":1}',
        '{"code":"c","pass":"2024-01-01","kind":"extra","status":"fail","appended":1}'
    ]
    panel5 = '{"universe":3,"attempted":3,"appended":2,"last_pass_date":"2024-01-01","fails":["10011425"],"mismatches":[]}'
    result5 = recon(cells5, panel5)
    assert not result5["c4_appended_ok"]
    assert not result5["c5_status_ok"]
    assert result5["verdict"] == "MISMATCH fails=2"

    # 边界/违规族
    # ① 空白行
    cells6 = [
        '   ',
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok"}'
    ]
    panel6 = '{"universe":1,"attempted":1,"appended":0,"last_pass_date":"2024-01-01","fails":[],"mismatches":[]}'
    result6 = recon(cells6, panel6)
    assert result6["blank"] == 1
    assert result6["malformed"] == 0

    # ② "{not json"
    cells7 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok"}',
        '{not json'
    ]
    panel7 = '{"universe":1,"attempted":1,"appended":0,"last_pass_date":"2024-01-01","fails":[],"mismatches":[]}'
    result7 = recon(cells7, panel7)
    assert result7["malformed"] == 1

    # ③ "[1,2]" 非 dict
    cells8 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok"}',
        '[1,2]'
    ]
    panel8 = '{"universe":1,"attempted":1,"appended":0,"last_pass_date":"2024-01-01","fails":[],"mismatches":[]}'
    result8 = recon(cells8, panel8)
    assert result8["malformed"] == 1

    # ④ dict 缺 code 键
    cells9 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok"}',
        '{"pass":"2024-01-01","kind":"extra","status":"ok"}'
    ]
    panel9 = '{"universe":1,"attempted":1,"appended":0,"last_pass_date":"2024-01-01","fails":[],"mismatches":[]}'
    result9 = recon(cells9, panel9)
    assert result9["malformed"] == 1

    # ⑤ code 非 str（int 5）
    cells10 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok"}',
        '{"code":5,"pass":"2024-01-01","kind":"extra","status":"ok"}'
    ]
    panel10 = '{"universe":1,"attempted":1,"appended":0,"last_pass_date":"2024-01-01","fails":[],"mismatches":[]}'
    result10 = recon(cells10, panel10)
    assert result10["malformed"] == 1

    # ⑥ appended 为 str "1"
    cells11 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok","appended":"1"}'
    ]
    panel11 = '{"universe":1,"attempted":1,"appended":0,"last_pass_date":"2024-01-01","fails":[],"mismatches":[]}'
    result11 = recon(cells11, panel11)
    assert result11["malformed"] == 1

    # ⑦ panel.universe 缺席
    cells12 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok"}'
    ]
    panel12 = '{"attempted":1,"appended":0,"last_pass_date":"2024-01-01","fails":[],"mismatches":[]}'
    result12 = recon(cells12, panel12)
    assert not result12["c2_universe_ok"]

    # ⑧ panel.last_pass_date 缺席
    cells13 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok"}'
    ]
    panel13 = '{"universe":1,"attempted":1,"appended":0,"fails":[],"mismatches":[]}'
    result13 = recon(cells13, panel13)
    assert not result13["c3_pass_ok"]

    # ⑨ 全行 malformed（0 valid）
    cells14 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok"}',
        '{not json'
    ]
    panel14 = '{"universe":1,"attempted":1,"appended":0,"last_pass_date":"2024-01-01","fails":[],"mismatches":[]}'
    result14 = recon(cells14, panel14)
    assert result14["valid"] == 0
    assert result14["pass"] == "-"
    assert not result14["c3_pass_ok"]
    assert not result14["c1_count_ok"]

    # ⑩ panel.fails 缺席
    cells15 = [
        '{"code":"a","pass":"2024-01-01","kind":"live","status":"ok"}'
    ]
    panel15 = '{"universe":1,"attempted":1,"appended":0,"last_pass_date":"2024-01-01"}'
    result15 = recon(cells15, panel15)
    assert not result15["c5_status_ok"]

    print("ALL PASS")
    return 0

def main():
    if len(sys.argv) == 1:
        print("Usage: python opt_cells_recon.py [results_dir]")
        sys.exit(2)
    elif sys.argv[1] == "selftest":
        selftest()
        sys.exit(0)
    else:
        results_dir = sys.argv[1] if len(sys.argv) > 1 else "results"
        if not os.path.isdir(results_dir):
            print("Error: results_dir does not exist or is not a directory")
            sys.exit(2)

        cells_file = os.path.join(results_dir, "options_update_cells.jsonl")
        status_file = os.path.join(results_dir, "options_update_status.json")

        try:
            with open(cells_file, 'r', encoding='utf-8-sig') as f:
                cells_lines = [line.rstrip('\n') for line in f]
        except Exception as e:
            print("Error reading cells file")
            sys.exit(2)

        try:
            with open(status_file, 'r', encoding='utf-8-sig') as f:
                panel_text = f.read()
        except Exception as e:
            print("Error reading status file")
            sys.exit(2)

        result = recon(cells_lines, panel_text)

        # 输出头行
        print(f"RECON lines={result['lines']} blank={result['blank']} malformed={result['malformed']} valid={result['valid']} codes_unique={result['codes_unique']} dup_codes={result['dup_codes']} kind_live={result['kind_live']} kind_extra={result['kind_extra']} kind_other={result['kind_other']} status_ok={result['status_ok']} status_fail={result['status_fail']} appended_sum={result['appended_sum']} pass={result['pass']}")

        # 输出检查行
        print(f"CHECK c0_malformed malformed={result['c0_malformed']} ok={1 if result['c0_malformed_ok'] else 0}")
        print(f"CHECK c1_count valid={result['c1_count_valid']} attempted={result['c1_count_attempted']} ok={1 if result['c1_count_ok'] else 0}")
        print(f"CHECK c2_universe codes_unique={result['c2_universe_codes_unique']} universe={result['c2_universe_universe']} ok={1 if result['c2_universe_ok'] else 0}")
        print(f"CHECK c3_pass cells_pass={result['c3_pass_cells_pass']} panel_pass={result['c3_pass_panel_pass']} ok={1 if result['c3_pass_ok'] else 0}")
        print(f"CHECK c4_appended cells={result['c4_appended_cells']} panel={result['c4_appended_panel']} ok={1 if result['c4_appended_ok'] else 0}")
        print(f"CHECK c5_status cells_fail={result['c5_status_cells_fail']} panel_fails={result['c5_status_panel_fails']} panel_mismatches={result['c5_status_panel_mismatches']} ok={1 if result['c5_status_ok'] else 0}")

        # 输出判读行
        print(result['verdict'])

        # 判断退出码
        if result['verdict'].startswith("MATCH"):
            sys.exit(0)
        else:
            sys.exit(1)

if __name__ == "__main__":
    main()
```