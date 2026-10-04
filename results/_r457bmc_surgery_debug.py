"""r457 bm-c surgery debug: apply replacement in memory, print region + detailed parse error."""
import datetime
import json

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
POOL = ROOT + r"\results\runnable_pool.json"

with open(POOL, "rb") as fh:
    raw = fh.read()

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
needle = b'keep-block note on crash_fuse"\r\n    }'
prov = (
    " | rel-bm-c-r457 %s: owner row restored on shared face "
    "(r637 four-face surgery healed VALUE+DIVLOWVOL owner rows but missed 3rd "
    "shard QUALITY -- ownerless since off-caliber-era releases while canonical "
    "burn stayed alive; evidence: burner pid 57116 alive per MSG-0857/0925/2005 "
    "+ nulls row growth 504->510 between 08:47-09:00 bm-b pushes; bm-b daemon "
    "keepalive self-adopts per r288 owner==myid gate; bm-c host_gates fail = "
    "bm-c cannot claim this shard, surgery is observation-heal not self-claim); "
    "owner_since=restore action-time per r400" % now
).encode("utf-8")
replacement = (
    b'keep-block note on crash_fuse' + prov + b'"\r\n'
    b'     "owner": "bm-b",\r\n'
    b'     "owner_since": "' + now.encode("ascii") + b'"\r\n'
    b'    }'
)
print("prov bytes: %d" % len(prov))
print("prov text:", prov.decode("utf-8"))
new = raw.replace(needle, replacement)
text = new.decode("utf-8")
lines = text.split("\n")
for i in range(13832, 13842):
    print("%5d|%s" % (i, lines[i][:200].replace("\r", "<CR>")))
try:
    json.loads(text)
    print("PARSE OK")
except ValueError as e:
    print("PARSE FAIL:", e)
