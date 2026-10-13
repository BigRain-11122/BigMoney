# -*- coding: utf-8 -*-
# r978-continuation: O-20261014-0312 receipt + early pulse (STALE clear) + prod_lanes refresh
import json, time, psutil, re

BQ = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
HB = BQ + r"\fleet\machines\bm-c.json"
now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

vm = psutil.virtual_memory()
d = json.load(open(HB, encoding="utf-8"))
d["ts"] = now
d["last_seen"] = now
d["clock_read"] = now
d["heartbeat_epoch_utc"] = epoch
d["free_ram_gb"] = round(vm.available / 1024**3, 1)
d["idle_ram_gb"] = d["free_ram_gb"]
d["ram_free_gb"] = d["free_ram_gb"]
# RAM 紧态如实保留（protect 档注记）——巡检令 §2
d["ram_note"] = "protect: i2v/ComfyUI 常驻+夜窗烧窗期·巡检令 O-20261014-0312 §2 紧态如实保留"
# 节律承诺：案 1 pulse-only ≤2h（随轮 S7 写+长烧窗轮中 pulse）
d["pulse_law"] = "PT-20261006-01② 案1: burn-window pulse-only <=2h (per-round S7 write + in-round pulse on long burns)"
d["prod_lanes"] = ("CPU=N1 W234 full cycle LANDED (938,589/K 512,720) + W235 seated, r978 dead-estate absorbed, "
                   "R35 off-by-one bug found vs gold (4 faces) -> generator fix + regen this window; "
                   "GPU=MV V3 lane: fullres 7/7 burned+relayed, i2v GATED on bm-a director sign (whitelist 3/7 per ORD 10-13 23:5x)")
json.dump(d, open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("pulse written:", now, "epoch:", epoch, "free_ram:", d["free_ram_gb"])

# receipt line into the order file
ORD = BQ + r"\fleet\orders\O-20261014-0312-bm-c.md"
t = open(ORD, encoding="utf-8").read()
line = ("- [x] bm-c r978-continuation 2026-10-14T03:1x：选案1=pulse-only ≤2h（随轮 S7 写+长烧窗轮中 pulse；"
        "beat 上限声明=烧窗间隙 2h）·首笔验证 ts=" + now + "（本令收到同窗即写清 STALE）·"
        "RAM 0.7G 紧态按 §2 protect 注记保留（ram_note 字段落 bm-c.json）。\n")
t = t.replace("- [ ]\n", "- [ ]\n" + line)
open(ORD, "w", encoding="utf-8", newline="").write(t)
print("receipt appended")
