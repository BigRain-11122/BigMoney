import json
import re

raw = open("fleet/machines/bm-a.json", encoding="utf-8", newline="").read()
eol = "\r\n" if "\r\n" in raw[:2000] else "\n"

CUR_TASK = ("r694: N2-W15 supply materialization -- GENERATE pool entry "
            "enrolled (seat MSG-1943 per MSG-1955 downstream open face); "
            "W3 judge verdict watch ETA ~22:1x")
VERDICT = ("green: N2 supply enrolled (pool ready=5, one unowned=claimable); "
           "W3 judge in-flight bm-c; golden-week board-clear legal")


def set_key(raw, key, val_json):
    pat = re.compile('^ "%s": .*?(,?)%s' % (re.escape(key), re.escape(eol)),
                     re.M)
    hits = pat.findall(raw)
    print("  key %-22s hits=%d" % (key, len(hits)))
    assert len(hits) == 1, "key %s line count=%d" % (key, len(hits))
    line_end = hits[0]
    return pat.sub(' "%s": %s%s' % (key, val_json, line_end), raw, count=1)


upd = {
    "clock_read": json.dumps("2026-10-04T19:52:00+08:00", ensure_ascii=False),
    "last_seen": json.dumps("2026-10-04T19:52:00+08:00", ensure_ascii=False),
    "heartbeat_epoch_utc": "1791114500",
    "current_task": json.dumps(CUR_TASK, ensure_ascii=False),
    "task": json.dumps("T-2026-09-30-133 s2 (N2 supply materialization: GENERATE pool entry)", ensure_ascii=False),
    "verdict": json.dumps(VERDICT, ensure_ascii=False),
    "round_no": "694",
    "last_round": json.dumps("r694", ensure_ascii=False),
    "loop_round": "694",
    "free_ram_gb": "58.0",
    "ram_free_gb": "58.0",
}
for k, v in upd.items():
    before = raw.find(' "loop_round":')
    raw = set_key(raw, k, v)
    after = raw.find(' "loop_round":')
    if before != after:
        print("  !!! loop_round offset moved at key %s: %d -> %d"
              % (k, before, after))
print("DONE, loop_round present:", ' "loop_round":' in raw)
