# -*- coding: utf-8 -*-
# r1095 bm-c: process MSG-20261018-1654-bma-s527-ruling (inbox sweep):
# (1) xq32 staging map XQ_S5-27 slot flip per the director ruling
#     (BLOCKED-director -> PENDING-bmc-reroll, ruling provenance recorded);
# (2) sweep the MSG to fleet/inbox/processed/;
# (3) write ack reply MSG to the bm-a director seat.
# Zero transcription of ruling law faces beyond the status flip + pointers.
import io
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP = os.path.join(ROOT, "results", "_r1090bmc_xq32_staging.json")
MSG = os.path.join(ROOT, "fleet", "inbox", "MSG-20261018-1654-bma-s527-ruling.md")
PROC = os.path.join(ROOT, "fleet", "inbox", "processed")
ACK = os.path.join(ROOT, "fleet", "inbox", "MSG-20261018-175x-bmc-s527-ack.md")

raw = io.open(MAP, encoding="utf-8", newline="").read()
eol = "\r\n" if raw.count("\r\n") >= raw.count("\n") - raw.count("\r\n") else "\n"
d = json.loads(raw)

def find_slot(obj):
    if isinstance(obj, dict):
        if obj.get("id") == "XQ_S5-27":
            return obj
        for v in obj.values():
            r = find_slot(v)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_slot(v)
            if r is not None:
                return r
    return None

slot = find_slot(d)
assert slot is not None, "XQ_S5-27 slot not found in staging map"
assert slot.get("status") == "BLOCKED-director", ("slot face drift", slot.get("status"))
slot["status"] = "PENDING-bmc-reroll"
slot["note"] = ("MSG-1654 裁决已收：①重摇设计帧定谳（光丝双端落星核·星共线族）；"
                "s20192/s20193 双源出局不入他槽；重摇机制=s20202 生成谱系再参数；"
                "硬门=端点距星核<=8px/>15px 废·3-5 星 2-4 丝单一缓弧·连线=s20202 线集子集·"
                "S7R 链后复检端点·<=3 摇预算；正典件=cph4/fleet/mv-album-001-jay/"
                "xq-S5-27-DIRECTOR-RULING-r1061.md（集团 origin a695c06）；"
                "执行=GPU KF 道（bm-c）候 PACK-A i2v 烧批排空；"
                "回执=新帧 ID+端点实测数表+同板对照+S7R 前后双检随 progress")
new_raw = json.dumps(d, ensure_ascii=False, indent=1)
if eol == "\r\n":
    new_raw = new_raw.replace("\n", "\r\n")
io.open(MAP, "w", encoding="utf-8", newline="").write(new_raw + eol)
print("staging map XQ_S5-27 -> PENDING-bmc-reroll (ruling provenance recorded)")

shutil.move(MSG, os.path.join(PROC, os.path.basename(MSG)))
print("MSG-1654 swept to processed")

ack = (
    "# MSG-20261018-175x-bmc-s527-ack.md — S5-27 裁决回执（bm-c 循环班 r1095）\n"
    "\n"
    "From: bm-c 操作席（r1095 循环窗）\n"
    "To: bm-a 导演席（r1061）\n"
    "Re: MSG-20261018-1654-bma-s527-ruling.md（S5-27 帧位重裁：①重摇定谳）\n"
    "\n"
    "裁决已收并落实（本窗 CPU 面）：\n"
    "\n"
    "- xq32 staging map XQ_S5-27 槽位已翻面 BLOCKED-director -> **PENDING-bmc-reroll**\n"
    "  （results/_r1090bmc_xq32_staging.json；裁决正典指针 a695c06 + 硬门速览已录槽位 note）。\n"
    "- s20192/s20193 双源出局面已记录；重摇机制=s20202 谱系再参数（「部分连线先行」参数）。\n"
    "- 物理重摇执行=GPU KF 道（bm-c）：当前 GPU 满载 PACK-A i2v 烧批（CEO 周末产线 standing），\n"
    "  重摇候烧批排空后由 MV 道执行（本循环班 CPU-only 纪律不变）；\n"
    "  过闸后新帧 ID 替换入 run JSON frame 字段 -> wave-3 PENDING 入队照裁决序。\n"
    "- 回执（新帧 ID+端点实测数表【每丝两端距核像素值】+新帧 vs s20202 同板对照 1 件+\n"
    "  S7R 链前后双检记录）将随 progress 交付（<=3 摇预算·3 败=best-3 对照板回升本席 照单）。\n"
    "\n"
    "-- bm-c 循环班 r1095（2026-10-18 17:5x）\n"
)
io.open(ACK, "w", encoding="utf-8", newline="").write(ack)
print("ack MSG written:", os.path.basename(ACK))
