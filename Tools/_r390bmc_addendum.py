# -*- coding: utf-8 -*-
"""r390 bm-c addendum: mid-window contest shard-3/4 self-claim+burn disclosure."""
import datetime as dt
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = dt.datetime.now()
NOW_TS = NOW.strftime("%Y-%m-%d %H:%M:%S")
NOW_ISO = NOW.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"

REPORT_ADDENDUM = """
## [r390 补记 00:3x] 中窗事件：本机 daemon 自claim+烧完 contest-ytd-p1 shard-3/4（双占面如实披露+下轮首查）
①中窗事实链（主交付 commit 50ebc7669 之后、收口 commit 6a71b024f 窗内）：本机 autofill tick 00:27:40 claim+launch contest-ytd-p1-shard-3of8（pid 31792）→00:29:36 烧完 21 行（burn_shard_3of8.jsonl 103KB）；00:30:10 claim+launch shard-4of8（pid 8680·core_verdict=multiproc·fullburn_window=true·target_met=true）→00:31:55 烧完 21 行（burn_shard_4of8.jsonl 104KB）——两分片产物已随收口 commit 6a71b024f 上 origin；供给缺口部分自填（contest 2/8 分片本机贡献·引擎活面实弹证明）。②双占面如实披露：origin 实读=bm-a 00:10-00:15 池行 claim 全 8 片（仅 shard-0/2 有 keepalive=在飞面；3/4/1/5/6/7=claimed 未起烧）；本机 daemon 00:27/00:30 重占 3/4 行——O-2210 claim-file 面=origin 零 contest claim 件（ls-tree 实证）=协议面互不可见族（r489 变体：两机 tick 各按己面 claim）；O-2150「池子放宽胜者为王」大赛语义下多机抢分片或为设计面，但 bm-a 引擎推进到 3/4 时若按其本地陈旧视图起烧=真双烧浪费（r489 算力意义性律）→下轮首查：bm-a tick 对 3/4 行为（跳过=合法竞速收编；起烧=kill-advice 消息按 r489 律）。③shard-3 law-2 红旗照录：pool_red_flags.jsonl +1 行（wall 60.2s·effective_cores 0.82·O-20260930-2355 sec.1 law-2）——r293 加载窗采样伪影先例候查（21 员轻分片族或真单核烧·下轮按 burn log/audit 块实测定性）；shard-4 launch face multiproc 过门。④nulls fuse 面复核：last_tick verdict=fuse_refused_crash_loop（fuse_refusals=6）=r389 故意保留的 ``--nulls`` sig 拒发在正确履职（防本机复抢 bm-a 在飞面）；nulls 池行 owner=bm-b（23:56:18·零 claim 件）待 MSG-2359 回执。⑤两分片 harvest/close 握手由 daemon 后续 tick 自然收口（O-2210 链），下轮核对池行翻面。
本地未达 origin commit 数=0（本补记推送后自证）
"""

APPEND_VERIFY = (" MID-WINDOW ADDENDUM: local engine self-claimed + burned contest-ytd-p1 shards 3+4 "
 "(21 rows each, products on origin via 6a71b024f, supply gap partially self-filled 2/8); double-claim "
 "face disclosed: bm-a pool-row claims all 8 shards 00:10-00:15 (keepalives only on 0/2, no contest "
 "claim-files on origin per ls-tree) vs our daemon re-claims 3/4 at 00:27/00:30 -- O-2150 winner-takes-all "
 "racing may be by-design but next-round first check = bm-a tick behavior on rows 3/4 (skip=legal race; "
 "launch=kill-advice per r489); shard-3 law-2 red flag logged (effective_cores 0.82 @60.2s wall, r293 "
 "loading-window-artifact precedent candidate); nulls fuse correctly refusing re-launch (6 refusals, "
 "r389 deliberate tombstone).")

APPEND_NEXT_PREFIX = ("(a0) CONTEST SHARD-3/4 double-claim watch (first check): bm-a tick behavior on rows 3/4 "
 "when their engine advances (skip=legal race, launch=kill-advice msg per r489); shard-3 law-2 red flag "
 "disposition (r293 loading-window artifact vs true single-core, measure via burn log/audit); contest "
 "harvest/close handshake verify (daemon next ticks); ")


def main():
    epoch = int(dt.datetime.now().timestamp())

    sp = os.path.join(ROOT, "state-bm-c.json")
    st = json.loads(open(sp, "rb").read().decode("utf-8-sig"))
    st["verify"] = st["verify"] + APPEND_VERIFY
    st["did"] = st["did"] + (" + mid-window: engine self-claimed + burned contest-ytd-p1 shards 3+4 "
                            "(21 rows each, on origin via 6a71b024f)")
    st["next"] = APPEND_NEXT_PREFIX + st["next"]
    st["current_task"] = "r390 addendum: contest double-claim disclosure + push + self-verify"
    st["heartbeat_epoch_utc"] = epoch
    st["clock_read"] = NOW_ISO
    st["last_ts"] = NOW_TS
    st["last_seen"] = NOW_TS
    st["updated"] = NOW_ISO
    st["updated_at"] = NOW_ISO
    st["last_round"] = st["last_round"] + " + addendum: contest shards 3/4 burned (double-claim disclosed)"
    with open(sp, "wb") as fh:
        fh.write(json.dumps(st, ensure_ascii=False, indent=1).encode("utf-8"))

    hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    hb = json.loads(open(hp, "rb").read().decode("utf-8-sig"))
    hb["verdict"] = hb["verdict"] + APPEND_VERIFY
    hb["prod_lanes"] = (hb["prod_lanes"] + " + ADDENDUM: engine self-burned contest-ytd-p1 shards 3+4 "
                        "(double-claim vs bm-a pool-row claims disclosed, next-round first check)")
    hb["latest_artifact"] = ("results/contest_p1/burn_shard_{3,4}of8.jsonl (21 rows each, contest YTD race "
                              "shards) + results/lowamp_deep_p1/sens.jsonl (500 rows) via commits 50ebc7669/6a71b024f "
                              "@ 2026-10-03 00:3x")
    hb["next_milestone"] = ("contest-ytd-p1 8-shard race completion + LOWAMP-DEEP-P1 finalize/E1 by 10-09 pre-market "
                            "(9/10 units done; nulls 2000 bm-a in-flight)")
    hb["activity_now"] = ("S7 addendum: contest double-claim disclosure push; engine idle post shard-3/4 "
                          "completion (next ticks continue race if rows free)")
    hb["current_task"] = "r390 addendum: disclosure push + delivery self-verify"
    hb["heartbeat_epoch_utc"] = epoch
    hb["clock_read"] = NOW_ISO
    hb["last_seen"] = NOW_TS
    hb["last_seen_at"] = NOW_TS
    hb["updated_at"] = NOW_ISO
    with open(hp, "wb") as fh:
        fh.write(json.dumps(hb, ensure_ascii=False, indent=1).encode("utf-8"))

    rp = os.path.join(ROOT, "round_reports-bm-c.md")
    with open(rp, "ab") as fh:
        fh.write(REPORT_ADDENDUM.encode("utf-8"))

    st2 = json.loads(open(sp, "rb").read().decode("utf-8-sig"))
    hb2 = json.loads(open(hp, "rb").read().decode("utf-8-sig"))
    assert isinstance(st2["heartbeat_epoch_utc"], int) and isinstance(hb2["heartbeat_epoch_utc"], int)
    assert "T" in st2["clock_read"]
    print("addendum OK: state/heartbeat updated, report +1 addendum entry, epoch=", epoch)


if __name__ == "__main__":
    main()
