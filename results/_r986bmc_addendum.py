import json, time
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
now_iso = datetime.now(CST).isoformat(timespec='seconds')

row = (f"{now_iso} | r986 addendum | PUSH-RACE closure: first push claw-blocked (range would delete bm-a faces -- "
       f"bm-a 20190b53e MF-collector-v3 absorb landed mid-window after my S0 fetch 0/0) -> fetch (behind 3) -> "
       f"stash-bridge rebase onto 5036a2f07 -> 2-file conflict resolved by machine-union "
       f"(compute_audit history 119+117->120 union-by-ts + latest newer-wins 06:11:32; token_usage base=newer "
       f"06:11:44 + machines mirror union; scripts results/_r986bmc_conflict_merge.py) -> continue refused twice "
       f"with clean UU index (r864 pit confirmation on bm-c: true blocker = satengine daemon re-wrote its own "
       f"faces post-add, MM unstaged; resolution = stage daemon newest writes live-wins, NOT checkout-discard) -> "
       f"rebase clean -> stash pop conflicted on same 2 faces (stale snapshots vs newer committed daemon writes) "
       f"-> r981 supersession-drop (checkout HEAD -- + stash drop, live-faces reproducible-class zero loss) -> "
       f"push LANDED 5036a2f07..715e45df8 -> delivery verified 0/0. MF-IC-P1 watch updated: bm-a collector v3 "
       f"transport fix live (PID 80340, 466+/5222 symbols at their commit), panel rebuild in flight -- S2 "
       f"completion gate check becomes live watch next windows | evidence: results/_r986bmc_conflict_merge.py + "
       f"results/_r986bmc_s05_probe.py | {now_iso} race window <=20min")
with open('logs/iteration-loop/round_reports-bm-c.md', 'a', encoding='utf-8') as f:
    f.write(row + '\n')

# state sync note update
d = json.load(open('state-bm-c.json', encoding='utf-8'))
d['sync'] = {
    'origin_tip': '715e45df8 (r986 closeout, post-rebase) at close',
    'ts': now_iso,
    'ahead_behind': '0/0 verified post-push',
    'note': 'r986: push raced bm-a 20190b53e absorb (claw caught, stash-bridge rebase landed, union merge 2 ledgers, supersession-drop stash); see r986 addendum row'
}
d['orders_ack_receipt'] = ('r986: zero unacked both scans; group ORD/DEC dual-delta FALSE both (ord 348eaf34 '
                          'content-sha / dec 86187eff hold); zero bm-c execution owed; push-race closed via rebase '
                          '(addendum row)')
json.dump(d, open('state-bm-c.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('addendum row + state sync note written')
