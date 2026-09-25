import os
import sys
import re

def parse_options_log(text):
    if text is None:
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
            # progress line
            m = re.match(r'\[opt-refresh\] (\d+)/(\d+) appended=(\d+) fuse=(\d+)', line)
            if m:
                progress = f"{m.group(1)}/{m.group(2)}"
                appended = int(m.group(3))
                fuse = int(m.group(4))
            
            # census line
            m = re.match(r'\[opt-refresh\] enumerated=(\d+) disk=(\d+) extra_sweep=(\d+) sweep_skip=(\d+) ckpt_done=(\d+) pending=(\d+)', line)
            if m:
                pending = int(m.group(6))
            
            # done line
            m = re.match(r'\[opt-refresh\] done pass_ok=(True|False) appended=(\d+) mismatches=\[(.*)\] fails=\[(.*)\] last_pass=(.*)', line)
            if m:
                done_pass = m.group(1) == 'True'
                done_appended = int(m.group(2))
                done_mismatches = len(m.group(3).strip()) == 0 and 0 or m.group(3).count(',') + 1
                done_fails = len(m.group(4).strip()) == 0 and 0 or m.group(4).count(',') + 1
                last_pass = m.group(5)
            
            # fuse events
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

def parse_ah_log(text):
    if text is None:
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
        # done line
        m = re.match(r'refresh done: pairs=(\d+) done=(\d+) quarantined=(\d+) pulled_rows=(\d+) cutoff=(.*) complete=(True|False) exit=(\d+)', line)
        if m:
            pairs = int(m.group(1))
            done_pairs = int(m.group(2))
            quarantined = int(m.group(3))
            pulled_rows = int(m.group(4))
            cutoff = m.group(5)
            complete = m.group(6) == 'True'
            exit_code = int(m.group(7))
        
        # em_unavail
        if line.startswith('EM mapping unavailable:'):
            em_unavail += 1
        
        # fuse_stops
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

def parse_mf_log(text):
    if text is None:
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
        # done line
        m = re.match(r'refresh done: \+(\d+) rows, (\d+) failures, (\d+) mismatches, complete=(True|False), panel cutoff=(.*)', line)
        if m:
            rows = int(m.group(1))
            failures = int(m.group(2))
            mismatches = int(m.group(3))
            complete = m.group(4) == 'True'
            cutoff = m.group(5)
        
        # blocks
        if line.startswith('source-level block suspected'):
            blocks += 1
        
        # rank_fails
        if line.startswith('rank pass failed:'):
            rank_fails += 1
        
        # rank_pass_events
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

def digest(options_text, ah_text, mf_text):
    options = parse_options_log(options_text)
    ah = parse_ah_log(ah_text)
    mf = parse_mf_log(mf_text)
    
    lanes = {
        'options': options,
        'ah': ah,
        'mf': mf
    }
    
    def render_field(val):
        if val is None:
            return '-'
        elif isinstance(val, bool):
            return str(val).lower()
        else:
            return str(val)
    
    def render_lanes():
        lines = []
        
        # options
        o = lanes['options']
        lines.append(
            f"LANE options state={o['state']} progress={render_field(o['progress'])} appended={render_field(o['appended'])} fuse={render_field(o['fuse'])} pending={render_field(o['pending'])} fuse_events={render_field(o['fuse_events'])} done_pass={render_field(o['done_pass'])} done_appended={render_field(o['done_appended'])} done_mismatches={render_field(o['done_mismatches'])} done_fails={render_field(o['done_fails'])} last_pass={render_field(o['last_pass'])}"
        )
        
        # ah
        a = lanes['ah']
        lines.append(
            f"LANE ah state={a['state']} pairs={render_field(a['pairs'])} done_pairs={render_field(a['done_pairs'])} quarantined={render_field(a['quarantined'])} pulled_rows={render_field(a['pulled_rows'])} cutoff={render_field(a['cutoff'])} complete={render_field(a['complete'])} exit={render_field(a['exit'])} em_unavail={render_field(a['em_unavail'])} fuse_stops={render_field(a['fuse_stops'])}"
        )
        
        # mf
        m = lanes['mf']
        lines.append(
            f"LANE mf state={m['state']} rows={render_field(m['rows'])} failures={render_field(m['failures'])} mismatches={render_field(m['mismatches'])} complete={render_field(m['complete'])} cutoff={render_field(m['cutoff'])} blocks={render_field(m['blocks'])} rank_fails={render_field(m['rank_fails'])} rank_pass_events={render_field(m['rank_pass_events'])}"
        )
        
        # verdict
        ok_count = sum([
            o['done_pass'] is True if o['done_pass'] is not None else False,
            a['complete'] is True and a['exit'] == 0 if a['complete'] is not None else False,
            m['complete'] is True if m['complete'] is not None else False
        ])
        lines.append(f"VERDICT ok={ok_count}/3")
        
        return lines
    
    ok = sum([
        options['done_pass'] is True if options['done_pass'] is not None else False,
        ah['complete'] is True and ah['exit'] == 0 if ah['complete'] is not None else False,
        mf['complete'] is True if mf['complete'] is not None else False
    ])
    
    return {
        'lanes': lanes,
        'ok': ok,
        'lines': render_lanes()
    }

