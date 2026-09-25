# r229 bm-a: state flip only (report line already landed; state file has BOM -> utf-8-sig both ways, BOM preserved on write)
import json, io, time

st = json.load(io.open('state-bm-a.json', encoding='utf-8-sig'))
assert st.get('round_no') == 228, f"unexpected round_no {st.get('round_no')} -- refuse double-flip"
st['round_no'] = 229
st['did'] = ("R229: T-72 s2 first-pull supervision R2 (3782/5228 @07:21, PID 29132 alive, zero failures, rate 22.2/min, ETA ~08:26; "
             "acceptance RUN turnkey lands pull-completion round ~R236; s3 wiring follows PASS only) + S6 weekend chain 17 legs all green "
             "(audit CLEAN, probe py_low_board_clear legal idle, cutoff 09-24, regime ORANGE d3 shadow, MF/AH known EM-block 30min self-heal churn, "
             "blf 5222 all_pass, paper family gated off no-new-bar, scorecard+dashboard refreshed, token delta=0) + orders 74/74 round-start scan zero-diff + "
             "decisions no new lines + smoke 25/25")
st['verdict'] = 'GREEN'
st['next'] = ("acceptance RUN at pull completion ~08:26 (python scripts/sina_mf_accept.py run -> exit 0=PASS/1=FAIL/2=machinery; artifact results/sina_mf_accept.json) "
              "then s3 S6 wiring (consumer rule: main-force aggregate display must use official r0+r1 recipe per R225); "
              "09-28 Monday new-bar full-chain relay; 10-01 month-boundary trio + REGIME_GUARD v3 date gate; T-70 midterm 10-09")
ts = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
st['ts'] = ts
st['last_round_ts'] = st.get('updated_at', ts)
st['updated_at'] = ts
st['current_task'] = 'r229 done: s2 pull supervised healthy (3782/5228 @07:21, ETA ~08:26); acceptance RUN at pull-completion round'
st['last_run'] = time.strftime('%Y-%m-%d %H:%M:%S')
st['last_round_at'] = ts
with io.open('state-bm-a.json', 'w', encoding='utf-8-sig', newline='') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")
print('state round_no ->', st['round_no'], 'ts', ts)
