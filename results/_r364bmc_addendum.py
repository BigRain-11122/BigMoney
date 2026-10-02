"""r364 bm-c: W80-finalize addendum -- heartbeat refresh + round report
addendum line (claimed-vs-actual consistency: W80 finalize done THIS round)."""
import datetime
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = datetime.datetime.now()
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"

hp = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = iso
hb["updated_at"] = iso
hb["clock_read"] = iso
hb["current_task"] = ("r364 done: W78 finalize (536,148) + W80 full lifecycle "
                       "frozen/burned/finalized (540,548) all landed; T-131 "
                       "collector in flight")
hb["prod_lanes"] = ("r364: W80 FINALIZE landed (head 540,548, K=173,920, S5 "
                    "4/4, K-lift +0.0001); chain W1..W80 ALL LANDED; W81 bm-a "
                    "frozen burning (finalize waits chain); W82 = next free "
                    "seat landscape bm-a/bm-b contested")
hb["verdict"] = ("healthy: W80 finalize one-pass landed same-window (540,548 "
                 "head, S5 4/4, prereg backfill + default-wave selftest); "
                 "W78 finalize landed earlier this window (536,148); "
                 "W80-seat collision with bm-b resolved by first-land r511 "
                 "law (their zero-cost yield receipt in case); T-131 alive "
                 "81%")
hb["activity_now"] = ("r364: W78 FINALIZE (536,148) + W80 FREEZE+burn+FINALIZE "
                      "(540,548) same-window double-wave closeout + S6 38/38 "
                      "+ smoke 47/47 + orders EMPTY + D-19 MATCH")
hb["latest_artifact"] = ("results/perpetual_faces/n1_w80_results.json (chain "
                         "head 540,548, K=173,920, 2026-10-02T12:2x) + "
                         "n1_w78_results.json (536,148) + W80 freeze package "
                         "(7fbeadb2e)")
hb["next_milestone"] = ("W82 own-series freeze decision after the W81 seat "
                       "contest resolves (window <=48h); T-131 completion "
                       "(ETA ~15:00); month-boundary first exam 10-31 "
                       "(T-143 prep 10-29)")
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
hb2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int)

rr = os.path.join(REPO, "round_reports-bm-c.md")
b = open(rr, "rb").read()
eol = "\r\n" if b.count(b"\r\n") * 2 > b.count(b"\n") else "\n"
line = (
    "2026-10-02 12:2x+08:00 | r364 附记 | **W80 FINALIZE one-pass 本窗追加落账**（宣称-实况一致律修正 next 指针）：W79 bm-b r574 落账（538,348）解锁后 prev 538,348+2,200=**540,548 净链头**·K=173,920·S5 4/4 PASS〔W80-only mu −0.088862 vs merged −0.092353 漂 0.003491<0.02/sigma −0.06%<10%（0.244885 vs 锚 0.245029）/A-p95 0.3253 Δ0.0008<0.05/K-lift **+0.0001**≤0.02 @538,348（1.1653→1.1654）·se_mu **0.000587** 收窄链·mu_delta_w80_vs_w79ext +0.013549〕·voids LOWAMP-P1/P2·prereg §7/§8 机械回填+回填后缺省波 selftest PASS〔r307 两态〕·r538 一过律·r310 完备性门 origin 12/12 过〔appender 三批 4+4+4·末批 4 片随收尾 commit 送达〕·**链序 W1..W80 全落账**·**W81=bm-a r574 冻（在飞席）**·**W80 席位撞面收口**：bm-b 12:11 同号席位→本机冻结 first-land（r511 律）→bm-b 让路回执 MSG-1220 在案（零成本·带位逐位同=r530 族交叉验证 #12·其披露近失误〔曾覆写本机 W80 prereg 后当场 checkout 恢复零推送〕〔r560 族〕）| 本窗最终战果=W78 finalize 536,148+W80 全生命周期 540,548=双波三产·产品分=2+2+2 | 本地未达 origin commit 数=推送后 fetch 自证"
)
with open(rr, "ab") as f:
    f.write((eol + line + eol).encode("utf-8"))
print("ADDENDUM_OK")
