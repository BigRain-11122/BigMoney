# r1037 bm-c: poke bm-a (xq T1 wave-1 boards landed origin 60a39ee, sea-review ready)
import json, urllib.request

body = json.dumps({
    "reason": "bm-c r1037: xq T1 wave-1 boards+receipt landed origin 60a39ee - sea-review ready (11 boards 33x8)",
    "tasks": ["BigStream-OSLoop"],
    "repos": ["."],
}).encode()
req = urllib.request.Request("http://100.110.185.62:8790/poke", data=body,
                             headers={"Content-Type": "application/json"})
try:
    r = urllib.request.urlopen(req, timeout=25)
    print("POKE", r.status, r.read().decode()[:300])
except Exception as e:
    print("POKE-FAIL", repr(e)[:300])
