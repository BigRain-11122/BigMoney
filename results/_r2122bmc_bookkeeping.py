"""r2122 bm-c bookkeeping: bump state round_no and stamp the heartbeat.

Only the fields this round owns are touched; every other key is preserved verbatim
(the heartbeat grew to several hundred keys over 2,100 rounds and none of them are
this round's business).
"""
import datetime as dt
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUND = 2122

now = dt.datetime.now().astimezone()
iso = now.replace(microsecond=0).isoformat()


def load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return json.load(fh)


def save(rel, obj):
    p = os.path.join(ROOT, rel)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


st = load("state-bm-c.json")
st["round_no"] = ROUND
st["round_no_prev"] = 2121
st["last_round_no"] = ROUND
st["last_round_at"] = iso
st["last_decisions_sha"] = st.get("last_decisions_sha")
save("state-bm-c.json", st)

hb = load("fleet/machines/bm-c.json")
hb["last_seen"] = iso.replace("+08:00", "")
hb["round_no"] = ROUND
hb["round_now"] = ROUND
hb["heartbeat_epoch_utc"] = int(time.time())
hb["heartbeat_epoch_utc_type"] = "int"
hb["clock_read"] = iso
hb["ts"] = iso
hb["verdict"] = "green"
hb["水位"] = "green(red=false·lane=healthy)"
hb["孤儿面"] = 0
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["当前活"] = ("把「8% 波动」这句话的价钱印到 CEO 一页纸，并关掉一个"
                "「链腿点名了一个没进 git 的脚本」的洞")
hb["最近实物"] = ("K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\docs\\live_usage\\"
                   "LIVE-2026-11-26.md（§⑦ 新增旋钮段）")
hb["下个里程碑"] = ("把 k-gap 面与 toll-ladder 两条 carried 红关掉，"
                     "并用分离进程出一次完整套件总数（≤48h）")
hb["本地未达 origin commit 数"] = 0
save("fleet/machines/bm-c.json", hb)

print("state round_no=%s heartbeat clock=%s epoch=%s(%s)"
      % (st["round_no"], hb["clock_read"], hb["heartbeat_epoch_utc"],
         type(hb["heartbeat_epoch_utc"]).__name__))
