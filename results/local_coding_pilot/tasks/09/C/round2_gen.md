```python
import os
import sys
import re

# === 解析函数 ===
def digest(options_text, ah_text, mf_text):
    lanes = {}
    ok_count = 0

    def parse_options(text):
        if not text:
            return {'state': 'missing'}
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return {'state': 'empty'}

        progress = None
        appended = None
        fuse = None
        pending = None
        done_pass = None
        done_appended = None
        done_mismatches = None
        done_fails = None
        last_pass = None
        fuse_events = 0

        for line in lines:
            if line.startswith('[opt-refresh] '):
                # progress 行
                m = re.match(r'\[opt-refresh\] (\d+)/(\d+) appended=(\d+) fuse=(\d+)', line)
                if m:
                    progress = f"{m.group(1)}/{m.group(2)}"
                    appended = int(m.group(3))
                    fuse = int(m.group(4))

                # census 行
                m = re.match(r'\[opt-refresh\] enumerated=(\d+) disk=(\d+) extra_sweep=(\d+) sweep_skip=(\d+) ckpt_done=(\d+) pending=(\d+)', line)
                if m:
                    pending = int(m.group(6))

                # done 行
                m = re.match(r'\[opt-refresh\] done pass_ok=(True|False) appended=(\d+) mismatches=\[(.*)\] fails=\[(.*)\] last_pass=(.*)', line)
                if m:
                    done_pass = m.group(1) == 'True'
                    done_appended = int(m.group(2))
                    # 计算列表元素数
                    mismatches_str = m.group(3).strip()
                    done_mismatches = len(mismatches_str) > 0 and len(mismatches_str.split(',')) or 0
                    fails_str = m.group(4).strip()
                    done_fails = len(fails_str) > 0 and len(fails_str.split(',')) or 0
                    last_pass = m.group(5)

                # fuse_events 行
                if line.startswith('[opt-refresh] conn-fuse:'):
                    fuse_events += 1

        state = 'done' if done_pass is not None else 'in_progress'
        return {
            'state': state,
            'progress': progress,
            'appended': appended,
            'fuse': fuse,
            'pending': pending,
            'fuse_events': fuse_events,
            'done_pass': done_pass,
            'done_appended': done_appended,
            'done_mismatches': done_mismatches,
            'done_fails': done_fails,
            'last_pass': last_pass
        }

    def parse_ah(text):
        if not text:
            return {'state': 'missing'}
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return {'state': 'empty'}

        pairs = None
        done_pairs = None
        quarantined = None
        pulled_rows = None
        cutoff = None
        complete = None
        exit_code = None
        em_unavail = 0
        fuse_stops = 0

        for line in lines:
            # done 行
            m = re.match(r'refresh done: pairs=(\d+) done=(\d+) quarantined=(\d+) pulled_rows=(\d+) cutoff=(.*) complete=(True|False) exit=(\d+)', line)
            if m:
                pairs = int(m.group(1))
                done_pairs = int(m.group(2))
                quarantined = int(m.group(3))
                pulled_rows = int(m.group(4))
                cutoff = m.group(5)
                complete = m.group(6) == 'True'
                exit_code = int(m.group(7))

            # em_unavail 行
            if line.startswith('EM mapping unavailable:'):
                em_unavail += 1

            # fuse_stops 行
            if line.startswith('fuse stop at '):
                fuse_stops += 1

        state = 'done' if complete is not None else 'in_progress'
        return {
            'state': state,
            'pairs': pairs,
            'done_pairs': done_pairs,
            'quarantined': quarantined,
            'pulled_rows': pulled_rows,
            'cutoff': cutoff,
            'complete': complete,
            'exit': exit_code,
            'em_unavail': em_unavail,
            'fuse_stops': fuse_stops
        }

    def parse_mf(text):
        if not text:
            return {'state': 'missing'}
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return {'state': 'empty'}

        rows = None
        failures = None
        mismatches = None
        complete = None
        cutoff = None
        blocks = 0
        rank_fails = 0
        rank_pass_events = 0

        for line in lines:
            # done 行
            m = re.match(r'refresh done: \+(\d+) rows, (\d+) failures, (\d+) mismatches, complete=(True|False), panel cutoff=(.*)', line)
            if m:
                rows = int(m.group(1))
                failures = int(m.group(2))
                mismatches = int(m.group(3))
                complete = m.group(4) == 'True'
                cutoff = m.group(5)

            # blocks 行
            if line.startswith('source-level block suspected'):
                blocks += 1

            # rank_fails 行
            if line.startswith('rank pass failed:'):
                rank_fails += 1

            # rank_pass_events 行（排除失败行）
            if line.startswith('rank pass ') and not line.startswith('rank pass failed:'):
                rank_pass_events += 1

        state = 'done' if complete is not None else 'in_progress'
        return {
            'state': state,
            'rows': rows,
            'failures': failures,
            'mismatches': mismatches,
            'complete': complete,
            'cutoff': cutoff,
            'blocks': blocks,
            'rank_fails': rank_fails,
            'rank_pass_events': rank_pass_events
        }

    lanes['options'] = parse_options(options_text)
    lanes['ah'] = parse_ah(ah_text)
    lanes['mf'] = parse_mf(mf_text)

    # 判定 ok
    def is_ok(lane_name, lane_data):
        if lane_data['state'] != 'done':
            return False
        if lane_name == 'options':
            return lane_data['done_pass'] is True
        elif lane_name == 'ah':
            return lane_data['complete'] is True and lane_data['exit'] == 0
        elif lane_name == 'mf':
            return lane_data['complete'] is True
        return False

    for name in ['options', 'ah', 'mf']:
        if is_ok(name, lanes[name]):
            ok_count += 1

    # 构造输出行
    lines = []
    def render_field(key, value):
        if value is None:
            return '-'
        elif isinstance(value, bool):
            return str(value).lower()
        else:
            return str(value)

    for name in ['options', 'ah', 'mf']:
        data = lanes[name]
        state = data['state']
        if state == 'missing':
            lines.append(f"LANE {name} state={state} progress=- appended=- fuse=- pending=- fuse_events=- done_pass=- done_appended=- done_mismatches=- done_fails=- last_pass=-")
        elif state == 'empty':
            lines.append(f"LANE {name} state={state} progress=- appended=- fuse=- pending=- fuse_events=0 done_pass=- done_appended=- done_mismatches=- done_fails=- last_pass=-")
        else:
            if name == 'options':
                lines.append(f"LANE {name} state={state} progress={render_field('progress', data['progress'])} appended={render_field('appended', data['appended'])} fuse={render_field('fuse', data['fuse'])} pending={render_field('pending', data['pending'])} fuse_events={render_field('fuse_events', data['fuse_events'])} done_pass={render_field('done_pass', data['done_pass'])} done_appended={render_field('done_appended', data['done_appended'])} done_mismatches={render_field('done_mismatches', data['done_mismatches'])} done_fails={render_field('done_fails', data['done_fails'])} last_pass={render_field('last_pass', data['last_pass'])}")
            elif name == 'ah':
                lines.append(f"LANE {name} state={state} pairs={render_field('pairs', data['pairs'])} done_pairs={render_field('done_pairs', data['done_pairs'])} quarantined={render_field('quarantined', data['quarantined'])} pulled_rows={render_field('pulled_rows', data['pulled_rows'])} cutoff={render_field('cutoff', data['cutoff'])} complete={render_field('complete', data['complete'])} exit={render_field('exit', data['exit'])} em_unavail={render_field('em_unavail', data['em_unavail'])} fuse_stops={render_field('fuse_stops', data['fuse_stops'])}")
            elif name == 'mf':
                lines.append(f"LANE {name} state={state} rows={render_field('rows', data['rows'])} failures={render_field('failures', data['failures'])} mismatches={render_field('mismatches', data['mismatches'])} complete={render_field('complete', data['complete'])} cutoff={render_field('cutoff', data['cutoff'])} blocks={render_field('blocks', data['blocks'])} rank_fails={render_field('rank_fails', data['rank_fails'])} rank_pass_events={render_field('rank_pass_events', data['rank_pass_events'])}")

    lines.append(f"VERDICT ok={ok_count}/3")

    return {
        'lanes': lanes,
        'ok': ok_count,
        'lines': lines
    }

# === 自测函数 ===
def selftest():
    # 样例一：全 ok 三道
    options_text = """[opt-refresh] pass target=2026-09-24 start 2026-09-26T01:00:00
[opt-refresh] enumerated=142 disk=200 extra_sweep=58 sweep_skip=0 ckpt_done=0 pending=200 months={'510050': ['202610', '202612', '202703'], '510300': ['202610', '202612', '202703']}
[opt-refresh] 25/200 appended=0 fuse=0
[opt-refresh] 200/200 appended=0 fuse=0
[opt-refresh] conn-fuse: 3 consecutive fails, stop
[opt-refresh] done pass_ok=True appended=0 mismatches=[] fails=[] last_pass=2026-09-24"""
    ah_text = """EM mapping unavailable: em page 1: RemoteDisconnected: Remote end closed connection without response
EM mapping unavailable: em page 1: RemoteDisconnected: Remote end closed connection without response
refresh done: pairs=6 done=6 quarantined=0 pulled_rows=1200 cutoff=2026-09-24 complete=True exit=0"""
    mf_text = """rank pass failed: page 1: RemoteDisconnected -> exit 2 (nothing written)
source-level block suspected (3 consecutive connection failures) -- stopping, checkpoint intact, gate retries after throttle window
refresh done: +3600 rows, 3 failures, 0 mismatches, complete=True, panel cutoff=2026-09-24"""

    result = digest(options_text, ah_text, mf_text)
    expected_ok = 3
    assert result['ok'] == expected_ok, f"样例一：期望 ok={expected_ok}，实际={result['ok']}"

    # 检查字段值
    assert result['lanes']['options']['state'] == 'done'
    assert result['lanes']['options']['progress'] == "200/200"
    assert result['lanes']['options']['appended'] == 0
    assert result['lanes']['options']['fuse'] == 0
    assert result['lanes']['options']['pending'] == 200
    assert result['lanes']['options']['fuse_events'] == 1
    assert result['lanes']['options']['done_pass'] is True
    assert result['lanes']['options']['done_appended'] == 0
    assert result['lanes']['options']['done_mismatches'] == 0
    assert result['lanes']['options']['done_fails'] == 0
    assert result['lanes']['options']['last_pass'] == "2026-09-24"

    assert result['lanes']['ah']['state'] == 'done'
    assert result['lanes']['ah']['pairs'] == 6
    assert result['lanes']['ah']['done_pairs'] == 6
    assert result['lanes']['ah']['quarantined'] == 0
    assert result['lanes']['ah']['pulled_rows'] == 1200
    assert result['lanes']['ah']['cutoff'] == "2026-09-24"
    assert result['lanes']['ah']['complete'] is True
    assert result['lanes']['ah']['exit'] == 0
    assert result['lanes']['ah']['em_unavail'] == 2
    assert result['lanes']['ah']['fuse_stops'] == 0

    assert result['lanes']['mf']['state'] == 'done'
    assert result['lanes']['mf']['rows'] == 3600
    assert result['lanes']['mf']['failures'] == 3
    assert result['lanes']['mf']['mismatches'] == 0
    assert result['lanes']['mf']['complete'] is True
    assert result['lanes']['mf']['cutoff'] == "2026-09-24"
    assert result['lanes']['mf']['blocks'] == 1
    assert result['lanes']['mf']['rank_fails'] == 1
    assert result['lanes']['mf']['rank_pass_events'] == 0

    expected_lines = [
        "LANE options state=done progress=200/200 appended=0 fuse=0 pending=200 fuse_events=1 done_pass=true done_appended=0 done_mismatches=0 done_fails=0 last_pass=2026-09-24",
        "LANE ah state=done pairs=6 done_pairs=6 quarantined=0 pulled_rows=1200 cutoff=2026-09-24 complete=true exit=0 em_unavail=2 fuse_stops=0",
        "LANE mf state=done rows=3600 failures=3 mismatches=0 complete=true cutoff=2026-09-24 blocks=1 rank_fails=1 rank_pass_events=0",
        "VERDICT ok=3/3"
    ]
    assert result['lines'] == expected_lines, f"样例一：输出行不匹配"

    # 样例二：options 在途
    options_text = """[opt-refresh] pass target=2026-09-24 start 2026-09-26T01:00:00
[opt-refresh] enumerated=142 disk=200 extra_sweep=58 sweep_skip=0 ckpt_done=0 pending=200 months={'510050': ['202610', '202612', '202703'], '510300': ['202610', '202612', '202703']}
[opt-refresh] 50/200 appended=0 fuse=0"""
    ah_text = """EM mapping unavailable: em page 1: RemoteDisconnected: Remote end closed connection without response
EM mapping unavailable: em page 1: RemoteDisconnected: Remote end closed connection without response
refresh done: pairs=6 done=6 quarantined=0 pulled_rows=1200 cutoff=2026-09-24 complete=True exit=0"""
    mf_text = """rank pass failed: page 1: RemoteDisconnected -> exit 2 (nothing written)
source-level block suspected (3 consecutive connection failures) -- stopping, checkpoint intact, gate retries after throttle window
refresh done: +3600 rows, 3 failures, 0 mismatches, complete=True, panel cutoff=2026-09-24"""

    result = digest(options_text, ah_text, mf_text)
    assert result['ok'] == 2, f"样例二：期望 ok=2，实际={result['ok']}"
    assert result['lanes']['options']['state'] == 'in_progress'
    assert result['lanes']['options']['progress'] == "50/200"
    assert result['lanes']['options']['done_pass'] is None
    # 修正：确保输出行格式正确
    expected_line_0 = "LANE options state=in_progress progress=50/200 appended=- fuse=- pending=- fuse_events=0 done_pass=- done_appended=- done_mismatches=- done_fails=- last_pass=-"
    assert result['lines'][0] == expected_line_0
    assert result['lines'][3] == "VERDICT ok=2/3"

    # 样例三：mf 受阻
    options_text = """[opt-refresh] pass target=2026-09-24 start 2026-09-26T01:00:00
[opt-refresh] enumerated=142 disk=200 extra_sweep=58 sweep_skip=0 ckpt_done=0 pending=200 months={'510050': ['202610', '202612', '202703'], '510300': ['202610', '202612', '202703']}
[opt-refresh] 25/200 appended=0 fuse=0
[opt-refresh] 200/200 appended=0 fuse=0
[opt-refresh] conn-fuse: 3 consecutive fails, stop
[opt-refresh] done pass_ok=True appended=0 mismatches=[] fails=[] last_pass=2026-09-24"""
    ah_text = """EM mapping unavailable: em page 1: RemoteDisconnected: Remote end closed connection without response
EM mapping unavailable: em page 1: RemoteDisconnected: Remote end closed connection without response
refresh done: pairs=6 done=6 quarantined=0 pulled_rows=1200 cutoff=2026-09-24 complete=True exit=0"""
    mf_text = """rank pass failed: page 1: RemoteDisconnected -> exit 2 (nothing written)
rank pass failed: page 2: RemoteDisconnected -> exit 3 (nothing written)
rank pass failed: page 3: RemoteDisconnected -> exit 4 (nothing written)
source-level block suspected (3 consecutive connection failures) -- stopping, checkpoint intact, gate retries after throttle window
source-level block suspected (3 consecutive connection failures) -- stopping, checkpoint intact, gate retries after throttle window
rank pass 2026-09-25T23:15:00: +3600 rows, 3 same-day skips, 2 not in rank face, 1 not in universe, 0 mismatches
refresh done: +120 rows, 3 failures, 0 mismatches, complete=False, panel cutoff=2026-09-23"""

    result = digest(options_text, ah_text, mf_text)
    assert result['ok'] == 2, f"样例三：期望 ok=2，实际={result['ok']}"
    assert result['lanes']['mf']['state'] == 'done'
    assert result['lanes']['mf']['rows'] == 120
    assert result['lanes']['mf']['complete'] is False
    assert result['lanes']['mf']['cutoff'] == "2026-09-23"
    assert result['lanes']['mf']['blocks'] == 2
    assert result['lanes']['mf']['rank_fails'] == 3
    assert result['lanes']['mf']['rank_pass_events'] == 1
    assert result['lines'][3] == "VERDICT ok=2/3"

    # 样例四：三道 missing
    result = digest(None, None, None)
    assert result['ok'] == 0, f"样例四：期望 ok=0，实际={result['ok']}"
    assert result['lanes']['options']['state'] == 'missing'
    assert result['lanes']['ah']['state'] == 'missing'
    assert result['lanes']['mf']['state'] == 'missing'
    assert result['lines'][3] == "VERDICT ok=0/3"

    # 边界测试
    # ① options done 行 mismatches=['a', 'b'] fails=['c']
    options_text = """[opt-refresh] done pass_ok=True appended=0 mismatches=['a', 'b'] fails=['c'] last_pass=2026-09-24"""
    result = digest(options_text, None, None)
    assert result['lanes']['options']['done_mismatches'] == 2
    assert result['lanes']['options']['done_fails'] == 1

    # ② options done 行 last_pass=None
    options_text = """[opt-refresh] done pass_ok=True appended=0 mismatches=[] fails=[] last_pass=None"""
    result = digest(options_text, None, None)
    assert result['lanes']['options']['last_pass'] == "None"

    # ③ options 文本仅空白行（空串与空格行）
    options_text = """\n   \n\n"""
    result = digest(options_text, None, None)
    assert result['lanes']['options']['state'] == 'empty'
    assert result['lanes']['options']['fuse_events'] == 0

    # ④ ah done 行 complete=True exit=3 → state=done 但 ah 不 ok（exit≠0）
    ah_text = """refresh done: pairs=6 done=6 quarantined=0 pulled_rows=1200 cutoff=2026-09-24 complete=True exit=3"""
    result = digest(None, ah_text, None)
    assert result['lanes']['ah']['state'] == 'done'
    assert result['lanes']['ah']['complete'] is True
    assert result['lanes']['ah']['exit'] == 3
    assert result['ok'] == 0

    # ⑤ ah 文本仅 3 条 `EM mapping unavailable:` 行 → state=in_progress、done 系七字段=None、em_unavail=3
    ah_text = """EM mapping unavailable: em page 1: RemoteDisconnected: Remote end closed connection without response
EM mapping unavailable: em page 1: RemoteDisconnected: Remote end closed connection without response
EM mapping unavailable: em page 1: RemoteDisconnected: Remote end closed connection without response"""
    result = digest(None, ah_text, None)
    assert result['lanes']['ah']['state'] == 'in_progress'
    assert result['lanes']['ah']['done_pairs'] is None
    assert result['lanes']['ah']['em_unavail'] == 3

    # ⑥ options 两条 done 行（先 pass_ok=False 后 pass_ok=True）→ done_pass=True（最后一条胜）
    options_text = """[opt-refresh] done pass_ok=False appended=0 mismatches=[] fails=[] last_pass=2026-09-24
[opt-refresh] done pass_ok=True appended=0 mismatches=[] fails=[] last_pass=2026-09-24"""
    result = digest(options_text, None, None)
    assert result['lanes']['options']['done_pass'] is True

    # ⑦ options 两条 `[opt-refresh] conn-fuse:` 行 → fuse_events=2
    options_text = """[opt-refresh] conn-fuse: 3 consecutive fails, stop
[opt-refresh] conn-fuse: 3 consecutive fails, stop"""
    result = digest(options_text, None, None)
    assert result['lanes']['options']['fuse_events'] == 2

    # ⑧ ah done 行 complete=False → ah 不 ok
    ah_text = """refresh done: pairs=6 done=6 quarantined=0 pulled_rows=1200 cutoff=2026-09-24 complete=False exit=0"""
    result = digest(None, ah_text, None)
    assert result['lanes']['ah']['complete'] is False
    assert result['ok'] == 0

    # ⑨ mf done 行 panel cutoff=None → cutoff="None"
    mf_text = """refresh done: +120 rows, 3 failures, 0 mismatches, complete=True, panel cutoff=None"""
    result = digest(None, None, mf_text)
    assert result['lanes']['mf']['cutoff'] == "None"

    print("ALL PASS")
    return True

# === 主程序入口 ===
def main():
    if len(sys.argv) == 1:
        print("Usage: python scripts/lane_log_digest.py [logs_dir]")
        sys.exit(2)
    elif sys.argv[1] == 'selftest':
        selftest()
        sys.exit(0)
    elif len(sys.argv) > 1 and sys.argv[1] == 'live':
        logs_dir = sys.argv[2] if len(sys.argv) > 2 else "logs"
        if not os.path.isdir(logs_dir):
            print(f"Error: {logs_dir} is not a directory", file=sys.stderr)
            sys.exit(2)

        files = ["options_refresh.log", "ah_refresh.log", "moneyflow_refresh.log"]
        texts = []
        for f in files:
            path = os.path.join(logs_dir, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as fd:
                    texts.append(fd.read())
            except Exception:
                texts.append(None)

        result = digest(*texts)
        for line in result['lines']:
            print(line)
        sys.exit(0 if result['ok'] == 3 else 1)
    else:
        print("Usage: python scripts/lane_log_digest.py [logs_dir]")
        sys.exit(2)

if __name__ == "__main__":
    main()
```