def selftest():
    # Test case 1: all ok
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
    assert result['ok'] == 3
    assert result['lanes']['options']['state'] == 'done'
    assert result['lanes']['ah']['state'] == 'done'
    assert result['lanes']['mf']['state'] == 'done'
    assert result['lanes']['options']['progress'] == '200/200'
    assert result['lanes']['options']['appended'] == 0
    assert result['lanes']['options']['fuse'] == 0
    assert result['lanes']['options']['pending'] == 200
    assert result['lanes']['options']['fuse_events'] == 1
    assert result['lanes']['options']['done_pass'] == True
    assert result['lanes']['options']['done_appended'] == 0
    assert result['lanes']['options']['done_mismatches'] == 0
    assert result['lanes']['options']['done_fails'] == 0
    assert result['lanes']['options']['last_pass'] == '2026-09-24'
    assert result['lanes']['ah']['pairs'] == 6
    assert result['lanes']['ah']['done_pairs'] == 6
    assert result['lanes']['ah']['quarantined'] == 0
    assert result['lanes']['ah']['pulled_rows'] == 1200
    assert result['lanes']['ah']['cutoff'] == '2026-09-24'
    assert result['lanes']['ah']['complete'] == True
    assert result['lanes']['ah']['exit'] == 0
    assert result['lanes']['ah']['em_unavail'] == 2
    assert result['lanes']['ah']['fuse_stops'] == 0
    assert result['lanes']['mf']['rows'] == 3600
    assert result['lanes']['mf']['failures'] == 3
    assert result['lanes']['mf']['mismatches'] == 0
    assert result['lanes']['mf']['complete'] == True
    assert result['lanes']['mf']['cutoff'] == '2026-09-24'
    assert result['lanes']['mf']['blocks'] == 1
    assert result['lanes']['mf']['rank_fails'] == 1
    assert result['lanes']['mf']['rank_pass_events'] == 0
    assert result['lines'][3] == 'VERDICT ok=3/3'
    
    # Test case 2: options in progress
    options_text = """[opt-refresh] pass target=2026-09-24 start 2026-09-26T01:00:00
[opt-refresh] enumerated=142 disk=200 extra_sweep=58 sweep_skip=0 ckpt_done=0 pending=200 months={'510050': ['202610', '202612', '202703'], '510300': ['202610', '202612', '202703']}
[opt-refresh] 50/200 appended=0 fuse=0"""
    
    result = digest(options_text, ah_text, mf_text)
    assert result['ok'] == 2
    assert result['lanes']['options']['state'] == 'in_progress'
    assert result['lanes']['options']['progress'] == '50/200'
    assert result['lanes']['options']['done_pass'] is None
    assert result['lanes']['options']['done_appended'] is None
    assert result['lanes']['options']['done_mismatches'] is None
    assert result['lanes']['options']['done_fails'] is None
    assert result['lanes']['options']['last_pass'] is None
    assert result['lines'][3] == 'VERDICT ok=2/3'
    
    # Test case 3: mf failed
    mf_text = """rank pass failed: page 1: RemoteDisconnected -> exit 2 (nothing written)
source-level block suspected (3 consecutive connection failures) -- stopping, checkpoint intact, gate retries after throttle window
rank pass failed: page 1: RemoteDisconnected -> exit 2 (nothing written)
rank pass failed: page 1: RemoteDisconnected -> exit 2 (nothing written)
source-level block suspected (3 consecutive connection failures) -- stopping, checkpoint intact, gate retries after throttle window
rank pass 2026-09-25T23:15:00: +3600 rows, 3 same-day skips, 2 not in rank face, 1 not in universe, 0 mismatches
refresh done: +120 rows, 3 failures, 0 mismatches, complete=False, panel cutoff=2026-09-23"""
    
    result = digest(options_text, ah_text, mf_text)
    assert result['ok'] == 2
    assert result['lanes']['mf']['state'] == 'done'
    assert result['lanes']['mf']['rows'] == 120
    assert result['lanes']['mf']['complete'] is False
    assert result['lanes']['mf']['cutoff'] == '2026-09-23'
    assert result['lanes']['mf']['blocks'] == 2
    assert result['lanes']['mf']['rank_fails'] == 3
    assert result['lanes']['mf']['rank_pass_events'] == 1
    assert result['lines'][3] == 'VERDICT ok=2/3'
    
    # Test case 4: all missing
    result = digest(None, None, None)
    assert result['ok'] == 0
    assert result['lanes']['options']['state'] == 'missing'
    assert result['lanes']['ah']['state'] == 'missing'
    assert result['lanes']['mf']['state'] == 'missing'
    assert result['lines'][3] == 'VERDICT ok=0/3'
    
    # Test case 5: options done with mismatch/fail
    options_text = """[opt-refresh] pass target=2026-09-24 start 2026-09-26T01:00:00
[opt-refresh] 200/200 appended=0 fuse=0
[opt-refresh] done pass_ok=True appended=0 mismatches=['a', 'b'] fails=['c'] last_pass=2026-09-24"""
    
    result = digest(options_text, ah_text, mf_text)
    assert result['lanes']['options']['done_mismatches'] == 2
    assert result['lanes']['options']['done_fails'] == 1
    
    # Test case 6: options done with last_pass=None
    options_text = """[opt-refresh] pass target=2026-09-24 start 2026-09-26T01:00:00
[opt-refresh] 200/200 appended=0 fuse=0
[opt-refresh] done pass_ok=True appended=0 mismatches=[] fails=[] last_pass=None"""
    
    result = digest(options_text, ah_text, mf_text)
    assert result['lanes']['options']['last_pass'] == 'None'
    
    # Test case 7: options empty lines only
    options_text = """   
   """
    
    result = digest(options_text, ah_text, mf_text)
    assert result['lanes']['options']['state'] == 'empty'
    assert result['lanes']['options']['fuse_events'] == 0
    
    # Test case 8: ah done with exit != 0
    ah_text = """refresh done: pairs=6 done=6 quarantined=0 pulled_rows=1200 cutoff=2026-09-24 complete=True exit=3"""
    
    result = digest(options_text, ah_text, mf_text)
    assert result['lanes']['ah']['state'] == 'done'
    assert result['lanes']['ah']['complete'] is True
    assert result['lanes']['ah']['exit'] == 3
    assert result['ok'] == 2
    
    # Test case 9: ah only em_unavail lines
    ah_text = """EM mapping unavailable: em page 1: RemoteDisconnected: Remote end closed connection without response
EM mapping unavailable: em page 1: RemoteDisconnected: Remote end closed connection without response
EM mapping unavailable: em page 1: RemoteDisconnected: Remote end closed connection without response"""
    
    result = digest(options_text, ah_text, mf_text)
    assert result['lanes']['ah']['state'] == 'in_progress'
    assert result['lanes']['ah']['done_pairs'] is None
    assert result['lanes']['ah']['em_unavail'] == 3
    
    # Test case 10: options multiple done lines (last wins)
    options_text = """[opt-refresh] pass target=2026-09-24 start 2026-09-26T01:00:00
[opt-refresh] 200/200 appended=0 fuse=0
[opt-refresh] done pass_ok=False appended=0 mismatches=[] fails=[] last_pass=2026-09-24
[opt-refresh] done pass_ok=True appended=0 mismatches=[] fails=[] last_pass=2026-09-24"""
    
    result = digest(options_text, ah_text, mf_text)
    assert result['lanes']['options']['done_pass'] is True
    
    # Test case 11: options multiple fuse lines
    options_text = """[opt-refresh] pass target=2026-09-24 start 2026-09-26T01:00:00
[opt-refresh] 200/200 appended=0 fuse=0
[opt-refresh] conn-fuse: 3 consecutive fails, stop
[opt-refresh] conn-fuse: 3 consecutive fails, stop"""
    
    result = digest(options_text, ah_text, mf_text)
    assert result['lanes']['options']['fuse_events'] == 2
    
    # Test case 12: ah complete=False
    ah_text = """refresh done: pairs=6 done=6 quarantined=0 pulled_rows=1200 cutoff=2026-09-24 complete=False exit=0"""
    
    result = digest(options_text, ah_text, mf_text)
    assert result['lanes']['ah']['complete'] is False
    assert result['ok'] == 2
    
    # Test case 13: mf cutoff=None
    mf_text = """refresh done: +3600 rows, 3 failures, 0 mismatches, complete=True, panel cutoff=None"""
    
    result = digest(options_text, ah_text, mf_text)
    assert result['lanes']['mf']['cutoff'] == 'None'
    
    print("ALL PASS")
    return True

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "selftest":
            selftest()
            return
        elif len(sys.argv) != 2:
            print("Usage: python scripts/lane_log_digest.py [logs_dir]")
            sys.exit(2)
        logs_dir = sys.argv[1]
    else:
        logs_dir = "logs"
    
    if not os.path.isdir(logs_dir):
        print(f"Error: {logs_dir} is not a directory", file=sys.stderr)
        sys.exit(2)
    
    files = ["options_refresh.log", "ah_refresh.log", "moneyflow_refresh.log"]
    texts = []
    
    for f in files:
        path = os.path.join(logs_dir, f)
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as fd:
                text = fd.read()
        except Exception:
            text = None
        texts.append(text)
    
    result = digest(*texts)
    for line in result['lines']:
        print(line)
    
    if result['ok'] == 3:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
