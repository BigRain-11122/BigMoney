# -*- coding: utf-8 -*-
# r1090 bm-c: machine-generate the 12:5x @bm-c 星晴 PACK-A 32-frame CDN staging map
# (orders 2026-10-18 12:5x dispatch; CEO 即时律 physical-dependency escape with
# in-ticket disclosure: 24 slots READY-NOW, 8 slots blocked on chain step-2/3
# [wave-2 variants already on disk are counted READY] + S5-27 director re-ruling).
# Zero hand-typing: manifest-driven + disk-verified + ZOOMQC/MSG-1200 action map.
import json, io, os, glob

GRP = r"K:\Fluxgroup\FluxGroup"
MANI = glob.glob(os.path.join(
    GRP, "cph4", "fleet", "mv-album-001-jay", "*PACK-A-v1.json"))[0]
CH = os.path.join(GRP, "media", "mv-album-001-jay", "chain-packA-state.json")

m = json.load(io.open(MANI, encoding="utf-8"))
# director-seat action faces (ZOOMQC r1057 + MSG-20261018-1200 sec.2/3): the
# whitelist-action first-choice OVERRIDES the manifest frame for these slots
ACTIONS = {
    "XQ_S5-26": ("s7rB-fallback", os.path.join(GRP, "media", "MV", "mv0001", "xingqing",
                   "abatch_s7r", "S5-26_s20191_s7rB.jpg"),
                 "ZOOMQC r1057: s20191_s7rC 不过检 -> grain-only s7rB 兜底 (MSG-1200 sec.2); ESGAN 补修后可再议升级"),
    "XQ_S5-28": ("s7rC-pass", os.path.join(GRP, "media", "MV", "mv0001", "xingqing",
                   "abatch_s7r", "S5-28_s20202_s7rC.png"),
                 "ZOOMQC r1057: s20202_s7rC 过检 -> wave-2 待烧 (MSG-1200 sec.2)"),
    "XQ_S5-27": ("DIRECTOR-RULING-PENDING", None,
                 "MSG-1200 sec.3: 帧位几何缺陷（双流星/流星雨读法）-> @bm-a 导演席重裁 3 选 1 pending; 挂起不烧; CDN 槽位候裁后填"),
}
slots = []
for u in m["units"]:
    uid, fr = u["id"], u["frame"]
    if uid in ACTIONS:
        kind, path, note = ACTIONS[uid]
        if path is None:
            slots.append({"id": uid, "status": "BLOCKED-director", "note": note,
                          "seed": None, "file": None, "bytes": None})
            continue
        b = os.path.getsize(path)
        slots.append({"id": uid, "status": "READY-NOW" if b > 100 * 1024 else "READY-UNDER-100KB",
                      "action": kind, "file": os.path.relpath(path, GRP).replace(os.sep, "/"),
                      "bytes": b, "note": note})
        continue
    if fr.startswith("PENDING"):
        seed = fr.split(":")[-1]
        slots.append({"id": uid, "status": "BLOCKED-T1R1-chain",
                      "seed": seed,
                      "file": "media/MV/mv0001/xingqing/t1r1hd/<T1R1 输出名·种子 %s>" % seed,
                      "bytes": None,
                      "note": "T1-1R 正档直烧 14 格 = chain-packA chain step 3 (wave-1 ETA ~17:00 -> wave-2 ~10min -> step 3); seed per signed manifest"})
        continue
    fp = os.path.join(GRP, fr.replace("/", os.sep))
    b = os.path.getsize(fp) if os.path.isfile(fp) else -1
    slots.append({"id": uid, "status": "READY-NOW" if b > 100 * 1024 else "MISSING-ON-DISK",
                 "seed": os.path.splitext(os.path.basename(fr))[0].split("_s")[-1],
                 "file": fr, "bytes": b if b > 0 else None})

ready = [s for s in slots if s["status"] == "READY-NOW"]
blocked = [s for s in slots if s["status"] != "READY-NOW"]
chain = json.load(io.open(CH, encoding="utf-8")) if os.path.isfile(CH) else {"ts": "absent"}
out = {
 "ticket": "orders 2026-10-18 12:5x 【@bm-c 派单】星晴 i2v PACK-A 32 胜者帧 CDN 交付 (41 曲加速令行动①)",
 "staged_by": "r1090 bm-c loop window (codely census 13:2x: single live session = this loop; MV ops seat dead post-MSG-1200 12:00; 查重律 zero live carrier)",
 "counts": {"total": len(slots), "ready_now": len(ready), "blocked": len(blocked)},
 "slots": slots,
 "chain_state_at_staging": chain,
 "dependency_disclosure": "CEO 即时律唯一暂缓事由=物理依赖票内留痕: 7 slots BLOCKED-T1R1-chain (chain step 3, ETA ~17:10 post wave-1[~17:00]+wave-2[~10min]) + 1 slot S5-27 BLOCKED-director (bm-a re-ruling per MSG-1200 sec.3). Partial upload REJECTED by acceptance spec (32/32 HEAD 200 + bytes>100KB + single 32-row receipt) -- partial = noise for bm-a ignition gate.",
 "executor_next": "next MV ops window OR next loop round when (a) chain state advances past t1r1hd step AND (b) S5-27 director ruling landed: upload 32 via the r1008 CDN tooling family (results/_r1008bmc_wave2_cdn_{verify,repair}.py = CDN URL/HEAD mechanism), receipt = fleet/inbox/MSG-20261018-<HHMM>-xq-frames32.md (32 rows: 帧位 id+种子+CDN URL+字节数), then poke bm-a (cloud wave ignition, minimax_h3 768P first_frame, 并发≤2, 1 日配额)",
 "manifest": os.path.relpath(MANI, GRP).replace(os.sep, "/"),
 "law_refs": ["CEO 即时律 O-20260924-1730 (same-round claim+start; 物理依赖暂缓须票内留痕)",
              "查重律 (no live carrier verified by census)", "歧义以导演席签发件帧位档为准 (ZOOMQC r1057 + MSG-1200 sec.2/3 adjudications staged per-slot)"],
}
p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                 "results", "_r1090bmc_xq32_staging.json")
io.open(p, "w", encoding="utf-8").write(json.dumps(out, indent=1, ensure_ascii=False))
print("STAGING OK -> %s" % p)
print("ready_now=%d blocked=%d (T1R1=%d director=%d)" % (
    len(ready), len(blocked),
    len([s for s in blocked if s["status"] == "BLOCKED-T1R1-chain"]),
    len([s for s in blocked if s["status"] == "BLOCKED-director"])))
for s in blocked:
    print("  BLOCKED", s["id"], s["status"], s.get("seed") or "")
